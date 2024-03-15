# Snippets for Chapter 5

## Quick links to the snippet of the recipes in this chapter
* [Creating an ingest pipeline](#creating-an-ingest-pipeline)
* [Enriching data with custom ingest pipeline for an existing Elastic Agent integration](#enriching-data-with-custom-ingest-pipeline-for-an-existing-elastic-agent-integration)
* [Using processor to enrich your data before ingesting with Elastic Agent](#using-processor-to-enrich-your-data-before-ingesting-with-elastic-agent)
* [Installing self-managed Logstash](#installing-self-managed-logstash)
* [Creating a Logstash pipeline](#creating-a-logstash-pipeline)
* [Setting up Pivot data transform](#setting-up-pivot-data-transform)
* [Setting up Latest data transform](#setting-up-latest-data-transform)


## Creating an ingest pipeline
### Sample snippet
```
Code here
```

## Enriching data with custom ingest pipeline for an existing Elastic Agent integration

## Using processor to enrich your data before ingesting with Elastic Agent

## Installing self-managed Logstash

## Creating a Logstash pipeline
### Input plugin (rennes_traffic-default.conf)
```yaml
input {
    http_poller {
        urls => {
            rennes_data_url => "https://data.rennesmetropole.fr/explore/dataset/etat-du-trafic-en-temps-reel/download?format=csv&timezone=Europe/Paris&use_labels_for_header=false"
        }
        request_timeout => 60
        schedule => { every => "10m" }
        codec => "line"
    }
}
```

### Filter plugins (rennes_traffic-default.conf)
```yaml
filter{
	csv {
        separator => ";"
        skip_header => "true"
        columns => ["datetime","predefinedlocationreference","averagevehiclespeed","traveltime","traveltimereliability","trafficstatus","vehicleprobemeasurement","geo_point_2d","geo_shape","gml_id","id_rva_troncon_fcd_v1_1","hierarchie","hierarchie_dv","denomination","insee","sens_circule","vitesse_maxi"]
        remove_field => ["geo_shape","gml_id","id_rva_troncon_fcd_v1_1"]
    }

    date {
        match => ["datetime", "UNIX"]
        target => "@timestamp"
    }

    if [sens_circule] == "Sens unique" {
        mutate {
            add_field => { "oneway" => "true" }
        }
    } 
    else {
        mutate {
            add_field => { "oneway" => "false" }
        }
    }

    mutate {
        rename => {"traveltime" => "traveltime.duration"}
        rename => {"predefinedlocationreference" => "location_reference"}
        rename => {"traveltimereliability" => "traveltime.reliability"}
        rename => {"vitesse_maxi" => "max_speed"}
        rename => {"geo_point_2d" => "location"}
        rename => {"averagevehiclespeed" => "average_vehicle_speed"}
        rename => {"trafficstatus" => "traffic_status"}
        rename => {"vehicleprobemeasurement" => "vehicle_probe_measurement"}
    }
    mutate {
        remove_field => ["datetime","message","path","host","@version","original","event.original","tags","sens_circule"]
    }
}
```

### Output plugins (rennes_traffic-default.conf)
```yaml
output {
    elasticsearch { 
        cloud_id => "CLOUD_ID"
        cloud_auth => "user:password"
        data_stream => true
        data_stream_type => "metrics"
        data_stream_dataset => "rennes_traffic"
        data_stream_namespace => "default"
    }

    stdout { codec => rubydebug }
}```

### Start Logstash
```console
sudo systemctl start logstash.service 
```

## Setting up Pivot data transform
### Bucket script aggregation
```json
"autorized_speed_percentage": {
    "bucket_script": { 
        "buckets_path": { 
            "avg_speed": "average_vehicle_speed.avg.value", 
            "maximum_speed": "max_speed.max.value" 
        }, 
        "script": "(params.avg_speed / params.maximun _speed) * 100" 
    } 
} 
```

### Dev tools snippet to create pivot data transform
```json
PUT _transform/rennes-traffic-location-pivot-transform
{
  "source": {
    "index": [
      "metrics-rennes_traffic-default"
    ]
  },
  "pivot": {
    "group_by": {
      "denomination": {
        "terms": {
          "field": "denomination"
        }
      },
      "hierarchie": {
        "terms": {
          "field": "hierarchie"
        }
      },
      "hierarchie_dv": {
        "terms": {
          "field": "hierarchie_dv"
        }
      },
      "location_reference": {
        "terms": {
          "field": "location_reference"
        }
      }
    },
    "aggregations": {
      "average_vehicle_speed.avg": {
        "avg": {
          "field": "average_vehicle_speed"
        }
      },
      "traveltime.duration.avg": {
        "avg": {
          "field": "traveltime.duration"
        }
      },
      "traveltime.reliability.avg": {
        "avg": {
          "field": "traveltime.reliability"
        }
      },
      "vehicle_probe_measurement.avg": {
        "avg": {
          "field": "vehicle_probe_measurement"
        }
      },
      "max_speed.max": {
        "max": {
          "field": "max_speed"
        }
      },
      "autorized_speed_percentage": {
        "bucket_script": {
          "buckets_path": {
            "avg_speed": "average_vehicle_speed.avg.value",
            "maximum_speed": "max_speed.max.value"
          },
          "script": "(params.avg_speed / params.maximum_speed) * 100"
        }
      }
    }
  },
  "description": "rennes-traffic-location-pivot-transform",
  "dest": {
    "index": "rennes-traffic-location"
  },
  "sync": {
    "time": {
      "field": "@timestamp"
    }
  }
}
```

## Setting up Latest data transform
### Dev tools snippet to create latest data transform
```json
PUT _transform/rennes-traffic-location-latest-trafficjam-transform
{
  "source": {
    "index": [
      "metrics-rennes_traffic-default"
    ]
  },
  "latest": {
    "unique_key": [
      "location_reference"
    ],
    "sort": "@timestamp"
  },
  "description": "rennes-traffic-location-latest-trafficjam-transform",
  "dest": {
    "index": "rennes-traffic-latest-trafficjam-location"
  },
  "sync": {
    "time": {
      "field": "@timestamp"
    }
  }
}
```