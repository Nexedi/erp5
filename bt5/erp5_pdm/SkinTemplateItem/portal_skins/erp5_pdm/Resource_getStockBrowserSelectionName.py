portal = context.getPortalObject()

if not portal.portal_selections.getSelectionParamsFor('resource_inventory_selection'):
  portal.portal_selections.setDomainTreeMode(None, 'resource_inventory_selection')
  node_category = portal.portal_preferences.getPreferredNodeCategory()
  if node_category:
    portal.portal_selections.setDomainDictFromParam('resource_inventory_selection', {'site': ('portal_categories', node_category)})

return 'resource_inventory_selection'
