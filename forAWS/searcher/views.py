import weaviate
from weaviate.classes.init import Auth
import weaviate.classes as wvc

import cohere
import os 
import dotenv

from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse

dotenv.load_dotenv()

URL = os.getenv('WEAVIATE_URL')
APIKEY = os.getenv('WEAVIATE_API')
cohere_api_key = os.getenv('COHERE_API')

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=URL,                                  
    auth_credentials=Auth.api_key(APIKEY),   
    headers={"X-Cohere-Api-Key": cohere_api_key,}            
)


co = cohere.Client(api_key=cohere_api_key)

def helper(query:str = 'pdf'):
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=URL,                                  
            auth_credentials=Auth.api_key(APIKEY),   
            headers={"X-Cohere-Api-Key": cohere_api_key,}            
        )
            
        tool = client.collections.get('Tool')
        results = tool.query.hybrid(
            query = query,
            limit=25
        )

        client.close()

        titles = [o.properties['name'] for o in results.objects]
       
        results = co.rerank(model="rerank-english-v3.0", query=query, documents=titles, top_n=3, return_documents=True)

        dic = {}
        for i, result in enumerate(results.results):
            dic[i] = result.document.text

        return dic

class SearcherView(APIView):
    '''
    Search for tool in database
    '''

    def get(self, request):

        results = helper()

        return JsonResponse(results)
    
    def post(self, request):
        '''
        Takes query and returns top 3 tools
        '''
        query = request.data['query']

        return JsonResponse(helper(query))
