from Products.ERP5Type.Document import newTempBase

portal =  context.getPortalObject()
portal_diff = portal.portal_diff

request = container.REQUEST
if request.get('first_object_path', None) is None:
  return []

first_doc = portal.restrictedTraverse(request['first_object_path'])
scd_doc = portal.restrictedTraverse(request['second_object_path'])

diff = portal_diff.diffPortalObject(first_doc, scd_doc).asBeautifiedJSONDiff()

# Return a list of TempBase objects which can be displayed in a listbox
tempbase_list = []
uid = 0
for x in diff:
  temp_obj = newTempBase(portal,
                        x['path'],
                        **x)
  temp_obj.setUid(int(uid))
  uid = uid + 1
  tempbase_list.append(temp_obj)

return tempbase_list
