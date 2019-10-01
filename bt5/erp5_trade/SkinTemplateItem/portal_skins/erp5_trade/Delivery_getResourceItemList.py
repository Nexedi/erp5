from Products.ERP5Type.Cache import CachingMethod
portal = context.getPortalObject()

if context.getPortalType() in portal.getPortalSaleTypeList():
  use_list = context.portal_preferences.getPreferredSaleUseList()
elif context.getPortalType() in portal.getPortalPurchaseTypeList():
  use_list = portal.portal_preferences.getPreferredPurchaseUseList()
elif context.getPortalType() in portal.getPortalInternalTypeList():
  use_list = portal.portal_preferences.getPreferredInternalUseList()
else:
  use_list = portal.portal_preferences.getPreferredPurchaseUseList()\
             + portal.portal_preferences.getPreferredSaleUseList()\
             + portal.portal_preferences.getPreferredInternalUseList()

if not use_list:
  return []

sql_kw = {}
try:
  resource_title = cell.resource_title
except AttributeError:
  resource_title = None
try:
  reference = cell.default_reference
except AttributeError:
  reference = None

if resource_title not in (None, ""):
  sql_kw['title'] = resource_title
if reference not in (None, ""):
  sql_kw['reference'] = reference


if len(sql_kw) == 0:
  try:
    if cell.getResourceValue() is not None:
      sql_kw['reference'] = cell.getResourceReference()
      sql_kw['title'] = cell.getResourceTitle()
    else:
      return [('None getResourceValue %s' % cell.getResourceTitle(), '')]
  except AttributeError:
    pass

sql_kw['portal_type'] = portal_type
sql_kw['validation_state'] = validation_state
sql_kw['default_use_uid'] = [context.portal_categories.resolveCategory(use).getUid()
                             for use in use_list]
sql_kw['limit'] = 20

result = []
for resource in portal.portal_catalog.searchResults(sort_on=(('portal_type', 'asc'),
                                                             ('title', 'asc')),
                                                    **sql_kw):
  result.append(
    (resource.getTitle(),
     resource.getRelativeUrl()))

result.append(('Not SQL found %s' % str(sql_kw), ''))
return result
