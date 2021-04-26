def sort(a, b):
  return cmp(a[0], b[0])

# context_portal_type : [actor_portal_type, actor_container_portal_type]
# nb: actor_container must be accessible by just going upward in the tree
portal_type_convertion = {'Use Case' : ['Use Case Actor', 'Use Case'],
                          'Use Case Scenario' : ['Use Case Actor', 'Use Case'],
                          'Use Case Scenario Step' : ['Use Case Actor', 'Use Case'],
                          'Test Case' : ['Test Case Actor', 'Test Case'],
                          'Test Case Step' : ['Test Case Actor', 'Test Case'],
                          'Test Report' : ['Test Report Actor', 'Test Report'],
                          'Test Report Step' : ['Test Report Actor','Test Report']}

item_list = [['', '']]
context_obj = context.getObject()
item_portal_type = portal_type_convertion.get(context_obj.getPortalType(), [None])

if item_portal_type[0] is not None:
  while context_obj is not None \
   and hasattr(context_obj, 'getPortalType') \
   and context_obj.getPortalType() != item_portal_type[1]:
    context_obj = context_obj.getParentValue()
  if context_obj is not None \
   and hasattr(context_obj, 'getPortalType') \
   and context_obj.getPortalType() == item_portal_type[1]:
    obj_list = context_obj.contentValues(filter={'portal_type': item_portal_type[0]})
    for obj in obj_list:
      url = obj.getRelativeUrl()
      label = obj.getTitle()
      item_list.append([label, url])
    item_list.sort(sort)

return item_list
