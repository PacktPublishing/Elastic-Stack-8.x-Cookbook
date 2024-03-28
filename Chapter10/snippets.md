# Snippets for Chapter 10

## <em>Quick links to the recipes</em>
* [Instrumenting your application with Elastic APM Agent](#instrumenting-your-application-with-elastic-apm-agent)
* [Setting up Real User Monitoring](#setting-up-real-user-monitoring)
* [Instrumenting and monitoring with OpenTelemetry](#instrumenting-and-monitoring-with-opentelemetry)
* [Monitoring Kubernetes environments with Elastic Agent](#monitoring-kubernetes-environments-with-elastic-agent)

## Instrumenting your application with Elastic APM Agent
### Elastiflix with no-instrumentation
**In [Chapter10/Elastiflix/no-instrumentation](https://github.com/PacktPublishing/Elastic-Stack-8.x-Cookbook/tree/main/Chapter10/Elastiflix/no-instrumentation)**

Start the application
```console
docker-compose -f docker-compose.yml up --build -d 
```
After verification at http://localhost:9000, stop the application
```console
docker-compose -f docker-compose.yml down
```
### Elastiflix with java-instrumentation
**In [Chapter10/Elastiflix/java-instrumentation](https://github.com/PacktPublishing/Elastic-Stack-8.x-Cookbook/tree/main/Chapter10/Elastiflix/java-instrumentation)**

After .env configuration, start the application
```console
docker-compose -f docker-compose.yml up --build -d 
```
Visit http://localhost:9000 and verify Java instrumentation in APM

Then, stop the application
```console
docker-compose -f docker-compose.yml down 
```

### Elastiflix with full-instrumentation
**In [Chapter10/Elastiflix/full-intrumentation](https://github.com/PacktPublishing/Elastic-Stack-8.x-Cookbook/tree/main/Chapter10/Elastiflix/full-intrumentation)**

After .env configuration, start the application
```console
docker-compose -f docker-compose.yml up --build -d 
```
Visit http://localhost:9000 and verify full instrumentation in APM

Then, stop the application
```console
docker-compose -f docker-compose.yml down 
```

## Setting up Real User Monitoring
### Elastiflix full-instrumentation with RUM
**In [Chapter10/Elastiflix/full-intrumentation-with-rum](https://github.com/PacktPublishing/Elastic-Stack-8.x-Cookbook/tree/main/Chapter10/Elastiflix/full-intrumentation-with-rum)**

After .env configuration, start the application
```console
docker-compose -f docker-compose.yml up --build -d 
```
Visit http://localhost:9000 and verify full instrumentation in APM and User experience UI

Then, stop the application
```console
docker-compose -f docker-compose.yml down 
```

## Instrumenting and monitoring with OpenTelemetry
Create an environment variable for the APM URL
```console
export APM_URL_WITHOUT_PREFIX=<your-url>
```
Create an environment variable for the secret token
```console
export APM_SECRET_TOKEN=<your-secret-token>
```
Create Kubernetes secret
```console
kubectl create secret generic elastic-secret --from-literal=elastic_apm_endpoint=$APM_URL_WITHOUT_PREFIX --from-literal=elastic_apm_secret_token=$APM_SECRET_TOKEN
```
Add the OpenTelemetry chart repository
```console
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry -helm-charts
```
Deploy the OpenTelemetry Demo
```console
helm install -f values.yaml cookbook-otel-demo open-telemetry/opentelemetry-demo
```
Verify the deployment
```console
kubectl get pods
```
Fetch the External IP of frondendproxy service
```console
kubectl -n default get svc cookbook-otel-demo-frontendproxy 
```

## Monitoring Kubernetes environments with Elastic Agent

Deploy Elastic Agent to the Kubernetes cluster
```console
kubectl apply -f elastic-agent-managed-kubernetes.yml 
```
Check Elastic Agent status
```console
kubectl get pods -n kube-system 
```
Add the kube-state-metrics helm repo and update the repo
```console
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
```
```console
helm repo update
```
Install and verify kube-state-metrics
```console
helm install --set namespaceOverride=kube-system kube-state-metrics prometheus-community/kube-state-metrics 
```
```console
kubectl get pods -n kube-system
```