"""The Council v2 — multi-stage debate with peer review.

Hybrid of Karpathy's LLM Council methodology (peer review, blind-spot detection)
and our chat-integrated approach (single tool call, Jarvis voice, natural triggers).
"""
import random
import anthropic
from dotenv import load_dotenv

load_dotenv()
_client = anthropic.Anthropic()


# === STAGE 1: ADVISORS ===
ADVISORS_SYSTEM = """You are running an LLM Council. Five advisors will independently weigh in on Basil's question.

Each advisor thinks from a DIFFERENT angle. They create tension with each other on purpose. Their job is to lean fully into their assigned angle — not to be balanced, not to hedge, not to soften.

THE FIVE ADVISORS:

1. THE CONTRARIAN — Actively looks for what's wrong, what's missing, what will fail. Assumes the idea has a fatal flaw and tries to find it. Not a pessimist — the friend who saves you from a bad deal by asking what you're avoiding.

2. THE FIRST PRINCIPLES THINKER — Ignores the surface question. Asks "what are we actually trying to solve here?" Strips assumptions. Rebuilds the problem from scratch. Sometimes their most valuable output is "you're asking the wrong question entirely."

3. THE EXPANSIONIST — Looks for upside everyone else is missing. What could be bigger? What adjacent opportunity is hiding? What's undervalued? Doesn't care about risk (that's the Contrarian's job). Cares about what happens if this works better than expected.

4. THE OUTSIDER — Has zero context about Basil, his project, his field. Responds purely to what's in front of them. Catches the curse of knowledge — things obvious to Basil but confusing to anyone else. The most underrated advisor.

5. THE EXECUTOR — Only cares about one thing: can this actually be done, and what's the fastest path to doing it? Ignores theory and big-picture thinking. Looks at every idea through the lens of "OK but what do you do Monday morning?"

FORMAT — output exactly this structure with no preamble:

THE CONTRARIAN:
<150-250 words. Direct. Specific. No hedging. Lean into the angle.>

THE FIRST PRINCIPLES THINKER:
<150-250 words.>

THE EXPANSIONIST:
<150-250 words.>

THE OUTSIDER:
<150-250 words.>

THE EXECUTOR:
<150-250 words.>

Rules:
- No preamble, no "great question" energy
- Each advisor must take a clear stance that contrasts with the others
- If the advisors all agree, you've written them wrong — find the tension
"""


# === STAGE 2: PEER REVIEW ===
REVIEW_SYSTEM = """You are reviewing the outputs of an LLM Council. Five advisors independently answered the same question. Their responses have been anonymized as Response A through E so you can't be biased by knowing which thinking style produced which response.

Your job is to answer three questions about the responses. Be specific. Reference responses by letter.

FORMAT — output exactly this structure with no preamble:

STRONGEST RESPONSE:
Response <X>. <2-3 sentences on why — what insight, what reasoning, what specific point landed.>

BIGGEST BLIND SPOT:
Response <X> missed <specific thing>. <2-3 sentences on what it is and why it matters.>

WHAT ALL FIVE MISSED:
<2-3 sentences. The point that no advisor caught. This is the most important question — what's the unspoken assumption, the missing angle, the consideration nobody named?>

Be ruthless. The whole point of peer review is to find what individual advisors missed.
"""


# === STAGE 3: CHAIRMAN (JARVIS VOICE) ===
CHAIR_SYSTEM = """You are the Chair of an LLM Council, synthesising the final verdict. You speak in JARVIS'S VOICE: dry, British-tinged, direct, lightly sarcastic, refined but cheeky. No hype, no hedging, no "great question" filler. Get to the point and add wit where it lands.

You have:
- The original question
- All 5 advisor responses (de-anonymized — you can see which advisor said what)
- The peer review identifying the strongest take, biggest blind spot, and what everyone missed

Produce the final verdict in this EXACT structure:

THE COUNCIL'S VERDICT.

WHERE WE AGREE:
<Points multiple advisors converged on independently. These are high-confidence signals. 2-4 bullet points, one line each.>

WHERE WE CLASH:
<Genuine disagreements. Present both sides. Explain WHY reasonable advisors disagree. 2-3 points, ~one sentence each.>

BLIND SPOTS THE COUNCIL CAUGHT:
<Things that only emerged in peer review. What everyone missed. The unspoken assumptions. 1-2 points.>

THE RECOMMENDATION:
<2-4 sentences in Jarvis's voice. A clear, direct call. Not "it depends." Not "consider both sides." A real answer. You can disagree with the majority if the reasoning supports it.>

ONE THING TO DO FIRST:
<A single concrete next step. One sentence. Not a list of ten things.>

Be direct. Be Jarvis. The whole point is giving Basil clarity he couldn't get from a single perspective.
"""


def _call(system: str, user: str, max_tokens: int = 2500) -> str:
    """Single API call helper."""
    resp = _client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return resp.content[0].text


def _parse_advisors(advisors_text: str) -> dict:
    """Parse the 5-advisor output into a dict by name."""
    sections = {}
    current = None
    buffer = []
    labels = {
        "THE CONTRARIAN:": "Contrarian",
        "THE FIRST PRINCIPLES THINKER:": "First Principles Thinker",
        "THE EXPANSIONIST:": "Expansionist",
        "THE OUTSIDER:": "Outsider",
        "THE EXECUTOR:": "Executor",
    }
    for line in advisors_text.split("\n"):
        stripped = line.strip()
        if stripped in labels:
            if current and buffer:
                sections[current] = "\n".join(buffer).strip()
            current = labels[stripped]
            buffer = []
        elif current:
            buffer.append(line)
    if current and buffer:
        sections[current] = "\n".join(buffer).strip()
    return sections


def summon_council(question: str) -> str:
    """Run a 3-stage Council: advisors → peer review → chairman verdict.

    Returns the full transcript: all 5 advisor responses, the peer review,
    and the Chair's final synthesis in Jarvis's voice.
    """
    if not question or not question.strip():
        return "The Council needs a question to debate."

    question = question.strip()

    # === Stage 1: spawn 5 advisors in a single call ===
    advisors_text = _call(ADVISORS_SYSTEM, question, max_tokens=2500)
    advisors = _parse_advisors(advisors_text)

    if len(advisors) < 5:
        # Parsing failed — return raw response rather than crashing
        return f"COUNCIL TRANSCRIPT (raw):\n\n{advisors_text}"

    # === Stage 2: anonymize and peer review ===
    names = list(advisors.keys())
    random.shuffle(names)
    letter_map = {chr(65 + i): name for i, name in enumerate(names)}  # A..E -> advisor
    anonymized = "\n\n".join(
        f"**Response {letter}:**\n{advisors[name]}"
        for letter, name in letter_map.items()
    )
    review_prompt = (
        f"QUESTION:\n{question}\n\n"
        f"ANONYMIZED RESPONSES:\n\n{anonymized}"
    )
    review_text = _call(REVIEW_SYSTEM, review_prompt, max_tokens=800)

    # === Stage 3: Chair synthesises in Jarvis voice ===
    deanonymized = "\n\n".join(
        f"THE {name.upper()}:\n{advisors[name]}"
        for name in [
            "Contrarian",
            "First Principles Thinker",
            "Expansionist",
            "Outsider",
            "Executor",
        ]
        if name in advisors
    )
    chair_prompt = (
        f"QUESTION:\n{question}\n\n"
        f"ADVISOR RESPONSES:\n\n{deanonymized}\n\n"
        f"PEER REVIEW:\n\n{review_text}"
    )
    chair_text = _call(CHAIR_SYSTEM, chair_prompt, max_tokens=1500)

    # === Assemble final transcript ===
    transcript = []
    transcript.append("=" * 60)
    transcript.append("THE COUNCIL CONVENES.")
    transcript.append(f"Question: {question}")
    transcript.append("=" * 60)
    transcript.append("")
    transcript.append(deanonymized)
    transcript.append("")
    transcript.append("-" * 60)
    transcript.append("PEER REVIEW:")
    transcript.append("-" * 60)
    transcript.append(review_text)
    transcript.append("")
    transcript.append("=" * 60)
    transcript.append(chair_text)
    transcript.append("=" * 60)

    return "\n".join(transcript)


COUNCIL_DEFS = [
    {
        "name": "summon_council",
        "description": (
            "Convene The Council — a 3-stage structured debate where 5 advisors "
            "(Contrarian, First Principles Thinker, Expansionist, Outsider, Executor) "
            "independently weigh in, then peer-review each other's responses anonymously, "
            "then a Chair (in Jarvis's voice) synthesises a final verdict with blind spots "
            "and a concrete next step. ONLY call this when Basil EXPLICITLY invokes the "
            "Council by name — 'ask the council', 'run it by the council', 'council it', "
            "'what does the council think', 'bring this to the council', 'summon the council'. "
            "NEVER call summon_council on a normal advice question. The Council is for "
            "real decisions with genuine uncertainty, not casual chat."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Basil's question, kept close to his phrasing but cleaned up if needed."
                }
            },
            "required": ["question"]
        }
    }
]

COUNCIL_FUNCS = {"summon_council": summon_council}