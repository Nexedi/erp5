# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Fabien Morin <fabien@nexedi.com>
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

from zope.interface import Interface

class IEncryptedPassword(Interface):
  """
  Encrypted Password interface specification

  Documents which implement IEncryptedPassword can have get set and check
  encrypted password.
  """

  def checkPassword(value):
    """
    Check the password `value` match the current password, usefull when changing password.
    """

  def checkPasswordValueAcceptable(value):
    """
    Check if the password `value` is acceptable in regard to password policy.
    """

  def checkUserCanChangePassword():
    """
    Check if the current logged in user have permission to change password, on this
    IEncryptedPassword.

    Raise Products.CMFCore.exceptions.AccessControl_Unauthorized in case they don't
    have the permission.

    This method is deprecated and is not used by IEncryptedPassword internally.
    """

  def setPassword(value):
    """
    Set the password to `value` (a string holding the password in clear text).

    Passing an empty value (such as None or empty string) will erase previously defined
    password, which usually prevent login with this password.
    """

  def setEncodedPassword(value, format='default'): # pylint: disable=redefined-builtin
    """
    Set an already encoded password.
    """

  def edit(self, **kw):
    """
    Edit the password and other properties of the documents through user interface.

    This method is responsible for supporting the case where a IEncryptedPassword is
    edited with a my_password field that is empty by default and not resetting the password
    when edited with password=None.
    """

  def getPassword(*args, **kw):
    """
    Retrieve password in desired format.

    getPassword([default], [format='default'])

    default (anything)
      Value to return if no password is set on context.
      Default: None
    format (string)
      String defining the format in which the password is expected.
      If password is not available in that format, KeyError will be
      raised.
      Default: 'default'
    """
