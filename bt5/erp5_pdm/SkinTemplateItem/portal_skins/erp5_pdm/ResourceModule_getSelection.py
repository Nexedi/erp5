# JM: a 'preferred_category_display_method_id' preference would be better

def getPreferredCategoryChildItemListMethodId():
  return context.getPortalObject().portal_preferences.getPreference(
    'preferred_category_child_item_list_method_id',
    'getCategoryChildCompactLogicalPathItemList')

def getPreferredCategoryDisplayMethodId():
  method = 'get' + getPreferredCategoryChildItemListMethodId() \
                   [ len('getCategoryChild') : - len('ItemList') ]
  return method == 'getTranslatedCompactTitle' and 'getCompactTranslatedTitle' \
      or method

class ResourceSelection:
  """
  Helper class to handle a selection of resources.
  """
  def getCommonMetricTypeList(self):
    """
    Get the list of metric_type categories
    that are common to all selected resources.
    """
    return [ metric_type['relative_url'].split('/',1)[1]
              for metric_type in self.context.
                ResourceModule_zGetCommonMetricTypeList(
                  resource_uid = self.getUidList()) ]

  def getCommonBaseQuantityUnitSet(self):
    """
    Get the set of possible quantity_unit categories
    for the list of metric_type returned by getCommonMetricTypeList.
    """
    return set([mt.split('/',1)[0] for mt in self.getCommonMetricTypeList()])

  def getCommonMetricTypeItemList(self):
    """
    Similar to getCommonMetricTypeList
    but return the categories as a list of tuples (title, id).
    This is mostly useful in ERP5Form instances to generate selection menus.
    """
    traverse = self.portal.portal_categories['metric_type'].restrictedTraverse
    display = getPreferredCategoryDisplayMethodId()
    return sorted((getattr(traverse(metric_type),display)(), metric_type)
      for metric_type in self.getCommonMetricTypeList())

  def getCommonQuantityUnitItemList(self):
    """
    Similar to getCommonBaseQuantityUnitSet
    but return the categories as a list of tuples (title, id).
    This is mostly useful in ERP5Form instances to generate selection menus.
    """
    traverse = self.portal.portal_categories['quantity_unit'].restrictedTraverse
    display = getPreferredCategoryChildItemListMethodId()
    common_quantity_unit_item_list = []
    for qu in sorted(self.getCommonBaseQuantityUnitSet()):
      common_quantity_unit_item_list.extend(getattr(traverse(qu),display)
        (display_none_category=0, local_sort_id='quantity'))
    return common_quantity_unit_item_list

  def getCommonTransformedResourceItemList(self):
    return [(r.title, r.relative_url) for r in \
     context.Resource_zGetTransformedResourceList(resource_uid=self.getUidList())]

self = ResourceSelection()
self.context = context
self.portal = context.getPortalObject()
uid_list = self.portal.portal_selections \
               .getSelectionCheckedUidsFor(context.REQUEST.selection_name)
if not uid_list:
  raise ValueError('No resource selected.')
self.getUidList = lambda: uid_list


return self
