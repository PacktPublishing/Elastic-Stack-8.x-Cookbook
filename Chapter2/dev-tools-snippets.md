Dev tools snippet for Chapter 2

### Movie search query
```
GET movies/_search
```

### Analyzer test
```
POST movies/_analyze
{
  "text": "A young couple decides to elope.",
  "analyzer": "standard_with_stopwords"
}
```

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

### Update with dynamic mapping
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