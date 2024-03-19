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
q = {
    "script": {
       "source": "ctx._source.genre = 'comedies'",
       "lang": "painless"
    },
    "query": {
        "bool": {
          "must": [
            {
              "term": {
                "genre": "comedy"
              }
            }
          ]
        }
    }
}

# Update the document in Elasticsearch
response = es.update_by_query(body=q, index=index_name)
print(f"Update status: {response}")

