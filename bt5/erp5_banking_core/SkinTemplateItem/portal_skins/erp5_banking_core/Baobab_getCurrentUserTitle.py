# get the current logged user site
if user_id is None:
  person = context.portal_membership.getAuthenticatedMember().getUserValue()
else:
  person_list = [x for x in context.acl_users.searchUsers(login=user_id, exact_match=True) if 'path' in x]
  if person_list:
    person, = person_list
    person = context.getPortalObject().restrictedTraverse(person['path'])
  else:
    person = None

if person is None:
  #context.log('Baobab_getUserAssignementList', 'Person %s not found' %(login))
  return ""
else:
  return person.getTitle()
