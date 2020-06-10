from Products.PythonScripts.standard import Object
portal = context.getPortalObject()

resource_uid = context.ResourceModule_getSelection().getUidList()
kw.update(group_by_node=1, group_by_resource=0, resource_uid=resource_uid)


def makeResultLine(brain):
  def getCurrentInventory():
    return portal.portal_simulation.getCurrentInventory(
        node_uid=brain.node_uid,
        resource_uid=resource_uid,
        quantity_unit=kw['quantity_unit'],
        metric_type=kw['metric_type'],
    )

  def getAvailableInventory():
    return portal.portal_simulation.getAvailableInventory(
        node_uid=brain.node_uid,
        resource_uid=resource_uid,
        quantity_unit=kw['quantity_unit'],
        metric_type=kw['metric_type'],
    )
  return Object(
      uid='new_',
      node_title=brain.node_title,
      converted_quantity=brain.converted_quantity,
      getCurrentInventory=getCurrentInventory,
      getAvailableInventory=getAvailableInventory,
  )


result_list = []
for brain in portal.portal_simulation.getFutureInventoryList(**kw):
  result_list.append(makeResultLine(brain))

return result_list
