# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Fabien Morin <fabien@nexedi.com>
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Kevin Deldycke <kevin_AT_nexedi_DOT_com>
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
import zope.interface
from AccessControl import ClassSecurityInfo
from AccessControl.AuthEncoding import pw_encrypt, pw_validate
from Products.ERP5Type.Globals import InitializeClass
from Acquisition import aq_base
from Products.ERP5Type import Permissions
from erp5.component.interface.IEncryptedPassword import IEncryptedPassword
from Products.ERP5Type.Globals import PersistentMapping
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.exceptions import AccessControl_Unauthorized

class EncryptedPasswordMixin:

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(IEncryptedPassword,)

  security.declareProtected(Permissions.SetOwnPassword, 'checkPassword')
  def checkPassword(self, value) :
    """
    """
    if value is not None :
      return pw_validate(self.getPassword(), value)
    return False

  security.declareProtected(Permissions.SetOwnPassword, 'checkPasswordValueAcceptable')
  def checkPasswordValueAcceptable(self, value):
    """Check the password.

    This method is defined explicitly, because we want to apply an
    authentication policy which itself may contain explicit password rules.

    Invalid passwords are supposed to be catched earlier in the user interface
    and reported properly to the user, this method is just to prevent wrong API
    usage.
    """
    if not self.getPortalObject().portal_preferences.isAuthenticationPolicyEnabled():
      # not a policy so basically all passwords are accceptable
      return True
    if not self.isPasswordValid(value):
      raise ValueError("Password value doest not comply with password policy")

  def checkUserCanChangePassword(self):
    if not _checkPermission(Permissions.SetOwnPassword, self):
      raise AccessControl_Unauthorized('setPassword')

  def _setEncodedPassword(self, value, format='default'):
    password = getattr(aq_base(self), 'password', None)
    if password is None or isinstance(password, basestring):
      password = self.password = PersistentMapping()
    self.password[format] = value

  security.declarePublic('setEncodedPassword')
  def setEncodedPassword(self, value, format='default'):
    """
    """
    self.checkUserCanChangePassword()
    self._setEncodedPassword(value, format=format)
    self.reindexObject()

  def _forceSetPassword(self, value):
    self.password = PersistentMapping()
    self._setEncodedPassword(pw_encrypt(value))

  def _setPassword(self, value):
    self.checkUserCanChangePassword()
    self.checkPasswordValueAcceptable(value)
    self._forceSetPassword(value)

  security.declarePublic('setPassword')
  def setPassword(self, value) :
    """
    """
    if value is not None:
      self._setPassword(value)
      self.reindexObject()

  security.declareProtected(Permissions.AccessContentsInformation, 'getPassword')
  def getPassword(self, *args, **kw):
    """
    """
    marker = []
    if len(args):
      default_password = args[0]
    else:
      default_password = None
    password = getattr(aq_base(self), 'password', marker)
    if password is marker:
      password = default_password
    else:
      format = kw.get('format', 'default')
      # Backward compatibility: if it's not a PersistentMapping instance,
      # assume it's a monovalued string, which corresponds to default
      # password encoding.
      if isinstance(password, PersistentMapping):
        password = password.get(format, default_password)
      else:
        if format != 'default':
          password = default_password
    return password

InitializeClass(EncryptedPasswordMixin)
