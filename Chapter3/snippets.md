# Dev tools snippet for Chapter 3

## Searching with the Query DSL

Here are the Dev tools commands for this recipe
### Sample query with OR operator
```
GET movies/_search
{
  "query": {
    "match": {
      "title": "Come home"
    }
  }
}
```

### Sample query with AND operator
```
GET movies/_search
{
  "query": {
    "match": {
      "title": {
        "query": "Come home",
        "operator": "and"
      }
    }
  }
}
```

### Minumum sould match query
```
GET movies/_search
{
  "query": {
    "match": {
      "title": {
        "query": "Come sweet home",
        "minimum_should_match": 2
      }
    }
  }
}
```

## Building advanced search query with Query DSL

### Range query
```
GET movies/_search
{
  "query": {
    "range": {
      "release_year": {
        "gte": "1925",
        "lte": "1927"
      }
    }
  }
}
```

### Multi match query
```
GET movies/_search
{
  "query": {
    "multi_match": {
      "query": "come home",
      "fields": [
        "title",
        "plot"
      ]
    }
  }
}
```

### Multi match most queries
```
GET movies/_search
{
  "query": {
    "multi_match": {
      "type": "most_fields",
      "query": "come home",
      "fields": [
        "title",
        "plot"
      ]
    }
  }
}
```

### Multi match phrase
```
GET movies/_search
{
  "query": {
    "multi_match": {
      "type": "phrase",
      "query": "come home",
      "fields": [
        "title",
        "plot"
      ]
    }
  }
}
```

### Boolean query
```
GET movies/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "title": "home"
          }
        },
        {
          "match": {
            "genre": "comedy"
          }
        }
      ]
    }
  }
}
```

### Boolean query with filter
```
GET movies/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "title": "home"
          }
        }
      ],
      "filter": [
        {
          "match": {
            "genre": "comedy"
          }
        }
      ]
    }
  }
}
```

### Boolean query with range filter
```
GET movies/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "title": "home"
          }
        }
      ],
      "should": [
        {
          "match": {
            "genre": "comedy"
          }
        }
      ]
    }
  }
}
```

### Boolean query with should
```
GET movies/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "title": "home"
          }
        }
      ],
      "filter": [
        {
          "range": {
            "release_year": {
              "gte": "1985"
            }
          }
        }
      ]
    }
  }
}
```

## Using Search template to pre-render search requests 

## Getting started with Search Applications for your Elasticsearch Index 

## Building search experience with Search Application Client 