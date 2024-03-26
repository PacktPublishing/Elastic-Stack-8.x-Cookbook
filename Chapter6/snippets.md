# Snippets for Chapter 6

## <em>Quick links to the recipes</em>
* [Exploring your data in Discover](#exploring-your-data-in-discover)
* [Exploring your data with ES|QL](#exploring-your-data-with-esql)
* [Creating visualization from Runtime fields](#creating-visualization-from-runtime-fields)
* [Creating Canvas workpad](#creating-canvas-workpad)


## Exploring your data in Discover

### Preparing regular data stream *metrics-rennes_traffic-raw*
Creates a component template for *metrics-rennes_traffic-raw* mappings
```
PUT _component_template/metrics-rennes_traffic-mappings@raw
{
  "template": {
    "mappings": {
      "properties": {
        "@timestamp": {
          "type": "date",
          "format": "date_optional_time||epoch_millis"
        },
        "traffic_status": {"type": "keyword"},
        "oneway": {"type": "boolean"},
        "location_reference": {"type": "keyword"},
        "denomination": {"type": "text"},
        "hierarchie": {"type": "keyword"},
        "hierarchie_dv": {"type": "keyword"},
        "insee": {"type": "keyword"},
        "vehicle_probe_measurement": {"type":"short"},
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
    "description": "Standard mappings for rennes traffic raw data fields",
    "data_stream": {
          "dataset": "rennes_traffic",
          "namespace": "default",
          "type": "metrics"
    }
  }
}
```

Creates a component template for *metrics-rennes_traffic-raw* Index Lifecyle Policy
```
PUT _ilm/policy/metrics-rennes_traffic-raw-lifecycle-policy
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

Creates a component template for *metrics-rennes_traffic-raw* index settings 
```
PUT _component_template/metrics-rennes_traffic-raw-settings
{
  "template": {
    "settings": {
      "index.lifecycle.name": "metrics-rennes_traffic-raw-lifecycle-policy"
    }
  },
  "_meta": {
    "description": "Settings for ILM for rennes_traffic-raw"
  }
}
```

Creates the index template for *metrics-rennes_traffic-raw*
```
PUT _index_template/metrics-rennes_traffic-raw-index-template
{
  "index_patterns": ["metrics-rennes_traffic-raw"],
  "data_stream": { },
  "composed_of": [ "metrics-rennes_traffic-mappings@raw", "metrics-rennes_traffic-raw-settings" ],
  "priority": 600,
  "_meta": {
    "description": "Template for rennes traffic raw data"
  }
}
```

## Exploring your data with ES|QL

### ES|QL congested traffic
```
from metrics-rennes_traffic-raw* 
| where traffic_status == "congested" 
| limit 50 
```

### ES|QL congested traffic with aggregation
```
from metrics-rennes_traffic-raw* 
| where traffic_status == "congested" 
| stats avg_traveltime = avg(traveltime.duration) by denomination 
| sort avg_traveltime desc 
| limit 50 
```

### ES|QL congested traffic with eval
```
from metrics-rennes_traffic-raw* 
| where traffic_status == "congested" 
| stats avg_traveltime = avg(traveltime.duration) by denomination  
| eval avg_traveltime_min = round(avg_traveltime/60) 
| sort avg_traveltime_min desc 
| keep denomination, avg_traveltime_min 
| limit 50 
```
### index mapping for *insee-codes*
```
{
  "properties": {
    "code_postal": {
      "type": "keyword"
    },
    "insee": {
      "type": "keyword"
    },
    "libelle_acheminement": {
      "type": "keyword"
    },
    "ligne_5_adresse_postale": {
      "type": "keyword"
    },
    "nom_de_la_commune": {
      "type": "keyword"
    }
  }
}
```

### Enrich policy
```
PUT /_enrich/policy/rennes-data-enrich
{
  "match": {
    "indices": [
      "insee-codes"
    ],
    "match_field": "insee",
    "enrich_fields": [
      "code_postal",
      "nom_de_la_commune"
    ]
  }
}
```

```
PUT _enrich/policy/rennes-data-enrich/_execute
```

### ES|QL congested traffic with enrich
```
from metrics-rennes_traffic-raw*
| where traffic_status == "congested"
| enrich rennes-data-enrich on insee with code_postal, nom_de_la_commune
| keep average_vehicle_speed, code_postal, nom_de_la_commune, denomination
| sort average_vehicle_speed desc
| limit 50
```

### ES|QL congested traffic with enrich and average aggregation
```
from metrics-rennes_traffic-raw*
| where traffic_status == "congested"
| enrich rennes-data-enrich on insee with code_postal, nom_de_la_commune
| stats avg_traveltime = avg(traveltime.duration) by nom_de_la_commune
| sort avg_traveltime desc
| limit 50
```

## Creating visualization from Runtime fields

### Hour of the day painless script
```
ZonedDateTime date =  doc['@timestamp'].value;
ZonedDateTime cet = date.withZoneSameInstant(ZoneId.of('Europe/Paris'));
int hour = cet.getHour();
if (hour < 10) {
    emit ('0' + String.valueOf(hour));
} else {
    emit (String.valueOf(hour));
}
```

### Day of the week painless script
```
emit(doc['@timestamp'].value.dayOfWeekEnum.getDisplayName(TextStyle.FULL, Locale.ROOT))
```

## Creating Canvas workpad

### SQL Traffic congestion over time
```
SELECT HOUR_OF_DAY("@timestamp") hour, COUNT(*) locations 
FROM "metrics-rennes_traffic-raw" 
WHERE traffic_status = 'congested' or traffic_status = 'heavy' 
GROUP BY hour 
ORDER BY hour 
```

### SQL total traffic jam 
```
SELECT COUNT(*)/10000 as locations 
FROM "metrics-rennes_traffic-raw" 
WHERE traffic_status = 'congested' or traffic_status = 'heavy' 
```

### SQL average traffic speed by hour
```
SELECT HOUR_OF_DAY("@timestamp") hour, AVG("average_vehicle_speed") speed 
FROM "metrics-rennes_traffic-raw" 
GROUP BY hour 
ORDER BY hour 
```

### SQL average traffic speed
```
SELECT AVG(average_vehicle_speed) metric 
FROM "metrics-rennes_traffic-raw" 
```

### SQL speeding locations
```
SELECT COUNT(DISTINCT location_reference) metric 
FROM "metrics-rennes_traffic-raw" 
WHERE average_vehicle_speed/max_speed > 1 
```

### SQL congested locations
```
SELECT COUNT(DISTINCT location_reference) as metric 
FROM "metrics-rennes_traffic-raw" 
WHERE traffic_status = 'congested' 
```
### SQL total locations
```
SELECT COUNT(DISTINCT location_reference) as metric 
FROM "metrics-rennes_traffic-raw" 
```
