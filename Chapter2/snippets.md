# Snippets for Chapter 2

## <em>Quick links to the recipes</em>
* [Adding data from the Elasticsearch client](#adding-data-from-the-elasticsearch-client)
* [Updating data in Elasticsearch](#updating-data-in-elasticsearch)
* [Deleting data in Elasticsearch](#deleting-data-in-elasticsearch)
* [Using analyzer](#using-analyzer)
* [Defining index mapping](#defining-index-mapping)
* [Using dynamic templates in document mapping](#using-dynamic-templates-in-document-mapping)
* [Creating an index template](#creating-an-index-template)
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
Index sample movie and store the document id to a tmp file
```python
response = es.index(index='movies', document=mymovie)
print(response)

# Write the '_id' to a file named tmp.txt
with open('tmp.txt', 'w') as file:
    file.write(response['_id'])

# Print the contents of the file to confirm it's written correctly
with open('tmp.txt', 'r') as file:
    print(f"document id saved to tmp.txt: {file.read()}")
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

## Updating data in Elasticsearch
Run the update script 
```console
python sampledata_update.py
```

Find the document in the movies index
```
GET movies/_search
```

## Deleting data in Elasticsearch

Find the document in the movies index
```
GET movies/_search
```
Run the delete script
```console
python sampledata_delete.py
```

Delete by query Dev Tools command
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

## Using analyzer

Run the script that create the index with an custom analyzer
```
python sampledata_analyzer.py
```

Verify the movies index settings
```
GET /movies/_settings  
```

Test the analyzer
```
POST movies/_analyze
{
  "text": "A young couple decides to elope.",
  "analyzer": "standard_with_stopwords"
}
```

## Defining index mapping
Inspect movie mapping
```
GET /movies/_mapping
```
Set movie explicit mapping
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
Reindex to new index explicit mapping
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

Check the explicit mapping
```
GET movies-with-explicit-mapping/_mapping 
```

## Using dynamic templates in document mapping
Update mapping with dynamic templates
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

Add a new movie to test the dynamic_template
```
POST movies/_doc/
{
  "review_year": 1993,
  "release_year": 1992,
  "title": "Reservoir Dogs",
  "origin": "American",
  "director": "Quentin Tarantino",
  "cast": "Harvey Keitel, Tim Roth, Steve Buscemi, Chris Penn, Michael Madsen, Lawrence Tierney",
  "genre": "crime drama",
  "wiki_page": "https://en.wikipedia.org/wiki/Reservoir_Dogs",
  "plot": "a group of criminals whose planned diamond robbery goes disastrously wrong, leading to intense suspicion and betrayal within their ranks."
}
```

Check the mapping result
```
GET /movies/_mapping 
```

## Creating an index template

Create component template for static mapping
```
PUT _component_template/movie-static-mapping
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

Create component template for dynamic mapping
```
PUT _component_template/movie-dynamic-mapping
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

Create index template
```
PUT _index_template/movie-template
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
  "composed_of": ["movie-static-mapping", "movie-dynamic-mapping"],
  "version": 1,
  "_meta": {
    "description": "movie template"
  }
}
```

Index sample document
```
POST movies/_doc/
{
  "award_year": 1998,
  "release_year": 1997,
  "title": "Titanic",
  "origin": "American",
  "director": "James Cameron",
  "cast": "Leonardo DiCaprio, Kate Winslet, Billy Zane, Frances Fisher, Victor Garber, Kathy Bates, Bill Paxton, Gloria Stuart, David Warner, Suzy Amis",
  "genre": "historical epic",
  "wiki_page": "https://en.wikipedia.org/wiki/Titanic_(1997_film)",
  "plot": "The ill-fated maiden voyage of the RMS Titanic, centering on a love story between a wealthy young woman and a poor artist aboard the luxurious, ill-fated R.M.S. Titanic"
}
```
Check new movies index mapping
```
GET /movies/_mapping 
```

## Indexing multiple documents using bulk

Run the bulk script
```console
python sampledata_bulk.py
```

Check new movies index mapping
```
GET /movies/_mapping 
```

Check document count
```
GET /movies/_count 
```









