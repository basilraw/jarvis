"""Time and math tools."""
import datetime
from zoneinfo import ZoneInfo
from simpleeval import simple_eval, NameNotDefined, FunctionNotDefined, InvalidExpression


def get_current_time(timezone: str = "Asia/Amman") -> str:
    """Get the current date and time in a given timezone."""
    try:
        tz = ZoneInfo(timezone)
    except Exception:
        return f"Unknown timezone '{timezone}'. Try names like 'Asia/Amman', 'Europe/London', 'America/New_York'."
    now = datetime.datetime.now(tz)
    return now.strftime("%A %d %B %Y, %H:%M") + f" ({timezone})"


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


TIMEMATH_DEFS = [
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
            "always use this tool to be accurate. Supports +, -, *, /, **, %, and parentheses."
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
    }
]

TIMEMATH_FUNCS = {"get_current_time": get_current_time, "calculate": calculate}