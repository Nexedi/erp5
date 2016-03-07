from Products.PythonScripts.standard import Object
portal = context.getPortalObject()

search_kw = dict(
  parent_portal_type='Payment Transaction',
  section_uid=context.getSourceSectionUid(),
  default_aggregate_uid=context.getUid(),
)

return Object(total_quantity=portal.portal_simulation.getInventory(**search_kw)),
