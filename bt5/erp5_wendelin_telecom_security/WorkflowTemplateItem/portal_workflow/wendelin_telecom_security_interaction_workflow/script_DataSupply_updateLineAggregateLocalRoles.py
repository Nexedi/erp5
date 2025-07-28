data_supply = state_change['object']

tag = script.id + '_' + data_supply.getRelativeUrl()
activate_kw = dict(tag=tag)

data_supply.reindexObject(activate_kw=activate_kw)

data_supply_line_list = data_supply.contentValues(portal_type='Data Supply Line')
if len(data_supply_line_list) == 0:
  return

for data_supply_line in data_supply_line_list:
  for value in data_supply_line.getAggregateValueList():
    value.activate(after_tag=tag).updateLocalRolesOnSecurityGroups()
