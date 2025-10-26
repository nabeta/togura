from logging import getLogger, DEBUG
from pathlib import Path
from pyalex import Works
from requests import HTTPError
from ruamel.yaml import YAML
from urllib.parse import urlparse
import iso639
import json
import math
import numpy as np
import os
import pandas as pd
import pyalex
import re
import requests
from togura.config import Config

logger = getLogger(__name__)
logger.setLevel(DEBUG)


def import_from_work_id(file):
    yaml = YAML()

    # Excelファイルを読み込み
    df = pd.read_excel(file, index_col=0)

    # OpenAlexのAPIで使用するメールアドレスを設定
    if Config().email != "":
        pyalex.config.email = Config().email

    for row in df.iterrows():
        if row[0] is None:
            continue
        if math.isnan(row[0]):
            continue

        # DOI以外のURLをスキップ
        hostname = urlparse(row[1]["url"]).hostname
        if hostname != "doi.org":
            continue

        # OpenAlexからメタデータを取得
        try:
            work = Works()[row[1]["url"]]
        except HTTPError:
            logger.error(f"{row[1]['url']}は見つかりませんでした")
            continue

        title = re.sub(
            r'[<>:"/\\|?*]', "_", " ".join(work["title"].splitlines())[:50]
        ).strip()
        dir_name = f"{Path.cwd()}/work/{row[0]}_{title}"
        os.makedirs(dir_name, exist_ok=True)

        entry = generate_entry(row, work, dir_name)

        # メタデータの作成
        with open(f"{dir_name}/jpcoar20.yaml", "w", encoding="utf-8") as file:
            yaml.dump(entry, file)

        with open(f"{dir_name}/jpcoar20.yaml", "r+", encoding="utf-8") as file:
            content = file.read()
            file.seek(0, 0)
            file.write(
                "# yaml-language-server: $schema=../../schema/jpcoar.json\n\n" + content
            )

        logger.debug(f"created {dir_name}/jpcoar20.yaml")


def generate_work_id_from_author_id(author_id_file, work_id_file):
    # OpenAlexのAPIで使用するメールアドレスを設定
    if Config().email != "":
        pyalex.config.email = Config().email

    # Excelファイルを読み込み
    author_df = pd.read_excel(author_id_file)
    work_ids = works_from_author_id(author_df.iterrows())

    works = []
    for work_id in np.unique(work_ids):
        hostname = urlparse(work_id).hostname
        if hostname == "doi.org":
            # OpenAlexから書誌情報を取得
            try:
                work = Works()[work_id]
                best_oa_location = work.get("best_oa_location")
                license = version = None
                if best_oa_location:
                    license = best_oa_location["license"]
                    version = best_oa_location["version"]

                works.append(
                    [
                        None,
                        work["doi"],
                        work["publication_year"],
                        work["open_access"]["oa_status"],
                        work["open_access"]["oa_url"],
                        license,
                        version,
                        work["title"],
                        work["id"],
                    ]
                )
            except HTTPError:
                # OpenAlexに検索結果がなかった場合
                logger.error(f"{work_id}は見つかりませんでした")
                continue
        elif hostname == "ci.nii.ac.jp":
            # CiNii Researchから書誌情報を取得
            response = requests.get(f"{work_id}.json")
            try:
                work = json.loads(response.content)
                works.append(
                    [
                        None,
                        work_id,
                        int(work["publication"]["prism:publicationDate"][0:4]),
                        None,
                        None,
                        None,
                        None,
                        work["dc:title"][0]["@value"],
                        None,
                    ]
                )
            except json.decoder.JSONDecodeError:
                # NAIDがリゾルブできなかった場合
                logger.error(f"{work_id}は見つかりませんでした")
                continue

    df = pd.DataFrame(
        works,
        columns=[
            "id",
            "url",
            "publication_year",
            "oa_status",
            "oa_url",
            "license",
            "version",
            "title",
            "openalex_url",
        ],
    )
    df.sort_values("publication_year").to_excel(work_id_file, index=False)


def generate_entry(row, work, dir_name):
    entry = {
        "title": [
            {
                "title": work["title"],
            },
        ],
        "type": work["type"],
        "identifier": [work["doi"]],
    }

    # 著者
    entry["creator"] = []
    for author in work["authorships"]:
        creator = {"creator_name": [{"name": author["author"]["display_name"]}]}
        if author["author"].get("orcid"):
            creator["name_identifier"] = [
                {
                    "identifier_scheme": "ORCID",
                    "identifier": author["author"]["orcid"],
                }
            ]
        entry["creator"].append(creator)

    # アクセス権
    if work["open_access"].get("is_oa"):
        entry["access_rights"] = "open access"
    else:
        entry["access_rights"] = "restricted access"

    # 権利情報
    if work["primary_location"].get("license_id"):
        entry["rights"] = [{"rights": work["primary_location"]["license"]}]

    # 出版者
    if work["primary_location"].get("source"):
        entry["publisher"] = [
            {"publisher": work["primary_location"]["source"]["host_organization_name"]}
        ]

    # 日付
    if work["publication_date"]:
        entry["date"] = [{"date": work["publication_date"], "date_type": "Issued"}]
    elif work["publication_year"]:
        entry["date"] = [{"date": work["publication_year"], "date_type": "Issued"}]

    # 言語
    if work["language"]:
        entry["language"] = iso639.Language.from_part1(work["language"]).part3

    # 収録物
    if work["primary_location"].get("source"):
        entry["source_title"] = [
            {"source_title": work["primary_location"]["source"]["display_name"]}
        ]

        if work["primary_location"]["source"].get("issn"):
            entry["source_identifier"] = []
            for issn in work["primary_location"]["source"]["issn"]:
                source_identifier = {"identifier_type": "ISSN", "identifier": issn}
                entry["source_identifier"].append(source_identifier)

    # 巻号
    if work["biblio"]:
        entry["volume"] = work["biblio"]["volume"]
        entry["issue"] = work["biblio"]["issue"]
        entry["page_start"] = work["biblio"]["first_page"]
        entry["page_end"] = work["biblio"]["last_page"]

    return entry


def works_from_author_id(rows):
    work_ids = []
    for row in rows:
        # DOI以外のURLをスキップ
        hostname = urlparse(row[1]["url"]).hostname
        if hostname == "orcid.org":
            work_ids += orcid_works(row)
        elif hostname == "researchmap.jp":
            work_ids += researchmap_works(row)
        else:
            continue

    return work_ids


def orcid_works(row):
    work_ids = []
    # OpenAlexのAPIで使用するメールアドレスを設定
    if Config().email != "":
        pyalex.config.email = Config().email

    works = Works().filter(authorships={"author": {"orcid": row[1]["url"]}}).get()
    for work in works:
        if work["doi"] is None:
            continue
        work_ids.append(work["doi"])

    return work_ids


def researchmap_works(row):
    work_ids = []
    response = requests.get(f"https://api.researchmap.jp{urlparse(row[1]['url']).path}")
    for graph in json.loads(response.content)["@graph"]:
        if graph["@type"] != "published_papers":
            continue
        for paper in graph["items"]:
            if paper["identifiers"].get("doi"):
                work_ids.append(f"https://doi.org/{paper['identifiers']['doi'][0]}")
            elif paper["identifiers"].get("cinii_na_id"):
                work_ids.append(
                    f"https://ci.nii.ac.jp/naid/{paper['identifiers']['cinii_na_id'][0]}"
                )

    return work_ids
