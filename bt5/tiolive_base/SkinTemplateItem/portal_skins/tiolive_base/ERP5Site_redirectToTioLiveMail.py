portal = context.getPortalObject()
return container.REQUEST.RESPONSE.redirect('%s/mail' % portal.ERP5Site_getTioLiveSiteRootUrl(include_language=0))
