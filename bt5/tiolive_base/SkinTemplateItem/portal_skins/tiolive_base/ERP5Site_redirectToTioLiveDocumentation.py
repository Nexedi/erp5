portal = context.getPortalObject()
return container.REQUEST.RESPONSE.redirect('%s/documentation' 
                                            %portal.ERP5Site_getTioLiveSiteRootUrl())
