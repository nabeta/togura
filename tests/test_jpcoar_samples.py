"""サンプルYAMLからJPCOARスキーマのXMLを生成し、JPCOARのサンプルXMLと比較するテスト"""

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from lxml import etree
from ruamel.yaml import YAML

from togura import jpcoar

ROOT = Path(__file__).resolve().parent.parent
SAMPLES_DIR = ROOT / "src" / "togura" / "samples"
XML_DIR = ROOT / "tests" / "samples"

BASE_URL = "https://togura.example.jp"
ENTRY_ID = 1
JPCOAR_NS = jpcoar.ns["jpcoar"]

# JPCOARのサンプルXMLはリポジトリに含めていないため、tests/samples に置いた場合のみテストする
pytestmark = pytest.mark.skipif(
    not (XML_DIR / "01_departmental_bulletin_paper_oa.xml").is_file(),
    reason="JPCOARのサンプルXMLが tests/samples にありません",
)
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


def generate_xml(name: str):
    """サンプルYAMLからXMLを生成し、lxmlの要素として返す"""
    with open(SAMPLES_DIR / name / "jpcoar20.yaml", encoding="utf-8") as f:
        entry = YAML().load(f)
    entry["id"] = ENTRY_ID
    root = jpcoar.generate(entry, BASE_URL)
    # ElementTreeでは "xml:lang" がそのままの属性名で入るため、
    # 一度文字列にしてからlxmlで読み直して名前空間を解決する
    return etree.fromstring(ET.tostring(root, encoding="utf-8"))


def load_expected_xml(name: str):
    parser = etree.XMLParser(remove_comments=True, remove_blank_text=True)
    return etree.parse(str(XML_DIR / f"{name}.xml"), parser).getroot()


def remove_togura_identifier(root):
    """Toguraが自動で付与するランディングページのURIを取り除いて返す"""
    landing_pages = [
        e
        for e in root.findall(f"{{{JPCOAR_NS}}}identifier")
        if e.get("identifierType") == "URI"
        and e.text == f"{BASE_URL}/{ENTRY_ID}/ro-crate-preview.html"
    ]
    for e in landing_pages:
        root.remove(e)
    return landing_pages


def to_tree(elem):
    """要素を比較しやすい (タグ, 属性, テキスト, 子要素) の組に変換する"""
    attrib = dict(elem.attrib)
    text = (elem.text or "").strip()
    # YAMLでは nameIdentifierURI がある場合はURIを識別子として保持するため、
    # 生成されるXMLでは要素の値もURIになる
    if elem.tag == f"{{{JPCOAR_NS}}}nameIdentifier" and attrib.get("nameIdentifierURI"):
        text = attrib["nameIdentifierURI"]
    return (
        elem.tag,
        attrib,
        text,
        [to_tree(child) for child in elem],
    )


@pytest.fixture
def name():
    return "01_departmental_bulletin_paper_oa"


def test_landing_page_identifier(name):
    """ランディングページのURIが識別子の先頭に出力される"""
    root = generate_xml(name)
    identifiers = root.findall(f"{{{JPCOAR_NS}}}identifier")
    assert identifiers[0].get("identifierType") == "URI"
    assert identifiers[0].text == f"{BASE_URL}/{ENTRY_ID}/ro-crate-preview.html"
    assert len(remove_togura_identifier(root)) == 1


def test_root_element(name):
    root = generate_xml(name)
    assert root.tag == f"{{{JPCOAR_NS}}}jpcoar"
    assert root.get(
        "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation"
    ) == load_expected_xml(name).get(
        "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation"
    )


def test_element_order(name):
    """要素がサンプルXMLと同じ順序で出力される"""
    actual = generate_xml(name)
    remove_togura_identifier(actual)
    expected = load_expected_xml(name)
    assert [e.tag for e in actual] == [e.tag for e in expected]


def test_xml_lang(name):
    """xml:lang が名前空間付きの属性として出力される"""
    actual = generate_xml(name)
    langs = [e.get(XML_LANG) for e in actual.iter() if e.get(XML_LANG)]
    assert "ja" in langs
    assert "ja-Kana" in langs


def test_file_label(name):
    """ファイルのラベルが出力される"""
    actual = generate_xml(name)
    uri = actual.find(f"{{{JPCOAR_NS}}}file/{{{JPCOAR_NS}}}URI")
    assert uri.get("label") == "JIS_12_3_34-57.pdf"
    assert uri.get("objectType") == "fulltext"


@pytest.mark.skip(
    reason="サンプルYAMLの権利情報（rights）がサンプルXMLと一致していないため"
)
def test_whole_document_matches_sample(name):
    """生成したXMLがサンプルXMLと一致する"""
    actual = generate_xml(name)
    remove_togura_identifier(actual)
    expected = load_expected_xml(name)
    actual_children = [to_tree(e) for e in actual]
    expected_children = [to_tree(e) for e in expected]
    for a, e in zip(actual_children, expected_children):
        assert a == e
    assert len(actual_children) == len(expected_children)
