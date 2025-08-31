from sickle import Sickle
from logging import getLogger, DEBUG
from urllib.parse import urlparse
import os
import requests
import xml.etree.ElementTree as ET
import yaml

logger = getLogger(__name__)
logger.setLevel(DEBUG)

def migrate(base_url, metadata_prefix, date_from, date_until, export_dir):
  sickle = Sickle(base_url)
  records = sickle.ListRecords(
    **{"metadataPrefix": metadata_prefix,
    "from": date_from,
    "until": date_until
  })

  if metadata_prefix == "jpcoar_2.0":
    jpcoar_ns = "https://github.com/JPCOAR/schema/blob/master/2.0/"
  else:
    jpcoar_ns = "https://github.com/JPCOAR/schema/blob/master/1.0/"

  ns = {
    "root": "http://www.openarchives.org/OAI/2.0/",
    "jpcoar": jpcoar_ns,
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "datacite": "https://schema.datacite.org/meta/kernel-4/",
    "oaire": "http://namespace.openaire.eu/schema/oaire/",
    "dcndl": "http://ndl.go.jp/dcndl/terms/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance"
  }

  for record in records:
    identifier = record.xml.find(".//root:identifier", ns).text.split(":")[-1]

    titles = []
    for title in record.xml.findall(".//dc:title", ns):
      d = {"title": title.text}
      lang = d.get("{http://www.w3.org/XML/1998/namespace}lang")
      if lang is not None:
        d["lang"] = lang
      titles.append(d)

    creators = []
    for creator in record.xml.findall(".//jpcoar:creator", ns):
      creators = []
      if creator.find("./jpcoar:creatorName", ns) is not None:
        creator_names = []
        for creator_name in creator.findall("./jpcoar:creatorName", ns):
          d = {"name": creator_name.text}
          lang = creator_name.get("{http://www.w3.org/XML/1998/namespace}lang")
          if lang is not None:
            d["lang"] = lang
          creator_names.append(d)

        creators.append({
          "creator_type": "著",
          "creator_name": creator_names
        })

    subjects = None
    if record.xml.find(".//jpcoar:subject", ns) is not None:
      subjects = []
      for subject in record.xml.findall(".//jpcoar:subject", ns):
        d = {"subject": subject.text}
        lang = subject.get("{http://www.w3.org/XML/1998/namespace}lang")
        if lang is not None:
          d["lang"] = lang
        subjects.append(d)

    publishers = None
    if record.xml.find(".//dc:publisher", ns) is not None:
      publishers = []
      for publisher in record.xml.findall(".//dc:publisher", ns):
        d = {"publisher": publisher.text}
        lang = publisher.get("{http://www.w3.org/XML/1998/namespace}lang")
        if lang is not None:
          d["lang"] = lang
        publishers.append(d)

    dates = None
    if record.xml.find(".//jpcoar:jpcoar/datacite:date", ns) is not None:
      dates = []
      for date in record.xml.findall(".//jpcoar:jpcoar/datacite:date", ns):
        dates.append({
          "date": date.text,
          "date_type": date.get("dateType")
        })

    languages = resource_type = version = identifiers = None

    if record.xml.find(".//dc:language", ns) is not None:
      languages = []
      for language in record.xml.findall(".//dc:language", ns):
        languages.append(language.text)

    if record.xml.find(".//dc:type", ns) is not None:
      resource_type = record.xml.find(".//dc:type", ns).text

    if record.xml.find(".//oaire:version", ns) is not None:
      version = record.xml.find(".//oaire:version", ns).text

    source_identifiers = source_titles = None

    if record.xml.find(".//jpcoar:sourceIdentifier", ns) is not None:
      source_identifiers = []
      for source_identifier in record.xml.findall(".//jpcoar:sourceIdentifier", ns):
        source_identifiers.append({
          "identifier": source_identifier.text,
          "identifier_type": source_identifier.get("identifierType")
        })

    volume = issue = page_start = page_end = None

    if record.xml.find(".//jpcoar:volume", ns) is not None:
      volume = record.xml.find(".//jpcoar:volume", ns).text

    if record.xml.find(".//jpcoar:issue", ns) is not None:
      issue = record.xml.find(".//jpcoar:issue", ns).text

    if record.xml.find(".//jpcoar:pageStart", ns) is not None:
      page_start = record.xml.find(".//jpcoar:pageStart", ns).text

    if record.xml.find(".//jpcoar:pageEnd", ns) is not None:
      page_end = record.xml.find(".//jpcoar:pageEnd", ns).text

    files = None
    if record.xml.find(".//jpcoar:jpcoar/jpcoar:file", ns) is not None:
      files = []
      for file in record.xml.findall(".//jpcoar:jpcoar/jpcoar:file", ns):
        uri = mime_type = extents = None
        if file.find(".//jpcoar:URI", ns) is not None:
          uri = file.find(".//jpcoar:URI", ns).text
        if file.find(".//jpcoar:mimeType", ns) is not None:
          mime_type = file.find("./jpcoar:mimeType", ns).text
        if file.find(".//jpcoar:extent", ns) is not None:
          extents = []
          for extent in file.findall(".//jpcoar:extent", ns):
            extents.append(extent.text)

        if uri is not None:
          d = {"uri": uri}
          if mime_type is not None:
            d["mime_type"] = mime_type
          if extents is not None:
            d["extent"] = extents
          files.append(d)

    entry = {
      "title": titles,
      "creator": creators,
      "subject": subjects,
      "publisher": publishers,
      "date": dates,
      "type": resource_type,
      "version": version,
      "language": languages,
      "source_identifier": source_identifiers,
      "volume": volume,
      "issue": issue,
      "page_start": page_start,
      "page_end": page_end,
      "file": files
    }

    filtered_entry = {k: v for (k, v) in entry.items() if v is not None}

    if titles == []:
      # タイトルが空の場合、仮タイトルを設定
      title = "__title_is_blank__"
    else:
      # タイトルの改行コードを削除、先頭50文字のみを取得
      title = ' '.join(titles[0]['title'].splitlines())[:50]

    dir_name = f"./{export_dir}/{identifier}_{title}"
    os.makedirs(dir_name, exist_ok = True)

    # ファイルのダウンロード
    if files is not None:
      for file in files:
        if file['uri'] is not None:
          if urlparse(file['uri']).hostname == urlparse(base_url).hostname and urlparse(file['uri']).scheme == urlparse(base_url).scheme:
            with open(f"{dir_name}/{file['uri'].split('/')[-1]}", "wb") as f:
              f.write(requests.get(file['uri']).content)
              logger.debug(f"downloaded {file['uri']}")

    # メタデータの作成
    with open(f"{dir_name}/jpcoar20.yaml", "w") as file:
      yaml.safe_dump(filtered_entry, file, encoding="utf-8", allow_unicode=True, sort_keys=False)

    with open(f"{dir_name}/jpcoar20.yaml", "r+") as file:
      content = file.read()
      file.seek(0, 0)
      file.write("# yaml-language-server: $schema=../../schema/jpcoar.json\n\n" + content)

    logger.debug(f"created {dir_name}/jpcoar20.yaml")
