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
document = {
    'director': 'Clint Eastwood2'
}

# Update the document in Elasticsearch
response = es.update(index=index_name, id=document_id, doc=document)
print(f"Update status: {response['result']}")

# Verify the update in Elasticsearch
updated_document = es.get(index=index_name, id=document_id)
print("Updated document:")
print(updated_document['_source'])