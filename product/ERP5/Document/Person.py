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

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.mixin.encrypted_password import EncryptedPasswordMixin
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable

try:
  from Products import PluggableAuthService
  from Products.ERP5Security.ERP5UserManager import ERP5UserManager
except ImportError:
  PluggableAuthService = None

#class Person(Node, XMLObject):
class Person(EncryptedPasswordMixin, XMLObject):
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

    zope.interface.implements(interfaces.INode)

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
                              'getTranslatedTitle')
    def getTranslatedTitle(self, **kw):
      """
        Returns the title if it exists or a combination of
        first name and last name
      """
      if self.title == '':
        name_list = []
        if self.getTranslatedFirstName(**kw) not in (None, ''):
          name_list.append(self.getTranslatedFirstName(**kw))
        if self.getTranslatedMiddleName(**kw) not in (None, ''):
          name_list.append(self.getTranslatedMiddleName(**kw))
        if self.getTranslatedLastName(**kw) not in (None, ''):
          name_list.append(self.getTranslatedLastName(**kw))
        return ' '.join(name_list)
      else:
        return self.title

    security.declareProtected(Permissions.AccessContentsInformation,
                              'title_or_id')
    def title_or_id(self):
      return self.getTitleOrId()

    security.declareProtected(Permissions.AccessContentsInformation,
                              'hasTitle')
    def hasTitle(self):
      return not not self.getTitle()

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

    def _setReference(self, value):
      """
        Set the user id. This method is defined explicitly, because:

        - we want to apply a different permission

        - we want to prevent duplicated user ids, but only when
          PAS _AND_ ERP5UserManager are used
      """
      activate_kw = {}
      portal = self.getPortalObject()
      if value:
        # Encode reference to hex to prevent uppercase/lowercase conflict in
        # activity table (when calling countMessageWithTag)
        activate_kw['tag'] = tag = 'Person_setReference_' + value.encode('hex')
        # Check that there no existing user
        acl_users = portal.acl_users
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
        # Check that there is no reindexation related to reference indexation
        if portal.portal_activities.countMessageWithTag(tag):
          raise RuntimeError, 'user id %s already exist' % (value,)

        # Prevent concurrent transaction to set the same reference on 2
        # different persons
        self.getParentValue().serialize()
        # Prevent to set the same reference on 2 different persons during the
        # same transaction
        transactional_variable = getTransactionalVariable()
        if tag in transactional_variable:
          raise RuntimeError, 'user id %s already exist' % (value,)
        else:
          transactional_variable[tag] = None

      self._baseSetReference(value)
      self.reindexObject(activate_kw=activate_kw)
      # invalid the cache for ERP5Security
      portal_caches = portal.portal_caches
      portal_caches.clearCache(cache_factory_list=('erp5_content_short', ))

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

      portal_simulation = self.getPortalObject().portal_simulation
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

      portal_simulation = self.getPortalObject().portal_simulation
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
