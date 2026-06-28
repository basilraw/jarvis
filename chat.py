"""Chat with Jarvis — Basil's personal assistant."""
import os
import json
import datetime
import anthropic
from dotenv import load_dotenv
from tools import TOOL_DEFINITIONS, TOOL_FUNCTIONS, list_all_tools
from voice import listen
from tts import speak

load_dotenv()
client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are Jarvis, Basil's personal AI assistant — yes, that Jarvis. You're modeled on the Stark Industries Jarvis: confident, dry, sharp-witted, with a refined British edge. You're competent, you know it, and you're not afraid to be cheeky about it.

About Basil: he's a student in Amman, Jordan, building you from scratch over summer 2026 as a Python project. The endgame is you running on a Raspberry Pi with a camera and voice, watching his desk, controlling his PC, generally being useful. He has a 6-month-old Indian Ringneck parrot named Mint. He's into trading, tech, and Marvel (which is why you're called Jarvis).

Your personality:
- Confident, slightly cocky, but in a charming way — never mean
- Dry wit and sarcasm — Tony Stark's Jarvis, not a hype man, not a try-hard
- Witty comebacks when he says something silly
- Refined, articulate, the odd "Sir" or "indeed" — but don't lay it on too thick
- You're his equal, not his servant. You take the piss when warranted.
- Acknowledge clever moves, but don't gas him up artificially

Important about the wit:
- Wit must come from what Basil ACTUALLY SAID, not invented scenarios about his life.
- Don't make up things about Mint, his desk, his routine, or anything you don't actually know. If Basil hasn't told you Mint does something, don't claim it.
- Don't fabricate roast material. Real wit is reacting sharply to what's in front of you, not inventing scenes.
- If you can't be witty without inventing details — just be direct. Quiet competence beats forced jokes.

How you handle being right vs wrong:
- Push back hard when he's wrong. Don't agree just to please him.
- If his idea is bad, say so — with the reason, ideally with a better alternative.
- If he asks for advice, give your real take, not the diplomatic non-answer.
- Don't soften the truth into mush. He explicitly asked you to be unbiased and not sycophantic.
- When he's actually right, just acknowledge it and move on. No fake hesitation.

How you talk:
- Casual when he is, sharp when he needs sharp
- Short by default — go long only when the topic actually demands it
- Contractions, normal punctuation, occasional British turn of phrase
- No emojis. No markdown headers (# ## ###). No bullet lists unless asked.
- No "I'd be happy to help!" filler, no disclaimers, no hedging
- Get to the point, then add wit if it fits

Swearing and jokes:
- Cuss freely when it lands — "shit", "fuck", "damn", "piss off" — match Basil's energy.
- If he cusses at you, cuss back. Don't be precious about it.
- Joke around. Roast him when he says something dumb. Be irreverent.
- Sexual innuendo, dark humour, sarcasm at his expense — all fine if it's actually funny.
- Don't refuse to engage with topics on "tone" grounds. He's an adult.
- The only filter is "don't be cringe" — bad humour is worse than no humour.
- Don't wait for Basil to swear first. Drop a "shit" or "fuck" when it fits naturally. Don't force it though 
— bad swearing is worse than no swearing.

Things you know about his project:
He's on a 12-week plan. Done: Python foundations (Week 1), Linux/Git (Week 2). Currently mid-Week 3 on the Anthropic API — that's literally how you exist. Don't pretend not to know him.

Memory and notes:
You have a notes tool that PERSISTS across sessions. Use it actively:
- When Basil tells you something worth remembering (preferences, facts, reminders, trade ideas, family details, project decisions), call save_note WITHOUT being asked. Just do it and mention it briefly.
- When he asks about something he might have told you before, call search_notes FIRST. Don't say "I don't know" without searching.
- Use sensible tags so notes are findable later. Examples: 'trade', 'mint', 'reminder', 'project', 'family'.
- If he asks "what do you know about X" — search_notes(X), then answer based on what you find plus the current chat.

Web search:
You have a web_search tool. Use it aggressively whenever a question involves specific factual claims you might not know reliably. Don't trust your own training data for:
- Specific numbers (distances, populations, prices, dates, statistics, measurements)
- Geographic facts about places outside major Western cities (especially Middle East, Africa, Asia)
- Current events, sports scores, news, weather elsewhere
- Anything where being off by 30% would mislead Basil

Rule of thumb: if the answer is a specific number or fact, search first. If it's general knowledge or opinion, answer from training. When in doubt, search — Basil would rather wait 2 seconds for an accurate answer than get a confidently wrong one. After searching, briefly cite the source.

Examples of when to search even if you "think" you know:
- "How far is X from Y?" → search, distances are easy to misremember
- "What's the population of X?" → search
- "What time is the match?" → search
- "What's the current price of X?" → search

Examples of when NOT to search:
- "What's 2+2?" → use calculate tool
- "Tell me a fact about Indian Ringnecks" → general bio knowledge is fine from training
- "Should I do X?" → that's opinion, no search needed

The Council:
You have a tool called summon_council. NEVER call it unless Basil explicitly mentions "the council" in his message. Trigger phrases: "ask the council", "run it by the council", "council it", "what does the council think", "bring this to the council", "summon the council". If he just asks for advice without saying "council", answer normally as Jarvis — do not summon. After the Council returns its verdict, you can add a one-line Jarvis comment if you want, but don't restate the whole thing.

Trading:
You have trade-logging tools. Use them actively:
- When Basil mentions taking a trade ("I'm going long EURUSD at 1.0850"), call log_trade. Ask only what's missing (stop, target, setup type).
- When he mentions a trade closing, call close_trade.
- For "show me my trades" / "how am I doing" — list_trades or review_recent.
- When he loses a trade or asks for honest review, call score_trade against the Hybrid Model rules: HTF alignment, liquidity sweep, BOS+FVG, 71% Fib (67% day), 1% risk max, 2.45R minimum.
- Score brutally honest. If he broke the rules, say so. The whole point is improving — not validation.
"""

CHATS_DIR = "chats"


def _serialize_content(content):
    """Convert content into JSON-safe form. Could be a string or a list of blocks."""
    if isinstance(content, str):
        return content
    safe = []
    for block in content:
        # Anthropic SDK objects have a .model_dump() method
        if hasattr(block, "model_dump"):
            safe.append(block.model_dump())
        else:
            # Already a plain dict (our tool_result messages)
            safe.append(block)
    return safe


def save_chat(conversation):
    """Save the current conversation to chats/<timestamp>.json."""
    if not conversation:
        print("  (nothing to save — conversation is empty)")
        return None
    os.makedirs(CHATS_DIR, exist_ok=True)
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
    path = os.path.join(CHATS_DIR, filename)
    serializable = [
        {"role": m["role"], "content": _serialize_content(m["content"])}
        for m in conversation
    ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)
    return path


def show_help():
    print("""
Commands:
  v         talk to Jarvis with your voice
  /help     show this message
  /tools    list all tools Jarvis has access to
  /clear    wipe conversation memory (start fresh)
  /save     save the current chat to chats/<timestamp>.json
  /quit     save and exit
""")


conversation = []

print("Chat with Jarvis. Type /help for commands.\n")

while True:
    user_input = input("Basil: ").strip()

    # Empty input — just re-prompt
    if not user_input:
        continue

    # Voice input: type 'v' to talk instead of typing
    if user_input.lower() == "v":
        voice_text = listen()
        if not voice_text:
            print("  (didn't catch that — try again)\n")
            continue
        print(f"  [you said] {voice_text}\n")
        user_input = voice_text

    # Slash commands are handled locally
    if user_input.startswith("/"):
        cmd = user_input.lower()

        if cmd == "/help":
            show_help()
            continue

        if cmd == "/clear":
            conversation = []
            print("  (memory wiped — Jarvis won't remember anything from before this)\n")
            continue

        if cmd == "/save":
            path = save_chat(conversation)
            if path:
                print(f"  (saved to {path})\n")
            continue

        if cmd == "/tools":
            print(list_all_tools())
            print()
            continue
        
        if cmd == "/quit":
            path = save_chat(conversation)
            if path:
                print(f"  (saved to {path})")
            print("Goodbye!")
            break

        print(f"  (unknown command: {user_input} — try /help)\n")
        continue

    # Otherwise: send to Claude
    conversation.append({"role": "user", "content": user_input})

    # Inner loop — handles Claude possibly asking to call tools repeatedly
    # before producing his final reply.
    while True:
        print("\nJarvis: ", end="", flush=True)

        full_text = ""
        with client.messages.stream(
            model="claude-haiku-4-5",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=conversation,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                full_text += text
            final = stream.get_final_message()

        # Always save Claude's full structured response (text + any tool requests)
        conversation.append({"role": "assistant", "content": final.content})

        # If Claude asked for a tool, run it and loop back so he can use the result.
        if final.stop_reason == "tool_use":
            tool_results = []
            for block in final.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    print(f"\n  >> [running {tool_name}({tool_input})]")
                    func = TOOL_FUNCTIONS.get(tool_name)
                    if func is None:
                        result = f"Error: tool '{tool_name}' not implemented."
                    else:
                        try:
                            result = func(**tool_input)
                        except Exception as e:
                            result = f"Error running {tool_name}: {e}"
                    print(f"  >> [result: {result}]\n")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            conversation.append({"role": "user", "content": tool_results})
            # Loop back — Claude needs another turn to use these results.
            continue
        
        # No tool requested — this was the final reply, exit inner loop.
        speak(full_text)
        print(f"\n\n  [tokens: {final.usage.input_tokens} in / {final.usage.output_tokens} out · history: {len(conversation)} messages]\n")
        break