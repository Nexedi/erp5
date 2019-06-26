import re
import json
from Products.ERP5Type.Log import log
from Products.ZSQLCatalog.SQLCatalog import Query, SimpleQuery, ComplexQuery

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

reference_separator = portal.getIngestionReferenceDictionary()["reference_separator"]

try:
  data_set = portal.data_set_module.get(data_set_reference)
  if data_set is None or portal.IsReferenceInvalidated(data_set):
    return { "status_code": 0, "result": [] }
except Exception as e: # fails because unauthorized access
  log("Unauthorized access to getDataStreamList.")
  return { "status_code": 1, "error_message": "401 - Unauthorized access. Please check your user credentials and try again." }

data_set = portal.data_set_module.get(data_set_reference)
if data_set is None:
  return []

query_dict = {
  "portal_type": "Data Stream",
  "reference": data_set.getReference() + reference_separator + "%",
  "validation_state": 'validated'}

data_stream_list = []

for stream in portal_catalog(**query_dict):
  if stream.getVersion() == "":
    return { "status_code": 2, "result": [] }
  data_stream_list.append({ 'id': 'data_stream_module/'+stream.getId(),
                            'reference': stream.getReference(),
                            'size': stream.getSize(),
                            'hash': stream.getVersion() })

dict = { 'status_code': 0, 'result': data_stream_list }
return json.dumps(dict)
