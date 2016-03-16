"""
  Find the list of objects to synchronize by calling the catalog.

  Possibly look up a single object based on its ID, GID
"""
person_list = []
if not id:
  for person in context.portal_catalog(portal_type='Person'):
    person = person.getObject()
    if person.getDefaultEmailText() and \
        person.getValidationState() not in ['invalidated', 'deleted'] and \
        person.getTitle() != 'Unknown':
      person_list.append(person)
  return person_list
# work on the defined person (id is not None)
person = getattr(context.person_module, id)
if person.getDefaultEmailText() and \
    person.getValidationState() not in ['invalidated', 'deleted'] and \
    person.getTitle() != 'Unknown':
  person_list.append(person)
return person_list
