##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights
# Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Classes: ERP5User, ERP5UserFactory
"""

from Products.ERP5Type.Globals import InitializeClass
from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from App.config import getConfiguration
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IUserFactoryPlugin
from Products.PluggableAuthService.PropertiedUser import PropertiedUser
from Products.PluggableAuthService.PropertiedUser import \
                                            _what_not_even_god_should_do
from Products.ERP5Security.ERP5UserManager import SUPER_USER

manage_addERP5UserFactoryForm = PageTemplateFile(
    'www/ERP5Security_addERP5UserFactory', globals(),
    __name__='manage_addERP5UserFactoryForm' )

def addERP5UserFactory( dispatcher, id, title=None, REQUEST=None ):
  """ Add a ERP5UserFactory to a Pluggable Auth Service. """

  euf = ERP5UserFactory(id, title)
  dispatcher._setObject(euf.getId(), euf)

  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect( '%s/manage_workspace'
                                  '?manage_tabs_message='
                                  'ERP5UserFactory+added.'
                                     % dispatcher.absolute_url())


class ERP5User(PropertiedUser):
  """ User class that checks the object allows acquisition of local roles the
  ERP5Type way.
  """
  _user_value = None
  _login_value = None

  def getRolesInContext( self, object ):
    """ Return the list of roles assigned to the user.
    For ERP5, we check if a _getAcquireLocalRoles is defined on the object.
    """
    user_id = self.getId()
    # [ x.getId() for x in self.getGroups() ]
    group_ids = self.getGroups()

    principal_ids = list( group_ids )
    principal_ids.insert( 0, user_id )

    local = {}
    object = aq_inner( object )

    while 1:
      local_roles = getattr( object, '__ac_local_roles__', None )
      if local_roles:
        if callable( local_roles ):
          local_roles = local_roles()

        dict = local_roles or {}
        for principal_id in principal_ids:
          for role in dict.get( principal_id, [] ):
            local[ role ] = 1

      # patch by Klaus for LocalRole blocking
      if getattr(object, '_getAcquireLocalRoles', None) is not None:
        if not object._getAcquireLocalRoles():
          break

      inner = aq_inner( object )
      parent = aq_parent( inner )

      if parent is not None:
        object = parent
        continue

      new = getattr( object, 'im_self', None )
      if new is not None:
        object = aq_inner( new )
        continue
      break

    # Patched: Developer role should not never be available as local role
    local.pop('Developer', None)
    return list( self.getRoles() ) + local.keys()

  def allowed( self, object, object_roles=None ):
    """ Check whether the user has access to object.
    As for getRolesInContext, we take into account _getAcquireLocalRoles for
    ERP5.
    """
    if self.getUserName() == SUPER_USER:
      # super user is allowed to accesss any object
      return 1

    if object_roles is _what_not_even_god_should_do:
      return 0

    # Short-circuit the common case of anonymous access.
    if object_roles is None or 'Anonymous' in object_roles:
      return 1

    # Check for Developer Role, see patches.User for rationale
    # XXX-arnau: copy/paste
    object_roles = set(object_roles)
    if 'Developer' in object_roles:
      object_roles.remove('Developer')
      product_config = getattr(getConfiguration(), 'product_config', None)
      if product_config:
        config = product_config.get('erp5')
        if config and self.getId() in config.developer_list:
          return 1

    # Provide short-cut access if object is protected by 'Authenticated'
    # role and user is not nobody
    if 'Authenticated' in object_roles and (
      self.getUserName() != 'Anonymous User'):
      return 1

    # Check for ancient role data up front, convert if found.
    # This should almost never happen, and should probably be
    # deprecated at some point.
    if 'Shared' in object_roles:
      object_roles = self._shared_roles(object)
      if object_roles is None or 'Anonymous' in object_roles:
        return 1

    # Check for a role match with the normal roles given to
    # the user, then with local roles only if necessary. We
    # want to avoid as much overhead as possible.
    user_roles = self.getRoles()
    for role in object_roles:
      if role in user_roles:
        if self._check_context(object):
          return 1
        return None

    # Still have not found a match, so check local roles. We do
    # this manually rather than call getRolesInContext so that
    # we can incur only the overhead required to find a match.
    inner_obj = aq_inner( object )
    user_id = self.getId()
    # [ x.getId() for x in self.getGroups() ]
    group_ids = self.getGroups()

    principal_ids = list( group_ids )
    principal_ids.insert( 0, user_id )

    while 1:
      local_roles = getattr( inner_obj, '__ac_local_roles__', None )
      if local_roles:
        if callable( local_roles ):
          local_roles = local_roles()

        dict = local_roles or {}
        for principal_id in principal_ids:
          local_roles = dict.get( principal_id, [] )
          for role in object_roles:
            if role in local_roles:
              if self._check_context( object ):
                return 1
              return 0

      # patch by Klaus for LocalRole blocking
      if getattr(inner_obj, '_getAcquireLocalRoles', None) is not None:
        if not inner_obj._getAcquireLocalRoles():
          break

      inner = aq_inner( inner_obj )
      parent = aq_parent( inner )

      if parent is not None:
        inner_obj = parent
        continue

      new = getattr( inner_obj, 'im_self', None )

      if new is not None:
        inner_obj = aq_inner( new )
        continue
      break

    return None

  def getUserValue(self):
    """ -> user document

    Return the document (ex: Person) corresponding to current user.
    """
    result = self._user_value
    if result is not None:
      return result
    user_list = [x for x in self.aq_parent.searchUsers(
      exact_match=True,
      id=self.getId(),
    ) if 'path' in x]
    if user_list:
      user, = user_list
      self._user_value = self.getPortalObject().restrictedTraverse(
        user['path'],
      )
      return self._user_value

  def getLoginValue(self):
    """ -> login document

    Return the document (ex: ERP5 Login) corresponding to current user's login.
    """
    result = self._login_value
    if result is not None:
      return result
    user_list = [x for x in self.aq_parent.searchUsers(
      exact_match=True,
      login=self.getUserName(),
    ) if 'login_list' in x]
    if user_list:
      user, = user_list
      login, = user['login_list']
      self._login_value = self.getPortalObject().restrictedTraverse(
        login['path'],
      )
      return self._login_value

  def getLoginValueList(self, portal_type=None, limit=None):
    """ -> list of login documents

    Return the list of login documents belonging to current user.
    """
    user_list = [x for x in self.aq_parent.searchUsers(
      exact_match=True,
      id=self.getId(),
      login_portal_type=portal_type,
      max_results=limit,
    ) if 'login_list' in x]
    if user_list:
      user, = user_list
      restrictedTraverse = self.getPortalObject().restrictedTraverse
      return [restrictedTraverse(x['path']) for x in user['login_list']]
    return []

InitializeClass(ERP5User)


class ERP5UserFactory(BasePlugin):
  """ PAS plugin for creating users that understand local roles blocking based
  on type information's acquire_local_roles
  """
  meta_type = 'ERP5 User Factory'
  security = ClassSecurityInfo()

  def __init__(self, id, title=None):
    self._id = self.id = id
    self.title = title

  security.declarePrivate('createUser')
  def createUser( self, user_id, name ):
    """ See IUserFactoryPlugin
    """
    return ERP5User(user_id, name)


classImplements( ERP5UserFactory
               , IUserFactoryPlugin
               )

InitializeClass(ERP5UserFactory)
