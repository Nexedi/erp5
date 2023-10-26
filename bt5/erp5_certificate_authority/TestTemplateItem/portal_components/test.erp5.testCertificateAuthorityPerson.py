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

#import os
import random
from Products.ERP5Type.tests.ERP5TypeCaucaseTestCase import ERP5TypeCaucaseTestCase
from Products.ERP5Type.Core.Workflow import ValidationFailed
from AccessControl import Unauthorized
from caucase.client import CaucaseHTTPError

from cryptography import x509
from cryptography.x509.oid import NameOID

class TestPersonCertificateLogin(ERP5TypeCaucaseTestCase):

  caucase_certificate_kw = {
    "company_name": "ERP5 Company",
    "country_name": "FR",
    "email_address": "noreply@erp5.net",
    "locality_name": "Lille",
    "state_or_province_name": "Nord-Pas-de-Calais"
  }

  def afterSetUp(self):
    self.setUpCaucase()
    if getattr(self.portal.portal_types.Person,
        'user_can_see_himself', None) is None:
      self.portal.portal_types.Person.newContent(
            id="user_can_see_himself",
            title="The User Himself",
            role_name=("Assignee",),
            role_base_category_script_id="ERP5Type_getSecurityCategoryFromSelf",
            role_base_category="group",
            portal_type="Role Information")
    self.tic()

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_web_service', 'erp5_certificate_authority')

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

    ssl_certificate = x509.load_pem_x509_certificate(certificate['certificate'])
    self.assertEqual(len(ssl_certificate.subject), 6)
    cn = [i.value for i in ssl_certificate.subject if i.oid == NameOID.COMMON_NAME][0]
    self.assertEqual(certificate_login.getReference().decode("UTF-8"), cn)

    self.assertEqual(["ERP5 Company"],
      [i.value for i in ssl_certificate.subject if i.oid == NameOID.ORGANIZATION_NAME])

    self.assertEqual(["FR"],
      [i.value for i in ssl_certificate.subject if i.oid == NameOID.COUNTRY_NAME])

    self.assertEqual(["noreply@erp5.net"],
      [i.value for i in ssl_certificate.subject if i.oid == NameOID.EMAIL_ADDRESS])

    self.assertEqual(["Lille"],
      [i.value for i in ssl_certificate.subject if i.oid == NameOID.LOCALITY_NAME])

    self.assertEqual(["Nord-Pas-de-Calais"],
      [i.value for i in ssl_certificate.subject if i.oid == NameOID.STATE_OR_PROVINCE_NAME])


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

    ssl_certificate = x509.load_pem_x509_certificate(certificate['certificate'])
    self.assertEqual(len(ssl_certificate.subject), 6)
    cn = [i.value for i in ssl_certificate.subject if i.oid == NameOID.COMMON_NAME][0]
    self.assertEqual(certificate_login.getReference().decode("UTF-8"), cn)

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

    ssl_certificate = x509.load_pem_x509_certificate(certificate['certificate'])
    self.assertEqual(len(ssl_certificate.subject), 6)
    cn = [i.value for i in ssl_certificate.subject if i.oid == NameOID.COMMON_NAME][0]
    self.assertEqual(certificate_login.getReference().decode("UTF-8"), cn)

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

    ssl_certificate = x509.load_pem_x509_certificate(new_certificate['certificate'])
    self.assertEqual(len(ssl_certificate.subject), 6)
    cn = [i.value for i in ssl_certificate.subject if i.oid == NameOID.COMMON_NAME][0]
    self.assertEqual(new_certificate_login.getReference().decode("UTF-8"), cn)

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

    ssl_certificate = x509.load_pem_x509_certificate(certificate_dict['certificate'])
    self.assertEqual(len(ssl_certificate.subject), 6)
    cn_list = [i.value for i in ssl_certificate.subject if i.oid == NameOID.COMMON_NAME]
    self.assertEqual(len(cn_list), 1)
    self.assertEqual(certificate_login.getReference().decode("UTF-8"), cn_list[0])

    self.assertEqual(certificate_login.getValidationState(), "draft")

    certificate_login.validate()
    self.assertEqual(certificate_login.getValidationState(), "validated")

    self.assertEqual(["ERP5 Company"],
      [i.value for i in ssl_certificate.subject if i.oid == NameOID.ORGANIZATION_NAME])

    self.assertEqual(["FR"],
      [i.value for i in ssl_certificate.subject if i.oid == NameOID.COUNTRY_NAME])

    self.assertEqual(["noreply@erp5.net"],
      [i.value for i in ssl_certificate.subject if i.oid == NameOID.EMAIL_ADDRESS])

    self.assertEqual(["Lille"],
      [i.value for i in ssl_certificate.subject if i.oid == NameOID.LOCALITY_NAME])

    self.assertEqual(["Nord-Pas-de-Calais"],
      [i.value for i in ssl_certificate.subject if i.oid == NameOID.STATE_OR_PROVINCE_NAME])

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

    ssl_certificate = x509.load_pem_x509_certificate(certificate_dict['certificate'])
    self.assertEqual(len(ssl_certificate.subject), 6)
    cn_list = [i.value for i in ssl_certificate.subject if i.oid == NameOID.COMMON_NAME]
    self.assertEqual(len(cn_list), 1)
    self.assertEqual(certificate_login.getReference().decode("UTF-8"), cn_list[0])
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

    # If no csr is provided, the private key is generated by the master
    # this is to provide backward compatibility with old clients
    self.assertIn("key", certificate_dict.keys())

    ssl_certificate = x509.load_pem_x509_certificate(certificate_dict['certificate'])
    self.assertEqual(len(ssl_certificate.subject), 6)
    cn_list = [i.value for i in ssl_certificate.subject if i.oid == NameOID.COMMON_NAME]
    self.assertEqual(len(cn_list), 1)
    self.assertEqual(certificate_login.getReference().decode("UTF-8"), cn_list[0])
    self.assertEqual(certificate_login.getValidationState(), "draft")

    same_certificate_dict = certificate_login.getCertificate()
    self.assertEqual(certificate_dict['certificate'], same_certificate_dict['certificate'])
    
    # If no csr is provided, the private key is generated by the master
    # this is to provide backward compatibility with old clients
    self.assertNotIn("key", same_certificate_dict.keys())

    self.assertRaises(ValueError, certificate_login.getCertificate, "some_csr_string")

  def test_certificate_login_revoke(self):
    person = self.portal.person_module.newContent(portal_type='Person')
    certificate_login = person.newContent(portal_type='Certificate Login')
    self.assertEqual(certificate_login.getReference(), None)
    self.assertRaises(ValueError, certificate_login.revokeCertificate)
    
    certificate_dict = certificate_login.getCertificate()
    reference = certificate_login.getReference()
    self.assertTrue(reference.startswith("CERT"))
    
    ssl_certificate = x509.load_pem_x509_certificate(certificate_dict['certificate'])
    self.assertEqual(len(ssl_certificate.subject), 6)
    cn_list = [i.value for i in ssl_certificate.subject if i.oid == NameOID.COMMON_NAME]
    self.assertEqual(len(cn_list), 1)
    self.assertEqual(certificate_login.getReference().decode("UTF-8"), cn_list[0])

    self.assertEqual(certificate_login.getDestinationReference(), None)
    self.assertNotEqual(certificate_login.getSourceReference(), None)

    self.assertEqual(None, certificate_login.revokeCertificate())
    self.assertEqual(certificate_login.getDestinationReference(), None)
    self.assertEqual(reference, certificate_login.getReference())

    # Revoke again must raise
    self.assertRaises(CaucaseHTTPError, certificate_login.revokeCertificate)

  def test_certificate_login_revoke_providing_key(self):
    person = self.portal.person_module.newContent(portal_type='Person')
    certificate_login = person.newContent(portal_type='Certificate Login')
    self.assertEqual(certificate_login.getReference(), None)
    self.assertRaises(ValueError, certificate_login.revokeCertificate)
    
    certificate_dict = certificate_login.getCertificate()
    reference = certificate_login.getReference()
    self.assertTrue(reference.startswith("CERT"))
    
    ssl_certificate = x509.load_pem_x509_certificate(certificate_dict['certificate'])
    self.assertEqual(len(ssl_certificate.subject), 6)
    cn_list = [i.value for i in ssl_certificate.subject if i.oid == NameOID.COMMON_NAME]
    self.assertEqual(len(cn_list), 1)
    self.assertEqual(certificate_login.getReference().decode("UTF-8"), cn_list[0])

    self.assertEqual(certificate_login.getDestinationReference(), None)
    self.assertNotEqual(certificate_login.getSourceReference(), None)

    self.assertEqual(None, certificate_login.revokeCertificate(certificate_dict['key']))
    self.assertEqual(certificate_login.getDestinationReference(), None)
    self.assertEqual(reference, certificate_login.getReference())

    # Revoke again must raise
    self.assertRaises(CaucaseHTTPError, certificate_login.revokeCertificate, certificate_dict['key'])

  def test_certificate_login_revoke_backward_compatibility(self):
    person = self.portal.person_module.newContent(portal_type='Person')
    certificate_login = person.newContent(portal_type='Certificate Login')
    self.assertEqual(certificate_login.getReference(), None)
    self.assertRaises(ValueError, certificate_login.revokeCertificate)
    
    certificate_dict = certificate_login.getCertificate()
    reference = certificate_login.getReference()
    self.assertTrue(reference.startswith("CERT"))

    ssl_certificate = x509.load_pem_x509_certificate(certificate_dict['certificate'])
    self.assertEqual(len(ssl_certificate.subject), 6)
    cn_list = [i.value for i in ssl_certificate.subject if i.oid == NameOID.COMMON_NAME]
    self.assertEqual(len(cn_list), 1)
    self.assertEqual(certificate_login.getReference().decode("UTF-8"), cn_list[0])

    self.assertEqual(certificate_login.getDestinationReference(), None)
    self.assertNotEqual(certificate_login.getSourceReference(), None)

    # Older implementation wont set it on the Certificate login
    certificate_login.setDestinationReference(None)
    certificate_login.setSourceReference(None)

    # Still raise since it has no valid certificate anymore
    self.assertRaises(ValueError, certificate_login.revokeCertificate)

  def test_certificate_login_revoke_backward_compatibility_with_old_serial(self):
    person = self.portal.person_module.newContent(portal_type='Person')
    certificate_login = person.newContent(portal_type='Certificate Login')
    self.assertEqual(certificate_login.getReference(), None)
    self.assertRaises(ValueError, certificate_login.revokeCertificate)
    
    certificate_login.getCertificate()
    reference = certificate_login.getReference()
    self.assertTrue(reference.startswith("CERT"))

    # Older implementation, using openssl, would have destination reference set
    # this just raise since it cannot be managed by caucase
    certificate_login.setDestinationReference("SOMESERIAL")

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
