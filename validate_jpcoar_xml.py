#!/usr/bin/env python3
# JPCOARスキーマのバリデーションを行う
import xmlschema
import sys
schema = xmlschema.XMLSchema("https://raw.githubusercontent.com/JPCOAR/schema/refs/heads/master/2.0/jpcoar_scm.xsd")
schema.validate(sys.argv[1])
