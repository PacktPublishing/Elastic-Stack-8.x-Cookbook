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
index_settings = {
    "settings": {
        "analysis": {
            "analyzer": {
                "standard_with_stopwords": {
                    "type": "standard",
                    "stopwords": "_english_"
                }
            }
        }
    }
}
es.indices.create(index='movies-python', body=index_settings)
#es.indices.put_settings(index='movies-python', settings=index_settings)

response = es.index(
    index='movies-python',
    document={
        'release_year': '1908',
        'title': 'It is not this day.',
        'origin': 'American',
        'director': 'D.W. Griffith',
        'cast': 'Harry Solter, Linda Arvidson',
        'genre': 'comedy',
        'wiki_page': 'https://en.wikipedia.org/wiki/A_Calamitous_Elopement',
        'plot': 'A young couple decides to elope after being caught in the midst of a romantic moment by the woman .'
    })

print(response)

settings = es.indices.get_settings(index='movies-python')
analyzer_settings = settings['movies-python']['settings']['index']['analysis']
print(f"Analyzer used for the index: {analyzer_settings}")

# response = es.search(index='movies', query={"match_all": {}})
# print("Sample movie data in Elasticsearch:")
# for hit in response['hits']['hits']:
#     print(hit['_source'])
