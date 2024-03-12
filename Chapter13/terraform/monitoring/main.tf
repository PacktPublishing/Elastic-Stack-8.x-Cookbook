//  Every root module needs a terraform block
terraform {
  required_version = ">=1.0.0"

  required_providers {

    ec = {
      source  = "elastic/ec"
      version = "0.9.0"
    }
    elasticstack = {
      source  = "elastic/elasticstack"
      version = "~>0.11"
    }
  }
}

// ESS API Key for the provider
provider "ec" {
  apikey = var.api_key
}

// Retrieve the latest stack pack version from the Terraform Registry
data "ec_stack" "latest" {
  version_regex = "latest"
  region        = "gcp-europe-west1"
}


// Resources require a type (ec_deployment) and an arbitrary name (workshop).
resource "ec_deployment" "monitoring" {

  name                   = "monitoring"
  version                = data.ec_stack.latest.version
  region                 = "gcp-europe-west1"
  deployment_template_id = "gcp-storage-optimized"

  elasticsearch = {

    hot = {
      size        = "4g"
      autoscaling = {}
    }
    frozen = {
      autoscaling = {}
    }
    ml = {
      autoscaling = {}
    }
  }

  kibana = {}

  integrations_server = {}
}

output "deployment_id" {
  value = ec_deployment.monitoring.id
}

output "deployment_version" {
  value = ec_deployment.monitoring.version
}


// Outputs marked sensitive do not display the value in console output, and must be explicitly requested with
// terraform output <output_name>
output "elastic_password" {
  value     = ec_deployment.monitoring.elasticsearch_password
  sensitive = true
}

// Variables are defined here. They can be passed in from the command line, or from a file
variable "api_key" {
  description = "The API key to connect to Elastic Cloud with"
  type        = string
  sensitive   = true
}


// settings for monitoring logs
#provider "elasticstack" {
#  # Use our Elastic Cloud deployment outputs for connection details.
#  # This also allows the provider to create the proper relationships between the two resources.
#  elasticsearch {
#    endpoints = [ec_deployment.monitoring.elasticsearch.https_endpoint]
#    username  = ec_deployment.monitoring.elasticsearch_username
#    password  = ec_deployment.monitoring.elasticsearch_password
#  }
#  alias = "monitoring"
#}
#
#resource "elasticstack_elasticsearch_index_lifecycle" "elastic-cloud-logs" {
#  provider = "elasticstack.monitoring"
#  name = "elastic-cloud-logs"
#
#  hot {
#      rollover {
#        max_size = "50gb"
#        max_age  = "7d"
#      }
#  }
#  delete {
#    min_age = "8d"
#      delete {}
#    }
#}