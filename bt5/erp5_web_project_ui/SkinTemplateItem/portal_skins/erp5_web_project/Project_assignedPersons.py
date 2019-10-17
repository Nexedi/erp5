project_title = context.getTitle()
portal_type='Person'


person_list = [x for x in context.portal_catalog(portal_type=portal_type,
                                              destination_project_title=project_title)]

person_list = [line for line in context.objectValues(portal_type="Person")]

'''
print person_list
for x in person_list:
  print x.getTitle()

return printed
'''
if not person_list:
  return "0"
count = len(person_list)
return count
