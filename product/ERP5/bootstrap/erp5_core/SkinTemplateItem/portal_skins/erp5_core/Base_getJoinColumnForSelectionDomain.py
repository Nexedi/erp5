'''
  This script is called by Simulation Tool in order to obtain the
  join_column for a getInventoryList or getMovementHistoryList query.
  In the past this supported only node_uid, so keep this as default value
  for backwards compatibility. Script can be customized for projects.
  XXX, Still it is not flexible, i.e. it does not support the case of e.g.
  have a domain on site category sometime used as node_category
  and sometimes as mirror_node_category or section_category.
'''
return {
  'ledger': 'ledger_uid',
}.get(selection_key, 'node_uid')
