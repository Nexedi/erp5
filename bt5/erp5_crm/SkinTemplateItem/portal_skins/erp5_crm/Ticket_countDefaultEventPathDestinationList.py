portal_catalog = context.getPortalObject().portal_catalog
domain = context.getDefaultEventPathDestinationValue()
if domain is None:
  return [[0]]

return portal_catalog.countResults(
  selection_domain={domain.getParentId(): ('portal_domains', domain.getRelativeUrl(),)})
