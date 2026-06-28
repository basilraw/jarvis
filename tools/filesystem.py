"""Sandboxed file reading tools."""
from pathlib import Path

SANDBOX_DIR = Path("sandbox").resolve()


def _safe_path(filename: str):
    """Resolve a filename to a real path inside the sandbox, or None if unsafe."""
    try:
        target = (SANDBOX_DIR / filename).resolve()
    except Exception:
        return None
    if SANDBOX_DIR not in target.parents and target != SANDBOX_DIR:
        return None
    return target


def list_files() -> str:
    """List all files inside the sandbox directory."""
    if not SANDBOX_DIR.exists():
        return f"Sandbox folder doesn't exist at {SANDBOX_DIR}."
    files = sorted(p.name for p in SANDBOX_DIR.iterdir() if p.is_file())
    if not files:
        return "Sandbox is empty."
    return "Files in sandbox: " + ", ".join(files)


def read_file(filename: str) -> str:
    """Read a file from inside the sandbox. Refuses anything outside."""
    target = _safe_path(filename)
    if target is None:
        return f"Refused: '{filename}' is outside the sandbox."
    if not target.exists():
        return f"File '{filename}' not found in sandbox."
    if not target.is_file():
        return f"'{filename}' is not a file."
    MAX_BYTES = 10_000
    try:
        text = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"'{filename}' isn't a readable text file."
    if len(text) > MAX_BYTES:
        text = text[:MAX_BYTES] + "\n... [truncated]"
    return text


FS_DEFS = [
    {
        "name": "list_files",
        "description": (
            "List all files in Basil's sandbox folder. Use this when he asks "
            "what files he has, what's in his folder, or what notes exist."
        ),
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "read_file",
        "description": (
            "Read the contents of a file in Basil's sandbox. "
            "Use after list_files if he asks what's in a specific note, "
            "or directly if he names a file. Only works on files inside the sandbox."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The filename to read, e.g. 'mint.txt'. No paths or slashes."
                }
            },
            "required": ["filename"]
        }
    }
]

FS_FUNCS = {"list_files": list_files, "read_file": read_file}