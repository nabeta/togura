import datetime
import glob
import os
import shutil
import yaml
import config
from jinja2 import Environment, FileSystemLoader
from logging import getLogger, DEBUG
from more_itertools import chunked

logger = getLogger(__name__)
logger.setLevel(DEBUG)

def generate(data_dir, output_dir, base_url, per_page = 100):
  """HTMLを作成する"""
  env = Environment(loader=FileSystemLoader('./', encoding='utf8'))
  template_index = env.get_template('templates/index.j2')
  template_index_page = env.get_template('templates/index_page.j2')
  template_show = env.get_template('templates/show.j2')
  template_show.globals['now'] = datetime.datetime.now(datetime.UTC)
  template_index_page.globals['now'] = datetime.datetime.now(datetime.UTC)
  template_index.globals['now'] = datetime.datetime.now(datetime.UTC)

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
      entry["id"] = os.path.basename(path).split("_")[0][:2]
      entries.append(entry)
      with open(f"{output_dir}/{entry['id']}/ro-crate-preview.html", "w") as file:
        show_html = template_show.render(entry = entry, files = files, base_url = config.base_url(), site_name = config.site_name())
        file.write(show_html)
        logger.debug(f"{entry['id']}.html")

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
    index_page_html = template_index_page.render(entries = index_entries, page = page, per_page = per_page, previous_page = previous_page, next_page = next_page, site_name = config.site_name())
    with open(f"{output_dir}/index{page}.html", "w") as file:
      file.write(index_page_html)
      logger.debug(f"index{page}.html")

    # index.htmlを生成。最近の登録10件を含む
    index_html = template_index.render(entries = entries[0:10], total_pages = len(indexes), site_name = config.site_name())
    with open(f"{output_dir}/index.html", "w") as file:
      file.write(index_html)
      logger.debug(f"index.html")

  # 画像ファイルをコピー
  shutil.copytree("templates/images", f"{output_dir}/images", dirs_exist_ok = True)
