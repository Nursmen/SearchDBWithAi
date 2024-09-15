"""
LLM takes data from csv and use it as a tool
"""

import pandas as pd


from openai import OpenAI
import json
import requests

from typing import Optional

def useTool(tool_name:str, query:str, openai_api_key:str, tool_api_key:Optional[str] = None, file_path: Optional[str] = None) -> int:
    """
    Uses the tool from the csv file or my own tool

    Returns:
        200: Success
        100: Need API KEY
        400: Error
    """


    df = pd.read_csv('./tools/Tools - Sheet1.csv')

    tool = df[df.Name == tool_name].to_dict(orient='records')[0]

    if tool_api_key is None and tool['Need API KEY'] != 'No':
        return 100

    if 'self.com' in tool['API']:
        tool['API'] = tool['API'].replace('https://self.com', 'http://localhost:8000')


    print(tool)
    print()

    # Construct the tool
    tools = [
        {
            "type": "function",
            "function": {
                "name": tool['Name'],
                "description": tool['Description'],
                "parameters": eval(tool['Format Output'])
            }
        }
    ]


    client = OpenAI(api_key=openai_api_key)

    messages = []
    messages.append({"role": "system", "content": "You are a helpful customer support assistant. Use the supplied tools to assist the user."})
    messages.append({"role": "user", "content": query})


    # Call the tool
    try:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=messages,
            tools=tools
        )
        print(response)

        tool_call = response.choices[0].message.tool_calls[0]
        arguments = json.loads(tool_call.function.arguments)

        print(f"Function called: {tool_call.function.name}")
        print(f"Arguments: {arguments}")
    except Exception as e:


        print(f"An error occurred: {e}")
        print(f"Error details: {e.response.text if hasattr(e, 'response') else 'No additional details'}")
        return 400

    api_endpoint = tool['API']
    method = tool['Method']
    need_api_key = tool['Need API KEY'].lower()

    # Request to the tool
    try:


        if method == 'GET':

            if need_api_key == 'search':
                arguments['access_key'] = tool_api_key
                api_response = requests.get(api_endpoint, params=arguments)
            else:
                api_response = requests.get(api_endpoint, params=arguments)

        elif method == 'POST':
            if file_path:
                # Handle file upload
                with open(file_path, 'rb') as file:
                    files = file.read()
                    if need_api_key == 'no':
                        api_response = requests.post(api_endpoint, data=files)
                    elif need_api_key == 'bearer':
                        headers = {'Authorization': f'Bearer {tool_api_key}'}
                        api_response = requests.post(api_endpoint, data=files, headers=headers)
                    elif need_api_key == 'header':
                        headers = {'authorization': f'{tool_api_key}'}
                        api_response = requests.post(api_endpoint, data=files, headers=headers)
                    else:
                        print("Method not supported")
                        return 400
            else:
                # JSON payload without file
                if need_api_key == 'no':
                    api_response = requests.post(api_endpoint, json=arguments)
                elif need_api_key == 'bearer':
                    headers = {'Authorization': f'Bearer {tool_api_key}'}
                    api_response = requests.post(api_endpoint, json=arguments, headers=headers)
                elif need_api_key == 'header':
                    headers = {'authorization': f'{tool_api_key}'}
                    api_response = requests.post(api_endpoint, json=arguments, headers=headers)
                else:
                    print("Method not supported")
                    return 400
        
        else:
            print("Method not supported")
            return 400
        
        
        api_response.raise_for_status()
        result = api_response.json()
        print("API Response:")
        print(json.dumps(result, indent=2))

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the API request: {e}")
        result = None


        return 400



    # Send the result to the LLM
    if result:
        messages.append({
            "role": "function",
            "name": tool_call.function.name,
            "content": json.dumps(result)
        })
    else:
        messages.append({
            "role": "function",
            "name": tool_call.function.name,
            "content": "Sorry, I couldn't retrieve the information you requested."
        })

    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=messages
    )

    print("Assistant's response:")
    print(response.choices[0].message.content)

    return 200
 

if __name__ == "__main__":
    import os

    import dotenv
    dotenv.load_dotenv()

    useTool('WEATHER_', 'What is the weather in Tokyo?', os.getenv('OPENAI_API_KEY'), '3dc841841c252a856ab099783939b5a6')

    print()

    useTool('IMAGE_TO_TEXT_', 'What is in this image .\searchers\dontBeDommb.jpg', os.getenv('OPENAI_API_KEY'), tool_api_key='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', file_path='searchers\dontBeDommb.jpg')

    print()

    text = """
    Welcome to our top 10 restaurants guide!

    1. The Golden Spoon
    A fine dining experience with a fusion of international cuisines.

    2. Mama Mia's Trattoria
    Authentic Italian dishes in a cozy, family-friendly atmosphere.

    3. Sushi Paradise
    Fresh, innovative sushi rolls and traditional Japanese delicacies.

    4. The Smoky Grill
    Premium steaks and barbecue with a rustic ambiance.

    5. Green Leaf Vegan Cafe
    Creative plant-based dishes that satisfy even non-vegans.

    6. Spice Route
    A journey through Indian flavors with both classic and modern twists.

    7. Le Petit Bistro
    Charming French cuisine in an intimate setting.

    8. Taco Fiesta
    Vibrant Mexican street food with a gourmet touch.

    9. The Seafood Shack
    Fresh catches of the day prepared in various mouthwatering styles.

    10. Sweet Tooth Bakery & Cafe
    Delightful pastries, cakes, and light meals for any time of day.


    """

    useTool('UNSTRUCTURE_TO_STRUCTURE_', f'Take names of the Restaurants in the following text: {text}', os.getenv('OPENAI_API_KEY'))