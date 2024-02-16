//  Every root module needs a terraform block
terraform {

  // Anything after version 1.0.0 maintains backward compatibility
  required_version = ">=1.0.0" 

  // Here we specify which providers Terraform should use, in this case the Elastic Cloud Provider, ec
  required_providers { 

/*
  Unqualified names will pull from the Github backed Terraform Registry; 
  https://registry.terraform.io/providers/elastic/ec 
  https://github.com/elastic/terraform-provider-ec
*/
    ec = {
      source  = "elastic/ec" 
      version = "0.9.0" // Pinning to a specific version ensures compatibility and avoids nasty surprises
    }
  }
}

// Here we pass parameters to the provider. In this case we're injecting a variable, api_key into the apikey parameter
provider "ec" { 
  apikey = var.api_key
}

// Retrieve the latest stack pack version from the Terraform Registry
data "ec_stack" "latest" {
  version_regex = "latest"
  region = "gcp-europe-west1"
}


 // Resources require a type (ec_deployment) and an arbitrary name (workshop).
resource "ec_deployment" "main-deployment" {

  name                   = "main-deployment"
  version                = data.ec_stack.latest.version
  region                 = "gcp-europe-west1"
  deployment_template_id = "gcp-storage-optimized"

  elasticsearch = {

    autoscale = "true"
    hot = {
        size = "4g"
        autoscaling = {
          max_size = "8g",
          max_size_resource = "memory"
        }
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
  value = ec_deployment.main-deployment.id
}

output "deployment_version" {
  value = ec_deployment.main-deployment.version
}


// Outputs marked sensitive do not display the value in console output, and must be explicitly requested with
// terraform output <output_name>
output "elastic_password" {
  value = ec_deployment.main-deployment.elasticsearch_password
  sensitive = true
}

// Variables are defined here. They can be passed in from the command line, or from a file
variable api_key {
  description = "The API key to connect to Elastic Cloud with"
  type = string
  sensitive = true
}
