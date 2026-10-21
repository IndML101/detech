"""Declarative Lua configuration loader for DETech.

Supports `lupa.LuaRuntime` when installed, and includes a zero-dependency
pure-Python recursive Lua table parser so DETech works out-of-the-box on any
fresh FreeBSD installation.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from detech.core.paths import resolve_lua_file


class LuaParseError(ValueError):
    """Raised when a Lua configuration file cannot be parsed."""


def _strip_lua_comments(source: str) -> str:
    """Remove single-line (--) and multi-line (--[[ ... ]]) Lua comments outside strings."""
    result: list[str] = []
    i = 0
    n = len(source)
    in_string: str | None = None

    while i < n:
        ch = source[i]
        if in_string:
            result.append(ch)
            if ch == "\\" and i + 1 < n:
                i += 1
                result.append(source[i])
            elif ch == in_string:
                in_string = None
            i += 1
            continue

        if ch in ('"', "'"):
            in_string = ch
            result.append(ch)
            i += 1
            continue

        if source.startswith("--[[", i):
            end = source.find("]]", i + 4)
            i = n if end == -1 else end + 2
            continue

        if source.startswith("--", i):
            end = source.find("\n", i + 2)
            i = n if end == -1 else end
            continue

        result.append(ch)
        i += 1

    return "".join(result)


class _Tokenizer:
    """Simple tokenizer for declarative Lua files."""

    TOKEN_RE = re.compile(
        r"""
        \s*(?:
            (?P<brace>[{}]) |
            (?P<punct>[=,;\[\]]) |
            (?P<string>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*') |
            (?P<number>-?\d+(?:\.\d+)?) |
            (?P<ident>[A-Za-z_][A-Za-z0-9_]*)
        )
        """,
        re.VERBOSE,
    )

    def __init__(self, text: str) -> None:
        self.tokens: list[tuple[str, str]] = []
        pos = 0
        n = len(text)
        while pos < n:
            if text[pos:].isspace():
                break
            m = self.TOKEN_RE.match(text, pos)
            if not m:
                snippet = text[pos : pos + 40]
                raise LuaParseError(f"Unexpected Lua syntax near: {snippet!r}")
            kind = m.lastgroup or "unknown"
            val = m.group(kind)
            self.tokens.append((kind, val))
            pos = m.end()
        self.idx = 0

    def peek(self) -> tuple[str, str] | None:
        if self.idx < len(self.tokens):
            return self.tokens[self.idx]
        return None

    def next(self) -> tuple[str, str]:
        tok = self.peek()
        if tok is None:
            raise LuaParseError("Unexpected end of Lua input")
        self.idx += 1
        return tok


def _parse_lua_pure(source: str) -> Any:
    """Parse a declarative Lua module (with optional `local` variables and `return { ... }`)."""
    cleaned = _strip_lua_comments(source)
    toks = _Tokenizer(cleaned)
    locals_env: dict[str, Any] = {}

    def parse_value() -> Any:
        tok = toks.peek()
        if tok is None:
            raise LuaParseError("Expected value, got EOF")
        kind, val = tok
        if kind == "brace" and val == "{":
            return parse_table()
        if kind == "string":
            toks.next()
            inner = val[1:-1]
            return bytes(inner, "utf-8").decode("unicode_escape")
        if kind == "number":
            toks.next()
            return float(val) if "." in val else int(val)
        if kind == "ident":
            toks.next()
            if val == "true":
                return True
            if val == "false":
                return False
            if val == "nil":
                return None
            if val in locals_env:
                return locals_env[val]
            return val
        raise LuaParseError(f"Unexpected token {tok}")

    def parse_table() -> dict[str, Any] | list[Any]:
        toks.next()  # consume '{'
        entries: list[tuple[Any | None, Any]] = []
        while True:
            peek = toks.peek()
            if peek is None:
                raise LuaParseError("Unclosed '{' in Lua table")
            if peek == ("brace", "}"):
                toks.next()
                break

            # Check for [key] = val or ident = val or positional item
            if peek == ("punct", "["):
                toks.next()
                key = parse_value()
                if toks.next() != ("punct", "]"):
                    raise LuaParseError("Expected ']' after table key")
                if toks.next() != ("punct", "="):
                    raise LuaParseError("Expected '=' after [key]")
                value = parse_value()
                entries.append((key, value))
            elif peek[0] == "ident":
                # Lookahead for '='
                saved_idx = toks.idx
                _, ident_name = toks.next()
                if toks.peek() == ("punct", "="):
                    toks.next()  # consume '='
                    value = parse_value()
                    entries.append((ident_name, value))
                else:
                    toks.idx = saved_idx
                    value = parse_value()
                    entries.append((None, value))
            else:
                value = parse_value()
                entries.append((None, value))

            sep = toks.peek()
            if sep in (("punct", ","), ("punct", ";")):
                toks.next()

        if not entries:
            return {}
        if all(k is None for k, _ in entries):
            return [v for _, v in entries]
        result: dict[str, Any] = {}
        auto_idx = 1
        for k, v in entries:
            if k is None:
                result[str(auto_idx)] = v
                auto_idx += 1
            else:
                result[str(k)] = v
        return result

    return_val: Any = {}
    while toks.peek() is not None:
        kind, val = toks.peek()  # type: ignore[misc]
        if kind == "ident" and val == "local":
            toks.next()
            _, var_name = toks.next()
            if toks.next() != ("punct", "="):
                raise LuaParseError(f"Expected '=' after local {var_name}")
            locals_env[var_name] = parse_value()
            if toks.peek() == ("punct", ";"):
                toks.next()
        elif kind == "ident" and val == "return":
            toks.next()
            return_val = parse_value()
            if toks.peek() == ("punct", ";"):
                toks.next()
        else:
            return_val = parse_value()

    return return_val


def _lupa_to_python(obj: Any) -> Any:
    """Recursively convert a lupa LuaTable into Python lists/dicts."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    try:
        items = list(obj.items())
    except Exception:
        return obj
    if not items:
        return {}
    keys = [k for k, _ in items]
    if all(isinstance(k, int) for k in keys) and keys == list(range(1, len(keys) + 1)):
        return [_lupa_to_python(v) for _, v in items]
    return {str(k): _lupa_to_python(v) for k, v in items}


def load_lua_string(source: str, use_lupa: bool = True) -> dict[str, Any]:
    """Parse a Lua configuration string into a Python dictionary."""
    if use_lupa:
        try:
            from lupa import LuaRuntime  # type: ignore[import-not-found]

            lua = LuaRuntime(unpack_returned_tuples=True)
            res = lua.execute(source)
            converted = _lupa_to_python(res)
            if isinstance(converted, dict):
                return converted
        except ImportError:
            pass
        except Exception as exc:
            raise LuaParseError(f"Lua execution failed: {exc}") from exc

    parsed = _parse_lua_pure(source)
    if not isinstance(parsed, dict):
        raise LuaParseError("Expected Lua file to return a table")
    return parsed


def load_lua_file(path: Path | str, use_lupa: bool = True) -> dict[str, Any]:
    """Load and parse a `.lua` file from disk."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Lua configuration file not found: {file_path}")
    return load_lua_string(file_path.read_text(encoding="utf-8"), use_lupa=use_lupa)


def load_all_user_configs() -> dict[str, dict[str, Any]]:
    """Load all standard DETech Lua configuration modules."""
    modules = ["config", "keybinds", "monitors", "rules", "plugins", "freebsd"]
    loaded: dict[str, dict[str, Any]] = {}
    for mod in modules:
        path = resolve_lua_file(f"{mod}.lua")
        loaded[mod] = load_lua_file(path)
    return loaded
