# Snippets for Chapter 2

## <em>Quick links to the recipes</em>
* [Adding data from the Elasticsearch client](#adding-data-from-the-elasticsearch-client)
* [Updating data in Elasticsearch](#updating-data-in-elasticsearch)
* [Deleting data in Elasticsearch](#deleting-data-in-elasticsearch)
* [Configuring Analyzer and tokenizers](#configuring-analyzer-and-tokenizers)
* [Defining index mapping](#defining-index-mapping)
* [Using dynamic templates in document mapping](#using-dynamic-templates-in-document-mapping)
* [Creating an index template](#create-index-template)
* [Indexing multiple documents using bulk](#indexing-multiple-documents-using-bulk)

## Adding data from the Elasticsearch client
Install Python requirements
```console
pip install -r requirements.txt 
```
Python imports
```python
import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
```
Connect to Elasticsearch
```python
load_dotenv()

ES_CID = os.getenv('ES_CID')
ES_USER = os.getenv('ES_USER')
ES_PWD = os.getenv('ES_PWD')

es = Elasticsearch(
    cloud_id=ES_CID,
    basic_auth=(ES_USER, ES_PWD)
)

print(es.info()) 
```
Run the index script
```console
python sampledata_index.py
```
Prepare sample movie
```python
mymovie = {  
  'release_year': '1908',  
  'title': 'It is not this day.',  
  'origin': 'American',  
  'director': 'D.W. Griffith',  
  'cast': 'Harry Solter, Linda Arvidson',  
  'genre': 'comedy',  
  'wiki_page':'https://en.wikipedia.org/wiki/A_Calamitous_Elopement',  
  'plot': 'A young couple decides to elope after being caught in the midst of a romantic moment by the woman .'  
} 
```
Index sample movie
```python
response = es.index(index='movies',document=mymovie) 
print(response) 
```
Check results
```python
response = es.search(index='movies', query={"match_all": {}}) 
print("Sample movie data in Elasticsearch:") 
for hit in response['hits']['hits']: 
 print(hit['_source']) 
```
Run the index script again
```console
python sampledata_index.py
```

## Update data in Elasticsearch
Run the update script 
```console
python sampledata_update.py
```

## Deleting data in Elasticsearch
### Movie search query
```
GET movies/_search
```
### Run the delete script
Run the delete script
```console
python sampledata_delete.py
```

### Delete by query Dev Tools command
```
POST /movies/_delete_by_query 
{ 
  "query": { 
    "match": { 
      "genre": "comedy" 
    } 
  } 
} 
```

## Configuring Analyzer and tokenizers

### Analyzer test
```
POST movies/_analyze
{
  "text": "A young couple decides to elope.",
  "analyzer": "standard_with_stopwords"
}
```
## Defining index mapping
### Inspect movie mapping
```
GET movies/_mapping
```
### Setting movie explicit mapping
```
PUT movies-with-explicit-mapping
{
  "mappings": {
    "properties": {
      "release_year": {
        "type": "short",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          }
        }
      },
      "cast": {
        "type": "text"
      },
      "plot": {
        "type": "text"
      }
    }
  }
}
```
### Reindex to new index explicit mapping
```
POST /_reindex
{
  "source": {
    "index": "movies"
  },
  "dest": {
    "index": "movies-with-explicit-mapping"
  }
}
```

### Check whether the new mapping
```
GET movies-with-explicit-mapping/_mapping 
```

## Using dynamic templates in document mapping
### Update mapping with dynamic templates
```
PUT movies/_mapping 
{ 
    "dynamic_templates": [{ 
        "years_as_short": { 
            "match_mapping_type": "long", 
            "match": "*year", 
            "mapping": { 
                "type": "short" 
            } 
        } 
    }] 
} 
```

## Creating an index template

### Create component template
```
PUT _component_template/component_template1
{
  "template": {
    "mappings": {
      "properties": {
        "genre": {
          "type": "keyword"
        }
      }
    }
  }
}
```

### Create dynamic component template
```
PUT _component_template/dynamic_component_template
{
  "template": {
    "mappings": {
      "dynamic_templates": [{
        "years_as_short": {
          "match_mapping_type": "long",
          "match": "*year",
          "mapping": {
            "type": "short"
          }
        }
      }]
    }
  }
}
```

### Create index template
```
PUT _index_template/template_1
{
  "index_patterns": ["movie*"],
  "template": {
    "settings": {
      "number_of_shards": 1
    },
    "mappings": {
      "_source": {
        "enabled": true
      },
      "properties": {
        "director": {
        "type": "keyword"
        }
      }
    },
    "aliases": {
      "mydata": { }
    }
  },
  "priority": 500,
  "composed_of": ["component_template1", "dynamic_component_template"],
  "version": 1,
  "_meta": {
    "description": "my custom template"
  }
}
```

## Indexing multiple documents using bulk

Run the bulk script
```console
python sampledata_bulk.py
```

### Check new movie mapping
```
GET /movies/_mapping 
```

### Check document count
```
GET movies/_count 
```








