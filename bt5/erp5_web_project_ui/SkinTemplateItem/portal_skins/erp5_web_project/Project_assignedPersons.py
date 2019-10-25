project_title = context.getTitle()
portal_type='Assignment'

n_persons = 0
person_dict = {}

for assignment in context.portal_catalog(portal_type=portal_type,
                                         destination_project_title=project_title):
  person_url = assignment.getParentRelativeUrl()
  if not person_url in person_dict:
    if getCount:
      person_dict[person_url] = person_url
      n_persons += 1
    else:
      person_dict[person_url] = context.restrictedTraverse(person_url)

if getCount:
  return n_persons

return person_dict
