import requests
import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

ES_CID = os.getenv('ES_CID')
ES_USER = os.getenv('ES_USER')
ES_PWD = os.getenv('ES_PWD')

es = Elasticsearch(
    cloud_id=ES_CID,
    basic_auth=(ES_USER, ES_PWD)
)

es.info()

index_name = 'movies'
document_id = ''

# replace the document_id by the id of the ingested document of the previous recipe
with open('tmp.txt', 'r') as file:
    document_id = file.read()

if document_id != '':
    if es.exists(index=index_name, id=document_id):
        # delete the document in Elasticsearch
        response = es.delete(index=index_name, id=document_id)
        print(f"delete status: {response['result']}")
    else:
        print(f"No delete performed: {document_id} does not exist in the index.")
else:
    print("No delet performed, document_id is invalid.")
