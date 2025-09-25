import glob
import logging
import os
import re
import shutil
from collections import Counter
from datetime import date
from ruamel.yaml import YAML
import togura.config as config
import togura.html as html
import togura.jalc as jalc
import togura.jpcoar as jpcoar
import togura.resourcesync as resourcesync
import togura.ro_crate as ro_crate

# ログ出力の設定
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def setup():
    # テンプレートのヘッダーファイルをコピーする
    if not os.path.isfile("./templates/head_custom.html"):
        shutil.copyfile("./templates/bootstrap.html", "./templates/head_custom.html")

    # 設定ファイルを作成する
    organization = (
        input("組織名を入力してください（初期値: 鳥座大学）:").strip() or "鳥座大学"
    )
    default_site_name = f"{organization}機関リポジトリ"
    default_base_url = "https://togura.example.jp"
    site_name = (
        input(
            f"機関リポジトリの名称を入力してください（初期値: {default_site_name}）:"
        ).strip()
        or default_site_name
    )
    base_url = (
        input(
            f"機関リポジトリのトップページのURLを入力してください（初期値: {default_base_url}）:"
        ).strip()
        or default_base_url
    )

    yaml = YAML()
    with open("./config.yaml", "w", encoding="utf-8") as file:
        yaml.dump(
            {
                "organization": organization,
                "site_name": site_name,
                "base_url": base_url,
                "logo_filename": "logo.png",
                "jalc_site_id": "dummy",
            },
            file,
            allow_unicode=True,
        )


def generate():
    data_dir = "./work"
    output_dir = "./public"
    base_url = config.base_url()
    yaml = YAML()

    paths = sorted(glob.glob(f"{data_dir}/*"))
    if len(paths) != len(set(paths)):
        duplicate_ids = ", ".join(Counter(paths).items())
        raise Exception(
            f"エラー: 登録番号 {duplicate_ids} が重複しています。別の番号を使用してください。"
        )

    for path in paths:
        entry_id = os.path.basename(path).split("_")[0]

        if not re.search(r"\d+", entry_id):
            raise Exception(
                f"エラー: 登録番号 {entry_id} の書式が正しくありません。半角の数字に変更してください。また、登録番号のあとに _ （アンダースコア）を入力していることを確認してください。"
            )

        with open(f"{path}/jpcoar20.yaml", encoding="utf-8") as file:
            entry = yaml.load(file)
            entry["id"] = entry_id

            # try:
            root = jpcoar.generate(entry, base_url)
            jpcoar.add_directory_file(path, entry, root, base_url)
            ro_crate.generate(path, output_dir, root)
            jalc.generate(path, output_dir, base_url)
            # except KeyError as e:
            #  logger.error(f"invalid metadata in {path}")
            #  continue

    html.generate(data_dir, output_dir, base_url)
    resourcesync.generate(output_dir, base_url)


# エンバーゴ期間が終了している資料の一覧を出力する
def check_expired_embargo(base_dir):
    yaml = YAML()
    for file in glob.glob(f"{base_dir}/*/jpcoar20.yaml"):
        with open(file, encoding="utf-8") as f:
            entry = yaml.load(f)
            if entry.get("access_rights") == "embargoed access" and entry.get("date"):
                for d in entry["date"]:
                    if d["date_type"] == "Available" and d["date"] <= date.today():
                        print(f"{d['date']}\t{file}")
