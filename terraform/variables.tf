# SOURCE: https://stackoverflow.com/a/76194380/15454191
locals {
  dot_env_file_path = "../.render.env"
  dot_env_regex     = "(?m:^\\s*([^#\\s]\\S*)\\s*=\\s*[\"']?(.*[^\"'\\s])[\"']?\\s*$)"
  dot_env           = { for tuple in regexall(local.dot_env_regex, file(local.dot_env_file_path)) : tuple[0] => sensitive(tuple[1]) }
  api_token         = local.dot_env["RENDER_API_KEY"]
  email             = local.dot_env["RENDER_EMAIL"]
  owner             = local.dot_env["OWNER"]
}
