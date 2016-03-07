"""
  Initialize a KM site.
"""
portal = context.getPortalObject()

# setup DMS settings
portal.Zuite_setupDMS()

if site_id:
  portal.web_site_module[site_id].edit(layout_force_anonymous_gadget=1)

# clear cache so UI is regenarated
portal.portal_caches.clearAllCache()

return "Created Successfully."
