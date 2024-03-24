# Snippets for Chapter 4

## <em>Quick links to the recipes</em>
* [Deploying standalone Elastic Agent](#deploying-standalone-elastic-agent)
* [Adding data from Beats](#adding-data-from-beats)
* [Setting up Data stream manually](#setting-up-data-stream-manually)
* [Setting up Time Series Data Stream (TSDS) manually](#setting-up-time-series-data-stream-tsds-manually)


## Deploying standalone Elastic Agent

Download Elastic Agent
```console
curl -L -O https://artifacts.elastic.co/downloads/beats/elastic-agent/elastic-agent-8.12.2-linux-x86_64.tar.gz
```
Extract Elastic Agent
```console
tar xzvf elastic-agent-8.12.2-linux-x86_64.tar.gz
```
Install Elastic Agent
```console
sudo ./elastic-agent install
```
Start Elastic Agent
```console
sudo systemctl start elastic-agent.service
```

## Adding data from Beats
Download Metricbeat
```console
curl -L -O https://artifacts.elastic.co/downloads/beats/metricbeat/metricbeat-8.12.2-amd64.deb
```
Extract Metricbeat
```console
sudo dpkg -i metricbeat-8.8.2-amd64.deb 
```
Enable Tomcat module
```console
sudo metricbeat modules enable tomcat 
```
Enable Jolokia module
```console
sudo metricbeat modules enable jolokia
```
Set up Metricbeat
```console
sudo metricbeat setup –e
```
Start Metricbeat
```console
sudo metricbeat setup –e
```

## Setting up Data stream manually

### Component template for Rennes traffic Index Lifecyle Policy
```
PUT _ilm/policy/rennes_traffic-lifecycle-policy
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_primary_shard_size": "50gb"
          }
        }
      },
      "delete": {
        "min_age": "30d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

### Component template for Rennes traffic mappings
```
PUT _component_template/rennes_traffic-mappings
{
  "template": {
    "mappings": {
      "properties": {
        "@timestamp": {
          "type": "date",
          "format": "date_optional_time||epoch_millis"
        },
        "traffic_status": {"type": "keyword"},
        "location_reference": {"type": "keyword"},
        "denomination": {"type": "text"},
        "hierarchie": {"type": "keyword"},
        "hierarchie_dv": {"type": "keyword"},
        "insee": {"type": "keyword"},
        "vehicles": {"type":"short"},
        "traveltime" : {
          "subobjects" : false,
          "properties" : {
            "reliability" : {
              "type" : "short"
            },
            "duration" : {
              "type" : "short"
            }
          }
        }
        ,
        "max_speed":{"type":"short"},
        "average_vehicle_speed":{"type":"short"},
        "location": {"type": "geo_point"},
        "data_stream": {
          "properties": {
            "namespace": {
              "type": "constant_keyword"
            },
            "type": {
              "type": "constant_keyword"
            },
            "dataset": {
              "type": "constant_keyword"
            }
          }
        }
      }
    }
  },
  "_meta": {
    "description": "Mappings for rennes traffic data fields"
  }
}
```

### Component template for index settings
```
PUT _component_template/rennes_traffic-settings
{
  "template": {
    "settings": {
      "index.lifecycle.name": "rennes_traffic-lifecycle-policy"
    }
  },
  "_meta": {
    "description": "Settings for ILM"
  }
}
```

### Rennes traffic index template
```
PUT _index_template/rennes_traffic-index-template
{
  "index_patterns": ["generic-rennes_traffic-*"],
  "data_stream": { },
  "composed_of": [ "rennes_traffic-mappings", "rennes_traffic-settings" ],
  "priority": 500,
  "_meta": {
    "description": "Template for rennes traffic data"
  }
}
```

### Ingest sample document into data stream
```
POST generic-rennes_traffic-default/_doc
{
  "@timestamp": "2024-01-17T23:07:00+02:00",
    "traffic_status": "heavy",
    "location_reference": "10273_D",
    "denomination": "Route départementale 34",
    "hierarchie": "Réseau d'armature",
    "hierarchie_dv": "Réseau de transit",
    "insee": "35206",
    "vehicles": "1",
    "traveltime.reliability": "60",
    "traveltime.duration": "16",
    "max_speed": "70",
    "average_vehicle_speed": "46",
    "location": {
      "lat": 48.04479275590756,
      "lon": -1.6502152435538264
    },
    "data_stream.type": "generic",
    "data_stream.dataset": "rennes_traffic",
    "data_stream.namespace": "default"
}
```

## Setting up Time Series Data Stream (TSDS) manually

### Creates a component template for TSDS mappings
```console
PUT _component_template/metrics-rennes_traffic-mappings@default
{
  "template": {
    "mappings": {
      "properties": {
        "@timestamp": {
          "type": "date",
          "format": "date_optional_time||epoch_millis"
        },
        "traffic_status": {
          "type": "keyword"
        },
        "oneway": {"type": "boolean"},
        "location_reference": {
          "type": "keyword",
          "time_series_dimension": true
        },
        "denomination": {
          "type": "keyword",
          "time_series_dimension": true
        },
        "hierarchie": {
          "type": "keyword",
          "time_series_dimension": true
        },
        "hierarchie_dv": {
          "type": "keyword",
          "time_series_dimension": true
        },
        "insee": {
          "type": "keyword",
          "time_series_dimension": true
        },
        "vehicle_probe_measurement": {
          "type":"long",
          "time_series_metric": "gauge"
        },
        "traveltime" : {
          "subobjects" : false,
          "properties" : {
            "reliability" : {
              "type" : "long",
              "time_series_metric": "gauge"
            },
            "duration" : {
              "type" : "long",
              "time_series_metric": "gauge"
            }
          }
        }
        ,
        "max_speed":{
          "type":"long"
        },
        "average_vehicle_speed":{
          "type":"float",
          "time_series_metric": "gauge"
        },
        "location": {"type": "geo_point"},
        "data_stream": {
          "properties": {
            "namespace": {
              "type": "constant_keyword"
            },
            "type": {
              "type": "constant_keyword"
            },
            "dataset": {
              "type": "constant_keyword"
            }
          }
        }
      }
    }
  },
  "_meta": {
    "description": "Mappings for rennes traffic metrics fields",
    "data_stream": {
      "dataset": "rennes_traffic",
      "namespace": "default",
      "type": "metrics"
    }
  }
}
```
### Create index template for TSDS
```
PUT _index_template/metrics-rennes_traffic-default-index-template
{
  "index_patterns": ["metrics-rennes_traffic-default"],
  "data_stream": {
  },
  "template": {
    "settings": {
      "index.mode": "time_series"
    }
  },
  "composed_of": [ "metrics-rennes_traffic-mappings@default", "rennes_traffic-settings" ],
  "priority": 500,
  "_meta": {
    "description": "Template for rennes traffice metrics data"
  }
}
```

### Ingest sample document into TSDS
```
POST metrics-rennes_traffic-default/_doc
{
  "@timestamp": "2024-01-17T23:07:00+02:00",
    "traffic_status": "heavy",
    "location_reference": "10273_D",
    "denomination": "Route départementale 34",
    "hierarchie": "Réseau d'armature",
    "hierarchie_dv": "Réseau de transit",
    "insee": "35206",
    "vehicles": "1",
    "traveltime.reliability": "60",
    "traveltime.duration": "16",
    "max_speed": "70",
    "average_vehicle_speed": "46",
    "location": {
      "lat": 48.04479275590756,
      "lon": -1.6502152435538264
    },
    "data_stream.type": "metrics",
    "data_stream.dataset": "rennes_traffic",
    "data_stream.namespace": "default"
}
```
### Test TSDS
```console
GET metrics-rennes_traffic-default/_search
{
  "size": 0,
  "aggs": {
    "tsid": {
      "terms": {
        "field": "_tsid"
      },
     "aggs": {
        "over_time": {
            "date_histogram": {
                "field": "@timestamp",
                "fixed_interval": "1d"
            },
            "aggs": {
                "min": {
                    "min": {
                        "field": "average_vehicle_speed"
                    }
                },
                "max": {
                    "max": {
                        "field": "average_vehicle_speed"
                    }
                },
                "avg": {
                    "avg": {
                        "field": "average_vehicle_speed"
                    }
                }
            }
        }
      }
    }
  }
}
```