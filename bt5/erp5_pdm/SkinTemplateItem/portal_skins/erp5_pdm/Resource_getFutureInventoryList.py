from Products.PythonScripts.standard import Object
portal = context.getPortalObject()

inventory_kw = {
    'selection_domain': selection_domain,
    'group_by_section': False,
    'group_by_node': True,
    'group_by_variation': True,
    'resource_uid': context.getUid(),
}

if node_category:
  inventory_kw['node_category'] = node_category
if section_category:
  inventory_kw['section_category'] = section_category

return portal.portal_simulation.getFutureInventoryList(**inventory_kw)
