"""This script invalidate all data sets (and corresponding ingestion objects) older than wendelin.io release (<= 2019)"""

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

from DateTime import DateTime
old_date = DateTime(2019, 12, 31)
catalog_kw = {'modification_date': {'query': old_date, 'range': '<='}}

print "Following Dataset were invalidated:"

for data_set in portal_catalog(portal_type="Data Set", **catalog_kw):
  print
  print "DATASET: " + data_set.getReference()
  print "state: " + data_set.getValidationState()
  print "date: " + str(data_set.getModificationDate())
  print "len of datastream list: " + str(len(data_set.DataSet_getDataStreamList()))
  for data_stream in data_set.DataSet_getDataStreamList():
    if data_stream is not None:
      portal.ERP5Site_invalidateIngestionObjects(data_stream.getReference())
      try:
        data_stream.invalidate()
      except Exception:
        pass # fails if it's already invalidated, draft or if it doens't allow invalidation (e.g. DI)
  portal.ERP5Site_invalidateReference(data_set)
  try:
    data_set.invalidate()
  except Exception:
    pass # fails if it's already invalidated, draft or if it doens't allow invalidation (e.g. DI)
return printed
