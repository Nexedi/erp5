if search_section_path is not None:
  section_value = context.getPortalObject().restrictedTraverse(search_section_path)
  return section_value.countResults(**kw)

return context.portal_catalog.countResults(**kw)
