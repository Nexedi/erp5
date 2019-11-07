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


from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.Sequence import SequenceList


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
    if not hasattr(self.portal.person_module, 'user'):
      user = self.portal.person_module.newContent(portal_type='Person', id='user', reference='user')
      user.newContent(portal_type='ERP5 Login', reference='user').validate()
      user.newContent(portal_type='Assignment').open()

  def stepCreateTestFoo(self, sequence = None, sequence_list = None, **kw):
    foo_module = self.portal.foo_module
    foo_module.newContent(portal_type='Foo', id='foo', foo_category='a', protected_property='Protected Property')
    # allow Member to view foo_module in a hard coded way as it is not required to setup complex
    # security for this test (by default only 5A roles + Manager can view default modules)
    for permission in ('Access contents information', 'View'):
      foo_module.manage_permission(
          permission,
          ('Manager', 'Member', 'Assignor', 'Assignee', 'Auditor', 'Associate' ),
          0)

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
        self.category_field_markup,
        self.portal.foo_module.foo.Foo_view())
    self.login()

  def stepAccessFooDoesNotDisplayCategoryName(self, sequence = None, sequence_list = None, **kw):
    """
      Try to view the Foo_view form, make sure our category name is not displayed
    """
    self.loginAs()
    self.assertNotIn(
        self.category_field_markup,
        self.portal.foo_module.foo.Foo_view())
    self.login()

  def stepChangeCategorySecurity(self, sequence = None, sequence_list = None, **kw):
    """
      here we change security of a category to which the "Foo" is related
      and which is displayed in the Foo's RelationStringField
    """
    category = self.portal.portal_categories.foo_category.a
    for permission in ('Access contents information', 'View'):
      category.manage_permission(permission, ('Manager',), 0 )

  def stepResetCategorySecurity(self, sequence = None, sequence_list = None, **kw):
    """
      reset it back
    """
    category = self.portal.portal_categories.foo_category.a
    for permission in ('Access contents information', 'View'):
      category.manage_permission(permission, ('Manager',), 1)

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
    # this really depends on the generated markup
    self.category_field_markup = '<input name="field_my_foo_category_title" value="a" type="text"'

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
      logged in user does not have are not displayed.
    """
    self.login() # as manager
    self.stepCreateObjects()
    self.stepCreateTestFoo()

    protected_property_markup = '<input name="field_my_protected_property" value="Protected Property" type="text"'
    self.assertIn(protected_property_markup, self.portal.foo_module.foo.Foo_viewSecurity())

    self.loginAs() # user without permission to access protected property
    self.assertNotIn(protected_property_markup, self.portal.foo_module.foo.Foo_viewSecurity())

  def test_translated_state_title_lookup(self):
    """
    Tests that looking up document which have the same translated state title
    but different states are found, and conversely same state document but with
    different title are not found.

    Note: not testing security, but here because this is one of the rare unit
    tests which install erp5_ui_test.
    """
    self.login()
    portal = self.portal
    newContent = portal.foo_bar_module.newContent
    foo_1 = newContent(portal_type='Foo')
    foo_1.reallyValidate()
    foo_2 = newContent(portal_type='Foo')
    foo_2.reallyValidate()
    foo_2.reallyInvalidate()
    bar_1 = newContent(portal_type='Bar')
    bar_1.reallyValidate()
    bar_2 = newContent(portal_type='Bar')
    bar_2.reallyValidate()
    bar_2.reallyInvalidate()
    # Test sanity checks:
    # - Foo: "correct" title
    self.assertEqual(foo_1.getTranslatedValidationStateTitle(), 'Validated')
    self.assertEqual(foo_2.getTranslatedValidationStateTitle(), 'Invalidated')
    # - Bar: reversed title
    self.assertEqual(bar_1.getTranslatedValidationStateTitle(), 'Invalidated')
    self.assertEqual(bar_2.getTranslatedValidationStateTitle(), 'Validated')
    self.tic()
    self.assertItemsEqual(
      portal.portal_catalog(
        select_list=['translated_validation_state_title'],
        uid=[
          foo_1.getUid(),
          foo_2.getUid(),
          bar_1.getUid(),
          bar_2.getUid(),
        ],
        translated_validation_state_title='Validat%',
        # Note: not actually tested, just checking nothing raises when this is
        # provided.
        sort_on=(('translated_validation_state_title', 'ASC'), ),
      ).dictionaries(),
      [
        {
          'path': foo_1.getPath(),
          'uid': foo_1.getUid(),
          'translated_validation_state_title': 'Validated',
        }, {
          'path': bar_2.getPath(),
          'uid': bar_2.getUid(),
          'translated_validation_state_title': 'Validated',
        }
      ],
    )
