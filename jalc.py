import yaml
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
from logging import getLogger, DEBUG

logger = getLogger(__name__)
logger.setLevel(DEBUG)

def generate(data_dir, output_dir, base_url):
  # メタデータYAMLファイルを開く
  with open(f"{data_dir}/jpcoar20.yaml", encoding = "utf-8") as file:
    entry = yaml.load(file, Loader = yaml.Loader)

  # ID登録が記述されていなければ処理を終了する
  if entry.get("identifier_registration") is None:
    return

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
  site_id.text = "dummy"

  content = ET.SubElement(body, "content", {"sequence": "0"})
  if classification:
    content.set("classification", classification)

  doi = ET.SubElement(content, "doi")
  doi.text = entry["identifier_registration"]["identifier"]

  url = ET.SubElement(content, "url")
  url.text = urljoin(base_url, f"{entry['id']}/ro-crate-preview.html")

  if book_classification:
    book_c = ET.SubElement(content, "book_classification")
    book_c.text = book_classification

  if classification == "01":
    journal_id_list = ET.SubElement(content, "journal_id_list")
    if entry.get("source_identifier"):
      for source_identifier in entry["source_identifier"]:
        if source_identifier["identifier_type"] == "PISSN":
          journal_id = ET.SubElement(journal_id_list, "journal_id", {"type": "ISSN"})
        elif source_identifier["identifier_type"] == "EISSN":
          journal_id = ET.SubElement(journal_id_list, "journal_id", {"type": "ISSN"})
        else:
          journal_id = ET.SubElement(journal_id_list, "journal_id", {"type": source_identifier["identifier_type"]})
        journal_id.text = source_identifier["identifier"]

  title_list = ET.SubElement(content, "title_list")
  for t in entry["title"]:
    titles = ET.SubElement(title_list, "titles")
    if t.get("lang"):
      titles.set("lang", iso_639_1(t["lang"]))
    title = ET.SubElement(titles, "title")
    title.text = t["title"]

  creator_list = ET.SubElement(content, "creator_list")
  for i, c in enumerate(entry["creator"]):
    creator = ET.SubElement(creator_list, "creator", {"sequence": str(i)})
    for name in c["creator_name"]:
      names = ET.SubElement(creator, "names")
      if name.get("lang"):
        names.set("lang", iso_639_1(name["lang"]))
      first_name = ET.SubElement(names, "first_name")
      first_name.text = name["name"]
    if c.get("name_identifier"):
      researcher_id = ET.SubElement(creator, "researcher_id")
      for identifier in c["name_identifier"]:
        id_code = ET.SubElement(researcher_id, "id_code", {"type": identifier.get("identifier_scheme", "")})
        id_code.text = identifier["identifier"]

  if book_classification:
    if entry.get("publisher"):
      publisher = ET.SubElement(content, "publisher")
      publisher_name = ET.SubElement(publisher, "publisher")
      publisher_name.text = entry["publisher"][0]["publisher"]

  if entry.get("volume"):
    volume = ET.SubElement(content, "volume")
    volume.text = entry["volume"]

  if entry.get("issue"):
    issue = ET.SubElement(content, "issue")
    issue.text = entry["issue"]

  if entry.get("pageStart"):
    first_page = ET.SubElement(content, "first_page")
    first_page.text = entry["pageStart"]

  if entry.get("pageEnd"):
    last_page = ET.SubElement(content, "last_page")
    last_page.text = entry["pageEnd"]

  if entry.get("funding_reference"):
    fund_list = ET.SubElement(content, "fund_list")
    for funding_reference in entry["funding_reference"]:
      fund = ET.SubElement(fund_list, "fund")
      funder_name = ET.SubElement(fund, "funder_name")
      funder_name.text = funding_reference["funder_name"][0].get("funder_name")
      if funding_reference.get("funder_identifier"):
        funder_identifier = ET.SubElement(fund, "funder_identifier", {"type": funding_reference.get("funder_identifier_type", "Other")})
        funder_identifier.text = funding_reference["funder_identifier"]

  # JaLC XMLを出力する
  with open(f"{output_dir}/{str(entry['id'])}/jalc.xml", "w") as file:
    ET.indent(root, space="\t", level=0)
    file.write(ET.tostring(root, encoding = "unicode", xml_declaration = True))

def iso_639_1(lang):
  if len(lang) > 2:
    if not lang == "und":
      return lang[:2]
    else:
      return "unk"
  else:
    return lang
