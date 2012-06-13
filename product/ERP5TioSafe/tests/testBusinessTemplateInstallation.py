# -*- coding: utf-8 -*-
##############################################################################
# -*- coding: utf8 -*-
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                       Jerome Perrin <jerome@nexedi.com>
#                       Guy Oswald Obama <guy@nexedi.com>
#
#
##############################################################################

"""Test suites for packaging of tiosafe
"""

from testTioSafeMixin import testTioSafeMixin
from DateTime import DateTime
from AccessControl.SecurityManagement import newSecurityManager

current_user_name = 'herve'

class TestPackaging(testTioSafeMixin):
  """Test business template packaging.

  Ce teste s'assure que certains éléments du site sont bien installés. Il peut
  également être utilisé pour initialiser un site.
  """

  def getTitle(self):
    return "TioSafe Business template packaging."

  def _createUser(self, user_name, user_groups, user_roles=['Member'], **kw):
    """Create a user.
    """
    kw['reference'] = user_name
    #kw.setdefault('password', 'secret')
    person = self.portal.person_module.newContent(**kw)
    assignment = person.newContent(
                          portal_type='Assignment',
                          start_date=DateTime(),
                          stop_date=DateTime() + 10,)
    assignment.open()
    self.tic()

    zodb_roles = self.portal.acl_users.zodb_roles
    for role in user_roles:
      if role != 'Member':
        zodb_roles.assignRoleToPrincipal(role, user_name)

  def loginAsUser(self, user_id):
    """Login with a given user_id """
    uf = self.getPortal().acl_users
    user = uf.getUserById(user_id).__of__(uf)
    return newSecurityManager(None, user)

  def afterSetUp(self):
    """set up """
    self._createUser(current_user_name, [], ['Author', 'Auditor', 'Assignee',
                                             'Assignor', 'Associate', 'Manager'])
    self.loginAsUser(current_user_name)
    portal = self.getPortal()
    self.portal = portal
    self.skin_tool = portal.portal_skins
    self.workflow_tool = portal.portal_workflow
    self.category_tool = portal.portal_categories
    self.preferences_tool = portal.portal_preferences

  def test_skins(self):
    """Test skins are present."""
    for skin_name in ( 'erp5_base',
                       'erp5_pdm',
                       'erp5_trade',
                       'erp5_syncml',
                       'erp5_integration',
                     ):
      self.failUnless(skin_name in self.skin_tool.objectIds(), skin_name)


import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPackaging))
  return suite

