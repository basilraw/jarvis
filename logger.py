import json
import datetime
import os

LOG_FILE = "log.json"

def log(message):
    # If the log file exists, load existing entries. If not, start fresh.
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            entries = json.load(f)
    else:
        entries = []
    
    # Build the new entry with a timestamp
    new_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "message": message
    }
    entries.append(new_entry)
    
    # Write the whole updated list back
    with open(LOG_FILE, "w") as f:
        json.dump(entries, f, indent=2)


# Test it — log a few things
log("Started Day 3")
log("Learned files and JSON")
log("Built the logger")

# Read everything back and pretty-print it
print("--- All log entries ---")
with open(LOG_FILE, "r") as f:
    entries = json.load(f)

for entry in entries:
    print(f"[{entry['timestamp']}] {entry['message']}")