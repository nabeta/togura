import os
import glob
import yaml
import datetime
import config
from jinja2 import Environment, FileSystemLoader
from logging import getLogger, DEBUG

logger = getLogger(__name__)
logger.setLevel(DEBUG)

def generate(data_dir, output_dir, base_url):
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
      entry["id"] = os.path.basename(path).split("_")[0][:2]
      entries.append(entry)
      with open(f"{output_dir}/{entry['id']}/ro-crate-preview.html", "w") as file:
        template_show.globals['now'] = datetime.datetime.now(datetime.UTC)
        show_html = template_show.render(entry = entry, files = files, base_url = config.base_url(), site_name = config.site_name())
        file.write(show_html)
        logger.debug(f"{entry['id']}.html")

  template_index.globals['now'] = datetime.datetime.now(datetime.UTC)
  index_html = template_index.render(entries = entries, site_name = config.site_name())
  with open(f"{output_dir}/index.html", "w") as file:
    file.write(index_html)
    logger.debug("index.html")
