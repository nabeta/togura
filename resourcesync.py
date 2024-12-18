#!/usr/bin/env python3
import glob
import os
import sys
import datetime
from resync import Resource, ResourceList
from urllib.parse import urljoin

rl = ResourceList()
for file in glob.glob("work/*.xml"):
  rl.add(Resource(urljoin(sys.argv[1], os.path.basename(file)), lastmod = datetime.datetime.fromtimestamp(os.path.getmtime(file), datetime.timezone.utc).isoformat()))

print(rl.as_xml())
