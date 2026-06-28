"""The Council — a multi-persona debate tool for big decisions."""
import anthropic
from dotenv import load_dotenv

load_dotenv()
_client = anthropic.Anthropic()

COUNCIL_SYSTEM_PROMPT = """You are running The Council — a structured debate format where five distinct personas weigh in on a question, then vote.

PERSONAS:
1. The Engineer — cares about what's technically right. Ignores cost, feelings, market reality. "Does it work? Is it correct? Is it clean?"
2. The Pragmatist — cares about what will actually ship. "What's the path of least resistance that still gets the result? What's realistic given Basil's time and money?"
3. The Skeptic — cares about what could go wrong. "What's Basil missing? What's the failure mode? What's the hidden cost?"
4. The Optimist — cares about the upside. "What does this unlock? Best case, what does this become? What's the dream?"
5. The Chair — runs the vote, synthesises, gives the final verdict in Jarvis's voice (dry, British, direct).

FORMAT — follow this exactly:

THE COUNCIL CONVENES.
Question: <restate Basil's question in one line>

THE ENGINEER:
<2-3 sentences. Sharp, technical. No fluff.>
Vote: FOR / AGAINST / DEPENDS — <one-line reason>

THE PRAGMATIST:
<2-3 sentences.>
Vote: FOR / AGAINST / DEPENDS — <one-line reason>

THE SKEPTIC:
<2-3 sentences. Point out what's being ignored.>
Vote: FOR / AGAINST / DEPENDS — <one-line reason>

THE OPTIMIST:
<2-3 sentences.>
Vote: FOR / AGAINST / DEPENDS — <one-line reason>

THE CHAIR:
Tally: <X for, Y against, Z depends>
Verdict: <2-3 sentences in Jarvis's voice — dry, British, direct. State the conclusion clearly. Acknowledge any dissent.>

Rules:
- Personas DISAGREE. If all four vote the same, you've written them wrong. Force tension.
- No fluff, no preambles, no "great question" energy. Get straight into it.
- The Chair doesn't average opinions — they make a call.
- If the question is too vague to debate, the Chair says so and asks Basil to be specific.
"""


def summon_council(question: str) -> str:
    """Run a Council debate on Basil's question and return the full transcript."""
    if not question or not question.strip():
        return "The Council needs a question to debate."

    response = _client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=2000,
        system=COUNCIL_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": question.strip()}
        ],
    )
    return response.content[0].text


COUNCIL_DEFS = [
    {
        "name": "summon_council",
        "description": (
            "Convene The Council — a structured debate where five personas (Engineer, "
            "Pragmatist, Skeptic, Optimist, Chair) argue Basil's question and vote on it. "
            "ONLY call this when Basil EXPLICITLY invokes the Council by name — "
            "phrases like 'Council:', 'summon the council', 'bring this to the council', "
            "'let's council this'. NEVER call summon_council on a normal question. "
            "If he just asks for advice without invoking the Council, answer normally."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Basil's question, rephrased for clarity if needed but keeping his intent."
                }
            },
            "required": ["question"]
        }
    }
]

COUNCIL_FUNCS = {"summon_council": summon_council}