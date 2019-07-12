from Products.ZSQLCatalog.SQLCatalog import Query, SimpleQuery

return
# This alarm was deprecated - kept for test

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

# invalidate old (more than 5 hours) pending ingestions (e.g. split ingestions that were canceled/interrumped and no resumed)
from DateTime import DateTime
now = DateTime()
now_minus_max = now - 1.0/24/60*9999
now_minus_5 = now - 1.0/24/60*60*5
catalog_kw = {'creation_date': {'query': (now_minus_max, now_minus_5), 'range': 'minmax'}, 'simulation_state': 'started', 'portal_type': 'Data Ingestion'}

for data_ingestion in portal_catalog(**catalog_kw):
  # search related data ingestions that are not old yet (less than 5 hours)
  catalog_kw = {'creation_date': {'query': (now_minus_5, DateTime()), 'range': 'minmax'},
                'simulation_state': 'started',
                'portal_type': 'Data Ingestion',
                'reference': data_ingestion.getReference()}
  invalidate = True
  if len(portal_catalog(**catalog_kw)) > 0:
    invalidate = False

  if invalidate:
    # invalidate related Data Stream
    kw_dict = {"portal_type": "Data Stream",
               "id": data_ingestion.getId()}
    for data_stream in portal_catalog(**kw_dict):
      if not data_stream.getReference().endswith("_invalid"):
        data_stream.setReference(data_stream.getReference() + "_invalid")
        try:
          data_stream.invalidate()
        except:
          context.logEntry("[WARNING] Could not invalidate data stream '%s', it was already invalidated or draft" % data_stream.getId())
    try:
      if not data_ingestion.getReference().endswith("_invalid"):
        data_ingestion.setReference(data_ingestion.getReference() + "_invalid")
      data_ingestion.deliver()
    except:
      context.logEntry("[WARNING] Could not invalidate/deliver data ingestion '%s', it was already invalidated/deliver" % data_ingestion.getId())
