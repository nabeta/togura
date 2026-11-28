from unittest.mock import patch

from ruamel.yaml import YAML
from typer.testing import CliRunner

from togura.cli import app

runner = CliRunner()


def run_setup(tmp_path, monkeypatch, lines, api_key=""):
    monkeypatch.chdir(tmp_path)
    with patch("togura.cli.pwinput.pwinput", return_value=api_key):
        result = runner.invoke(app, ["setup"], input="\n".join(lines) + "\n")
    assert result.exit_code == 0, result.output
    with open(tmp_path / "config.yaml", encoding="utf-8") as f:
        return YAML(typ="safe").load(f)


def test_setup_defaults(tmp_path, monkeypatch):
    config = run_setup(tmp_path, monkeypatch, ["", "", "", "", ""])
    assert config == {
        "organization": "鳥座大学",
        "site_name": "鳥座大学機関リポジトリ",
        "base_url": "https://togura.example.jp",
        "email": "",
        "openalex_api_key": "",
        "jalc_site_id": "SI/togura.dummy",
        "logo_filename": "logo.png",
    }


def test_setup_custom_values(tmp_path, monkeypatch):
    config = run_setup(
        tmp_path,
        monkeypatch,
        [
            " 例示大学 ",
            "",
            "https://repo.example.ac.jp",
            "repo@example.ac.jp",
            "SI/example",
        ],
        api_key=" secret ",
    )
    assert config == {
        "organization": "例示大学",
        # 名称の初期値は組織名から作られる
        "site_name": "例示大学機関リポジトリ",
        "base_url": "https://repo.example.ac.jp",
        "email": "repo@example.ac.jp",
        "openalex_api_key": "secret",
        "jalc_site_id": "SI/example",
        "logo_filename": "logo.png",
    }
