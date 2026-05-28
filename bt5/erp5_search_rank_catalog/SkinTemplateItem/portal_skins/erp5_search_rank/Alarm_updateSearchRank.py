portal = context.getPortalObject()

# How to drop documents in final state?

portal.portal_catalog.searchAndActivate(
  method_id='Base_updateSearchRank',
  activate_kw={'tag': tag, 'priority': 4},
)
context.activate(after_tag=tag).getId()
