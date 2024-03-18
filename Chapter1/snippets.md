# Snippets for Chapter 1

## <em>Quick links to the recipes</em>
* [Installing Elastic Stack with Elastic Cloud on Kubernetes](#installing-elastic-stack-with-elastic-cloud-on-kubernetes)
* [Creating and setting up data tiering](#creating-and-setting-up-data-tiering)
* [Creating and setting up additional Elasticsearch nodes](#creating-and-setting-up-additional-elasticsearch-nodes)
* [Setting up snapshot repository](#setting-up-snapshot-repository)



## Installing Elastic Stack with Elastic Cloud on Kubernetes

Create the ECK custom resource definitions
```console
kubectl create -f https://download.elastic.co/downloads/eck/2.11.0/crds.yaml
```
Install ECK Operator
```console
kubectl apply -f https://download.elastic.co/downloads/eck/2.11.0/operator.yaml
```
Monitor the operator logs
```console
kubectl -n elastic-system logs -f statefulset.apps/elastic-operator
```
Deploy an  3 Elasticsearch nodes cluster
```console
kubectl apply -f elasticsearch.yaml
```
Deploy Kibana 
```console
kubectl apply -f kibana.yaml
```
Check details of Kibana
```console
kubectl get kibana
```
Get the ClusterIP service created for Kibana 
```console
kubectl get service kibana-sample-kb-http
```
Retrieve default password
```console
kubectl get secret elasticsearch-sample-es-elastic-user -o=jsonpath='{.data.elastic}' | base64 --decode; echo
```

## Creating and setting up data tiering
Generate enrollment token
```console
./bin/elasticsearch --enrollment-token -s node 
```
Cold node definition
```yaml
node.name: node-frozen
node.roles: ["data_frozen"] 
```
Frozen node definition
```yaml
node.name: node-cold  
node.roles: ["data_cold"] 
```
Start the node with enrollment token
```console
./bin/elasticsearch --enrollment-token <enrollment-token>
```

## Creating and setting up additional Elasticsearch nodes

## Setting up snapshot repository

### Sample AWS S3 policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::elasticsearch-s3-bucket-repository",
        "arn:aws:s3:::elasticsearch-s3-bucket-repository/*"
      ]
    }
  ]
}
```


