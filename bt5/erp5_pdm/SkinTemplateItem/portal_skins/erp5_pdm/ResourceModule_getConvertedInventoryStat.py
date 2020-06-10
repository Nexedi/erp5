from Products.PythonScripts.standard import Object
portal = context.getPortalObject()

resource_uid = context.ResourceModule_getSelection().getUidList()

obj = Object(uid="new_")
obj["node_title"] = ""
obj["section_title"] = ""
obj["variation_text"] = ""
obj["getCurrentInventory"] = portal.portal_simulation.getCurrentInventory(
    quantity_unit=kw['quantity_unit'],
    metric_type=kw['metric_type'],
    resource_uid=resource_uid,
    selection_domain=kw.get('selection_domain', None))
obj["getAvailableInventory"] = portal.portal_simulation.getAvailableInventory(
    quantity_unit=kw['quantity_unit'],
    resource_uid=resource_uid,
    metric_type=kw['metric_type'],
    selection_domain=kw.get('selection_domain', None))
obj["converted_quantity"] = portal.portal_simulation.getFutureInventory(
    quantity_unit=kw['quantity_unit'],
    resource_uid=resource_uid,
    metric_type=kw['metric_type'],
    selection_domain=kw.get('selection_domain', None))
return [obj,]
