from pathlib import Path
from ruamel.yaml import YAML
import xml.etree.ElementTree as ET
import togura.jalc as jalc


def test_add_creator():
    yaml = YAML()
    path = f"{Path(__file__).parent}/../src/togura/samples/01_departmental_bulletin_paper_oa/jpcoar20.yaml"
    root = ET.Element("root")
    with open(path, "r", encoding="utf-8") as file:
        entry = yaml.load(file)
        body = ET.SubElement(root, "body")
        content = ET.SubElement(body, "content", {"sequence": "0"})
        assert jalc.add_creator(entry, root, content) is not None


def test_add_contributor():
    yaml = YAML()
    path = f"{Path(__file__).parent}/../src/togura/samples/05_doctoral_thesis_oa/jpcoar20.yaml"
    root = ET.Element("root")
    with open(path, "r", encoding="utf-8") as file:
        entry = yaml.load(file)
        body = ET.SubElement(root, "body")
        head = ET.SubElement(root, "head")
        content = ET.SubElement(body, "content", {"sequence": "0"})
        content_classification = ET.SubElement(head, "content_classification")
        content_classification.text = "03"
        assert (
            jalc.add_contributor(entry, root, content, content_classification)
            is not None
        )


def test_add_date():
    yaml = YAML()
    path = f"{Path(__file__).parent}/../src/togura/samples/05_doctoral_thesis_oa/jpcoar20.yaml"
    root = ET.Element("root")
    with open(path, "r", encoding="utf-8") as file:
        entry = yaml.load(file)
        body = ET.SubElement(root, "body")
        head = ET.SubElement(root, "head")
        content = ET.SubElement(body, "content", {"sequence": "0"})
        content_classification = ET.SubElement(head, "content_classification")
        content_classification.text = "03"
        classification = "article"
        assert (
            jalc.add_date(entry, root, content, content_classification, classification)
            is not None
        )


def test_add_funding_reference():
    yaml = YAML()
    path = f"{Path(__file__).parent}/../src/togura/samples/01_departmental_bulletin_paper_oa/jpcoar20.yaml"
    root = ET.Element("root")
    with open(path, "r", encoding="utf-8") as file:
        entry = yaml.load(file)
        body = ET.SubElement(root, "body")
        content = ET.SubElement(body, "content", {"sequence": "0"})
        assert jalc.add_funding_reference(entry, root, content) is not None
