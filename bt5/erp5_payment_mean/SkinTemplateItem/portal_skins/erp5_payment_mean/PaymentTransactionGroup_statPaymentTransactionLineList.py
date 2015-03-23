from Products.PythonScripts.standard import Object
portal = context.getPortalObject()

kw.update({
  'parent_portal_type':'Payment Transaction',
  'section_uid':context.getSourceSectionUid(),
  'default_aggregate_uid':context.getUid(),
  'node_category':'account_type/asset/cash/bank',
})

return Object(total_quantity=portal.portal_simulation.getInventory(**kw)),
