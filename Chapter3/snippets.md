# Snippets for Chapter 3

## <em>Quick links to the recipes</em>
* [Searching with the Query DSL ](#searching-with-the-query-dsl)
* [Building advanced search query with Query DSL](#building-advanced-search-query-with-query-dsl)
* [Using Search template to pre-render search requests](#using-search-template-to-pre-render-search-requests)
* [Getting started with Search Applications for your Elasticsearch Index](#getting-started-with-search-applications-for-your-elasticsearch-index)
* [Building search experience with Search Application Client](#building-search-experience-with-search-application-client)
* [Measuring the performance of your search applications with Behaviour analytics](#measuring-the-performance-of-your-search-applications-with-behaviour-analytics)


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

### Match phrase query
```
GET movies/_search 
{ 
  "query": { 
    "match_phrase": { 
      "title": "sweet home" 
    } 
  } 
}
```
## Building advanced search query with Query DSL
Here are the Dev tools commands for this recipe
### Range query
```
GET /movies/_search
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
GET /movies/_search
{
  "query": {
    "multi_match": {
      "query": "come home",
      "fields": ["title", "plot"]
    }
  }
}
```

### Multi match most queries
```
GET /movies/_search
{
  "query": {
    "multi_match": {
      "type": "most_fields",
      "query": "come home",
      "fields": ["title", "plot"]
    }
  }
}
```

### Multi match phrase
```
GET /movies/_search
{
  "query": {
    "multi_match": {
      "type": "phrase",
      "query": "come home",
      "fields": ["title", "plot"]
    }
  }
}
```

### Boolean query
```
GET /movies/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "title": "home" } },
        { "match": { "genre": "comedy" } }
      ]
    }
  }
}
```

### Boolean query with filter
```
GET /movies/_search
{
  "query": {
    "bool": {
      "must": [ { "match": { "title": "home" } } ],
      "filter": [ { "match": { "genre": "comedy" } } ]
    }
  }
}
```

### Boolean query with should
```
GET /movies/_search
{
  "query": {
    "bool": {
      "must": [ { "match": { "title": "home" } } ],
      "should": [ { "match": { "genre": "comedy" } } ]
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
### Add search template
```
PUT _scripts/movies-search-template
{
  "script": {
    "lang": "mustache",
    "source": {
      "query": {
        "bool": {
          "must": [
            {
              "multi_match": {
                "query": "{{query}}",
                "fields": [
                  "title^4",
                  "plot",
                  "cast",
                  "director"
                ]
              }
            },
            {
              "multi_match": {
                "query": "{{query}}",
                "type": "phrase_prefix",
                "fields": [
                  "title^4",
                  "plot",
                  "director"
                ]
              }
            }
          ]
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
      "sort": [
        {
          "release_year": "desc"
        }
      ],
      "fields": [
        "title",
        "release_year",
        "director",
        "origin"
      ],
      "_source": "false"
    }
  }
}
```
### Render search template with sample parameters
```
GET _render/template  
{ 
  "id": "movies-search-template", 
  "params": { 
    "query": "space", 
    "agg_size": 3 
  } 
} 
```

### Query with search template 
```
GET movies/_search/template 
{ 
  "id": "movies-search-template", 
  "params": { 
    "query": "space", 
    "agg_size": 3 
  } 
} 
```

### Search template with conditions
```
GET _render/template 
{ 
  "source": "{ \"query\": { \"bool\": { \"filter\": [ {{#last_10y}} { \"range\": { \"release_year\": { \"gte\": \"now-10y/d\", \"lt\": \"now/d\" } } }, {{/last_10y}} { \"term\": { \"origin\": \"{{origin}}\" }}]}}}", 
  "params": { 
    "last_10y": true, 
    "origin": "American" 
  } 
} 
```

## Getting started with Search Applications for your Elasticsearch Index

### Create search application with search template
```
PUT _application/search_application/movies-search-application
{
  "indices": [
    "movies"
  ],
  "template": {
    "script": {
      "lang": "mustache",
      "source": {
        "query": {
          "bool": {
            "must": [
              {
                "multi_match": {
                  "query": "{{query}}",
                  "fields": [
                    "title^4",
                    "plot",
                    "cast",
                    "director"
                  ]
                }
              },
              {
                "multi_match": {
                  "query": "{{query}}",
                  "type": "phrase_prefix",
                  "fields": [
                    "title^4",
                    "plot",
                    "director"
                  ]
                }
              }
            ]
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
        "sort": [
          {
            "release_year": "desc"
          }
        ],
        "fields": [
          "title",
          "release_year",
          "director",
          "origin"
        ],
        "_source": "false"
      }
    }
  }
}
```

### Test the search application in Dev Tools
```
GET _application/search_application/movies-search-application/_search 
{ 
  "params": { 
    "query": "space", 
    "agg_size": "5" 
  } 
} 
```

## Building search experience with Search Application Client

### Install the react application dependencies
```console
yarn install
```

### Cross-Origin Resource Sharing (CORS) Settings for Elasticsearch
```yaml
http.cors.allow-origin: "*" 
http.cors.enabled: true 
http.cors.allow-credentials: true 
http.cors.allow-methods: OPTIONS, HEAD, GET, POST, PUT, DELETE 
http.cors.allow-headers: X-Requested-With, X-Auth-Token, Content-Type, Content-Length, Authorization, Access-Control-Allow-Headers, Accept  
```

### Update search application with search template
```
PUT _application/search_application/movies-search-application
{
  "indices": ["movies"],
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
                  "fields": [ "title^4", "plot", "cast", "director" ]
                }
              },
              {
                "multi_match" : {
                  "query":    "{{query}}",
                  "type": "phrase_prefix",
                  "fields": [ "title^4", "plot"]
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
        "size": 10,
        "agg_size": 5,
        "from": 0
      }
    }
  }
}
```

### Locate and update the following in App.tsx
```Javascript
const request = SearchApplicationClient(     
    'movies-search-application' 
    /*elasticsearch_endpoint*/, 
    /*your_api_key*/ 
) 
```

### Start the application
```console
yarn start
```

## Measuring the performance of your search applications with Behaviour analytics
Locate and uncomment the following code blocks in App.tsx
```Javascript
createTracker({  
  	endpoint: "https://xxx.cloud.es.io:443",  
  	collectionName: "movie-stats",  
  	apiKey: "xxx",  
}); 
```

```Javascript
trackPageView() 
```

```Javascript
trackSearch({  
  search: {  
  query: query,  
  results: {  
    ...  
  },  
},
})
```

```Javascript
trackSearchClick({  
  document: { ... },  
  search: {  
    ...  
  },  
  page: {  
    url: url,  
    ...  
  },  
}); 
```

Start the application
```console
yarn start
```
