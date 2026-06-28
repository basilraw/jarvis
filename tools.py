"""Tools that Jarvis can call."""
import os
from pathlib import Path
import requests
import datetime
from zoneinfo import ZoneInfo
from simpleeval import simple_eval, NameNotDefined, FunctionNotDefined, InvalidExpression


from api import fetch_weather
from formatter import extract_current


def get_weather(location: str) -> str:
    """Fetch real weather for a city and return a short summary string."""
    try:
        data = fetch_weather(location)
        w = extract_current(data)
        return (
            f"{w['city']}, {w['country']}: "
            f"{w['temp_c']}°C (feels like {w['feels_like']}°C), "
            f"{w['condition']}, humidity {w['humidity']}%, wind {w['wind']} km/h."
        )
    except requests.exceptions.HTTPError:
        return f"Couldn't find weather data for '{location}'."
    except requests.exceptions.ConnectionError:
        return "No internet connection — can't reach the weather API."
    except requests.exceptions.Timeout:
        return "Weather API took too long to respond."
    except (KeyError, IndexError):
        return f"Weather data for '{location}' came back malformed."


# The schema Claude reads to decide when/how to call get_weather.
# Notice: this is a list (you'll add more tools to it later).
# === FILE SYSTEM TOOL ===
# Hardcoded sandbox path. Claude can ONLY read files inside here.
SANDBOX_DIR = Path("sandbox").resolve()


def _safe_path(filename: str) -> Path | None:
    """Resolve a filename to a real path inside the sandbox, or None if unsafe."""
    try:
        # Combine the sandbox with the requested filename, then resolve.
        # .resolve() expands any '..' tricks like 'foo/../../../etc/passwd'
        target = (SANDBOX_DIR / filename).resolve()
    except Exception:
        return None
    # The resolved path MUST still be inside the sandbox folder.
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
    # Cap reading at ~10KB to avoid dumping massive files into the API
    MAX_BYTES = 10_000
    try:
        text = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"'{filename}' isn't a readable text file."
    if len(text) > MAX_BYTES:
        text = text[:MAX_BYTES] + "\n... [truncated]"
    return text

# === TIME TOOL ===

def get_current_time(timezone: str = "Asia/Amman") -> str:
    """Get the current date and time in a given timezone."""
    try:
        tz = ZoneInfo(timezone)
    except Exception:
        return f"Unknown timezone '{timezone}'. Try names like 'Asia/Amman', 'Europe/London', 'America/New_York'."
    now = datetime.datetime.now(tz)
    return now.strftime("%A %d %B %Y, %H:%M") + f" ({timezone})"


# === MATH TOOL ===

def calculate(expression: str) -> str:
    """Safely evaluate a math expression. Supports +, -, *, /, **, %, parentheses."""
    try:
        result = simple_eval(expression)
        return f"{expression} = {result}"
    except (NameNotDefined, FunctionNotDefined):
        return f"Couldn't evaluate '{expression}' — only basic math operators allowed."
    except InvalidExpression as e:
        return f"Invalid expression: {e}"
    except ZeroDivisionError:
        return "Division by zero."
    except Exception as e:
        return f"Couldn't evaluate '{expression}': {e}"
TOOL_DEFINITIONS = [
    {
        "name": "get_weather",
        "description": (
            "Get the current real-world weather conditions for a city. "
            "Use this whenever Basil asks about weather, temperature, "
            "rain, or outdoor conditions for any location."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": (
                        "City and optionally country, e.g. 'Amman', "
                        "'Tokyo', 'London, UK'."
                    )
                }
            },
            "required": ["location"]
        }
    },
    {
        "name": "list_files",
        "description": (
            "List all files in Basil's sandbox folder. Use this when he asks "
            "what files he has, what's in his folder, or what notes exist."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
        }
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
    },
    {
        "name": "get_current_time",
        "description": (
            "Get the current real-world date and time. Use whenever Basil asks "
            "what time it is, what day it is, or anything time-related. "
            "Defaults to Amman, Jordan but accepts other timezones."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": (
                        "IANA timezone name like 'Asia/Amman', 'Europe/London', "
                        "'America/New_York', 'Asia/Tokyo'. Defaults to Asia/Amman."
                    )
                }
            }
        }
    },
    {
        "name": "calculate",
        "description": (
            "Evaluate a math expression. Use this whenever Basil asks for any "
            "arithmetic, no matter how simple. Don't compute math yourself — "
            "always use this tool to be accurate. Supports +, -, *, /, **, %, "
            "and parentheses."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A math expression like '2+2', '15*73', '(40+8)/3', '2**10'."
                }
            },
            "required": ["expression"]
        }
    },
]


# Dispatcher: maps a tool name to the actual function to call.
# When Claude says "I want to call get_weather", we look it up here.
TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "list_files": list_files,
    "read_file": read_file,
    "get_current_time": get_current_time,
    "calculate": calculate,
}