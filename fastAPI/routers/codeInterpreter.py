"""
Code interpreter
"""

from openai import OpenAI
from e2b_code_interpreter import CodeInterpreter
import base64
import os
import dotenv
import requests
from urllib.parse import urlparse

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

e2b_code_interpreter = CodeInterpreter(api_key=os.getenv('E2B_API_KEY'))

def is_url(string):
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
      
def upload_file_for_code_interpreter(file_url):
  """
  This function uploads a file to the code interpreter and returns the path.
  """

  if is_url(file_url):
  
      response = requests.get(file_url)
      if response.status_code == 200:

          filename = os.path.basename(urlparse(file_url).path)
          if not filename:
              filename = 'downloaded_file'
          

          with open(filename, 'wb') as f:
              f.write(response.content)
          
          file_url = filename  
      else:
          raise Exception(f"Failed to download file from {file_url}")
  elif not os.path.exists(file_url):
      raise FileNotFoundError(f"File not found: {file_url}")

  # At this point, file_url is a local file path
  with open(file_url, "rb") as f:
      returned_path = e2b_code_interpreter.upload_file(f)
  return returned_path  

def code_interpret(code):
  """
  This function executes the code interpreter and returns the results.
  """

  print("Running code interpreter...")
  exec = e2b_code_interpreter.notebook.exec_cell(
    code,
    on_stderr=lambda stderr: print("[Code Interpreter]", stderr),
    on_stdout=lambda stdout: print("[Code Interpreter]", stdout),
  )

  if exec.error:
    print("[Code Interpreter ERROR]", exec.error)
    return exec.error
  else:
    results = []
    for i, result in enumerate(exec.results):
        if result.png:
            # Decode the base64 encoded PNG data
            png_data = base64.b64decode(result.png)
        
            # Generate a unique filename for the PNG
            filename = f"chart_{i}.png"

            # Save the decoded PNG data to a file
            with open(filename, "wb") as f:
                f.write(png_data)

            print(f"Saved chart to {filename}")
            results.append(filename)
        else:
            results.append(result)
    return results

SYSTEM_PROMPT = """
## your job & context
you are a python data scientist. you are given tasks to complete and you run python code to solve them.
- the python code runs in jupyter notebook.
- every time you call `execute_python` tool, the python code is executed in a separate cell. it's okay to multiple calls to `execute_python`.
- display visualizations using matplotlib or any other visualization library directly in the notebook. don't worry about saving the visualizations to a file.
- you have access to the internet and can make api requests.
- you also have access to the filesystem and can read/write files.
- you can install any pip package (if it exists) if you need to but the usual packages for data analysis are already preinstalled.
- you can run any python code you want, everything is running in a secure sandbox environment.
"""

tools = [
    {
        "type": "function",
        "function": {
        "name": "execute_python",
        "description": "Execute python code in a Jupyter notebook cell and returns any result, stdout, stderr, display_data, and error.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The python code to execute in a single cell."
                }
            },
            "required": ["code"]
        }
        },
    }
]

if __name__ == '__main__':  
  
  user_message = "Plot a normal distribution chart"
  file_url = r'..\tools\Tools - Sheet1.csv'
  
  print(f"\n{'='*50}\nUser Message: {user_message}\n{'='*50}")

  messages = [
      {
          "role": "system",
          "content": SYSTEM_PROMPT,
      },
  ]

  file_url = upload_file_for_code_interpreter(code_interpreter, file_url)
        
  messages.append(
    {
    "role": "user",
    "content": [
        {
        "type": "text",
        "text": user_message,
        },
    ]
    }
  )


  response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto"
  )

  for choice in response.choices:
    if choice.message.tool_calls and len(choice.message.tool_calls) > 0:
      for tool_call in choice.message.tool_calls:
        if tool_call.function.name == "execute_python":
          if "code" in tool_call.function.arguments:
            code = eval(tool_call.function.arguments)["code"]
          else:
            code = tool_call.function.arguments
          print("CODE TO RUN")
          print(code)
          code_interpreter_results = code_interpret(code_interpreter, code)
    else:
      print("Answer:", choice.message.content)
   

    print(code_interpreter_results)