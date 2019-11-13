from Products.ERP5Type.Document import newTempDeliveryLine
portal = context.getPortalObject()

result = []

for i in range(item_count):
  obj = newTempDeliveryLine(portal, id="tmp_item_%s" % i, uid="new_item_%s" % i)
  result.append(obj)

return result
