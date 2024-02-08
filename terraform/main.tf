# TODO: fix unauthorized errors (test w/raw api)
# λ tfa tfplan
# render_service.db: Creating...
# render_service.web: Creating...
# ╷
# │ Error: failed to create service
# │
# │   with render_service.web,
# │   on main.tf line 1, in resource "render_service" "web":
# │    1: resource "render_service" "web" {
# │
# │ Unauthorized
# │
# │ Error: failed to create service
# │
# │   with render_service.db,
# │   on main.tf line 28, in resource "render_service" "db":
# │   28: resource "render_service" "db" {
# │
# │ Unauthorized

resource "render_service" "web" {
  name        = "qaas-web"
  type        = "web_service"
  repo        = "https://github.com/pythoninthegrass/qaas.git"
  branch      = "main"
  auto_deploy = true
  owner       = local.owner

  web_service_details = {
    env                           = "docker"
    plan                          = "starter"
    region                        = "ohio"
    pull_request_previews_enabled = true
    health_check_path             = "/healthz"
  }
}

resource "render_service_environment" "web" {
  service = render_service.web.id
  variables = [{
    key   = "PORT"
    value = "8000"
    key   = "POSTGRES_URI"
    value = render_service.db.private_service_details.url
  }]
}

resource "render_service" "db" {
  name   = "qaas-postgres"
  type   = "private_service"
  repo   = "hhttps://github.com/pythoninthegrass/render-postgres"
  branch = "main"
  owner  = local.owner

  private_service_details = {
    env  = "docker"
    plan = "free"
    disk = {
      name       = "quotes"
      mount_path = "/data/db"
      size_gb    = 5
    }
  }
}

