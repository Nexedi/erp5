portal = context.getPortalObject()
cancel_url = portal.absolute_url()
return container.REQUEST.RESPONSE.redirect(
         '%s/ERP5Site_viewChangeAuthenticatedMemberPasswordDialog?cancel_url=%s' 
           %(portal.ERP5Site_getTioLiveSiteRootUrl(), cancel_url))
