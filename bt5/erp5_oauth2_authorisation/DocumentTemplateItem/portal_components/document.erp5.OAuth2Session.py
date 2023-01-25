##############################################################################
#
# Copyright (c) 2020 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5Type.XMLObject import XMLObject

class OAuth2Session(XMLObject):
  security = ClassSecurityInfo()

  def getExpirationDate(self):
    """
    Return the earliest expiration date between policy's and refresh token's.
    """
    policy_date = self.getPolicyExpirationDate()
    refresh_token_date = self.getRefreshTokenExpirationDate()
    if policy_date is None:
      return refresh_token_date
    if refresh_token_date is None:
      return policy_date
    return min(policy_date, refresh_token_date)

  def _setExpirationDate(self, value):
    """
    Prevent setting an expiration date.
    """
    raise RuntimeError('This is a computed property')

  security.declareProtected(Permissions.ModifyPortalContent, 'refreshAccessToken')
  def refreshAccessToken(self):
    """
    Force the expiration of any Access Token related to this session.
    Call this when any Access Token property becomes outdated, for example
    when user's groups or global roles change.
    """
    self.setIntIndex(self.getIntIndex() + 1)

  def getFloatIndex(self):
    """
    So the expiration date is present in catalog table. Used by
    session garbage-collection alarm.
    """
    # Note: deprecate when expiration_date enters standard catalog.
    expiration_date = self.getExpirationDate()
    if expiration_date is not None:
      return expiration_date.timeTime()