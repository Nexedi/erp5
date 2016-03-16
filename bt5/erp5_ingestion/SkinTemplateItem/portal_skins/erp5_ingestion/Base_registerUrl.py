if context.hasUrlString():
  portal = context.getPortalObject()
  portal_url_registry = portal.portal_url_registry
  portal_url_registry.registerURL(context.asNormalisedURL(), context.getReference(), context=context)
