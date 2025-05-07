import yaml

def config(config_file):
  with open(config_file, encoding = "utf-8") as file:
    return yaml.load(file, Loader = yaml.Loader)

def base_url():
  return config("config.yml")["base_url"]

def site_name():
  return config("config.yml")["site_name"]

def organization():
  return config("config.yml")["organization"]

def jalc_site_id():
  return config("config.yml")["jalc_site_id"]

