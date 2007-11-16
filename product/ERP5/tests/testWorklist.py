##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. 
# All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.Sequence import SequenceList
from zExceptions import BadRequest
from Products.ERP5Type.Tool.ClassTool import _aq_reset
from Testing.ZopeTestCase.PortalTestCase import PortalTestCase

class TestWorklist(ERP5TypeTestCase):

  run_all_test = 1
  quiet = 1
  login = PortalTestCase.login

  checked_portal_type = 'Organisation'
  checked_workflow = 'validation_workflow'
  worklist_assignor_id = 'assignor_worklist'
  actbox_assignor_name = 'assignor_todo'
  worklist_owner_id = 'owner_worklist'
  actbox_owner_name = 'owner_todo'
  worklist_assignor_owner_id = 'assignor_owner_worklist'
  actbox_assignor_owner_name = 'assignor_owner_todo'

  def getTitle(self):
    return "Worklist"

  def getBusinessTemplateList(self):
    """
    Return list of bt5 to install
    """
    return ('erp5_base',)

  def getUserFolder(self):
    """
    Return the user folder
    """
    return getattr(self.getPortal(), 'acl_users', None)

  def createManagerAndLogin(self):
    """
    Create a simple user in user_folder with manager rights.
    This user will be used to initialize data in the method afterSetup
    """
    self.getUserFolder()._doAddUser('manager', '', ['Manager'], [])
    self.login('manager')

  def createERP5Users(self, user_dict):
    """
    Create all ERP5 users needed for the test.
    ERP5 user = Person object + Assignment object in erp5 person_module.
    """
    portal = self.getPortal()
    module = portal.getDefaultModule("Person")
    # Create the Person.
    for user_login, user_data in user_dict.items():
      # Create the Person.
      self.logMessage("Create user: %s" % user_login)
      person = module.newContent(
        portal_type='Person', 
        reference=user_login, 
        password='hackme',
      )
      # Create the Assignment.
      assignment = person.newContent( 
        portal_type = 'Assignment',
        group = "%s" % user_data[0],
        function = "%s" % user_data[1],
        start_date = '01/01/1900',
        stop_date = '01/01/2900',
      )
      assignment.open()
    # Reindexing is required for the security to work
    get_transaction().commit()
    self.tic()

  def createUsers(self):
    """
    Create all users needed for the test
    """
    self.createERP5Users(self.getUserDict())

  def getUserDict(self):
    """
    Return dict of users needed for the test
    """
    user_dict = {
      'foo': [None, None],
      'bar': [None, None],
    }
    return user_dict

  def stepLoginAsFoo(self, sequence=None, sequence_list=None, **kw):
    self.login("foo")

  def stepLoginAsBar(self, sequence=None,
                       sequence_list=None, **kw):
    self.login("bar")

  def createDocument(self):
    module = self.getPortal().getDefaultModule(self.checked_portal_type)
    return module.newContent(portal_type=self.checked_portal_type)

  def getWorklistDocumentCountFromActionName(self, action_name):
    self.assertEquals(action_name[-1], ')')
    left_parenthesis_offset = action_name.rfind('(')
    self.assertNotEquals(left_parenthesis_offset, -1)
    return int(action_name[left_parenthesis_offset + 1:-1])

  def createWorklist(self):
    workflow = self.getWorkflowTool()[self.checked_workflow]
    worklists = workflow.worklists

    for worklist_id, actbox_name, role in [
          (self.worklist_assignor_id, self.actbox_assignor_name, 'Assignor'),
          (self.worklist_owner_id, self.actbox_owner_name, 'Owner'),
          (self.worklist_assignor_owner_id, self.actbox_assignor_owner_name, 'Assignor; Owner')]:
      worklists.addWorklist(worklist_id)
      worklist_definition = worklists._getOb(worklist_id)
      worklist_definition.setProperties('',
          actbox_name='%s (%%(count)s)' % (actbox_name, ),
          props={'guard_roles': role,
                 'var_match_portal_type': self.checked_portal_type})

  def test_01_worklist(self, quiet=0, run=run_all_test):
    """
    Test the permission of the building module.
    """
    if not run: 
      return

    workflow_tool = self.portal.portal_workflow

    self.logMessage("Create Manager")
    self.createManagerAndLogin()
    self.createUsers()
    self.logMessage("Create worklist")
    self.createWorklist()
    self.logMessage("Create document as Manager")
    document = self.createDocument()

    get_transaction().commit()
    self.tic()
    self.portal.portal_caches.clearAllCache()

    result = workflow_tool.listActions(object=document)
    self.logout()

    # Users can not see worklist as they are not Assignor
    for user_id in ('manager', ):
      self.login(user_id)
      result = workflow_tool.listActions(object=document)
      self.logMessage("Check %s worklist as Assignor" % user_id)
      entry_list = [x for x in result \
                    if x['name'].startswith(self.actbox_assignor_name)]
      self.assertEquals(len(entry_list), 0)
      self.logMessage("Check %s worklist as Owner" % user_id)
      entry_list = [x for x in result \
                    if x['name'].startswith(self.actbox_owner_name)]
      self.assertEquals(len(entry_list), 1)
      self.assertEquals(
        self.getWorklistDocumentCountFromActionName(entry_list[0]['name']), 1)
      self.logout()
    for user_id in ('foo', 'bar'):
      self.logMessage("Check %s worklist" % user_id)
      self.login(user_id)
      result = workflow_tool.listActions(object=document)
      self.assertEquals(result, [])
      self.logout()

    # Define foo as Assignor
    self.login('manager')
    self.logMessage("Give foo Assignor role")
    document.manage_addLocalRoles('foo', ['Assignor'])
    self.logMessage("Give manager Assignor role")
    document.manage_addLocalRoles('manager', ['Assignor'])
    document.reindexObject()
    get_transaction().commit()
    self.tic()
    self.portal.portal_caches.clearAllCache()
    self.logout()

    for user_id in ('manager', ):
      self.login(user_id)
      result = workflow_tool.listActions(object=document)
      self.logMessage("Check %s worklist as Assignor" % user_id)
      entry_list = [x for x in result \
                    if x['name'].startswith(self.actbox_assignor_name)]
      self.assertEquals(len(entry_list), 1)
      self.assertEquals(
        self.getWorklistDocumentCountFromActionName(entry_list[0]['name']), 1)
      self.logMessage("Check %s worklist as Owner" % user_id)
      entry_list = [x for x in result \
                    if x['name'].startswith(self.actbox_owner_name)]
      self.assertEquals(len(entry_list), 1)
      self.assertEquals(
        self.getWorklistDocumentCountFromActionName(entry_list[0]['name']), 1)
      self.logMessage("Check %s worklist as Owner and Assignor" % user_id)
      entry_list = [x for x in result \
                    if x['name'].startswith(self.actbox_assignor_owner_name)]
      self.assertEquals(len(entry_list), 1)
      self.assertEquals(
        self.getWorklistDocumentCountFromActionName(entry_list[0]['name']), 1)
      self.logout()
    for user_id in ('bar', ):
      self.login(user_id)
      result = workflow_tool.listActions(object=document)
      self.logMessage("Check %s worklist as Assignor" % user_id)
      entry_list = [x for x in result \
                    if x['name'].startswith(self.actbox_assignor_name)]
      self.assertEquals(len(entry_list), 0)
      self.logMessage("Check %s worklist as Owner" % user_id)
      entry_list = [x for x in result \
                    if x['name'].startswith(self.actbox_owner_name)]
      self.assertEquals(len(entry_list), 0)
      self.logout()
    for user_id in ('foo', ):
      self.login(user_id)
      result = workflow_tool.listActions(object=document)
      self.logMessage("Check %s worklist as Assignor" % user_id)
      entry_list = [x for x in result \
                    if x['name'].startswith(self.actbox_assignor_name)]
      self.assertEquals(len(entry_list), 1)
      self.assertTrue(
        self.getWorklistDocumentCountFromActionName(entry_list[0]['name']), 1)
      self.logMessage("Check %s worklist as Owner" % user_id)
      entry_list = [x for x in result \
                    if x['name'].startswith(self.actbox_owner_name)]
      self.assertEquals(len(entry_list), 0)
      self.logout()

    # Define foo and bar as Assignee
    self.login('manager')
    self.logMessage("Give foo Assignee role")
    document.manage_addLocalRoles('foo', ['Assignee'])
    self.logMessage("Give bar Assignee role")
    document.manage_addLocalRoles('bar', ['Assignee'])
    document.reindexObject()
    get_transaction().commit()
    self.tic()
    self.portal.portal_caches.clearAllCache()
    self.logout()

    # Users can not see worklist as they are not Assignor
    for user_id in ('manager', ):
      self.login(user_id)
      result = workflow_tool.listActions(object=document)
      self.logMessage("Check %s worklist as Assignor" % user_id)
      entry_list = [x for x in result \
                    if x['name'].startswith(self.actbox_assignor_name)]
      self.assertEquals(len(entry_list), 1)
      self.assertTrue(
        self.getWorklistDocumentCountFromActionName(entry_list[0]['name']), 1)
      self.logMessage("Check %s worklist as Owner" % user_id)
      entry_list = [x for x in result \
                    if x['name'].startswith(self.actbox_owner_name)]
      self.assertEquals(len(entry_list), 1)
      self.assertTrue(
        self.getWorklistDocumentCountFromActionName(entry_list[0]['name']), 1)
      self.logout()
    for user_id in ('bar', ):
      self.login(user_id)
      result = workflow_tool.listActions(object=document)
      self.logMessage("Check %s worklist as Assignor" % user_id)
      entry_list = [x for x in result \
                    if x['name'].startswith(self.actbox_assignor_name)]
      self.assertEquals(len(entry_list), 0)
      self.logMessage("Check %s worklist as Owner" % user_id)
      entry_list = [x for x in result \
                    if x['name'].startswith(self.actbox_owner_name)]
      self.assertEquals(len(entry_list), 0)
      self.logout()
    for user_id in ('foo', ):
      self.login(user_id)
      result = workflow_tool.listActions(object=document)
      self.logMessage("Check %s worklist as Assignor" % user_id)
      entry_list = [x for x in result \
                    if x['name'].startswith(self.actbox_assignor_name)]
      self.assertEquals(len(entry_list), 1)
      self.assertTrue(
        self.getWorklistDocumentCountFromActionName(entry_list[0]['name']), 1)
      self.logMessage("Check %s worklist as Owner" % user_id)
      entry_list = [x for x in result \
                    if x['name'].startswith(self.actbox_owner_name)]
      self.assertEquals(len(entry_list), 0)
      self.logout()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestWorklist))
  return suite
