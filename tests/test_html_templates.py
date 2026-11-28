"""src/togura/templates/*.j2 のテスト"""

import datetime
import shutil
from html.parser import HTMLParser
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader
from ruamel.yaml import YAML

from togura import html

PACKAGE_DIR = Path(__file__).parent.parent / "src" / "togura"
TEMPLATE_DIR = PACKAGE_DIR / "templates"
SAMPLE_DIRS = sorted(p for p in (PACKAGE_DIR / "samples").iterdir() if p.is_dir())
NOW = datetime.datetime(2026, 1, 2, 3, 4, 5, tzinfo=datetime.UTC)
BASE_URL = "https://repository.example.jp"
SITE_NAME = "テストリポジトリ"

VOID_ELEMENTS = {"meta", "link", "img", "br", "hr", "input"}


class Node:
    def __init__(self, tag, attrs=None, parent=None):
        self.tag = tag
        self.attrs = dict(attrs or [])
        self.parent = parent
        self.children = []
        self.texts = []

    def elements(self):
        return [c for c in self.children if isinstance(c, Node)]

    def iter(self, tag=None):
        for child in self.elements():
            if tag is None or child.tag == tag:
                yield child
            yield from child.iter(tag)

    def text(self):
        parts = []
        for child in self.children:
            parts.append(child.text() if isinstance(child, Node) else child)
        return " ".join(" ".join(parts).split())


class TreeBuilder(HTMLParser):
    """終了タグの対応を検証しながらDOMツリーを組み立てる"""

    def __init__(self):
        super().__init__()
        self.root = Node("#document")
        self.current = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in VOID_ELEMENTS:
            self.current = node

    def handle_endtag(self, tag):
        assert self.current.tag == tag, (
            f"</{tag}> が <{self.current.tag}> を閉じようとしています"
        )
        self.current = self.current.parent

    def handle_data(self, data):
        self.current.children.append(data)


def parse(source):
    builder = TreeBuilder()
    builder.feed(source)
    builder.close()
    assert builder.current is builder.root, (
        f"<{builder.current.tag}> が閉じられていません"
    )
    return builder.root


@pytest.fixture(scope="module")
def env():
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR, encoding="utf8"))
    env.filters["filename"] = html.filename
    env.globals["now"] = NOW
    return env


def load_sample(path):
    with open(path / "jpcoar20.yaml", encoding="utf-8") as file:
        entry = YAML().load(file)
    entry["id"] = path.name.split("_")[0]
    return entry


def render_show(env, entry, files=()):
    source = env.get_template("show.j2").render(
        entry=entry, files=list(files), base_url=BASE_URL, site_name=SITE_NAME
    )
    return parse(source)


def minimal_entry(**fields):
    entry = {
        "id": "99",
        "type": "article",
        "title": [{"lang": "ja", "title": "最小のタイトル"}],
        "identifier": [f"{BASE_URL}/99/ro-crate-preview.html"],
    }
    entry.update(fields)
    return entry


def fields(doc):
    """詳細画面の項目名と、その値のdd要素の組を返す"""
    result = []
    for dl in doc.iter("dl"):
        children = dl.elements()
        for dt, dd in zip(children[::2], children[1::2]):
            result.append((dt.text(), dd))
    return result


def field_values(doc, label):
    return [dd for name, dd in fields(doc) if name == label]


def assert_dl_structure(doc):
    """すべてのdlの子要素がdtとddの組の繰り返しになっていること"""
    for dl in doc.iter("dl"):
        tags = [child.tag for child in dl.elements()]
        assert tags == ["dt", "dd"] * (len(tags) // 2), tags


# 詳細画面（show.j2）: すべてのサンプル


@pytest.mark.parametrize("sample", SAMPLE_DIRS, ids=lambda p: p.name)
def test_show_renders_sample(env, sample):
    entry = load_sample(sample)
    doc = render_show(env, entry, files=["fulltext.pdf"])

    main_title = entry["title"][0]["title"]
    assert next(doc.iter("title")).text() == f"{main_title} | {SITE_NAME}"
    assert next(doc.iter("h1")).text() == main_title
    assert_dl_structure(doc)

    # タイトルはすべての言語の値が言語ごとに表示される
    # （カタログにもタイトルがあるため、最初のタイトルを確認する）
    titles = field_values(doc, "タイトル")[0]
    assert [dt.text() for dt in titles.iter("dt")] == [
        t["lang"] for t in entry["title"]
    ]
    assert [dd.text() for dd in titles.iter("dd")] == [
        " ".join(t["title"].split()) for t in entry["title"]
    ]

    # 作成者ごとに枠が表示される
    assert len(field_values(doc, "作成者")) == len(entry.get("creator") or [])

    # 所属の見出しは、所属があるときだけ表示される
    for dd in field_values(doc, "作成者所属") + field_values(doc, "寄与者所属"):
        assert dd.text() != ""

    # 作業ディレクトリのファイルへのリンク
    hrefs = [a.attrs.get("href") for a in doc.iter("a")]
    assert "./fulltext.pdf" in hrefs

    # JaLC XMLへのリンクはDOIを登録しているときだけ表示される
    assert ("jalc.xml" in hrefs) == bool(entry.get("identifier_registration"))
    assert "jpcoar20.xml" in hrefs
    assert "ro-crate-metadata.json" in hrefs

    assert f"最終更新日: {NOW}" in doc.text()


def test_show_relative_links(env):
    doc = render_show(env, minimal_entry())
    hrefs = [a.attrs.get("href") for a in doc.iter("a")]
    assert "../index.html" in hrefs
    assert next(doc.iter("img")).attrs["src"] == "../images/logo.png"


# 詳細画面（show.j2）: 個別の項目


def test_show_omits_optional_fields(env):
    doc = render_show(env, minimal_entry())
    labels = [name for name, _ in fields(doc)]
    for label in [
        "その他のタイトル",
        "作成者",
        "寄与者",
        "アクセス権",
        "権利情報",
        "主題",
        "内容記述",
        "出版者",
        "日付",
        "言語",
        "ID登録",
        "関連情報",
        "助成情報",
        "収録物識別子",
        "収録物名",
        "学位授与番号",
        "権利者情報",
        "バージョン情報",
        "出版者情報",
        "日付（リテラル）",
        "時間的範囲",
        "位置情報",
        "ページ数",
        "会議記述",
        "版",
        "部編名",
        "原文の言語",
        "大きさ",
        "物理的形態",
        "所蔵機関",
        "データセットシリーズ",
        "カタログ",
    ]:
        assert label not in labels
    assert "jalc.xml" not in [a.attrs.get("href") for a in doc.iter("a")]


def test_show_title_has_no_orphan_dd(env):
    entry = minimal_entry(
        title=[
            {"lang": "ja", "title": "日本語のタイトル"},
            {"lang": "en", "title": "English title"},
        ],
        alternative=[{"lang": "en", "title": "Alternative title"}],
    )
    doc = render_show(env, entry)
    assert_dl_structure(doc)

    [titles] = field_values(doc, "タイトル")
    assert [
        (dt.text(), dd.text()) for dt, dd in zip(titles.iter("dt"), titles.iter("dd"))
    ] == [
        ("ja", "日本語のタイトル"),
        ("en", "English title"),
    ]
    [alternative] = field_values(doc, "その他のタイトル")
    assert alternative.text() == "en Alternative title"


@pytest.mark.parametrize(
    "key, name_key, label, affiliation_label",
    [
        ("creator", "creator_name", "作成者", "作成者所属"),
        ("contributor", "contributor_name", "寄与者", "寄与者所属"),
    ],
)
def test_show_affiliation_heading(env, key, name_key, label, affiliation_label):
    entry = minimal_entry(
        **{
            key: [
                {"name_identifier": [], name_key: [{"lang": "ja", "name": "所属なし"}]},
                {
                    name_key: [{"lang": "ja", "name": "所属あり"}],
                    "affiliation": [
                        {
                            "name_identifier": [
                                {
                                    "identifier_scheme": "ROR",
                                    "identifier": "https://ror.org/x",
                                }
                            ],
                            "affiliation_name": [{"lang": "ja", "name": "テスト大学"}],
                        }
                    ],
                },
            ]
        }
    )
    doc = render_show(env, entry)
    assert_dl_structure(doc)

    without_affiliation, with_affiliation = field_values(doc, label)
    assert affiliation_label not in without_affiliation.text()
    assert affiliation_label in with_affiliation.text()

    [affiliation] = field_values(doc, affiliation_label)
    assert affiliation.text() == "ROR https://ror.org/x ja テスト大学"


def test_show_orcid_is_linked(env):
    orcid = "https://orcid.org/0000-0002-1825-0097"
    entry = minimal_entry(
        creator=[
            {
                "creator_name": [{"lang": "ja", "name": "著者"}],
                "name_identifier": [
                    {"identifier_scheme": "ORCID", "identifier": orcid},
                    {"identifier_scheme": "e-Rad_Researcher", "identifier": "12345678"},
                ],
            }
        ]
    )
    doc = render_show(env, entry)
    [creator] = field_values(doc, "作成者")
    assert [a.attrs["href"] for a in creator.iter("a")] == [orcid]
    assert "e-Rad_Researcher 12345678" in creator.text()


def test_show_funding_reference(env):
    entry = minimal_entry(
        funding_reference=[
            {
                "funder_identifier": {
                    "funder_identifier_type": "Crossref Funder",
                    "funder_identifier": "https://doi.org/10.13039/501100001691",
                },
                "funder_name": [{"lang": "ja", "funder_name": "日本学術振興会"}],
                "award_number": {
                    "award_number_type": "JGN",
                    "award_number": "JP12345678",
                    "award_uri": "https://kaken.nii.ac.jp/grant/KAKENHI-PROJECT-12345678/",
                },
                "award_title": [{"lang": "ja", "award_title": "研究課題名"}],
            },
            {"award_number": {"award_number": "ABC-1"}, "funder_name": []},
        ]
    )
    doc = render_show(env, entry)
    assert_dl_structure(doc)

    [funding] = field_values(doc, "助成情報")
    links = [(a.attrs["href"], a.text()) for a in funding.iter("a")]
    assert links == [
        ("https://kaken.nii.ac.jp/grant/KAKENHI-PROJECT-12345678/", "JP12345678")
    ]
    text = funding.text()
    assert "Crossref Funder https://doi.org/10.13039/501100001691" in text
    assert "ja 日本学術振興会" in text
    assert "ja 研究課題名" in text
    assert "ABC-1" in text


def test_show_identifier_registration(env):
    entry = minimal_entry(
        identifier_registration={
            "identifier": "10.12345/abc",
            "identifier_type": "JaLC",
        }
    )
    doc = render_show(env, entry)
    [registration] = field_values(doc, "ID登録")
    [link] = registration.iter("a")
    assert link.attrs["href"] == link.text() == "https://doi.org/10.12345/abc"
    assert "jalc.xml" in [a.attrs.get("href") for a in doc.iter("a")]


def test_show_source_title(env):
    entry = minimal_entry(
        source_title=[{"lang": "ja", "source_title": "紀要"}],
        volume="10",
        issue="2",
        page_start="1",
        page_end="20",
    )
    doc = render_show(env, entry)
    [source] = field_values(doc, "収録物名")
    assert source.text() == "ja 紀要. vol. 10, issue 2. 1-20."


def test_show_dissertation(env):
    entry = minimal_entry(
        dissertation_number="甲第1号",
        degree_name=[{"lang": "ja", "degree_name": "博士（文学）"}],
        date_granted="2025-03-25",
        degree_grantor=[
            {"degree_grantor_name": [{"lang": "ja", "name": "テスト大学"}]},
            {"degree_grantor_name": [{"lang": "en", "name": "Test University"}]},
        ],
    )
    doc = render_show(env, entry)
    assert_dl_structure(doc)

    assert [dd.text() for dd in field_values(doc, "学位授与番号")] == ["甲第1号"]
    assert [dd.text() for dd in field_values(doc, "学位名")] == ["ja 博士（文学）"]
    assert [dd.text() for dd in field_values(doc, "学位授与年月日")] == ["2025-03-25"]
    assert [dd.text() for dd in field_values(doc, "学位授与機関")] == [
        "ja テスト大学 en Test University"
    ]


def test_show_file_information(env):
    entry = minimal_entry(
        file=[
            {
                "uri": "https://example.jp/files/a.pdf",
                "mime_type": "application/pdf",
                "extent": ["1 MB", "10 pages"],
                "date": [{"date_type": "Available", "date": "2025-04-01"}],
                "version": "1.0",
            }
        ]
    )
    doc = render_show(env, entry, files=["b.csv"])
    [files] = field_values(doc, "ファイル情報")
    text = files.text()
    assert "ファイル形式 application/pdf" in text
    assert "大きさ 1 MB 10 pages" in text
    assert "Available 2025-04-01" in text
    assert "バージョン 1.0" in text
    assert [a.attrs["href"] for a in files.iter("a")] == [
        "https://example.jp/files/a.pdf",
        "./b.csv",
    ]
    assert f"{BASE_URL}/99/b.csv" in text


# 一覧ページ（index.j2・index_page.j2）


@pytest.fixture(scope="module")
def sample_entries():
    return [load_sample(path) for path in SAMPLE_DIRS]


def entry_links(doc):
    return [
        a.attrs["href"]
        for a in doc.iter("a")
        if a.attrs.get("href", "").endswith("/ro-crate-preview.html")
    ]


def test_index(env, sample_entries):
    source = env.get_template("index.j2").render(
        entries=sample_entries, total_pages=3, site_name=SITE_NAME
    )
    doc = parse(source)

    assert next(doc.iter("title")).text() == SITE_NAME
    assert SITE_NAME in next(doc.iter("h1")).text()
    hrefs = [a.attrs.get("href") for a in doc.iter("a")]
    assert [h for h in hrefs if h.startswith("index") and h != "index.html"] == [
        "index1.html",
        "index2.html",
        "index3.html",
    ]
    assert entry_links(doc) == [
        f"{e['id']}/ro-crate-preview.html" for e in sample_entries
    ]
    assert "resourcelist.xml" in hrefs
    assert f"最終更新日: {NOW}" in doc.text()

    items = list(doc.iter("li"))
    for entry, item in zip(sample_entries, items, strict=True):
        assert f"[{entry['type']}]" in item.text()
        assert " ".join(entry["title"][0]["title"].split()) in item.text()


def test_index_entry_dates(env):
    entry = minimal_entry(
        creator=[
            {"creator_name": []},
            {"creator_name": [{"lang": "ja", "name": "著者"}]},
        ],
        file=[{"date": [{"date_type": "Available", "date": "2025-04-01"}]}],
    )
    source = env.get_template("index.j2").render(
        entries=[entry], total_pages=1, site_name=SITE_NAME
    )
    [item] = parse(source).iter("li")
    assert item.text() == "99 [article] 著者 . 最小のタイトル Available: 2025-04-01"


@pytest.mark.parametrize(
    "page, previous_page, next_page",
    [(1, None, 2), (2, 1, 3), (3, 2, None)],
)
def test_index_page(env, sample_entries, page, previous_page, next_page):
    source = env.get_template("index_page.j2").render(
        entries=sample_entries[:5],
        page=page,
        per_page=5,
        previous_page=previous_page,
        next_page=next_page,
        site_name=SITE_NAME,
    )
    doc = parse(source)

    links = {a.text(): a.attrs.get("href") for a in doc.iter("a")}
    assert links["トップページ"] == "index.html"
    assert links.get("前のページ") == (previous_page and f"index{previous_page}.html")
    assert links.get("次のページ") == (next_page and f"index{next_page}.html")
    assert f"{(page - 1) * 5 + 1}件目から{page * 5}件目まで" in doc.text()
    assert entry_links(doc) == [
        f"{e['id']}/ro-crate-preview.html" for e in sample_entries[:5]
    ]
    assert next(doc.iter("img")).attrs["src"] == "./images/logo.png"


# サイト全体の生成（html.generate）


class StubConfig:
    site_name = SITE_NAME
    base_url = BASE_URL


def test_generate(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "public"
    for path in SAMPLE_DIRS[:3]:
        shutil.copytree(path, data_dir / path.name)
    (data_dir / SAMPLE_DIRS[0].name / "fulltext.pdf").write_bytes(b"%PDF")
    monkeypatch.setattr(html, "Config", StubConfig)

    html.generate(data_dir, output_dir, BASE_URL, per_page=2)

    assert (output_dir / "images" / "logo.png").is_file()
    assert (output_dir / "index.html").is_file()
    assert (output_dir / "index1.html").is_file()
    assert (output_dir / "index2.html").is_file()
    assert not (output_dir / "index3.html").exists()

    # 一覧は新しい順（IDの降順）
    index1 = parse((output_dir / "index1.html").read_text(encoding="utf-8"))
    assert entry_links(index1) == [
        "02/ro-crate-preview.html",
        "01/ro-crate-preview.html",
    ]

    show = (output_dir / "00" / "ro-crate-preview.html").read_text(encoding="utf-8")
    doc = parse(show)
    assert "./fulltext.pdf" in [a.attrs.get("href") for a in doc.iter("a")]
    assert "./jpcoar20.yaml" not in [a.attrs.get("href") for a in doc.iter("a")]
    assert_dl_structure(doc)


# 詳細画面（show.j2）: これまで表示していなかった項目


@pytest.mark.parametrize(
    ("label", "fields_", "expected"),
    [
        ("バージョン情報", {"version": "1.01"}, "1.01"),
        (
            "日付（リテラル）",
            {"dcterms_date": [{"date": "安永6-文政13", "lang": "ja"}]},
            "ja 安永6-文政13",
        ),
        (
            "時間的範囲",
            {"temporal": [{"temporal": "江戸時代", "lang": "ja"}]},
            "ja 江戸時代",
        ),
        ("ページ数", {"num_pages": 24}, "24"),
        ("版", {"edition": [{"edition": "第2版", "lang": "ja"}]}, "ja 第2版"),
        (
            "部編名",
            {"volume_title": [{"volume_title": "前編", "lang": "ja"}]},
            "ja 前編",
        ),
        ("原文の言語", {"original_language": ["jpn", "eng"]}, "jpn eng"),
        ("大きさ", {"extent": [{"extent": "34冊", "lang": "ja"}]}, "ja 34冊"),
        ("物理的形態", {"format": [{"format": "袋綴"}]}, "袋綴"),
        ("データセットシリーズ", {"dataset_series": True}, "True"),
        ("データセットシリーズ", {"dataset_series": False}, "False"),
    ],
)
def test_show_simple_fields(env, label, fields_, expected):
    doc = render_show(env, minimal_entry(**fields_))
    assert_dl_structure(doc)
    assert [dd.text() for dd in field_values(doc, label)] == [expected]


def test_show_rights_holder(env):
    entry = minimal_entry(
        rights_holder=[
            {
                "name_identifier": [
                    {
                        "identifier_scheme": "ORCID",
                        "identifier": "https://orcid.org/0000-0001-0002-0003",
                    }
                ],
                "rights_holder_name": [{"name": "鳥座大学", "lang": "ja"}],
            }
        ]
    )
    doc = render_show(env, entry)
    assert_dl_structure(doc)
    [dd] = field_values(doc, "権利者情報")
    assert "ja 鳥座大学" in dd.text()
    assert "https://orcid.org/0000-0001-0002-0003" in [
        a.attrs.get("href") for a in dd.iter("a")
    ]


def test_show_jpcoar_publisher(env):
    entry = minimal_entry(
        jpcoar_publisher=[
            {
                "publisher_name": [{"publisher_name": "須原屋, 茂兵衞", "lang": "ja"}],
                "publisher_description": [
                    {"publisher_description": "巻之一三", "lang": "ja"}
                ],
                "location": [{"location": "江戸", "lang": "ja"}],
                "publication_place": [{"publication_place": "JPN"}],
            }
        ]
    )
    doc = render_show(env, entry)
    assert_dl_structure(doc)
    [dd] = field_values(doc, "出版者情報")
    assert dd.text() == (
        "ja 須原屋, 茂兵衞 出版者注記 巻之一三 出版地 江戸 出版地（国名コード） JPN"
    )


def test_show_geo_location(env):
    entry = minimal_entry(
        geo_location=[
            {"geo_location_point": {"point_longitude": 139.7, "point_latitude": 35.6}},
            {
                "geo_location_box": {
                    "west_bound_longitude": -140.4875,
                    "east_bound_longitude": 109.618333,
                    "south_bound_latitude": 60.255,
                    "north_bound_latitude": 75.589167,
                }
            },
            {"geo_location_place": ["東京", "京都"]},
        ]
    )
    doc = render_show(env, entry)
    assert_dl_structure(doc)
    [dd] = field_values(doc, "位置情報")
    assert [dt.text() for dt in dd.iter("dt")] == [
        "位置情報（点）",
        "位置情報（空間）",
        "位置情報（自由記述）",
        "位置情報（自由記述）",
    ]
    assert [d.text() for d in dd.iter("dd")] == [
        "経度 139.7、緯度 35.6",
        "西端経度 -140.4875、東端経度 109.618333、 南端緯度 60.255、北端緯度 75.589167",
        "東京",
        "京都",
    ]


def test_show_conference(env):
    entry = load_sample(PACKAGE_DIR / "samples" / "08_conference_object")
    doc = render_show(env, entry)
    assert_dl_structure(doc)
    [dd] = field_values(doc, "会議記述")
    assert [(dt.text(), d.text()) for dt, d in zip(dd.iter("dt"), dd.iter("dd"))] == [
        ("en", "RDA Seventh Plenary Meeting"),
        ("回次", "7"),
        ("主催機関", "The Research Data Alliance"),
        ("開催期間", "February 29th to March 4th, 2016 (2016-2-29 - 2016-3-4)"),
        ("開催会場", "Hitotsubashi Hall"),
        ("開催地", "Tokyo"),
        ("開催国", "JPN"),
    ]


def test_show_holding_agent(env):
    entry = load_sample(PACKAGE_DIR / "samples" / "12_digital_archive")
    doc = render_show(env, entry)
    [dd] = field_values(doc, "所蔵機関")
    assert [(dt.text(), d.text()) for dt, d in zip(dd.iter("dt"), dd.iter("dd"))] == [
        ("ROR", "https://ror.org/01464wm64"),
        ("ja", "人間文化研究機構 国文学研究資料館"),
        ("en", "National Institute of Japanese Literature"),
    ]
    assert [a.attrs["href"] for a in dd.iter("a")] == ["https://ror.org/01464wm64"]


def test_show_catalog(env):
    entry = load_sample(PACKAGE_DIR / "samples" / "12_digital_archive")
    doc = render_show(env, entry)
    assert_dl_structure(doc)
    [dd] = field_values(doc, "カタログ")
    catalog = dd.elements()[0]
    labels = [dt.text() for dt in catalog.elements()[::2]]
    assert labels == [
        "提供機関",
        "識別子",
        "タイトル",
        "内容記述",
        "主題",
        "ライセンス",
        "権利情報",
        "アクセス権",
        "代表画像",
    ]
    hrefs = [a.attrs["href"] for a in dd.iter("a")]
    assert "https://kokusho.nijl.ac.jp" in hrefs
    assert "https://kokusho.nijl.ac.jp/page/usage.html" in hrefs
    assert "国書データベース" in dd.text()
    assert "open access" in dd.text()
