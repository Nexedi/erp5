portal = context.getPortalObject()

# Reset selections
selection_tool = portal.portal_selections
selection_tool.setSelectionFor('sale_order_selection', None)

# Create role categories
role_base_category = portal.restrictedTraverse('portal_categories/role')
for role_id, role_title in (
    ('client', 'Client'),
    ('supplier', 'Supplier')):
  if role_base_category.get(role_id) is None:
    role_base_category.newContent(
      portal_type='Category',
      id=role_id,
      title=role_title
    )

# Set system preferences
preference = portal.portal_preferences.getActiveSystemPreference()
preference.setPreferredClientRoleList(['role/client'])
preference.setPreferredSupplierRoleList(['role/supplier'])

# Create some nodes
for portal_type in ('Person', 'Organisation'):
  for role in ('client', 'supplier'):
    portal.getDefaultModule(portal_type).newContent(
        id='test_trade_ui_test_' + role,
        portal_type=portal_type,
        title='%s %s' % (portal_type, role),
        role_value=role_base_category[role],
    ).validate()

return "Reset Successfully."
