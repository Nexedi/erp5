from Products.ZSQLCatalog.SQLCatalog import Query, SimpleQuery, ComplexQuery

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

portal_type_query = ComplexQuery(Query(portal_type='Data Stream'),
                                 Query(portal_type='Data Array'),
                                 Query(portal_type='Data Descriptor'),
                                 Query(portal_type='Data Ingestion'),
                                 Query(portal_type='Data Analysis'),
                                 logical_operator="OR")
kw_dict = {"query": portal_type_query,
           "reference": reference}

for document in portal_catalog(**kw_dict):
  portal.InvalidateReference(document)
  try:
    document.invalidate()
  except:
    pass # fails if it's already invalidated, draft or if it doens't allow invalidation (e.g. DI)
