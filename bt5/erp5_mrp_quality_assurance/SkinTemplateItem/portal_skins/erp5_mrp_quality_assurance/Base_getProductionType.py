portal = context.getPortalObject()

return portal.portal_preferences.getPreferredProductionType() or 'VIN'
