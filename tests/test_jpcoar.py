import glob
import os
import togura.jpcoar as jpcoar
import xml.etree.ElementTree as ET
from ruamel.yaml import YAML


def test_resource_type_uri():
    assert jpcoar.resource_type_uri("test") is None
    assert (
        jpcoar.resource_type_uri("article")
        == "http://purl.org/coar/resource_type/c_6501"
    )


def test_generate():
    yaml = YAML()
    files = sorted(
        glob.glob(f"{os.path.dirname(__file__)}/../src/togura/samples/*/jpcoar20.yaml")
    )
    for file in files:
        with open(file, encoding="utf-8") as f:
            entry = yaml.load(f)
            entry["id"] = 1
            result = jpcoar.generate(entry, "https://togura.example.jp")
            assert type(result) is ET.Element
