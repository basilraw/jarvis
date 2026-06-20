"""CLI weather tool — orchestrator."""
import argparse
import json
import sys
import requests
from colorama import Fore, init

from api import fetch_weather
from formatter import extract_current, print_weather
from storage import save_to_history

init(autoreset=True)


def main():
    parser = argparse.ArgumentParser(description="Get the current weather for a city.")
    parser.add_argument("city", help="City name to look up")
    parser.add_argument("--save", action="store_true", help="Save this lookup to history.json")
    args = parser.parse_args()

    try:
        data = fetch_weather(args.city)
    except requests.exceptions.ConnectionError:
        print(Fore.RED + "Error: no internet connection.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(Fore.RED + "Error: request timed out.")
        sys.exit(1)
    except requests.exceptions.HTTPError:
        print(Fore.RED + f"Error: '{args.city}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(Fore.RED + f"Error: couldn't parse response — '{args.city}' might not exist.")
        sys.exit(1)

    weather = extract_current(data)
    print_weather(weather)

    if args.save:
        save_to_history(weather)
        print(Fore.GREEN + "Saved to history.json")


if __name__ == "__main__":
    main()