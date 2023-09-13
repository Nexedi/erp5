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

from AccessControl import ClassSecurityInfo, Unauthorized, getSecurityManager

class PersonCertificateLoginMixin:
  security = ClassSecurityInfo()

  def checkCertificateRequest(self):
    try:
      self.checkUserCanChangePassword()
    except Unauthorized:
      # in ERP5 user has no SetOwnPassword permission on Person document
      # referring himself, so implement "security" by checking that currently
      # logged in user is trying to get/revoke his own certificate
      user_id = self.getUserId()
      if not user_id:
        raise
      if getSecurityManager().getUser().getId() != user_id:
        raise

  def _generateCertificate(self):
    certificate_login = self.newContent(
      portal_type="Certificate Login",
    )
    certificate_dict = certificate_login.getCertificate()
    certificate_login.validate()
    return certificate_dict

  security.declarePublic('generateCertificate')
  def generateCertificate(self):
    """Returns new SSL certificate
       This API was kept for backward compatibility"""
    self.checkCertificateRequest()
    return self._generateCertificate()