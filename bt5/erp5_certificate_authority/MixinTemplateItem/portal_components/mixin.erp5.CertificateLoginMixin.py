# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2023 Nexedi SA and Contributors. All Rights Reserved.
#                    Rafael Monnerat <rafael@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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

class CertificateLoginMixin:
  security = ClassSecurityInfo()

  def _getCaucaseConnector(self):
    portal = self.getPortalObject()
    connector_list = portal.portal_catalog.unrestrictedSearchResults(
      portal_type="Caucase Connector",
      reference="erp5-certificate-login",
      validation_state="validated"
    )
    if len(connector_list) == 0:
      raise ValueError("No caucase connector found!")
    if len(connector_list) > 1:
      raise ValueError("Too many caucase connector found!")
    
    return connector_list[0]

  def _getCertificate(self, csr=None):
    caucase_connector = self._getCaucaseConnector()
    portal = self.getPortalObject()

    certificate_dict = {
      "common_name" : self.getReference()
    }
    if self.getReference() and self.getCsrId():
      if csr is not None:
        raise ValueError("The certificate was already requsted without the certificate sign request.")
      certificate_dict["id"] = self.getCsrId()
      crt_pem = caucase_connector.getCertificate(self.getCsrId())
      certificate_dict["certificate"] = crt_pem
      # We should assert that reference is the CN of crt_pem
      return certificate_dict

    _id = self._generateRandomId()
    reference = 'CERTLOGIN-%i-%s' % (
      portal.portal_ids.generateNewId(
        id_group='certificate_login',
        id_generator='non_continuous_integer_increasing',
      ), _id
    )
    self.setReference(reference)
    template_csr = caucase_connector.getCertificateSigningRequestTemplate(reference)
    csr_id = caucase_connector.createCertificateSigningRequest(csr)

    caucase_connector.createCertificate(csr_id, template_csr=template_csr)
    crt_pem = caucase_connector.getCertificate(csr_id)
    self.setCsrId(csr_id)

    return {
      "certificate" : crt_pem,
      "id" : self.getCsrId(),
      "common_name" : reference
    }
    
  security.declarePublic('getCertificate')
  def getCertificate(self, csr=None):
    """Returns new SSL certificate"""
    if csr is None and self.getCsrId() is None:
      key, csr = self._getCaucaseConnector()._createCertificateRequest()
      certificate_dict = self._getCertificate(csr=csr)
      certificate_dict["key"] = key
      return certificate_dict
    else:
      return self._getCertificate(csr=csr)

  def _revokeCertificate(self, key_pem=None):
    if self.getDestinationReference() is not None or (
      self.getReference() is not None and self.getCsrId() is None
    ):
      raise ValueError("You cannot revoke certificates from prior implementation!")
    
    if self.getCsrId() is not None:
      caucase_connector = self._getCaucaseConnector()
      crt_pem = caucase_connector.getCertificate(self.getCsrId())
      if key_pem is None:
        return caucase_connector.revokeCertificate(crt_pem, key_pem)
      return caucase_connector.revokeCertificate(crt_pem)
    else:
      raise ValueError("No certificate found to revoke!")

  security.declarePrivate('revokeCertificate')
  def revokeCertificate(self, key_pem=None):
    """Revokes existing certificate"""
    self._revokeCertificate(key_pem=key_pem)