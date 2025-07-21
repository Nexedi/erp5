tag = script.id
activate_kw = dict(tag=tag)

item = state_change['object']
item.reindexObject(activate_kw=activate_kw)

for aggregate_value in item.getAggregateValueList():
  aggregate_value.activate(after_tag=tag).updateLocalRolesOnSecurityGroups()
  try:
    content_values = aggregate_value.contentValues()
    for content_value in content_values:
      content_value.activate(after_tag=tag).updateLocalRolesOnSecurityGroups()
  except AttributeError:
    pass
