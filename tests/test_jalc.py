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


# JaLCのXSDスキーマはリポジトリに含めていないため、tests/jalc に置いた場合のみ検証する
@pytest.mark.skipif(
    not JALC_SCHEMA_DIR.is_dir(),
    reason="JaLCのXSDスキーマが tests/jalc にありません",
)
@pytest.mark.parametrize("name", JALC_SAMPLES)
def test_generate_valid_against_schema(project, name):
    """出力したJaLC XMLがJaLCのXSDスキーマに適合する"""
    validate_with_schema(generate_jalc(project, load_sample(name)))


def validate_with_schema(xml_path: Path) -> None:
    """content_classification に対応するJaLCのXSDスキーマで検証する"""
    classification = ET.parse(xml_path).findtext("head/content_classification")
    schema = xmlschema.XMLSchema(str(JALC_SCHEMA_DIR / JALC_SCHEMAS[classification]))
    schema.validate(str(xml_path))


def validate_with_schema_if_available(xml_path: Path) -> None:
    """tests/jalc にXSDスキーマがある場合のみ検証する"""
    if JALC_SCHEMA_DIR.is_dir():
        validate_with_schema(xml_path)


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


# --- 寄与者 ---


def contributors_of(xml_path: Path) -> list:
    return ET.parse(xml_path).findall("body/content/contributor_list/contributor")


def test_generate_dataset_contributors(project):
    """研究データの寄与者が contributor_list に出力される"""
    xml_path = generate_jalc(project, load_sample("07_dataset"))
    contributors = contributors_of(xml_path)

    assert [(c.get("sequence"), c.get("contributor_type")) for c in contributors] == [
        ("0", "ProjectLeader"),
        ("1", "DataCollector"),
        ("2", "ContactPerson"),
    ]
    first = contributors[0]
    # XSDスキーマの順序（names、affiliations、researcher_id）で出力される
    assert [e.tag for e in first] == [
        "names",
        "names",
        "names",
        "affiliations",
        "researcher_id",
    ]
    assert [
        (e.get("lang"), e.findtext("first_name")) for e in first.findall("names")
    ] == [
        ("ja", "夏目, 漱石"),
        ("en", "Natsume, Soseki"),
        ("ja", "ナツメ, ソウセキ"),
    ]
    affiliation = first.find("affiliations/affiliation")
    assert affiliation.get("sequence") == "0"
    assert [
        (e.get("lang"), e.text) for e in affiliation.findall("affiliation_name")
    ] == [("ja", "東京大学"), ("en", "The University of Tokyo")]
    assert affiliation.find("affiliation_identifier").get("type") == "ISNI"
    id_code = first.find("researcher_id/id_code")
    assert (id_code.get("type"), id_code.text) == (
        "ORCID",
        "https://orcid.org/0000-0001-0002-0003",
    )
    validate_with_schema_if_available(xml_path)


def test_generate_contributor_without_contributor_type(project):
    """寄与者の種別がなければ必須の contributor_type に Other を出力する"""
    entry = load_sample("07_dataset")
    del entry["contributor"][0]["contributor_type"]
    xml_path = generate_jalc(project, entry)
    assert [c.get("contributor_type") for c in contributors_of(xml_path)] == [
        "Other",
        "DataCollector",
        "ContactPerson",
    ]
    validate_with_schema_if_available(xml_path)


@pytest.mark.parametrize(
    ("scheme", "expected"),
    [
        ("ISNI", "ISNI"),
        ("GRID", "GRID"),
        ("ROR", "ROR"),
        ("Ringgold", "RINGGOLD"),
        ("kakenhi", "Other"),
    ],
)
def test_generate_contributor_affiliation_identifier_type(project, scheme, expected):
    """所属機関識別子のスキームをJaLCで使用できる type に変換する"""
    entry = load_sample("07_dataset")
    entry["contributor"][0]["affiliation"][0]["name_identifier"][0][
        "identifier_scheme"
    ] = scheme
    xml_path = generate_jalc(project, entry)
    identifier = contributors_of(xml_path)[0].find(
        "affiliations/affiliation/affiliation_identifier"
    )
    assert identifier.get("type") == expected
    validate_with_schema_if_available(xml_path)


def test_generate_contributor_affiliation_without_identifier(project):
    """所属機関識別子がない所属も出力できる"""
    entry = load_sample("07_dataset")
    del entry["contributor"][0]["affiliation"][0]["name_identifier"]
    xml_path = generate_jalc(project, entry)
    affiliation = contributors_of(xml_path)[0].find("affiliations/affiliation")
    assert affiliation.findtext("affiliation_name") == "東京大学"
    assert affiliation.find("affiliation_identifier") is None
    validate_with_schema_if_available(xml_path)


def test_generate_thesis_without_contributors(project):
    """JaLCのXSDスキーマで寄与者を記述できない種別（学位論文）には出力しない"""
    entry = load_sample("05_doctoral_thesis_oa")
    assert entry["contributor"]
    xml_path = generate_jalc(project, entry)
    assert ET.parse(xml_path).find("body/content/contributor_list") is None
    validate_with_schema_if_available(xml_path)


# --- 助成情報 ---


def funds_of(xml_path: Path) -> list:
    return ET.parse(xml_path).findall("body/content/fund_list/fund")


def test_generate_article_fund(project):
    """論文の助成情報が fund_list に出力される"""
    xml_path = generate_jalc(project, load_sample("01_departmental_bulletin_paper_oa"))
    funds = funds_of(xml_path)
    assert len(funds) == 1
    fund = funds[0]
    assert [e.tag for e in fund] == [
        "funder_name",
        "funder_identifier",
        "award_number_group",
    ]
    assert fund.find("funder_name").attrib == {"lang": "ja"}
    assert fund.findtext("funder_name") == "日本学術振興会"
    assert fund.find("funder_identifier").attrib == {"type": "Other"}
    assert fund.findtext("funder_identifier") == "1025"
    # 論文ではプログラム情報と研究課題名は出力しない
    assert [e.tag for e in fund.find("award_number_group")] == ["award_number"]
    award_number = fund.find("award_number_group/award_number")
    assert (award_number.get("type"), award_number.text) == ("JGN", "JP18049069")
    validate_with_schema_if_available(xml_path)


def test_generate_dataset_fund(project):
    """研究データではプログラム情報と研究課題名も出力される"""
    entry = load_sample("07_dataset")
    entry["funding_reference"][0]["funding_stream_identifier"] = {
        "funding_stream_identifier": "JP-PROGRAM-1",
        "funding_stream_identifier_type": "JGN_fundingStream",
    }
    xml_path = generate_jalc(project, entry)
    group = funds_of(xml_path)[0].find("award_number_group")
    # XSDスキーマの順序で出力される
    assert [(e.tag, e.text) for e in group] == [
        ("program_id", "JP-PROGRAM-1"),
        ("program_name", "科学研究費助成事業"),
        ("project_name", "情報爆発時代の情報検索基盤技術"),
        ("award_number", "JP18049069"),
    ]
    validate_with_schema_if_available(xml_path)


@pytest.mark.parametrize(
    ("identifier_type", "expected"),
    [
        ("Crossref Funder", "FundRef"),
        ("GRID", "GRID"),
        ("ISNI", "ISNI"),
        ("ROR", "ROR"),
        ("e-Rad_funder", "Other"),
        ("Other", "Other"),
        (None, "Other"),
    ],
)
def test_generate_funder_identifier_type(project, identifier_type, expected):
    """助成機関識別子のタイプをJaLCで使用できる type に変換する"""
    entry = load_sample("01_departmental_bulletin_paper_oa")
    funder_identifier = entry["funding_reference"][0]["funder_identifier"]
    if identifier_type is None:
        del funder_identifier["funder_identifier_type"]
    else:
        funder_identifier["funder_identifier_type"] = identifier_type
    xml_path = generate_jalc(project, entry)
    assert funds_of(xml_path)[0].find("funder_identifier").get("type") == expected
    validate_with_schema_if_available(xml_path)


def test_generate_fund_first_funder_name(project):
    """funder_name は1件のみ記述できるため、最初の名称を出力する"""
    entry = load_sample("01_departmental_bulletin_paper_oa")
    entry["funding_reference"][0]["funder_name"].append(
        {"funder_name": "Japan Society for the Promotion of Science", "lang": "en"}
    )
    xml_path = generate_jalc(project, entry)
    funder_names = funds_of(xml_path)[0].findall("funder_name")
    assert [e.text for e in funder_names] == ["日本学術振興会"]
    validate_with_schema_if_available(xml_path)


def test_generate_fund_without_optional_items(project):
    """助成機関識別子と研究課題番号がなくても出力できる"""
    entry = load_sample("07_dataset")
    del entry["funding_reference"][0]["funder_identifier"]
    del entry["funding_reference"][0]["award_number"]
    xml_path = generate_jalc(project, entry)
    fund = funds_of(xml_path)[0]
    # award_number_group には award_number が必須のため、出力しない
    assert [e.tag for e in fund] == ["funder_name"]
    validate_with_schema_if_available(xml_path)


def test_generate_fund_without_funder_name(project):
    """助成機関名がない助成情報は出力しない"""
    entry = load_sample("01_departmental_bulletin_paper_oa")
    del entry["funding_reference"][0]["funder_name"]
    xml_path = generate_jalc(project, entry)
    assert ET.parse(xml_path).find("body/content/fund_list") is None
    validate_with_schema_if_available(xml_path)


# --- 収録物識別子・収録物名 ---


def test_generate_journal_id_list(project):
    """論文の収録物識別子が journal_id_list に出力される"""
    entry = load_sample("01_departmental_bulletin_paper_oa")
    entry["source_identifier"] = [
        {"identifier_type": "PISSN", "identifier": "1880-697X"},
        {"identifier_type": "EISSN", "identifier": "1880-6988"},
        {"identifier_type": "ISSN", "identifier": "1880-7003"},
        {"identifier_type": "NCID", "identifier": "AA12032633"},
    ]
    xml_path = generate_jalc(project, entry)
    journal_ids = ET.parse(xml_path).findall("body/content/journal_id_list/journal_id")
    # PISSN、EISSNは issn_type で冊子体と電子版を区別する
    assert [(e.attrib, e.text) for e in journal_ids] == [
        ({"type": "ISSN", "issn_type": "print"}, "1880-697X"),
        ({"type": "ISSN", "issn_type": "online"}, "1880-6988"),
        ({"type": "ISSN"}, "1880-7003"),
        ({"type": "NCID"}, "AA12032633"),
    ]
    validate_with_schema_if_available(xml_path)


def test_generate_journal_id_unknown_type(project):
    """JaLCにない識別子タイプは出力しない"""
    entry = load_sample("01_departmental_bulletin_paper_oa")
    entry["source_identifier"].append(
        {"identifier_type": "ISSN-L", "identifier": "1880-697X"}
    )
    xml_path = generate_jalc(project, entry)
    journal_ids = ET.parse(xml_path).findall("body/content/journal_id_list/journal_id")
    assert [e.text for e in journal_ids] == ["1880-697X", "AA12032633"]
    validate_with_schema_if_available(xml_path)


def test_generate_article_without_source_title(project):
    """論文のXSDスキーマには収録物名の要素がないため、出力しない"""
    xml_path = generate_jalc(project, load_sample("01_departmental_bulletin_paper_oa"))
    root = ET.parse(xml_path).getroot()
    assert root.find(".//series_title") is None
    texts = {e.text for e in root.iter()}
    assert "東京大学大学院情報学環紀要 情報学研究" not in texts
    assert "Journal of information studies" not in texts
    validate_with_schema_if_available(xml_path)


def test_generate_thesis_series_title(project):
    """学位論文では、同じ言語の収録物名をシリーズ名として出力する"""
    entry = load_sample("05_doctoral_thesis_oa")
    entry["source_title"] = [
        {"source_title": "鳥座大学学位論文集", "lang": "ja"},
        {"source_title": "Togura University Dissertations", "lang": "en"},
    ]
    entry["source_identifier"] = [
        {"identifier_type": "PISSN", "identifier": "1880-697X"}
    ]
    xml_path = generate_jalc(project, entry)
    content = ET.parse(xml_path).find("body/content")
    titles = content.findall("title_list/titles")
    assert [(e.get("lang"), e.findtext("series_title"), e[0].tag) for e in titles] == [
        ("en", "Togura University Dissertations", "series_title"),
        ("ja", "鳥座大学学位論文集", "series_title"),
        # ja-Kana のタイトルには同じ言語の収録物名がない
        ("ja", None, "title"),
    ]
    # 図書のXSDスキーマには journal_id_list がない
    assert content.find("journal_id_list") is None
    validate_with_schema_if_available(xml_path)


def test_generate_dataset_without_source(project):
    """研究データには収録物識別子・収録物名を出力しない"""
    entry = load_sample("07_dataset")
    entry["source_title"] = [{"source_title": "データ集", "lang": "ja"}]
    entry["source_identifier"] = [
        {"identifier_type": "PISSN", "identifier": "1880-697X"}
    ]
    xml_path = generate_jalc(project, entry)
    root = ET.parse(xml_path).getroot()
    assert root.find(".//journal_id_list") is None
    assert root.find(".//series_title") is None
    validate_with_schema_if_available(xml_path)
