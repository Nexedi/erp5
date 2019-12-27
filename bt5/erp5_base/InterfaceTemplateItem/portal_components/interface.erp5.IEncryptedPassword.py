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
    Check the password, usefull when changing password
    """

  def checkPasswordValueAcceptable(value):
    """
    Check if the password value is acceptable - i.e. follows site rules.
    """

  def setEncodedPassword(value, format='default'):
    """
    Set an already encoded password.
    """

  def _forceSetPassword(value):
    """
    Because both _setPassword and setPassword are considered as
    public method (they are callable from user directly or through edit method)
    _forceSetPassword is needed to reset password without security check by
    Password Tool. This method is not callable through edit method as it not
    begins with _set*
    """

  def checkUserCanChangePassword():
    """
    check user have permission to change his password. Raise in case he cannot.
    """

  def setPassword(value) :
    """
    Set the password, only if the password is not empty and if
    checkUserCanChangePassword don't raise any error
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
      If passowrd is not available in that format, KeyError will be
      raised.
      Default: 'default'
    """
