portal = context.getPortalObject()
return container.REQUEST.RESPONSE.redirect('%s/profile'
                                            %portal.ERP5Site_getTioLiveSiteRootUrl())
