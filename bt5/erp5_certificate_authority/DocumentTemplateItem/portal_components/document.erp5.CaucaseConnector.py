##############################################################################
#
# Copyright (c) 2023 Nexedi SARL and Contributors. All Rights Reserved.
#                    Rafael Monnerat <rafael@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Globals import InitializeClass
from caucase.client import CaucaseClient, CaucaseHTTPError
from Products.ERP5Type.Core.Workflow import ValidationFailed
from caucase.utils import load_ca_certificate, load_certificate

from six.moves import http_client

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import tempfile

_DEFAULTBACKEND = default_backend()

class CaucaseConnector(XMLObject):
  meta_type = 'Caucase Connector'

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _getConnection(self, **kw):
    message_list = self.checkConsistency()
    if message_list:
      raise ValidationFailed(message_list)
    return CaucaseClient(**kw)

  def _getServiceConnection(self, **kw):
    return self._getConnection(ca_url="%s/cas" % self.getUrlString(""), **kw)

  def _getUserConnection(self, **kw):
    return self._getConnection(ca_url="%s/cau" % self.getUrlString(""), **kw)

  def _getAuthenticatedServiceConnection(self):
    if self.getUserCertificate() is None:
      if self.hasUserCertificateRequestReference():
        self.bootstrapCaucaseConfiguration()

    if self.getUserCertificate() is None:
      raise ValueError("You need to set the User Key and Certificate!")

    with tempfile.NamedTemporaryFile(prefix='caucase_user_', bufsize=0) as user_key_file:
      user_key_file.write(self.getUserKey())
      user_key_file.write("\n")
      user_key_file.write(self.getUserCertificate())
      user_key_file.flush()
      return self._getServiceConnection(user_key=user_key_file.name)

  def getCertificateSigningRequestTemplate(self, common_name):
    key_pem = self.getPrivateTemplateKey()
    if not key_pem:
      key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=_DEFAULTBACKEND)
      self.setPrivateTemplateKey(
        key.private_bytes(
          encoding=serialization.Encoding.PEM,
          format=serialization.PrivateFormat.PKCS8,
          encryption_algorithm=serialization.NoEncryption()).decode())
    else:
      key = serialization.load_pem_private_key(
        key_pem,
        password=None,
        backend=_DEFAULTBACKEND
      )

    name_attribute_list = self._getSubjectNameAttributeList()
    name_attribute_list.append(
      x509.NameAttribute(NameOID.COMMON_NAME,
                         # The cryptography library only accept Unicode.
                         common_name.decode('UTF-8')))

    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name(
       name_attribute_list
    )).sign(key, hashes.SHA256(), _DEFAULTBACKEND)

    return csr.public_bytes(serialization.Encoding.PEM).decode()

  security.declareProtected(Permissions.ManageUsers, 'bootstrapCaucaseConfiguration')
  def bootstrapCaucaseConfiguration(self):
    if self.getUserCertificate() is None:
      caucase_connection = self._getUserConnection()
      if not self.hasUserCertificateRequestReference():
        key, csr = self._createCertificateRequest()
        csr_id = caucase_connection.createCertificateSigningRequest(csr)
        self.setUserCertificateRequestReference(csr_id)
        self.setUserKey(key)
      
      csr_id = self.getUserCertificateRequestReference()
      try:
        crt_pem = caucase_connection.getCertificate(
            csr_id=csr_id)
      except CaucaseHTTPError as e:
        if e.args[0] != http_client.NOT_FOUND:
          raise

        # If server does not know our CSR anymore, getCertificateSigningRequest will raise.
        # If it does, we were likely rejected, so exit by letting exception
        # through.
        caucase_connection.getCertificateSigningRequest(csr_id)
      else:
        self.setUserCertificate(crt_pem)

  def _getSubjectNameAttributeList(self):
    crt_pem = self.getUserCertificate()
    if crt_pem is None:
      name_attribute_list = []
      for oid, value in [
        (NameOID.ORGANIZATION_NAME, self.getCompanyName("ERP5")),
        (NameOID.LOCALITY_NAME, self.getLocalityName()),
        (NameOID.EMAIL_ADDRESS, self.getEmailAddress()),
        (NameOID.STATE_OR_PROVINCE_NAME, self.getStateOrProvinceName()),
        (NameOID.COUNTRY_NAME, self.getCountryName()),
      ]:
        if value:
          name_attribute_list.append(x509.NameAttribute(oid, value.decode()))
      return name_attribute_list
    else:
      # Extract name attributes from the existing crt
      ssl_certificate = x509.load_pem_x509_certificate(crt_pem)
      # Filtered to a set of relevant OID
      name_oid_list = [
        NameOID.ORGANIZATION_NAME, 
        NameOID.LOCALITY_NAME, 
        NameOID.EMAIL_ADDRESS, 
        NameOID.STATE_OR_PROVINCE_NAME, 
        NameOID.COUNTRY_NAME,
      ]
      return [i for i in ssl_certificate.subject if i.oid in name_oid_list ]

  def _createCertificateRequest(self):
    key = rsa.generate_private_key(
      public_exponent=65537, key_size=2048, backend=_DEFAULTBACKEND)
    key_pem = key.private_bytes(
      encoding=serialization.Encoding.PEM,
      format=serialization.PrivateFormat.PKCS8,
      encryption_algorithm=serialization.NoEncryption()
    )

    name_attribute_list = self._getSubjectNameAttributeList()
    name_attribute_list.append(
      x509.NameAttribute(NameOID.COMMON_NAME,
                         # The cryptography library only accept Unicode.
                         "erp5-user".decode('UTF-8')))

    # Probably we should extend a bit more the attributes.
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name(
      name_attribute_list
    )).sign(key, hashes.SHA256(), _DEFAULTBACKEND)

    return key_pem.decode(), csr.public_bytes(serialization.Encoding.PEM).decode()

  def getCACertificate(self):
    return self._getServiceConnection().getCACertificate()

  def updateCACertificateChain(self):
    with tempfile.NamedTemporaryFile(prefix='caucase_ca_certificate_chain_', bufsize=0) as ca_crt_file:
      if self.getCaCertificateChain():
        ca_crt_file.write(self.getCaCertificateChain())
        ca_crt_file.write("\n")
        ca_crt_file.flush()
        ca_crt_file.seek(0)

      updated = self._getServiceConnection().updateCAFile(
        url="%s/cas" % self.getUrlString(""),
        ca_crt_path=ca_crt_file.name)
      if updated:
        ca_crt_file.seek(0)
        self.setCaCertificateChain(ca_crt_file.read())

  security.declareProtected(Permissions.ManageUsers, 'verifyCertificate')
  def verifyCertificate(self, crt_pem):
    if not self.getCaCertificateChain():
      self.updateCACertificateChain()

    # Here we are just checking if the certificate is valid, and if the
    # certificate was issued from a ca we expect, otherwise it will just fail.
    load_certificate(
      crt_pem, [load_ca_certificate(self.getCaCertificateChain())], [])
    return crt_pem

  def createCertificateSigningRequest(self, csr):
    return self._getServiceConnection().createCertificateSigningRequest(csr)

  security.declareProtected(Permissions.ManageUsers, 'createCertificate')
  def createCertificate(self, csr_id, template_csr=""):
    return self._getAuthenticatedServiceConnection().createCertificate(csr_id, template_csr)

  security.declareProtected(Permissions.ManageUsers, 'getCertificate')
  def getCertificate(self, csr_id):
    return self.verifyCertificate(
      self._getAuthenticatedServiceConnection().getCertificate(csr_id))

  security.declareProtected(Permissions.ManageUsers, 'revokeCertificate')
  def revokeCertificate(self, crt_pem, key_pem=None):
    if key_pem is None:
      return self._getAuthenticatedServiceConnection().revokeCertificate(crt_pem)
    return self._getServiceConnection().revokeCertificate(crt_pem, key_pem)

InitializeClass(CaucaseConnector)