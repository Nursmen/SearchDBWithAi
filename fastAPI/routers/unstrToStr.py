import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

import dotenv

dotenv.load_dotenv()

llm = ChatOpenAI(model_name="gpt-3.5-turbo")

prompt_template = """
You are a data transformation expert. Given the following schema and unstructured data, convert the data into the structured format as described. If you cannot return valid output, return nothing.

Schema:
{schema}

Data:
{data}

Output:
{{
    "data": [
        {{
            "...": {{
                "...": [...],
                "...": [...],
                "...": [...],
            }}
        }},
        {{
            "...": {{
                "...": [...],
                "...": [...],
                "...": [...],
            }}
        }},
    ]
}}
"""

prompt = PromptTemplate(template=prompt_template, input_variables=["schema", "data"])

chain = prompt | llm

def unstructerToStr(schema, data):
    """
    Converts unstructured data to a structured format based on the given schema.
    
    Parameters:
    schema (str): The schema description.
    data (str): The unstructured data.
    
    Returns:
    dict: The structured data.
    """
    inputs = {
        "schema": schema,
        "data": data
    }
    
    result = chain.invoke(inputs)
    try:
        structured_data = json.loads(result.content)
    except:
        print(result.content)
        structured_data = json.loads('{"data":[]}')
    return structured_data

if __name__ == "__main__":
    schema = "Name: John Doe\nAge: 30\nCity: New York"
    data = "Name: John Doe\nAge: 30\nCity: New York"
    structured_data = unstructerToStr(schema, data) 
    print(structured_data)