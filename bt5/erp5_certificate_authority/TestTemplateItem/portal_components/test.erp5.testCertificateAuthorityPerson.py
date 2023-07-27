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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Core.Workflow import ValidationFailed
from AccessControl import Unauthorized

class TestPersonCertificateLogin(ERP5TypeTestCase):

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
    person = self.portal.person_module.newContent(portal_type='Person')
    person.newContent(portal_type='Assignment').open()
    person.newContent(portal_type='ERP5 Login', reference=login).validate()
    person.updateLocalRolesOnSecurityGroups()
    self.tic()
    return person.getUserId(), login

  def test_person_generate_certificate(self):
    user_id, login = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    certificate = person.generateCertificate()

    certificate_login_list = person.objectValues(
      portal_type="Certificate Login"
    )
    self.assertEqual(len(certificate_login_list), 1)
    certificate_login = certificate_login_list[0]
    self.assertNotEqual(certificate_login.getReference(), user_id)
    self.assertNotEqual(certificate_login.getReference(), login)
    self.assertTrue(certificate_login.getReference().startswith("CERT"))

    self.assertIn('CN=%s' % certificate_login.getReference(), certificate['certificate'])
    self.assertNotIn('CN=%s' % user_id, certificate['certificate'])

  def test_person_duplicated_login(self):
    user_id, login = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    person.newContent(portal_type='ERP5 Login', reference=user_id).validate()
    self.tic()

    certificate = person.generateCertificate()
    certificate_login_list = person.objectValues(
      portal_type="Certificate Login"
    )
    # If a erp5_login is already using the User ID, just reuse it for now
    self.assertEqual(len(certificate_login_list), 1)
    certificate_login = certificate_login_list[0]
    self.assertNotEqual(certificate_login.getReference(), user_id)
    self.assertNotEqual(certificate_login.getReference(), login)
    self.assertTrue(certificate_login.getReference().startswith("CERT"))
    self.assertIn('CN=%s' % certificate_login.getReference(), certificate['certificate'])
    self.assertNotIn('CN=%s' % user_id, certificate['certificate'])

    # ERP5 Login dont conflicts
    person.newContent(portal_type='ERP5 Login',
      reference=certificate_login.getReference()).validate()

  def test_person_generate_certificate_twice(self):
    user_id, login = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    certificate = person.generateCertificate()

    certificate_login_list = person.objectValues(
      portal_type="Certificate Login"
    )
    self.assertEqual(len(certificate_login_list), 1)
    certificate_login = certificate_login_list[0]
    self.assertNotEqual(certificate_login.getReference(), user_id)
    self.assertNotEqual(certificate_login.getReference(), login)
    self.assertTrue(certificate_login.getReference().startswith("CERT"))
    
    self.assertIn('CN=%s' % certificate_login.getReference(), certificate['certificate'])
    self.assertNotIn('CN=%s' % user_id, certificate['certificate'])
    self.assertNotIn('CN=%s' % login, certificate['certificate'])
    self.assertEqual(certificate_login.getValidationState(), "validated")

    new_certificate = person.generateCertificate()

    # Ensure it don't create a second object
    certificate_login_list = person.objectValues(
      portal_type="Certificate Login"
    )
    self.assertEqual(len(certificate_login_list), 2)
    new_certificate_login = [i for i in certificate_login_list
      if i.getUid() != certificate_login.getUid()][0]

    self.assertNotEqual(new_certificate_login.getReference(), user_id)
    self.assertNotEqual(new_certificate_login.getReference(), login)
    self.assertNotEqual(new_certificate_login.getReference(),
      certificate_login.getReference())
    
    self.assertTrue(new_certificate_login.getReference().startswith("CERT"))
    
    self.assertIn('CN=%s' % new_certificate_login.getReference(), new_certificate['certificate'])
    self.assertNotIn('CN=%s' % user_id, new_certificate['certificate'])
    self.assertNotIn('CN=%s' % login, new_certificate['certificate'])
    self.assertNotIn('CN=%s' % certificate_login.getReference(), new_certificate['certificate'])
    self.assertEqual(new_certificate_login.getValidationState(), "validated")

  def test_person_generate_certificate_for_another(self):
    _, login = self._createPerson()
    _, login2 = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    self.loginByUserName(login2)
    self.assertRaises(Unauthorized, person.generateCertificate)

  def test_person_duplicated_login_from_another_user(self):
    user_id, login = self._createPerson()
    person = self.portal.person_module.newContent(portal_type='Person',
      reference=str(random.random()), password=login)
    person.newContent(portal_type='Assignment').open()

    # Try to create a login with other person user_id to cheat the system
    person.newContent(portal_type='ERP5 Login', reference=user_id).validate()
    self.tic()
    self.loginByUserName(login)
    user = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    self.assertEqual(user.getUserId(), user_id)
    self.assertRaises(Unauthorized, person.generateCertificate)

    self.login()
    certificate_login_list = [ i for i in person.objectValues(
      portal_type="Certificate Login"
    ) if i.getValidationState() == "validated"]

    self.assertEqual(len(certificate_login_list), 0)

  def test_certificate_login_cant_validate(self):
    person = self.portal.person_module.newContent(portal_type='Person')
    certificate_login = person.newContent(portal_type='Certificate Login')
    self.assertRaises(ValidationFailed, certificate_login.validate)

  def test_certificate_login_get_certificate(self):
    person = self.portal.person_module.newContent(portal_type='Person')
    certificate_login = person.newContent(portal_type='Certificate Login')
    self.assertEqual(certificate_login.getReference(), None)

    certificate_dict = certificate_login.getCertificate()

    self.assertNotEqual(certificate_login.getReference(), None)
    self.assertNotEqual(certificate_login.getReference(), person.getUserId())

    self.assertTrue(certificate_login.getReference().startswith("CERT"))
    
    self.assertIn('CN=%s' % certificate_login.getReference(), certificate_dict['certificate'])
    self.assertNotIn('CN=%s' % person.getUserId(), certificate_dict['certificate'])
    self.assertEqual(certificate_login.getValidationState(), "draft")

    certificate_login.validate()
    self.assertEqual(certificate_login.getValidationState(), "validated")

  def test_certificate_login_get_certificate_set_reference(self):
    person = self.portal.person_module.newContent(portal_type='Person')
    certificate_login = person.newContent(portal_type='Certificate Login',
      reference="FAKEREFERENCE-%s" % (person.getUid()))
    self.assertNotEqual(certificate_login.getReference(), None)

    certificate_dict = certificate_login.getCertificate()

    self.assertNotEqual(certificate_login.getReference(), None)
    self.assertNotEqual(certificate_login.getReference(), person.getUserId())

    # Reference is reset while setting the generate the certificate.
    self.assertTrue(certificate_login.getReference().startswith("CERT"))
    
    self.assertIn('CN=%s' % certificate_login.getReference(), certificate_dict['certificate'])
    self.assertNotIn('CN=%s' % person.getUserId(), certificate_dict['certificate'])
    self.assertEqual(certificate_login.getValidationState(), "draft")

    certificate_login.validate()
    self.assertEqual(certificate_login.getValidationState(), "validated")

  def test_certificate_login_get_certificate_twice(self):
    person = self.portal.person_module.newContent(portal_type='Person')
    certificate_login = person.newContent(portal_type='Certificate Login')
    self.assertEqual(certificate_login.getReference(), None)

    certificate_dict = certificate_login.getCertificate()
    
    reference = certificate_login.getReference()
    # Reference is reset while setting the generate the certificate.
    self.assertTrue(reference.startswith("CERT"))
    
    self.assertIn('CN=%s' % reference, certificate_dict['certificate'])
    self.assertNotIn('CN=%s' % person.getUserId(), certificate_dict['certificate'])
    self.assertEqual(certificate_login.getValidationState(), "draft")

    self.assertRaises(ValueError, certificate_login.getCertificate)

  def test_certificate_login_revoke(self):
    person = self.portal.person_module.newContent(portal_type='Person')
    certificate_login = person.newContent(portal_type='Certificate Login')
    self.assertEqual(certificate_login.getReference(), None)
    self.assertRaises(ValueError, certificate_login.revokeCertificate)
    
    certificate_dict = certificate_login.getCertificate()
    reference = certificate_login.getReference()
    self.assertTrue(reference.startswith("CERT"))
    self.assertIn('CN=%s' % reference, certificate_dict['certificate'])
    self.assertNotEqual(certificate_login.getDestinationReference(), None)

    self.assertEqual(None, certificate_login.revokeCertificate())
    self.assertEqual(certificate_login.getDestinationReference(), None)
    self.assertEqual(reference, certificate_login.getReference())

    # Revoke again must raise
    self.assertRaises(ValueError, certificate_login.revokeCertificate)

  def test_certificate_login_revoke_backward_compatibility(self):
    person = self.portal.person_module.newContent(portal_type='Person')
    certificate_login = person.newContent(portal_type='Certificate Login')
    self.assertEqual(certificate_login.getReference(), None)
    self.assertRaises(ValueError, certificate_login.revokeCertificate)
    
    certificate_dict = certificate_login.getCertificate()
    reference = certificate_login.getReference()
    self.assertTrue(reference.startswith("CERT"))
    self.assertIn('CN=%s' % reference, certificate_dict['certificate'])
    self.assertNotEqual(certificate_login.getDestinationReference(), None)

    # Older implementation wont set it on the Certificate login
    certificate_login.setDestinationReference(None)
    self.assertEqual(None, certificate_login.revokeCertificate())
    self.assertEqual(certificate_login.getDestinationReference(), None)
    self.assertEqual(reference, certificate_login.getReference())

    # Still raise since it has no valid certificate anymore
    self.assertRaises(ValueError, certificate_login.revokeCertificate)

  def test_certificate_login_revoke_no_certificate(self):
    person = self.portal.person_module.newContent(portal_type='Person')
    certificate_login = person.newContent(portal_type='Certificate Login')
    self.assertEqual(certificate_login.getReference(), None)

    self.assertRaises(ValueError, certificate_login.revokeCertificate)
    certificate_login.setReference("FAKEREFERENCE-%s" % (person.getUid()))

    # Still raise since it has no certificate
    self.assertRaises(ValueError, certificate_login.revokeCertificate)