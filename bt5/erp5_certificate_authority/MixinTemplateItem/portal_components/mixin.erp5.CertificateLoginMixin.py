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

  def _getCertificate(self):
    portal = self.getPortalObject()
    _id = self._generateRandomId()
    reference = 'CERTLOGIN-%i-%s-%s' % (
      portal.portal_ids.generateNewId(
        id_group='certificate_login',
        id_generator='non_continuous_integer_increasing',
      ), _id, self.getParentValue().getReference("")
    )
    self.setReference(reference)
    certificate_dict = self.getPortalObject().portal_certificate_authority\
      .getNewCertificate(self.getReference())
    self.setDestinationReference(certificate_dict['id'])
    return certificate_dict

  def _revokeCertificate(self):
    if self.getDestinationReference() is not None:
      certificate_dict = self.getPortalObject().portal_certificate_authority\
        .revokeCertificate(self.getDestinationReference())
      self.setDestinationReference(None)
      return certificate_dict
    elif self.getReference() is not None:
      # Backward compatibility whenever the serial wast set
      certificate_dict = self.getPortalObject().portal_certificate_authority\
        .revokeCertificateByCommonName(self.getReference())
      # Ensure it is None
      self.setDestinationReference(None)
      return certificate_dict
    else:
      raise ValueError("No certificate found to revoke!")

  security.declarePublic('getCertificate')
  def getCertificate(self):
    """Returns new SSL certificate"""
    if self.getDestinationReference() is not None:
      raise ValueError("Certificate was already issued, please revoke first.")
    return self._getCertificate()

  security.declarePublic('revokeCertificate')
  def revokeCertificate(self):
    """Revokes existing certificate"""
    self._revokeCertificate()
