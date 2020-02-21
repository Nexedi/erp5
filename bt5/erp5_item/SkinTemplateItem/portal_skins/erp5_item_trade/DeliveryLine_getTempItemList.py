from Products.ERP5Type.Document import newTempDeliveryLine # pylint: disable=no-name-in-module
portal = context.getPortalObject()

try:
  count = int(context.REQUEST.get('field_your_item_count', ''))
except ValueError:
  count = 10

result = []

for i in range(count):
  obj = newTempDeliveryLine(portal, id="tmp_item_%s" % i, uid="new_item_%s" % i)
  result.append(obj)

return result
