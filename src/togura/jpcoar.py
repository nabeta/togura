import os
import glob
import mimetypes
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

ns = {
    "jpcoar": "https://github.com/JPCOAR/schema/blob/master/2.0/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "datacite": "https://schema.datacite.org/meta/kernel-4/",
    "oaire": "http://namespace.openaire.eu/schema/oaire/",
    "dcndl": "http://ndl.go.jp/dcndl/terms/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}

for key in ns.keys():
    ET.register_namespace(key, ns[key])


def access_rights_uri(string):
    match string:
        case "embargoed access":
            return "http://purl.org/coar/access_right/c_f1cf"
        case "metadata only access":
            return "http://purl.org/coar/access_right/c_14cb"
        case "open access":
            return "http://purl.org/coar/access_right/c_abf2"
        case "restricted access":
            return "http://purl.org/coar/access_right/c_16ec"


def resource_type_uri(string):
    match string:
        case "conference paper":
            return "http://purl.org/coar/resource_type/c_5794"
        case "data paper":
            return "http://purl.org/coar/resource_type/c_beb9"
        case "departmental bulletin paper":
            return "http://purl.org/coar/resource_type/c_6501"
        case "editorial":
            return "http://purl.org/coar/resource_type/c_b239"
        case "journal":
            return "http://purl.org/coar/resource_type/c_0640"
        case "journal article":
            return "http://purl.org/coar/resource_type/c_6501"
        case "newspaper":
            return "http://purl.org/coar/resource_type/c_2fe3"
        case "review article":
            return "http://purl.org/coar/resource_type/c_dcae04bc"
        case "other periodical":
            return "http://purl.org/coar/resource_type/QX5C-AR31"
        case "software paper":
            return "http://purl.org/coar/resource_type/c_7bab"
        case "article":
            return "http://purl.org/coar/resource_type/c_6501"
        case "book":
            return "http://purl.org/coar/resource_type/c_2f33"
        case "book part":
            return "http://purl.org/coar/resource_type/c_3248"
        case "cartographic material":
            return "http://purl.org/coar/resource_type/c_12cc"
        case "map":
            return "http://purl.org/coar/resource_type/c_12cd"
        case "conference object":
            return "http://purl.org/coar/resource_type/c_c94f"
        case "conference output":
            return "http://purl.org/coar/resource_type/c_c94f"
        case "conference presentation":
            return "http://purl.org/coar/resource_type/R60J-J5BD"
        case "conference proceedings":
            return "http://purl.org/coar/resource_type/c_f744"
        case "conference poster":
            return "http://purl.org/coar/resource_type/c_6670"
        case "aggregated data":
            return "http://purl.org/coar/resource_type/ACF7-8YT9"
        case "clinical trial data":
            return "http://purl.org/coar/resource_type/c_cb28"
        case "compiled data":
            return "http://purl.org/coar/resource_type/FXF3-D3G7"
        case "dataset":
            return "http://purl.org/coar/resource_type/c_ddb1"
        case "encoded data":
            return "http://purl.org/coar/resource_type/AM6W-6QAW"
        case "experimental data":
            return "http://purl.org/coar/resource_type/63NG-B465"
        case "genomic data":
            return "http://purl.org/coar/resource_type/A8F1-NPV9"
        case "geospatial data":
            return "http://purl.org/coar/resource_type/2H0M-X761"
        case "laboratory notebook":
            return "http://purl.org/coar/resource_type/H41Y-FW7B"
        case "measurement and test data":
            return "http://purl.org/coar/resource_type/DD58-GFSX"
        case "observational data":
            return "http://purl.org/coar/resource_type/FF4C-28RK"
        case "recorded data":
            return "http://purl.org/coar/resource_type/CQMR-7K63"
        case "simulation data":
            return "http://purl.org/coar/resource_type/W2XT-7017"
        case "survey data":
            return "http://purl.org/coar/resource_type/NHD0-W6SY"
        case "image":
            return "http://purl.org/coar/resource_type/c_c513"
        case "still image":
            return "http://purl.org/coar/resource_type/c_ecc8"
        case "moving image":
            return "http://purl.org/coar/resource_type/c_8a7e"
        case "video":
            return "http://purl.org/coar/resource_type/c_12ce"
        case "lecture":
            return "http://purl.org/coar/resource_type/c_8544"
        case "design patent":
            return "http://purl.org/coar/resource_type/C53B-JCY5"
        case "patent":
            return "http://purl.org/coar/resource_type/c_15cd"
        case "PCT application":
            return "http://purl.org/coar/resource_type/SB3Y-W4EH"
        case "plant patent":
            return "http://purl.org/coar/resource_type/Z907-YMBB"
        case "plant variety protection":
            return "http://purl.org/coar/resource_type/GPQ7-G5VE"
        case "software patent":
            return "http://purl.org/coar/resource_type/MW8G-3CR8"
        case "trademark":
            return "http://purl.org/coar/resource_type/H6QP-SC1X"
        case "utility model":
            return "http://purl.org/coar/resource_type/9DKX-KSAF"
        case "report":
            return "http://purl.org/coar/resource_type/c_93fc"
        case "research report":
            return "http://purl.org/coar/resource_type/c_18ws"
        case "technical report":
            return "http://purl.org/coar/resource_type/c_18gh"
        case "policy report":
            return "http://purl.org/coar/resource_type/c_186u"
        case "working paper":
            return "ihttp://purl.org/coar/resource_type/c_8042"
        case "data management plan":
            return "http://purl.org/coar/resource_type/c_ab20"
        case "sound":
            return "http://purl.org/coar/resource_type/c_18cc"
        case "thesis":
            return "http://purl.org/coar/resource_type/c_46ec"
        case "bachelor thesis":
            return "http://purl.org/coar/resource_type/c_7a1f"
        case "master thesis":
            return "http://purl.org/coar/resource_type/c_bdcc"
        case "doctoral thesis":
            return "http://purl.org/coar/resource_type/c_db06"
        case "commentary":
            return "http://purl.org/coar/resource_type/D97F-VB57"
        case "design":
            return "http://purl.org/coar/resource_type/542X-3S04"
        case "industrial design":
            return "http://purl.org/coar/resource_type/JBNF-DYAD"
        case "interactive resource":
            return "http://purl.org/coar/resource_type/c_e9a0"
        case "layout design":
            return "http://purl.org/coar/resource_type/BW7T-YM2G"
        case "learning object":
            return "http://purl.org/coar/resource_type/c_e059"
        case "manuscript":
            return "http://purl.org/coar/resource_type/c_0040"
        case "musical notation":
            return "http://purl.org/coar/resource_type/c_18cw"
        case "peer review":
            return "http://purl.org/coar/resource_type/H9BQ-739P"
        case "research proposal":
            return "http://purl.org/coar/resource_type/c_baaf"
        case "research protocol":
            return "http://purl.org/coar/resource_type/YZ1N-ZFT9"
        case "software":
            return "http://purl.org/coar/resource_type/c_5ce6"
        case "source code":
            return "http://purl.org/coar/resource_type/QH80-2R4E"
        case "technical documentation":
            return "http://purl.org/coar/resource_type/c_71bd"
        case "transcription":
            return "http://purl.org/coar/resource_type/6NC7-GK9S"
        case "workflow":
            return "http://purl.org/coar/resource_type/c_393c"
        case "other":
            return "http://purl.org/coar/resource_type/c_1843"


def text_version_uri(string):
    match string:
        case "AO":
            return "http://purl.org/coar/version/c_b1a7d7d4d402bcce"
        case "SMUR":
            return "http://purl.org/coar/version/c_71e4c1898caa6e32"
        case "AM":
            return "http://purl.org/coar/version/c_ab4af688f83e57aa"
        case "P":
            return "http://purl.org/coar/version/c_fa2ee174bc00049f"
        case "VoR":
            return "http://purl.org/coar/version/c_970fb48d4fbd8a85"
        case "CVoR":
            return "http://purl.org/coar/version/c_e19f295774971610"
        case "EVoR":
            return "http://purl.org/coar/version/c_dc82b40f9837b551"
        case "NA":
            return "http://purl.org/coar/version/c_be7fb7dd8ff6fe43"


def jpcoar_identifier_type(string):
    url = urlparse(string)
    match url.hostname.lower():
        case "doi.org":
            return "DOI"
        case "dx.doi.org":
            return "DOI"
        case "hdl.handle.net":
            return "HDL"
        case _:
            return "URI"


def generate(entry, base_url):
    """JPCOARスキーマのXMLを作成する"""
    root = ET.Element(ET.QName(ns["jpcoar"], "jpcoar"))
    root.set(
        ET.QName(ns["xsi"], "schemaLocation"),
        "https://github.com/JPCOAR/schema/blob/master/2.0/ jpcoar_scm.xsd",
    )

    # 1 タイトル
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/1
    for d in entry["title"]:
        title = ET.SubElement(root, ET.QName(ns["dc"], "title"))
        title.text = d["title"]
        if d.get("lang") is not None:
            title.set("xml:lang", d["lang"])

    # 2 その他のタイトル
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/2
    if entry.get("alternative"):
        for d in entry["alternative"]:
            alternative = ET.SubElement(root, ET.QName(ns["dcterms"], "alternative"))
            alternative.text = d["title"]
            if d.get("lang") is not None:
                alternative.set("xml:lang", d["lang"])

    # 3 作成者
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/3
    if entry.get("creator"):
        add_creator(entry, root)

    # 4 寄与者
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/4
    if entry.get("contributor"):
        add_contributor(entry, root)

    # 5 アクセス権
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/5
    if entry.get("access_rights"):
        access_rights = ET.SubElement(root, ET.QName(ns["dcterms"], "accessRights"))
        access_rights.set("rdf:resource", access_rights_uri(entry["access_rights"]))
        access_rights.text = entry["access_rights"]

    # 6 権利情報
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/6
    if entry.get("rights"):
        for d in entry["rights"]:
            rights = ET.SubElement(root, ET.QName(ns["dc"], "rights"))
            if d.get("rights"):
                rights.text = d["rights"]
            if d.get("rights_uri"):
                rights.set(ET.QName(ns["rdf"], "resource"), d["rights_uri"])
            if d.get("lang") is not None:
                rights.set("xml:lang", d["lang"])

    # 7 権利者情報
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/7
    if entry.get("rights_holder"):
        for d in entry["rights_holder"]:
            rights_holder = ET.SubElement(root, ET.QName(ns["jpcoar"], "rightsHolder"))
            # 権利者識別子
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/7-.1
            if d.get("name_identifier"):
                for d_identifier in d["name_identifier"]:
                    name_identifier = ET.SubElement(
                        rights_holder,
                        ET.QName(ns["jpcoar"], "nameIdentifier"),
                        {
                            "nameIdentifierScheme": d_identifier["identifier_scheme"],
                            "nameIdentifierURI": d_identifier["identifier"],
                        },
                    )
                    name_identifier.text = name_identifier["identifier"]
            # 権利者名
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/7-.2
            if d.get("rights_holder_name"):
                for d_name in d["rights_holder_name"]:
                    rights_holder_name = ET.SubElement(
                        rights_holder, ET.QName(ns["jpcoar"], "rightsHolderName")
                    )
                    rights_holder_name.text = d_name["name"]
                    if d_name.get("lang") is not None:
                        rights_holder_name.set("xml:lang", d_name["lang"])

    # 8 主題
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/8
    if entry.get("subject"):
        for d in entry["subject"]:
            subject = ET.SubElement(root, ET.QName(ns["jpcoar"], "subject"))
            subject.text = d["subject"]
            if d.get("subject_scheme"):
                subject.set("subjectScheme", d["subject_scheme"])
            if d.get("subject_uri"):
                subject.set("subjectURI", d["subject_uri"])
            if d.get("lang") is not None:
                subject.set("xml:lang", d["lang"])

    # 9 内容記述
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/9
    if entry.get("description"):
        for d in entry["description"]:
            description = ET.SubElement(root, ET.QName(ns["datacite"], "description"))
            description.text = d["description"]
            if d.get("description_type") is not None:
                description.set("descriptionType", d["description_type"])
            if d.get("lang") is not None:
                description.set("xml:lang", d["lang"])

    # 10 出版者
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/10
    if entry.get("publisher"):
        for d in entry["publisher"]:
            publisher = ET.SubElement(root, ET.QName(ns["dc"], "publisher"))
            publisher.text = d["publisher"]
            if d.get("lang") is not None:
                publisher.set("xml:lang", d["lang"])

    # 11 出版者情報
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/11
    if entry.get("jpcoar_publisher"):
        add_jpcoar_publisher(entry, root)

    # 12 日付
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/12
    if entry.get("date"):
        for d in entry["date"]:
            date = ET.SubElement(
                root, ET.QName(ns["datacite"], "date"), {"dateType": d["date_type"]}
            )
            date.text = str(d["date"])

    # 13 日付（リテラル）
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/13
    if entry.get("dcterms_date"):
        for d in entry["dcterms_date"]:
            date = ET.SubElement(root, ET.QName(ns["dcterms"], "date"))
            date.text = str(d["date"])

    # 14 言語
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/14
    if entry.get("language"):
        for d in entry["language"]:
            language = ET.SubElement(root, ET.QName(ns["dc"], "language"))
            language.text = d

    # 15 資源タイプ
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/15
    resource_type = ET.SubElement(
        root,
        ET.QName(ns["dc"], "type"),
        {ET.QName(ns["rdf"], "resource"): resource_type_uri(entry["type"])},
    )
    resource_type.text = entry["type"]

    # 16 バージョン情報
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/16
    if entry.get("version"):
        version = ET.SubElement(root, ET.QName(ns["datacite"], "version"))
        version.text = entry["version"]

    # 17 出版タイプ
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/17
    if entry.get("text_version"):
        text_version = ET.SubElement(
            root,
            ET.QName(ns["oaire"], "version"),
            {ET.QName(ns["rdf"], "resource"): text_version_uri(entry["text_version"])},
        )
        text_version.text = entry["text_version"]

    # 18 識別子
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/18
    add_identifier(entry, root, base_url)

    # 19 ID登録
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/19
    if entry.get("identifier_registration"):
        identifier_registration = ET.SubElement(
            root,
            ET.QName(ns["jpcoar"], "identifierRegistration"),
            {"identifierType": entry["identifier_registration"]["identifier_type"]},
        )
        identifier_registration.text = entry["identifier_registration"]["identifier"]

    # 20 関連情報
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/20
    if entry.get("relation"):
        for relation in entry["relation"]:
            elem_relation = ET.SubElement(root, ET.QName(ns["jpcoar"], "relation"))
            if relation.get("relation_type") is not None:
                elem_relation.set("relationType", relation["relation_type"])
            # 関連識別子
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/20-.1
            if relation.get("related_identifier") is not None:
                elem_related_identifier = ET.SubElement(
                    elem_relation, ET.QName(ns["jpcoar"], "relatedIdentifier")
                )
                elem_related_identifier.text = relation["related_identifier"][
                    "identifier"
                ]
                if relation["related_identifier"].get("identifier_type"):
                    elem_related_identifier.set(
                        "identifierType",
                        relation["related_identifier"]["identifier_type"],
                    )

            # 関連名称
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/20-.2
            if relation.get("related_title") is not None:
                for related_title in relation["related_title"]:
                    elem_related_title = ET.SubElement(
                        elem_relation, ET.QName(ns["jpcoar"], "relatedTitle")
                    )
                    elem_related_title.text = related_title["related_title"]
                    if related_title.get("lang") is not None:
                        elem_related_title.set("xml:lang", related_title["lang"])

    # 21 時間的範囲
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/21
    if entry.get("temporal"):
        for d in entry["temporal"]:
            temporal = ET.SubElement(root, ET.QName(ns["dcterms"], "temporal"))
            temporal.text = d["temporal"]
            if d.get("lang") is not None:
                temporal.set("xml:lang", d["lang"])

    # 22 位置情報
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/22
    if entry.get("geo_location"):
        add_geo_location(entry, root)

    # 23 助成情報
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/23
    if entry.get("funding_reference"):
        add_funding_reference(entry, root)

    # 24 収録物識別子
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/24
    if entry.get("source_identifier"):
        for d in entry["source_identifier"]:
            source_identifier = ET.SubElement(
                root,
                ET.QName(ns["jpcoar"], "sourceIdentifier"),
                {"identifierType": d["identifier_type"]},
            )
            source_identifier.text = d["identifier"]

    # 25 収録物名
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/25
    if entry.get("source_title"):
        for d in entry["source_title"]:
            source_title = ET.SubElement(root, ET.QName(ns["jpcoar"], "sourceTitle"))
            source_title.text = d["source_title"]
            if d.get("lang") is not None:
                source_title.set("xml:lang", d["lang"])

    # 26 巻
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/26
    if entry.get("volume"):
        volume = ET.SubElement(root, ET.QName(ns["jpcoar"], "volume"))
        volume.text = entry["volume"]

    # 27 号
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/27
    if entry.get("issue"):
        issue = ET.SubElement(root, ET.QName(ns["jpcoar"], "issue"))
        issue.text = entry["issue"]

    # 28 ページ数
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/28
    if entry.get("num_pages"):
        num_pages = ET.SubElement(root, ET.QName(ns["jpcoar"], "numPages"))
        num_pages.text = str(entry["num_pages"])

    # 29 開始ページ
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/29
    if entry.get("page_start"):
        page_start = ET.SubElement(root, ET.QName(ns["jpcoar"], "pageStart"))
        page_start.text = entry["page_start"]

    # 30 終了ページ
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/30
    if entry.get("page_end"):
        page_end = ET.SubElement(root, ET.QName(ns["jpcoar"], "pageEnd"))
        page_end.text = entry["page_end"]

    # 31 学位授与番号
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/31
    if entry.get("dissertation_number"):
        dissertation_number = ET.SubElement(
            root, ET.QName(ns["dcndl"], "dissertationNumber")
        )
        dissertation_number.text = entry["dissertation_number"]

    # 32 学位名
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/32
    if entry.get("degree_name"):
        for d in entry["degree_name"]:
            degree_name = ET.SubElement(root, ET.QName(ns["dcndl"], "degreeName"))
            degree_name.text = d["degree_name"]
            if d.get("lang") is not None:
                degree_name.set("xml:lang", d["lang"])

    # 33 学位授与年月日
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/33
    if entry.get("date_granted"):
        date_granted = ET.SubElement(root, ET.QName(ns["dcndl"], "dateGranted"))
        date_granted.text = str(entry["date_granted"])

    # 34 学位授与機関
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/34
    if entry.get("degree_grantor"):
        degree_grantor = ET.SubElement(root, ET.QName(ns["jpcoar"], "degreeGrantor"))
        for d in entry["degree_grantor"]:
            if d.get("name_identifier"):
                for i in d["name_identifier"]:
                    for i in d["name_identifier"]:
                        name_identifier = ET.SubElement(
                            degree_grantor, ET.QName(ns["jpcoar"], "nameIdentifier")
                        )
                        if i.get("name_identifier_scheme"):
                            name_identifier.set(
                                "nameIdentifierScheme", i["name_identifier_scheme"]
                            )
                        name_identifier.text = i["identifier"]
            if d.get("degree_grantor_name"):
                for i in d["degree_grantor_name"]:
                    degree_grantor_name = ET.SubElement(
                        degree_grantor, ET.QName(ns["jpcoar"], "degreeGrantorName")
                    )
                    degree_grantor_name.text = i["name"]
                    if i.get("lang") is not None:
                        degree_grantor_name.set("xml:lang", i["lang"])

    # 35 会議記述
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/35
    if entry.get("conference"):
        add_conference(entry, root)

    # 36 版
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/36
    if entry.get("edition"):
        for d in entry["edition"]:
            edition = ET.SubElement(root, ET.QName(ns["dcndl"], "edition"))
            edition.text = d["edition"]
            if d.get("lang") is not None:
                edition.set("xml:lang", d["lang"])

    # 37 部編名
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/37
    if entry.get("volume_title"):
        for d in entry["volume_title"]:
            volume_title = ET.SubElement(root, ET.QName(ns["dcndl"], "volumeTitle"))
            volume_title.text = d["volume_title"]
            if d.get("lang") is not None:
                volume_title.set("xml:lang", d["lang"])

    # 38 原文の言語
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/38
    if entry.get("original_language"):
        for d in entry["original_language"]:
            original_language = ET.SubElement(
                root, ET.QName(ns["dcndl"], "originalLanguage")
            )
            original_language.text = d

    # 39 大きさ
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/39
    if entry.get("extent"):
        for d in entry["extent"]:
            extent = ET.SubElement(root, ET.QName(ns["dcterms"], "extent"))
            extent.text = d["extent"]
            if d.get("lang") is not None:
                extent.set("xml:lang", d["lang"])

    # 40 物理的形態
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/40
    if entry.get("format"):
        for d in entry["format"]:
            format = ET.SubElement(root, ET.QName(ns["jpcoar"], "format"))
            format.text = d["format"]
            if d.get("lang") is not None:
                format.set("xml:lang", d["lang"])

    # 41 所蔵機関
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/41
    if entry.get("holding_agent"):
        holding_agent = ET.SubElement(root, ET.QName(ns["jpcoar"], "holdingAgent"))
        if entry["holding_agent"]["holding_agent_name_identifier"] is not None:
            holding_agent_name_identifier = ET.SubElement(
                holding_agent,
                ET.QName(ns["jpcoar"], "holdingAgentNameIdentifier"),
                {
                    "nameIdentifierScheme": entry["holding_agent"][
                        "holding_agent_name_identifier"
                    ]["name_identifier_scheme"]
                },
            )
            holding_agent_name_identifier.text = entry["holding_agent"][
                "holding_agent_name_identifier"
            ]["identifier"]
        for d_name in entry["holding_agent"]["holding_agent_name"]:
            holding_agent_name = ET.SubElement(
                holding_agent, ET.QName(ns["jpcoar"], "holdingAgentName")
            )
            holding_agent_name.text = d_name["holding_agent_name"]
            if d_name.get("lang") is not None:
                holding_agent_name.set("xml:lang", d_name["lang"])

    # 42 データセットシリーズ
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/42
    if entry.get("dataset_series"):
        dataset_series = ET.SubElement(root, ET.QName(ns["jpcoar"], "datasetSeries"))
        dataset_series.text = str(entry["dataset_series"])

    # 43 ファイル情報
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/43
    if entry.get("file"):
        add_file(entry, root)

    # 44 カタログ
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44
    if entry.get("catalog"):
        add_catalog(entry, root)

    logger.debug(f"{str(entry['id'])} created")
    return root


def add_creator(entry, root):
    """作成者をメタデータに追加する"""
    for creator in entry["creator"]:
        elem_creator = ET.SubElement(
            root, ET.QName(ns["jpcoar"], "creator"), {"creatorType": "著"}
        )
        # 作成者識別子
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/3-.1
        if creator.get("name_identifier"):
            for name_identifier in creator["name_identifier"]:
                elem_name_identifier = ET.SubElement(
                    elem_creator,
                    ET.QName(ns["jpcoar"], "nameIdentifier"),
                    {
                        "nameIdentifierScheme": name_identifier["identifier_scheme"],
                        "nameIdentifierURI": name_identifier["identifier"],
                    },
                )
                elem_name_identifier.text = name_identifier["identifier"]

        # 作成者姓名
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/3-.2
        if creator.get("creator_name"):
            for creator_name in creator["creator_name"]:
                elem_creator_name = ET.SubElement(
                    elem_creator, ET.QName(ns["jpcoar"], "creatorName")
                )
                elem_creator_name.text = creator_name["name"]
                if creator_name.get("lang") is not None:
                    elem_creator_name.set("xml:lang", creator_name["lang"])

        # 作成者姓
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/3-.3
        if creator.get("family_name"):
            for family_name in creator["family_name"]:
                elem_family_name = ET.SubElement(
                    elem_creator, ET.QName(ns["jpcoar"], "familyName")
                )
                elem_family_name.text = family_name["name"]
                if family_name.get("lang") is not None:
                    elem_family_name.set("xml:lang", family_name["lang"])

        # 作成者名
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/3-.4
        if creator.get("given_name"):
            for given_name in creator["given_name"]:
                elem_given_name = ET.SubElement(
                    elem_creator, ET.QName(ns["jpcoar"], "givenName")
                )
                elem_given_name.text = given_name["name"]
                if given_name.get("lang") is not None:
                    elem_given_name.set("xml:lang", given_name["lang"])

        # 作成者別名
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/3-.5
        if creator.get("creator_alternative"):
            for creator_alternative in creator["creator_alternative"]:
                elem_creator_alternative = ET.SubElement(
                    elem_creator, ET.QName(ns["jpcoar"], "creatorAlternative")
                )
                elem_creator_alternative.text = creator_alternative["name"]
                if creator_alternative.get("lang") is not None:
                    elem_creator_alternative.set("xml:lang", given_name["lang"])

        # 作成者所属
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/3-.6
        if creator.get("affiliation"):
            for affiliation in creator["affiliation"]:
                elem_affiliation = ET.SubElement(
                    elem_creator, ET.QName(ns["jpcoar"], "affiliation")
                )
                if affiliation.get("name_identifier"):
                    for affiliation_identifier in affiliation["name_identifier"]:
                        elem_affiliation_identifier = ET.SubElement(
                            elem_affiliation,
                            ET.QName(ns["jpcoar"], "nameIdentifier"),
                            {
                                "nameIdentifierScheme": affiliation_identifier[
                                    "identifier_scheme"
                                ],
                                "nameIdentifierURI": affiliation_identifier["identifier"],
                            },
                        )
                        elem_affiliation_identifier.text = affiliation_identifier[
                            "identifier"
                        ]
                for affiliation_name in affiliation["affiliation_name"]:
                    elem_affiliation_name = ET.SubElement(
                        elem_affiliation, ET.QName(ns["jpcoar"], "affiliationName")
                    )
                    elem_affiliation_name.text = affiliation_name["name"]
                    if affiliation_name.get("lang") is not None:
                        elem_affiliation_name.set("xml:lang", affiliation_name["lang"])


def add_contributor(entry, root):
    """寄与者をメタデータに追加する"""
    for contributor in entry["contributor"]:
        elem_contributor = ET.SubElement(root, ET.QName(ns["jpcoar"], "contributor"))
        if contributor.get("contributor_type") is not None:
            elem_contributor.set("contributorType", contributor["contributor_type"])

        # 寄与者識別子
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/4-.1
        if contributor.get("name_identifier"):
            for name_identifier in contributor["name_identifier"]:
                elem_name_identifier = ET.SubElement(
                    elem_contributor,
                    ET.QName(ns["jpcoar"], "nameIdentifier"),
                    {
                        "nameIdentifierScheme": name_identifier["identifier_scheme"],
                        "nameIdentifierURI": name_identifier["identifier"],
                    },
                )
                elem_name_identifier.text = name_identifier["identifier"]

        # 寄与者姓名
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/4-.2
        if contributor.get("contributor_name"):
            for contributor_name in contributor["contributor_name"]:
                elem_contributor_name = ET.SubElement(
                    elem_contributor, ET.QName(ns["jpcoar"], "contributorName")
                )
                elem_contributor_name.text = contributor_name["name"]
                if contributor_name.get("lang") is not None:
                    elem_contributor_name.set("xml:lang", contributor_name["lang"])

        # 寄与者姓
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/4-.3
        if contributor.get("family_name"):
            for family_name in contributor["family_name"]:
                elem_family_name = ET.SubElement(
                    elem_contributor, ET.QName(ns["jpcoar"], "familyName")
                )
                elem_family_name.text = family_name["name"]
                if family_name.get("lang") is not None:
                    elem_family_name.set("xml:lang", family_name["lang"])

        # 寄与者名
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/4-.4
        if contributor.get("given_name"):
            for given_name in contributor["given_name"]:
                elem_given_name = ET.SubElement(
                    elem_contributor, ET.QName(ns["jpcoar"], "givenName")
                )
                elem_given_name.text = given_name["name"]
                if given_name.get("lang") is not None:
                    elem_given_name.set("xml:lang", given_name["lang"])

        # 寄与者別名
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/4-.5
        if contributor.get("contributor_alternative"):
            for contributor_alternative in contributor["contributor_alternative"]:
                elem_contributor_alternative = ET.SubElement(
                    elem_contributor, ET.QName(ns["jpcoar"], "contributorAlternative")
                )
                elem_contributor_alternative.text = contributor_alternative["name"]
                if contributor_alternative.get("lang") is not None:
                    elem_contributor_alternative.set("xml:lang", given_name["lang"])

        # 寄与者所属
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/4-.6
        if contributor.get("affiliation"):
            for affiliation in contributor["affiliation"]:
                elem_affiliation = ET.SubElement(
                    elem_contributor, ET.QName(ns["jpcoar"], "affiliation")
                )
                for affiliation_identifier in affiliation["name_identifier"]:
                    elem_affiliation_identifier = ET.SubElement(
                        elem_affiliation,
                        ET.QName(ns["jpcoar"], "nameIdentifier"),
                        {
                            "nameIdentifierScheme": affiliation_identifier[
                                "identifier_scheme"
                            ],
                            "nameIdentifierURI": affiliation_identifier["identifier"],
                        },
                    )
                elem_affiliation_identifier.text = affiliation_identifier["identifier"]
                for affiliation_name in affiliation["affiliation_name"]:
                    elem_affiliation_name = ET.SubElement(
                        elem_affiliation, ET.QName(ns["jpcoar"], "affiliationName")
                    )
                    elem_affiliation_name.text = affiliation_name["name"]
                    if affiliation_name.get("lang") is not None:
                        elem_affiliation_name.set("xml:lang", affiliation_name["lang"])


def add_jpcoar_publisher(entry, root):
    for d in entry["jpcoar_publisher"]:
        jpcoar_publisher = ET.SubElement(root, ET.QName(ns["jpcoar"], "publisher"))
        # 出版者名
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/11-.1
        for d_name in d["publisher_name"]:
            jpcoar_publisher_name = ET.SubElement(
                jpcoar_publisher, ET.QName(ns["jpcoar"], "publisherName")
            )
            jpcoar_publisher_name.text = d_name["publisher_name"]
            if d_name.get("lang") is not None:
                jpcoar_publisher_name.set("xml:lang", d_name["lang"])

        # 出版者注記
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/11-.2
        for d_description in d["publisher_description"]:
            jpcoar_publisher_description = ET.SubElement(
                jpcoar_publisher, ET.QName(ns["jpcoar"], "publisherDescription")
            )
            jpcoar_publisher_description.text = d_description["publisher_description"]
            if d_description.get("lang") is not None:
                jpcoar_publisher_description.set("xml:lang", d_description["lang"])

        # 出版地
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/11-.3
        for d_location in d["location"]:
            jpcoar_publisher_location = ET.SubElement(
                jpcoar_publisher, ET.QName(ns["dcndl"], "location")
            )
            jpcoar_publisher_location.text = d_location["location"]
            if d_location.get("lang") is not None:
                jpcoar_publisher_location.set("xml:lang", d_location["lang"])

        # 出版地（国名コード）
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/11-.4
        for d_place in d["publication_place"]:
            jpcoar_publisher_place = ET.SubElement(
                jpcoar_publisher, ET.QName(ns["dcndl"], "publicationPlace")
            )
            jpcoar_publisher_place.text = d_place["publication_place"]
            # if d_place.get("lang") is not None:
            #   jpcoar_publisher_place.set("xml:lang", d_place["lang"])


def add_identifier(entry, root, base_url):
    """識別子をメタデータに追加する"""
    elem_identifier = ET.SubElement(
        root, ET.QName(ns["jpcoar"], "identifier"), {"identifierType": "URI"}
    )
    elem_identifier.text = urljoin(base_url, f"{entry['id']}/ro-crate-preview.html")

    if entry.get("identifier"):
        for identifier in entry["identifier"]:
            # TODO: URI形式になっていない識別子の扱いを検討する
            try:
                elem_identifier = ET.SubElement(
                    root,
                    ET.QName(ns["jpcoar"], "identifier"),
                    {"identifierType": jpcoar_identifier_type(identifier)},
                )
                elem_identifier.text = identifier
            except AttributeError:
                continue


def add_geo_location(entry, root):
    for d in entry["geo_location"]:
        geo_location = ET.SubElement(root, ET.QName(ns["datacite"], "geoLocation"))
        # 位置情報（点）
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/22-.1
        if d.get("geo_location_point"):
            geo_location_point = ET.SubElement(
                geo_location, ET.QName(ns["datacite"], "geoLocationPoint")
            )
            geo_location_point_longitude = ET.SubElement(
                geo_location_point, ET.QName(ns["datacite"], "pointLongitude")
            )
            geo_location_point_longitude.text = d["geo_location_point"][
                "point_longitude"
            ]
            geo_location_point_latitude = ET.SubElement(
                geo_location_point, ET.QName(ns["datacite"], "pointLatitude")
            )
            geo_location_point_latitude.text = d["geo_location_point"]["point_latitude"]

        # 位置情報（空間）
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/22-.2
        if d.get("geo_location_box"):
            geo_location_box = ET.SubElement(
                geo_location, ET.QName(ns["datacite"], "geoLocationBox")
            )
            if d["geo_location_box"].get("west_bound_longitude") is not None:
                west_bound_longitude = ET.SubElement(
                    geo_location_box, ET.QName(ns["datacite"], "westBoundLongitude")
                )
                west_bound_longitude.text = str(
                    d["geo_location_box"]["west_bound_longitude"]
                )
            if d["geo_location_box"].get("east_bound_longitude") is not None:
                east_bound_longitude = ET.SubElement(
                    geo_location_box, ET.QName(ns["datacite"], "eastBoundLongitude")
                )
                east_bound_longitude.text = str(
                    d["geo_location_box"]["east_bound_longitude"]
                )
            if d["geo_location_box"].get("south_bound_latitude") is not None:
                south_bound_latitude = ET.SubElement(
                    geo_location_box, ET.QName(ns["datacite"], "southBoundLatitude")
                )
                south_bound_latitude.text = str(
                    d["geo_location_box"]["south_bound_latitude"]
                )
            if d["geo_location_box"].get("north_bound_latitude") is not None:
                north_bound_latitude = ET.SubElement(
                    geo_location_box, ET.QName(ns["datacite"], "northBoundLatitude")
                )
                north_bound_latitude.text = str(
                    d["geo_location_box"]["north_bound_latitude"]
                )

        # 位置情報（自由記述）
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/22-.3
        if d.get("geo_location_place"):
            for d_place in d["geo_location_place"]:
                geo_location_place = ET.SubElement(
                    geo_location, ET.QName(ns["datacite"], "geoLocationPlace")
                )
                geo_location_place.text = d_place


def add_funding_reference(entry, root):
    """助成情報をメタデータに追加する"""
    for funding_reference in entry["funding_reference"]:
        elem_funding_reference = ET.SubElement(
            root, ET.QName(ns["jpcoar"], "fundingReference")
        )

        # 助成機関識別子
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/23-.1
        if funding_reference.get("funder_identifier"):
            elem_funder_identifier = ET.SubElement(
                elem_funding_reference,
                ET.QName(ns["jpcoar"], "funderIdentifier"),
                {
                    "funderIdentifierType": funding_reference["funder_identifier"][
                        "funder_identifier_type"
                    ]
                },
            )
            elem_funder_identifier.text = funding_reference["funder_identifier"][
                "funder_identifier"
            ]

        # 助成機関名
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/23-.2
        for funder_name in funding_reference["funder_name"]:
            elem_funder_name = ET.SubElement(
                elem_funding_reference, ET.QName(ns["jpcoar"], "funderName")
            )
            elem_funder_name.text = funder_name["funder_name"]
            if funder_name.get("lang") is not None:
                elem_funder_name.set("xml:lang", funder_name["lang"])

        # プログラム情報識別子
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/23-.3
        if funding_reference.get("funding_stream_identifier"):
            funding_stream_identifier = ET.SubElement(
                elem_funding_reference,
                ET.QName(ns["jpcoar"], "fundingStreamIdentifier"),
            )
            if funding_reference["funding_stream_identifier"].get(
                "funding_stream_identifier"
            ):
                funding_stream_identifier.text = funding_reference[
                    "funding_stream_identifier"
                ]["funding_stream_identifier"]
            if funding_reference["funding_stream_identifier"].get(
                "funding_stream_identifier_type"
            ):
                funding_stream_identifier.set(
                    "fundingStreamIdentifierType",
                    funding_reference["funding_stream_identifier"][
                        "funding_stream_identifier_type"
                    ],
                )
            if funding_reference["funding_stream_identifier"].get(
                "funding_stream_identifier_type_uri"
            ):
                funding_stream_identifier.set(
                    "fundingStreamIdentifierTypeURI",
                    funding_reference["funding_stream_identifier"][
                        "funding_stream_identifier_type_uri"
                    ],
                )

        # プログラム情報
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/23-.4
        if funding_reference.get("funding_stream"):
            for funding_stream in funding_reference["funding_stream"]:
                elem_funding_stream = ET.SubElement(
                    elem_funding_reference, ET.QName(ns["jpcoar"], "fundingStream")
                )
                elem_funding_stream.text = funding_stream["funding_stream"]
                if funding_stream.get("lang") is not None:
                    elem_funding_stream.set("xml:lang", funding_stream["lang"])

        # 研究課題番号
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/23-.5
        if funding_reference.get("award_number"):
            elem_award_number = ET.SubElement(
                elem_funding_reference, ET.QName(ns["jpcoar"], "awardNumber")
            )
            elem_award_number.text = funding_reference["award_number"]["award_number"]
            if funding_reference["award_number"].get("award_number_type"):
                elem_award_number.set(
                    "awardNumberType",
                    funding_reference["award_number"]["award_number_type"],
                )
            if funding_reference["award_number"].get("award_uri"):
                elem_award_number.set(
                    "awardURI", funding_reference["award_number"]["award_uri"]
                )

        # 研究課題名
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/23-.6
        if funding_reference.get("award_title"):
            for award_title in funding_reference["award_title"]:
                elem_award_title = ET.SubElement(
                    elem_funding_reference, ET.QName(ns["jpcoar"], "awardTitle")
                )
                elem_award_title.text = award_title["award_title"]
                if award_title.get("lang") is not None:
                    elem_award_title.set("xml:lang", award_title["lang"])


def add_conference(entry, root):
    conference = ET.SubElement(root, ET.QName(ns["jpcoar"], "conference"))
    for d in entry["conference"]:
        # 会議名
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/35-.1
        conference_name = ET.SubElement(
            conference, ET.QName(ns["jpcoar"], "conferenceName")
        )
        for d_name in d["conference_name"]:
            conference_name.text = d_name["conference_name"]
            if d_name.get("lang") is not None:
                conference_name.set("xml:lang", d_name["lang"])

        # 回次
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/35-.2
        if d.get("conference_sequence"):
            conference_sequence = ET.SubElement(
                conference, ET.QName(ns["jpcoar"], "conferenceSequence")
            )
            conference_sequence.text = str(d["conference_sequence"])

        # 主催機関
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/35-.3
        if d.get("conference_sponsor"):
            for d_sponsor in d["conference_sponsor"]:
                conference_sponsor = ET.SubElement(
                    conference, ET.QName(ns["jpcoar"], "conferenceSponsor")
                )
                conference_sponsor.text = d_sponsor["conference_sponsor"]
                if d_sponsor.get("lang") is not None:
                    conference_sponsor.set("xml:lang", d_sponsor["lang"])

        # 開催期間
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/35-.4
        if d.get("conference_date"):
            conference_date = ET.SubElement(
                conference, ET.QName(ns["jpcoar"], "conferenceDate")
            )
            if d["conference_date"].get("conference_date") is not None:
                conference_date.text = str(d["conference_date"]["conference_date"])
                if d["conference_date"].get("lang") is not None:
                    conference_date.set("xml:lang", d["conference_date"]["lang"])
            if d["conference_date"].get("start_day"):
                conference_date.set("startDay", str(d["conference_date"]["start_day"]))
            if d["conference_date"].get("start_month"):
                conference_date.set(
                    "startMonth", str(d["conference_date"]["start_month"])
                )
            if d["conference_date"].get("start_year"):
                conference_date.set(
                    "startYear", str(d["conference_date"]["start_year"])
                )
            if d["conference_date"].get("end_day"):
                conference_date.set("endDay", str(d["conference_date"]["end_day"]))
            if d["conference_date"].get("end_month"):
                conference_date.set("endMonth", str(d["conference_date"]["end_month"]))
            if d["conference_date"].get("end_year"):
                conference_date.set("endYear", str(d["conference_date"]["end_year"]))

        # 開催会場
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/35-.5
        if d.get("conference_venue"):
            for d_venue in d["conference_venue"]:
                conference_venue = ET.SubElement(
                    conference, ET.QName(ns["jpcoar"], "conferenceVenue")
                )
                conference_venue.text = d_venue["conference_venue"]
                if d_venue.get("lang") is not None:
                    conference_venue.set("xml:lang", d_venue["lang"])

        # 開催地
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/35-.6
        if d.get("conference_place"):
            for d_place in d["conference_place"]:
                conference_place = ET.SubElement(
                    conference, ET.QName(ns["jpcoar"], "conferencePlace")
                )
                conference_place.text = d_venue["conference_place"]
                if d_place.get("lang") is not None:
                    conference_place.set("xml:lang", d_place["lang"])

        # 開催国
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/35-.7
        if d.get("conference_country"):
            conference_country = ET.SubElement(
                conference, ET.QName(ns["jpcoar"], "conferenceCountry")
            )
            conference_country.text = d["conference_country"]["conference_country"]
            if d["conference_country"].get("lang") is not None:
                conference_country.set("xml:lang", d["conference_country"]["lang"])


def add_file(entry, root):
    """ファイルの情報をメタデータに追加する"""
    if entry.get("file"):
        for file in entry["file"]:
            elem_file = ET.SubElement(root, ET.QName(ns["jpcoar"], "file"))

            # 本文URL
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/43-.1
            if file.get("uri"):
                elem_file_uri = ET.SubElement(elem_file, ET.QName(ns["jpcoar"], "URI"))
                if file.get("object_type"):
                    elem_file_uri.set("objectType", file["object_type"])
                elem_file_uri.text = file["uri"]

            # ファイルフォーマット
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/43-.2
            if file.get("mime_type"):
                elem_file_mime_type = ET.SubElement(
                    elem_file, ET.QName(ns["jpcoar"], "mimeType")
                )
                elem_file_mime_type.text = file["mime_type"]

            # サイズ
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/43-.3
            if file.get("extent"):
                for extent in file["extent"]:
                    elem_file_extent = ET.SubElement(
                        elem_file, ET.QName(ns["jpcoar"], "extent")
                    )
                    elem_file_extent.text = extent

            # 日付
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/43-.4
            if file.get("date"):
                for date in file["date"]:
                    elem_file_date = ET.SubElement(
                        elem_file, ET.QName(ns["datacite"], "date")
                    )
                    if date.get("date_type"):
                        elem_file_date.set("dateType", date["date_type"])
                    elem_file_date.text = str(date["date"])

            # バージョン情報
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/43-.5
            if file.get("version"):
                elem_file_version = ET.SubElement(
                    elem_file, ET.QName(ns["datacite"], "version")
                )
                elem_file_version.text = file["version"]


def add_directory_file(data_dir, entry, root, base_url):
    """実ファイルの情報をメタデータに追加する"""
    for file in glob.glob(f"{data_dir}/*"):
        filename = os.path.basename(file)
        if filename == "jpcoar20.yaml":
            continue

        elem_file = ET.SubElement(root, ET.QName(ns["jpcoar"], "file"))
        elem_file_uri = ET.SubElement(
            elem_file,
            ET.QName(ns["jpcoar"], "URI"),
            {
                # "objectType": file["object_type"],
                "label": filename
            },
        )
        elem_file_uri.text = urljoin(base_url, f"{entry['id']}/{filename}")

        elem_mime_type = ET.SubElement(elem_file, ET.QName(ns["jpcoar"], "mimeType"))
        elem_file_extent = ET.SubElement(elem_file, ET.QName(ns["jpcoar"], "extent"))
        elem_file_extent.text = str(os.path.getsize(file))
        # for extent in file["extent"]:
        # elem_file_extent = ET.SubElement(elem_file, ET.QName(ns["jpcoar"], "extent"))
        # elem_file_extent.text = extent

        # for date in file["date"]:
        # elem_file_date = ET.SubElement(elem_file, ET.QName(ns["datacite"], "date"), {"dateType": date["date_type"]})
        # elem_file_date.text = str(date["date"])
        elem_mime_type.text = mimetypes.guess_type(file)[0]


def add_catalog(entry, root):
    catalog = ET.SubElement(root, ET.QName(ns["jpcoar"], "catalog"))

    # 提供機関
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.1
    if entry["catalog"].get("contributor"):
        add_contributor(entry["catalog"], catalog)

    # 識別子
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.2
    if entry["catalog"].get("identifier"):
        for d in entry["catalog"]["identifier"]:
            # TODO: URI形式になっていない識別子の扱いを検討する
            try:
                elem_identifier = ET.SubElement(
                    catalog,
                    ET.QName(ns["jpcoar"], "identifier"),
                    {"identifierType": jpcoar_identifier_type(d)},
                )
                elem_identifier.text = d
            except AttributeError:
                continue

    # タイトル
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.3
    if entry["catalog"].get("title"):
        for d in entry["catalog"]["title"]:
            title = ET.SubElement(catalog, ET.QName(ns["dc"], "title"))
            title.text = d["title"]
            if d.get("lang") is not None:
                title.set("xml:lang", d["lang"])

    # 内容記述
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.4
    if entry["catalog"].get("description"):
        for d in entry["catalog"]["description"]:
            description = ET.SubElement(
                catalog, ET.QName(ns["datacite"], "description")
            )
            description.set("descriptionType", d["description_type"])
            description.text = d["description"]
            if d.get("lang") is not None:
                description.set("xml:lang", d["lang"])

    # 主題
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.5
    if entry["catalog"].get("subject"):
        for d in entry["catalog"]["subject"]:
            subject = ET.SubElement(catalog, ET.QName(ns["jpcoar"], "subject"))
            subject.text = d["subject"]
            if d.get("subject_scheme"):
                subject.set("subjectScheme", d["subject_scheme"])
            if d.get("subject_uri"):
                subject.set("subjectURI", d["subject_uri"])
            if d.get("lang") is not None:
                subject.set("xml:lang", d["lang"])

    # ライセンス
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.6
    if entry["catalog"].get("license"):
        for d in entry["catalog"]["license"]:
            license = ET.SubElement(catalog, ET.QName(ns["jpcoar"], "license"))
            license.text = d["license"]
            license.set("licenseType", d["license_type"])
            if d.get("license_uri") is not None:
                license.set("rdf:resource", d["license_uri"])
            if d.get("lang") is not None:
                license.set("xml:lang", d["lang"])

    # 権利情報
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.7
    if entry["catalog"].get("rights"):
        for d in entry["catalog"]["rights"]:
            rights = ET.SubElement(catalog, ET.QName(ns["dc"], "rights"))
            rights.text = d["rights"]
            if d.get("rights_uri") is not None:
                rights.set("rdf:resource", d["rights_uri"])
            if d.get("lang") is not None:
                rights.set("xml:lang", d["lang"])

    # アクセス権
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.8
    if entry["catalog"].get("access_rights"):
        catalog_access_rights = ET.SubElement(
            catalog, ET.QName(ns["dcterms"], "accessRights")
        )
        catalog_access_rights.text = entry["catalog"]["access_rights"]

    # 代表画像
    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.9
    if entry["catalog"].get("file"):
        catalog_file = ET.SubElement(catalog, ET.QName(ns["jpcoar"], "file"))
        catalog_file_uri = ET.SubElement(catalog_file, ET.QName(ns["jpcoar"], "URI"))
        if entry["catalog"]["file"].get("object_type"):
            catalog_file_uri.set("objectType", entry["catalog"]["file"]["object_type"])
        if entry["catalog"]["file"].get("uri"):
            catalog_file_uri.text = entry["catalog"]["file"]["uri"]
