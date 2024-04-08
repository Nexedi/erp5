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

import binascii
import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.Document.Node import Node
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.Utils import bytes2str, str2bytes
from erp5.component.mixin.EncryptedPasswordMixin import EncryptedPasswordMixin
from erp5.component.mixin.LoginAccountProviderMixin import LoginAccountProviderMixin
from erp5.component.mixin.ERP5UserMixin import ERP5UserMixin
from Products.ERP5Type.Core.Workflow import ValidationFailed
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.exceptions import AccessControl_Unauthorized

try:
  from Products import PluggableAuthService
except ImportError:
  PluggableAuthService = None
else:
  from Products.ERP5Security.ERP5UserManager import ERP5UserManager
  from Products.ERP5Security.ERP5LoginUserManager import ERP5LoginUserManager


class UserExistsError(ValidationFailed):
  def __init__(self, user_id):
    super(UserExistsError, self).__init__('user id %s already exists' % (user_id, ))


@zope.interface.implementer(interfaces.INode)
class Person(EncryptedPasswordMixin, Node, LoginAccountProviderMixin, ERP5UserMixin):
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

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTitle')
  def getTitle(self, **kw):
    """
    Returns the title if it exists or a combination of
    first name, middle name and last name
    """
    title = ' '.join([x for x in (self.getFirstName(),
                                  self.getMiddleName(),
                                  self.getLastName()) if x])
    if title:
      return title
    return super(Person, self).getTitle(**kw)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTranslatedTitle')
  def getTranslatedTitle(self, **kw):
    """
    Returns the title if it exists or a combination of
    first name, middle name and last name
    """
    title = ' '.join([x for x in (self.getTranslatedFirstName(**kw),
                                  self.getTranslatedMiddleName(**kw),
                                  self.getTranslatedLastName(**kw)) if x])
    if title:
      return title
    return super(Person, self).getTranslatedTitle(**kw)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'title_or_id')
  def title_or_id(self):
    return self.getTitleOrId()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'hasTitle')
  def hasTitle(self):
    return self.hasFirstName() or \
        self.hasLastName() or \
        self.hasMiddleName() or \
        self._baseHasTitle()

  def __checkUserIdAvailability(self, pas_plugin_class, user_id=None, login=None, check_concurrent_execution=True):
    # Encode reference to hex to prevent uppercase/lowercase conflict in
    # activity table (when calling countMessageWithTag)
    if user_id:
      tag = 'set_userid_' + bytes2str(binascii.hexlify(str2bytes(user_id)))
    else:
      tag = 'set_userid_' + bytes2str(binascii.hexlify(str2bytes(login)))
    # Check that there no existing user
    acl_users = getattr(self, 'acl_users', None)
    if PluggableAuthService is not None and isinstance(acl_users,
          PluggableAuthService.PluggableAuthService.PluggableAuthService):
      plugin_name_set = {
        plugin_name for plugin_name, plugin_value in acl_users.plugins.listPlugins(
          PluggableAuthService.interfaces.plugins.IUserEnumerationPlugin,
        ) if isinstance(plugin_value, pas_plugin_class)
      }
      if plugin_name_set:
        if any(
          user['pluginid'] in plugin_name_set
          for user in acl_users.searchUsers(
            id=user_id,
            login=login,
            exact_match=True,
          )
        ):
          raise UserExistsError(user_id or login)
      else:
        # PAS is used, without expected enumeration plugin: property has no
        # effect on user enumeration, skip checks.
        # XXX: what if desired plugin becomes active later ?
        return

    if not check_concurrent_execution:
      return
    # Check that there is no reindexation related to reference indexation
    if self.getPortalObject().portal_activities.countMessageWithTag(tag):
      raise UserExistsError(user_id)

    # Prevent concurrent transaction to set the same reference on 2
    # different persons
    # XXX: person_module is rather large because of all permission
    # declarations, it would be better to find a smaller document to use
    # here.
    self.getParentValue().serialize()
    # Prevent to set the same reference on 2 different persons during the
    # same transaction
    transactional_variable = getTransactionalVariable()
    if tag in transactional_variable:
      raise UserExistsError(user_id)
    else:
      transactional_variable[tag] = None
    self.reindexObject(activate_kw={'tag': tag})

  def _setReference(self, value):
    """
    Set the user id. This method is defined explicitly, because
    we want to prevent duplicated user ids, but only when
    PAS _AND_ ERP5UserManager are used
    """
    if value != self.getReference():
      if value:
        self.__checkUserIdAvailability(
          pas_plugin_class=ERP5UserManager,
          login=value,
        )
      self._baseSetReference(value)
      # invalid the cache for ERP5Security
      self.getPortalObject().portal_caches.clearCache(cache_factory_list=('erp5_content_short', ))

  def _setUserId(self, value):
    """
    Set the user id. This method is defined explicitly, because:

      - we want to apply a different permission

      - we want to prevent duplicated user ids, but only when
        PAS _AND_ ERP5LoginUserManager are used
    """
    existing_user_id = self.getUserId()
    if value != existing_user_id:
      if value:
        self.__checkUserIdAvailability(
          pas_plugin_class=ERP5LoginUserManager,
          user_id=value,
        )
      if existing_user_id and not _checkPermission(Permissions.ManageUsers, self):
        raise AccessControl_Unauthorized('setUserId')
      self._baseSetUserId(value)

  security.declareProtected(Permissions.ModifyPortalContent, 'initUserId')
  def initUserId(self):
    """Initialize user id.

    ERP5 guarantees unicity of user id when setUserId is called, but this
    comes at the expense of performance, because two transactions are not
    allowed to change any user id at a time.
    This implementation uses an id generator which already guarantees the
    unicity of generated values, so when using this method we can trust
    ourselves and don't need setUserId to check unicity of the user id
    we are generating with other concurrent generations.
    We ignore the risk that another concurrent transaction might be modifying
    a user with a conflicting user id (using another method than initUserId)
    and only check we are not generating an user id that would already be
    used before, in case some user ids were already set by other methods than
    initUserId - the most probable case being migration of persons created
    before introduction of user id and ERP5 Logins.

    If user id are really important in a project(which is very unlikely), this
    method can be customized in a type based method named Person_initUserId
    """
    method = self.getTypeBasedMethod('initUserId')
    if method is not None:
      return method()
    if not self.hasUserId():
      portal = self.getPortalObject()
      user_id = 'P%i' % portal.portal_ids.generateNewId(
          id_group='user_id',
          id_generator='non_continuous_integer_increasing',
      )
      self.__checkUserIdAvailability(
          pas_plugin_class=ERP5LoginUserManager,
          user_id=user_id,
          check_concurrent_execution=False
      )
      # until migration from ERP5UserManager -> ERP5UserManager is completed
      # we want to make sure we are not generating a user id that was used
      # as a reference of a not yet migrated person, otherwise we'll have a
      # duplicate when this person will be migrated.
      self.__checkUserIdAvailability(
          pas_plugin_class=ERP5UserManager,
          login=user_id,
          check_concurrent_execution=False
      )
      self._baseSetUserId(user_id)
      self.reindexObject()

  # Time management
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAvailableTime')
  def getAvailableTime(self, *args, **kw):
    """
    Calculate available time for a person

    See SimulationTool.getAvailableTime
    """
    kw['node'] = [self.getUid()]

    portal_simulation = self.getPortalObject().portal_simulation
    return portal_simulation.getAvailableTime(*args, **kw)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAvailableTimeSequence')
  def getAvailableTimeSequence(self, *args, **kw):
    """
    Calculate available time for a person in a sequence

    See SimulationTool.getAvailableTimeSequence
    """
    kw['node'] = [self.getUid()]

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
