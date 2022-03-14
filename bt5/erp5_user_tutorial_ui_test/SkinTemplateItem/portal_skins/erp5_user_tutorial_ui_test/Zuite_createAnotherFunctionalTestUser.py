"""
 Creates the functional test user, validate and open assignment.
"""
portal = context.getPortalObject()
howto_dict = context.Zuite_getHowToInfo()

functional_test_username = howto_dict['functional_another_test_username']
person = getattr(portal.person_module, functional_test_username, None)
if person is None:
  person = portal.person_module.newContent(portal_type='Person',
                                           id=functional_test_username,
                                           title=functional_test_username)

  person.edit(reference=functional_test_username,
              default_email_text=howto_dict['functional_test_user_email'])

  person.validate()

  assignment = person.newContent(portal_type='Assignment',
                                 start_date='01/01/2011',
                                 stop_date='01/01/2111',
                                 function='company/manager')
  assignment.open()

  login = person.newContent(
    portal_type='ERP5 Login',
    reference=functional_test_username,
    password=howto_dict['functional_test_user_password'],
  )
  login.validate()

  # XXX (lucas): These tests must be able to run on an instance without security.
  # BBB for PAS 1.9.0 we pass a response and undo the redirect
  response = container.REQUEST.RESPONSE
  for role in ('Assignee', 'Assignor', 'Associate', 'Auditor', 'Owner'):
    portal.acl_users.zodb_roles.manage_assignRoleToPrincipals(
        role,
        (person.Person_getUserId(),),
        RESPONSE=response)
    response.setStatus(200)

return 'Done.'
