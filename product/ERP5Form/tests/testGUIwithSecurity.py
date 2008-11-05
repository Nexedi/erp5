##############################################################################
# -*- coding: utf8 -*-
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#          Bartek Górny <bartek@erp5.pl>
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
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from Testing import ZopeTestCase
from Products.ERP5Type.Utils import get_request
from Products.ERP5Type.tests.utils import createZODBPythonScript
from ZPublisher.HTTPRequest import FileUpload
from StringIO import StringIO
from Products.ERP5Form.Selection import Selection
from Products.ERP5Form.Form import ERP5Form
from DateTime import DateTime


class TestGUISecurity(ERP5TypeTestCase):
  """
  """
  quiet = 0
  run_all_test = 1

  def getBusinessTemplateList(self):
    return ('erp5_ui_test', 'erp5_base')

  def getTitle(self):
    return "Security Issues in GUI"

  def afterSetUp(self):
    self.login()

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def loginAs(self, id='user'):
    uf = self.getPortal().acl_users
    user = uf.getUserById(id).__of__(uf)
    newSecurityManager(None, user)

  def stepTic(self,**kw):
    self.tic()

  def stepCreateObjects(self, sequence = None, sequence_list = None, **kw):
    # Make sure that the status is clean.
    portal = self.getPortal()
    portal.ListBoxZuite_reset()
    message = portal.foo_module.FooModule_createObjects()
    self.failUnless('Created Successfully' in message)
    if not hasattr(portal.person_module, 'user'):
      user = portal.person_module.newContent(portal_type='Person', id='user', reference='user')
      asg = user.newContent(portal_type='Assignment')
      asg.setStartDate(DateTime() - 100)
      asg.setStopDate(DateTime() + 100)
      asg.open()
    get_transaction().commit()

  def stepCreateTestFoo(self, sequence = None, sequence_list = None, **kw):
    foo_module = self.getPortal().foo_module
    foo_module.newContent(portal_type='Foo', id='foo', foo_category='a')
    get_transaction().commit()

  def stepAccessFoo(self, sequence = None, sequence_list = None, **kw):
    """
      Try to view the Foo_view form, make sure Unauthorized is not raised.
    """
    self.loginAs()
    self.getPortal().foo_module.foo.Foo_view()
    self.login()

  def stepChangeCategorySecurity(self, sequence = None, sequence_list = None, **kw):
    """
      here we change security of a category to which the "Foo" is related
      and which is displayed in the Foo's RelationStringField
    """
    category = self.getPortal().portal_categories.foo_category.a
    args = (('Manager',), 0)
    category.manage_permission('Access contents information', *args)
    category.manage_permission('View', *args)
    get_transaction().commit()
    self.tic()

  def stepResetCategorySecurity(self, sequence = None, sequence_list = None, **kw):
    """
      reset it back
    """
    category = self.getPortal().portal_categories.foo_category.a
    args = ((), 1)
    category.manage_permission('Access contents information', *args)
    category.manage_permission('View', *args)
    get_transaction().commit()
    self.tic()

  def test_01_relationFieldToInaccessibleObject(self, quiet=quiet, run=run_all_test):
    """
      This test checks if a form can be viewed when it contains a RelationStringField which
      links to an object the user is not authorized to view.

      This fails for now. A proposed patch solving this problem is here:
      http://svn.erp5.org/experimental/FSPatch/Products/ERP5Form/ERP5Form_safeRelationField.diff?view=markup

      This problem can happen for example in the following situation:
      - a user is a member of a project P team, so he can view P
      - the user creates a project-related document and leaves it in "draft" state
      - the user quits the project P team
      Then the user can not view the project, but still can view his document as he is the owner.
      An attempt to view the document form would raise Unauthorized.
    """
    self.login()
    if not run: return
    if not quiet:
      message = 'test_01_relationFieldToInaccessibleObject'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateObjects \
                       CreateTestFoo \
                       Tic \
                       AccessFoo \
                       ChangeCategorySecurity \
                       AccessFoo \
                       ResetCategorySecurity \
                       AccessFoo \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestGUISecurity))
  return suite

