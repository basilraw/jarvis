"""Weather tool."""
import requests
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


WEATHER_DEFS = [
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
                    "description": "City and optionally country, e.g. 'Amman', 'Tokyo', 'London, UK'."
                }
            },
            "required": ["location"]
        }
    }
]

WEATHER_FUNCS = {"get_weather": get_weather}