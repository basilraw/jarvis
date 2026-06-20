"""Weather API client."""
import requests


def fetch_weather(city, timeout=10):
    """Fetch raw weather data for a city from wttr.in.
    Returns parsed JSON dict. Raises requests/json exceptions on failure.
    """
    url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()