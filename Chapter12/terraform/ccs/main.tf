terraform {
  required_version = ">= 1.0.0"

  required_providers {
    ec = {
      source  = "elastic/ec"
      version = "0.9.0"
    }
  }
}

provider "ec" {
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

