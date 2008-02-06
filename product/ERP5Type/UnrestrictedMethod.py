##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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

from AccessControl.User import UnrestrictedUser
from AccessControl.SecurityManagement import getSecurityManager, \
        newSecurityManager, setSecurityManager

class PrivilegedUser(UnrestrictedUser):
  """User that bypasses all security checks, but retains an original
  identity.

  This is used to execute some system activities which should not be
  affected by any given user. UnrestrictedUser is not used as it is,
  because the owner must be still provided, so that new objects will
  be owned by the same user (of course, without privileged rights).
  """
  def getId(self):
    """Get the ID of the user. This is disabled in UnrestrictedUser."""
    return self.getUserName()

class UnrestrictedMethod(object):
  """Callable object that bypasses all security checks.

  This method is dangerous. Never use this, until you are 100% certain
  that you have no other way.

  When a method is wrapped with an instance of this class, it will behave
  in the same way as before, besides that all security checks pass through.
  This is required, for example, for the simulation to expand movements,
  regardless of the permissions given to a user.

  This method is dangerous. Note that not only a method directly wrapped,
  but also methods invoked subsequently within that method, bypass all
  the security checks. If the user can inject something, for example,
  by passing an arbitrary parameter, this will be a serious security hole.

  This method is dangerous. Enough said. Be careful.
  """
  def __init__(self, method):
    self._m = method

  def __call__(self, *args, **kw):
    security_manager = getSecurityManager()
    user = security_manager.getUser()
    if user.getId() is None:
      # This is a special user, thus the user is not allowed to own objects.
      super_user = UnrestrictedUser(user.getUserName(), None,
                                    user.getRoles(), user.getDomains())
    else:
      uf = user.aq_inner.aq_parent
      # XXX is it better to get roles from the parent (i.e. portal)?
      role_list = uf.valid_roles()
      super_user = PrivilegedUser(user.getId(), None,
                                  role_list, user.getDomains()).__of__(uf)
    newSecurityManager(None, super_user)
    try:
      return self._m(*args, **kw)
    finally:
      # Make sure that the original user is back.
      setSecurityManager(security_manager)

