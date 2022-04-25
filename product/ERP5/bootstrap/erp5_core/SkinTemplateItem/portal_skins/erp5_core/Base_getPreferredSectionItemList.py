""" Return the preferred sections.
The sections are of portal type `portal_type` and in state `validation_state`
and are member of the preferred section category (from preferences).

An optional "base_category" can be passed to make sure the currently used
section is returned even if it's not in the list.
"""

from Products.ERP5Type.Cache import CachingMethod
from AccessControl import getSecurityManager

def getPreferredSectionItemList(portal_type, validation_state):
  portal = context.getPortalObject()
  section_category = portal.portal_preferences.getPreferredSectionCategory() or\
                       portal.portal_preferences.getPreferredAccountingTransactionSectionCategory()

  if not section_category:
    return [('', '')]

  group_uid = portal.portal_categories.getCategoryUid(section_category)
  return [('', '')] + [(x.getTitle(), x.getRelativeUrl()) for x in 
                      portal.portal_catalog(portal_type=portal_type,
                                            validation_state=validation_state,
                                            default_group_uid=group_uid,
                                            sort_on=('title',))]

getPreferredSectionItemList = CachingMethod(getPreferredSectionItemList,
                                            '%s.%s' % (script.getId(),
                                              getSecurityManager().getUser().getIdOrUserName()),
                                            cache_factory='erp5_ui_short')
section_item_list = getPreferredSectionItemList(portal_type, validation_state)

if base_category:
  section_item_list = section_item_list[::] # make a copy not to modify the cache value
  current_category = context.getProperty(base_category)
  if current_category and current_category not in list(zip(*section_item_list))[1]:
    section_item_list.append(
        (context.getProperty('%s_title' % base_category),
         context.getProperty(base_category)))

return section_item_list
