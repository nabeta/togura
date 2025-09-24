import togura.jpcoar as jpcoar

resource_type_uri = jpcoar.resource_type_uri("article")
if resource_type_uri == "http://purl.org/coar/resource_type/c_6501":
    print("Smoke test succeeded")
else:
    raise RuntimeError(resource_type_uri)
