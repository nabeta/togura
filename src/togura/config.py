import os
from pathlib import Path
from ruamel.yaml import YAML


class Config(object):
    def __init__(self):
        file = f"{Path.cwd()}/config.yaml"
        yaml = YAML()
        if os.path.isfile(file):
            with open(file, encoding="utf-8") as f:
                self.entry = yaml.load(f)

    @property
    def organization(self):
        return self.entry["organization"]

    @property
    def site_name(self):
        return self.entry["site_name"]

    @property
    def base_url(self):
        return self.entry["base_url"]

    @property
    def email(self):
        return self.entry["email"]

    @property
    def jalc_site_id(self):
        return self.entry["jalc_site_id"]
