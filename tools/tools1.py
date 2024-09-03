from typing import Dict
from firecrawl import FirecrawlApp
from langchain.agents import tool
from langchain_community.tools.riza.command import ExecPython

import dotenv
import os

'''
OK. Format of output data:
{
    'result': data
}
    ^^^       ^^^
    str       array

Specifications could be seen inside of function.
Function specification:
    Name
    Description
    Output format
''' 

dotenv.load_dotenv()

@tool
def crawl_url(url:str):
    """
    Crawl url
    """
    FIRECRAWL_API = os.getenv('FIRECRAWL')

    app = FirecrawlApp(api_key=FIRECRAWL_API)

    return app.scrape_url(url)

@tool
def code_interpreter(code:str):
    '''
    Run python code you provide
    '''

    return ExecPython().invoke(code)

