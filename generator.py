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

