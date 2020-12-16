portal = context.getPortalObject()

try:
  count = int(context.REQUEST.get('field_your_item_count', ''))
except ValueError:
  count = 10

result = []

for i in range(count):
  obj = portal.newContent(
      portal_type='Movement',
      temp_object=True,
      id="tmp_item_%s" % i,
      uid="new_item_%s" % i)
  result.append(obj)

return result
