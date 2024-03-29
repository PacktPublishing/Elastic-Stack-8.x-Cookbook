# Snippets for Chapter 4

## <em>Quick links to the recipes</em>
* [Deploying standalone Elastic Agent](#deploying-standalone-elastic-agent)
* [Adding data from Beats](#adding-data-from-beats)
* [Setting up Data stream manually](#setting-up-data-stream-manually)
* [Setting up Time Series Data Stream (TSDS) manually](#setting-up-time-series-data-stream-tsds-manually)


## Deploying standalone Elastic Agent
Sample elastic-agent.yml file (v8.12.2)
```yml
id: 35e9ab3a-0f00-46f5-8291-28327c7d1f68
revision: 2
outputs:
  default:
    type: elasticsearch
    hosts:
      - 'https://ae121ee941fe44b0bd62c6a1cd9531a4.us-central1.gcp.cloud.es.io:443'
    username: '${ES_USERNAME}'
    password: '${ES_PASSWORD}'
    preset: balanced
output_permissions:
  default:
    _elastic_agent_monitoring:
      indices:
        - names:
            - logs-elastic_agent.apm_server-default
          privileges: &ref_0
            - auto_configure
            - create_doc
        - names:
            - metrics-elastic_agent.apm_server-default
          privileges: *ref_0
        - names:
            - logs-elastic_agent.auditbeat-default
          privileges: *ref_0
        - names:
            - metrics-elastic_agent.auditbeat-default
          privileges: *ref_0
        - names:
            - logs-elastic_agent.cloud_defend-default
          privileges: *ref_0
        - names:
            - logs-elastic_agent.cloudbeat-default
          privileges: *ref_0
        - names:
            - metrics-elastic_agent.cloudbeat-default
          privileges: *ref_0
        - names:
            - logs-elastic_agent-default
          privileges: *ref_0
        - names:
            - metrics-elastic_agent.elastic_agent-default
          privileges: *ref_0
        - names:
            - metrics-elastic_agent.endpoint_security-default
          privileges: *ref_0
        - names:
            - logs-elastic_agent.endpoint_security-default
          privileges: *ref_0
        - names:
            - logs-elastic_agent.filebeat_input-default
          privileges: *ref_0
        - names:
            - metrics-elastic_agent.filebeat_input-default
          privileges: *ref_0
        - names:
            - logs-elastic_agent.filebeat-default
          privileges: *ref_0
        - names:
            - metrics-elastic_agent.filebeat-default
          privileges: *ref_0
        - names:
            - logs-elastic_agent.fleet_server-default
          privileges: *ref_0
        - names:
            - metrics-elastic_agent.fleet_server-default
          privileges: *ref_0
        - names:
            - logs-elastic_agent.heartbeat-default
          privileges: *ref_0
        - names:
            - metrics-elastic_agent.heartbeat-default
          privileges: *ref_0
        - names:
            - logs-elastic_agent.metricbeat-default
          privileges: *ref_0
        - names:
            - metrics-elastic_agent.metricbeat-default
          privileges: *ref_0
        - names:
            - logs-elastic_agent.osquerybeat-default
          privileges: *ref_0
        - names:
            - metrics-elastic_agent.osquerybeat-default
          privileges: *ref_0
        - names:
            - logs-elastic_agent.packetbeat-default
          privileges: *ref_0
        - names:
            - metrics-elastic_agent.packetbeat-default
          privileges: *ref_0
        - names:
            - logs-elastic_agent.pf_elastic_collector-default
          privileges: *ref_0
        - names:
            - logs-elastic_agent.pf_elastic_symbolizer-default
          privileges: *ref_0
        - names:
            - logs-elastic_agent.pf_host_agent-default
          privileges: *ref_0
    _elastic_agent_checks:
      cluster:
        - monitor
    6728c7ca-b716-4ac4-9050-6c946a146662:
      indices:
        - names:
            - logs-system.auth-default
          privileges: *ref_0
        - names:
            - logs-system.syslog-default
          privileges: *ref_0
        - names:
            - logs-system.application-default
          privileges: *ref_0
        - names:
            - logs-system.security-default
          privileges: *ref_0
        - names:
            - logs-system.system-default
          privileges: *ref_0
        - names:
            - metrics-system.cpu-default
          privileges: *ref_0
        - names:
            - metrics-system.diskio-default
          privileges: *ref_0
        - names:
            - metrics-system.filesystem-default
          privileges: *ref_0
        - names:
            - metrics-system.fsstat-default
          privileges: *ref_0
        - names:
            - metrics-system.load-default
          privileges: *ref_0
        - names:
            - metrics-system.memory-default
          privileges: *ref_0
        - names:
            - metrics-system.network-default
          privileges: *ref_0
        - names:
            - metrics-system.process-default
          privileges: *ref_0
        - names:
            - metrics-system.process.summary-default
          privileges: *ref_0
        - names:
            - metrics-system.socket_summary-default
          privileges: *ref_0
        - names:
            - metrics-system.uptime-default
          privileges: *ref_0
    47420f8a-8788-4894-93c1-93f8ab86c4e2:
      indices:
        - names:
            - logs-apache.access-default
          privileges: *ref_0
        - names:
            - logs-apache.error-default
          privileges: *ref_0
        - names:
            - metrics-apache.status-default
          privileges: *ref_0
agent:
  download:
    sourceURI: 'https://artifacts.elastic.co/downloads/'
  monitoring:
    enabled: true
    use_output: default
    namespace: default
    logs: true
    metrics: true
  features: {}
  protection:
    enabled: false
    uninstall_token_hash: hOHQw11akrp9VWZZd2FIhupi3veg9fuu6ddWiKifal4=
    signing_key: >-
      MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEJ0N1Z4TCW6u1yO/0KLycrTE3DxpaQ7udlyVYwvWadsZgpGmr4Idxn3DA3IVTBbc713ZQklE5eF9ffU3akVA+XQ==
inputs:
  - id: logfile-system-6728c7ca-b716-4ac4-9050-6c946a146662
    name: system-2
    revision: 1
    type: logfile
    use_output: default
    meta:
      package:
        name: system
        version: 1.54.0
    data_stream:
      namespace: default
    package_policy_id: 6728c7ca-b716-4ac4-9050-6c946a146662
    streams:
      - id: logfile-system.auth-6728c7ca-b716-4ac4-9050-6c946a146662
        data_stream:
          dataset: system.auth
          type: logs
        ignore_older: 72h
        paths:
          - /var/log/auth.log*
          - /var/log/secure*
        exclude_files:
          - \.gz$
        multiline:
          pattern: ^\s
          match: after
        tags:
          - system-auth
        processors:
          - add_locale: null
          - rename:
              fields:
                - from: message
                  to: event.original
              ignore_missing: true
              fail_on_error: false
          - syslog:
              field: event.original
              ignore_missing: true
              ignore_failure: true
      - id: logfile-system.syslog-6728c7ca-b716-4ac4-9050-6c946a146662
        data_stream:
          dataset: system.syslog
          type: logs
        paths:
          - /var/log/messages*
          - /var/log/syslog*
          - /var/log/system*
        exclude_files:
          - \.gz$
        multiline:
          pattern: ^\s
          match: after
        processors:
          - add_locale: null
        tags: null
        ignore_older: 72h
  - id: winlog-system-6728c7ca-b716-4ac4-9050-6c946a146662
    name: system-2
    revision: 1
    type: winlog
    use_output: default
    meta:
      package:
        name: system
        version: 1.54.0
    data_stream:
      namespace: default
    package_policy_id: 6728c7ca-b716-4ac4-9050-6c946a146662
    streams:
      - id: winlog-system.application-6728c7ca-b716-4ac4-9050-6c946a146662
        name: Application
        data_stream:
          dataset: system.application
          type: logs
        condition: '${host.platform} == ''windows'''
        ignore_older: 72h
      - id: winlog-system.security-6728c7ca-b716-4ac4-9050-6c946a146662
        name: Security
        data_stream:
          dataset: system.security
          type: logs
        condition: '${host.platform} == ''windows'''
        ignore_older: 72h
      - id: winlog-system.system-6728c7ca-b716-4ac4-9050-6c946a146662
        name: System
        data_stream:
          dataset: system.system
          type: logs
        condition: '${host.platform} == ''windows'''
        ignore_older: 72h
  - id: system/metrics-system-6728c7ca-b716-4ac4-9050-6c946a146662
    name: system-2
    revision: 1
    type: system/metrics
    use_output: default
    meta:
      package:
        name: system
        version: 1.54.0
    data_stream:
      namespace: default
    package_policy_id: 6728c7ca-b716-4ac4-9050-6c946a146662
    streams:
      - id: system/metrics-system.cpu-6728c7ca-b716-4ac4-9050-6c946a146662
        data_stream:
          dataset: system.cpu
          type: metrics
        metricsets:
          - cpu
        cpu.metrics:
          - percentages
          - normalized_percentages
        period: 10s
      - id: system/metrics-system.diskio-6728c7ca-b716-4ac4-9050-6c946a146662
        data_stream:
          dataset: system.diskio
          type: metrics
        metricsets:
          - diskio
        diskio.include_devices: null
        period: 10s
      - id: system/metrics-system.filesystem-6728c7ca-b716-4ac4-9050-6c946a146662
        data_stream:
          dataset: system.filesystem
          type: metrics
        metricsets:
          - filesystem
        period: 1m
        processors:
          - drop_event.when.regexp:
              system.filesystem.mount_point: ^/(sys|cgroup|proc|dev|etc|host|lib|snap)($|/)
      - id: system/metrics-system.fsstat-6728c7ca-b716-4ac4-9050-6c946a146662
        data_stream:
          dataset: system.fsstat
          type: metrics
        metricsets:
          - fsstat
        period: 1m
        processors:
          - drop_event.when.regexp:
              system.fsstat.mount_point: ^/(sys|cgroup|proc|dev|etc|host|lib|snap)($|/)
      - id: system/metrics-system.load-6728c7ca-b716-4ac4-9050-6c946a146662
        data_stream:
          dataset: system.load
          type: metrics
        metricsets:
          - load
        condition: '${host.platform} != ''windows'''
        period: 10s
      - id: system/metrics-system.memory-6728c7ca-b716-4ac4-9050-6c946a146662
        data_stream:
          dataset: system.memory
          type: metrics
        metricsets:
          - memory
        period: 10s
      - id: system/metrics-system.network-6728c7ca-b716-4ac4-9050-6c946a146662
        data_stream:
          dataset: system.network
          type: metrics
        metricsets:
          - network
        period: 10s
        network.interfaces: null
      - id: system/metrics-system.process-6728c7ca-b716-4ac4-9050-6c946a146662
        data_stream:
          dataset: system.process
          type: metrics
        metricsets:
          - process
        period: 10s
        process.include_top_n.by_cpu: 5
        process.include_top_n.by_memory: 5
        process.cmdline.cache.enabled: true
        process.cgroups.enabled: false
        process.include_cpu_ticks: false
        processes:
          - .*
      - id: >-
          system/metrics-system.process.summary-6728c7ca-b716-4ac4-9050-6c946a146662
        data_stream:
          dataset: system.process.summary
          type: metrics
        metricsets:
          - process_summary
        period: 10s
      - id: >-
          system/metrics-system.socket_summary-6728c7ca-b716-4ac4-9050-6c946a146662
        data_stream:
          dataset: system.socket_summary
          type: metrics
        metricsets:
          - socket_summary
        period: 10s
      - id: system/metrics-system.uptime-6728c7ca-b716-4ac4-9050-6c946a146662
        data_stream:
          dataset: system.uptime
          type: metrics
        metricsets:
          - uptime
        period: 10s
  - id: logfile-apache-47420f8a-8788-4894-93c1-93f8ab86c4e2
    name: apache-standalone
    revision: 1
    type: logfile
    use_output: default
    meta:
      package:
        name: apache
        version: 1.17.0
    data_stream:
      namespace: default
    package_policy_id: 47420f8a-8788-4894-93c1-93f8ab86c4e2
    streams:
      - id: logfile-apache.access-47420f8a-8788-4894-93c1-93f8ab86c4e2
        data_stream:
          dataset: apache.access
          type: logs
        paths:
          - /var/log/apache2/access.log*
          - /var/log/apache2/other_vhosts_access.log*
          - /var/log/httpd/access_log*
        tags:
          - apache-access
        exclude_files:
          - .gz$
      - id: logfile-apache.error-47420f8a-8788-4894-93c1-93f8ab86c4e2
        data_stream:
          dataset: apache.error
          type: logs
        paths:
          - /var/log/apache2/error.log*
          - /var/log/httpd/error_log*
        exclude_files:
          - .gz$
        tags:
          - apache-error
        processors:
          - add_locale: null
  - id: apache/metrics-apache-47420f8a-8788-4894-93c1-93f8ab86c4e2
    name: apache-standalone
    revision: 1
    type: apache/metrics
    use_output: default
    meta:
      package:
        name: apache
        version: 1.17.0
    data_stream:
      namespace: default
    package_policy_id: 47420f8a-8788-4894-93c1-93f8ab86c4e2
    streams:
      - id: apache/metrics-apache.status-47420f8a-8788-4894-93c1-93f8ab86c4e2
        data_stream:
          dataset: apache.status
          type: metrics
        metricsets:
          - status
        hosts:
          - 'http://127.0.0.1'
        period: 30s
        server_status_path: /server-status
signed:
  data: >-
    eyJpZCI6IjM1ZTlhYjNhLTBmMDAtNDZmNS04MjkxLTI4MzI3YzdkMWY2OCIsImFnZW50Ijp7ImZlYXR1cmVzIjp7fSwicHJvdGVjdGlvbiI6eyJlbmFibGVkIjpmYWxzZSwidW5pbnN0YWxsX3Rva2VuX2hhc2giOiJoT0hRdzExYWtycDlWV1paZDJGSWh1cGkzdmVnOWZ1dTZkZFdpS2lmYWw0PSIsInNpZ25pbmdfa2V5IjoiTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFSjBOMVo0VENXNnUxeU8vMEtMeWNyVEUzRHhwYVE3dWRseVZZd3ZXYWRzWmdwR21yNElkeG4zREEzSVZUQmJjNzEzWlFrbEU1ZUY5ZmZVM2FrVkErWFE9PSJ9fSwiaW5wdXRzIjpbeyJpZCI6ImxvZ2ZpbGUtc3lzdGVtLTY3MjhjN2NhLWI3MTYtNGFjNC05MDUwLTZjOTQ2YTE0NjY2MiIsIm5hbWUiOiJzeXN0ZW0tMiIsInJldmlzaW9uIjoxLCJ0eXBlIjoibG9nZmlsZSJ9LHsiaWQiOiJ3aW5sb2ctc3lzdGVtLTY3MjhjN2NhLWI3MTYtNGFjNC05MDUwLTZjOTQ2YTE0NjY2MiIsIm5hbWUiOiJzeXN0ZW0tMiIsInJldmlzaW9uIjoxLCJ0eXBlIjoid2lubG9nIn0seyJpZCI6InN5c3RlbS9tZXRyaWNzLXN5c3RlbS02NzI4YzdjYS1iNzE2LTRhYzQtOTA1MC02Yzk0NmExNDY2NjIiLCJuYW1lIjoic3lzdGVtLTIiLCJyZXZpc2lvbiI6MSwidHlwZSI6InN5c3RlbS9tZXRyaWNzIn0seyJpZCI6ImxvZ2ZpbGUtYXBhY2hlLTQ3NDIwZjhhLTg3ODgtNDg5NC05M2MxLTkzZjhhYjg2YzRlMiIsIm5hbWUiOiJhcGFjaGUtc3RhbmRhbG9uZSIsInJldmlzaW9uIjoxLCJ0eXBlIjoibG9nZmlsZSJ9LHsiaWQiOiJhcGFjaGUvbWV0cmljcy1hcGFjaGUtNDc0MjBmOGEtODc4OC00ODk0LTkzYzEtOTNmOGFiODZjNGUyIiwibmFtZSI6ImFwYWNoZS1zdGFuZGFsb25lIiwicmV2aXNpb24iOjEsInR5cGUiOiJhcGFjaGUvbWV0cmljcyJ9XX0=
  signature: >-
    MEQCIE+0QHUGqN7tHw6SlLyzZN7F1jjR6GtCjta/3bNGejXTAiA47CWiI4E804eOJzAhDTU4TJXXB1oxgmflFnn7nB1H3Q==
secret_references: []
```
Download Elastic Agent
```console
curl -L -O https://artifacts.elastic.co/downloads/beats/elastic-agent/elastic-agent-8.12.2-linux-x86_64.tar.gz
```
Extract Elastic Agent
```console
tar xzvf elastic-agent-8.12.2-linux-x86_64.tar.gz
```
Replace elastic-agent.yml file with the one downloaded from Kibana
```console
cp /tmp/elastic-agent.yml /home/admin/elastic-agent-8.12.2-linux-x86_64
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
  "@timestamp": "2024-04-17T11:07:00",
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
```
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

Run the Python script to ingest into Data stream
```console
pip install -r requirements.txt
```
```console
python tsds.py
```

Verify the data stream
```
GET generic-rennes_traffic-default/_search 
```

### Ingest sample document into TSDS

Get the current time from terminal in the right format
```console
date -u +"%Y-%m-%dT%H:%M:%SZ"
```
Change @timestamp with you current time that you got from the terminal
```
POST /metrics-rennes_traffic-default/_doc
{
  "@timestamp": "<your_current_time_here>",
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

Run the Python script to ingest into TSDS
```console
python tsds.py
```

### Test TSDS
```
GET /metrics-rennes_traffic-default/_search
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

Verify the TSDS
```
GET metrics-rennes_traffic-default/_search 
```
