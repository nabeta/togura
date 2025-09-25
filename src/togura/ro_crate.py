import os
import glob
import mimetypes
import tempfile
import xml.etree.ElementTree as ET
from ruamel.yaml import YAML
from rocrate.rocrate import ROCrate
from rocrate.model.person import Person
from logging import getLogger, DEBUG

logger = getLogger(__name__)
logger.setLevel(DEBUG)


def generate(data_dir, output_dir, root):
    """RO-Crateのディレクトリを出力する"""
    entry_id = os.path.basename(data_dir).split("_")[0]
    yaml = YAML()

    with open(f"{data_dir}/jpcoar20.yaml", encoding="utf-8") as file:
        entry = yaml.load(file)

    crate = ROCrate(gen_preview=False)
    crate.name = entry["title"][0]["title"]

    # ファイルを追加
    for file in glob.glob(f"{data_dir}/*"):
        filename = os.path.basename(file)
        if filename == "jpcoar20.yaml":
            continue

        crate.add_file(
            file,
            properties={
                "contentSize": str(os.path.getsize(file)),
                "encodingFormat": mimetypes.guess_type(file)[0],
            },
        )

    # 作成者を追加
    if entry.get("creator"):
        for creator in entry["creator"]:
            if len(creator["creator_name"]) > 0:
                crate.add(
                    Person(
                        crate, properties={"name": creator["creator_name"][0]["name"]}
                    )
                )

    # JPCOARスキーマのXMLファイルを追加
    with tempfile.TemporaryDirectory() as tempdir:
        with open(f"{tempdir}/jpcoar20.xml", "w", encoding="utf-8") as xml_file:
            ET.indent(root, space="\t", level=0)
            xml_file.write(ET.tostring(root, encoding="unicode", xml_declaration=True))
            xml_file.seek(0)
            crate.add_file(
                xml_file.name,
                dest_path="jpcoar20.xml",
                properties={
                    "contentSize": str(os.path.getsize(xml_file.name)),
                    "encodingFormat": "application/xml",
                },
            )

        # ディレクトリを出力
        crate_dir = f"public/{entry_id}"
        crate.write(crate_dir)
