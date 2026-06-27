"""A basic chat loop with Claude."""
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

print("Chat with Claude. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")
    
    if user_input.lower() == "quit":
        print("Goodbye!")
        break
    
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        messages=[
            {"role": "user", "content": user_input}
        ]
    )
    
    print(f"\nClaude: {message.content[0].text}\n")
    print(f"  [tokens used: {message.usage.input_tokens} in / {message.usage.output_tokens} out, stop reason: {message.stop_reason}]\n")