from langchain.vectorstores.elasticsearch import ElasticsearchStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import NLTKTextSplitter
from langchain_community.document_loaders.csv_loader import CSVLoader
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

load_dotenv()

ES_CID = os.getenv('ES_CID')
ES_USER = os.getenv('ES_USER')
ES_PWD = os.getenv('ES_PWD')
MOVIE_DATASET = os.getenv('DATASET')
INDEX_NAME = "movies-langchain-generated"
query_model_id = ".multilingual-e5-small_linux-x86_64"
INGEST_PIPELINE_ID = "movies-rag-langchain-pipeline"

# ingest pipeline processors
ingest_pipeline_processors = {
    "processors": [
        {
            "inference": {
                "model_id": query_model_id,
                "field_map": {
                    "query_field": "text_field"
                },
                "target_field": "vector_query_field",
                "on_failure": [
                    {
                        "append": {
                            "field": "_source._ingest.inference_errors",
                            "value": [
                                {
                                    "message": "Processor 'inference' in pipeline 'movies-rag-langchain-pipeline' failed with message '{{ "
                                               "_ingest.on_failure_message }}'",
                                    "pipeline": INGEST_PIPELINE_ID,
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


def create_index(client, index_name):
    """Creates an index in Elasticsearch if one isn't already there."""
    if not client.indices.exists(index=INDEX_NAME):
        pass
    else:
        print("Deleting existing movies index...")
        client.options(ignore_status=[404, 400]).indices.delete(index=INDEX_NAME)
    # index mapping
    mappings = {
        "properties": {
            "director": {
                "type": "keyword"
            },
            "genre": {
                "type": "keyword"
            },
            "metadata": {
                "properties": {
                    "cast": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
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
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "origin": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "release_year": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "row": {
                        "type": "long"
                    },
                    "source": {
                        "type": "text",
                        "analyzer": "my_english_analyzer",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "title": {
                        "type": "text",
                        "analyzer": "my_english_analyzer",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "wiki": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    }
                }
            },
            "text_field": {
                "type": "text",
                "analyzer": "my_english_analyzer",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "vector_query_field": {
                "properties": {
                    "is_truncated": {
                        "type": "boolean"
                    },
                    "predicted_value": {
                        "type": "dense_vector",
                        "dims": 384,
                        "index": True,
                        "similarity": "dot_product"
                    }
                }
            }
        }
    }
    # index setting
    settings = {
        "analysis": {
            "analyzer": {
                "my_english_analyzer": {
                    "type": "english",
                    "stopwords": ["_english_", "where", "which", "how", "when", "wherever"]
                }
            }
        }, "default_pipeline": INGEST_PIPELINE_ID
    }
    client.options(ignore_status=[400, 404]).indices.create(
        index=index_name,
        settings=settings,
        mappings=mappings
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


def create_vector_db(dataset, index_name):
    loader = CSVLoader(
        file_path=dataset,
        metadata_columns=["release_year", "title", "origin", "director", "cast", "genre", "wiki"],
        csv_args={
            "fieldnames": ["release_year", "title", "origin", "director", "cast", "genre", "wiki", "plot"]
        }
    )
    documents = loader.load()

    text_splitter = NLTKTextSplitter(chunk_size=1000, chunk_overlap=200)

    docs = text_splitter.split_documents(documents)

    print("Creating documents...")
    docs = ElasticsearchStore.from_documents(
        docs,
        es_cloud_id=ES_CID,
        index_name=index_name,
        es_user=ES_USER,
        es_password=ES_PWD,
        query_field="text_field",
        vector_query_field="vector_query_field.predicted_value",
        strategy=ElasticsearchStore.ApproxRetrievalStrategy(query_model_id=query_model_id),
        bulk_kwargs={"request_timeout": 300, "chunk_size": 500}
    )


if __name__ == "__main__":
    es = Elasticsearch(
        cloud_id=ES_CID,
        basic_auth=(ES_USER, ES_PWD)
    )
    es.info()
    print("Creating index...")
    create_index(es, INDEX_NAME)
    print("Creating ingest pipeline...")
    create_ingest_pipeline(es, INGEST_PIPELINE_ID)
    print("Creating documents...")
    create_vector_db(MOVIE_DATASET, INDEX_NAME)
    print("Done.")
