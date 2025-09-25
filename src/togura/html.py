import datetime
import glob
import os
import shutil
from ruamel.yaml import YAML
from togura.config import Config
from jinja2 import Environment, FileSystemLoader
from logging import getLogger, DEBUG
from more_itertools import chunked
from pathlib import Path
from urllib.parse import urlparse


def filename(url):
    return os.path.basename(urlparse(url).path)


logger = getLogger(__name__)
logger.setLevel(DEBUG)

if os.path.isdir(f"{Path.cwd()}/templates"):
    template_dir = f"{Path.cwd()}/templates"
else:
    template_dir = f"{os.path.dirname(__file__)}/templates"

env = Environment(loader=FileSystemLoader(template_dir, encoding="utf8"))
env.filters["filename"] = filename
template_index = env.get_template("index.j2")
template_index_page = env.get_template("index_page.j2")
template_show = env.get_template("show.j2")
template_index.globals["now"] = datetime.datetime.now(datetime.UTC)
template_index_page.globals["now"] = datetime.datetime.now(datetime.UTC)
template_show.globals["now"] = datetime.datetime.now(datetime.UTC)


def generate(data_dir, output_dir, base_url, per_page=100):
    """HTMLを作成する"""
    conf = Config()
    yaml = YAML()

    entries = []
    for path in sorted(glob.glob(f"{data_dir}/*"), key=os.path.basename, reverse=True):
        files = []
        for file in glob.glob(f"{path}/*"):
            filename = os.path.basename(file)
            if filename == "jpcoar20.yaml":
                continue
            else:
                files.append(filename)

        with open(f"{path}/jpcoar20.yaml", encoding="utf-8") as file:
            entry = yaml.load(file)

            # タイトルが空ならスキップ
            if entry["title"] == []:
                continue

            entry["id"] = os.path.basename(path).split("_")[0]
            entries.append(entry)
            try:
                with open(
                    f"{output_dir}/{entry['id']}/ro-crate-preview.html",
                    "w",
                    encoding="utf-8",
                ) as file:
                    show_html = template_show.render(
                        entry=entry,
                        files=files,
                        base_url=conf.base_url,
                        site_name=conf.site_name,
                    )
                    file.write(show_html)
                    logger.debug(f"{entry['id']}.html")
            except FileNotFoundError:
                logger.error(f"metadata not found in {data_dir}")
                continue

    indexes = list(chunked(entries, per_page))
    for i, index_entries in enumerate(indexes):
        page = i + 1

        # ページ送りの情報を設定
        previous_page = next_page = None
        if page > 1:
            previous_page = page - 1
        if len(entries) > page * per_page:
            next_page = page + 1

        # 分割した一覧ページ（index1.htmlなど）を作成
        index_page_html = template_index_page.render(
            entries=index_entries,
            page=page,
            per_page=per_page,
            previous_page=previous_page,
            next_page=next_page,
            site_name=conf.site_name,
        )
        with open(f"{output_dir}/index{page}.html", "w", encoding="utf-8") as file:
            file.write(index_page_html)
            logger.debug(f"index{page}.html")

        # index.htmlを生成。最近の登録10件を含む
        index_html = template_index.render(
            entries=entries[0:10], total_pages=len(indexes), site_name=conf.site_name
        )
        with open(f"{output_dir}/index.html", "w", encoding="utf-8") as file:
            file.write(index_html)
            logger.debug(f"{output_dir}/index.html")

    # 画像ファイルをコピー
    shutil.copytree("templates/images", f"{output_dir}/images", dirs_exist_ok=True)
