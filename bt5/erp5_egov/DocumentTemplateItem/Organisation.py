##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.exceptions import AccessControl_Unauthorized


from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject

#from Products.ERP5.Core.MetaNode import MetaNode
#from Products.ERP5.Document.MetaNode import MetaNode


try:
  from Products import PluggableAuthService
  from Products.ERP5Security.ERP5UserManager import ERP5UserManager
except ImportError:
  PluggableAuthService = None

try:
  from AccessControl.AuthEncoding import pw_encrypt
except ImportError:
  pw_encrypt = lambda pw:pw

try:
  from AccessControl.AuthEncoding import pw_validate
except ImportError:
  pw_validate = lambda reference, attempt: reference == attempt


#class Organisation(MetaNode, XMLObject):
class Organisation(XMLObject):
    """
      An Organisation object holds the information about
      an organisation (ex. a division in a company, a company,
      a service in a public administration).

      Organisation objects can contain Coordinate objects
      (ex. Telephone, Url) as well a documents of various types.

      Organisation objects can be synchronized accross multiple
      sites.

      Organisation objects inherit from the MetaNode base class
      (one of the 5 base classes in the ERP5 universal business model)
    """

    meta_type = 'ERP5 Organisation'
    portal_type = 'Organisation'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Organisation
                      , PropertySheet.Mapping
                      , PropertySheet.Task
                      , PropertySheet.Reference
                      , PropertySheet.PSJ_Form
                      )


    security.declareProtected('Manage users', 'setReference')
    def setReference(self, value):
      """
        Set the user id. This method is defined explicitly, because:

        - we want to apply a different permission

        - we want to prevent duplicated user ids, but only when
          PAS _AND_ ERP5UserManager are used
      """
      if value:
        acl_users = getToolByName(self, 'acl_users')
        if PluggableAuthService is not None and isinstance(acl_users,
              PluggableAuthService.PluggableAuthService.PluggableAuthService):
          plugin_list = acl_users.plugins.listPlugins(
              PluggableAuthService.interfaces.plugins.IUserEnumerationPlugin)
          for plugin_name, plugin_value in plugin_list:
            if isinstance(plugin_value, ERP5UserManager):
              user_list = acl_users.searchUsers(id=value,
                                                exact_match=True)
              if len(user_list) > 0:
                raise RuntimeError, 'user id %s already exist' % (value,)
              break
      self._setReference(value)
      self.reindexObject()
      # invalid the cache for ERP5Security
      portal_caches = getToolByName(self.getPortalObject(), 'portal_caches')
      portal_caches.clearCache(cache_factory_list=('erp5_content_short', ))

      # an organisation have always a valid and open assignement
      #if not len(self.contentValues(portal_type='Assignment')):
      #  assignment = self.newContent( portal_type='Assignment')
      #  assignment.open()
      #  get_transaction().commit()

    def checkPassword(self, value) :
      """
        Check the password, usefull when changing password
      """
      if value is not None :
        return pw_validate(self.getPassword(), value)
      return False

    security.declarePublic('setPassword')
    def setPassword(self, value) :
      """
        Set the password, only if the password is not empty.
      """
      if value is not None:
        if not _checkPermission(Permissions.SetOwnPassword, self):
          raise AccessControl_Unauthorized('setPassword')
        self._setPassword(pw_encrypt(value))
        self.reindexObject()
 

