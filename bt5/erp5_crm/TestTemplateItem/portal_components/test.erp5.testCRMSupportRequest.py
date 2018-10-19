from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestSupportRequestnterractions(ERP5TypeTestCase):

  def createPersonUser(self, roles=()):
    person = self.portal.person_module.newContent(
      portal_type='Person',)
    person.newContent(
      portal_type='Assignment').open()
    login = person.newContent(
      portal_type='ERP5 Login',
      reference=self.newPassword(),
      password=self.newPassword())
    for _ in range(5): # try to get a non-used login
      if login.checkConsistency():
        login.setReference(self.newPassword())
    login.validate()
    person.validate()

    self.tic()
    for role in roles:
      self.portal.acl_users.zodb_roles.assignRoleToPrincipal(
        role, person.getUserId())
    return person

  def test_SupportRequest_setSource_on_open(self):
    """The user opening a support request will automatically be set as
    "Operation Manager" on the support request.
    """
    support_request = self.portal.support_request_module.newContent(
        portal_type='Support Request',
        title=self.id())
    support_request.submit()
    self.tic()

    self.assertIsNone(support_request.getSource())

    person = self.createPersonUser(('Assignor', ))
    self.login(person.getUserId())
    self.portal.portal_workflow.doActionFor(
        support_request,
        'validate_action')

    self.assertEqual(person, support_request.getSourceValue())
