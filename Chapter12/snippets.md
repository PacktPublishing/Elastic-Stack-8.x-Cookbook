# Snippets for Chapter 12

## <em>Quick links to the recipes</em>
* [Managing snapshot lifecycle](#managing-snapshot-lifecycle)
* [Configuring Elastic Stack components with Terraform](#configuring-elastic-stack-components-with-terraform)
* [Enabling and configuring Cross-Cluster Search](#enabling-and-configuring-cross-cluster-search)


## Managing snapshot lifecycle
### Dev tools command to create a data view for SLM history indices
```
POST kbn:/api/data_views/data_view 
{ 
  "data_view": { 
    "title": ".slm-history-*", 
    "name": "SLM data view", 
    "timeFieldName": "@timestamp" 
  } 
} 
```

## Configuring Elastic Stack components with Terraform
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
```console
terraform apply --destroy 
```

## Enabling and configuring cross-cluster search
### Terraform commands
```console
terraform init
```
```console
terraform apply
```

### APM indices settings
Error Indices: 
```
logs-apm*,apm-*,new-team-deployment:logs-apm*,new-team-deployment:apm-*
```
Onboarding Indices: 
```
apm-*,new-team-deployment:apm-*
```

Span Indices: 
```
traces-apm*,apm-*,new-team-deployment:traces-apm*, new-team-deployment:apm-*
```
Transaction Indices: 
```
traces-apm*,apm-*,new-team-deployment:apm-*,new-team-deployment:traces-apm*
```

Metrics Indices: 
```
metrics-apm*,apm-*,new-team-deployment:metrics-apm*,new-team-deployment:apm-* 
```