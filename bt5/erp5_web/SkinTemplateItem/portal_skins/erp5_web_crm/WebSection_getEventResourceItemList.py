"""Inspired by Event_getResourceItemList
Use Auditor proxy role to let anonymous users accessing resources.
"""

from Products.ERP5Type.Cache import CachingMethod
portal = context.getPortalObject()

sql_kw = {'portal_type': portal.getPortalResourceTypeList(),
          'use_uid': portal.portal_categories.getCategoryUid(portal.portal_preferences.getPreferredEventUse(), base_category='use'),
          'validation_state': 'validated',
          'sort_on': 'title'}

def getResourceItemList():
  return [('', '')] + [(result.getTitle(), result.getRelativeUrl()) for result in portal.portal_catalog(**sql_kw)]

getResourceItemList = CachingMethod(getResourceItemList,
      id=(script.id, context.Localizer.get_selected_language()),
      cache_factory='erp5_ui_long')

return getResourceItemList()
