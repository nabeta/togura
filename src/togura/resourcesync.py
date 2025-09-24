import os
import datetime
from pathlib import Path
from resync import Resource, ResourceList, CapabilityList, SourceDescription
from urllib.parse import urljoin


def generate(output_dir, base_url):
    rsd = SourceDescription()
    caps = CapabilityList()
    rl = ResourceList()

    for data_dir in os.listdir(output_dir):
        if not os.path.isdir(os.path.join(output_dir, data_dir)):
            continue

        if data_dir == ".keep":
            continue
        if data_dir == ".well-known":
            continue
        if data_dir == "images":
            continue

        file = f"{data_dir}/jpcoar20.xml"
        rl.add(
            Resource(
                urljoin(base_url, file),
                lastmod=datetime.datetime.fromtimestamp(
                    os.path.getmtime(f"public/{file}"), datetime.timezone.utc
                ).isoformat(),
            )
        )

    caps.add_capability(rl, urljoin(base_url, "resourcelist.xml"))

    with open(f"{Path.cwd()}/public/capabilitylist.xml", "w", encoding="utf-8") as file:
        file.write(caps.as_xml())

    with open(f"{Path.cwd()}/public/resourcelist.xml", "w", encoding="utf-8") as file:
        file.write(rl.as_xml())

    rsd.add_capability_list(urljoin(base_url, "capabilitylist.xml"))

    os.makedirs(f"{Path.cwd()}/public/.well-known", exist_ok=True)
    with open(
        f"{Path.cwd()}/public/.well-known/resourcesync", "w", encoding="utf-8"
    ) as file:
        file.write(rsd.as_xml())
