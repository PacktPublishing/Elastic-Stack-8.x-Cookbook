terraform {
  required_version = ">= 1.0.0"

  required_providers {
    ec = {
      source  = "elastic/ec"
      version = "0.9.0"
    }
  }
}

// Here we pass parameters to the provider. In this case we're injecting a variable, api_key into the apikey parameter
provider "ec" {
  apikey = var.api_key
}

// Variables are defined here. They can be passed in from the command line, or from a file
variable api_key {
  description = "The API key to connect to Elastic Cloud with"
  type = string
  sensitive = true
}

data "ec_stack" "latest" {
  version_regex = "latest"
  region        = "gcp-europe-west1"
}

resource "ec_deployment" "custom-ccs-id" {
  name                   = "new-team-deployment"

  region                 = "gcp-europe-west1"
  version                = data.ec_stack.latest.version
  deployment_template_id = "gcp-storage-optimized"

  elasticsearch = {
    hot = {
      size = "2g"
      autoscaling = {
        max_size = "8g"
      }
    }
  }

  kibana = {}
  integrations_server = {}
}

