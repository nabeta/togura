import shutil
from pathlib import Path

import pytest
from ruamel.yaml import YAML
from typer.testing import CliRunner

from togura.cli import app

runner = CliRunner()
SAMPLE_YAML = (
    Path(__file__).resolve().parent.parent
    / "src/togura/samples/01_departmental_bulletin_paper_oa/jpcoar20.yaml"
)


@pytest.fixture
def project(tmp_path, monkeypatch):
    """init済みで設定ファイルのあるToguraのフォルダ"""
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app, ["init"]).exit_code == 0
    with open(tmp_path / "config.yaml", "w", encoding="utf-8") as f:
        YAML().dump(
            {
                "organization": "鳥座大学",
                "site_name": "鳥座大学機関リポジトリ",
                "base_url": "https://togura.example.jp",
                "email": "",
                "jalc_site_id": "SI/togura.dummy",
                "logo_filename": "logo.png",
            },
            f,
        )
    return tmp_path


def add_work(project: Path, dir_name: str) -> Path:
    work = project / "work" / dir_name
    work.mkdir()
    shutil.copy(SAMPLE_YAML, work / "jpcoar20.yaml")
    return work


def test_generate(project):
    add_work(project, "1_bulletin")
    add_work(project, "20_bulletin")
    result = runner.invoke(app, ["generate"])
    assert result.exit_code == 0, result.output
    assert "構築処理が完了しました" in result.output
    for entry_id in ["1", "20"]:
        for name in [
            "jpcoar20.xml",
            "jalc.xml",
            "ro-crate-metadata.json",
            "ro-crate-preview.html",
        ]:
            assert (project / "public" / entry_id / name).is_file()
    for name in ["index.html", "resourcelist.xml", "changelist.xml"]:
        assert (project / "public" / name).is_file()


@pytest.mark.parametrize("dir_name", ["abc_bulletin", "1a_bulletin", "１_bulletin"])
def test_generate_invalid_entry_id(project, dir_name):
    add_work(project, "1_bulletin")
    add_work(project, dir_name)
    result = runner.invoke(app, ["generate"])
    assert result.exit_code == 1
    assert "の書式が正しくありません" in result.output
    # 登録番号の確認は出力の前に行う
    assert not (project / "public" / "1").exists()


def test_generate_duplicate_entry_id(project):
    add_work(project, "1_bulletin")
    add_work(project, "1_other")
    result = runner.invoke(app, ["generate"])
    assert result.exit_code == 1
    assert "登録番号 1 が重複しています" in result.output
    assert not (project / "public" / "1").exists()


def test_generate_missing_metadata(project):
    work = add_work(project, "1_bulletin")
    yaml = YAML()
    with open(work / "jpcoar20.yaml", encoding="utf-8") as f:
        entry = yaml.load(f)
    del entry["type"]
    with open(work / "jpcoar20.yaml", "w", encoding="utf-8") as f:
        yaml.dump(entry, f)
    result = runner.invoke(app, ["generate"])
    assert result.exit_code == 1
    assert "'type'にエラーがあります" in result.output
