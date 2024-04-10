# Snippets for Chapter 8

## <em>Quick links to the recipes</em>
* [Finding deviation in your data with outlier detection](#finding-deviation-in-your-data-with-outlier-detection)
* [Building a model to perform regression analysis ](#building-a-model-to-perform-regression-analysis)
* [Building a model for classification ](#building-a-model-for-classification)
* [Using trained model for inference](#using-trained-model-for-inference)
* [Deploying third-party NLP models and testing via UI](#deploying-third-party-nlp-models-and-testing-via-ui)
* [Running advanced data processing with trained models](#running-advanced-data-processing-with-trained-models)


## Finding deviation in your data with outlier detection
### Data transform
Create the Transform
```
PUT _transform/rennes-traffic-dataframe-analysis
{
  "source": {
    "index": [
      "metrics-rennes_traffic-raw"
    ],
    "runtime_mappings": {
      "day_of_week": {
        "type": "keyword",
        "script": {
          "source": "emit(doc['@timestamp'].value.dayOfWeekEnum.getDisplayName(TextStyle.FULL, Locale.ROOT))"
        }
      },
      "hour_of_day": {
        "type": "keyword",
        "script": {
          "source": "ZonedDateTime date =  doc['@timestamp'].value;\nZonedDateTime cet = date.withZoneSameInstant(ZoneId.of('Europe/Paris'));\nint hour = cet.getHour();\nif (hour < 10) {\n    emit ('0' + String.valueOf(hour));\n} else {\n    emit (String.valueOf(hour));\n}"
        }
      }
    }
  },
  "pivot": {
    "group_by": {
      "location_reference": {
        "terms": {
          "field": "location_reference"
        }
      },
      "hour_of_day": {
        "terms": {
          "field": "hour_of_day"
        }
      },
      "day_of_week": {
        "terms": {
          "field": "day_of_week"
        }
      }
    },
    "aggregations": {
      "average_vehicle_speed.avg": {
        "avg": {
          "field": "average_vehicle_speed"
        }
      },
      "max_speed.max": {
        "max": {
          "field": "max_speed"
        }
      },
      "traveltime.duration.avg": {
        "avg": {
          "field": "traveltime.duration"
        }
      },
      "top_metrics": {
        "top_metrics": {
          "metrics": [
            {
              "field": "traffic_status"
            }
          ],
          "sort": {
            "@timestamp": "asc"
          }
        }
      }
    }
  },
  "dest": {
    "index": "rennes-traffic-dataframe-analysis"
  },
  "sync": {
    "time": {
      "field": "@timestamp"
    }
  }
}
```

Start the Transform
```
POST _transform/rennes-traffic-dataframe-analysis/_start
```

### Sample outlier job
```json
{
  "id": "rennes-traffic-dataframe-outlier",
  "create_time": 1699630045127,
  "version": "10.0.0",
  "authorization": {
    "roles": [
      "viewer",
      "editor",
      "superuser"
    ]
  },
  "description": "Outlier detection for rennes traffic",
  "source": {
    "index": [
      "rennes-traffic-dataframe-analysis"
    ],
    "query": {
      "match_all": {}
    }
  },
  "dest": {
    "index": "rennes-traffic-dataframe-outlier",
    "results_field": "ml"
  },
  "analysis": {
    "outlier_detection": {
      "compute_feature_influence": true,
      "outlier_fraction": 0.05,
      "standardization_enabled": true
    }
  },
  "analyzed_fields": {
    "includes": [
      "max_speed.max",
      "traveltime.duration.avg",
      "average_vehicle_speed.avg"
    ],
    "excludes": []
  },
  "model_memory_limit": "500mb",
  "allow_lazy_start": false,
  "max_num_threads": 1
}
```

## Building a model to perform regression analysis
### Sample regression job
```json
{
  "id": "rennes-traffic-dataframe-regression",
  "create_time": 1712700893689,
  "version": "12.0.0",
  "authorization": {
    "roles": [
      "editor",
      "viewer",
      "superuser"
    ]
  },
  "description": "",
  "source": {
    "index": [
      "rennes-traffic-dataframe-analysis"
    ],
    "query": {
      "match_all": {}
    }
  },
  "dest": {
    "index": "rennes-traffic-dataframe-regression",
    "results_field": "ml"
  },
  "analysis": {
    "regression": {
      "dependent_variable": "traveltime.duration.avg",
      "num_top_feature_importance_values": 4,
      "prediction_field_name": "traveltime.duration.avg_prediction",
      "training_percent": 50,
      "randomize_seed": 7096944827446183000,
      "loss_function": "mse",
      "early_stopping_enabled": true
    }
  },
  "analyzed_fields": {
    "includes": [
      "day_of_week",
      "hour_of_day",
      "location_reference",
      "max_speed.max",
      "traveltime.duration.avg"
    ],
    "excludes": []
  },
  "model_memory_limit": "58mb",
  "allow_lazy_start": false,
  "max_num_threads": 1
}
```
## Building a model for classification
### Sample classification job
```json
{
  "id": "rennes-traffic-dataframe-classification",
  "create_time": 1712734380025,
  "version": "12.0.0",
  "authorization": {
    "roles": [
      "editor",
      "viewer",
      "superuser"
    ]
  },
  "description": "",
  "source": {
    "index": [
      "rennes-traffic-dataframe-analysis"
    ],
    "query": {
      "match_all": {}
    }
  },
  "dest": {
    "index": "rennes-traffic-dataframe-classification",
    "results_field": "ml"
  },
  "analysis": {
    "classification": {
      "dependent_variable": "top_metrics.traffic_status",
      "num_top_feature_importance_values": 4,
      "class_assignment_objective": "maximize_minimum_recall",
      "num_top_classes": -1,
      "prediction_field_name": "top_metrics.traffic_status_prediction",
      "training_percent": 20,
      "randomize_seed": 8520675537385589000,
      "early_stopping_enabled": true
    }
  },
  "analyzed_fields": {
    "includes": [
      "day_of_week",
      "hour_of_day",
      "location_reference",
      "max_speed.max",
      "top_metrics.traffic_status"
    ],
    "excludes": []
  },
  "model_memory_limit": "117mb",
  "allow_lazy_start": false,
  "max_num_threads": 1
}
```
## Using trained model for inference

```console
pip install -r requirements.txt
```

```console
streamlit run rennes_traffic_predict.py
```
## Deploying third-party NLP models and testing via UI

```console
pip install 'eland[pytorch]'
```
```console
eland_import_hub_model –help
```
```console
eland_import_hub_model \
--cloud-id <ES_CID> \
-u <ES_USER> -p <ES_PWD> \
--hub-model-id dslim/bert-base-NER \
--task-type ner  --start
```

```console
eland_import_hub_model \
--cloud-id <ES_CID> \
-u <ES_USER> -p <ES_PWD> \
--hub-model-id nickmuchi/distilroberta-base-movie-genre-prediction \
--task-type text_classification  --start
```

## Running advanced data processing with trained models

### *movie-anonymized* ingest pipeline
```json
{
  "description": "Ingest pipeline for movie anonymization",
  "processors": [
    {
      "csv": {
        "field": "message",
        "target_fields": [
          "release_year",
          "title",
          "origin",
          "director",
          "cast",
          "genre",
          "wiki",
          "plot"
        ],
        "ignore_missing": false
      }
    },
    {
        "set": {
          "field": "anonymized_plot",
          "value": "{{{plot}}}"
        }
    },
    {
      "convert": {
        "field": "release_year",
        "type": "long",
        "ignore_missing": true
      }
    },
    {
          "inference": {
            "model_id": "dslim__bert-base-ner",
            "field_map": {
              "plot": "text_field"
            }
          }
    },
    {
          "script": {
            "lang": "painless",
            "source": "String msg = ctx['plot'];\r\n for (item in ctx['ml']['inference']['entities']) {\r\n if (item['class_name']!='MISC') {\r\n msg = msg.replace(item['entity'], '<' + item['class_name'] + '>')\r\n}\r\n}\r\n ctx['anonymized_plot']=msg"
          }
    },
    {
      "redact": {
        "field": "anonymized_plot",
        "patterns": [
          "%{YEAR:YEAR}"
        ]
      }
    },
    {
      "remove": {
        "field": ["message","ml","plot"],
        "ignore_missing": true,
        "ignore_failure": true
      }
    }
  ]
}
```

### *movie-anonymized* mapping
```json
{
  "properties": {
    "cast": {
      "type": "text"
    },
    "director": {
      "type": "text"
    },
    "genre": {
      "type": "keyword"
    },
    "origin": {
      "type": "keyword"
    },
    "release_year": {
      "type": "long"
    },
    "title": {
      "type": "text"
    },
    "wiki": {
      "type": "keyword"
    },
    "anonymized_plot": {
      "type": "text"
    }
  }
}
```