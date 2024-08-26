import weaviate
from weaviate.classes.init import Auth
import weaviate.classes as wvc

from langchain_community.retrievers import (
    WeaviateHybridSearchRetriever,
)
from langchain_core.documents import Document

import cohere
import os 
import dotenv

dotenv.load_dotenv()

URL = os.getenv('WEAVIATE_URL')
APIKEY = os.getenv('WEAVIATE_API')
OPENAI_API_KEY = os.getenv('OPENAI_API')


client = weaviate.Client(
    url=URL,
    auth_client_secret=weaviate.AuthApiKey(api_key=APIKEY),
    additional_headers={
        "X-Openai-Api-Key": OPENAI_API_KEY,
    },
)


retriever = WeaviateHybridSearchRetriever(
    client=client,
    index_name="WHYTHEFUCKINEEDTOCHANGEYOUEVERYTIME",
    text_key="text",
    attributes=[],
    create_schema_if_missing=True,
)


docs = [Document(
    metadata={'usage': 'read pdf files'},
    page_content='pdf_reader'
    ),

    Document(
    metadata={'usage': 'read csv files'},
    page_content='csv_reader'
    ),

    Document(
    metadata={'usage': 'read excel files'},
    page_content='excel_reader'
    ),

    Document(
    metadata={'usage': 'search web pages'},
    page_content='web_search'
    ),

    Document(
    metadata={'usage': 'get info from html of page'},
    page_content='crawler'
    ),
]

retriever.add_documents(docs)

result = retriever.invoke('pdf')



titles = [o.page_content for o in result]

print()
print()
print()
print()

for i in titles:
    print(i)

co = cohere.Client(api_key=cohere_api_key)

results = co.rerank(model="rerank-english-v3.0", query='pdf', documents=titles, top_n=3, return_documents=True)
print('------------')
for i in results.results:
    print(i.document.text)


print()
print()
print()
print()
print()