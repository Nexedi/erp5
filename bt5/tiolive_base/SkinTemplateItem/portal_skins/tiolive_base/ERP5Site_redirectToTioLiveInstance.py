portal = context.getPortalObject()
return container.REQUEST.RESPONSE.redirect('%s/%s'
                                            % (portal.ERP5Site_getTioLiveSiteRootUrl(), site_id))
