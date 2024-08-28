from typing import Dict
from firecrawl import FirecrawlApp

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

def crawl_url(url:str) -> Dict:
    '''
    Crawl URL
    Crawl single url
    '''

