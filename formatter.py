"""Format weather data for display."""
from colorama import Fore, Style


def extract_current(data):
    """Pull current conditions out of the raw API response into a flat dict."""
    current = data['current_condition'][0]
    area = data['nearest_area'][0]
    return {
        "city": area['areaName'][0]['value'],
        "country": area['country'][0]['value'],
        "temp_c": current['temp_C'],
        "feels_like": current['FeelsLikeC'],
        "condition": current['weatherDesc'][0]['value'],
        "humidity": current['humidity'],
        "wind": current['windspeedKmph'],
    }


def print_weather(weather):
    """Pretty-print the weather summary in colour."""
    print(Fore.CYAN + Style.BRIGHT + f"\n--- Weather for {weather['city']}, {weather['country']} ---")
    print(Fore.YELLOW + f"Temperature: {weather['temp_c']}°C (feels like {weather['feels_like']}°C)")
    print(Fore.WHITE + f"Condition:   {weather['condition']}")
    print(Fore.WHITE + f"Humidity:    {weather['humidity']}%")
    print(Fore.WHITE + f"Wind:        {weather['wind']} km/h")