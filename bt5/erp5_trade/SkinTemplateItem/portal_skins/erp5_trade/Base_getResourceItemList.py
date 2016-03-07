try:
  return container.REQUEST.other[script.id]
except KeyError:
  pass

if not use_list:
  return []

portal = context.getPortalObject()
translateString = portal.Base_translateString

if portal_type is None:
  portal_type = portal.getPortalResourceTypeList()

use_uid = [context.portal_categories.resolveCategory(use).getUid()
              for use in use_list]

result = [('', '')]

for resource in context.portal_catalog.searchResults(
               portal_type=portal_type,
               default_use_uid=use_uid,
               validation_state=validation_state,
               sort_on=(('portal_type', 'asc'),
                        ('title', 'asc'))) :
  if show_default_quantity_unit and resource.getQuantityUnit():
    result.append(
     ('%s (%s)' % (resource.getTitle(),
                   translateString(resource.getQuantityUnitTitle()),),
      resource.getRelativeUrl()))
  else:
    result.append(
     (resource.getTitle(),
      resource.getRelativeUrl()))

container.REQUEST.other[script.id] = result

return result
