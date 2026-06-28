"""Persistent notes tool."""
import json
import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

NOTES_FILE = Path("notes.json")


def _load_notes() -> list:
    """Read all notes from disk. Returns empty list if file doesn't exist."""
    if not NOTES_FILE.exists():
        return []
    try:
        with NOTES_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_notes(notes: list) -> None:
    """Write all notes back to disk."""
    with NOTES_FILE.open("w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)


def save_note(content: str, tags: list | None = None) -> str:
    """Save a new note with optional tags and a timestamp."""
    if not content or not content.strip():
        return "Note is empty — nothing to save."
    notes = _load_notes()
    entry = {
        "id": len(notes) + 1,
        "timestamp": datetime.datetime.now(ZoneInfo("Asia/Amman")).isoformat(),
        "content": content.strip(),
        "tags": [t.lower() for t in (tags or [])],
    }
    notes.append(entry)
    _save_notes(notes)
    tag_str = f" [tags: {', '.join(entry['tags'])}]" if entry["tags"] else ""
    return f"Note #{entry['id']} saved.{tag_str}"


def list_notes(limit: int = 10) -> str:
    """List the most recent notes."""
    notes = _load_notes()
    if not notes:
        return "No notes yet."
    recent = notes[-limit:]
    lines = []
    for n in recent:
        tag_str = f" [{', '.join(n['tags'])}]" if n.get("tags") else ""
        ts = n["timestamp"][:16].replace("T", " ")
        lines.append(f"#{n['id']} ({ts}){tag_str}: {n['content']}")
    return "\n".join(lines)


def search_notes(query: str) -> str:
    """Search notes by keyword in content or tags. Case-insensitive, word-by-word."""
    notes = _load_notes()
    if not notes:
        return "No notes yet."
    stopwords = {"the", "a", "an", "is", "are", "was", "were", "to", "of", "in", "for", "and", "or"}
    words = [w for w in query.lower().split() if w not in stopwords and len(w) > 1]
    if not words:
        words = [query.lower()]
    matches = []
    for n in notes:
        haystack = n["content"].lower() + " " + " ".join(n.get("tags", []))
        if any(w in haystack for w in words):
            matches.append(n)
    if not matches:
        return f"No notes match '{query}'."
    lines = []
    for n in matches:
        tag_str = f" [{', '.join(n['tags'])}]" if n.get("tags") else ""
        ts = n["timestamp"][:16].replace("T", " ")
        lines.append(f"#{n['id']} ({ts}){tag_str}: {n['content']}")
    return "\n".join(lines)


NOTES_DEFS = [
    {
        "name": "save_note",
        "description": (
            "Save a note to Basil's persistent notes file. Use this whenever he asks "
            "you to remember something, take a note, log a trade, set a reminder, "
            "or save a fact. Notes persist across sessions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "The note content — what to remember."},
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Optional list of short tag strings to categorise the note. "
                        "Examples: ['trade'], ['mint', 'feeding'], ['reminder']."
                    )
                }
            },
            "required": ["content"]
        }
    },
    {
        "name": "list_notes",
        "description": (
            "List the most recent notes Basil has saved. Use when he asks "
            "what notes he has, what he told you to remember, or to review recent items."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "How many recent notes to show. Defaults to 10."}
            }
        }
    },
    {
        "name": "search_notes",
        "description": (
            "Search notes for a keyword. Use this whenever Basil asks about something "
            "he MIGHT have told you before — about Mint, trades, reminders, family, "
            "anything. Search FIRST before saying you don't know."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The keyword to search for in note content or tags."}
            },
            "required": ["query"]
        }
    }
]

NOTES_FUNCS = {"save_note": save_note, "list_notes": list_notes, "search_notes": search_notes}