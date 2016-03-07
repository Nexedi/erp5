"""
  Returns a list of dictionaries with information about the owners of
  the document in the form:

  {
    'url': person_url,
    'title': person_title,
    'email': person_email,
  }
"""

info_list = []

person_list = context.Base_getOwnerValueList()

for person_object in person_list:
  person_title = person_object.getTitle() or person_object.getReference('')
  person_url = '%s/view' % person_object.absolute_url()
  person_email = person_object.getDefaultEmailText('')

  info_list.append(dict(title=person_title, email=person_email, url=person_url))

return info_list
