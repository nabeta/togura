from logging import getLogger, DEBUG
from pathlib import Path
from pyalex import Works
from requests import HTTPError
from ruamel.yaml import YAML
from urllib.parse import urlparse
import os
import pandas as pd
import pyalex
import re
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

        entry = {
            "id": row[0],
            "title": [
                {
                    "title": work["title"],
                },
            ],
            "type": work["type"],
            "date": [{"date": work["publication_date"], "date_type": "Issued"}],
            "identifier": [work["doi"]],
        }

        if work["open_access"].get("is_oa"):
            entry["access_rights"] = "open access"

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

        if work["primary_location"].get("source"):
            # 出版者
            entry["publisher"] = [
                {
                    "publisher": work["primary_location"]["source"][
                        "host_organization_name"
                    ]
                }
            ]

            # 収録物
            entry["source_title"] = [
                {"source_title": work["primary_location"]["source"]["display_name"]}
            ]

            if work["primary_location"]["source"].get("issn"):
                entry["source_identifier"] = []
                for issn in work["primary_location"]["source"]["issn"]:
                    source_identifier = {"identifier_type": "ISSN", "identifier": issn}
                    entry["source_identifier"].append(source_identifier)

        # 権利情報
        if work["primary_location"].get("license_id"):
            entry["rights"] = [{"rights": work["primary_location"]["license"]}]

        if work["biblio"]:
            entry["volume"] = work["biblio"]["volume"]
            entry["issue"] = work["biblio"]["issue"]
            entry["page_start"] = work["biblio"]["first_page"]
            entry["page_end"] = work["biblio"]["last_page"]

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
