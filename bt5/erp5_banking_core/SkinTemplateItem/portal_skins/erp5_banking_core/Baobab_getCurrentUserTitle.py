# get the current logged user site
if user_id is None:
  login = context.portal_membership.getAuthenticatedMember().getUserName()
else:
  login = user_id

persons = context.acl_users.erp5_users.getUserByLogin(login)

if len(persons) == 0:
  #context.log('Baobab_getUserAssignementList', 'Person %s not found' %(login))
  return ""
else:
  person = persons[0]
  return person.getTitle()
