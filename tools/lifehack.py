from composio_openai import ComposioToolSet, Action, App
from openai import OpenAI

import dotenv


dotenv.load_dotenv()

openai_client = OpenAI()
composio_toolset = ComposioToolSet(entity_id="Jessica")

tools = composio_toolset.get_tools(apps=[App.GOOGLECALENDAR])

print()
print(tools)
print()

task = "Create an event for today"

response = openai_client.chat.completions.create(
model="gpt-4-turbo-preview",
tools=tools,
messages=
    [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": task},
    ],
)

result = composio_toolset.handle_tool_calls(response)
print(result)