import os
import yaml
from pathlib import Path

class Config(object):
  def __init__(self):
    file = f"{Path.cwd()}/config.yaml"
    if os.path.isfile(file):
      with open(file, encoding = "utf-8") as f:
        self.entry = yaml.safe_load(f)

  @property
  def base_url(self):
    return self.entry["base_url"]

  @property
  def site_name(self):
    return self.entry["site_name"]

  @property
  def organization(self):
    return self.entry["organization"]

  @property
  def jalc_site_id(self):
    return self.entry["jalc_site_id"]
