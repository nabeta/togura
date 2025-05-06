#!/usr/bin/env python3
import glob
import yaml
import config
import jpcoar
import html
import ro_crate
import jalc
import resourcesync
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def main():
  data_dir = "./work"
  output_dir = "./public"
  base_url = config.base_url()

  for path in glob.glob(f"{data_dir}/*"):
    with open(f"{path}/jpcoar20.yaml", encoding = "utf-8") as file:
      entry = yaml.load(file, Loader = yaml.Loader)
      root = jpcoar.generate(entry, base_url)
      jpcoar.add_directory_file(path, entry, root, base_url)
      ro_crate.generate(path, output_dir, root)
      jalc.generate(path, output_dir, base_url)
  html.generate(data_dir, output_dir, base_url)
  resourcesync.generate(output_dir, base_url)

if __name__ == "__main__":
  main()
