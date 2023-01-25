##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Fabien MORIN <fabien@nexedi.com>
#                    Francois-Xaiver Algrain <fxalgrain@tiolive.com>
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

from Products.CMFCore.utils import getToolByName
from Products import PluggableAuthService

PluggableAuthServiceTool = PluggableAuthService.PluggableAuthService.PluggableAuthService
IUserEnumerationPlugin = PluggableAuthService.interfaces.plugins.IUserEnumerationPlugin
IAuthenticationPlugin = PluggableAuthService.interfaces.plugins.IAuthenticationPlugin
ZODBUserManager = PluggableAuthService.plugins.ZODBUserManager.ZODBUserManager

def isLocalLoginAvailable(self, login):
  """
  Check for login avaibility.
  Use activated user enumeration plugin which are ERP5 or ZODB user manager
  Returned Values :
  True : Login is available
  False : Login is already used
  None : No founded PluggableAuthServiceTool with id 'acl_users'
  """
  if not login:
    return False
  portal = self.getPortalObject()
  acl_users = getToolByName(portal, 'acl_users')

  if isinstance(acl_users,PluggableAuthServiceTool):
    return not acl_users.searchUsers(login=login, exact_match=True)
  return None
