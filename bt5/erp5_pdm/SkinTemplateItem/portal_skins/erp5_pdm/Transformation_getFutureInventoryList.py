"""
  Returns the future inventory list of all the Transformed Resources.
"""
def getTransformationResourceList():
  resource_dict = {}
  for m in context.contentValues(
     filter={'portal_type': ['Transformation Optional Resource', 'Transformation Transformed Resource']}):
    r = m.getResource()
    if r is not None:
      resource_dict[r] = 1
  return list(resource_dict.keys())

resource_list = getTransformationResourceList()
if not resource_list:
  # When there is no resource, we have nothing to do.
  return []
portal = context.getPortalObject()
simulation_tool = portal.portal_simulation
kw['resource'] = resource_list
return simulation_tool.getFutureInventoryList(**kw)
