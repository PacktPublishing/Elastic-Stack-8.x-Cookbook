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
INDEX_NAME = "movies-dense-vector"
INGEST_PIPELINE_ID = "ml-inference-plot-vector"
SENTENCE_TRANSFORMERS_MODEL_ID = ".multilingual-e5-small_linux-x86_64"

# Define ingest pipeline
ingest_pipeline_processors = {
    "processors": [
        {
            "inference": {
                "field_map": {
                    "plot": "text_field"
                },
                "model_id": SENTENCE_TRANSFORMERS_MODEL_ID,
                "target_field": "ml.inference.plot_vector",
                "on_failure": [
                    {
                        "append": {
                            "field": "_source._ingest.inference_errors",
                            "value": [
                                {
                                    "message": "Processor 'inference' in pipeline 'ml-inference-plot-vector' failed "
                                               "with message '{{ _ingest.on_failure_message }}'",
                                    "pipeline": INGEST_PIPELINE_ID,
                                    "timestamp": "{{{ _ingest.timestamp }}}"
                                }
                            ]
                        }
                    }
                ]
            }
        },
        {
            "set": {
                "field": "plot_vector",
                "if": "ctx?.ml?.inference != null && ctx.ml.inference['plot_vector'] != null",
                "copy_from": "ml.inference.plot_vector.predicted_value",
                "description": "Copy the predicted_value to 'plot_vector'"
            }
        },
        {
            "remove": {
                "field": "ml.inference.plot_vector",
                "ignore_missing": True
            }
        }
    ]
}


def download_dataset():
    with open(MOVIE_DATASET) as f:
        reader = csv.DictReader(f)
        return sum([1 for row in reader])


def create_index(client, index_name):
    """Creates an index in Elasticsearch if one isn't already there."""
    if client.indices.exists(index=index_name):
        print("Deleting existing movies index...")
        client.options(ignore_status=[404, 400]).indices.delete(index=index_name)
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
                "type": "short",
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
            },
            "plot_vector": {
                "type": "dense_vector",
                "dims": 384,
                "index": "true",
                "similarity": "dot_product"
            }
        }
    }
    settings = {"number_of_shards": 1, "default_pipeline": INGEST_PIPELINE_ID}
    client.options(ignore_status=[400]).indices.create(
        index=index_name,
        settings=settings,
        mappings=mappings,
    )


def create_ingest_pipeline(client, pipeline_id):
    # Check if the pipeline exists
    if client.options(ignore_status=[404, 400]).ingest.get_pipeline(id=pipeline_id):
        client.options(ignore_status=[404, 400]).ingest.delete_pipeline(id=pipeline_id)
    # Create the pipeline
    print("Creating ingest pipeline...")
    client.options(ignore_status=[400]).ingest.put_pipeline(
        id=pipeline_id,
        description="Ingest pipeline to generate plot_vector",
        processors=ingest_pipeline_processors['processors'])
    print(f"Pipeline {pipeline_id} created.")


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

    # Connect to the Elasticsearch cluster
    es = Elasticsearch(
        cloud_id=ES_CID,
        basic_auth=(ES_USER, ES_PWD),
        request_timeout=30
    )

    print("Creating ingest pipeline...")
    create_ingest_pipeline(es, INGEST_PIPELINE_ID)

    print("Creating index...")
    create_index(es, index_name=INDEX_NAME)

    print("Indexing documents...")
    progress = tqdm.tqdm(unit="docs", total=number_of_docs)
    successes = 0
    for ok, action in streaming_bulk(
            client=es, index=INDEX_NAME, actions=generate_actions(),
    ):
        progress.update(1)
        successes += ok
    print("Indexed %d/%d documents" % (successes, number_of_docs))


if __name__ == "__main__":
    main()
