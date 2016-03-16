portal = context.getPortalObject()
domain = context.getDefaultEventPathDestinationValue()
if domain is None:
  return []

return portal.portal_catalog(selection_domain={domain.getParentId(): ('portal_domains', domain.getRelativeUrl())})
