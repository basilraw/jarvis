# Jarvis (summer build)

A growing AI assistant project I'm building over summer 2026. Currently a Python CLI weather tool — by week 12 it'll be a voice-controlled assistant with vision running on a Raspberry Pi, controlling a custom streaming receiver.

## Current features

- `weather.py` — fetches live weather for any city via wttr.in, prints a clean coloured summary, optionally saves history.

## Setup

```bash
git clone https://github.com/basilraw/jarvis.git
cd jarvis
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python weather.py Amman
python weather.py London --save
python weather.py --help
```

## Built with

- Python 3.14
- requests, colorama
- Some grit and a lot of debugging

## Roadmap

- [x] Week 1 — Python foundations + CLI weather tool
- [x] Week 2 — Linux, Git, GitHub
- [ ] Week 3 — Claude API chatbot
- [ ] Week 4 — Tool use (give the assistant skills)
- [ ] Week 5 — Voice (speech in/out)
- [ ] Week 6 — Wake word
- [ ] Week 7 — Raspberry Pi
- [ ] Week 8 — Vision
- [ ] Weeks 9–11 — Custom receiver + integration
- [ ] Week 12 — Polish + demo