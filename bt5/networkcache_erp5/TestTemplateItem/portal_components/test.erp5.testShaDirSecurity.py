# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Lucas Carvalho <lucas@nexedi.com>
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


from AccessControl import Unauthorized
from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
from erp5.component.test.ShaDirMixin import ShaDirMixin
from erp5.component.test.ShaSecurityMixin import ShaSecurityMixin


class TestShaDirSecurity(ShaDirMixin, ShaSecurityMixin, SecurityTestCase):
  """
    ShaDir Security Test Case
  """

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "SHADIR Security Test Case"

  def afterSetUp(self):
    """
      Initialize the ERP5 site.
    """
    self.group = 'shadir'
    ShaDirMixin.afterSetUp(self)
    ShaSecurityMixin.afterSetUp(self)

  def beforeTearDown(self):
    """
      Clear everything for next test.
    """
    for module in ('person_module',
                   'data_set_module',
                   'document_module',):
      folder = self.portal[module]
      folder.manage_delObjects(list(folder.objectIds()))
    self.tic()

  # Tests
  def test_anonymous_can_not_create_data_set(self):
    """
      Annonymous should not be able to create data set and it also should not
      be able to view data_set_module.
    """
    self.logout()
    self.assertTrue(self.portal.portal_membership.isAnonymousUser())

    def tryToCreateDataSet():
      self.portal.data_set_module.newContent(
                  portal_type='Data Set',
                  reference=self.key)

    self.assertRaises(Unauthorized, tryToCreateDataSet)

  def test_anonymous_can_not_view_data_set_module(self):
    """
      Anonymous should not be able to view data set module.
    """
    self.logout()
    self.assertTrue(self.portal.portal_membership.isAnonymousUser())
    self.assertRaises(Unauthorized, self.portal.data_set_module.view)

  def test_anonymous_can_read_data_set_object(self):
    """
      Anonymous can read a data set object if it is in published state.
    """
    self.login()
    self.assertFalse(self.portal.portal_membership.isAnonymousUser())

    data_set = self.portal.data_set_module.newContent(portal_type='Data Set',
                                                      reference=self.key)
    data_set.publish()
    self.tic()

    self.logout()
    self.assertTrue(self.portal.portal_membership.isAnonymousUser())

    data_set.view()
    data_set()

  def test_user_can_create_and_view_data_set(self):
    """
      User must be able to create and view  a data set object
      It also must check if data set can be published.
    """
    self.changeUser(self.lucas_user)
    data_set = self.portal.data_set_module.newContent(
                           portal_type='Data Set',
                           reference=self.key)
    self.tic()

    data_set()
    data_set.view()

    self.login()
    data_set.publish()
    self.tic()
    self.changeUser(self.lucas_user)
    self.assertEqual('Published', data_set.getValidationStateTitle())

    self.assertUserHaveRoleOnDocument(self.lucas_user, 'Auditor', data_set)

  def test_user_can_not_view_data_set_module(self):
    """
      User must not be able to see data set module.
      Author can not view the module.
    """
    self.changeUser(self.lucas_user)
    self.assertRaises(Unauthorized, self.portal.data_set_module.view)
    self.assertRaises(Unauthorized, self.portal.data_set_module)

    self.assertUserHaveRoleOnDocument(self.lucas_user, 'Author',
                                                  self.portal.data_set_module)

  def test_user_can_view_published_data_set_from_other_users(self):
    """
      If the user A creates a Data Set object, and publish it.
      The user B must be able to view the object.
    """
    self.changeUser(self.toto_user)
    data_set = self.portal.data_set_module.newContent(
                           portal_type='Data Set',
                           reference=self.key)
    self.login()
    data_set.publish()
    self.tic()

    self.changeUser(self.lucas_user)
    data_set()
    data_set.view()

  # Text Document
  def test_user_can_create_and_view_document(self):
    """
      User must be able to create and view a text document object
      It also must check if the document can be published alive.
    """
    self.changeUser(self.lucas_user)
    document = self.portal.document_module.newContent(portal_type='Text')
    self.tic()

    document()
    document.view()

    self.login()
    document.publishAlive()
    self.tic()

    self.changeUser(self.lucas_user)
    self.assertEqual('Published Alive', document.getValidationStateTitle())
    self.assertUserHaveRoleOnDocument(self.lucas_user, 'Auditor', document)

  def test_user_can_not_view_document_module(self):
    """
      User must not be able to see document module.
      Author can not view the module.
    """
    self.changeUser(self.lucas_user)
    self.assertRaises(Unauthorized, self.portal.document_module.view)
    self.assertRaises(Unauthorized, self.portal.document_module)
    self.assertUserHaveRoleOnDocument(self.lucas_user, 'Author',
                                                  self.portal.document_module)

  def test_user_can_view_published_alive_text_from_other_users(self):
    """
      If the user A creates a Text object, and publish it.
      The user B must be able to view the object.
    """
    self.changeUser(self.toto_user)
    document = self.portal.document_module.newContent(portal_type='Text')
    self.login()
    document.publishAlive()
    self.tic()

    self.changeUser(self.lucas_user)
    document()
    document.view()

  # Contribution Tool
  def test_user_create_text_document_using_contribution_tool(self):
    """
      User must be able to create a text document using contribution.
    """
    self.changeUser(self.lucas_user)
    contribution_tool = self.portal.portal_contributions
    self.assertUserHaveRoleOnDocument(self.lucas_user, 'Author',
                                                           contribution_tool)
    data_set = self.portal.data_set_module.newContent(portal_type='Data Set')
    document = self.portal.portal_contributions.newContent(
                                    filename='test.txt',
                                    data=b'test content',
                                    reference='test-reference',
                                    discover_metadata=False,
                                    follow_up_list=[data_set.getRelativeUrl()])
    document()
    document.view()
    self.assertUserHaveRoleOnDocument(self.lucas_user, 'Auditor', document)
