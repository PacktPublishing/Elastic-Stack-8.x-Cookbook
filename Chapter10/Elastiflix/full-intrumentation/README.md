# Elastiflix Demo Application (full instrumentation)

## Overview

This demo application is a simple movie app that allows you to add movies to your favourites list. 


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
``` console
docker-compose -f docker-compose.yml up -d 
```
then visit the app at `localhost:9000`