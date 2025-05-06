#!/usr/bin/env python3
import sys
import os
import glob
import yaml
import mimetypes
import shutil
import datetime
from xml.dom import minidom
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
import generator
import resourcesync
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

ns = {
  "jpcoar": "https://github.com/JPCOAR/schema/blob/master/2.0/",
  "dc": "http://purl.org/dc/elements/1.1/",
  "dcterms": "http://purl.org/dc/terms/",
  "datacite": "https://schema.datacite.org/meta/kernel-4/",
  "oaire": "http://namespace.openaire.eu/schema/oaire/",
  "dcndl": "http://ndl.go.jp/dcndl/terms/",
  "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
  "xsi": "http://www.w3.org/2001/XMLSchema-instance"
}

for key in ns.keys():
  ET.register_namespace(key, ns[key])

def access_rights_uri(string):
  match string:
    case "embargoed access":
      return "http://purl.org/coar/access_right/c_f1cf"
    case "metadata only access":
      return "http://purl.org/coar/access_right/c_14cb"
    case "open access":
      return "http://purl.org/coar/access_right/c_abf2"
    case "restricted access":
      return "http://purl.org/coar/access_right/c_16ec"

def resource_type_uri(string):
  match string:
    case "conference paper":
      return "http://purl.org/coar/resource_type/c_5794"
    case "data paper":
      return "http://purl.org/coar/resource_type/c_beb9"
    case "departmental bulletin paper":
      return "http://purl.org/coar/resource_type/c_6501"
    case "editorial":
      return "http://purl.org/coar/resource_type/c_b239"
    case "journal":
      return "http://purl.org/coar/resource_type/c_0640"
    case "journal article":
      return "http://purl.org/coar/resource_type/c_6501"
    case "newspaper":
      return "http://purl.org/coar/resource_type/c_2fe3"
    case "review article":
      return "http://purl.org/coar/resource_type/c_dcae04bc"
    case "other periodical":
      return "http://purl.org/coar/resource_type/QX5C-AR31"
    case "software paper":
      return "http://purl.org/coar/resource_type/c_7bab"
    case "article":
      return "http://purl.org/coar/resource_type/c_6501"
    case "book":
      return "http://purl.org/coar/resource_type/c_2f33"
    case "book part":
      return "http://purl.org/coar/resource_type/c_3248"
    case "cartographic material":
      return "http://purl.org/coar/resource_type/c_12cc"
    case "map":
      return "http://purl.org/coar/resource_type/c_12cd"
    case "conference output":
      return "http://purl.org/coar/resource_type/c_c94f"
    case "conference presentation":
      return "http://purl.org/coar/resource_type/R60J-J5BD"
    case "conference proceedings":
      return "http://purl.org/coar/resource_type/c_f744"
    case "conference poster":
      return "http://purl.org/coar/resource_type/c_6670"
    case "aggregated data":
      return "http://purl.org/coar/resource_type/ACF7-8YT9"
    case "clinical trial data":
      return "http://purl.org/coar/resource_type/c_cb28"
    case "compiled data":
      return "http://purl.org/coar/resource_type/FXF3-D3G7"
    case "dataset":
      return "http://purl.org/coar/resource_type/c_ddb1"
    case "encoded data":
      return "http://purl.org/coar/resource_type/AM6W-6QAW"
    case "experimental data":
      return "http://purl.org/coar/resource_type/63NG-B465"
    case "genomic data":
      return "http://purl.org/coar/resource_type/A8F1-NPV9"
    case "geospatial data":
      return "http://purl.org/coar/resource_type/2H0M-X761"
    case "laboratory notebook":
      return "http://purl.org/coar/resource_type/H41Y-FW7B"
    case "measurement and test data":
      return "http://purl.org/coar/resource_type/DD58-GFSX"
    case "observational data":
      return "http://purl.org/coar/resource_type/FF4C-28RK"
    case "recorded data":
      return "http://purl.org/coar/resource_type/CQMR-7K63"
    case "simulation data":
      return "http://purl.org/coar/resource_type/W2XT-7017"
    case "survey data":
      return "http://purl.org/coar/resource_type/NHD0-W6SY"
    case "image":
      return "http://purl.org/coar/resource_type/c_c513"
    case "still image":
      return "http://purl.org/coar/resource_type/c_ecc8"
    case "moving image":
      return "http://purl.org/coar/resource_type/c_8a7e"
    case "video":
      return "http://purl.org/coar/resource_type/c_12ce"
    case "lecture":
      return "http://purl.org/coar/resource_type/c_8544"
    case "design patent":
      return "http://purl.org/coar/resource_type/C53B-JCY5"
    case "patent":
      return "http://purl.org/coar/resource_type/c_15cd"
    case "PCT application":
      return "http://purl.org/coar/resource_type/SB3Y-W4EH"
    case "plant patent":
      return "http://purl.org/coar/resource_type/Z907-YMBB"
    case "plant variety protection":
      return "http://purl.org/coar/resource_type/GPQ7-G5VE"
    case "software patent":
      return "http://purl.org/coar/resource_type/MW8G-3CR8"
    case "trademark":
      return "http://purl.org/coar/resource_type/H6QP-SC1X"
    case "utility model":
      return "http://purl.org/coar/resource_type/9DKX-KSAF"
    case "report":
      return "http://purl.org/coar/resource_type/c_93fc"
    case "research report":
      return "http://purl.org/coar/resource_type/c_18ws"
    case "technical report":
      return "http://purl.org/coar/resource_type/c_18gh"
    case "policy report":
      return "http://purl.org/coar/resource_type/c_186u"
    case "working paper":
      return "ihttp://purl.org/coar/resource_type/c_8042"
    case "data management plan":
      return "http://purl.org/coar/resource_type/c_ab20"
    case "sound":
      return "http://purl.org/coar/resource_type/c_18cc"
    case "thesis":
      return "http://purl.org/coar/resource_type/c_46ec"
    case "bachelor thesis":
      return "http://purl.org/coar/resource_type/c_7a1f"
    case "master thesis":
      return "http://purl.org/coar/resource_type/c_bdcc"
    case "doctoral thesis":
      return "http://purl.org/coar/resource_type/c_db06"
    case "commentary":
      return "http://purl.org/coar/resource_type/D97F-VB57"
    case "design":
      return "http://purl.org/coar/resource_type/542X-3S04"
    case "industrial design":
      return "http://purl.org/coar/resource_type/JBNF-DYAD"
    case "interactive resource":
      return "http://purl.org/coar/resource_type/c_e9a0"
    case "layout design":
      return "http://purl.org/coar/resource_type/BW7T-YM2G"
    case "learning object":
      return "http://purl.org/coar/resource_type/c_e059"
    case "manuscript":
      return "http://purl.org/coar/resource_type/c_0040"
    case "musical notation":
      return "http://purl.org/coar/resource_type/c_18cw"
    case "peer review":
      return "http://purl.org/coar/resource_type/H9BQ-739P"
    case "research proposal":
      return "http://purl.org/coar/resource_type/c_baaf"
    case "research protocol":
      return "http://purl.org/coar/resource_type/YZ1N-ZFT9"
    case "software":
      return "http://purl.org/coar/resource_type/c_5ce6"
    case "source code":
      return "http://purl.org/coar/resource_type/QH80-2R4E"
    case "technical documentation":
      return "http://purl.org/coar/resource_type/c_71bd"
    case "transcription":
      return "http://purl.org/coar/resource_type/6NC7-GK9S"
    case "workflow":
      return "http://purl.org/coar/resource_type/c_393c"
    case "other":
      return "http://purl.org/coar/resource_type/c_1843"

def text_version_uri(string):
  match string:
    case "AO":
      return "http://purl.org/coar/version/c_b1a7d7d4d402bcce"
    case "SMUR":
      return "http://purl.org/coar/version/c_71e4c1898caa6e32"
    case "AM":
      return "http://purl.org/coar/version/c_ab4af688f83e57aa"
    case "P":
      return "http://purl.org/coar/version/c_fa2ee174bc00049f"
    case "VoR":
      return "http://purl.org/coar/version/c_970fb48d4fbd8a85"
    case "CVoR":
      return "http://purl.org/coar/version/c_e19f295774971610"
    case "EVoR":
      return "http://purl.org/coar/version/c_dc82b40f9837b551"
    case "NA":
      return "http://purl.org/coar/version/c_be7fb7dd8ff6fe43"

def jpcoar_identifier_type(string):
  url = urlparse(string)
  match url.hostname.lower():
    case "doi.org":
      return "DOI"
    case "dx.doi.org":
      return "DOI"
    case "hdl.handle.net":
      return "HDL"
    case _:
      return "URI"

def generate_xml(entry, ns, base_url):
  """JPCOARスキーマのXMLを作成する"""
  root = ET.Element(ET.QName(ns["jpcoar"], "jpcoar"))
  root.set(ET.QName(ns["xsi"], "schemaLocation"), "https://github.com/JPCOAR/schema/blob/master/2.0/ jpcoar_scm.xsd")

  for title in entry["title"]:
    elem_title = ET.SubElement(root, ET.QName(ns["dc"], "title"), {
      "xml:lang": title.get("lang", "und") or "und"
    })
    elem_title.text = title["title"]

  if entry.get("creator"):
    add_creator(entry, root)

  if entry.get("contributor"):
    add_contributor(entry, root)

  if entry.get("access_rights"):
    elem_access_rights = ET.SubElement(root, ET.QName(ns["dcterms"], "accessRights"))
    elem_access_rights.set("rdf:resource", access_rights_uri(entry["access_rights"]))
    elem_access_rights.text = entry["access_rights"]

  if entry.get("rights"):
    for rights in entry["rights"]:
      elem_rights = ET.SubElement(root, ET.QName(ns["dc"], "rights"), {
        "xml:lang": rights.get("lang", "und") or "und"
      })
      if rights.get("rights_uri"):
        elem_rights.set(ET.QName(ns["rdf"], "resource"), rights["rights_uri"])
      elem_rights.text = rights["rights"]

  if entry.get("subject"):
    for subject in entry["subject"]:
      elem_subject = ET.SubElement(root, ET.QName(ns["jpcoar"], "subject"), {
        "subjectScheme": subject["subject_scheme"],
        "xml:lang": subject.get("lang", "und") or "und"
      })
      if subject.get("subject_uri"):
        elem_subject.set("subjectURI", subject["subject_uri"])
      elem_subject.text = subject["subject"]

  if entry.get("description"):
    for description in entry["description"]:
      elem_description = ET.SubElement(root, ET.QName(ns["datacite"], "description"), {
        "descriptionType": description["description_type"],
        "xml:lang": description.get("lang", "und") or "und",
      })
      elem_description.text = description["description"]

  if entry.get("publisher"):
    for publisher in entry["publisher"]:
      elem_publisher = ET.SubElement(root, ET.QName(ns["dc"], "publisher"), {
        "xml:lang": publisher.get("lang", "und") or "und"
      })
      elem_publisher.text = publisher["publisher"]

  if entry.get("date"):
    for date in entry["date"]:
      elem_date = ET.SubElement(root, ET.QName(ns["datacite"], "date"), {"dateType": date["date_type"]})
      elem_date.text = str(date["date"])

  if entry.get("language"):
    for language in entry["language"]:
      elem_language = ET.SubElement(root, ET.QName(ns["dc"], "language"))
      elem_language.text = language

  elem_resource_type = ET.SubElement(root, ET.QName(ns["dc"], "type"), {
    ET.QName(ns["rdf"], "resource"): resource_type_uri(entry["type"])
  })
  elem_resource_type.text = entry["type"]

  if entry.get("text_version"):
    elem_text_version = ET.SubElement(root, ET.QName(ns["oaire"], "version"), {
      ET.QName(ns["rdf"], "resource"): text_version_uri(entry["text_version"])
    })
    elem_text_version.text = entry["text_version"]

  add_identifier(entry, root, base_url)

  if entry.get("identifier_registration"):
    elem_identifier_registration = ET.SubElement(root, ET.QName(ns["jpcoar"], "identifierRegistration"), {
      "identifierType": entry["identifier_registration"]["identifier_type"]
    })
    elem_identifier_registration.text = entry["identifier_registration"]["identifier"]

  if entry.get("relation"):
    for relation in entry["relation"]:
      elem_relation = ET.SubElement(root, ET.QName(ns["jpcoar"], "relation"), {
        "relationType": relation["relation_type"]
      })
      elem_related_identifier = ET.SubElement(elem_relation, ET.QName(ns["jpcoar"], "relatedIdentifier"), {"identifierType": relation["related_identifier"]["identifier_type"]})
      elem_related_identifier.text = relation["related_identifier"]["identifier"]

  if entry.get("funding_reference"):
    add_funding_reference(entry, root)

  if entry.get("source_identifier"):
    for source_identifier in entry["source_identifier"]:
      elem_source_identifier = ET.SubElement(root, ET.QName(ns["jpcoar"], "sourceIdentifier"), {"identifierType": source_identifier["identifier_type"]})
      elem_source_identifier.text = source_identifier["identifier"]

  if entry.get("source_title"):
    for source_title in entry["source_title"]:
      elem_source_title = ET.SubElement(root, ET.QName(ns["jpcoar"], "sourceTitle"), {
        "xml:lang": source_title.get("lang", "und") or "und"
      })
      elem_source_title.text = source_title["source_title"]

  if entry.get("volume"):
    volume = ET.SubElement(root, ET.QName(ns["jpcoar"], "volume"))
    volume.text = entry["volume"]

  if entry.get("issue"):
    issue = ET.SubElement(root, ET.QName(ns["jpcoar"], "issue"))
    issue.text = entry["issue"]

  if entry.get("num_pages"):
    num_pages = ET.SubElement(root, ET.QName(ns["jpcoar"], "numPages"))
    num_pages.text = str(entry["num_pages"])

  if entry.get("page_start"):
    page_start = ET.SubElement(root, ET.QName(ns["jpcoar"], "pageStart"))
    page_start.text = entry["page_start"]

  if entry.get("page_end"):
    page_end = ET.SubElement(root, ET.QName(ns["jpcoar"], "pageEnd"))
    page_end.text = entry["page_end"]

  if entry.get("dissertation_number"):
    dissertation_number = ET.SubElement(root, ET.QName(ns["dcndl"], "dissertationNumber"))
    dissertation_number.text = entry["dissertation_number"]

  if entry.get("degree_name"):
    for d in entry["degree_name"]:
      degree_name = ET.SubElement(root, ET.QName(ns["dcndl"], "degreeName"), {
        "xml:lang": d.get("lang", "und") or "und"
      })
      degree_name.text = d["degree_name"]

  if entry.get("date_granted"):
    date_granted = ET.SubElement(root, ET.QName(ns["dcndl"], "dateGranted"))
    date_granted.text = str(entry["date_granted"])

  if entry.get("degree_grantor"):
    degree_grantor = ET.SubElement(root, ET.QName(ns["jpcoar"], "degreeGrantor"))
    for d in entry["degree_grantor"]:
      for i in d["name_identifier"]:
        name_identifier = ET.SubElement(degree_grantor, ET.QName(ns["jpcoar"], "nameIdentifier"), {
          "nameIdentifierScheme": i.get("name_identifier_scheme", "unk")
        })
        name_identifier.text = i["identifier"]
      for i in d["degree_grantor_name"]:
        degree_grantor_name = ET.SubElement(degree_grantor, ET.QName(ns["jpcoar"], "degreeGrantorName"), {
          "xml:lang": i.get("lang", "und") or "und"
        })
        degree_grantor_name.text = i["name"]

  if entry.get("file"):
    add_file(entry, root)

  logger.debug(f"{str(entry['id'])}.yaml")
  return root

def add_creator(entry, root):
  """作成者をメタデータに追加する"""
  for creator in entry["creator"]:
    elem_creator = ET.SubElement(root, ET.QName(ns["jpcoar"], "creator"), {"creatorType": "著"})
    if creator.get("name_identifier"):
      for name_identifier in creator["name_identifier"]:
        elem_name_identifier = ET.SubElement(elem_creator, ET.QName(ns["jpcoar"], "nameIdentifier"), {
          "nameIdentifierScheme": name_identifier["identifier_scheme"],
          "nameIdentifierURI": name_identifier["identifier"]
        })
        elem_name_identifier.text = name_identifier["identifier"]
    if creator.get("creator_name"):
      for creator_name in creator["creator_name"]:
        elem_creator_name = ET.SubElement(elem_creator, ET.QName(ns["jpcoar"], "creatorName"), {
          "xml:lang": creator_name.get("lang", "und") or "und"
        })
        elem_creator_name.text = creator_name["name"]
    if creator.get("affiliation"):
      for affiliation in creator["affiliation"]:
        elem_affiliation = ET.SubElement(elem_creator, ET.QName(ns["jpcoar"], "affiliation"))
        elem_affiliation_identifier = ET.SubElement(elem_affiliation, ET.QName(ns["jpcoar"], "nameIdentifier"), {
          "nameIdentifierScheme": affiliation["identifier_scheme"],
          "nameIdentifierURI": affiliation["identifier"]
        })
        elem_affiliation_identifier.text = affiliation["identifier"]
        for affiliation_name in affiliation["affiliation_name"]:
          elem_affiliation_name = ET.SubElement(elem_affiliation, ET.QName(ns["jpcoar"], "affiliationName"), {
            "xml:lang": affiliation_name.get("lang", "und") or "und"
          })
          elem_affiliation_name.text = affiliation_name["name"]

def add_contributor(entry, root):
  """寄与者をメタデータに追加する"""
  for contributor in entry["contributor"]:
    elem_contributor = ET.SubElement(root, ET.QName(ns["jpcoar"], "contributor"))
    if contributor.get("name_identifier"):
      for name_identifier in contributor["name_identifier"]:
        elem_name_identifier = ET.SubElement(elem_contributor, ET.QName(ns["jpcoar"], "nameIdentifier"), {
          "nameIdentifierScheme": name_identifier["identifier_scheme"],
          "nameIdentifierURI": name_identifier["identifier"]
        })
        elem_name_identifier.text = name_identifier["identifier"]
    if contributor.get("contributor_name"):
      for contributor_name in contributor["contributor_name"]:
        elem_contributor_name = ET.SubElement(elem_contributor, ET.QName(ns["jpcoar"], "contributorName"), {
          "xml:lang": contributor_name.get("lang", "und") or "und"
        })
        elem_contributor_name.text = contributor_name["name"]
    if contributor.get("affiliation"):
      for affiliation in contributor["affiliation"]:
        elem_affiliation = ET.SubElement(elem_contributor, ET.QName(ns["jpcoar"], "affiliation"))
        elem_affiliation_identifier = ET.SubElement(elem_affiliation, ET.QName(ns["jpcoar"], "nameIdentifier"), {
          "nameIdentifierScheme": affiliation["identifier_scheme"],
          "nameIdentifierURI": affiliation["identifier"]
        })
        elem_affiliation_identifier.text = affiliation["identifier"]
        for affiliation_name in affiliation["affiliation_name"]:
          elem_affiliation_name = ET.SubElement(elem_affiliation, ET.QName(ns["jpcoar"], "affiliationName"), {
            "xml:lang": affiliation_name.get("lang", "und") or "und"
          })
          elem_affiliation_name.text = affiliation_name["name"]

def add_identifier(entry, root, prefix):
  elem_identifier = ET.SubElement(root, ET.QName(ns["jpcoar"], "identifier"), {"identifierType": "URI"})
  elem_identifier.text = urljoin(config()["base_url"], f"{entry['id']}/ro-crate-metadata.html")

  if entry.get("identifier"):
    for identifier in entry["identifier"]:
      elem_identifier = ET.SubElement(root, ET.QName(ns["jpcoar"], "identifier"), {"identifierType": jpcoar_identifier_type(identifier)})
      elem_identifier.text = identifier

def add_funding_reference(entry, root):
  """助成情報をメタデータに追加する"""
  for funding_reference in entry["funding_reference"]:
    elem_funding_reference = ET.SubElement(root, ET.QName(ns["jpcoar"], "fundingReference"))

    if funding_reference.get("funder_identifier"):
      elem_funder_identifier = ET.SubElement(elem_funding_reference, ET.QName(ns["jpcoar"], "funderIdentifier"), {
        "funderIdentifierType": funding_reference["funder_identifier_type"]
      })
      elem_funder_identifier.text = funding_reference["funder_identifier"]

    for funder_name in funding_reference["funder_name"]:
      elem_funder_name = ET.SubElement(elem_funding_reference, ET.QName(ns["jpcoar"], "funderName"), {
        "xml:lang": funder_name.get("lang", "und") or "und"
      })
      elem_funder_name.text = funder_name["funder_name"]

    if funding_reference.get("funding_stream"):
      for funding_stream in funding_reference["funding_stream"]:
        elem_funding_stream = ET.SubElement(elem_funding_reference, ET.QName(ns["jpcoar"], "fundingStream"), {
          "xml:lang": funding_stream.get("lang", "und") or "und"
        })
        elem_funding_stream.text = funding_stream["funding_stream"]

    if funding_reference.get("award_number"):
      elem_award_number = ET.SubElement(elem_funding_reference, ET.QName(ns["jpcoar"], "awardNumber"), {
        "awardURI": funding_reference["award_number"]["award_uri"],
        "awardNumberType": funding_reference["award_number"]["award_number_type"]
       })
      elem_award_number.text = funding_reference["award_number"]["award_number"]

    if funding_reference.get("award_title"):
      for award_title in funding_reference["award_title"]:
        elem_award_title = ET.SubElement(elem_funding_reference, ET.QName(ns["jpcoar"], "awardTitle"), {
          "xml:lang": award_title.get("lang", "und") or "und"
        })
        elem_award_title.text = award_title["award_title"]

def add_file(entry, root):
  if entry.get("file"):
    for file in entry["file"]:
      elem_file = ET.SubElement(root, ET.QName(ns["jpcoar"], "file"))

      if file.get("uri"):
        elem_file_uri = ET.SubElement(elem_file, ET.QName(ns["jpcoar"], "URI"), {
            "objectType": file.get("object_type", "") or ""
          }
        )
        elem_file_uri.text = file["uri"]

      if file.get("mime_type"):
        elem_file_mime_type = ET.SubElement(elem_file, ET.QName(ns["jpcoar"], "mimeType"))
        elem_file_mime_type.text = file["mime_type"]

      if file.get("extent"):
        for extent in file["extent"]:
          elem_file_extent = ET.SubElement(elem_file, ET.QName(ns["jpcoar"], "extent"))
          elem_file_extent.text = extent

      if file.get("date"):
        for date in file["date"]:
          elem_file_date = ET.SubElement(elem_file, ET.QName(ns["datacite"], "date"), {
            "dateType": date.get("date_type", "und")
          })
          elem_file_date.text = str(date["date"])

def add_directory_file(data_dir, entry, root, ns, base_url):
  """ファイルの情報をメタデータに追加する"""
  for file in glob.glob(f"{data_dir}/*"):
    filename = os.path.basename(file)
    if filename == "jpcoar20.yaml":
      continue

    elem_file = ET.SubElement(root, ET.QName(ns["jpcoar"], "file"))
    elem_file_uri = ET.SubElement(
      elem_file,
      ET.QName(ns["jpcoar"], "URI"),
      {
        # "objectType": file["object_type"],
        "label": filename
      }
    )
    elem_file_uri.text = urljoin(base_url, f"{entry['id']}/{filename}")

    elem_mime_type = ET.SubElement(elem_file, ET.QName(ns["jpcoar"], "mimeType"))
    elem_file_extent = ET.SubElement(elem_file, ET.QName(ns["jpcoar"], "extent"))
    elem_file_extent.text = str(os.path.getsize(file))
    # for extent in file["extent"]:
      # elem_file_extent = ET.SubElement(elem_file, ET.QName(ns["jpcoar"], "extent"))
      # elem_file_extent.text = extent

    # for date in file["date"]:
      # elem_file_date = ET.SubElement(elem_file, ET.QName(ns["datacite"], "date"), {"dateType": date["date_type"]})
      # elem_file_date.text = str(date["date"])
    elem_mime_type.text = mimetypes.guess_type(file)[0]

def config():
  with open("config.yml", encoding = "utf-8") as file:
    return yaml.load(file, Loader = yaml.Loader)

def main():
  data_dir = "./work"
  output_dir = "./public"
  base_url = config()["base_url"]

  for path in glob.glob(f"{data_dir}/*"):
    with open(f"{path}/jpcoar20.yaml", encoding = "utf-8") as file:
      entry = yaml.load(file, Loader = yaml.Loader)
      root = generate_xml(entry, ns, base_url)
      add_directory_file(path, entry, root, ns, base_url)
      generator.generate_ro_crate(path, output_dir, root)
      generator.generate_jalc_xml(path, output_dir, config)
  generator.generate_html(data_dir, output_dir, config)
  resourcesync.generate_resourcesync(output_dir, base_url)

if __name__ == "__main__":
  main()
