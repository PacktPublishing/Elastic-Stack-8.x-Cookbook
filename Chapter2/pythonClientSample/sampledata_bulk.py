import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import tqdm
from elasticsearch.helpers import streaming_bulk
import csv

load_dotenv()

ES_CID = os.getenv('ES_CID')
ES_USER = os.getenv('ES_USER')
ES_PWD = os.getenv('ES_PWD')
MOVIE_DATASET = os.getenv('MOVIE_DATASET')


def download_dataset():
    with open(MOVIE_DATASET) as f:
        reader = csv.DictReader(f)
        return sum([1 for row in reader])


def create_index(client):
    """Creates an index in Elasticsearch if one isn't already there."""
    mappings = {
        "properties": {
            "cast": {
                "type": "text"
            },
            "director": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "genre": {
                "type": "keyword"
            },
            "origin": {
                "type": "keyword"
            },
            "plot": {
                "type": "text"
            },
            "release_year": {
                "type": "long",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "title": {
                "type": "text",
            },
            "wiki_page": {
                "type": "keyword"
            }
        }
    }
    settings = {"number_of_shards": 1}
    client.options(ignore_status=[400]).indices.create(
        index="movies",
        settings=settings,
        mappings=mappings
    )


def generate_actions():
    """Reads the file through csv.DictReader() and for each row
    yields a single document. This function is passed into the bulk()
    helper to create many documents in sequence.
    """
    with open(MOVIE_DATASET, encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            doc = {
                "release_year": row["Release Year"],
                "title": (row["Title"]),
                "origin": row["Origin/Ethnicity"],
                "director": row["Director"],
                "cast": row["Cast"],
                "genre": row["Genre"],
                "wiki_page": row["Wiki Page"],
                "plot": row["Plot"]
            }
            yield doc


def main():
    print("Loading dataset...")
    number_of_docs = download_dataset()
    print("number of docs: ", number_of_docs)

    client = Elasticsearch(
        cloud_id=ES_CID,
        basic_auth=(ES_USER, ES_PWD)
    )

    if client.indices.exists(index="movies"):
        print("Deleting existing movies index...")
        client.options(ignore_status=[404, 400]).indices.delete(index="movies")

    print("Creating index...")
    create_index(client)

    print("Indexing documents...")
    progress = tqdm.tqdm(unit="docs", total=number_of_docs)
    successes = 0
    for ok, action in streaming_bulk(
            client=client, index="movies", actions=generate_actions(),
    ):
        progress.update(1)
        successes += ok
    print("Indexed %d/%d documents" % (successes, number_of_docs))


if __name__ == "__main__":
    main()
