# get the current logged user site
if user_id is None:
  person = context.portal_membership.getAuthenticatedMember().getUserValue()
else:
  person_path_set = {
    x['path']
    for x in context.acl_users.searchUsers(login=user_id, exact_match=True)
    if 'path' in x
  }
  if person_path_set:
    person_path, = person_path_set
    person = context.getPortalObject().restrictedTraverse(person_path)
  else:
    person = None

if person is None:
  #context.log('Baobab_getUserAssignementList', 'Person %s not found' %(login))
  return ""
else:
  return person.getTitle()
