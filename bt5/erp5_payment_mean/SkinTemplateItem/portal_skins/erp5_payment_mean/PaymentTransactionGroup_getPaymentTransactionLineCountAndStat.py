portal = context.getPortalObject()
cache = portal.REQUEST.other
cache_key = context.getId() + '_' + script.id
try:
  return cache[cache_key]
except KeyError:
  row, = portal.portal_simulation.getInventoryList(
    select_dict={'count': 'COUNT(*)'},
    ignore_group_by=1,
    section_uid=context.getSourceSectionUid(),
    strict_aggregate_uid=context.getUid(),
    node_uid=[x.uid for x in portal.portal_catalog(
      portal_type='Account',
      strict_account_type_uid=portal.portal_categories.account_type.asset.cash.bank.getUid(),
    )],
  )
  cache[cache_key] = result = (row.count, row.total_quantity)
  return result
