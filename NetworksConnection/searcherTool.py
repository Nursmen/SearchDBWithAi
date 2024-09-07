from langchain.agents import tool

import weaviate
from langchain_community.retrievers import (
    WeaviateHybridSearchRetriever,
)

import cohere

import os
import dotenv

dotenv.load_dotenv()

URL = os.getenv('WEAVIATE_URL')
APIKEY = os.getenv('WEAVIATE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
COHERE_API_KEY = os.getenv('COHERE_API_KEY')

client = weaviate.Client(
    url=URL,
    auth_client_secret=weaviate.AuthApiKey(api_key=APIKEY),
    additional_headers={
        "X-Openai-Api-Key": OPENAI_API_KEY,
    },
)

retriever = WeaviateHybridSearchRetriever(
    client=client,
    index_name="TOOLSET_TEST",
    text_key="text",
    attributes=[],
    create_schema_if_missing=True,
    k=25,
)

co = cohere.Client(api_key=COHERE_API_KEY)

@tool
def tool_searcher(query: str):
    """
    Scan a predefined tools database and retrieve the most appropriate tool required for a given task. When a command is provided, the searcher automatically looks up the tools available in the connected apps to ensure the necessary tool exists.
    """
    firstFilter = [ff.page_content for ff in retriever.invoke(query)]

    results = co.rerank(model="rerank-english-v3.0", query=query, documents=firstFilter, top_n=1, return_documents=True)

    return results.results[0].document.text

if __name__ == "__main__":
    print(tool_searcher("calendar"))
    