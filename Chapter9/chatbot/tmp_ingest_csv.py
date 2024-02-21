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
MOVIE_DATASET = os.getenv('MOVIE_DATASET')

CSV_PATH="/Users/huagechen/PycharmProjects/llamatest/llama_company_data/wiki_movie_plots_deduped.csv"
DB_FAISS_PATH = "vectorstores/db_faiss/"

def create_index(client):
    """Creates an index in Elasticsearch if one isn't already there."""
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
              "text": {
                "type": "text",
                "analyzer": "my_english_analyzer",
                "fields": {
                  "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                  }
                }
              },
              "vector": {
                "type": "dense_vector",
                "dims": 384,
                "index": True,
                "similarity": "cosine"
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
        }
    }
    client.options(ignore_status=[400]).indices.create(
        index="movies-langchain-generated",
        settings=settings,
        mappings=mappings
    )


def create_vector_db():
    loader = CSVLoader(
        file_path="/Users/huagechen/PycharmProjects/llamatest/llama_company_data/wiki_movie_plots_deduped.csv",
        metadata_columns=["release_year", "title", "origin", "director", "cast", "genre", "wiki"],
        csv_args={
            "fieldnames": ["release_year", "title","origin","director","cast","genre","wiki","plot"]
        }
    )
    documents = loader.load()

    text_splitter = NLTKTextSplitter(chunk_size=500, chunk_overlap=100)



    docs=text_splitter.split_documents(documents)
    print(docs)
    embeddings=HuggingFaceEmbeddings(model_name='elastic/multilingual-e5-small-optimized')

    client = Elasticsearch(
        cloud_id=ES_CID,
        basic_auth=(ES_USER, ES_PWD)
    )

    if client.indices.exists(index="movies-langchain-generated"):
        print("Deleting existing movies index...")
        client.options(ignore_status=[404, 400]).indices.delete(index="movies-langchain-generated")
    print("Creating index...")

    create_index(client)
    print("Creating documents...")
    db = ElasticsearchStore(
        es_cloud_id=ES_CID,
        index_name="movies-langchain-generated",
        embedding=embeddings,
        es_user=ES_USER,
        es_password=ES_PWD,
    )

    docs = db.from_documents(
        docs,
        embeddings,
        es_cloud_id=ES_CID,
        es_user=ES_USER,
        es_password=ES_PWD,
        index_name="movies-langchain-generated"
    )

if __name__=="__main__":
    create_vector_db()