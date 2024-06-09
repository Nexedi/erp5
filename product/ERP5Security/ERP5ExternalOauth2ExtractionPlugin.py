# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces import plugins
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.ERP5Security import _setUserNameForAccessLog

from Products.ERP5Type.Cache import DEFAULT_CACHE_SCOPE
import time
from zLOG import LOG, INFO

try:
  import facebook
except ImportError:
  facebook = None


# Form for new plugin in ZMI
manage_addERP5FacebookExtractionPluginForm = PageTemplateFile(
  'www/ERP5Security_addERP5FacebookExtractionPlugin', globals(),
  __name__='manage_addERP5FacebookExtractionPluginForm')



def addERP5FacebookExtractionPlugin(dispatcher, id, title=None, REQUEST=None):
  """ Add a ERP5FacebookExtractionPlugin to a Pluggable Auth Service. """

  plugin = ERP5FacebookExtractionPlugin(id, title)
  dispatcher._setObject(plugin.getId(), plugin)

  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect(
      '%s/manage_workspace'
      '?manage_tabs_message='
      'ERP5FacebookExtractionPlugin+added.'
      % dispatcher.absolute_url())

# Form for new plugin in ZMI
manage_addERP5GoogleExtractionPluginForm = PageTemplateFile(
  'www/ERP5Security_addERP5GoogleExtractionPlugin', globals(),
  __name__='manage_addERP5GoogleExtractionPluginForm')

def addERP5GoogleExtractionPlugin(dispatcher, id, title=None, REQUEST=None):
  """ Add a ERP5GoogleExtractionPlugin to a Pluggable Auth Service. """

  plugin = ERP5GoogleExtractionPlugin(id, title)
  dispatcher._setObject(plugin.getId(), plugin)

  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect(
      '%s/manage_workspace'
      '?manage_tabs_message='
      'ERP5GoogleExtractionPlugin+added.'
      % dispatcher.absolute_url())

class ERP5ExternalOauth2ExtractionPlugin:

  cache_factory_name = 'external_oauth2_token_cache_factory'
  security = ClassSecurityInfo()

  def __init__(self, id, title=None):
    #Register value
    self._setId(id)
    self.title = title

  #####################
  # memcached helpers #
  #####################
  def _getCacheFactory(self):
    portal = self.getPortalObject()
    cache_tool = portal.portal_caches
    cache_factory = cache_tool.getRamCacheRoot().get(self.cache_factory_name)
    #XXX This conditional statement should be remove as soon as
    #Broadcasting will be enable among all zeo clients.
    #Interaction which update portal_caches should interact with all nodes.
    if cache_factory is None \
        and getattr(cache_tool, self.cache_factory_name, None) is not None:
      #ram_cache_root is not up to date for current node
      cache_tool.updateCache()
    cache_factory = cache_tool.getRamCacheRoot().get(self.cache_factory_name)
    if cache_factory is None:
      raise KeyError("Cache factory %s not found" % self.cache_factory_name)
    return cache_factory

  def setToken(self, key, body):
    cache_factory = self._getCacheFactory()
    cache_duration = cache_factory.cache_duration
    for cache_plugin in cache_factory.getCachePluginList():
      cache_plugin.set(key, DEFAULT_CACHE_SCOPE,
                       body, cache_duration=cache_duration)

  def getToken(self, key):
    cache_factory = self._getCacheFactory()
    for cache_plugin in cache_factory.getCachePluginList():
      cache_entry = cache_plugin.get(key, DEFAULT_CACHE_SCOPE)
      if cache_entry is not None:
        cache_value = cache_entry.getValue()
        # getToken is called for the access_token_dict and for
        # the user entry. We try to refresh only for the
        # access_token_dict
        if 'refresh_token' in cache_value:
          return self.refreshTokenIfExpired(key, cache_value)
        return cache_value
    raise KeyError('Key %r not found' % key)

  ####################################
  #ILoginPasswordHostExtractionPlugin#
  ####################################
  security.declarePrivate('extractCredentials')
  def extractCredentials(self, request):
    """ Extract Oauth2 credentials from cookie.

    This plugins uses two level of cache storage:
     - cookie_value => access_token_dict
     - access_token => user_entry

    access_token_dict depends on the concrete plugin classes,
    but this is generally access_token and refresh_token.
    user_entry must contain "reference", which is the reference
    of the corresponding login document in ERP5.
    """
    access_token_dict = {}
    cookie_hash = request.get(self.cookie_name)
    if cookie_hash is not None:
      try:
        access_token_dict = self.getToken(cookie_hash)
      except KeyError:
        LOG(self.getId(), INFO, 'Hash %s not found' % cookie_hash)
        return {}

    token = None
    if "access_token" in access_token_dict:
      token = access_token_dict["access_token"]

    if token is None:
      # no token, then no credentials
      return {}

    user_entry = None
    try:
      user_entry = self.getToken(token)
    except KeyError:
      user_entry = self.getUserEntry(access_token_dict)
      if user_entry is not None:
        # Reduce data size because, we don't need more than reference
        user_entry = {"reference": user_entry["reference"]}

    if user_entry is None:
      # no user, then no credentials
      return {}

    try:
      # Every request will update cache to postpone the cache expiration
      # to keep the user logged in
      self.setToken(token, user_entry)
    except KeyError as error:
      # allow to work w/o cache
      LOG(self.getId(), INFO, error)
      pass

    # Credentials returned here will be used by ERP5LoginUserManager to find the login document
    # having reference `user`.
    creds = {
      "login_portal_type": self.login_portal_type,
      "external_login": user_entry["reference"]
    }

    # PAS wants remote_host / remote_address
    creds['remote_host'] = request.get('REMOTE_HOST', '')
    try:
      creds['remote_address'] = request.getClientAddr()
    except AttributeError:
      creds['remote_address'] = request.get('REMOTE_ADDR', '')

    _setUserNameForAccessLog('%s=%s' % (self.getId(), creds['external_login']) , request)
    return creds

def getFacebookUserEntry(token):
  if facebook is None:
    LOG('ERP5FacebookExtractionPlugin', INFO,
        'No facebook module, install facebook-sdk package. '
          'Authentication disabled.')
    return None
  args = {'fields' : 'id,name,email', }
  facebook_entry = facebook.GraphAPI(token, timeout=5).get_object("me", **args)

  user_entry = {}
  if facebook_entry is not None:
    # sanitise value
    for k in ('name', 'id'):
      v = facebook_entry[k]
      if six.PY2:
        v = v.encode('utf-8')
      try:
        if k == 'id':
          user_entry['reference'] = v
        else:
          user_entry[k] = v
      except KeyError:
        raise ValueError(facebook_entry)
  return user_entry

class ERP5FacebookExtractionPlugin(ERP5ExternalOauth2ExtractionPlugin, BasePlugin):
  """
  Plugin to authenicate as machines.
  """

  meta_type = "ERP5 Facebook Extraction Plugin"
  login_portal_type = "Facebook Login"
  cookie_name = "__ac_facebook_hash"
  cache_factory_name = "facebook_server_auth_token_cache_factory"

  def refreshTokenIfExpired(self, key, access_token_dict):
    return access_token_dict

  def getUserEntry(self, token):
    return getFacebookUserDict(token)


class ERP5GoogleExtractionPlugin(ERP5ExternalOauth2ExtractionPlugin, BasePlugin):
  """
  Plugin to authenticate using google OAuth2.
  """
  meta_type = "ERP5 Google Extraction Plugin"
  login_portal_type = "Google Login"
  cookie_name = "__ac_google_hash"
  cache_factory_name = "google_server_auth_token_cache_factory"

  def refreshTokenIfExpired(self, key, access_token_dict):
    if (time.time() - access_token_dict["response_timestamp"]) \
         >= access_token_dict['expires_in']:
      access_token_dict = self.getPortalObject().unrestrictedTraverse(
        access_token_dict['connector_relative_url']
      ).refreshToken(access_token_dict)
      self.setToken(key, access_token_dict)
    return access_token_dict

  def getUserEntry(self, access_token_dict):
    return self.getPortalObject().unrestrictedTraverse(
      access_token_dict['connector_relative_url'],
    ).getUserEntry(access_token_dict['access_token'])


#List implementation of class
classImplements( ERP5FacebookExtractionPlugin,
                plugins.ILoginPasswordHostExtractionPlugin
               )
InitializeClass(ERP5FacebookExtractionPlugin)

classImplements( ERP5GoogleExtractionPlugin,
                plugins.ILoginPasswordHostExtractionPlugin
               )
InitializeClass(ERP5GoogleExtractionPlugin)

