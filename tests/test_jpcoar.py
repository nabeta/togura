import glob
import os
import pytest
import togura.jpcoar as jpcoar
import xml.etree.ElementTree as ET
from ruamel.yaml import YAML


def test_access_rights_uri():
    assert jpcoar.access_rights_uri("test") is None
    assert (
        jpcoar.access_rights_uri("embargoed access")
        == "http://purl.org/coar/access_right/c_f1cf"
    )


def test_resource_type_uri():
    assert jpcoar.resource_type_uri("test") is None
    assert (
        jpcoar.resource_type_uri("article")
        == "http://purl.org/coar/resource_type/c_6501"
    )


def test_text_version_uri():
    assert jpcoar.text_version_uri("test") is None
    assert (
        jpcoar.text_version_uri("AO")
        == "http://purl.org/coar/version/c_b1a7d7d4d402bcce"
    )


def test_jpcoar_identifier_type():
    assert jpcoar.jpcoar_identifier_type("https://doi.org/12345") == "DOI"
    assert jpcoar.jpcoar_identifier_type("http://dx.doi.org/12345") == "DOI"
    assert jpcoar.jpcoar_identifier_type("http://hdl.handle.net/12345") == "HDL"
    assert jpcoar.jpcoar_identifier_type("https://example.com/12345") == "URI"
    with pytest.raises(AttributeError):
        jpcoar.jpcoar_identifier_type("example.com/12345")


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
