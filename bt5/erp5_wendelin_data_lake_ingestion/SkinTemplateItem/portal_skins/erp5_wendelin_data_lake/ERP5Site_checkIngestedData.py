import json
portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

def getDatasetInfo(data_set):
  size = 0
  datastream_result_dict = json.loads(portal.ERP5Site_getDataStreamList(data_set.getReference()))
  for stream_dict in datastream_result_dict['result']:
    size += stream_dict['full-size']
  return len(datastream_result_dict['result']), size

def format_size(num, suffix='b'):
  for unit in ['','K','M','G','T','P','E','Z']:
    if abs(num) < 1024.0:
      return "%3.1f %s%s" % (num, unit, suffix)
    num /= 1024.0
  return "%.1f %s%s" % (num, 'Yi', suffix)

data_set_list = []

if data_set_reference:
  try:
    data_set = portal.data_set_module.get(data_set_reference)
    if data_set is None or portal.ERP5Site_checkReferenceInvalidated(data_set):
      return "Not found: there is no valid dataset for that reference"
    data_set_list.append(data_set)
  except Exception as e: # fails because unauthorized access
    return "ERROR: " + str(e)
else:
  data_set_list = portal_catalog(portal_type="Data Set", validation_state='validated OR published')

total_size = 0
for data_set in data_set_list:
  print "Data set " + data_set.getReference()
  nfiles, size = getDatasetInfo(data_set)
  total_size += size
  print "  #files: " + str(nfiles)
  print "  Size: " + format_size(size)
  print

if len(data_set_list) > 1:
  print
  print "TOTAL SIZE: " + format_size(total_size)

return printed
