"""
  This method returns the list of searchable types
  from a document management point of view.

  The result is translated and cached.

  NOTE: some hardcoded values need to be moved
  to preferences
"""
def getSearchableTypeList(language):
  type_list = list(context.getPortalDocumentTypeList())
  # We add here hardcoded types
  types_tools = context.portal_types
  type_ids = types_tools.objectIds()
  if 'Query' in type_ids:
    type_list.append('Query')
  if 'Project' in type_ids:
    type_list.append('Project')
  if 'Conference' in type_ids:
    type_list.append('Conference')
  type_list.sort()
  return type_list

from Products.ERP5Type.Cache import CachingMethod
language = context.Localizer.get_selected_language()
method = CachingMethod(getSearchableTypeList, ('WebSite_getSearchableTypeList'))

return method(language)
