import datetime
import os
import xml.etree.ElementTree as ET
from logging import DEBUG, getLogger
from urllib.parse import urljoin

from ruamel.yaml import YAML

from togura.config import Config

logger = getLogger(__name__)
logger.setLevel(DEBUG)

# JaLCのXSDスキーマでの文字数の上限
ABSTRACT_MAX_LENGTH = 4000
DESCRIPTION_MAX_LENGTH = 5000


class JalcError(ValueError):
    """メタデータがJaLCのXSDスキーマに適合しない場合のエラー"""


def check_length(text, max_length, label, lang=None):
    """文字数がJaLCのXSDスキーマの上限を超えていればエラーにする"""
    if len(text) > max_length:
        target = f"{label}（{lang}）" if lang else label
        raise JalcError(
            f"{target}が{len(text)}文字あります。JaLCでは{max_length}文字以内で記述してください。"
        )


def generate(data_dir, output_dir, base_url):
    entry_id = os.path.basename(data_dir).split("_")[0]
    yaml = YAML()

    # メタデータYAMLファイルを開く
    with open(f"{data_dir}/jpcoar20.yaml", encoding="utf-8") as file:
        entry = yaml.load(file)

    # ID登録が記述されていなければ処理を終了する
    if entry.get("identifier_registration") is None:
        return

    # 設定ファイルは実行時のフォルダから読み込む
    conf = Config()

    root = ET.Element("root")
    head = ET.SubElement(root, "head")

    error_process = ET.SubElement(head, "error_process")
    error_process.text = "0"

    result_method = ET.SubElement(head, "result_method")
    result_method.text = "0"

    content_classification = ET.SubElement(head, "content_classification")
    classification = book_classification = None
    match entry["type"]:
        case "conference paper":
            content_classification.text = "01"
            classification = "article"
        case "departmental bulletin paper":
            content_classification.text = "01"
            classification = "article"
        case "journal article":
            content_classification.text = "01"
            classification = "article"
        case "periodical":
            content_classification.text = "01"
            classification = "article"
        case "review article":
            content_classification.text = "01"
            classification = "article"
        case "data paper":
            content_classification.text = "01"
            classification = "article"
        case "editorial":
            content_classification.text = "01"
            classification = "article"
        case "article":
            content_classification.text = "01"
            classification = "article"
        case "other":
            content_classification.text = "01"
            classification = "article"
        case "newspaper":
            content_classification.text = "01"
            classification = "article"
        case "software paper":
            content_classification.text = "01"
            classification = "article"
        case "thesis":
            content_classification.text = "02"
            book_classification = "03"
        case "bachelor thesis":
            content_classification.text = "02"
            book_classification = "03"
        case "master thesis":
            content_classification.text = "02"
            book_classification = "03"
        case "doctoral thesis":
            content_classification.text = "02"
            book_classification = "03"
        case "learning material":
            content_classification.text = "04"
        case "learning object":
            content_classification.text = "04"
        case "dataset":
            content_classification.text = "03"
        case "software":
            content_classification.text = "03"
        case _:
            return

    request_kind = ET.SubElement(head, "request_kind")
    request_kind.text = "01"

    body = ET.SubElement(root, "body")
    site_id = ET.SubElement(body, "site_id")
    site_id.text = conf.jalc_site_id

    content = ET.SubElement(body, "content", {"sequence": "0"})
    if classification:
        content.set("classification", classification)

    doi = ET.SubElement(content, "doi")
    doi.text = entry["identifier_registration"]["identifier"]

    url = ET.SubElement(content, "url")
    url.text = urljoin(base_url, f"{entry_id}/ro-crate-preview.html")

    if book_classification:
        book_c = ET.SubElement(content, "book_classification")
        book_c.text = book_classification

    if classification == "article":
        add_journal_id_list(entry, content)

    add_title_list(entry, content, content_classification)

    add_creator(entry, root, content)
    add_contributor(entry, root, content, content_classification)
    add_date(entry, root, content, content_classification, classification)

    if entry.get("relation"):
        relation_list = ET.SubElement(content, "relation_list")
        for relation in entry["relation"]:
            related_content = ET.SubElement(relation_list, "related_content")
            if relation["related_identifier"].get("identifier_type"):
                related_content.set(
                    "type", relation["related_identifier"]["identifier_type"]
                )
                related_content.set("relation", relation["relation_type"])
            related_content.text = relation["related_identifier"]["identifier"]

    if content_classification.text in ["02", "03"]:
        publisher = ET.SubElement(content, "publisher")
        publisher_name = ET.SubElement(publisher, "publisher_name")
        if entry.get("publisher"):
            publisher_name.text = entry["publisher"][0]["publisher"]
        else:
            publisher_name.text = conf.organization

    if entry.get("volume"):
        volume = ET.SubElement(content, "volume")
        volume.text = entry["volume"]

    if entry.get("issue"):
        issue = ET.SubElement(content, "issue")
        issue.text = entry["issue"]

    if entry.get("page_start"):
        first_page = ET.SubElement(content, "first_page")
        first_page.text = entry["page_start"]

    if entry.get("page_end"):
        last_page = ET.SubElement(content, "last_page")
        last_page.text = entry["page_end"]

    add_funding_reference(entry, root, content, content_classification)
    add_keyword_list(entry, content, content_classification)
    add_subject_list(entry, content, content_classification)
    add_abstract_list(entry, content, content_classification)
    add_description_list(entry, content, content_classification)

    # JaLC XMLを出力する
    with open(f"{output_dir}/{entry_id!s}/jalc.xml", "w", encoding="utf-8") as file:
        ET.indent(root, space="\t", level=0)
        file.write(ET.tostring(root, encoding="unicode", xml_declaration=True))


# JaLCの journal_id の type に使用できる値
JALC_JOURNAL_ID_TYPES = {
    "DOI",
    "ISSN",
    "ISBN",
    "CODEN",
    "JID",
    "JSTNO",
    "NCID",
    "MATID",
}

# JPCOARのISSNの識別子タイプとJaLCの issn_type の対応
JALC_ISSN_TYPES = {"PISSN": "print", "EISSN": "online"}


def add_journal_id_list(entry, content):
    """収録物識別子を journal_id_list として追加する（論文のみ）"""
    journal_id_list = ET.SubElement(content, "journal_id_list")
    for source_identifier in entry.get("source_identifier") or []:
        identifier_type = source_identifier.get("identifier_type")
        if identifier_type in ("PISSN", "EISSN", "ISSN"):
            attrib = {"type": "ISSN"}
            # 冊子体（PISSN）と電子版（EISSN）を issn_type で区別する
            if identifier_type in JALC_ISSN_TYPES:
                attrib["issn_type"] = JALC_ISSN_TYPES[identifier_type]
        elif identifier_type in JALC_JOURNAL_ID_TYPES:
            attrib = {"type": identifier_type}
        else:
            # JaLCにない識別子タイプは出力しない
            continue
        journal_id = ET.SubElement(journal_id_list, "journal_id", attrib)
        journal_id.text = str(source_identifier["identifier"])


def add_title_list(entry, content, content_classification):
    """タイトルを title_list として追加する

    図書・学位論文（content_classification が 02）では、
    同じ言語の収録物名をシリーズ名（series_title）として出力する
    """
    series_titles = {}
    if content_classification.text == "02":
        for source_title in entry.get("source_title") or []:
            if source_title.get("source_title"):
                series_titles.setdefault(
                    source_title.get("lang"), source_title["source_title"]
                )

    title_list = ET.SubElement(content, "title_list")
    for t in entry["title"]:
        titles = ET.SubElement(title_list, "titles")
        if t.get("lang"):
            titles.set("lang", iso_639_1(t["lang"]))
        if t.get("lang") in series_titles:
            series_title = ET.SubElement(titles, "series_title")
            series_title.text = series_titles[t["lang"]]
        title = ET.SubElement(titles, "title")
        title.text = t["title"]


# JaLCの affiliation_identifier の type に使用できる値
JALC_AFFILIATION_IDENTIFIER_TYPES = {
    "FundRef",
    "GRID",
    "ISNI",
    "ROR",
    "NID",
    "WIKIDATA",
    "RINGGOLD",
}


def affiliation_identifier_type(scheme):
    """JPCOARの所属機関識別子のスキームをJaLCの type に変換する"""
    scheme = (scheme or "").upper()
    if scheme in JALC_AFFILIATION_IDENTIFIER_TYPES:
        return scheme
    # kakenhi などJaLCにないスキームは Other とする
    return "Other"


def add_person(parent, tag, sequence, person, name_key):
    """作成者・寄与者の要素を追加する

    JaLCのXSDスキーマでは names、affiliations、researcher_id の順に出力する
    """
    elem_person = ET.SubElement(parent, tag, {"sequence": str(sequence)})
    for name in person.get(name_key) or []:
        names = ET.SubElement(elem_person, "names")
        if name.get("lang"):
            names.set("lang", iso_639_1(name["lang"]))
        first_name = ET.SubElement(names, "first_name")
        first_name.text = name["name"]

    if person.get("affiliation"):
        affiliations = ET.SubElement(elem_person, "affiliations")
        for i, affiliation in enumerate(person["affiliation"]):
            elem_affiliation = ET.SubElement(
                affiliations, "affiliation", {"sequence": str(i)}
            )
            for affiliation_name in affiliation.get("affiliation_name") or []:
                elem_affiliation_name = ET.SubElement(
                    elem_affiliation, "affiliation_name"
                )
                elem_affiliation_name.text = affiliation_name["name"]
                if affiliation_name.get("lang"):
                    elem_affiliation_name.set(
                        "lang", iso_639_1(affiliation_name["lang"])
                    )
            for affiliation_identifier in affiliation.get("name_identifier") or []:
                elem_affiliation_identifier = ET.SubElement(
                    elem_affiliation,
                    "affiliation_identifier",
                    {
                        "type": affiliation_identifier_type(
                            affiliation_identifier.get("identifier_scheme")
                        )
                    },
                )
                elem_affiliation_identifier.text = affiliation_identifier["identifier"]

    if person.get("name_identifier"):
        researcher_id = ET.SubElement(elem_person, "researcher_id")
        for identifier in person["name_identifier"]:
            id_code = ET.SubElement(
                researcher_id,
                "id_code",
                {"type": identifier.get("identifier_scheme", "")},
            )
            id_code.text = identifier["identifier"]

    return elem_person


def add_creator(entry, root, content):
    creator_list = ET.SubElement(content, "creator_list")
    for i, creator in enumerate(entry["creator"]):
        add_person(creator_list, "creator", i, creator, "creator_name")

    return root


def add_contributor(entry, root, content, content_classification):
    """寄与者を追加する

    JaLCのXSDスキーマで寄与者（contributor_list）を記述できるのは研究データのみ
    """
    if entry.get("contributor") and content_classification.text == "03":
        contributor_list = ET.SubElement(content, "contributor_list")
        for i, contributor in enumerate(entry["contributor"]):
            elem_contributor = add_person(
                contributor_list, "contributor", i, contributor, "contributor_name"
            )
            # contributor_type は必須のため、記述がなければ Other とする
            elem_contributor.set(
                "contributor_type", contributor.get("contributor_type") or "Other"
            )

    return root


def add_date(entry, root, content, content_classification, classification):
    if entry.get("date"):
        pub_date_str = None
        date_granted = entry.get("date_granted")

        for date in entry["date"]:
            if date["date_type"] == "Issued":
                pub_date_str = date["date"]
            elif date_granted:
                pub_date_str = date_granted
            elif date["date_type"] == "Created" or date["date_type"] == "Updated":
                pub_date_str = date["date"]

        if pub_date_str:
            if type(pub_date_str) is str:
                pub_date = datetime.datetime.strptime(pub_date_str, "%Y-%m-%d")
            elif type(pub_date_str) is datetime.date:
                pub_date = pub_date_str

            publication_date = ET.SubElement(content, "publication_date")
            year = ET.SubElement(publication_date, "year")
            year.text = str(pub_date.year).zfill(4)
            month = ET.SubElement(publication_date, "month")
            month.text = str(pub_date.month).zfill(2)
            day = ET.SubElement(publication_date, "day")
            day.text = str(pub_date.day).zfill(2)

            if classification == "article":
                elem_date = ET.SubElement(content, "date")
                elem_date.text = pub_date.strftime("%Y%m%d")

    if entry.get("date") and content_classification.text == "03":
        date_list = ET.SubElement(content, "date_list")
        for date in entry["date"]:
            elem_date = ET.SubElement(date_list, "date")
            elem_date.set("type", date["date_type"])
            elem_date.text = str(date["date"])

    return root


# JPCOARの助成機関識別子のタイプとJaLCの funder_identifier の type の対応
JALC_FUNDER_IDENTIFIER_TYPES = {
    "Crossref Funder": "FundRef",
    "GRID": "GRID",
    "ISNI": "ISNI",
    "ROR": "ROR",
}


def funder_identifier_type(identifier_type):
    """JPCOARの助成機関識別子のタイプをJaLCの type に変換する"""
    # e-Rad_funder などJaLCにないタイプは Other とする
    return JALC_FUNDER_IDENTIFIER_TYPES.get(identifier_type, "Other")


def first_value(items, key):
    """言語ごとに記述された値のうち、最初の値と言語を返す"""
    for item in items or []:
        if item.get(key):
            return item[key], item.get("lang")
    return None, None


def add_funding_reference(entry, root, content, content_classification=None):
    """助成情報を fund_list として追加する

    研究データ（content_classification が 03）では、プログラム情報識別子、
    プログラム情報、研究課題名も award_number_group に出力する
    """
    funds = []
    for funding_reference in entry.get("funding_reference") or []:
        # funder_name は必須で、1件のみ記述できる
        funder_name_text, funder_name_lang = first_value(
            funding_reference.get("funder_name"), "funder_name"
        )
        if funder_name_text is None:
            continue

        fund = ET.Element("fund")
        funder_name = ET.SubElement(fund, "funder_name")
        funder_name.text = funder_name_text
        if funder_name_lang:
            funder_name.set("lang", iso_639_1(funder_name_lang))

        identifier = funding_reference.get("funder_identifier") or {}
        if identifier.get("funder_identifier"):
            funder_identifier = ET.SubElement(
                fund,
                "funder_identifier",
                {
                    "type": funder_identifier_type(
                        identifier.get("funder_identifier_type")
                    )
                },
            )
            funder_identifier.text = str(identifier["funder_identifier"])

        # award_number_group には award_number が必須
        award = funding_reference.get("award_number") or {}
        if award.get("award_number"):
            award_number_group = ET.SubElement(fund, "award_number_group")
            if content_classification is not None and (
                content_classification.text == "03"
            ):
                add_research_data_program(award_number_group, funding_reference)
            award_number = ET.SubElement(award_number_group, "award_number")
            award_number.text = str(award["award_number"])
            if award.get("award_number_type"):
                award_number.set("type", award["award_number_type"])

        funds.append(fund)

    # fund_list には fund が1件以上必要
    if funds:
        fund_list = ET.SubElement(content, "fund_list")
        fund_list.extend(funds)

    return root


def add_research_data_program(award_number_group, funding_reference):
    """研究データの award_number_group にプログラム情報と研究課題名を追加する

    XSDスキーマの順序（program_id、program_name、project_name）で出力する
    """
    stream_identifier = funding_reference.get("funding_stream_identifier") or {}
    if stream_identifier.get("funding_stream_identifier"):
        program_id = ET.SubElement(award_number_group, "program_id")
        program_id.text = str(stream_identifier["funding_stream_identifier"])

    program_name_text, _ = first_value(
        funding_reference.get("funding_stream"), "funding_stream"
    )
    if program_name_text:
        program_name = ET.SubElement(award_number_group, "program_name")
        program_name.text = program_name_text

    project_name_text, _ = first_value(
        funding_reference.get("award_title"), "award_title"
    )
    if project_name_text:
        project_name = ET.SubElement(award_number_group, "project_name")
        project_name.text = project_name_text


# 分類記号を値とする主題のスキーム。キーワードではないため keyword_list に出力しない
CLASSIFICATION_SUBJECT_SCHEMES = {"NDC", "NDLC", "DDC", "UDC", "LCC"}


def add_keyword_list(entry, content, content_classification):
    """主題を keyword_list として追加する

    JaLCのXSDスキーマで keyword_list を記述できるのは論文（01）と教材（04）のみ
    """
    if content_classification.text not in ("01", "04"):
        return

    subjects = [
        d
        for d in entry.get("subject") or []
        if d.get("subject")
        and d.get("subject_scheme") not in CLASSIFICATION_SUBJECT_SCHEMES
    ]
    if not subjects:
        return

    keyword_list = ET.SubElement(content, "keyword_list")
    for i, d in enumerate(subjects):
        keyword = ET.SubElement(keyword_list, "keyword", {"sequence": str(i)})
        if d.get("lang"):
            keyword.set("lang", iso_639_1(d["lang"]))
        keyword.text = str(d["subject"])


def add_subject_list(entry, content, content_classification):
    """主題を subject_list として追加する（研究データのみ）

    研究データでは subject_scheme で主題のスキームを記述できるため、
    keyword_list と異なり分類記号の主題も出力する
    """
    if content_classification.text != "03":
        return

    subjects = [d for d in entry.get("subject") or [] if d.get("subject")]
    if not subjects:
        return

    subject_list = ET.SubElement(content, "subject_list")
    for d in subjects:
        subject = ET.SubElement(subject_list, "subject")
        if d.get("lang"):
            subject.set("lang", iso_639_1(d["lang"]))
        # subject_uri は主題の値のURIで、スキームのURI（scheme_uri）ではないため出力しない
        if d.get("subject_scheme"):
            subject.set("subject_scheme", d["subject_scheme"])
        subject.text = str(d["subject"])


def add_abstract_list(entry, content, content_classification):
    """内容記述のうち抄録を abstract_list として追加する（論文のみ）

    JaLCのXSDスキーマで abstract_list を記述できるのは論文のみ。
    内容記述の種別が Abstract のものだけを出力する
    """
    if content_classification.text != "01":
        return

    abstracts = [
        d
        for d in entry.get("description") or []
        if d.get("description") and d.get("description_type") == "Abstract"
    ]
    if not abstracts:
        return

    abstract_list = ET.SubElement(content, "abstract_list")
    for d in abstracts:
        check_length(str(d["description"]), ABSTRACT_MAX_LENGTH, "抄録", d.get("lang"))
        abstract = ET.SubElement(abstract_list, "abstract")
        if d.get("lang"):
            abstract.set("lang", iso_639_1(d["lang"]))
        abstract.text = str(d["description"])


# JaLCの description の type に使用できる値
JALC_DESCRIPTION_TYPES = {
    "Abstract",
    "Methods",
    "SeriesInformation",
    "TableOfContents",
    "TechnicalInfo",
    "Other",
}


def add_description_list(entry, content, content_classification):
    """内容記述を description_list として追加する（研究データのみ）

    研究データでは内容記述の種別を type で記述できるため、抄録以外も出力する
    """
    if content_classification.text != "03":
        return

    descriptions = [d for d in entry.get("description") or [] if d.get("description")]
    if not descriptions:
        return

    description_list = ET.SubElement(content, "description_list")
    for d in descriptions:
        check_length(
            str(d["description"]), DESCRIPTION_MAX_LENGTH, "内容記述", d.get("lang")
        )
        # type は必須のため、種別がない、またはJaLCにない種別の場合は Other とする
        description_type = d.get("description_type")
        if description_type not in JALC_DESCRIPTION_TYPES:
            description_type = "Other"
        description = ET.SubElement(
            description_list, "description", {"type": description_type}
        )
        if d.get("lang"):
            description.set("lang", iso_639_1(d["lang"]))
        description.text = str(d["description"])


def iso_639_1(lang):
    if len(lang) > 2:
        if not lang == "und":
            return lang[:2]
        else:
            return "unk"
    else:
        return lang
