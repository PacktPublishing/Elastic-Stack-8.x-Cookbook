# Dev tools snippet for Chapter 9 Search application

## BM25 search
### Search template with lexical search
```
PUT _application/search_application/movie_vector_search_application
{
  "indices": ["movies-dense-vector"],
  "template": {
    "script": {
      "lang": "mustache",
      "source": """
        {
          "query": {
            "bool": {
              "must": [
              {{#query}}
              {
                "multi_match" : {
                  "query":    "{{query}}",
                  "fields": [ "title^4", "plot", "cast", "director"]
                }
              }
              {{/query}}
            ],
            "filter": {{#toJson}}_es_filters{{/toJson}}
            }
          },
          "aggs": {
            "genre_facet": {
              "terms": {
                "field": "genre",
                "size": "{{agg_size}}"
              }
            },
            "director_facet": {
              "terms": {
                "field": "director.keyword",
                "size": "{{agg_size}}"
              }
            }
          },
          "from": {{from}},
          "size": {{size}},
          "sort": {{#toJson}}_es_sort_fields{{/toJson}}
        }
      """,
      "params": {
        "query": "",
        "_es_sort_fields": {},
        "_es_filters": {},
        "_es_aggs": {},
        "agg_size": 5,
        "from": 0,
        "size": 12
      }
    }
  }
}
```

## Dense vector search
### dense vector query
```
POST movies-dense-vector/_search
{
  "knn": {
    "field": "plot_vector",
    "k": 5,
    "num_candidates": 50,
    "query_vector_builder": {
      "text_embedding": {
        "model_id": ".multilingual-e5-small_linux-x86_64",
        "model_text": "romantic moment"
      }
    }
  },
  "fields": [ "title", "plot" ]
}
```

### Search template with dense vector search
```
PUT _application/search_application/movie_vector_search_application
{
  "indices": [
    "movies-dense-vector"
  ],
  "template": {
    "script": {
      "lang": "mustache",
      "source": """
      {
          "knn": {
            "field": "{{knn_field}}",
            "k": "{{k}}",
            "num_candidates": {{num_candidates}},
            "filter": {{#toJson}}_es_filters{{/toJson}},
            "query_vector_builder": {
              "text_embedding": {
                "model_id": ".multilingual-e5-small_linux-x86_64",
                "model_text": "{{query}}"
              }
            }
          },
          "fields": {{#toJson}}fields{{/toJson}},
          "aggs": {
            "genre_facet": {
              "terms": {
                "field": "genre",
                "size": "{{agg_size}}"
              }
            },
            "director_facet": {
              "terms": {
                "field": "director.keyword",
                "size": "{{agg_size}}"
              }
            }
          },
          "from": {{from}},
          "size": {{size}}
      }
      """,
      "params": {
        "knn_field": "plot_vector",
        "query": "",
        "k": 20,
        "num_candidates": 100,
        "_es_filters": [],
        "fields": ["title", "plot"],
        "agg_size": 5,
        "from": 0,
        "size":9
      }
    }
  }
}
```

## Sparse vector search

### Semantic search by using the text_expansion query
```
POST movies-sparse-vector/_search
{
   "query":{
      "text_expansion":{
         "plot_sparse_vector":{
            "model_id":".elser_model_2",
            "model_text":" romantic moment"
         }
      }
   }
}
```

### Using ELSER in search application template
```
PUT _application/search_application/movie_vector_search_application
{
  "indices": [
    "movies-sparse-vector"
  ],
  "template": {
    "script": {
      "lang": "mustache",
      "source": """
      {
          "query":{
                "text_expansion":{
                   "plot_sparse_vector":{
                      "model_id":"{{elser_model_id}}",
                      "model_text": "{{query}}"
                   }
                }
             },
          "fields": {{#toJson}}fields{{/toJson}},
          "aggs": {
            "genre_facet": {
              "terms": {
                "field": "genre",
                "size": "{{agg_size}}"
              }
            },
            "director_facet": {
              "terms": {
                "field": "director.keyword",
                "size": "{{agg_size}}"
              }
            }
          },
          "from": {{from}},
          "size": {{size}}
      }
      """,
      "params": {
        "elser_model_id": ".elser_model_2_linux-x86_64",
        "query": "",
        "_es_filters": [],
        "fields": ["title", "plot"],
        "agg_size": 5,
        "from": 0,
        "size": 12
      }
    }
  }
}
```

## Hybrid search
### BM25 search relevance score test
```
POST movies-dense-vector/_search
{
  "query": {
    "multi_match" : {
    "fields": [ "title^4", "plot", "cast", "director"],
    "query":    "love story and a jewel onboard a ship while travelling across Atlantic"
    }
  },
  "fields": [ "title" ],
  "_source": false
}
```
### Vector search relevance score test
```
# Vector search relevance score test
POST movies-dense-vector/_search
{
  "knn": {
    "field": "plot_vector",
    "k": 12,
    "num_candidates": 200,
    "query_vector_builder": {
      "text_embedding": {
        "model_id": ".multilingual-e5-small_linux-x86_64",
        "model_text": "love story and a jewel onboard a ship while travelling across Atlantic"
      }
    }
  },
  "fields": [ "title", "plot" ],
  "_source": false
}
```

### Hybrid search using dense vector and bm25 search with boost
```
PUT _application/search_application/movie_vector_search_application
{
  "indices": [
    "movies-dense-vector"
  ],
  "template": {
    "script": {
      "lang": "mustache",
      "source": """
      {
          "query": {
            "multi_match" : {
              "query":    "{{query}}",
              "boost": "{{boost_bm25}}",
              "fields": [ "title^4", "plot", "cast", "director" ]
            }
          },
          "knn": {
            "field": "{{knn_field}}",
            "k": "{{k}}",
            "num_candidates": {{num_candidates}},
            "filter": {{#toJson}}_es_filters{{/toJson}},
            "query_vector_builder": {
              "text_embedding": {
                "model_id": ".multilingual-e5-small_linux-x86_64",
                "model_text": "{{query}}"
              }
            },
            "boost": "{{boost_knn}}"
          },
          "fields": {{#toJson}}fields{{/toJson}},
          "aggs": {
            "genre_facet": {
              "terms": {
                "field": "genre",
                "size": "{{agg_size}}"
              }
            },
            "director_facet": {
              "terms": {
                "field": "director.keyword",
                "size": "{{agg_size}}"
              }
            }
          },
          "from": {{from}},
          "size": {{size}}
      }
      """,
      "params": {
        "knn_field": "plot_vector",
        "query": "",
        "k": 20,
        "boost_bm25":1,
        "boost_knn": 50,
        "_es_filters": [],
        "num_candidates": 200,
        "fields": ["title", "plot"],
        "agg_size": 10,
        "from": 0,
        "size":20
      }
    }
  }
}
```

### Hybrid search using dense vector and bm25 search with rrf
```
PUT _application/search_application/movie_vector_search_application
{
  "indices": [
    "movies-dense-vector"
  ],
  "template": {
    "script": {
      "lang": "mustache",
      "source": """
      {
          "query": {
            "multi_match" : {
              "query":    "{{query}}",
              "fields": [ "title^4", "plot", "cast", "director" ]
            }
          },
          "knn": {
            "field": "{{knn_field}}",
            "k": "{{k}}",
            "num_candidates": {{num_candidates}},
            "filter": {{#toJson}}_es_filters{{/toJson}},
            "query_vector_builder": {
              "text_embedding": {
                "model_id": ".multilingual-e5-small_linux-x86_64",
                "model_text": "{{query}}"
              }
            }
          },
          "rank": {
            "rrf": {
              "window_size": {{rrf.window_size}},
              "rank_constant": {{rrf.rank_constant}}
            }
          },
          "fields": {{#toJson}}fields{{/toJson}},
          "aggs": {
            "genre_facet": {
              "terms": {
                "field": "genre",
                "size": "{{agg_size}}"
              }
            },
            "director_facet": {
              "terms": {
                "field": "director.keyword",
                "size": "{{agg_size}}"
              }
            }
          },
          "from": {{from}},
          "size": {{size}}
      }
      """,
      "params": {
        "knn_field": "plot_vector",
        "query": "",
        "k": 12,
        "_es_filters": [],
        "num_candidates": 200,
        "fields": ["title", "plot"],
        "agg_size": 10,
        "size": 24,
        "from": 0,
        "rrf": {
          "window_size": 50,
          "rank_constant": 20
        }
      }
    }
  }
}
```

### Hybrid search using elser and bm25 search with rrf
```
PUT _application/search_application/movie_vector_search_application
{
  "indices": [
    "movies-sparse-vector"
    ],
    "template": {
      "script": {
        "lang": "mustache",
        "source": """
        {
          "sub_searches": [
            {{#text_fields}}
            {
              "query": {
                "match": {
                  "{{.}}": {
                    "query": "{{query}}"
                  }
                }
              }
            },
            {{/text_fields}}
            {{#elser_fields}}
            {
              "query": {
                "text_expansion": {
                  "{{.}}": {
                    "model_text": "{{query}}",
                    "model_id":"{{elser_model_id}}"
                  }
                }
              }
            },
            {{/elser_fields}}
            ],
            "rank": {
              "rrf": {
                "window_size": {{rrf.window_size}},
                "rank_constant": {{rrf.rank_constant}}
              }
            },
            "fields": {{#toJson}}fields{{/toJson}},
            "aggs": {
              "genre_facet": {
                "terms": {
                  "field": "genre",
                  "size": "{{agg_size}}"
                }
              },
              "director_facet": {
                "terms": {
                  "field": "director",
                  "size": "{{agg_size}}"
                }
              }
            },
            "from": {{from}},
            "size": {{size}}
        }
        """,
        "params": {
          "elser_fields": ["title_sparse_vector", "plot_sparse_vector"],
          "text_fields": ["title"],
          "elser_model_id": ".elser_model_2_linux-x86_64",
          "query": "",
          "_es_filters": [],
          "fields": ["title", "plot"],
          "agg_size": 10,
          "size": 24,
          "from": 0,
          "rrf": {
            "window_size": 50,
            "rank_constant": 20
          }
        }
      }
    }
}
```