import glob
import re
import shutil
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date, datetime, timedelta
from importlib import metadata
from logging import DEBUG, getLogger
from pathlib import Path
from typing import Annotated

import pwinput
import typer
import xmlschema
from ruamel.yaml import YAML

import togura.migrate as migrate_repository
from togura import html, importer, jalc, jpcoar, resourcesync, ro_crate
from togura.config import Config, write_config

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
        bool | None,
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
):
    pass


PACKAGE_DIR = Path(__file__).parent
# init で作成する空のディレクトリ
INIT_DIRS = ["archive", "public/.well-known", "schema", "trash", "work"]
# init でパッケージからコピーするディレクトリ
INIT_COPY_DIRS = ["samples", "templates", ".vscode"]


@app.command()
def init(
    dir_name: Annotated[
        Path, typer.Argument(help="作成するフォルダ。省略時は現在のフォルダ")
    ] = Path("."),
):
    """
    Toguraのフォルダ（ディレクトリ）を設定します。
    """

    # 初期ディレクトリを作成する
    for name in INIT_DIRS:
        (dir_name / name).mkdir(parents=True, exist_ok=True)

    shutil.copy(PACKAGE_DIR / "schema" / "jpcoar.json", dir_name / "schema")
    for name in INIT_COPY_DIRS:
        shutil.copytree(PACKAGE_DIR / name, dir_name / name, dirs_exist_ok=True)

    # テンプレートのヘッダーファイルをコピーする。編集済みのファイルは上書きしない
    head_custom = dir_name / "templates" / "head_custom.html"
    if not head_custom.exists():
        shutil.copyfile(PACKAGE_DIR / "templates" / "bootstrap.html", head_custom)


DEFAULT_ORGANIZATION = "鳥座大学"
DEFAULT_BASE_URL = "https://togura.example.jp"
DEFAULT_JALC_SITE_ID = "SI/togura.dummy"
DEFAULT_LOGO_FILENAME = "logo.png"


def ask(message: str, default: str = "") -> str:
    """入力を受け付け、空欄の場合は初期値を返す"""
    return input(message).strip() or default


@app.command()
def setup():
    """
    Toguraの初期設定を行います。
    """

    organization = ask(
        f"組織名を入力してください（初期値: {DEFAULT_ORGANIZATION}）:",
        DEFAULT_ORGANIZATION,
    )
    default_site_name = f"{organization}機関リポジトリ"
    site_name = ask(
        f"機関リポジトリの名称を入力してください（初期値: {default_site_name}）:",
        default_site_name,
    )
    base_url = ask(
        f"機関リポジトリのトップページのURLを入力してください（初期値: {DEFAULT_BASE_URL}）:",
        DEFAULT_BASE_URL,
    )
    email = ask("機関リポジトリの連絡担当者のメールアドレスを入力してください。空欄でもかまいません:")
    # APIキーは画面に表示しない
    openalex_api_key = pwinput.pwinput(
        "OpenAlexのWebAPIキーを入力してください。OpenAlexからの書誌情報の取得を行わない場合は、空欄のままでかまいません:",
        mask="*",
    ).strip()
    jalc_site_id = ask(
        f"JaLCのサイトIDを入力してください（JaLC正会員のみ。初期値: {DEFAULT_JALC_SITE_ID}）:",
        DEFAULT_JALC_SITE_ID,
    )

    write_config(
        Path.cwd() / "config.yaml",
        {
            "organization": organization,
            "site_name": site_name,
            "base_url": base_url,
            "email": email,
            "openalex_api_key": openalex_api_key,
            "jalc_site_id": jalc_site_id,
            "logo_filename": DEFAULT_LOGO_FILENAME,
        },
    )


def entry_id_of(path: Path) -> str:
    """資料のフォルダ名から登録番号を取り出す。フォルダ名は「登録番号_任意の文字列」"""
    return path.name.split("_")[0]


def check_entry_ids(paths: list[Path]) -> None:
    """登録番号の書式と重複を確認し、問題があればエラーを表示して終了する"""
    for path in paths:
        entry_id = entry_id_of(path)
        if not re.fullmatch(r"[0-9]+", entry_id):
            typer.echo(
                f"エラー: 登録番号 {entry_id} の書式が正しくありません。半角の数字に変更してください。また、登録番号のあとに _ （アンダースコア）を入力していることを確認してください。",
                err=True,
            )
            raise typer.Exit(code=1)

    counts = Counter(entry_id_of(path) for path in paths)
    for entry_id, count in counts.items():
        if count > 1:
            typer.echo(
                f"エラー: 登録番号 {entry_id} が重複しています。別の番号を使用してください。",
                err=True,
            )
            raise typer.Exit(code=1)


@app.command()
def generate():
    """
    HTMLファイルとメタデータファイルを出力します。
    """
    data_dir = Path.cwd() / "work"
    output_dir = Path.cwd() / "public"
    trash_dir = Path.cwd() / "trash"
    base_url = Config().base_url
    yaml = YAML()

    paths = sorted(data_dir.glob("*"))
    # 出力を始める前に、すべての資料の登録番号を確認する
    check_entry_ids(paths)

    for path in paths:
        yaml_path = path / "jpcoar20.yaml"
        with open(yaml_path, encoding="utf-8") as file:
            entry = yaml.load(file)
        entry["id"] = entry_id_of(path)

        try:
            root = jpcoar.generate(entry, base_url)
            jpcoar.add_directory_file(path, entry, root, base_url)
            ro_crate.generate(path, output_dir, root)
            jalc.generate(path, output_dir, base_url)
        except KeyError as e:
            typer.echo(f"以下のメタデータの{e}にエラーがあります。", err=True)
            typer.echo(yaml_path, err=True)
            raise typer.Exit(code=1) from e

    html.generate(data_dir, output_dir, base_url)
    resourcesync.generate(output_dir, trash_dir, base_url)

    typer.echo("Toguraによるリポジトリの構築処理が完了しました。")


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
