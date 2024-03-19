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
document_id = 'vlM9C4kBU-BJO8sdwiK7'

# replace the document_id by the id of the ingested document of the previous recipe
with open('tmp.txt', 'r') as file:
    document_id = file.read()

# delete the document in Elasticsearch
response = es.delete(index=index_name, id=document_id)
print(f"delete status: {response['result']}")

