## Script (Python) "Inventory_inventoriateLocatedPieceTissu"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
item_list = context.zGetLocatedPieceTissuList()
cr = '\r'
tab = '\t'
report = "Inventaire"+tab+"Resource_variantée"+tab+"Liste de pièces"+cr
item_dict = {}

for item in item_list :
  if not item.resource in item_dict.keys() :
    item_dict[item.resource] = {}
  if not item.variation in item_dict[item.resource].keys() :
    item_dict[item.resource][item.variation] = []
  item_dict[item.resource][item.variation].append(item.id)

for resource_key in item_dict.keys() :
  for variation_key in item_dict[resource_key].keys() :
    movement_list = context.Resource_zGetInventoryMovementList(resource_relative_url=resource_key,variation_relative_url=variation_key)
    if len(movement_list) == 0 :
      report += "pas d'inventaire"+tab+variation_key+tab+str(item_dict[resource_key][variation_key])+cr
    else :
      movement = movement_list[0].getObject()
      if movement is not None :
        movement.setItemIdList(item_dict[resource_key][variation_key])
        report += movement.getRelativeUrl()+tab+variation_key+tab+str(item_dict[resource_key][variation_key])+cr
      else:
        report += "None"+tab+variation_key+tab+str(item_dict[resource_key][variation_key])+cr

request.RESPONSE.setHeader('Content-Type','application/text')

return report
