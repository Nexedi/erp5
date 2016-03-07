resource_list = context.getValueList('resource')
if resource_list:
  return resource_list[0].getTitle()
