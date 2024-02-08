terraform {
  required_providers {
    render = {
      source  = "jackall3n/render"
      version = "1.3.0"
    }
  }
}

provider "render" {
  # email   = local.email
  api_key = base64encode(local.api_token)
}
