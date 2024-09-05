functions = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given city",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g., San Francisco, CA",
                },
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    },
    {
        "name": "search_files",
        "description": "Search files in a specified directory",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "The directory path where the search should be performed",
                },
                "filename": {"type": "string", "description": "The name of the file to search for"},
            },
            "required": ["directory", "filename"],
        },
    },
]

import openai

response = openai.ChatCompletion.create(
    model="gpt-4-0613",  # You can use other models like gpt-3.5-turbo
    messages=[
        {"role": "user", "content": "Can you check the weather in New York?"},
    ],
    functions=functions,
    function_call="auto",  # Auto will let the model decide if it needs to call a function
)
    
def get_current_weather(location, unit="celsius"):
    # Implement the logic for getting weather
    return f"The current temperature in {location} is 25 {unit}"

if response["choices"][0]["finish_reason"] == "function_call":
    function_name = response["choices"][0]["message"]["function_call"]["name"]
    arguments = response["choices"][0]["message"]["function_call"]["arguments"]

    if function_name == "get_current_weather":
        # Implement the logic for getting weather
        result = get_current_weather(**arguments)
        # Send the result back to the model
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[
                {"role": "user", "content": "Can you check the weather in New York?"},
                {"role": "assistant", "function_call": {"name": "get_current_weather", "arguments": arguments}},
                {"role": "function", "name": function_name, "content": result},
            ],
        )

final_output = response["choices"][0]["message"]["content"]
print(final_output)