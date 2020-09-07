"""
This script is called from ebulk client to get list of Data Streams for a Data set.
"""

import json
from erp5.component.module.Log import log

portal = context.getPortalObject()

try:
  data_set = portal.data_set_module.get(data_set_reference)
  if data_set is None or portal.ERP5Site_checkReferenceInvalidated(data_set):
    return { "status_code": 0, "result": [] }
except Exception as e: # fails because unauthorized access
  log("Unauthorized access to getDataStreamList: " + str(e))
  return { "status_code": 1, "error_message": "401 - Unauthorized access. Please check your user credentials and try again." }

data_stream_dict = {}
for stream in data_set.DataSet_getDataStreamList():
  if stream and not portal.ERP5Site_checkReferenceInvalidated(stream) and stream.getValidationState() != "draft":
    data_stream_info_dict = { 'id': 'data_stream_module/'+stream.getId(),
                              'size': stream.getSize(),
                              'hash': stream.getVersion() }
    if stream.getReference() in data_stream_dict:
      data_stream_dict[stream.getReference()]['data-stream-list'].append(data_stream_info_dict)
      data_stream_dict[stream.getReference()]['large-hash'] = data_stream_dict[stream.getReference()]['large-hash'] + str(stream.getVersion())
      data_stream_dict[stream.getReference()]['full-size'] = int(data_stream_dict[stream.getReference()]['full-size']) + int(stream.getSize())
    else:
      data_stream_dict[stream.getReference()] = { 'data-stream-list': [data_stream_info_dict],
                                                  'id': 'data_stream_module/'+stream.getId(),
                                                  'reference': stream.getReference(),
                                                  'large-hash': stream.getVersion(),
                                                  'full-size': stream.getSize() }

result_dict = { 'status_code': 0, 'result': data_stream_dict.values()}
return json.dumps(result_dict)
