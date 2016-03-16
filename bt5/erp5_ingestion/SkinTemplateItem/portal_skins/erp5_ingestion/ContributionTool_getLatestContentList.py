"""
  Get latest documents sorted.
"""
kw['portal_type'] = context.getPortalDocumentTypeList()
kw['sort_on'] = (('creation_date', 'descending'),)
return context.portal_catalog(**kw)
