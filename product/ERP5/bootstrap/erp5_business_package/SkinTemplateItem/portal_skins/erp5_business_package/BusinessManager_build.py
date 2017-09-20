manager = context
manager.build()

p = context.getPortalObject()
return p.REQUEST.RESPONSE.redirect(
  manager.absolute_url_path())
