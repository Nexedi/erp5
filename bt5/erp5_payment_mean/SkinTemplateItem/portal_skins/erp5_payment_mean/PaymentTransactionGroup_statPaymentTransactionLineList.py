from Products.PythonScripts.standard import Object
portal = context.getPortalObject()

kw.update({
  'section_uid': context.getSourceSectionUid(),
  'strict_aggregate_uid': context.getUid(),
  'node_uid': [x.uid for x in portal.portal_catalog(
    portal_type='Account',
    strict_account_type_uid=portal.portal_categories.account_type.asset.cash.bank.getUid(),
  )],
})

return Object(total_quantity=portal.portal_simulation.getInventory(**kw)),
