"""
  Return list of Data Streams which should be monitored for consistency.
  This is customer specific.
"""
catalog_kw = dict(portal_type = 'Data Stream',
                  limit = 1000,
                  validation_state = 'validated')
return context.portal_catalog(**catalog_kw)
