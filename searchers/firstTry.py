import weaviate
from weaviate.classes.init import Auth
import weaviate.classes as wvc

import cohere
import os 
import dotenv

dotenv.load_dotenv()

URL = os.getenv('WEAVIATE_URL')
APIKEY = os.getenv('WEAVIATE_API')
cohere_api_key = os.getenv('COHERE_API')

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=URL,                                  
    auth_credentials=Auth.api_key(APIKEY),   
    headers={"X-Cohere-Api-Key": cohere_api_key,}            
)

tool = client.collections.get('Tool')

results = tool.query.hybrid(
    query = 'pdf',
    limit=25
)
client.close()

titles = [o.properties['name'] for o in results.objects]

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