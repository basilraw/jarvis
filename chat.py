"""Chat with Claude — now with conversation memory."""
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# This list lives across all turns. Each item is {role, content}.
conversation = []

print("Chat with Claude. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        print("Goodbye!")
        break

    # Add YOUR message to the history before sending
    conversation.append({"role": "user", "content": user_input})

    # Send the FULL conversation history every turn
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        messages=conversation
    )

    # Get Claude's text reply
    reply = message.content[0].text

    # Add Claude's reply to the history too — critical
    conversation.append({"role": "assistant", "content": reply})

    print(f"\nClaude: {reply}\n")
    print(f"  [tokens: {message.usage.input_tokens} in / {message.usage.output_tokens} out · history: {len(conversation)} messages]\n")