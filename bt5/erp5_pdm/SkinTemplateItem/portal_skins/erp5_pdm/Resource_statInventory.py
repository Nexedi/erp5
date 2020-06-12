from Products.PythonScripts.standard import Object
inventory_kw = {
  'selection_domain': selection_domain
}
if node_category:
  inventory_kw['node_category'] = node_category
if section_category:
  inventory_kw['section_category'] = section_category
if quantity_unit:
  inventory_kw['quantity_unit'] = quantity_unit
if metric_type:
  inventory_kw['metric_type'] = metric_type

obj = Object(uid="new_")
obj["node_title"] = ""
obj["section_title"] = ""
obj["variation_text"] = ""
obj["getCurrentInventory"] = context.getCurrentInventory(**inventory_kw)
obj["getAvailableInventory"] = context.getAvailableInventory(**inventory_kw)
obj["inventory"] = context.getFutureInventory(**inventory_kw)

return [obj,]
