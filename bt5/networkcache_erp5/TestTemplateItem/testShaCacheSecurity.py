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


import transaction
from AccessControl import Unauthorized
from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
from ShaCacheMixin import ShaCacheMixin
from ShaSecurityMixin import ShaSecurityMixin


class TestShaCacheSecurity(ShaCacheMixin, ShaSecurityMixin, SecurityTestCase):
  """
    ShaCache Security Test Case
  """

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "SHADIR Security Test Case"

  def getBusinessTemplateList(self):
    """
      Return the list of required business templates.
    """
    return ShaCacheMixin().getBusinessTemplateList() + \
                         ('erp5_pdm',
                          'erp5_data_set',
                          'erp5_web_shadir',
                          'networkcache_erp5',)

  def afterSetUp(self):
    """
      Initialize the ERP5 site.
    """
    self.group = 'shacache'
    ShaCacheMixin.afterSetUp(self)
    ShaSecurityMixin.afterSetUp(self)

  def beforeTearDown(self):
    """
      Clear everything for next test.
    """
    for module in ('person_module',
                   'image_module',
                   'document_module',):
      folder = self.portal[module]
      folder.manage_delObjects(list(folder.objectIds()))
    transaction.commit()
    self.tic()

  # Tests
  def test_anonymous_can_not_create_document(self):
    """
      Annonymous should not be able to create any kind of document
      under document_module and image_module.
    """
    self.logout()
    self.assertTrue(self.portal.portal_membership.isAnonymousUser())

    for module in ('image_module', 'document_module',):
      module = getattr(self.portal, module)
      for portal_type in module.getVisibleAllowedContentTypeList():
        def tryToCreateDataSet():
          module.newContent(portal_type=portal_type,
                            reference=self.key)

        self.assertRaises(Unauthorized, tryToCreateDataSet)

  def test_anonymous_can_not_view_document_module(self):
    """
      Anonymous should not be able to view document module.
    """
    self.logout()
    self.assertTrue(self.portal.portal_membership.isAnonymousUser())
    self.assertRaises(Unauthorized, self.portal.document_module.view)
    self.assertRaises(Unauthorized, self.portal.document_module)

  def test_anonymous_can_not_view_image_module(self):
    """
      Anonymous should not be able to view image module.
    """
    self.logout()
    self.assertTrue(self.portal.portal_membership.isAnonymousUser())
    self.assertRaises(Unauthorized, self.portal.image_module.view)
    self.assertRaises(Unauthorized, self.portal.image_module)


  def test_anonymous_can_not_read_document_list(self):
    """
      Anonymous can not read any document object under document_module
      and image_module.
    """
    for module in ('image_module', 'document_module',):
      module = getattr(self.portal, module)
      for portal_type in module.getVisibleAllowedContentTypeList():
         self.login()
         self.assertFalse(self.portal.portal_membership.isAnonymousUser())

         document = module.newContent(portal_type=portal_type)
         document.publishAlive()
         self.stepTic()

         self.logout()
         self.assertTrue(self.portal.portal_membership.isAnonymousUser())

         self.assertRaises(Unauthorized, document.view)
         self.assertRaises(Unauthorized, document)

  def test_user_can_create_and_view_document_list(self):
    """
      User must be able to create and view any document object under
      document_module and image_module.

      It also must check if document can be published alive.
    """
    self.changeUser(self.lucas_user)
    for module in ('image_module', 'document_module',):
      module = getattr(self.portal, module)
      for portal_type in module.getVisibleAllowedContentTypeList():
        document = module.newContent(portal_type=portal_type)

        document()
        document.view()

        document.publishAlive()
        self.stepTic()

        self.assertEquals('Published Alive',
                            document.getValidationStateTitle())

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

  def test_user_can_not_view_image_module(self):
    """
      User must not be able to see image module.
      Author can not view the module.
    """
    self.changeUser(self.lucas_user)
    self.assertRaises(Unauthorized, self.portal.image_module.view)
    self.assertRaises(Unauthorized, self.portal.image_module)

    self.assertUserHaveRoleOnDocument(self.lucas_user, 'Author',
                                      self.portal.image_module)

  def test_user_can_view_published_alive_document_from_other_users(self):
    """
      If the user A creates a document object, and set it as published alive.
      The user B must be able to view the object.
    """
    for module in ('image_module', 'document_module',):
      module = getattr(self.portal, module)
      for portal_type in module.getVisibleAllowedContentTypeList():

        self.changeUser(self.toto_user)
        document = module.newContent(portal_type=portal_type)
        document.publishAlive()
        self.stepTic()

        self.changeUser(self.lucas_user)
        document()
        document.view()

  # Contribution Tool
  def test_user_create_document_using_contribution_tool(self):
    """
      User must be able to create a document using contribution.
    """
    self.changeUser(self.lucas_user)
    contribution_tool = self.portal.portal_contributions
    self.assertUserHaveRoleOnDocument(self.lucas_user, 'Author',
                                                           contribution_tool)
    document = self.portal.portal_contributions.newContent(
                                    filename='test.txt',
                                    data='test content',
                                    reference='test-reference')
    document()
    document.view()
    self.assertUserHaveRoleOnDocument(self.lucas_user, 'Auditor', document)
