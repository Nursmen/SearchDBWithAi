'''
LLM which will take any json schema plus api endpoint plus method(post/get) and will use it as a tool.
'''

from openai import OpenAI
import json
import requests

client = OpenAI()

json_schema =   {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The customer's order ID.",
                    },
                },
                "required": ["order_id"],
                "additionalProperties": False,
            }

api_endpoint = "https://api.example.com/data"
method = "POST"
name = "get_delivery_date"
description = """Get the delivery date for a customer's order. Call this whenever you need to know the delivery date, for example when a customer asks 'Where is my package"""

tools = [
    {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": json_schema,
        }
    }
]

messages = []
messages.append({"role": "system", "content": "You are a helpful customer support assistant. Use the supplied tools to assist the user."})
messages.append({"role": "user", "content": "Hi, can you tell me the delivery date for my order?"})
messages.append({"role": "assistant", "content": "Hi there! I can help with that. Can you please provide your order ID?"})
messages.append({"role": "user", "content": "i think it is order_12345"})

response = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=messages,
    tools=tools
)

print(response)

tool_call = response.choices[0].message.tool_calls[0]
arguments = json.loads(tool_call.function.arguments)

print(tool_call.function.name)
print(arguments)

def get_from_db(user_id, tool_name, arguments):
    api_endpoint = "https://api.example.com/data"
    method = "POST"
    header_token = 'asdfsdf'
    response = requests.request(method, api_endpoint, json=arguments, headers={'Authorization': f'Bearer {header_token}'})
    return response.json()



#response = wrapper(api_endpoint, method, payload=arguments)