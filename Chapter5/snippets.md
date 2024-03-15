# Snippets for Chapter 5

## Quick links to the snippet of the recipes in this chapter
* [Creating an ingest pipeline](#creating-an-ingest-pipeline)
* [Enriching data with custom ingest pipeline for an existing Elastic Agent integration](#enriching-data-with-custom-ingest-pipeline-for-an-existing-elastic-agent-integration)
* [Using processor to enrich your data before ingesting with Elastic Agent](#using-processor-to-enrich-your-data-before-ingesting-with-elastic-agent)
* [Installing self-managed Logstash](#installing-self-managed-logstash)
* [Setting up pivot data transform](#setting-up-pivot-data-transform)
* [Setting up latest data transform](#setting-up-latest-data-transform)


## Creating an ingest pipeline
### Sample snippet
```
Code here
```

## Enriching data with custom ingest pipeline for an existing Elastic Agent integration

## Using processor to enrich your data before ingesting with Elastic Agent

## Installing self-managed Logstash

## Setting up Pivot data transform
### Dev tools snippet to create pivot data transform
```
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

## Setting up latest data transform
### Dev tools snippet to create latest data transform
```
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