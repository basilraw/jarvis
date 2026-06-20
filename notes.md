# Week 1 — Python Foundations

Finished in 6 days. Took me from school-level Python (loops, functions, classes)
to having a working CLI tool that talks to the internet, handles errors,
takes flags, and saves history.

## What I built

- **stdlib_test.py** — practice using math, datetime, random from Python's built-in library
- **utils.py** — my first custom module (greet, current_time, random_choice)
- **main.py** — imports utils.py and uses its functions
- **colors.py** — colored terminal output with colorama (the dashboard look for Jarvis later)
- **requirements.txt** — every package my project needs, with versions
- **files.py** — reading and writing plain text files
- **json_test.py** — writing Mint's data to JSON and reading it back
- **logger.py** — appends timestamped entries to log.json (the same pattern Jarvis will use for chat history)
- **weather.py** — full CLI weather app. Takes a city, fetches live weather, formats output, handles errors, optional --save flag for history

## New concepts I learned

- **Virtual environment (.venv)**: a per-project sandbox so my packages don't fight with other projects' packages
- **pip + requirements.txt**: pip installs packages from PyPI; requirements.txt is the ingredient list so anyone (or my future Pi) can install the same versions
- **Modules and imports**: any .py file is a module. Stdlib has hundreds; you can also write your own and import them
- **File I/O with `with open(...)`**: 'r' = read, 'w' = write (overwrites), 'a' = append. `with` auto-closes the file
- **JSON**: text format for structured data. json.dump writes Python dict/list to a file, json.load reads it back
- **HTTP / APIs**: every internet call is request → response. 200 = OK, 4xx/5xx = error
- **try / except**: catches errors so the program doesn't crash. Always name the specific exception (never bare `except:`)
- **f-string formatting**: `:.2f` for decimals, `:>10` for alignment, `:,` for thousand separators, `%Y-%m-%d` for dates
- **List / dict comprehensions**: one-line way to build lists or dicts from another sequence
- **argparse**: handles command-line arguments properly. Gives you --help and error messages for free

## Patterns to remember

- **Read → append → write** for any JSON file you keep updating (used in logger.py and the --save flag of weather.py)
- **Wrap every network call in try/except** with timeout, raise_for_status, and specific exception types
- **Always use `with open(...)`** instead of plain `open()` so files get closed even if something errors
- **Use venv from day one** of every new project

## Things I want to dig into later

- The wttr.in API has hourly forecasts and multi-day data I didn't touch — could make a "weather tomorrow" feature
- argparse can do more (subcommands, types, defaults) — worth a deeper look
- Why does importing a module create a __pycache__ folder? Bytecode caching, but how exactly?

## Where this leads

Week 2 = Linux + Git. Get everything on GitHub.
Week 3 = Claude API. weather.py becomes the template for Jarvis's `get_weather` tool.
Week 7 = same code, but running on a Raspberry Pi.
## Git status
- Project is now version-controlled with git
## Git workflow learned
- git init / add / commit / log
- Branches for risky changes
- Merging back into main