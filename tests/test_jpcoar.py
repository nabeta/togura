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


def build_creators(creators):
    """作成者のリストからjpcoar:creator要素を組み立て、再パースして返す"""
    root = ET.Element("root")
    jpcoar.add_creator({"creator": creators}, root)
    reparsed = ET.fromstring(ET.tostring(root, encoding="unicode"))
    return reparsed.findall(f"{{{jpcoar.ns['jpcoar']}}}creator")


def test_creator_type_uses_yaml_value():
    creators = build_creators([{"creator_type": "編"}])
    assert creators[0].get("creatorType") == "編"


def test_creator_type_defaults_to_author():
    creators = build_creators([{}])
    assert creators[0].get("creatorType") == "著"


def test_creator_type_is_per_creator():
    creators = build_creators(
        [{"creator_type": "編"}, {"creator_type": "訳"}, {}]
    )
    assert [c.get("creatorType") for c in creators] == ["編", "訳", "著"]


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
