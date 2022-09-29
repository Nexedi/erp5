try:
  return container.REQUEST.other[script.id]
except KeyError:
  pass

if not role_list:
  return []

portal = context.getPortalObject()

if not portal_type:
  portal_type = portal.getPortalNodeTypeList()

role_uid = [portal.portal_categories.resolveCategory(role).getUid()
              for role in role_list]

result = container.REQUEST.other[script.id] = [('', '')] + [
      (x.getTitle(), x.getRelativeUrl()) for x in
            context.portal_catalog.searchResults(
               portal_type=portal_type,
               default_role_uid=role_uid,
               validation_state=validation_state,
               sort_on=(('portal_type', 'asc'),
                        ('title', 'asc'))) ]

return result
