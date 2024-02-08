output "web_url" {
  value = render_service.web.web_service_details.url
}

output "db_url" {
  value = render_service.db.private_service_details.url
}
