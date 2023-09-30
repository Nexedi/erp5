# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2023 Nexedi SARL and Contributors. All Rights Reserved.
#                     Rafael Monnerat <rafael@nexedi.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from caucase.client import CaucaseHTTPError


class TestCertificateAuthorityCaucaseConnector(ERP5TypeTestCase):

  def afterSetUp(self):
    self.setUpCaucase()
    self.caucase_connector = self.portal.portal_web_services.test_caucase_connector

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_web_service', 'erp5_certificate_authority')

  def test_getConnection_no_url(self):
    connector_no_url_string = self.portal.portal_web_services.newContent(
      portal_type="Caucase Connector"
    )
    self.assertRaises(ValueError, connector_no_url_string._getConnection)

  def test_getConnection(self):
    self.assertNotEqual(None, self.caucase_connector._getConnection())
    self.assertNotEqual(None, self.caucase_connector._getConnection(mode="service"))
    self.assertNotEqual(None, self.caucase_connector._getConnection(mode="user"))
    self.assertRaises(ValueError, self.caucase_connector._getConnection, "unknownmode")

  def test_getAuthenticatedConnection_no_url(self):
    connector_no_url_string = self.portal.portal_web_services.newContent(
      portal_type="Caucase Connector"
    )
    self.assertRaises(ValueError, connector_no_url_string._getAuthenticatedConnection)

  def test_getAuthenticatedConnection_with_url(self):
    connector_no_url_string = self.portal.portal_web_services.newContent(
      portal_type="Caucase Connector",
      url_string="https://hasurl.but.no.user_certificate"
    )
    self.assertRaises(ValueError, connector_no_url_string._getAuthenticatedConnection)

  def test(self):
    # Simply test
    key, csr = self.caucase_connector._createCertificateRequest()

    # Only simple test for the order of response dont change
    self.assertIn("PRIVATE KEY", key)
    self.assertIn("CERTIFICATE REQUEST", csr)
    
    csr_id = self.caucase_connector.createCertificateSigningRequest(csr)
    self.caucase_connector.createCertificate(csr_id)
    cert_data = self.caucase_connector.getCertificate(csr_id)

    cert = x509.load_pem_x509_certificate(cert_data, default_backend())
    privkey = serialization.load_pem_private_key(key.encode(), None, default_backend())

    cerfificate_pub = cert.public_key().public_bytes(
      serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
    private_key_pub = privkey.public_key().public_bytes(
      serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)

    self.assertEqual(cerfificate_pub, private_key_pub)

    self.assertEqual(None, self.caucase_connector.revokeCertificate(cert_data, key.encode()))

    self.assertRaises(CaucaseHTTPError, self.caucase_connector.revokeCertificate, cert_data, key.encode())

  def test_revoke_without_key(self):
    key, csr = self.caucase_connector._createCertificateRequest()

    # Only simple test for the order of response dont change
    self.assertIn("PRIVATE KEY", key)
    self.assertIn("CERTIFICATE REQUEST", csr)
    
    csr_id = self.caucase_connector.createCertificateSigningRequest(csr)
    self.caucase_connector.createCertificate(csr_id)
    cert_data = self.caucase_connector.getCertificate(csr_id)

    self.assertEqual(None, self.caucase_connector.revokeCertificate(cert_data))

    self.assertRaises(CaucaseHTTPError, self.caucase_connector.revokeCertificate, cert_data)

