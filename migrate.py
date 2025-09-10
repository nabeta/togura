from sickle import Sickle
from logging import getLogger, DEBUG
from urllib.parse import urlparse
import os
import re
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
    "until": date_until,
    "ignore_deleted": True
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

    # 1 タイトル
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/1
    titles = []
    for title in record.xml.findall(".//dc:title", ns):
      d = {"title": title.text}
      lang = title.get("{http://www.w3.org/XML/1998/namespace}lang")
      if lang is not None:
        d["lang"] = lang
      titles.append(d)

    # 2 その他のタイトル
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/2
    alternatives = []
    for alternative in record.xml.findall(".//dcterms:alternative", ns):
      d = {"title": title.text}
      lang = alternative.get("{http://www.w3.org/XML/1998/namespace}lang")
      if lang is not None:
        d["lang"] = lang
      alternatives.append(d)

    # 3 作成者
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/3
    creators = []
    for creator in record.xml.findall(".//jpcoar:creator", ns):
      creators = []
      name_identifiers = []
      if creator.find("./jpcoar:nameIdentifier", ns) is not None:
        for name_identifier in creator.findall("./jpcoar:nameIdentifier", ns):
          d = {
            "identifier_scheme": name_identifier.get("nameIdentifierScheme")
          }

          if name_identifier.get("nameIdentifierURI") is not None:
            d["identifier"] = name_identifier.get("nameIdentifierURI")
          else:
            d["identifier"] = name_identifier.text
          name_identifiers.append(d)

      creator_names = []
      if creator.find("./jpcoar:creatorName", ns) is not None:
        for creator_name in creator.findall("./jpcoar:creatorName", ns):
          d = {"name": creator_name.text}
          lang = creator_name.get("{http://www.w3.org/XML/1998/namespace}lang")
          if lang is not None:
            d["lang"] = lang
          creator_names.append(d)

      creators.append({
        "name_identifier": name_identifiers,
        "creator_name": creator_names
      })

    # 4 寄与者
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/4
    contributors = []
    for contributor in record.xml.findall(".//jpcoar:contributor", ns):
      name_identifiers = []
      if contributor.find("./jpcoar:nameIdentifier", ns) is not None:
        for name_identifier in contributor.findall("./jpcoar:nameIdentifier", ns):
          d = {
            "identifier_scheme": name_identifier.get("nameIdentifierScheme")
          }

          if name_identifier.get("nameIdentifierURI") is not None:
            d["identifier"] = name_identifier.get("nameIdentifierURI")
          else:
            d["identifier"] = name_identifier.text
          name_identifiers.append(d)

      contributor_names = []
      if contributor.find("./jpcoar:contributorName", ns) is not None:
        for contributor_name in creator.findall("./jpcoar:contributorName", ns):
          d = {"name": contributor_name.text}
          lang = contributor_name.get("{http://www.w3.org/XML/1998/namespace}lang")
          if lang is not None:
            d["lang"] = lang
          contributor_names.append(d)

      contributors.append({
        "contributor_type": contributor.get("contributorType"),
        "name_identifier": name_identifiers,
        "contributor_name": contributor_names
      })

    # 5 アクセス権
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/5
    access_rights = None
    if record.xml.find(".//jpcoar:jpcoar/dcterms:accessRights", ns) is not None:
      access_rights = record.xml.find(".//jpcoar:jpcoar/dcterms:accessRights", ns).text

    # 6 権利情報
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/6
    rights = None
    if record.xml.find(".//jpcoar:jpcoar/dc:rights", ns) is not None:
      rights = []
      for right in record.xml.findall(".//jpcoar:jpcoar/dc:rights", ns):
        d = {"rights": right.text}
        rights_url = right.get("rdf:resource")
        if rights_url is not None:
          d["rights_uri"] = rights_url
        lang = right.get("{http://www.w3.org/XML/1998/namespace}lang")
        if lang is not None:
          d["lang"] = lang
        rights.append(d)

    # 7 権利者情報
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/7
    rights_holders = []
    for rights_holder in record.xml.findall(".//jpcoar:rightsHolder", ns):
      rights_holders = []
      if rights_holder.find("./jpcoar:rightsHolderName", ns) is not None:
        rights_holder_names = []
        for rights_holder_name in rights_holder.findall("./jpcoar:rightsHolderName", ns):
          d = {"name": rights_holder_name.text}
          lang = rights_holder_name.get("{http://www.w3.org/XML/1998/namespace}lang")
          if lang is not None:
            d["lang"] = lang
          rights_holder_names.append(d)

        rights_holders.append({
          "rights_holder_name": rights_holder_names
        })

    # 8 主題
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/8
    subjects = None
    if record.xml.find(".//jpcoar:subject", ns) is not None:
      subjects = []
      for subject in record.xml.findall(".//jpcoar:subject", ns):
        d = {"subject": subject.text}
        lang = subject.get("{http://www.w3.org/XML/1998/namespace}lang")
        if lang is not None:
          d["lang"] = lang
        subjects.append(d)

    # 9 内容記述
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/9
    descriptions = None
    if record.xml.find(".//datacite:description", ns) is not None:
      descriptions = []
      for description in record.xml.findall(".//datacite:description", ns):
        d = {"description": description.text}
        lang = description.get("{http://www.w3.org/XML/1998/namespace}lang")
        if lang is not None:
          d["lang"] = lang
        description_type = description.get("descriptionType")
        if description_type is not None:
          d["description_type"] = description_type
        descriptions.append(d)

    # 10 出版者
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/10
    publishers = None
    if record.xml.find(".//dc:publisher", ns) is not None:
      publishers = []
      for publisher in record.xml.findall(".//dc:publisher", ns):
        d = {"publisher": publisher.text}
        lang = publisher.get("{http://www.w3.org/XML/1998/namespace}lang")
        if lang is not None:
          d["lang"] = lang
        publishers.append(d)

    # 12 日付
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/12
    dates = None
    if record.xml.find(".//jpcoar:jpcoar/datacite:date", ns) is not None:
      dates = []
      for date in record.xml.findall(".//jpcoar:jpcoar/datacite:date", ns):
        dates.append({
          "date": date.text,
          "date_type": date.get("dateType")
        })

    # 14 言語
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/14
    languages = None
    if record.xml.find(".//dc:language", ns) is not None:
      languages = []
      for language in record.xml.findall(".//dc:language", ns):
        languages.append(language.text)

    # 15 資源タイプ
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/15
    resource_type = None
    if record.xml.find(".//dc:type", ns) is not None:
      resource_type = record.xml.find(".//dc:type", ns).text

    # 16 バージョン情報
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/16
    version = None
    if record.xml.find(".//datacite:version", ns) is not None:
      version = record.xml.find(".//datacite:version", ns).text

    # 17 出版タイプ
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/17
    text_version = None
    if record.xml.find(".//oaire:version", ns) is not None:
      text_version = record.xml.find(".//oaire:version", ns).text

    # 20 関連情報
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/20
    relations = None
    if record.xml.find(".//jpcoar:jpcoar/jpcoar:relation", ns) is not None:
      relations = []
      for relation in record.xml.findall(".//jpcoar:jpcoar/jpcoar:relation", ns):
        if relation.find(".//jpcoar:relatedIdentifier", ns) is not None:
          d = {}
          if relation.get("relationType") is not None:
            d["relation_type"] = relation.get("relationType")
          related_identifier = relation.find(".//jpcoar:relatedIdentifier", ns)
          d["related_identifier"] = {
            "identifier": related_identifier.text,
          }
          if related_identifier.get("identifierType") is not None:
            d["identifier_type"] = related_identifier.get("identifierType")
        relations.append(d)

    # 24 収録物識別子
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/24
    source_identifiers = None
    if record.xml.find(".//jpcoar:sourceIdentifier", ns) is not None:
      source_identifiers = []
      for source_identifier in record.xml.findall(".//jpcoar:sourceIdentifier", ns):
        source_identifiers.append({
          "identifier": source_identifier.text,
          "identifier_type": source_identifier.get("identifierType")
        })

    # 25 収録物名
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/25
    source_titles = None
    if record.xml.find(".//jpcoar:jpcoar/jpcoar:sourceTitle", ns) is not None:
      source_titles = []
      for source_title in record.xml.findall(".//jpcoar:jpcoar/jpcoar:sourceTitle", ns):
        d = {"source_title": source_title.text}
        lang = source_title.get("{http://www.w3.org/XML/1998/namespace}lang")
        if lang is not None:
          d["lang"] = lang
        source_titles.append(d)

    # 26 巻
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/26
    volume = None
    if record.xml.find(".//jpcoar:volume", ns) is not None:
      volume = record.xml.find(".//jpcoar:volume", ns).text

    # 27 号
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/27
    issue = None
    if record.xml.find(".//jpcoar:issue", ns) is not None:
      issue = record.xml.find(".//jpcoar:issue", ns).text

    # 28 ページ数
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/28
    num_pages = None
    if record.xml.find(".//jpcoar:numPages", ns) is not None:
      num_pages = record.xml.find(".//jpcoar:numPages", ns).text

    # 29 開始ページ
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/29
    page_start = None
    if record.xml.find(".//jpcoar:pageStart", ns) is not None:
      page_start = record.xml.find(".//jpcoar:pageStart", ns).text

    # 30 終了ページ
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/30
    page_end = None
    if record.xml.find(".//jpcoar:pageEnd", ns) is not None:
      page_end = record.xml.find(".//jpcoar:pageEnd", ns).text

    # 31 学位授与番号
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/31
    dissertation_number = None
    if record.xml.find(".//dcndl:dissertationNumber", ns) is not None:
      dissertation_number = record.xml.find(".//dcndl:dissertationNumber", ns).text

    # 37 部編名
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/37
    volume_titles = None
    if record.xml.find(".//dcndl:dissertationNumber", ns) is not None:
      volume_titles = []
      for volume_title in record.xml.findall(".//jpcoar:jpcoar/dcndl:volumeTitle", ns):
        d = {"volume_title": volume_title.text}
        lang = volume_title.get("{http://www.w3.org/XML/1998/namespace}lang")
        if lang is not None:
          d["lang"] = lang
        volume_titles.append(d)

    # 39 大きさ
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/39
    extents = None
    if record.xml.find(".//jpcoar:jpcoar/dcterms:extent", ns) is not None:
      extents = []
      for extent in record.xml.findall(".//jpcoar:jpcoar/dcterms:extent", ns):
        d = {"extent": extent.text}
        lang = extent.get("{http://www.w3.org/XML/1998/namespace}lang")
        if lang is not None:
          d["lang"] = lang
        extents.append(d)

    # 43 ファイル情報
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/43
    files = None
    if record.xml.find(".//jpcoar:jpcoar/jpcoar:file", ns) is not None:
      files = []
      for file in record.xml.findall(".//jpcoar:jpcoar/jpcoar:file", ns):
        uri = label = mime_type = file_extents = None
        if file.find(".//jpcoar:URI", ns) is not None:
          uri = file.find(".//jpcoar:URI", ns).text
        if file.find(".//jpcoar:mimeType", ns) is not None:
          mime_type = file.find("./jpcoar:mimeType", ns).text
        if file.find(".//jpcoar:extent", ns) is not None:
          file_extents = []
          for extent in file.findall(".//jpcoar:extent", ns):
            file_extents.append(extent.text)
        if file.find(".//datacite:date", ns) is not None:
          file_dates = []
          for date in record.xml.findall(".//jpcoar:jpcoar/datacite:date", ns):
            file_dates.append({
              "date": date.text,
              "date_type": date.get("dateType")
            })

        if uri is not None:
          d = {"uri": uri}
          if mime_type is not None:
            d["mime_type"] = mime_type
          if file_extents is not None:
            d["extent"] = file_extents
          if(len(file_dates) > 0):
            d["date"] = file_dates
          files.append(d)

    entry = {
      "title": titles,
      "alternative": alternatives,
      "creator": creators,
      "contributor": contributors,
      "acccess_rights": access_rights,
      "rights": rights,
      "rights_holder": rights_holders,
      "subject": subjects,
      "description": descriptions,
      "publisher": publishers,
      "date": dates,
      "language": languages,
      "type": resource_type,
      "version": version,
      "text_version": text_version,
      "relation": relations,
      "source_identifier": source_identifiers,
      "source_title": source_titles,
      "volume": volume,
      "issue": issue,
      "num_pages": num_pages,
      "page_start": page_start,
      "page_end": page_end,
      "dissertation_number": dissertation_number,
      "volume_title": volume_titles,
      "extent": extents,
      "file": files
    }

    # 値が空のキーを削除
    filtered_entry = {k: v for (k, v) in entry.items() if v is not None}

    if titles == []:
      # タイトルが空の場合、仮タイトルを設定
      title = "__title_is_blank__"
    else:
      # タイトルの改行コードを削除、先頭50文字のみを取得
      title = re.sub(r'[<>:"/\\|?*]', '_', ' '.join(titles[0]['title'].splitlines())[:50]).strip()

    dir_name = f"./{export_dir}/{identifier}_{title}"
    os.makedirs(dir_name, exist_ok = True)

    # ファイルのダウンロード
    if files is not None:
      for file in files:
        if file['uri'] is not None:
          if urlparse(file['uri']).hostname == urlparse(base_url).hostname and urlparse(file['uri']).scheme == urlparse(base_url).scheme:
            response = requests.get(file['uri'], allow_redirects=False)
            if response.status_code == requests.codes.ok:
              with open(f"{dir_name}/{file['uri'].split('/')[-1]}", "wb") as f:
                f.write(response.content)
                logger.debug(f"downloaded {file['uri']}")
            else:
              logger.debug(f"skipped {file['uri']}")

    # メタデータの作成
    with open(f"{dir_name}/jpcoar20.yaml", "w", encoding = "utf-8") as file:
      yaml.safe_dump(filtered_entry, file, encoding="utf-8", allow_unicode=True, sort_keys=False)

    with open(f"{dir_name}/jpcoar20.yaml", "r+", encoding = "utf-8") as file:
      content = file.read()
      file.seek(0, 0)
      file.write("# yaml-language-server: $schema=../../schema/jpcoar.json\n\n" + content)

    logger.debug(f"created {dir_name}/jpcoar20.yaml")
