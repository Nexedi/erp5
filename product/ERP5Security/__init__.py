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
from __future__ import absolute_import

from copy import deepcopy
from collections import defaultdict
from base64 import encodebytes

from Acquisition import aq_inner, aq_parent
from AccessControl.Permissions import manage_users as ManageUsers
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
from Products.PluggableAuthService.permissions import ManageGroups
from Products.ERP5Type import IS_ZOPE2
import six

# This user is used to bypass all security checks.
SUPER_USER = '__erp5security-=__'

def mergedLocalRoles(object):
  """Returns a merging of object and its ancestors'
  __ac_local_roles__."""
  # Modified to take into account _getAcquireLocalRoles
  merged = defaultdict(list)
  object = aq_inner(object)
  while 1:
    local_role_dict = getattr(object, '__ac_local_roles__', None)
    if local_role_dict:
      if callable(local_role_dict):
        local_role_dict = local_role_dict() or {}
      for k, v in six.iteritems(local_role_dict):
        merged[k] += v
    # block acquisition
    if not getattr(object, '_getAcquireLocalRoles', lambda: True)():
      break
    parent = aq_parent(object)
    if parent is not None:
      object = aq_inner(parent)
      continue
    self = getattr(object, '__self__', None)
    if self is not None:
      object = aq_inner(self)
      continue
    break
  return deepcopy(merged)


if IS_ZOPE2: # BBB
  def _setUserNameForAccessLog(username, REQUEST):
    """Make the current user look as `username` in Zope's Z2.log

  Taken from Products.CMFCore.CookieCrumbler._setAuthHeader
  """
  # Set the authorization header in the medusa http request
  # so that the username can be logged to the Z2.log
  # Put the full-arm latex glove on now...
  try:
    # Is this WSGI ?
    REQUEST._orig_env['wsgi.input']
  except KeyError:
    # Not WSGI, maybe Medusa
    try:
      medusa_headers = REQUEST.RESPONSE.stdout._request._header_cache
    except AttributeError:
      pass
    else:
      medusa_headers['authorization'] = 'Basic %s' % encodebytes(('%s:' % username).encode()).decode().rstrip()
  else:
    REQUEST._orig_env['REMOTE_USER'] = username
else: # zope4
  def _setUserNameForAccessLog(username, REQUEST):
    """
    Nothing to do for this on Zope4.
    """
    pass

def initialize(context):
  from . import (
    ERP5UserManager,
    ERP5LoginUserManager,
    ERP5GroupManager,
    ERP5RoleManager,
    ERP5UserFactory,
    ERP5KeyAuthPlugin,
    ERP5ExternalAuthenticationPlugin,
    ERP5BearerExtractionPlugin,
    ERP5ExternalOauth2ExtractionPlugin,
    ERP5AccessTokenExtractionPlugin,
    ERP5DumbHTTPExtractionPlugin,
    ERP5ExternalOpenIdConnectExtractionPlugin,
    ERP5OAuth2ResourceServerPlugin,
  )

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
  registerMultiPlugin(ERP5ExternalOpenIdConnectExtractionPlugin.ERP5OpenIdConnectExtractionPlugin.meta_type)
  registerMultiPlugin(ERP5OAuth2ResourceServerPlugin.ERP5OAuth2ResourceServerPlugin.meta_type)


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

  context.registerClass( ERP5ExternalOpenIdConnectExtractionPlugin.ERP5OpenIdConnectExtractionPlugin
                       , permission=ManageUsers
                       , constructors=(
                          ERP5ExternalOpenIdConnectExtractionPlugin.manage_addERP5OpenIdConnectExtractionPluginForm,
                          ERP5ExternalOpenIdConnectExtractionPlugin.addERP5OpenIdConnectExtractionPlugin, )
                       , visibility=None
                       , icon='www/portal.gif'
                       )

  context.registerClass( ERP5OAuth2ResourceServerPlugin.ERP5OAuth2ResourceServerPlugin
                       , permission=ManageUsers
                       , constructors=(
                          ERP5OAuth2ResourceServerPlugin.manage_addERP5OAuth2ResourceServerPluginForm,
                          ERP5OAuth2ResourceServerPlugin.addERP5OAuth2ResourceServerPlugin, )
                       , visibility=None
                       , icon='www/portal.gif'
                       )
