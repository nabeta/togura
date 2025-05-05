import os
import glob
import yaml
import xml.etree.ElementTree as ET
import tempfile
import datetime
from rocrate.rocrate import ROCrate
from rocrate.model.person import Person
from jinja2 import Template, Environment, FileSystemLoader
from logging import getLogger, DEBUG

logger = getLogger(__name__)
logger.setLevel(DEBUG)

def generate_ro_crate(data_dir, output_dir, root):
  """RO-Crateのディレクトリを出力する"""
  with open(f"{data_dir}/jpcoar20.yaml", encoding = "utf-8") as file:
    entry = yaml.load(file, Loader = yaml.Loader)

  crate = ROCrate(gen_preview = True)
  crate.name = entry["title"][0]["title"]

  # ファイルを追加
  for file in glob.glob(f"{data_dir}/*"):
    filename = os.path.basename(file)
    if filename == "jpcoar20.yaml":
      continue

    data = crate.add_file(file)

  # 作成者を追加
  if entry.get("creator"):
    for creator in entry["creator"]:
      c = crate.add(Person(crate, properties = {
           "name": creator["creator_name"][0]["name"]
        }
      ))

  # JPCOARスキーマのXMLファイルを追加
  with tempfile.TemporaryDirectory() as tempdir:
    with open(f"{tempdir}/jpcoar20.xml", "w", encoding = "utf-8") as xml_file:
      ET.indent(root, space="\t", level=0)
      xml_file.write(ET.tostring(root, encoding = "unicode", xml_declaration = True))
      xml_file.seek(0)
      crate.add_file(xml_file.name, dest_path = "jpcoar20.xml")

    # ディレクトリを出力
    crate_dir = f"{output_dir}/{str(entry['id'])}"
    crate.write(crate_dir)

def generate_html(data_dir, output_dir, config):
  """HTMLを作成する"""
  env = Environment(loader=FileSystemLoader('./', encoding='utf8'))
  template_index = env.get_template('templates/index.j2')
  template_show = env.get_template('templates/show.j2')
  entries = []
  for path in sorted(glob.glob(f"{data_dir}/*"), key=os.path.basename, reverse=True):
    files = []
    for file in glob.glob(f"{path}/*"):
      filename = os.path.basename(file)
      if filename == "jpcoar20.yaml":
        continue
      else:
        files.append(filename)

    with open(f"{path}/jpcoar20.yaml", encoding = "utf-8") as file:
      entry = yaml.load(file, Loader = yaml.Loader)
      entries.append(entry)
      with open(f"{output_dir}/{str(entry['id'])}.html", "w") as file:
        template_show.globals['now'] = datetime.datetime.now(datetime.UTC)
        show_html = template_show.render(entry = entry, files = files, config = config())
        file.write(show_html)
        logger.debug(f"{str(entry['id'])}.html")

  template_index.globals['now'] = datetime.datetime.now(datetime.UTC)
  index_html = template_index.render(entries = entries, config = config())
  with open(f"{output_dir}/index.html", "w") as file:
    file.write(index_html)
    logger.debug("index.html")

def generate_jalc_xml(data_dir, output_dir, config):
  # メタデータYAMLファイルを開く
  with open(f"{data_dir}/jpcoar20.yaml", encoding = "utf-8") as file:
    entry = yaml.load(file, Loader = yaml.Loader)

  # ID登録や収録物識別子が記述されていなければ処理を終了する
  if entry.get("identifier_registration") == None:
    return

  if entry.get("source_identifier") == None:
    return

  root = ET.Element("root")
  head = ET.SubElement(root, "head")

  error_process = ET.SubElement(head, "error_process")
  error_process.text = "0"

  result_method = ET.SubElement(head, "result_method")
  result_method.text = "0"

  content_classification = ET.SubElement(head, "content_classification")
  classification = None
  match entry["type"]:
    case "departmental bulletin paper":
      content_classification.text = "01"
      classification = "article"
    case "journal article":
      content_classification.text = "01"
      classification = "article"
    case _:
      return

  request_kind = ET.SubElement(head, "request_kind")
  request_kind.text = "01"

  body = ET.SubElement(root, "body")
  content = ET.SubElement(body, "content", {"classification": classification, "sequence": ""})

  doi = ET.SubElement(content, "doi")
  doi.text = entry["identifier_registration"]["identifier"]

  url = ET.SubElement(content, "url")
  url.text = f"{config()['base_url']}/{entry['id']}"

  journal_id_list = ET.SubElement(content, "journal_id_list")
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
    titles = ET.SubElement(title_list, "titles", {"lang": t.get("lang", "unknown")})
    title = ET.SubElement(titles, "titles")
    title.text = t["title"]

  creator_list = ET.SubElement(content, "creator_list")
  for i, c in enumerate(entry["creator"]):
    creator = ET.SubElement(creator_list, "creator", {"sequence": str(i)})
    for name in c["creator_name"]:
      names = ET.SubElement(creator, "names", {"lang": name.get("lang", "")})
      first_name = ET.SubElement(names, "first_name")
      first_name.text = name["name"]
    if c.get("name_identifier"):
      researcher_id = ET.SubElement(creator, "researcher_id")
      for identifier in c["name_identifier"]:
        id_code = ET.SubElement(researcher_id, "id_code", {"type": identifier.get("identifier_scheme", "")})
        id_code.text = identifier["identifier"]

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
