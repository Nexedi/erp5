portal = context.getPortalObject()
search_kw = {
  "portal_type": "Action Information",
  "strict_action_type_uid": portal.portal_categories.action_type.restrictedTraverse(action_type).getUid(),
  "sort_on": (("float_index", "DESC"),)
}
if parent_portal_type:
  search_kw['parent_uid'] = portal.portal_types.restrictedTraverse(parent_portal_type).getUid()
return portal.portal_catalog(
  **search_kw
)
