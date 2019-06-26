from Products.ZSQLCatalog.SQLCatalog import Query, SimpleQuery, ComplexQuery

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

try:
  if success: # full split ingestions successfully appendend
    # invalidate old ingestion objects
    data_stream = portal_catalog.getResultValue(
      portal_type = 'Data Stream',
      reference = reference,
      validation_state = "validated")
    if data_stream != None:
      data_ingestion = portal_catalog.getResultValue(
        portal_type = 'Data Ingestion',
        id = data_stream.getId())
      portal.InvalidateReference(data_stream)
      data_stream.invalidate()
      if not portal.IsReferenceInvalidated(data_ingestion):
        portal.InvalidateReference(data_ingestion)
      data_an = portal_catalog.getResultValue(
        portal_type = 'Data Analysis',
        id = data_stream.getId())
      if data_an != None:
        portal.InvalidateReference(data_an)
      data_array = portal_catalog.getResultValue(
        portal_type = 'Data Array',
        id = data_stream.getId())
      if data_array != None:
        portal.InvalidateReference(data_array)
        data_array.invalidate()
  else: # split ingestion interrumped and restarted
    # invalidate draft datastreams and old started data ingestions
    for data_ingestion in portal_catalog(portal_type = "Data Ingestion",
                                         simulation_state = "started",
                                         reference = reference):
      if not portal.IsReferenceInvalidated(data_ingestion):
        portal.InvalidateReference(data_ingestion)
      data_ingestion.deliver()
    for data_stream in portal_catalog(portal_type = "Data Stream",
                                         validation_state = "draft",
                                         reference = reference):
      if not portal.IsReferenceInvalidated(data_stream):
        portal.InvalidateReference(data_stream)
except Exception as e:
  context.logEntry("ERROR in ERP5Site_invalidateSplitIngestions: " + str(e))
  pass
