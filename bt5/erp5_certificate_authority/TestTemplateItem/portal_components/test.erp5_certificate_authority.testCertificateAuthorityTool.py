# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                     Ivan Tyagov <ivan@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import os
import random
import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from AccessControl import Unauthorized

class TestCertificateAuthority(ERP5TypeTestCase):

  def getTitle(self):
    return "Test Certificate Authority"

  def afterSetUp(self):
    if getattr(self.portal.portal_types.Person, 
        'user_can_see_himself', None) is None:
      self.portal.portal_types.Person.newContent(
            id="user_can_see_himself",
            title="The User Himself",
            role_name=("Assignee",),
            role_base_category_script_id="ERP5Type_getSecurityCategoryFromSelf",
            role_base_category="group",
            portal_type="Role Information")
    if "TEST_CA_PATH" in os.environ:
      self.portal.portal_certificate_authority.certificate_authority_path = \
          os.environ['TEST_CA_PATH']

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_certificate_authority')

  def _createPerson(self):
    login = str(random.random())
    person = self.portal.person_module.newContent(portal_type='Person',
      reference=login, password=login)
    person.newContent(portal_type='Assignment').open()
    person.newContent(portal_type='ERP5 Login', reference=login).validate()
    person.updateLocalRolesOnSecurityGroups()
    self.tic()
    return person.getUserId(), login

  def test_person_request_certificate(self):
    user_id, login = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    certificate = person.getCertificate()

    certificate_login_list = person.objectValues(
      portal_type="Certificate Login"
    )
    self.assertEquals(len(certificate_login_list), 1)
    certificate_login = certificate_login_list[0]
    self.assertEquals(certificate_login.getReference(), user_id)
    self.assertEquals(certificate_login.getValidationState(), "validated")
    
    self.assertTrue('CN=%s' % user_id in certificate['certificate'])

  def test_person_duplicated_login(self):
    user_id, login = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    person.newContent(portal_type='ERP5 Login', reference=user_id).validate()
    self.tic()

    certificate = person.getCertificate()
    certificate_login_list = person.objectValues(
      portal_type="Certificate Login"
    )
    # If a erp5_login is already using the User ID, just reuse it for now
    self.assertEquals(len(certificate_login_list), 0)
    self.assertTrue('CN=%s' % user_id in certificate['certificate'])

  def test_person_revoke_certificate(self):
    _, login = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    self.assertRaises(ValueError, person.revokeCertificate)

  def test_person_request_revoke_certificate(self):
    user_id, login = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    certificate = person.getCertificate()
    certificate_login_list = person.objectValues(
      portal_type="Certificate Login"
    )
    self.assertEquals(len(certificate_login_list), 1)
    certificate_login = certificate_login_list[0]
    self.assertEquals(certificate_login.getReference(), user_id)
    self.assertEquals(certificate_login.getValidationState(), "validated")

    self.assertTrue('CN=%s' % user_id in certificate['certificate'])
    person.revokeCertificate()

  def test_person_request_certificate_twice(self):
    user_id, login = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    certificate = person.getCertificate()

    certificate_login_list = person.objectValues(
      portal_type="Certificate Login"
    )
    self.assertEquals(len(certificate_login_list), 1)
    certificate_login = certificate_login_list[0]
    self.assertEquals(certificate_login.getReference(), user_id)

    self.assertTrue('CN=%s' % user_id in certificate['certificate'])
    self.assertEquals(certificate_login.getValidationState(), "validated")

    self.assertRaises(ValueError, person.getCertificate)

    # Ensure it don't create a second object
    certificate_login_list = person.objectValues(
      portal_type="Certificate Login"
    )
    self.assertEquals(len(certificate_login_list), 1)
    certificate_login = certificate_login_list[0]
    self.assertEquals(certificate_login.getReference(), user_id)
    self.assertEquals(certificate_login.getValidationState(), "validated")

  def test_person_request_revoke_request_certificate(self):
    user_id, login = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    certificate = person.getCertificate()

    certificate_login_list = person.objectValues(
      portal_type="Certificate Login"
    )
    self.assertEquals(len(certificate_login_list), 1)
    certificate_login = certificate_login_list[0]
    self.assertEquals(certificate_login.getReference(), user_id)

    self.assertTrue('CN=%s' % user_id in certificate['certificate'])
    self.assertEquals(certificate_login.getValidationState(), "validated")

    person.revokeCertificate()

    certificate = person.getCertificate()
    # Ensure it don't create a second object
    certificate_login_list = person.objectValues(
      portal_type="Certificate Login"
    )
    self.assertEquals(len(certificate_login_list), 1)
    certificate_login = certificate_login_list[0]
    self.assertEquals(certificate_login.getReference(), user_id)
    self.assertEquals(certificate_login.getValidationState(), "validated")

  def test_person_request_certificate_for_another(self):
    _, login = self._createPerson()
    _, login2 = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    self.loginByUserName(login2)
    self.assertRaises(Unauthorized, person.getCertificate)

  def test_person_duplicated_login_from_another_user(self):
    user_id, login = self._createPerson()    
    person = self.portal.person_module.newContent(portal_type='Person',
      reference=str(random.random()), password=login)
    person.newContent(portal_type='Assignment').open()

    # Try to create a login with other person user_id to cheat the system
    person.newContent(portal_type='ERP5 Login', reference=user_id).validate()
    self.tic()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    self.assertRaises(ValidationFailed, person.getCertificate)

    certificate_login_list = [ i for i in person.objectValues(
      portal_type="Certificate Login"
    ) if i.getValidationState() == "validated"]
    
    self.assertEquals(len(certificate_login_list), 0)

  def test_person_revoke_certificate_for_another(self):
    user_id, login = self._createPerson()
    _, login2 = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    certificate = person.getCertificate()
    self.assertTrue('CN=%s' % user_id in certificate['certificate'])
    self.loginByUserName(login2)
    self.assertRaises(Unauthorized, person.revokeCertificate)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCertificateAuthority))
  return suite