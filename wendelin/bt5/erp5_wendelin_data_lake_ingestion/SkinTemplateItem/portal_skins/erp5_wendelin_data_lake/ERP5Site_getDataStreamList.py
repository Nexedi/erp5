"""
This script is called from ebulk client to get list of Data Streams for a Data set.
"""
import json
from erp5.component.module.Log import log

limit=[]
if batch_size:
  limit=[offset, batch_size]

portal = context.getPortalObject()

try:
  data_set = portal.data_set_module.get(data_set_reference)
  if data_set is None or data_set.getReference().endswith("_invalid"):
    return json.dumps({ "status_code": 0, "result": [] })
except Exception as e: # fails because unauthorized access
  log("Unauthorized access to getDataStreamList: " + str(e))
  return json.dumps({ "status_code": 1, "error_message": "401 - Unauthorized access. Please check your user credentials and try again." })

data_set_uid = data_set.getUid()
data_stream_list = context.ERP5Site_getDataStreamList(data_set_uid, limit)

data_stream_dict = {}
for stream_brain in data_stream_list:
  reference = stream_brain.reference
  version = stream_brain.version
  size = stream_brain.size
  data_stream_id = stream_brain.relative_url
  data_stream_info_dict = {'id': data_stream_id,
                           'size': size,
                           'hash': version}
  if reference in data_stream_dict:
    data_stream_dict[reference]['data-stream-list'].append(data_stream_info_dict)
    data_stream_dict[reference]['large-hash'] = data_stream_dict[reference]['large-hash'] + str(version)
    data_stream_dict[reference]['full-size'] = int(data_stream_dict[reference]['full-size']) + int(size)
  else:
    data_stream_dict[reference] = { 'data-stream-list': [data_stream_info_dict],
                                    'id': data_stream_id,
                                    'reference': reference,
                                    'large-hash': version,
                                    'full-size': size}

result_dict = { 'status_code': 0, 'result': data_stream_dict.values()}
return json.dumps(result_dict)
