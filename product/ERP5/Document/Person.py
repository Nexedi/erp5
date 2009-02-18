##############################################################################
#
# Copyright (c) 2002-2005 Nexedi SARL and Contributors. All Rights Reserved.
#                         Jean-Paul Smets-Solanes <jp@nexedi.com>
#                         Kevin Deldycke <kevin_AT_nexedi_DOT_com>
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
from Globals import PersistentMapping
from Acquisition import aq_base

#from Products.ERP5.Core.Node import Node

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Utils import assertAttributePortalType
from Products.ERP5Type.XMLObject import XMLObject

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
      

#class Person(Node, XMLObject):
class Person(XMLObject):
    """
      An Person object holds the information about
      an person (ex. you, me, someone in the company,
      someone outside of the company, a member of the portal,
      etc.).

      Person objects can contain Coordinate objects
      (ex. Telephone, Url) as well a documents of various types.

      Person objects can be synchronized accross multiple
      sites.

      Person objects inherit from the Node base class
      (one of the 5 base classes in the ERP5 universal business model)
    """

    meta_type = 'ERP5 Person'
    portal_type = 'Person'
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
                      , PropertySheet.Reference
                      , PropertySheet.Person
                      , PropertySheet.Login
                      , PropertySheet.Mapping
                      , PropertySheet.Task
                      )

    def _setTitle(self, value):
      """
        Here we see that we must define a notion
        of priority in the way fields are updated
      """
      if value != self.getTitle():
        self.title = value

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getTitle')
    def getTitle(self, **kw):
      """
        Returns the title if it exists or a combination of
        first name and last name
      """
      if self.title == '':
        name_list = []
        if self.getFirstName() not in (None, ''):
          name_list.append(self.getFirstName())
        if self.getMiddleName() not in (None, ''):
          name_list.append(self.getMiddleName())
        if self.getLastName() not in (None, ''):
          name_list.append(self.getLastName())
        return ' '.join(name_list)
      else:
        return self.title

    security.declareProtected(Permissions.AccessContentsInformation,
                              'title_or_id')
    def title_or_id(self):
      return self.getTitleOrId()

    def _setFirstName(self, value):
      """
        Update Title if first_name is modified
      """
      self._baseSetFirstName(value)
      name_list = []
      if self.getFirstName(): name_list.append(self.getFirstName())
      if self.getLastName(): name_list.append(self.getLastName())
      if name_list: self._setTitle(' '.join(name_list))

    def _setLastName(self, value):
      """
        Update Title if last_name is modified
      """
      self._baseSetLastName(value)
      name_list = []
      if self.getFirstName(): name_list.append(self.getFirstName())
      if self.getLastName(): name_list.append(self.getLastName())
      if name_list: self._setTitle(' '.join(name_list))

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

    security.declareProtected(Permissions.SetOwnPassword, 'checkPassword')
    def checkPassword(self, value) :
      """
        Check the password, usefull when changing password
      """      
      if value is not None :
        return pw_validate(self.getPassword(), value)
      return False

    def _setEncodedPassword(self, value, format='default'):
      password = getattr(aq_base(self), 'password', None)
      if password is None:
        password = self.password = PersistentMapping()
      self.password[format] = value

    security.declarePublic('setPassword')
    def setEncodedPassword(self, value, format='default'):
      """
        Set an already encoded password.
      """
      if not _checkPermission(Permissions.SetOwnPassword, self):
        raise AccessControl_Unauthorized('setEncodedPassword')
      self._setEncodedPassword(value, format=format)
      self.reindexObject()

    def _setPassword(self, value):
      self.password = PersistentMapping()
      self._setEncodedPassword(pw_encrypt(value))

    security.declarePublic('setPassword')
    def setPassword(self, value) :
      """
        Set the password, only if the password is not empty.
      """
      if value is not None:
        if not _checkPermission(Permissions.SetOwnPassword, self):
          raise AccessControl_Unauthorized('setPassword')
        self._setPassword(value)
        self.reindexObject()

    security.declareProtected(Permissions.AccessContentsInformation, 'getPassword')
    def getPassword(self, *args, **kw):
      """
        Retrieve password in desired format.

        getPassword([default], [format='default'])

        default (anything)
          Value to return if no passord is set on context.
          Default: no default, raises AttributeError if property is not set.
        format (string)
          String defining the format in which the password is expected.
          If passowrd is not available in that format, KeyError will be
          raised.
          Default: 'default'
      """
      password = getattr(aq_base(self), 'password', *args)
      format = kw.get('format', 'default')
      try:
        # Backward compatibility: if it's not a PersistentMapping instance,
        # assume it's a monovalued string, which corresponds to default
        # password encoding.
        if isinstance(password, PersistentMapping):
          password = password[format]
        else:
          if format != 'default':
            raise KeyError
      except KeyError:
        raise KeyError, 'Password is not available in %r format.' % (format, )
      return password

    # Time management
    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getAvailableTime')
    def getAvailableTime(self, *args, **kw):
      """
      Calculate available time for a person

      See SimulationTool.getAvailableTime
      """
      assignment_list = self.contentValues(portal_type='Assignment')
      calendar_uid_list = []
      for assignment in assignment_list:
        calendar_uid_list.extend(assignment.getCalendarUidList())
      kw['node'] = [self.getUid()] + calendar_uid_list

      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getAvailableTime(*args, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getAvailableTimeSequence')
    def getAvailableTimeSequence(self, *args, **kw):
      """
      Calculate available time for a person in a sequence
      
      See SimulationTool.getAvailableTimeSequence
      """
      assignment_list = self.contentValues(portal_type='Assignment')
      calendar_uid_list = []
      for assignment in assignment_list:
        calendar_uid_list.extend(assignment.getCalendarUidList())
      kw['node'] = [self.getUid()] + calendar_uid_list

      portal_simulation = getToolByName(self, 'portal_simulation')
      return portal_simulation.getAvailableTimeSequence(*args, **kw)

    # Notifiation API
    security.declareProtected(Permissions.AccessContentsInformation, 
                              'notifyMessage')
    def notifyMessage(self, message):
      """
      This method can only be called with proxy roles.

      A per user preference allows for deciding how to be notified.
      - by email
      - by SMS (if meaningful)
      - daily
      - weekly
      - instantly

      notification is handled as an activity
      """
