"""Bare-bones demo of tool use — Anthropic's canonical example."""
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# Step 1: Define a tool. This is just a description for Claude.
# It says: "there's a tool called get_weather, here's what it does, here's what it takes."
tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather in a given location.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and country, e.g. 'Amman, Jordan'"
                }
            },
            "required": ["location"]
        }
    }
]


def fake_get_weather(location):
    """The actual tool. For now, just returns a fake fixed value."""
    print(f"  >> [tool ran: fake_get_weather(location='{location}')]")
    return f"The weather in {location} is 28C and sunny."


# Step 2: Send a message that should trigger the tool
print(">> Sending message to Claude...")
messages = [
    {"role": "user", "content": "What's the weather like in Amman right now?"}
]

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=500,
    tools=tools,
    messages=messages,
)

print(f">> Claude's first response. stop_reason: {response.stop_reason}")
print(f">> Content blocks: {response.content}")

# Step 3: Check whether Claude wants to use a tool
if response.stop_reason == "tool_use":
    # Find the tool_use block in the response
    tool_use_block = next(b for b in response.content if b.type == "tool_use")
    tool_name = tool_use_block.name
    tool_input = tool_use_block.input
    tool_use_id = tool_use_block.id

    print(f"\n>> Claude wants to call tool '{tool_name}' with input {tool_input}")

    # Step 4: Actually run the tool
    if tool_name == "get_weather":
        tool_result = fake_get_weather(**tool_input)

    # Step 5: Send the tool result back as a new message
    # The conversation now has 3 turns: user question, Claude's tool request, our tool result
    messages.append({"role": "assistant", "content": response.content})
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": tool_result
            }
        ]
    })

    # Step 6: Get Claude's final reply using the tool result
    print("\n>> Sending tool result back to Claude...")
    final = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        tools=tools,
        messages=messages,
    )
    print(f"\n>> Final reply: {final.content[0].text}")
else:
    print(f"\n>> Claude didn't use a tool. Reply: {response.content[0].text}")