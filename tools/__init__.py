"""Tools that Jarvis can call.

This package gathers all individual tool modules and exposes:
- TOOL_DEFINITIONS: list of schemas for Claude
- TOOL_FUNCTIONS: dict mapping tool name to Python function
"""
from .weather import WEATHER_DEFS, WEATHER_FUNCS
from .filesystem import FS_DEFS, FS_FUNCS
from .timemath import TIMEMATH_DEFS, TIMEMATH_FUNCS
from .notes import NOTES_DEFS, NOTES_FUNCS

# Anthropic's built-in web search — Claude runs the search on their end.
# Just include this in the tools list and it works. No Python function needed.
WEB_SEARCH_DEF = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 5,  # cap searches per turn to keep cost predictable
}

TOOL_DEFINITIONS = (
    WEATHER_DEFS
    + FS_DEFS
    + TIMEMATH_DEFS
    + NOTES_DEFS
    + [WEB_SEARCH_DEF]
)

TOOL_FUNCTIONS = {
    **WEATHER_FUNCS,
    **FS_FUNCS,
    **TIMEMATH_FUNCS,
    **NOTES_FUNCS,
}


def list_all_tools() -> str:
    """Return a human-readable list of all tools currently available."""
    lines = ["Jarvis currently has access to these tools:"]
    for d in TOOL_DEFINITIONS:
        name = d["name"]
        desc = d.get("description", "(built-in server-side tool)")
        short = desc.split(".")[0]
        lines.append(f"  • {name} — {short}")
    return "\n".join(lines)