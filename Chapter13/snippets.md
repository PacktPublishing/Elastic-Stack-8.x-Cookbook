# Snippets for Chapter 13

## <em>Quick links to the recipes</em>
* [Setting up stack monitoring](#setting-up-stack-monitoring)
* [Monitoring cluster health via API](#monitoring-cluster-health-via-api)
* [Enabling audit logging](#enabling-audit-logging )


## Setting up stack monitoring
### Terraform commands
```console
terraform init
```
```console
terraform plan 
```
```console
terraform apply
```

## Monitoring cluster health via API
### Dev tools snippets
```
GET _health_report 
```
```
GET _health_report/shards_availability
```
```
GET _cluster/allocation/explain
{
  "index": "<index-name>",
  "shard": 0,
  "primary": false
}
```

## Enabling audit logging
### Elasticsearch user settings
```yaml
xpack.security.audit.enabled: true 
xpack.security.audit.logfile.events.emit_request_body: false 
```

### Kibana user settings
```yaml
xpack.security.audit.enabled: true 
```
### ES|QL snippet for user login attempts
```sql
from elastic-cloud-logs-8  
    | where event.type == "access" 
    | stats attempts = count(event.type) by user.name, kibana.space_id, event.outcome
    | limit 20
```

### ES|QL snippet for user login granted attempts
```sql
from elastic-cloud-logs-8 
    | where event.action == "access_granted"  
    | stats attempts = count(event.action) by user.name,elasticsearch.audit.user.roles, elasticsearch.audit.indices 
    | sort attempts desc
```
