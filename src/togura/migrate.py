from oaipmh_scythe import Scythe
from logging import getLogger, DEBUG
from ruamel.yaml import YAML
from urllib.parse import urlparse
import os
import re
import requests

logger = getLogger(__name__)
logger.setLevel(DEBUG)


def migrate(
    base_url, metadata_prefix, date_from, date_until, export_dir, metadata_only
):
    scythe = Scythe(base_url)
    records = scythe.list_records(
        **{
            "metadata_prefix": metadata_prefix,
            "from_": date_from,
            "until": date_until,
            "ignore_deleted": True,
        }
    )

    if metadata_prefix == "jpcoar_2.0":
        jpcoar_ns = "https://github.com/JPCOAR/schema/blob/master/2.0/"
    else:
        jpcoar_ns = "https://github.com/JPCOAR/schema/blob/master/1.0/"

    ns = {
        "root": "http://www.openarchives.org/OAI/2.0/",
        "jpcoar": jpcoar_ns,
        "dc": "http://purl.org/dc/elements/1.1/",
        "dcterms": "http://purl.org/dc/terms/",
        "datacite": "https://schema.datacite.org/meta/kernel-4/",
        "oaire": "http://namespace.openaire.eu/schema/oaire/",
        "dcndl": "http://ndl.go.jp/dcndl/terms/",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    yaml = YAML()

    for record in records:
        identifier = record.xml.find(".//root:identifier", ns).text.split(":")[-1]

        # 1 タイトル
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/1
        titles = []
        for title in record.xml.findall(".//dc:title", ns):
            d = {"title": title.text}
            lang = title.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lang is not None:
                d["lang"] = lang
            titles.append(d)

        # 2 その他のタイトル
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/2
        alternatives = []
        for alternative in record.xml.findall(".//dcterms:alternative", ns):
            d = {"title": alternative.text}
            lang = alternative.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lang is not None:
                d["lang"] = lang
            alternatives.append(d)

        # 3 作成者
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/3
        creators = add_creator(record, ns)

        # 4 寄与者
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/4
        contributors = add_contributor(record, ns)

        # 5 アクセス権
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/5
        access_rights = None
        if record.xml.find(".//jpcoar:jpcoar/dcterms:accessRights", ns) is not None:
            access_rights = record.xml.find(
                ".//jpcoar:jpcoar/dcterms:accessRights", ns
            ).text

        # 6 権利情報
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/6
        rights = None
        if record.xml.find(".//jpcoar:jpcoar/dc:rights", ns) is not None:
            rights = []
            for right in record.xml.findall(".//jpcoar:jpcoar/dc:rights", ns):
                d = {"rights": right.text}
                rights_url = right.get("rdf:resource")
                if rights_url is not None:
                    d["rights_uri"] = rights_url
                lang = right.get("{http://www.w3.org/XML/1998/namespace}lang")
                if lang is not None:
                    d["lang"] = lang
                rights.append(d)

        # 7 権利者情報
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/7
        rights_holders = None
        if record.xml.findall(".//jpcoar:jpcoar/jpcoar:rightsHolder", ns) is not None:
            rights_holders = []
            for rights_holder in record.xml.findall(
                ".//jpcoar:jpcoar/jpcoar:rightsHolder", ns
            ):
                # 権利者識別子
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/7-.1
                if rights_holder.find("./jpcoar:nameIdentifier", ns) is not None:
                    name_identifiers = []
                    for name_identifier in rights_holder.findall(
                        "./jpcoar:nameIdentifier", ns
                    ):
                        scheme = name_identifier.get("nameIdentifierScheme")
                        if scheme == "e-Rad":
                            scheme = "e-Rad_Researcher"
                        d = {"identifier_scheme": scheme}
                        if name_identifier.get("nameIdentifierURI") is not None:
                            d["identifier"] = name_identifier.get("nameIdentifierURI")
                        else:
                            d["identifier"] = name_identifier.text
                        name_identifiers.append(d)

                # 権利者名
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/7-.2
                if rights_holder.find("./jpcoar:rightsHolderName", ns) is not None:
                    rights_holder_names = []
                    for rights_holder_name in rights_holder.findall(
                        "./jpcoar:rightsHolderName", ns
                    ):
                        d = {"name": rights_holder_name.text}
                        lang = rights_holder_name.get(
                            "{http://www.w3.org/XML/1998/namespace}lang"
                        )
                        if lang is not None:
                            d["lang"] = lang
                        rights_holder_names.append(d)

                    rights_holders.append(
                        {
                            "name_identifier": name_identifiers,
                            "rights_holder_name": rights_holder_names,
                        }
                    )

        # 8 主題
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/8
        subjects = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:subject", ns) is not None:
            subjects = []
            for subject in record.xml.findall(".//jpcoar:jpcoar/jpcoar:subject", ns):
                d = {"subject": subject.text}
                lang = subject.get("{http://www.w3.org/XML/1998/namespace}lang")
                if lang is not None:
                    d["lang"] = lang
                subjects.append(d)

        # 9 内容記述
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/9
        descriptions = None
        if record.xml.find(".//datacite:description", ns) is not None:
            descriptions = []
            for description in record.xml.findall(".//datacite:description", ns):
                d = {"description": description.text}
                lang = description.get("{http://www.w3.org/XML/1998/namespace}lang")
                if lang is not None:
                    d["lang"] = lang
                description_type = description.get("descriptionType")
                if description_type is not None:
                    d["description_type"] = description_type
                descriptions.append(d)

        # 10 出版者
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/10
        publishers = None
        if record.xml.find(".//jpcoar:jpcoar/dc:publisher", ns) is not None:
            publishers = []
            for publisher in record.xml.findall(".//jpcoar:jpcoar/dc:publisher", ns):
                d = {"publisher": publisher.text}
                lang = publisher.get("{http://www.w3.org/XML/1998/namespace}lang")
                if lang is not None:
                    d["lang"] = lang
                publishers.append(d)

        # 11 出版者情報
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/11
        jpcoar_publishers = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:publisher", ns) is not None:
            jpcoar_publishers = []
            for jpcoar_publisher in record.xml.findall(
                ".//jpcoar:jpcoar/jpcoar:publisher", ns
            ):
                # 出版者名
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/11-.1
                publisher_names = []
                for publisher_name in jpcoar_publisher.findall(
                    "./jpcoar:publisherName", ns
                ):
                    d = {"publisher_name": publisher_name.text}
                    lang = publisher_name.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang is not None:
                        d["lang"] = lang
                    publisher_names.append(d)

                # 出版者注記
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/11-.2
                publisher_descriptions = []
                for publisher_description in jpcoar_publisher.findall(
                    "./jpcoar:publisherDescription", ns
                ):
                    d = {"publisher_description": publisher_description.text}
                    lang = publisher_description.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang is not None:
                        d["lang"] = lang
                    publisher_descriptions.append(d)

                # 出版地
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/11-.3
                publisher_locations = []
                for publisher_location in jpcoar_publisher.findall(
                    "./dcndl:location", ns
                ):
                    d = {"location": publisher_location.text}
                    lang = publisher_location.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang is not None:
                        d["lang"] = lang
                    publisher_locations.append(d)

                # 出版地（国名コード）
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/11-.4
                publisher_places = []
                for publisher_place in jpcoar_publisher.findall(
                    "./dcndl:publicationPlace", ns
                ):
                    d = {"publication_place": publisher_place.text}
                    lang = publisher_place.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang is not None:
                        d["lang"] = lang
                    publisher_places.append(d)

                jpcoar_publishers.append(
                    {
                        "publisher_name": publisher_names,
                        "publisher_description": publisher_descriptions,
                        "location": publisher_locations,
                        "publisher_place": publisher_places,
                    }
                )

        # 12 日付
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/12
        dates = None
        if record.xml.find(".//jpcoar:jpcoar/datacite:date", ns) is not None:
            dates = []
            for date in record.xml.findall(".//jpcoar:jpcoar/datacite:date", ns):
                dates.append({"date": date.text, "date_type": date.get("dateType")})

        # 13 日付（リテラル）
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/13
        dcterms_dates = None
        if record.xml.find(".//jpcoar:jpcoar/dcterms:date", ns) is not None:
            dcterms_dates = []
            for dcterms_date in record.xml.findall(".//jpcoar:jpcoar/dcterms:date", ns):
                d = {"date": dcterms_date.text}
                lang = dcterms_date.get("{http://www.w3.org/XML/1998/namespace}lang")
                if lang is not None:
                    d["lang"] = lang
                dcterms_dates.append(d)

        # 14 言語
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/14
        languages = None
        if record.xml.find(".//jpcoar:jpcoar/dc:language", ns) is not None:
            languages = []
            for language in record.xml.findall(".//jpcoar:jpcoar/dc:language", ns):
                languages.append(language.text)

        # 15 資源タイプ
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/15
        resource_type = None
        if record.xml.find(".//jpcoar:jpcoar/dc:type", ns) is not None:
            resource_type = record.xml.find(".//jpcoar:jpcoar/dc:type", ns).text

        # 16 バージョン情報
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/16
        version = None
        if record.xml.find(".//jpcoar:jpcoar/datacite:version", ns) is not None:
            version = record.xml.find(".//jpcoar:jpcoar/datacite:version", ns).text

        # 17 出版タイプ
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/17
        text_version = None
        if record.xml.find(".//jpcoar:jpcoar/oaire:version", ns) is not None:
            text_version = record.xml.find(".//jpcoar:jpcoar/oaire:version", ns).text

        # 18 識別子
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/18
        identifiers = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:identifier", ns) is not None:
            identifiers = []
            for d in record.xml.findall(".//jpcoar:jpcoar/jpcoar:identifier", ns):
                identifiers.append(d.text)

        # 19 ID登録
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/19
        identifier_registration = None
        if (
            record.xml.find(".//jpcoar:jpcoar/jpcoar:identifierRegistration", ns)
            is not None
        ):
            registration = record.xml.find(
                ".//jpcoar:jpcoar/jpcoar:identifierRegistration", ns
            )
            identifier_registration = {
                "identifier": registration.text,
                "identifier_type": registration.get("identifierType"),
            }

        # 20 関連情報
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/20
        relations = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:relation", ns) is not None:
            relations = []
            for relation in record.xml.findall(".//jpcoar:jpcoar/jpcoar:relation", ns):
                d = {}
                if relation.get("relationType") is not None:
                    d["relation_type"] = relation.get("relationType")

                # 関連識別子
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/20-.1
                if relation.find("./jpcoar:relatedIdentifier", ns) is not None:
                    related_identifier = relation.find("./jpcoar:relatedIdentifier", ns)
                    d["related_identifier"] = {"identifier": related_identifier.text}
                    if related_identifier.get("identifierType") is not None:
                        d["related_identifier"]["identifier_type"] = (
                            related_identifier.get("identifierType")
                        )

                # 関連名称
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/20-.2
                related_titles = []
                for related_title in relation.findall("./jpcoar:relatedTitle", ns):
                    d_title = {"related_title": related_title.text}
                    lang = related_title.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang is not None:
                        d_title["lang"] = lang
                    related_titles.append(d_title)
                d["related_title"] = related_titles

                relations.append(d)

        # 21 時間的範囲
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/21
        temporals = None
        if record.xml.find(".//jpcoar:jpcoar/dcterms:temporal", ns) is not None:
            temporals = []
            for temporal in record.xml.findall(".//jpcoar:jpcoar/dcterms:temporal", ns):
                d = {"temporal": temporal.text}
                lang = temporal.get("{http://www.w3.org/XML/1998/namespace}lang")
                if lang is not None:
                    d["lang"] = lang
                temporals.append(d)

        # 22 位置情報
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/22
        geo_locations = None
        if record.xml.find(".//jpcoar:jpcoar/datacite:geoLocation", ns) is not None:
            geo_locations = []
            for geo_location in record.xml.findall(
                ".//jpcoar:jpcoar/datacite:geoLocation", ns
            ):
                d = {}
                # 位置情報（点）
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/22-.1
                if geo_location.find("./datacite:geoLocationPoint"):
                    d["geo_location_point"] = {
                        "point_longitude": geo_location.find(
                            "./datacite:geoLocationPoint/datacite:pointLongitude"
                        ),
                        "point_latitude": geo_location.find(
                            "./datacite:geoLocationPoint/datacite:pointLatitude"
                        ),
                    }

                # 位置情報（空間）
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/22-.2
                if geo_location.find("./datacite:geoLocationBox"):
                    d["geo_location_box"] = {
                        "west_bound_longitude": geo_location.find(
                            "./datacite:geoLocationBox/datacite:westBoundLongitude"
                        ),
                        "east_bound_longitude": geo_location.find(
                            "./datacite:geoLocationBox/datacite:eastBoundLongitude"
                        ),
                        "south_bound_latitude": geo_location.find(
                            "./datacite:geoLocationBox/datacite:southBoundLatitude"
                        ),
                        "north_bound_latitude": geo_location.find(
                            "./datacite:geoLocationBox/datacite:northBoundLatitude"
                        ),
                    }

                # 位置情報（自由記述）
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/22-.2
                geo_location_places = []
                for geo_location_place in geo_location.findall(
                    "./datacite:geoLocationPlace"
                ):
                    geo_location_places.append(geo_location_place.text)
                if len(geo_location_places) > 0:
                    d["geo_location_place"] = geo_location_places

                geo_locations.append(d)

        # 23 助成情報
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/23
        funding_references = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:fundingReference", ns) is not None:
            funding_references = []
            for funding_reference in record.xml.findall(
                ".//jpcoar:jpcoar/jpcoar:fundingReference", ns
            ):
                d = {}
                # 助成機関識別子
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/23-.1
                funder_identifier = funding_reference.find(
                    "./jpcoar:funderIdentifier", ns
                )
                if funder_identifier is None:
                    funder_identifier = funding_reference.find(
                        "./datacite:funderIdentifier", ns
                    )
                if funder_identifier is not None:
                    d["funder_identifier"] = {
                        "funder_identifier": funder_identifier.text,
                        "funder_identifier_type": funder_identifier.get(
                            "funderIdentifierType"
                        ),
                    }
                    if funder_identifier.get("funderIdentifierTypeURI"):
                        d["funder_identifier"]["funder_identifier_type_url"] = (
                            funder_identifier.get("funderIdentifierTypeURI")
                        )

                # 助成機関名
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/23-.2
                funder_names = None
                if funding_reference.find("./jpcoar:funderName", ns) is not None:
                    funder_names = []
                    for funder_name in funding_reference.findall(
                        "./jpcoar:funderName", ns
                    ):
                        d_name = {"funder_name": funder_name.text}
                        lang = funder_name.get(
                            "{http://www.w3.org/XML/1998/namespace}lang"
                        )
                        if lang is not None:
                            d_name["lang"] = lang
                        funder_names.append(d_name)
                    d["funder_name"] = funder_names

                # プログラム情報識別子
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/23-.3
                funding_stream_identifier = funding_reference.find(
                    "./jpcoar:fundingStreamIdentifier", ns
                )
                if funding_stream_identifier is not None:
                    d["funding_stream_identifier"] = {
                        "funding_stream_identifier": funding_stream_identifier.text
                    }
                    if funding_stream_identifier.get("fundingStreamIdentifierType"):
                        d["funding_stream_identifier"][
                            "funding_stream_identifier_type"
                        ] = funding_stream_identifier.get("fundingStreamIdentifierType")
                    if funding_stream_identifier.get("fundingStreamIdentifierTypeURI"):
                        d["funding_stream_identifier"][
                            "funding_stream_identifier_type_uri"
                        ] = funding_stream_identifier.get(
                            "fundingStreamIdentifierTypeURI"
                        )

                # プログラム情報
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/23-.4
                funding_streams = None
                if funding_reference.find("./jpcoar:fundingStream", ns) is None:
                    funding_streams = []
                    for funding_stream in funding_reference.findall(
                        "./jpcoar:fundingStream", ns
                    ):
                        d = {"funding_stream": funding_stream.text}
                        lang = funding_stream.get(
                            "{http://www.w3.org/XML/1998/namespace}lang"
                        )
                        if lang is not None:
                            d["lang"] = lang
                        funding_streams.append(d)
                    d["funding_stream"] = funding_streams

                # 研究課題番号
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/23-.5
                # https://schema.irdb.nii.ac.jp/ja/schema/1.0.2/22-.3
                award_number = funding_reference.find("./jpcoar:awardNumber", ns)
                if award_number is None:
                    award_number = funding_reference.find("./datacite:awardNumber", ns)
                if award_number is not None:
                    d["award_number"] = {"award_number": award_number.text}
                    if award_number.get("awardURI"):
                        d["award_number"]["award_number_url"] = award_number.get(
                            "awardURI"
                        )
                    if award_number.get("awardNumberType"):
                        d["award_number"]["award_number_type"] = award_number.get(
                            "awardNumberType"
                        )

                # 研究課題名
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/23-.6
                award_titles = []
                for award_title in funding_reference.findall("./jpcoar:awardTitle", ns):
                    d_title = {"award_title": award_title.text}
                    lang = award_title.get("{http://www.w3.org/XML/1998/namespace}lang")
                    if lang is not None:
                        d_title["lang"] = lang
                    award_titles.append(d_title)
                d["award_title"] = award_titles

                funding_references.append(d)

        # 24 収録物識別子
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/24
        source_identifiers = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:sourceIdentifier", ns) is not None:
            source_identifiers = []
            for source_identifier in record.xml.findall(
                ".//jpcoar:jpcoar/jpcoar:sourceIdentifier", ns
            ):
                source_identifiers.append(
                    {
                        "identifier": source_identifier.text,
                        "identifier_type": source_identifier.get("identifierType"),
                    }
                )

        # 25 収録物名
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/25
        source_titles = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:sourceTitle", ns) is not None:
            source_titles = []
            for source_title in record.xml.findall(
                ".//jpcoar:jpcoar/jpcoar:sourceTitle", ns
            ):
                d = {"source_title": source_title.text}
                lang = source_title.get("{http://www.w3.org/XML/1998/namespace}lang")
                if lang is not None:
                    d["lang"] = lang
                source_titles.append(d)

        # 26 巻
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/26
        volume = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:volume", ns) is not None:
            volume = record.xml.find(".//jpcoar:jpcoar/jpcoar:volume", ns).text

        # 27 号
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/27
        issue = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:issue", ns) is not None:
            issue = record.xml.find(".//jpcoar:jpcoar/jpcoar:issue", ns).text

        # 28 ページ数
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/28
        num_pages = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:numPages", ns) is not None:
            num_pages = record.xml.find(".//jpcoar:jpcoar/jpcoar:numPages", ns).text

        # 29 開始ページ
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/29
        page_start = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:pageStart", ns) is not None:
            page_start = record.xml.find(".//jpcoar:jpcoar/jpcoar:pageStart", ns).text

        # 30 終了ページ
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/30
        page_end = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:pageEnd", ns) is not None:
            page_end = record.xml.find(".//jpcoar:jpcoar/jpcoar:pageEnd", ns).text

        # 31 学位授与番号
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/31
        dissertation_number = None
        if record.xml.find(".//jpcoar:jpcoar/dcndl:dissertationNumber", ns) is not None:
            dissertation_number = record.xml.find(
                ".//jpcoar:jpcoar/dcndl:dissertationNumber", ns
            ).text

        # 32 学位名
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/32
        degree_names = None
        if record.xml.find(".//jpcoar:jpcoar/dcndl:degreeName", ns) is not None:
            degree_names = []
            for degree_name in record.xml.findall(
                ".//jpcoar:jpcoar/dcndl:degreeName", ns
            ):
                d = {"degree_name": degree_name.text}
                lang = degree_name.get("{http://www.w3.org/XML/1998/namespace}lang")
                if lang is not None:
                    d["lang"] = lang
                degree_names.append(d)

        # 33 学位授与年月日
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/33
        date_granted = None
        if record.xml.find(".//jpcoar:jpcoar/dcndl:dateGranted", ns) is not None:
            date_granted = record.xml.find(
                ".//jpcoar:jpcoar/dcndl:dateGranted", ns
            ).text

        # 34 学位授与機関
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/34
        degree_grantors = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:degreeGrantor", ns) is not None:
            degree_grantors = []
            for degree_grantor in record.xml.findall(
                ".//jpcoar:jpcoar/jpcoar:degreeGrantor", ns
            ):
                # 学位授与機関識別子
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/34-.1
                degree_grantor_identifiers = None
                if degree_grantor.find("./jpcoar:nameIdentifier", ns) is not None:
                    degree_grantor_identifiers = []
                    for degree_grantor_identifier in degree_grantor.findall(
                        "./jpcoar:nameIdentifier", ns
                    ):
                        d = {"identifier": degree_grantor_identifier.text}
                        if degree_grantor_identifier.get("nameIdentifierScheme"):
                            d["name_identifier_scheme"] = degree_grantor_identifier.get(
                                "nameIdentifierScheme"
                            )
                        degree_grantor_identifiers.append(d)

                # 学位授与機関名
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/34-.2
                degree_grantor_names = None
                if degree_grantor.find("./jpcoar:degreeGrantorName", ns) is not None:
                    degree_grantor_names = []
                    for degree_grantor_name in degree_grantor.findall(
                        "./jpcoar:degreeGrantorName", ns
                    ):
                        d = {"name": degree_grantor_name.text}
                        lang = degree_grantor_name.get(
                            "{http://www.w3.org/XML/1998/namespace}lang"
                        )
                        if lang is not None:
                            d["lang"] = lang
                        degree_grantor_names.append(d)

                degree_grantors.append(
                    {
                        "name_identifier": degree_grantor_identifiers,
                        "degree_grantor_name": degree_grantor_names,
                    }
                )

        # 35 会議記述
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/35
        conferences = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:conference", ns) is not None:
            conferences = []
            for conference in record.xml.findall(
                ".//jpcoar:jpcoar/jpcoar:conference", ns
            ):
                # 会議名
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/35-.1
                conference_names = []
                for conference_name in conference.findall(
                    "./jpcoar:conferenceName", ns
                ):
                    d = {"conference_name": conference_name.text}
                    lang = conference_name.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang is not None:
                        d["lang"] = lang
                    conference_names.append(d)

                # 回次
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/35-.2
                sequence = conference.find("./jpcoar:conferenceSequence", ns)

                # 主催機関
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/35-.3
                conference_sponsors = None
                if conference.find("./jpcoar:conferenceSponsor", ns) is not None:
                    conference_sponsors = []
                    for conference_sponsor in conference.findall(
                        "./jpcoar:conferenceSponsor", ns
                    ):
                        d = {"conference_sponsor": conference_sponsor.text}
                        lang = conference_sponsor.get(
                            "{http://www.w3.org/XML/1998/namespace}lang"
                        )
                        if lang is not None:
                            d["lang"] = lang
                        conference_sponsors.append(d)

                # 開催期間
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/35-.4
                conference_date = None
                conf_date = conference.find("./jpcoar:conferenceDate", ns)
                if conf_date is not None:
                    conference_date = {}
                    if conf_date.get("startDay"):
                        conference_date["start_day"] = conf_date["startDay"]
                    if conf_date.get("startMonth"):
                        conference_date["start_month"] = conf_date["startMonth"]
                    if conf_date.get("startYear"):
                        conference_date["start_year"] = conf_date["startYear"]
                    if conf_date.get("endDay"):
                        conference_date["end_day"] = conf_date["endDay"]
                    if conf_date.get("endMonth"):
                        conference_date["end_month"] = conf_date["endMonth"]
                    if conf_date.get("endYear"):
                        conference_date["end_year"] = conf_date["endYear"]

                # 開催会場
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/35-.5
                conference_venues = None
                if conference.find("./jpcoar:conferenceVenue", ns) is not None:
                    conference_venues = []
                    for conference_venue in conference.findall(
                        "./jpcoar:conferenceVenue", ns
                    ):
                        d = {"conference_venue": conference_venue.text}
                        lang = conference_venue.get(
                            "{http://www.w3.org/XML/1998/namespace}lang"
                        )
                        if lang is not None:
                            d["lang"] = lang
                        conference_venues.append(d)

                # 開催地
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/35-.6
                conference_places = None
                if conference.find("./jpcoar:conferencePlace", ns) is not None:
                    conference_places = []
                    for conference_place in conference.findall(
                        "./jpcoar:conferencePlace", ns
                    ):
                        d = {"conference_place": conference_place.text}
                        lang = conference_place.get(
                            "{http://www.w3.org/XML/1998/namespace}lang"
                        )
                        if lang is not None:
                            d["lang"] = lang
                        conference_places.append(d)

                # 開催国
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/35-.7
                country = conference.find("./jpcoar:conferenceCountry", ns)

                conf = {"conference_name": conference_names}

                if sequence is not None:
                    conf["conference_sequence"] = sequence.text
                if conference_sponsors is not None:
                    conf["conference_sponsor"] = conference_sponsors
                if conference_venues is not None:
                    conf["conference_venue"] = conference_venues
                if conference_places is not None:
                    conf["conference_place"] = conference_places
                if country is not None:
                    conf["conference_country"] = country.text

                conferences.append(conf)

        # 36 版
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/36
        editions = None
        if record.xml.find(".//jpcoar:jpcoar/dcndl:edition", ns) is not None:
            editions = []
            for edition in record.xml.findall(".//jpcoar:jpcoar/dcndl:edition", ns):
                d = {"edition": edition.text}
                lang = edition.get("{http://www.w3.org/XML/1998/namespace}lang")
                if lang is not None:
                    d["lang"] = lang
                editions.append(d)

        # 37 部編名
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/37
        volume_titles = None
        if record.xml.find(".//jpcoar:jpcoar/dcndl:volumeTitle", ns) is not None:
            volume_titles = []
            for volume_title in record.xml.findall(
                ".//jpcoar:jpcoar/dcndl:volumeTitle", ns
            ):
                d = {"volume_title": volume_title.text}
                lang = volume_title.get("{http://www.w3.org/XML/1998/namespace}lang")
                if lang is not None:
                    d["lang"] = lang
                volume_titles.append(d)

        # 38 原文の言語
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/38
        original_languages = None
        if record.xml.find(".//jpcoar:jpcoar/dcndl:originalLanguage", ns) is not None:
            original_languages = []
            for original_language in record.xml.findall(
                ".//jpcoar:jpcoar/dcndl:originalLanguage", ns
            ):
                original_languages.append(original_language.text)

        # 39 大きさ
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/39
        extents = None
        if record.xml.find(".//jpcoar:jpcoar/dcterms:extent", ns) is not None:
            extents = []
            for extent in record.xml.findall(".//jpcoar:jpcoar/dcterms:extent", ns):
                d = {"extent": extent.text}
                lang = extent.get("{http://www.w3.org/XML/1998/namespace}lang")
                if lang is not None:
                    d["lang"] = lang
                extents.append(d)

        # 40 物理的形態
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/40
        formats = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:format", ns) is not None:
            formats = []
            for format in record.xml.findall(".//jpcoar:jpcoar/jpcoar:format", ns):
                d = {"format": format.text}
                lang = format.get("{http://www.w3.org/XML/1998/namespace}lang")
                if lang is not None:
                    d["lang"] = lang
                formats.append(d)

        # 41 所蔵機関
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/41
        holding_agent = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:holdingAgent", ns) is not None:
            dataset_series = record.xml.find(
                ".//jpcoar:jpcoar/jpcoar:datasetSeries", ns
            ).text

        # 42 データセットシリーズ
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/42
        dataset_series = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:datasetSeries", ns) is not None:
            dataset_series = record.xml.find(
                ".//jpcoar:jpcoar/jpcoar:datasetSeries", ns
            ).text

        # 43 ファイル情報
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/43
        files = None
        if record.xml.find(".//jpcoar:jpcoar/jpcoar:file", ns) is not None:
            files = []
            for file in record.xml.findall(".//jpcoar:jpcoar/jpcoar:file", ns):
                # 本文URI
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/43-.1
                file_uri = None
                if file.find("./jpcoar:URI", ns) is not None:
                    file_uri = file.find("./jpcoar:URI", ns).text

                # ファイルフォーマット
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/43-.2
                file_mime_type = None
                if file.find("./jpcoar:mimeType", ns) is not None:
                    file_mime_type = file.find("./jpcoar:mimeType", ns).text

                # サイズ
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/43-.3
                file_extents = None
                if file.find("./jpcoar:extent", ns) is not None:
                    file_extents = []
                    for extent in file.findall("./jpcoar:extent", ns):
                        file_extents.append(extent.text)

                # 日付
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/43-.4
                file_dates = None
                if file.find("./datacite:date", ns) is not None:
                    file_dates = []
                    for date in file.findall("./datacite:date", ns):
                        file_dates.append(
                            {"date": date.text, "date_type": date.get("dateType")}
                        )

                # バージョン情報
                # https://schema.irdb.nii.ac.jp/ja/schema/2.0/43-.5
                file_version = None
                v = file.find("./datacite:version", ns)
                if v is not None:
                    file_version = v.text

                if file_uri is not None:
                    d = {"uri": file_uri}
                if file_mime_type is not None:
                    d["mime_type"] = file_mime_type
                if file_extents is not None:
                    d["extent"] = file_extents
                if file_dates is not None:
                    if len(file_dates) > 0:
                        d["date"] = file_dates
                if file_version is not None:
                    d["version"] = file_version

                if d.get("uri") is not None:
                    files.append(d)

        # 44 カタログ
        # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44
        c = record.xml.find(".//jpcoar:jpcoar/jpcoar:catalog", ns)
        catalog = None
        if c is not None:
            # 提供機関
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.1
            if c.find("./jpcoar:contributor", ns) is not None:
                catalog_contributors = []
                for catalog_contributor in c.findall("./jpcoar:contributor", ns):
                    d = {"contributor_name": catalog_contributor.text}
                    lang = catalog_contributor.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang is not None:
                        d["lang"] = lang
                    catalog_contributors.append(d)

            # 識別子
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.2
            if c.find("./jpcoar:identifier", ns) is not None:
                catalog_identifiers = []
                for catalog_identifier in c.findall("./jpcoar:identifier", ns):
                    catalog_identifiers.append(catalog_identifier.text)

            # タイトル
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.3
            if c.find("./jpcoar:title", ns) is not None:
                catalog_titles = []
                for title in c.findall("./jpcoar:title", ns):
                    d = {"title": title.text}
                    lang = title.get("{http://www.w3.org/XML/1998/namespace}lang")
                    if lang is not None:
                        d["lang"] = lang
                    catalog_titles.append(d)

            # 内容記述
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.4
            catalog_descriptions = None
            if c.find("./datacite:description", ns) is not None:
                catalog_descriptions = []
                for description in c.findall("./datacite:description", ns):
                    d = {"description": description.text}
                    description_type = description.get("descriptionType")
                    if description_type is not None:
                        d["description_type"] = description_type
                    lang = description.get("{http://www.w3.org/XML/1998/namespace}lang")
                    if lang is not None:
                        d["lang"] = lang
                    catalog_descriptions.append(d)

            # 主題
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.5
            catalog_subjects = None
            if c.find("./jpcoar:subject", ns) is not None:
                catalog_subjects = []
                for subject in c.findall("./jpcoar:subject", ns):
                    d = {"subject": subject.text}
                    lang = subject.get("{http://www.w3.org/XML/1998/namespace}lang")
                    if lang is not None:
                        d["lang"] = lang
                    catalog_subjects.append(d)

            # ライセンス
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.6
            catalog_licenses = None
            if c.find("./jpcoar:license", ns) is not None:
                catalog_licenses = []
                for catalog_license in c.findall("./jpcoar:license", ns):
                    d = {"license": catalog_license.text}
                    license_type = catalog_license.get("licenseType")
                    if license_type is not None:
                        d["license_type"] = license_type
                    license_url = catalog_license.get("rdf:resource")
                    if license_url is not None:
                        d["license_uri"] = license_url
                    lang = catalog_license.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang is not None:
                        d["lang"] = lang
                    catalog_licenses.append(d)

            # 権利情報
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.7
            catalog_rights = None
            if c.find("./dc:rights", ns) is not None:
                for catalog_right in c.findall("./dc:rights", ns):
                    d = {"rights": catalog_right.text}
                    rights_url = catalog_right.get("rdf:resource")
                    if rights_url is not None:
                        d["rights_uri"] = rights_url
                    lang = catalog_right.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang is not None:
                        d["lang"] = lang
                    catalog_rights.append(d)

            # アクセス権
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.8
            catalog_access_rights = c.find("./dcterms:accessRights", ns)

            # 代表画像
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/44-.9
            c_file = c.find("./jpcoar:file", ns)
            catalog_file = None
            if c_file is not None:
                catalog_file = {"uri": c_file.text}
                if c_file.get("objectType"):
                    catalog_file["object_type"] = c_file.get("objectType")

            catalog = {}
            if catalog_identifiers is not None:
                catalog["identifier"] = catalog_identifiers
            if catalog_titles is not None:
                catalog["title"] = catalog_titles
            if catalog_descriptions is not None:
                catalog["description"] = catalog_descriptions
            if catalog_subjects is not None:
                catalog["subject"] = catalog_subjects
            if catalog_licenses is not None:
                catalog["license"] = catalog_licenses
            if catalog_rights is not None:
                catalog["rights"] = catalog_rights
            if catalog_access_rights is not None:
                catalog["access_rights"] = catalog_access_rights.text
            if catalog_file is not None:
                catalog["file"] = catalog_file

        entry = {
            "title": titles,
            "alternative": alternatives,
            "creator": creators,
            "contributor": contributors,
            "acccess_rights": access_rights,
            "rights": rights,
            "rights_holder": rights_holders,
            "subject": subjects,
            "description": descriptions,
            "publisher": publishers,
            "jpcoar_publisher": jpcoar_publishers,
            "date": dates,
            "dcterms_date": dcterms_dates,
            "language": languages,
            "type": resource_type,
            "version": version,
            "text_version": text_version,
            "identifier": identifiers,
            "identifier_registration": identifier_registration,
            "relation": relations,
            "temporal": temporals,
            "geo_location": geo_locations,
            "funding_reference": funding_references,
            "source_identifier": source_identifiers,
            "source_title": source_titles,
            "volume": volume,
            "issue": issue,
            "num_pages": num_pages,
            "page_start": page_start,
            "page_end": page_end,
            "dissertation_number": dissertation_number,
            "degree_name": degree_names,
            "date_granted": date_granted,
            "degree_grantor": degree_grantors,
            "conference": conferences,
            "edition": editions,
            "volume_title": volume_titles,
            "original_language": original_languages,
            "extent": extents,
            "format": formats,
            "holding_agent": holding_agent,
            "dataset_series": dataset_series,
            "file": files,
            "catalog": catalog,
        }

        # 値が空のキーを削除
        filtered_entry = {k: v for (k, v) in entry.items() if v is not None}

        if titles == []:
            # タイトルが空の場合、仮タイトルを設定
            title = "__title_is_blank__"
        else:
            # タイトルの改行コードを削除、先頭50文字のみを取得
            title = re.sub(
                r'[<>:"/\\|?*]', "_", " ".join(titles[0]["title"].splitlines())[:50]
            ).strip()

        dir_name = f"./{export_dir}/{identifier}_{title}"
        os.makedirs(dir_name, exist_ok=True)

        # ファイルのダウンロード
        if metadata_only is False:
            if files is not None:
                for file in files:
                    if file.get("uri") is not None:
                        if (
                            urlparse(file["uri"]).hostname
                            == urlparse(base_url).hostname
                            and urlparse(file["uri"]).scheme
                            == urlparse(base_url).scheme
                        ):
                            response = requests.get(file["uri"], allow_redirects=False)
                            if response.status_code == requests.codes.ok:
                                with open(
                                    f"{dir_name}/{file['uri'].split('/')[-1]}", "wb"
                                ) as f:
                                    f.write(response.content)
                                    logger.debug(f"downloaded {file['uri']}")
                            else:
                                logger.debug(f"skipped {file['uri']}")

        # メタデータの作成
        with open(f"{dir_name}/jpcoar20.yaml", "w", encoding="utf-8") as file:
            yaml.dump(filtered_entry, file)

        with open(f"{dir_name}/jpcoar20.yaml", "r+", encoding="utf-8") as file:
            content = file.read()
            file.seek(0, 0)
            file.write(
                "# yaml-language-server: $schema=../../schema/jpcoar.json\n\n" + content
            )
        logger.debug(f"created {dir_name}/jpcoar20.yaml")


def add_creator(record, ns):
    creators = None
    if record.xml.find(".//jpcoar:jpcoar/jpcoar:creator", ns) is not None:
        creators = []
        for creator in record.xml.findall(".//jpcoar:jpcoar/jpcoar:creator", ns):
            # 作成者識別子
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/3-.1
            creator_name_identifiers = []
            if creator.find("./jpcoar:nameIdentifier", ns) is not None:
                for name_identifier in creator.findall("./jpcoar:nameIdentifier", ns):
                    scheme = name_identifier.get("nameIdentifierScheme")
                    if scheme == "e-Rad":
                        scheme = "e-Rad_Researcher"
                    d = {"identifier_scheme": scheme}
                    if name_identifier.get("nameIdentifierURI") is not None:
                        d["identifier"] = name_identifier.get("nameIdentifierURI")
                    else:
                        d["identifier"] = name_identifier.text
                    creator_name_identifiers.append(d)

            # 作成者姓名
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/3-.2
            creator_names = []
            if creator.find("./jpcoar:creatorName", ns) is not None:
                for creator_name in creator.findall("./jpcoar:creatorName", ns):
                    d = {"name": creator_name.text}
                    lang = creator_name.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang is not None:
                        d["lang"] = lang
                    creator_names.append(d)

            # 作成者姓
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/3-.3
            creator_family_names = None
            if creator.find("./jpcoar:familyName", ns) is not None:
                creator_family_names = []
                for creator_family_name in creator.findall("./jpcoar:familyName", ns):
                    d = {"name": creator_family_name.text}
                    lang = creator_family_name.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang is not None:
                        d["lang"] = lang
                    creator_family_names.append(d)

            # 作成者名
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/3-.4
            creator_given_names = None
            if creator.find("./jpcoar:givenName", ns) is not None:
                creator_given_names = []
                for creator_given_name in creator.findall("./jpcoar:givenName", ns):
                    d = {"name": creator_given_name.text}
                    lang = creator_given_name.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang is not None:
                        d["lang"] = lang
                    creator_given_names.append(d)

            # 作成者別名
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/3-.5
            creator_alternatives = None
            if creator.find("./jpcoar:Alternative", ns) is not None:
                creator_alternatives = []
                for creator_alternative in creator.findall("./jpcoar:Alternative", ns):
                    d = {"name": creator_alternative.text}
                    lang = creator_alternative.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang is not None:
                        d["lang"] = lang
                    creator_alternatives.append(d)

            # 作成者所属
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/3-.6
            creator_affiliations = []
            if creator.find("./jpcoar:affiliation", ns) is not None:
                for affiliation in creator.findall("./jpcoar:affiliation", ns):
                    # 所属機関識別子
                    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/3-.6-.1
                    name_identifiers = []
                    for name_identifier in affiliation.findall(
                        "./jpcoar:nameIdentifier", ns
                    ):
                        d = {
                            "identifier_scheme": name_identifier.get(
                                "nameIdentifierScheme"
                            ),
                            "identifier": name_identifier.text,
                        }
                        if name_identifier.get("nameIdentifierURI"):
                            d["name_identifier_uri"] = name_identifier.get(
                                "nameIdentifierURI"
                            )
                        name_identifiers.append(d)

                    # 所属機関名
                    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/3-.6-.2
                    affiliation_names = []
                    for affiliation_name in affiliation.findall(
                        "./jpcoar:affiliationName", ns
                    ):
                        d = {"name": affiliation_name.text}
                        lang = affiliation_name.get(
                            "{http://www.w3.org/XML/1998/namespace}lang"
                        )
                        if lang is not None:
                            d["lang"] = lang
                        affiliation_names.append(d)

                    creator_affiliations.append(
                        {
                            "name_identifier": name_identifiers,
                            "affiliation_name": affiliation_names,
                        }
                    )

            creators.append(
                {
                    "name_identifier": creator_name_identifiers,
                    "creator_name": creator_names,
                    "affiliation": creator_affiliations,
                }
            )

    return creators


def add_contributor(record, ns):
    contributors = None
    if record.xml.find(".//jpcoar:jpcoar/jpcoar:contributor", ns) is not None:
        contributors = []
        for contributor in record.xml.findall(
            ".//jpcoar:jpcoar/jpcoar:contributor", ns
        ):
            # 寄与者識別子
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/4-.1
            contributor_name_identifiers = []
            if contributor.find("./jpcoar:nameIdentifier", ns) is not None:
                for name_identifier in contributor.findall(
                    "./jpcoar:nameIdentifier", ns
                ):
                    scheme = name_identifier.get("nameIdentifierScheme")
                    if scheme == "e-Rad":
                        scheme = "e-Rad_Researcher"
                    d = {"identifier_scheme": scheme}
                    if name_identifier.get("nameIdentifierURI") is not None:
                        d["identifier"] = name_identifier.get("nameIdentifierURI")
                    else:
                        d["identifier"] = name_identifier.text
                    contributor_name_identifiers.append(d)

            # 寄与者姓名
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/4-.2
            contributor_names = []
            if contributor.find("./jpcoar:contributorName", ns) is not None:
                for contributor_name in contributor.findall(
                    "./jpcoar:contributorName", ns
                ):
                    d = {"name": contributor_name.text}
                    lang = contributor_name.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang is not None:
                        d["lang"] = lang
                    contributor_names.append(d)

            # 寄与者姓
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/4-.3
            contributor_family_names = None
            if contributor.find("./jpcoar:familyName", ns) is not None:
                contributor_family_names = []
                for contributor_family_name in contributor.findall(
                    "./jpcoar:familyName", ns
                ):
                    d = {"name": contributor_family_name.text}
                    lang = contributor_family_name.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang is not None:
                        d["lang"] = lang
                    contributor_family_names.append(d)

            # 寄与者名
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/4-.4
            contributor_given_names = None
            if contributor.find("./jpcoar:givenName", ns) is not None:
                contributor_given_names = []
                for contributor_given_name in contributor.findall(
                    "./jpcoar:givenName", ns
                ):
                    d = {"name": contributor_given_name.text}
                    lang = contributor_given_name.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang is not None:
                        d["lang"] = lang
                    contributor_given_names.append(d)

            # 寄与者別名
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/4-.5
            contributor_alternatives = None
            if contributor.find("./jpcoar:Alternative", ns) is not None:
                contributor_alternatives = []
                for contributor_alternative in contributor.findall(
                    "./jpcoar:Alternative", ns
                ):
                    d = {"name": contributor_alternative.text}
                    lang = contributor_alternative.get(
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    )
                    if lang is not None:
                        d["lang"] = lang
                    contributor_alternatives.append(d)

            # 寄与者所属
            # https://schema.irdb.nii.ac.jp/ja/schema/2.0/4-.6
            contributor_affiliations = []
            if contributor.find("./jpcoar:affiliation", ns) is not None:
                for affiliation in contributor.findall("./jpcoar:affiliation", ns):
                    # 所属機関識別子
                    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/4-.6-.1
                    name_identifiers = []
                    for name_identifier in affiliation.findall(
                        "./jpcoar:nameIdentifier", ns
                    ):
                        d = {
                            "identifier_scheme": name_identifier.get(
                                "nameIdentifierScheme"
                            ),
                            "identifier": name_identifier.text,
                        }
                        if name_identifier.get("nameIdentifierURI"):
                            d["name_identifier_uri"] = name_identifier.get(
                                "nameIdentifierURI"
                            )
                        name_identifiers.append(d)

                    # 所属機関名
                    # https://schema.irdb.nii.ac.jp/ja/schema/2.0/4-.6-.2
                    affiliation_names = []
                    for affiliation_name in affiliation.findall(
                        "./jpcoar:affiliationName", ns
                    ):
                        d = {"name": affiliation_name.text}
                        lang = affiliation_name.get(
                            "{http://www.w3.org/XML/1998/namespace}lang"
                        )
                        if lang is not None:
                            d["lang"] = lang
                        affiliation_names.append(d)

                    contributor_affiliations.append(
                        {
                            "name_identifier": name_identifiers,
                            "affiliation_name": affiliation_names,
                        }
                    )

            contributors.append(
                {
                    "contributor_type": contributor.get("contributorType"),
                    "name_identifier": contributor_name_identifiers,
                    "contributor_name": contributor_names,
                    "affiliation": contributor_affiliations,
                }
            )

    return contributors
