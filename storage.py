"""Persist weather lookups to history.json."""
import json
import os
import datetime

HISTORY_FILE = "history.json"


def save_to_history(weather):
    """Append a weather entry to history.json (creates the file if needed)."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    else:
        history = []

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "city": weather['city'],
        "country": weather['country'],
        "temp_c": weather['temp_c'],
        "condition": weather['condition'],
    }
    history.append(entry)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)