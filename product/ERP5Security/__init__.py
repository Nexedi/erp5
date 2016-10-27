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
""" ERP5Security product initialization.
"""

from copy import deepcopy

from AccessControl.Permissions import manage_users as ManageUsers
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
from Products.PluggableAuthService.permissions import ManageGroups

import ERP5UserManager
import ERP5LoginUserManager
import ERP5GroupManager
import ERP5RoleManager
import ERP5UserFactory
import ERP5KeyAuthPlugin
import ERP5ExternalAuthenticationPlugin
import ERP5BearerExtractionPlugin
import ERP5ExternalOauth2ExtractionPlugin
import ERP5AccessTokenExtractionPlugin
import ERP5DumbHTTPExtractionPlugin

def mergedLocalRoles(object):
  """Returns a merging of object and its ancestors'
  __ac_local_roles__."""
  # Modified to take into account _getAcquireLocalRoles
  merged = {}
  object = getattr(object, 'aq_inner', object)
  while 1:
    if getattr(object, '__ac_local_roles__', None) is not None:
      roles = object.__ac_local_roles__ or {}
      if callable(roles): roles = roles()
      for k, v in roles.iteritems():
        merged.setdefault(k, []).extend(v)
    # block acquisition
    if getattr(object, '_getAcquireLocalRoles', None) is not None:
      if not object._getAcquireLocalRoles():
        break
    if getattr(object, 'aq_parent', None) is not None:
      object = object.aq_parent
      object = getattr(object, 'aq_inner', object)
      continue
    if getattr(object, 'im_self', None) is not None:
      object = object.im_self
      object = getattr(object, 'aq_inner', object)
      continue
    break

  return deepcopy(merged)

registerMultiPlugin(ERP5UserManager.ERP5UserManager.meta_type)
registerMultiPlugin(ERP5LoginUserManager.ERP5LoginUserManager.meta_type)
registerMultiPlugin(ERP5GroupManager.ERP5GroupManager.meta_type)
registerMultiPlugin(ERP5RoleManager.ERP5RoleManager.meta_type)
registerMultiPlugin(ERP5UserFactory.ERP5UserFactory.meta_type)
registerMultiPlugin(ERP5KeyAuthPlugin.ERP5KeyAuthPlugin.meta_type)
registerMultiPlugin(ERP5ExternalAuthenticationPlugin.ERP5ExternalAuthenticationPlugin.meta_type)
registerMultiPlugin(ERP5BearerExtractionPlugin.ERP5BearerExtractionPlugin.meta_type)
registerMultiPlugin(ERP5ExternalOauth2ExtractionPlugin.ERP5FacebookExtractionPlugin.meta_type)
registerMultiPlugin(ERP5ExternalOauth2ExtractionPlugin.ERP5GoogleExtractionPlugin.meta_type)
registerMultiPlugin(ERP5AccessTokenExtractionPlugin.ERP5AccessTokenExtractionPlugin.meta_type)
registerMultiPlugin(ERP5DumbHTTPExtractionPlugin.ERP5DumbHTTPExtractionPlugin.meta_type)

def initialize(context):

  context.registerClass( ERP5UserManager.ERP5UserManager
                       , permission=ManageUsers
                       , constructors=(
                          ERP5UserManager.manage_addERP5UserManagerForm,
                          ERP5UserManager.addERP5UserManager, )
                       , visibility=None
                       , icon='www/portal.gif'
                       )

  context.registerClass( ERP5LoginUserManager.ERP5LoginUserManager
                       , permission=ManageUsers
                       , constructors=(
                          ERP5LoginUserManager.manage_addERP5LoginUserManagerForm,
                          ERP5LoginUserManager.addERP5LoginUserManager, )
                       , visibility=None
                       , icon='www/portal.gif'
                       )

  context.registerClass( ERP5GroupManager.ERP5GroupManager
                       , permission=ManageGroups
                       , constructors=(
                          ERP5GroupManager.manage_addERP5GroupManagerForm,
                          ERP5GroupManager.addERP5GroupManager, )
                       , visibility=None
                       , icon='www/portal.gif'
                       )

  context.registerClass( ERP5RoleManager.ERP5RoleManager
                       , permission=ManageUsers
                       , constructors=(
                          ERP5RoleManager.manage_addERP5RoleManagerForm,
                          ERP5RoleManager.addERP5RoleManager, )
                       , visibility=None
                       , icon='www/portal.gif'
                       )

  context.registerClass( ERP5UserFactory.ERP5UserFactory
                       , permission=ManageUsers
                       , constructors=(
                          ERP5UserFactory.manage_addERP5UserFactoryForm,
                          ERP5UserFactory.addERP5UserFactory, )
                       , visibility=None
                       , icon='www/portal.gif'
                       )

  context.registerClass( ERP5KeyAuthPlugin.ERP5KeyAuthPlugin
                       , permission=ManageUsers
                       , constructors=(
                          ERP5KeyAuthPlugin.manage_addERP5KeyAuthPluginForm,
                          ERP5KeyAuthPlugin.addERP5KeyAuthPlugin, )
                       , visibility=None
                       , icon='www/portal.gif'
                       )

  context.registerClass( ERP5ExternalAuthenticationPlugin.ERP5ExternalAuthenticationPlugin
                       , permission=ManageUsers
                       , constructors=(
                          ERP5ExternalAuthenticationPlugin.manage_addERP5ExternalAuthenticationPluginForm,
                          ERP5ExternalAuthenticationPlugin.addERP5ExternalAuthenticationPlugin, )
                       , visibility=None
                       , icon='www/portal.gif'
                       )

  context.registerClass( ERP5BearerExtractionPlugin.ERP5BearerExtractionPlugin
                       , permission=ManageUsers
                       , constructors=(
                          ERP5BearerExtractionPlugin.manage_addERP5BearerExtractionPluginForm,
                          ERP5BearerExtractionPlugin.addERP5BearerExtractionPlugin, )
                       , visibility=None
                       , icon='www/portal.gif'
                       )

  context.registerClass( ERP5ExternalOauth2ExtractionPlugin.ERP5FacebookExtractionPlugin
                       , permission=ManageUsers
                       , constructors=(
                          ERP5ExternalOauth2ExtractionPlugin.manage_addERP5FacebookExtractionPluginForm,
                          ERP5ExternalOauth2ExtractionPlugin.addERP5FacebookExtractionPlugin, )
                       , visibility=None
                       , icon='www/portal.gif'
                       )

  context.registerClass( ERP5ExternalOauth2ExtractionPlugin.ERP5GoogleExtractionPlugin
                       , permission=ManageUsers
                       , constructors=(
                          ERP5ExternalOauth2ExtractionPlugin.manage_addERP5GoogleExtractionPluginForm,
                          ERP5ExternalOauth2ExtractionPlugin.addERP5GoogleExtractionPlugin, )
                       , visibility=None
                       , icon='www/portal.gif'
                       )

  context.registerClass( ERP5AccessTokenExtractionPlugin.ERP5AccessTokenExtractionPlugin
                       , permission=ManageUsers
                       , constructors=(
                          ERP5AccessTokenExtractionPlugin.manage_addERP5AccessTokenExtractionPluginForm,
                          ERP5AccessTokenExtractionPlugin.addERP5AccessTokenExtractionPlugin, )
                       , visibility=None
                       , icon='www/portal.gif'
                       )

  context.registerClass( ERP5DumbHTTPExtractionPlugin.ERP5DumbHTTPExtractionPlugin
                       , permission=ManageUsers
                       , constructors=(
                          ERP5DumbHTTPExtractionPlugin.manage_addERP5DumbHTTPExtractionPluginForm,
                          ERP5DumbHTTPExtractionPlugin.addERP5DumbHTTPExtractionPlugin, )
                       , visibility=None
                       , icon='www/portal.gif'
                       )

from AccessControl.SecurityInfo import ModuleSecurityInfo
ModuleSecurityInfo('Products.ERP5Security.ERP5UserManager').declarePublic(
  'getUserByLogin')
