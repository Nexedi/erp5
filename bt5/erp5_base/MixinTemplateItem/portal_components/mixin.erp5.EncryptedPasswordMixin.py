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
from AuthEncoding.AuthEncoding import pw_encrypt, pw_validate
from Products.ERP5Type.Globals import InitializeClass
from Acquisition import aq_base
from Products.ERP5Type import Permissions
from erp5.component.interface.IEncryptedPassword import IEncryptedPassword
from Products.ERP5Type.Globals import PersistentMapping
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.exceptions import AccessControl_Unauthorized
from six import string_types as basestring

@zope.interface.implementer(IEncryptedPassword,)
class EncryptedPasswordMixin(object):
  """Encrypted Password Mixin
  """
  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

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
      # not policy enabled, so basically all passwords are accceptable
      return True
    if not self.isPasswordValid(value):
      raise ValueError("Password does not comply with password policy")

  def checkUserCanChangePassword(self):
    if not _checkPermission(Permissions.SetOwnPassword, self):
      raise AccessControl_Unauthorized('setPassword')

  def _setEncodedPassword(
      self,
      value,
      format='default',  # pylint: disable=redefined-builtin
  ):
    password = getattr(aq_base(self), 'password', None)
    if password is None or isinstance(password, basestring):
      password = self.password = PersistentMapping()
    self.password[format] = value

  security.declareProtected(Permissions.SetOwnPassword, 'setEncodedPassword')
  def setEncodedPassword(
      self,
      value,
      format='default',  # pylint: disable=redefined-builtin
  ):
    """
    """
    self._setEncodedPassword(value, format=format)
    self.reindexObject()

  def _forceSetPassword(self, value):
    # this method is kept for backward compatibility, as there might be interaction
    # workflows on this method.
    self.password = PersistentMapping()
    if value:
      self._setEncodedPassword(pw_encrypt(value))

  def _setPassword(self, value):
    self.checkPasswordValueAcceptable(value)
    self._forceSetPassword(value)

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
      format_ = kw.get('format', 'default')
      # Backward compatibility: if it's not a PersistentMapping instance,
      # assume it's a monovalued string, which corresponds to default
      # password encoding.
      if isinstance(password, PersistentMapping):
        password = password.get(format_, default_password)
      else:
        if format_ != 'default':
          password = default_password
    return password

  security.declareProtected(Permissions.ModifyPortalContent, 'edit')
  def edit(self, *args, **kw):
    """edit, with support for empty password for the user interface.

    In the user interface, we can have a my_password field, that will not
    be pre-filled with the current password, but will be empty. To accomodate
    this case, we don't edit the password if it is empty.
    """
    if kw.get('password') is None:
      kw.pop('password', None)
    return super(EncryptedPasswordMixin, self).edit(*args, **kw)


InitializeClass(EncryptedPasswordMixin)
