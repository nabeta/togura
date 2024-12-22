#!/usr/bin/env python3
import os
import sys
import datetime
from resync import Resource, ResourceList, CapabilityList, SourceDescription
from urllib.parse import urljoin

def main():
  if len(sys.argv) != 2:
    print("Usage: python3 resourcesync.py <base_url>")
    sys.exit(1)

  rsd = SourceDescription()
  caps = CapabilityList()
  rl = ResourceList()
  public_dir = "public"
  base_url = sys.argv[1]

  for data_dir in os.listdir(public_dir):
    if not os.path.isdir(os.path.join(public_dir, data_dir)):
      continue

    if data_dir == ".keep":
      continue
    if data_dir == ".well-known":
      continue

    file = f"{data_dir}/jpcoar20.xml"
    rl.add(Resource(urljoin(base_url, file), lastmod = datetime.datetime.fromtimestamp(os.path.getmtime(f"public/{file}"), datetime.timezone.utc).isoformat()))

  caps.add_capability(rl, urljoin(base_url, "resourcelist.xml"))

  with open(f"public/capabilitylist.xml", "w") as file:
    file.write(caps.as_xml())

  with open(f"public/resourcelist.xml", "w") as file:
    file.write(rl.as_xml())

  rsd.add_capability_list(urljoin(base_url, "capabilitylist.xml"))
  with open(f"public/.well-known/resourcesync", "w") as file:
    file.write(rsd.as_xml())


if __name__ == "__main__":
    main()
