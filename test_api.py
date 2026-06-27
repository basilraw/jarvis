"""First test of the Anthropic API."""
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "Hello! Introduce yourself in two sentences and tell me what 2+2 equals."}
    ]
)

print(message.content[0].text)