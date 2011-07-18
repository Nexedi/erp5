# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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

from Products.ERP5Type import Permissions
from AccessControl.AuthEncoding import pw_validate
from AccessControl import ClassSecurityInfo

class LoginAccountProviderMixin:
  """
  This class provides a generic implementation of ILoginAccountProvider.
  """

  # Declarative security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.SetOwnPassword, 'notifyLoginFailure')
  def notifyLoginFailure(self, **kw):
    """
    Notify an authentication failure.
    """
    method = self._getTypeBasedMethod('notifyLoginFailure')
    return method(**kw)

  security.declareProtected(Permissions.SetOwnPassword, 'isLoginBlocked')
  def isLoginBlocked(self, **kw):
    """
    Is this login blocked?
    """
    method = self._getTypeBasedMethod('isLoginBlocked')
    return method(**kw)    

  security.declareProtected(Permissions.SetOwnPassword, 'isPasswordExpired')
  def isPasswordExpired(self, **kw):
    """
    Is password expired?
    """
    method = self._getTypeBasedMethod('isPasswordExpired')
    return method(**kw)

  security.declareProtected(Permissions.SetOwnPassword, 'isPasswordValid')
  def isPasswordValid(self, password, **kw):
    """
    Is password valid?
    """
    method = self._getTypeBasedMethod('isPasswordValid')
    return method(password, **kw)
    
  security.declareProtected(Permissions.SetOwnPassword, 'isPasswordAlreadyUsed')
  def isPasswordAlreadyUsed(self, password):
    """
      Return if password has already been used.
    """
    preferred_number_of_last_password_to_check = self.portal_preferences.getPreferredNumberOfLastPasswordToCheck()
    password_list = self.getLastChangedPasswordValueList() + [self.getPassword()]
    password_list.reverse()
    for encoded_password in password_list[:preferred_number_of_last_password_to_check]:
      if pw_validate(encoded_password, password):
        return True
    return False
    