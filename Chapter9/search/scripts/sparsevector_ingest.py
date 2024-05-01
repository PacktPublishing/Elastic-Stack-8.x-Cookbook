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
INDEX_NAME = "movies-sparse-vector"
INGEST_PIPELINE_ID = "ml-inference-plot-vector-sparse"

# Elser model ID; This one depends on the model you have deployed
# We are using the recommended model optimized for linux-x86_64 architecture
ELSER_MODEL_ID = ".elser_model_2_linux-x86_64"

# Define ingest pipeline
elser_ingest_pipeline_processors = {
    "processors": [
        {
            "inference": {
                "model_id": ELSER_MODEL_ID,
                "input_output": [
                    {
                        "input_field": "plot",
                        "output_field": "plot_sparse_vector"
                    }
                ],
                "on_failure": [
                    {
                        "append": {
                            "field": "_source._ingest.inference_errors",
                            "value": [
                                {
                                    "message": "Processor 'inference' in pipeline 'ml-inference-plot-vector-sparse' "
                                               "failed with message '{{ _ingest.on_failure_message }}'",
                                    "pipeline": ELSER_MODEL_ID,
                                    "timestamp": "{{{ _ingest.timestamp }}}"
                                }
                            ]
                        }
                    }
                ]
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
            # Add the plot_sparse_vector field
            "plot_sparse_vector": {
                "type": "sparse_vector"
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
    client.options(ignore_status=[400]).ingest.put_pipeline(
        id=pipeline_id,
        description="Ingest pipeline to generate plot_vector",
        processors=elser_ingest_pipeline_processors['processors'])
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
        request_timeout=300
    )

    print("Creating ingest pipeline...")
    create_ingest_pipeline(es, INGEST_PIPELINE_ID)

    print("Creating index...")
    create_index(es, index_name=INDEX_NAME)

    print("Indexing documents...")
    progress = tqdm.tqdm(unit="docs", total=number_of_docs)
    successes = 0
    for ok, action in streaming_bulk(
            client=es, chunk_size=100, index=INDEX_NAME, actions=generate_actions(),
    ):
        progress.update(1)
        successes += ok
    print("Indexed %d/%d documents" % (successes, number_of_docs))


if __name__ == "__main__":
    main()
