from pathlib import Path

from typer.testing import CliRunner

from togura.cli import app

runner = CliRunner()


def run_init(*args):
    result = runner.invoke(app, ["init", *args])
    assert result.exit_code == 0, result.output


def assert_initialized(dest: Path):
    for name in ["archive", "public/.well-known", "trash", "work"]:
        assert (dest / name).is_dir()
    assert (dest / "schema" / "jpcoar.json").is_file()
    assert (dest / ".vscode" / "settings.json").is_file()
    assert (dest / "templates" / "index.j2").is_file()
    assert (
        dest / "samples" / "01_departmental_bulletin_paper_oa" / "jpcoar20.yaml"
    ).is_file()
    assert (dest / "templates" / "head_custom.html").read_text(encoding="utf-8") == (
        dest / "templates" / "bootstrap.html"
    ).read_text(encoding="utf-8")


def test_init_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_init("repo")
    assert_initialized(tmp_path / "repo")


def test_init_current_dir_by_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_init()
    assert_initialized(tmp_path)


def test_init_keeps_head_custom(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_init("repo")
    head_custom = tmp_path / "repo" / "templates" / "head_custom.html"
    head_custom.write_text("custom", encoding="utf-8")
    run_init("repo")
    assert head_custom.read_text(encoding="utf-8") == "custom"


def test_init_creates_head_custom_in_target_dir(tmp_path, monkeypatch):
    """現在のフォルダに head_custom.html があっても、作成先には作成する"""
    monkeypatch.chdir(tmp_path)
    run_init()
    run_init("repo")
    assert (tmp_path / "repo" / "templates" / "head_custom.html").is_file()
