"""
We take a query and generate a Pydantic model for the response.
"""

from pydantic import BaseModel, create_model, Field
from typing import List, Dict, Any
import openai
import os
import dotenv
import json

dotenv.load_dotenv()

def extract_fields_from_query(query: str) -> Dict[str, Any]:
    """
    Use ChatGPT to extract fields from the query.
    This function leverages OpenAI's API to analyze the query and identify relevant fields.
    """
    prompt = f"""
    Analyze the following query and extract the fields and their corresponding data types to json:
    
    Query: '{query}'
    
    Instructions:
    1. Identify all explicit and implicit fields mentioned in the query.
    2. Determine the most appropriate data type for each field.
    3. For fields that could be multiple types, choose the most likely or flexible option.
    4. If a field is clearly a list or array, specify it as List[appropriate_type].
    5. For complex nested structures, use Dict[str, Any] as a placeholder.
    
    Return the results as a Python dictionary where:
    - Keys are the extracted field names (in snake_case if multi-word).
    - Values are the corresponding Python data types (str, int, float, bool, List[str], etc.).
    
    Example:
    {{"user_name": "str", "age": "int", "is_active": "bool", "hobbies": "List[str]"}}
    
    Ensure the output is a valid Python dictionary that can be directly parsed.
    """
    
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        response_format={"type": "json_object"}
    )
    
    fields_response = response.choices[0].message.content
    # The fields should now be extracted as a Python dictionary.
    fields = json.loads(fields_response)  # Be cautious of eval, validate input first.
    return fields, fields_response

def generate_pydantic_model(query: str) -> BaseModel:
    # Step 1: Extract fields from the query using ChatGPT
    fields, fields_response = extract_fields_from_query(query)
    
    # Step 2: Dynamically create a Pydantic model using the fields
    schema = create_model(
        'DynamicSchema',
        **{field_name: (field_type, ...) for field_name, field_type in fields.items()}
    )
    
    return schema, fields_response

def struct(query: str, model: BaseModel):

    client = openai.OpenAI()

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Extract the event information."},
            {"role": "user", "content": query},
        ],
        response_format=model,
    )

    result = completion.choices[0].message.parsed

    return result

if __name__ == "__main__":
    query = "Create a Pydantic model for a user profile with fields: 'name', 'age', 'email', 'is_active', 'address', 'phone_number', and 'orders' which is a list of order IDs."
    model, generated_json = generate_pydantic_model(query)
    print(model)    
    # check the fields of the model
    print(model.model_fields)
    print(generated_json)

    query = "John Doe, 32, john.doe@email.com, active user, 123 Main St, San Francisco, CA 94122, +1 (555) 123-4567, orders: [1001, 1002, 1003]"
    result = struct(query, model)
    print(result)