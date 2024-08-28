import weaviate

from langchain_community.retrievers import (
    WeaviateHybridSearchRetriever,
)
from langchain_core.documents import Document

import cohere
import os 
import dotenv

from fastapi import APIRouter
import random

router = APIRouter()


dotenv.load_dotenv()

URL = os.getenv('WEAVIATE_URL')
APIKEY = os.getenv('WEAVIATE_API')
OPENAI_API_KEY = os.getenv('OPENAI_API')

cohere_api_key = os.getenv('COHERE_API')

client = weaviate.Client(
    url=URL,
    auth_client_secret=weaviate.AuthApiKey(api_key=APIKEY),
    additional_headers={
        "X-Openai-Api-Key": OPENAI_API_KEY,
    },
)


retriever = WeaviateHybridSearchRetriever(
    client=client,
    index_name="WHYTHEFUCKINEEDOCHANGEYOUEVERYTIME",
    text_key="text",
    attributes=[],
    create_schema_if_missing=True,
)

def helper(retriever=retriever, cohere_api_key=cohere_api_key, query:str='pdf'):

    result = retriever.invoke(query)



    titles = [o.page_content for o in result]


    co = cohere.Client(api_key=cohere_api_key)

    results = co.rerank(model="rerank-english-v3.0", query=query, documents=titles, top_n=3, return_documents=True)
    res = []
    for i in results.results:
        res.append(i.document.text)

    return res

@router.get("/", tags=["search"])
async def search():
    return {"message": helper()}

@router.post("/", tags=["search"])
async def search(query:str):
    return {"message": helper(query=query)}