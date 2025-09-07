import os
import yaml

def config(file):
  print(file)
  with open(file, encoding = "utf-8") as f:
    return yaml.load(f, Loader = yaml.Loader)

def base_url():
  return config(config_file())["base_url"]

def site_name():
  return config(config_file())["site_name"]

def organization():
  return config(config_file())["organization"]

def jalc_site_id():
  return config(config_file())["jalc_site_id"]

def config_file():
  if os.path.isfile("./config.yaml"):
    return "config.yaml"
  elif os.path.isfile("./config.yml"):
    return "config.yml"
