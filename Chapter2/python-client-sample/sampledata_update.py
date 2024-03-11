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
# replace the document_id by the id of the ingested document of the previous recipe

document_id = '<ID_OF_THE_INGESTED_DOCUMENT>'
document = {
    'director': 'Clint Eastwood'
}

# Update the document in Elasticsearch
response = es.update(index=index_name, id=document_id, doc=document)
print(f"Update status: {response['result']}")

# Verify the update in Elasticsearch
updated_document = es.get(index=index_name, id=document_id)
print("Updated document:")
print(updated_document['_source'])