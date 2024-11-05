# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Timeout import getTimeLeft
from Products.ERP5Type.XMLObject import XMLObject

import requests
import tempfile

class ClammitConnector(XMLObject):
  # CMF Type Definition
  meta_type = "Clammit Connector"
  portal_type = "Clammit Connector"

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  _SANE_HTTP_STATUS_CODE = 200
  _INFECTED_HTTP_STATUS_CODE = 418
  _DEFAULT_TIMEOUT = 30 # In seconds

  def _query(self, *args, **kw):
    timeout = kw.pop("timeout", self.getTimeout(self._DEFAULT_TIMEOUT))
    timeout = min(
      getTimeLeft() or timeout,
      timeout,
    )

    ca_certificate = self.getCertificateAuthorityCertificate()
    if ca_certificate:
      with tempfile.NamedTemporaryFile() as certificate_authoritity_certificate:
        certificate_authoritity_certificate.write(ca_certificate)
        certificate_authoritity_certificate.seek(0)
        kw["verify"] = certificate_authoritity_certificate.name
        return requests.request(*args, timeout=timeout, **kw)

    return requests.request(*args, timeout=timeout, **kw)

  def isSafe(self, data):
    response = self._query(
      "POST",
      self.getUrlString() + "/scan",
      files={"file": data},
    )
    if response.status_code == self._SANE_HTTP_STATUS_CODE:
      return True
    elif response.status_code == self._INFECTED_HTTP_STATUS_CODE:
      return False
    else:
      raise ValueError("Unknown status code")

  def isReady(self):
    response = self._query(
      "GET",
      self.getUrlString() + "/readyz",
      timeout=3, # The timeout is much shorter as it is a light query
    )
    if response.status_code == 200:
      return True
    return False