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

from zope.interface import Interface

class ILoginAccountProvider(Interface):
  """
  Documents which implement the ILoginAccountProvider interface are considered as
  providers of ERP5 login accounts.
  """

  def notifyLoginFailure(**kw):
    """
    Notify an authentication failure.
    """

  def notifyPasswordExpire(**kw):
    """
    Notify a password expire event.
    """

  def isLoginBlocked(**kw):
    """
    Is this login blocked?
    """

  def isPasswordExpired(**kw):
    """
    Is password expired?
    """

  def isPasswordValid(password, **kw):
    """
    Is password valid?
    """

  def analyzePassword(password, **kw):
    """
    Analyze password validity.

    Returns a list of Products.ERP5Type.Message.Message instances describing
    the reason for this password not to be valid (too short, not complex).

    If password is valid, the returned list is empty.
    """

  def isPasswordAlreadyUsed(password):
    """
      Return if password has already been used.
    """
