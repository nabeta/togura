import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import xmlschema
from ruamel.yaml import YAML

from togura import jalc


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


# --- jpcoar20.yaml から jalc.xml への変換 ---

ROOT = Path(__file__).resolve().parent.parent
SAMPLES_DIR = ROOT / "src" / "togura" / "samples"
JALC_SCHEMA_DIR = ROOT / "tests" / "jalc"
BASE_URL = "https://togura.example.jp"
ENTRY_ID = "1"

# content_classification に対応するJaLCのXSDスキーマ
JALC_SCHEMAS = {
    "01": "article.xsd",
    "02": "book.xsd",
    "03": "research_data.xsd",
    "04": "e-learning.xsd",
}


# JaLC XMLが出力されるサンプル（ID登録があり、資源タイプがJaLCのコンテンツ種別に対応するもの）
# 12_digital_archive はID登録があるが、資源タイプ book に対応する種別がないため出力されない
JALC_SAMPLES = [
    "01_departmental_bulletin_paper_oa",
    "05_doctoral_thesis_oa",
    "06_doctoral_thesis_published",
    "07_dataset",
]


@pytest.fixture
def project(tmp_path, monkeypatch):
    """設定ファイルを置いたフォルダに移動する"""
    monkeypatch.chdir(tmp_path)
    with open(tmp_path / "config.yaml", "w", encoding="utf-8") as file:
        YAML().dump(
            {
                "organization": "鳥座大学",
                "site_name": "鳥座大学機関リポジトリ",
                "base_url": BASE_URL,
                "email": "",
                "jalc_site_id": "SI/togura.dummy",
                "logo_filename": "logo.png",
            },
            file,
        )
    return tmp_path


def generate_jalc(project: Path, entry: dict) -> Path:
    """資料のフォルダを作成してJaLC XMLを出力し、出力先のパスを返す"""
    data_dir = project / "work" / f"{ENTRY_ID}_sample"
    data_dir.mkdir(parents=True)
    with open(data_dir / "jpcoar20.yaml", "w", encoding="utf-8") as file:
        YAML().dump(entry, file)
    output_dir = project / "public"
    (output_dir / ENTRY_ID).mkdir(parents=True)
    jalc.generate(str(data_dir), str(output_dir), BASE_URL)
    return output_dir / ENTRY_ID / "jalc.xml"


def load_sample(name: str) -> dict:
    with open(SAMPLES_DIR / name / "jpcoar20.yaml", encoding="utf-8") as file:
        return YAML().load(file)


@pytest.mark.parametrize("name", JALC_SAMPLES)
def test_generate_valid_against_schema(project, name):
    """出力したJaLC XMLがJaLCのXSDスキーマに適合する"""
    xml_path = generate_jalc(project, load_sample(name))
    classification = ET.parse(xml_path).findtext("head/content_classification")
    schema = xmlschema.XMLSchema(str(JALC_SCHEMA_DIR / JALC_SCHEMAS[classification]))
    schema.validate(str(xml_path))


def test_generate_departmental_bulletin_paper(project):
    """紀要論文のサンプルの各項目が正しく変換される"""
    xml_path = generate_jalc(project, load_sample("01_departmental_bulletin_paper_oa"))
    root = ET.parse(xml_path).getroot()

    assert [e.text for e in root.find("head")] == ["0", "0", "01", "01"]
    assert root.findtext("body/site_id") == "SI/togura.dummy"

    content = root.find("body/content")
    assert content.attrib == {"sequence": "0", "classification": "article"}
    assert content.findtext("doi") == "10.15017/64495"
    assert content.findtext("url") == f"{BASE_URL}/{ENTRY_ID}/ro-crate-preview.html"
    # PISSNはISSNとして出力される
    assert [
        (e.get("type"), e.text) for e in content.findall("journal_id_list/journal_id")
    ] == [("ISSN", "1880-697X"), ("NCID", "AA12032633")]
    # 言語は2文字のコードになる（ja-Kana、ja-Latn は ja）
    assert [
        (e.get("lang"), e.findtext("title"))
        for e in content.findall("title_list/titles")
    ] == [
        ("ja", "情報爆発時代の研究基盤構想"),
        (
            "en",
            "Research Project on Cyber Infrastructure for Information-explosion Era",
        ),
        ("ja", "ジョウホウ バクハツ ジダイ ノ ケンキュウ キバン コウソウ"),
        ("ja", "Joho bakuhatsu jidai no kenkyu kiban koso"),
    ]

    creators = content.findall("creator_list/creator")
    assert len(creators) == 1
    assert creators[0].get("sequence") == "0"
    assert [
        (e.get("lang"), e.findtext("first_name")) for e in creators[0].findall("names")
    ] == [("ja", "安達, 淳"), ("en", "Adachi, Jun"), ("ja", "アダチ, ジュン")]
    affiliation = creators[0].find("affiliations/affiliation")
    assert [
        (e.get("lang"), e.text) for e in affiliation.findall("affiliation_name")
    ] == [("ja", "東京大学"), ("en", "The University of Tokyo")]
    assert affiliation.find("affiliation_identifier").attrib == {"type": "ISNI"}
    assert (
        affiliation.findtext("affiliation_identifier")
        == "http://www.isni.org/isni/0000000121691048"
    )
    id_code = creators[0].find("researcher_id/id_code")
    assert id_code.get("type") == "ORCID"
    assert id_code.text == "https://orcid.org/0000-0001-0002-0003"

    assert [e.text for e in content.find("publication_date")] == ["2015", "10", "01"]
    assert content.findtext("date") == "20151001"
    assert content.findtext("volume") == "12"
    assert content.findtext("issue") == "3"
    assert content.findtext("first_page") == "34"
    assert content.findtext("last_page") == "57"

    fund = content.find("fund_list/fund")
    assert fund.findtext("funder_name") == "日本学術振興会"
    # e-Rad_funder は Other として出力される
    assert fund.find("funder_identifier").attrib == {"type": "Other"}
    assert fund.findtext("funder_identifier") == "1025"
    assert fund.findtext("award_number_group/award_number") == "JP18049069"

    # 紀要論文には出版者を出力しない
    assert content.find("publisher") is None


def test_generate_without_identifier_registration(project):
    """ID登録が記述されていなければ出力しない"""
    entry = load_sample("01_departmental_bulletin_paper_oa")
    del entry["identifier_registration"]
    assert not generate_jalc(project, entry).exists()


def test_generate_unsupported_type(project):
    """JaLCのコンテンツ種別に対応しない資源タイプは出力しない"""
    entry = load_sample("12_digital_archive")
    assert entry["identifier_registration"]
    assert entry["type"] == "book"
    assert not generate_jalc(project, entry).exists()
