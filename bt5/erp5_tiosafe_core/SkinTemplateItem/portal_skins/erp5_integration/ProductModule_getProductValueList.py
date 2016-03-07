"""
  Find the list of objects to synchronize by calling the catalog.

  Possibly look up a single object based on its ID, GID
"""

if gid is not None and len(gid):
  gid_generator_method_id = context_document.getGidGeneratorMethodId()
  method = getattr(context_document, gid_generator_method_id)
  for prod in context.getPortalObject().product_module.contentValues():
    prod_gid = method(prod)
    if prod_gid == gid:
      return [prod,]
  return []
elif id is not None and len(id):
  # work on the defined product (id is not None)
  product = getattr(context.product_module, id)
  if product.getValidationState() not in  ['invalidated', 'deleted'] and \
      product.getTitle() != 'Unknown':
    return [product,]
  return []
else:
  product_list = []
  product_append = product_list.append
  while context_document.getParentValue().getPortalType() != "Synchronization Tool":
    context_document = context_document.getParentValue()
  site = [x for x in context_document.Base_getRelatedObjectList(portal_type="Integration Module")][0].getParentValue()

  sale_supply_list = context.getPortalObject().sale_supply_module.searchFolder(title=site.getTitle(),
                                                                               validation_state="validated")
  if len(sale_supply_list) != 1:
    return []
  sale_supply = sale_supply_list[0].getObject()
  for line in sale_supply.contentValues(portal_type="Sale Supply Line"):
    resource = line.getResourceValue()
    if resource is not None and resource.getValidationState() == "validated":
      product_append(resource)
  return product_list
