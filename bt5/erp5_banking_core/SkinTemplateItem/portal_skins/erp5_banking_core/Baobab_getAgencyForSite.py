portal = context.getPortalObject()
if isinstance(site, str):
  site = portal.portal_categories.site.restrictedTraverse(site)
return portal.organisation_module["site_%3s" % (site.getCodification(), )]
