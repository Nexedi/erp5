from Products.PythonScripts.standard import Object
obj = Object(uid="new_")
obj["node_title"] = ""
obj["section_title"] = ""
obj["variation_text"] = ""
obj["getCurrentInventory"] = context.getCurrentInventory(selection_domain=kw.get('selection_domain', None))
obj["getAvailableInventory"] = context.getAvailableInventory(selection_domain=kw.get('selection_domain', None))
obj["inventory"] = context.getFutureInventory(selection_domain=kw.get('selection_domain', None))

return [obj,]
