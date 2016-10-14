# -*- coding: utf-8 -*-
##############################################################################
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
from DateTime import DateTime


class TestGUISecurity(ERP5TypeTestCase):
  """
  """

  def getBusinessTemplateList(self):
    return ('erp5_ui_test', 'erp5_base')

  def getTitle(self):
    return "Security Issues in GUI"

  def loginAs(self, id='user'):
    uf = self.getPortal().acl_users
    user = uf.getUser(id).__of__(uf)
    newSecurityManager(None, user)

  def stepCreateObjects(self, sequence = None, sequence_list = None, **kw):
    # Make sure that the status is clean.
    self.portal.ListBoxZuite_reset()
    message = self.portal.foo_module.FooModule_createObjects()
    self.assertTrue('Created Successfully' in message)
    if not hasattr(portal.person_module, 'user'):
      user = portal.person_module.newContent(portal_type='Person', id='user', reference='user')
      user.newContent(portal_type='ERP5 Login', reference='user').validate()
      asg = user.newContent(portal_type='Assignment')
      asg.setStartDate(DateTime() - 100)
      asg.setStopDate(DateTime() + 100)
      asg.open()

  def stepCreateTestFoo(self, sequence = None, sequence_list = None, **kw):
    foo_module = self.portal.foo_module
    foo_module.newContent(portal_type='Foo', id='foo', foo_category='a', reference='Foo Reference')
    # allow Member to view foo_module in a hard coded way as it is not required to setup complex
    # security for this test (by default only 5A roles + Manager can view default modules)
    args = (('Manager', 'Member', 'Assignor', 'Assignee', 'Auditor', 'Associate' ), 0)
    foo_module.manage_permission('Access contents information', *args)
    foo_module.manage_permission('View', *args)

  def stepAccessFooDoesNotRaise(self, sequence = None, sequence_list = None, **kw):
    """
      Try to view the Foo_view form, make sure Unauthorized is not raised.
    """
    self.loginAs()
    self.portal.foo_module.foo.Foo_view()
    self.login()

  def stepAccessFooDisplaysCategoryName(self, sequence = None, sequence_list = None, **kw):
    """
      Try to view the Foo_view form, make sure our category name is displayed
    """
    self.loginAs()
    self.assertIn(
      # this really depends on the generated markup
      '<input name="field_my_foo_category_title" value="a" type="text"',
      self.portal.foo_module.foo.Foo_view())
    self.login()

  def stepAccessFooDoesNotDisplayReference(self, sequence = None, sequence_list = None, **kw):
    """
      Try to view the Foo_view form, make sure our reference is not displayed
    """
    self.loginAs()
    self.assertNotIn(
      # this really depends on the generated markup
      '<input name="field_my_reference" value="Foo Reference" type="text"',
      self.portal.foo_module.foo.Foo_view())
    self.login()

  def stepAccessFooDisplaysReference(self, sequence = None, sequence_list = None, **kw):
    """
      Try to view the Foo_view form, make sure our reference is displayed
    """
    self.loginAs()
    self.assertIn(
      # this really depends on the generated markup
      '<input name="field_my_reference" value="Foo Reference" type="text"',
      self.portal.foo_module.foo.Foo_view())
    self.login()

  def stepAccessFooDoesNotDisplayCategoryName(self, sequence = None, sequence_list = None, **kw):
    """
      Try to view the Foo_view form, make sure our category name is not displayed
    """
    self.loginAs()
    self.assertNotIn(
      # this really depends on the generated markup
      '<input name="field_my_foo_category_title" value="a" type="text"',
      self.portal.foo_module.foo.Foo_view())
    self.login()

  def stepChangeCategorySecurity(self, sequence = None, sequence_list = None, **kw):
    """
      here we change security of a category to which the "Foo" is related
      and which is displayed in the Foo's RelationStringField
    """
    category = self.portal.portal_categories.foo_category.a
    args = (('Manager',), 0)
    category.manage_permission('Access contents information', *args)
    category.manage_permission('View', *args)

  def stepResetCategorySecurity(self, sequence = None, sequence_list = None, **kw):
    """
      reset it back
    """
    category = self.portal.portal_categories.foo_category.a
    args = ((), 1)
    category.manage_permission('Access contents information', *args)
    category.manage_permission('View', *args)

  def stepChangePropertySecurity(self, sequence = None, sequence_list = None, **kw):
    """
      here we change security of a `reference` property
    """
    self.portal.portal_property_sheets.Reference.reference_property.setReadPermission(
      'Manage contents',)

  def stepResetPropertySecurity(self, sequence = None, sequence_list = None, **kw):
    """
      reset it back
    """
    self.portal.portal_property_sheets.Reference.reference_property.setReadPermission(
      'Access contents information')

  def test_01_relationFieldToInaccessibleObject(self):
    """
      This test checks if a form can be viewed when it contains a RelationStringField which
      links to an object the user is not authorized to view.

      This problem can happen for example in the following situation:
      - a user is a member of a project P team, so he can view P
      - the user creates a project-related document and leaves it in "draft" state
      - the user quits the project P team
      Then the user can not view the project, but still can view his document as he is the owner.
      An attempt to view the document form would raise Unauthorized.
    """
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateObjects \
                       CreateTestFoo \
                       Tic \
                       AccessFooDoesNotRaise \
                       AccessFooDisplaysCategoryName \
                       ChangeCategorySecurity \
                       Tic \
                       AccessFooDoesNotRaise \
                       AccessFooDoesNotDisplayCategoryName \
                       ResetCategorySecurity \
                       Tic \
                       AccessFooDoesNotRaise \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_read_permission_property(self):
    """
      This test checks that property defined with a `read_property` that the
      logged in user does not have cannot be displayed.

      Foo_view has a my_reference field, so in this test we will make this
      property protected and make sure user cannot access it.
    """
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateObjects \
                       CreateTestFoo \
                       Tic \
                       AccessFooDoesNotRaise \
                       AccessFooDisplaysReference \
                       ChangePropertySecurity \
                       Tic \
                       AccessFooDoesNotRaise \
                       AccessFooDoesNotDisplayReference \
                       ResetPropertySecurity \
                       Tic \
                       AccessFooDoesNotRaise \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestGUISecurity))
  return suite

