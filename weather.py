import argparse
import requests
import json
import sys
import datetime
import os
from colorama import Fore, Style, init

init(autoreset=True)

# Set up the argument parser
parser = argparse.ArgumentParser(description="Get the current weather for a city.")
parser.add_argument("city", help="City name to look up")
parser.add_argument("--save", action="store_true", help="Save this lookup to history.json")
args = parser.parse_args()

city = args.city
url = f"https://wttr.in/{city}?format=j1"

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.ConnectionError:
    print(Fore.RED + "Error: no internet connection.")
    sys.exit(1)
except requests.exceptions.Timeout:
    print(Fore.RED + "Error: request timed out.")
    sys.exit(1)
except requests.exceptions.HTTPError:
    print(Fore.RED + f"Error: '{city}' not found.")
    sys.exit(1)
except json.JSONDecodeError:
    print(Fore.RED + f"Error: couldn't parse response — '{city}' might not exist.")
    sys.exit(1)

current = data['current_condition'][0]
area = data['nearest_area'][0]

city_name = area['areaName'][0]['value']
country = area['country'][0]['value']
temp_c = current['temp_C']
feels_like = current['FeelsLikeC']
condition = current['weatherDesc'][0]['value']
humidity = current['humidity']
wind = current['windspeedKmph']

print(Fore.CYAN + Style.BRIGHT + f"\n--- Weather for {city_name}, {country} ---")
print(Fore.YELLOW + f"Temperature: {temp_c}°C (feels like {feels_like}°C)")
print(Fore.WHITE + f"Condition:   {condition}")
print(Fore.WHITE + f"Humidity:    {humidity}%")
print(Fore.WHITE + f"Wind:        {wind} km/h")

# Save to history if --save was passed
if args.save:
    HISTORY_FILE = "history.json"
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    else:
        history = []

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "city": city_name,
        "country": country,
        "temp_c": temp_c,
        "condition": condition,
    }
    history.append(entry)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

    print(Fore.GREEN + "Saved to history.json")