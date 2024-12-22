#!/usr/bin/env python3
import os
import sys
import datetime
from resync import Resource, ResourceList
from urllib.parse import urljoin

def main():
  if len(sys.argv) != 2:
    print("Usage: python3 resourcesync.py <base_url>")
    sys.exit(1)

  rl = ResourceList()
  public_dir = "public"
  base_url = sys.argv[1]

  for data_dir in os.listdir(public_dir):
    if not os.path.isdir(os.path.join(public_dir, data_dir)):
      continue

    if data_dir == ".keep":
      continue

    file = f"{data_dir}/jpcoar20.xml"
    rl.add(Resource(urljoin(base_url, file), lastmod = datetime.datetime.fromtimestamp(os.path.getmtime(f"public/{file}"), datetime.timezone.utc).isoformat()))

  with open(f"public/resourcelist.xml", "w") as file:
    file.write(rl.as_xml())

if __name__ == "__main__":
    main()
