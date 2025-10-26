import glob
import os
import re
import shutil
import typer
import xml.etree.ElementTree as ET
import xmlschema
from collections import Counter
from datetime import datetime, date, timedelta
from logging import getLogger, DEBUG
from pathlib import Path
from ruamel.yaml import YAML
from importlib import metadata
from typing import Optional
from typing_extensions import Annotated
from togura.config import Config
import togura.html as html
import togura.jalc as jalc
import togura.jpcoar as jpcoar
import togura.migrate as migrate_repository
import togura.importer as importer
import togura.resourcesync as resourcesync
import togura.ro_crate as ro_crate

__version__ = metadata.version("togura")
app = typer.Typer()
logger = getLogger(__name__)
logger.setLevel(DEBUG)

work_file_app = typer.Typer(help="資料の情報のファイルを作成します")
app.add_typer(work_file_app, name="work-file")


def version_callback(value: bool):
    if value:
        print(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
):
    pass


@app.command()
def init(dir_name: Path = typer.Argument()):
    """
    Toguraのフォルダ（ディレクトリ）を設定します。
    """

    if dir_name is None:
        dest_dir = Path.cwd()
    else:
        dest_dir = dir_name

    # 初期ディレクトリを作成する
    os.makedirs(dest_dir, exist_ok=True)
    os.makedirs(f"{dest_dir}/archive", exist_ok=True)
    os.makedirs(f"{dest_dir}/public/.well-known", exist_ok=True)
    os.makedirs(f"{dest_dir}/schema", exist_ok=True)
    os.makedirs(f"{dest_dir}/trash", exist_ok=True)
    os.makedirs(f"{dest_dir}/work", exist_ok=True)
    shutil.copy(
        f"{Path(__file__).parent}/schema/jpcoar.json", f"{dest_dir}/schema/jpcoar.json"
    )
    shutil.copytree(
        f"{Path(__file__).parent}/samples", f"{dest_dir}/samples", dirs_exist_ok=True
    )
    shutil.copytree(
        f"{Path(__file__).parent}/templates",
        f"{dest_dir}/templates",
        dirs_exist_ok=True,
    )
    shutil.copytree(
        f"{Path(__file__).parent}/.vscode", f"{dest_dir}/.vscode", dirs_exist_ok=True
    )

    # テンプレートのヘッダーファイルをコピーする
    if not os.path.isfile(f"{Path.cwd()}/templates/head_custom.html"):
        shutil.copyfile(
            f"{Path(__file__).parent}/templates/bootstrap.html",
            f"{dest_dir}/templates/head_custom.html",
        )


# 設定ファイルを作成する
@app.command()
def setup():
    """
    Toguraの初期設定を行います。
    """

    organization = (
        input("組織名を入力してください（初期値: 鳥座大学）:").strip() or "鳥座大学"
    )
    default_site_name = f"{organization}機関リポジトリ"
    default_base_url = "https://togura.example.jp"
    default_jalc_site_id = "SI/togura.dummy"

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

    email = input(
        "メールアドレスを入力してください。OpenAlexのWebAPIによるメタデータの検索で使用します。空欄でもかまいませんが、メールアドレスを入力すると検索が速くなります:"
    ).strip()

    jalc_site_id = (
        input(
            f"JaLCのサイトIDを入力してください（JaLC正会員のみ。初期値: {default_jalc_site_id}）:"
        ).strip()
        or default_jalc_site_id
    )

    yaml = YAML()
    with open(f"{Path.cwd()}/config.yaml", "w", encoding="utf-8") as file:
        yaml.dump(
            {
                "organization": organization,
                "site_name": site_name,
                "base_url": base_url,
                "email": email,
                "jalc_site_id": jalc_site_id,
                "logo_filename": "logo.png",
            },
            file,
        )


@app.command()
def generate():
    """
    HTMLファイルとメタデータファイルを出力します。
    """
    data_dir = f"{Path.cwd()}/work"
    output_dir = f"{Path.cwd()}/public"
    trash_dir = f"{Path.cwd()}/trash"
    base_url = Config().base_url
    yaml = YAML()

    paths = sorted(glob.glob(f"{data_dir}/*"))
    ids = sorted([os.path.basename(path).split("_")[0] for path in paths])
    if len(paths) != len(set(ids)):
        # duplicate_ids = ", ".join(Counter(ids).items())
        for duplicate_id in Counter(ids).items():
            if duplicate_id[1] > 1:
                raise Exception(
                    f"エラー: 登録番号 {duplicate_id[0]} が重複しています。別の番号を使用してください。"
                )

    for path in paths:
        entry_id = os.path.basename(path).split("_")[0]

        if not re.search(r"\d+", entry_id):
            raise Exception(
                f"エラー: 登録番号 {entry_id} の書式が正しくありません。半角の数字に変更してください。また、登録番号のあとに _ （アンダースコア）を入力していることを確認してください。"
            )

        yaml_path = f"{path}/jpcoar20.yaml"
        with open(yaml_path, encoding="utf-8") as file:
            entry = yaml.load(file)
            entry["id"] = entry_id

            try:
                root = jpcoar.generate(entry, base_url)
                jpcoar.add_directory_file(path, entry, root, base_url)
                ro_crate.generate(path, output_dir, root)
                jalc.generate(path, output_dir, base_url)
            except KeyError as e:
                typer.echo(f"以下のメタデータの{e}にエラーがあります。")
                typer.echo(yaml_path)
                raise typer.Exit(code=1)

    html.generate(data_dir, output_dir, base_url)
    resourcesync.generate(output_dir, trash_dir, base_url)

    typer.echo("Toguraによるリポジトリの構築処理が完了しました。")
    typer.Exit(code=0)


@app.command()
def migrate(
    base_url: str = typer.Option(..., "--base-url", help="移行元のOAI-PMHのベースURL"),
    export_dir: str = typer.Option(
        ..., "--export-dir", help="ファイルの保存先のディレクトリ"
    ),
    date_from: str = typer.Option(
        datetime.strftime(datetime.today() - timedelta(days=30), "%Y-%m-%d"),
        "--date-from",
        help="移行対象の開始日",
    ),
    date_until: str = typer.Option(
        datetime.strftime(datetime.today(), "%Y-%m-%d"),
        "--date-until",
        help="移行対象の終了日",
    ),
    metadata_prefix: str = typer.Option(
        "jpcoar_1.0", "--metadata-prefix", help="移行元のmetadataPrefix"
    ),
    metadata_only: bool = typer.Option(
        False, "--metadata-only", is_flag=True, help="メタデータのみをダウンロードする"
    ),
):
    """
    他の機関リポジトリから本文ファイルとメタデータファイルをToguraに移行します。
    """

    migrate_repository.migrate(
        base_url, metadata_prefix, date_from, date_until, export_dir, metadata_only
    )

    typer.echo("Toguraによるリポジトリの移行処理が完了しました。")
    typer.Exit(code=0)


# エンバーゴ期間が終了している資料の一覧を出力する
@app.command()
def check_expired_embargo(
    work_dir: str = typer.Option(
        "work", "--dir", help="ファイルの保存先のディレクトリ"
    ),
    update: bool = typer.Option(
        False,
        "--update",
        help="メタデータを更新する",
    ),
):
    """
    エンバーゴ期間が終了している資料を出力します。
    """
    yaml = YAML()
    yaml.preserve_quotes = True
    for file in glob.glob(f"{work_dir}/*/jpcoar20.yaml"):
        with open(file, "r+", encoding="utf-8") as f:
            entry = yaml.load(f)
            if entry.get("access_rights") == "embargoed access" and entry.get("date"):
                for d in entry["date"]:
                    if d["date_type"] == "Available" and d["date"] <= date.today():
                        typer.echo(f"{d['date']}\t{file}")
                        if update is True:
                            entry["access_rights"] = "open access"
                            f.truncate(0)
                            f.seek(0)
                            yaml.dump(entry, f)
                            logger.debug(
                                f"{file}のdcterms:accessRightsをopen accessに変更しました"
                            )

    typer.Exit(code=0)


@app.command()
def validate(format: str = typer.Argument(..., help="メタデータのフォーマット")):
    """
    メタデータの出力が正しく行われているかのチェックを行います。
    """
    format_name = None
    match format:
        case "jpcoar20-xml":
            format_name = "JPCOARスキーマXMLファイル"
            schema = xmlschema.XMLSchema(
                "https://raw.githubusercontent.com/JPCOAR/schema/refs/heads/master/2.0/jpcoar_scm.xsd"
            )
            for file in glob.glob(f"{Path.cwd()}/public/*/jpcoar20.xml"):
                try:
                    schema.validate(file)
                except Exception as e:
                    typer.echo(f"以下の{format_name}にエラーがあります。")
                    typer.echo(file)
                    typer.echo(e)
                    # raise typer.Exit(code=1)
                    continue

        # case "togura-yaml":
        case "jalc-xml":
            format_name = "JaLC XMLファイル"
            for file in glob.glob(f"{Path.cwd()}/public/*/jalc.xml"):
                schema_file = None
                classification = (
                    ET.parse(file).getroot().find(".//head/content_classification").text
                )
                match classification:
                    case "01":
                        schema_file = "article"
                    case "02":
                        schema_file = "book"
                    case "03":
                        schema_file = "research_data"
                    case "04":
                        schema_file = "e-learning"
                    case "99":
                        schema_file = "general_data"
                    case _:
                        schema_file = "article"

                schema = xmlschema.XMLSchema(
                    f"{Path.cwd()}/schema/XSDスキーマ/{schema_file}.xsd"
                )
                try:
                    schema.validate(file)
                except Exception as e:
                    typer.echo(f"以下の{format_name}にエラーがあります。")
                    typer.echo(file)
                    typer.echo(e)
                    # raise typer.Exit(code=1)
                    continue

    typer.echo(f"Toguraによる{format_name}のチェックが完了しました。")
    typer.Exit(code=0)


@work_file_app.command("import")
def import_from_work_id(
    file: str = typer.Argument(..., help="資料識別子一覧のExcelファイル"),
):
    """
    資料識別子の一覧からメタデータを作成します。
    """

    importer.import_from_work_id(file)


@work_file_app.command("create-by-author-id")
def generate_work_id_from_author_id(
    author_id_file: str = typer.Argument(..., help="著者識別子一覧のExcelファイル"),
    work_id_file: str = typer.Argument(..., help="資料識別子一覧のExcelファイル"),
):
    """
    著者識別子の一覧から資料識別子の一覧を作成します。
    """

    importer.generate_work_id_from_author_id(author_id_file, work_id_file)


if __name__ == "__main__":
    app()
