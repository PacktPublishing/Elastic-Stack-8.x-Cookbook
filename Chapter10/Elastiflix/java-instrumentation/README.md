# Elastiflix Demo Application (java instrumentation)

## Overview

This demo application is a simple movie app that allows you to add movies to your favourites list. 
This example show you how to instrument the Java microservice with Elastic APM Agent.

## Setup

add your Elastic deployment details and credentials to the .env file:

`.env` file in same directory as compose files:

```
ELASTIC_APM_SERVER_URL="https://foobar.apm.us-central1.gcp.cloud.es.io"
ELASTIC_APM_SECRET_TOKEN="secret123"

ELASTICSEARCH_USERNAME="elastic"
ELASTICSEARCH_PASSWORD="changeme"
ELASTICSEARCH_URL="https://foobar.es.us-central1.gcp.cloud.es.io"
```

## start the app:

You can start the app in 3 different ways and also with different scenarios. See below for the scenarios.


```
Elastic instrumented:
```
cd Elastiflix
docker-compose -f docker-compose.yml up -d --build
```


then visit the app at `localhost:9000` 

the add favourites button is the main functionality right now. It calls the node service which then calls the python service

