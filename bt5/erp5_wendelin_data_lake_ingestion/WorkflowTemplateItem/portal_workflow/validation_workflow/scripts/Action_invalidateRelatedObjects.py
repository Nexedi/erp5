from Products.ZSQLCatalog.SQLCatalog import Query, SimpleQuery

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog
object = state_change['object']

if object.getPortalType() == "Data Set":
  data_set = object
  data_set_prefix = data_set.getReference() + portal.getIngestionReferenceDictionary()["reference_separator"]
  #context.logEntry("Invalidating data set '%s' and dependencies." % data_set.getReference())
  reference_query = Query(**{'reference': data_set_prefix + '%'})
  kw_dict = {"portal_type": "Data Stream",
             "query": reference_query}
  for data_stream in portal_catalog(**kw_dict):
    if data_stream.getReference().startswith(data_set_prefix) and not portal.IsReferenceInvalidated(data_stream):
      portal.ERP5Site_invalidateIngestionObjects(data_stream.getReference())
  portal.InvalidateReference(data_set)
  data_set.setVersion("000")
elif object.getPortalType() == "Data Stream":
  data_stream = object
  portal.ERP5Site_invalidateIngestionObjects(data_stream.getReference())
