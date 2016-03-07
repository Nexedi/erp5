from Products.ERP5Type.Cache import CachingMethod

def getLatestModificationDate():
  document = context.getPortalObject().portal_catalog(
    portal_type=("Web Section", "Web Site",) + context.getPortalDocumentTypeList(),
    sort_on=(('modification_date', 'descending'),),
    select_list=('modification_date',),
    limit=1,
    )
  if document:
    return document[0].modification_date
  return getattr(context, 'getModificationDate', context.modified)()

getLatestModificationDate = CachingMethod(
  getLatestModificationDate,
  id="Base_getWebDocumentDrivenModificationDate",
  cache_factory="erp5_content_short",
  )

return getLatestModificationDate()
