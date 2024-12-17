#!/usr/bin/env python3
import sys
import yaml
from xml.dom import minidom
import xml.etree.ElementTree as ET

with open(sys.argv[1]) as file:
  entry = yaml.load(file, Loader = yaml.Loader)

ns = {
  "jpcoar": "https://github.com/JPCOAR/schema/blob/master/2.0/",
  "dc": "http://purl.org/dc/elements/1.1/",
  "dcterms": "http://purl.org/dc/terms/",
  "datacite": "https://schema.datacite.org/meta/kernel-4/",
  "oaire": "http://namespace.openaire.eu/schema/oaire/",
  "dcndl": "http://ndl.go.jp/dcndl/terms/",
  "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
  "xsi": "http://www.w3.org/2001/XMLSchema-instance"
}

for key in ns.keys():
  ET.register_namespace(key, ns[key])

root = ET.Element(ET.QName(ns["jpcoar"], "jpcoar"))
root.set(ET.QName(ns["xsi"], "schemaLocation"), "https://github.com/JPCOAR/schema/blob/master/2.0/ jpcoar_scm.xsd")

for title in entry["title"]:
  elem_title = ET.SubElement(root, ET.QName(ns["dc"], "title"))
  elem_title.text = title["title"]
for creator in entry["creator"]:
  elem_creator = ET.SubElement(root, ET.QName(ns["jpcoar"], "creator"), {"creatorType": "著"})
  for name_identifier in creator["name_identifier"]:
    elem_name_identifier = ET.SubElement(elem_creator, ET.QName(ns["jpcoar"], "nameIdentifier"), {
      "nameIdentifierScheme": name_identifier["identifier_scheme"],
      "nameIdentifierURI": name_identifier["identifier"]
    })
    elem_name_identifier.text = name_identifier["identifier"]
  for creator_name in creator["creator_name"]:
    elem_creator_name = ET.SubElement(elem_creator, ET.QName(ns["jpcoar"], "creatorName"), {"xml:lang": creator_name["lang"]})
    elem_creator_name.text = creator_name["name"]
  for affiliation in creator["affiliation"]:
    elem_affiliation = ET.SubElement(elem_creator, ET.QName(ns["jpcoar"], "affiliation"))
    elem_affiliation_identifier = ET.SubElement(elem_affiliation, ET.QName(ns["jpcoar"], "nameIdentifier"), {
      "nameIdentifierScheme": affiliation["identifier_scheme"],
      "nameIdentifierURI": affiliation["identifier"]
    })
    elem_affiliation_identifier.text = affiliation["identifier"]
    for affiliation_name in affiliation["affiliation_name"]:
      elem_affiliation_name = ET.SubElement(elem_affiliation, ET.QName(ns["jpcoar"], "affiliationName"), {"xml:lang": affiliation_name["lang"]})
      elem_affiliation_name.text = affiliation_name["name"]

elem_access_rights = ET.SubElement(root, ET.QName(ns["dcterms"], "accessRights"))
elem_access_rights.text = entry["access_rights"]

for rights in entry["rights"]:
  elem_rights = ET.SubElement(root, ET.QName(ns["dc"], "rights"), {
    "xml:lang": rights["lang"],
    ET.QName(ns["rdf"], "resource"): rights["rights"]
  })
  elem_rights.text = rights["rights"]

for subject in entry["subject"]:
  elem_subject = ET.SubElement(root, ET.QName(ns["jpcoar"], "subject"), {
    "xml:lang": subject["lang"],
    "subjectScheme": subject["subject_scheme"]
  })
  elem_subject.text = subject["subject"]

for publisher in entry["publisher"]:
  elem_publisher = ET.SubElement(root, ET.QName(ns["dc"], "publisher"), {"xml:lang": publisher["lang"]})
  elem_publisher.text = publisher["publisher"]

for date in entry["date"]:
  elem_date = ET.SubElement(root, ET.QName(ns["datacite"], "date"), {"dateType": date["date_type"]})
  elem_date.text = str(date["date"])

for language in entry["language"]:
  elem_language = ET.SubElement(root, ET.QName(ns["dc"], "language"))
  elem_language.text = language

elem_resource_type = ET.SubElement(root, ET.QName(ns["dc"], "type"))
elem_resource_type.text = entry["type"]

elem_text_version = ET.SubElement(root, ET.QName(ns["oaire"], "version"))
elem_text_version.text = entry["text_version"]

for identifier in entry["identifier"]:
  elem_identifier = ET.SubElement(root, ET.QName(ns["jpcoar"], "identifier"))
  elem_identifier.text = identifier

elem_identifier_registration = ET.SubElement(root, ET.QName(ns["jpcoar"], "identifierRegistration"), {
  "identifierType": entry["identifier_registration"]["identifier_type"]
})
elem_identifier_registration.text = entry["identifier_registration"]["identifier"]

if entry.get("relation"):
  for relation in entry["relation"]:
    elem_relation = ET.SubElement(root, ET.QName(ns["jpcoar"], "relation"), {
      "relationType": relation["relation_type"]
    })
    elem_related_identifier = ET.SubElement(elem_relation, ET.QName(ns["jpcoar"], "relatedIdentifier"))
    elem_related_identifier.text = relation["related_identifier"]

for funding_reference in entry["funding_reference"]:
  elem_funding_reference = ET.SubElement(root, ET.QName(ns["jpcoar"], "fundingReference"))
  elem_funder_identifier = ET.SubElement(elem_funding_reference, ET.QName(ns["jpcoar"], "funderIdentifier"), {
    "funderIdentifierType": funding_reference["funder_identifier_type"]
  })
  elem_funder_identifier.text = funding_reference["funder_identifier"]
  elem_funder_name = ET.SubElement(elem_funding_reference, ET.QName(ns["jpcoar"], "funderName"), {
    "xml:lang": funding_reference["funder_name"]["lang"]
  })
  elem_funder_name.text = funding_reference["funder_name"]["funder_name"]
  elem_funding_stream = ET.SubElement(elem_funding_reference, ET.QName(ns["jpcoar"], "fundingStream"), {
    "xml:lang": funding_reference["funding_stream"]["lang"]
  })
  elem_funding_stream.text = funding_reference["funding_stream"]["funding_stream"]

  elem_award_number = ET.SubElement(elem_funding_reference, ET.QName(ns["jpcoar"], "awardNumber"), {
    "awardURI": funding_reference["award_number"]["award_uri"],
    "awardNumberType": funding_reference["award_number"]["award_number_type"]
   })
  elem_award_number.text = funding_reference["award_number"]["award_number"]

  elem_award_title = ET.SubElement(elem_funding_reference, ET.QName(ns["jpcoar"], "awardTitle"), {
    "xml:lang": funding_reference["award_title"]["lang"]
  })
  elem_award_title.text = funding_reference["award_title"]["award_title"]

for source_identifier in entry["source_identifier"]:
  elem_source_identifier = ET.SubElement(root, ET.QName(ns["jpcoar"], "sourceIdentifier"), {"identifierType": source_identifier["identifier_type"]})
  elem_source_identifier.text = source_identifier["source_identifier"]

for source_title in entry["source_title"]:
  elem_source_title = ET.SubElement(root, ET.QName(ns["jpcoar"], "sourceTitle"), {"xml:lang": source_title["lang"]})
  elem_source_title.text = source_title["source_title"]

volume = ET.SubElement(root, ET.QName(ns["jpcoar"], "volume"))
volume.text = entry["volume"]

issue = ET.SubElement(root, ET.QName(ns["jpcoar"], "issue"))
issue.text = entry["issue"]

num_pages = ET.SubElement(root, ET.QName(ns["jpcoar"], "numPages"))
num_pages.text = str(entry["num_pages"])

page_start = ET.SubElement(root, ET.QName(ns["jpcoar"], "pageStart"))
page_start.text = entry["page_start"]

page_end = ET.SubElement(root, ET.QName(ns["jpcoar"], "pageEnd"))
page_end.text = entry["page_end"]

for file in entry["file"]:
  elem_file = ET.SubElement(root, ET.QName(ns["jpcoar"], "file"))
  elem_file_uri = ET.SubElement(
    elem_file,
    ET.QName(ns["jpcoar"], "URI"),
    {
      "objectType": file["object_type"],
      "label": file["label"]
    }
  )
  elem_file_uri.text = file["uri"]

  for extent in file["extent"]:
    elem_file_extent = ET.SubElement(elem_file, ET.QName(ns["jpcoar"], "extent"))
    elem_file_extent.text = extent

  for date in file["date"]:
    elem_file_date = ET.SubElement(elem_file, ET.QName(ns["datacite"], "date"), {"dateType": date["date_type"]})
    elem_file_date.text = str(date["date"])

ET.indent(root, space = "  ", level = 0)
print(ET.tostring(root, encoding = "unicode", xml_declaration = True))
