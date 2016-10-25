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
from Products.ERP5Security.ERP5UserManager import SUPER_USER
from Products.PluggableAuthService.PluggableAuthService import DumbHTTPExtractor
from AccessControl.SecurityManagement import getSecurityManager, \
  setSecurityManager, newSecurityManager
from Products.ERP5Type.Cache import DEFAULT_CACHE_SCOPE
import socket
from zLOG import LOG, ERROR, INFO

try:
  import facebook
except ImportError:
  facebook = None

try:
  import apiclient.discovery
  import httplib2
  import oauth2client.client
except ImportError:
  httplib2 = None

#Form for new plugin in ZMI
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

#Form for new plugin in ZMI
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

  cache_factory_name = 'extrenal_oauth2_token_cache_factory'
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
      raise KeyError
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
        return cache_entry.getValue()
    raise KeyError('Key %r not found' % key)

  ####################################
  #ILoginPasswordHostExtractionPlugin#
  ####################################
  security.declarePrivate('extractCredentials')
  def extractCredentials(self, request):
    """ Extract Oauth2 credentials from the request header. """
    Base_createOauth2User = getattr(self.getPortalObject(),
      'Base_createOauth2User', None)
    if Base_createOauth2User is None:
      LOG('ERP5ExternalOauth2ExtractionPlugin', INFO,
          'No Base_createOauth2User script available, install '
            'erp5_credential_oauth2, disabled authentication.')
      return DumbHTTPExtractor().extractCredentials(request)

    creds = {}
    token = None
    if request._auth is not None:
      # 1st - try to fetch from Authorization header
      if self.header_string.lower() in request._auth.lower():
        l = request._auth.split()
        if len(l) == 2:
          token = l[1]

    if token is None:
      # no token
      return DumbHTTPExtractor().extractCredentials(request)

    # token is available
    user = None
    user_entry = None
    try:
      user = self.getToken(self.prefix + token)
    except KeyError:
      user_entry = self.getUserEntry(token)
      if user_entry is not None:
        user = user_entry['reference']

    if user is None:
      # fallback to default way
      return DumbHTTPExtractor().extractCredentials(request)

    tag = '%s_user_creation_in_progress' % user.encode('hex')

    if self.getPortalObject().portal_activities.countMessageWithTag(tag) > 0:
      self.REQUEST['USER_CREATION_IN_PROGRESS'] = user
    else:
      # create the user if not found
      if not self.searchUsers(id=user, exact_match=True):
        sm = getSecurityManager()
        if sm.getUser().getId() != SUPER_USER:
          newSecurityManager(self, self.getUser(SUPER_USER))
        try:
          self.REQUEST['USER_CREATION_IN_PROGRESS'] = user
          if user_entry is None:
            user_entry = self.getUserEntry(token)
          try:
            self.Base_createOauth2User(tag, **user_entry)
          except Exception:
            LOG('ERP5ExternalOauth2ExtractionPlugin', ERROR,
              'Issue while calling creation script:', error=True)
            raise
        finally:
          setSecurityManager(sm)
    try:
      self.setToken(self.prefix + token, user)
    except KeyError:
      # allow to work w/o cache
      pass
    creds['external_login'] = user
    creds['remote_host'] = request.get('REMOTE_HOST', '')
    try:
      creds['remote_address'] = request.getClientAddr()
    except AttributeError:
      creds['remote_address'] = request.get('REMOTE_ADDR', '')
    return creds

class ERP5FacebookExtractionPlugin(ERP5ExternalOauth2ExtractionPlugin, BasePlugin):
  """
  Plugin to authenicate as machines.
  """

  meta_type = "ERP5 Facebook Extraction Plugin"
  prefix = 'fb_'
  header_string = 'facebook'

  def getUserEntry(self, token):
    if facebook is None:
      LOG('ERP5FacebookExtractionPlugin', INFO,
          'No facebook module, install facebook-sdk package. '
            'Authentication disabled.')
      return None
    timeout = socket.getdefaulttimeout()
    try:
      # require really fast interaction
      socket.setdefaulttimeout(5)
      facebook_entry = facebook.GraphAPI(token).get_object("me")
    except Exception:
      facebook_entry = None
    finally:
      socket.setdefaulttimeout(timeout)

    user_entry = {}
    if facebook_entry is not None:
      # sanitise value
      try:
        for k in ('first_name', 'last_name', 'id', 'email'):
          if k == 'id':
            user_entry['reference'] = self.prefix + facebook_entry[k].encode(
              'utf-8')
          else:
            user_entry[k] = facebook_entry[k].encode('utf-8')
      except KeyError:
        user_entry = None
    return user_entry

class ERP5GoogleExtractionPlugin(ERP5ExternalOauth2ExtractionPlugin, BasePlugin):
  """
  Plugin to authenicate as machines.
  """

  meta_type = "ERP5 Google Extraction Plugin"
  prefix = 'go_'
  header_string = 'google'

  def getUserEntry(self, token):
    if httplib2 is None:
      LOG('ERP5GoogleExtractionPlugin', INFO,
        'No Google modules available, please install google-api-python-client '
        'package. Authentication disabled..')
      return None
    timeout = socket.getdefaulttimeout()
    try:
      # require really fast interaction
      socket.setdefaulttimeout(5)
      http = oauth2client.client.AccessTokenCredentials(token, 'ERP5 Client'
        ).authorize(httplib2.Http())
      service = apiclient.discovery.build("oauth2", "v1", http=http)
      google_entry = service.userinfo().get().execute()
    except Exception:
      google_entry = None
    finally:
      socket.setdefaulttimeout(timeout)

    user_entry = {}
    if google_entry is not None:
      # sanitise value
      try:
        for k in (('first_name', 'given_name'),
            ('last_name', 'family_name'),
            ('reference', 'id'),
            ('email', 'email')):
          value = google_entry[k[1]].encode('utf-8')
          if k[0] == 'reference':
            value = self.prefix + value
          user_entry[k[0]] = value
      except KeyError:
        user_entry = None
    return user_entry

#List implementation of class
classImplements( ERP5FacebookExtractionPlugin,
                plugins.ILoginPasswordHostExtractionPlugin
               )
InitializeClass(ERP5FacebookExtractionPlugin)

classImplements( ERP5GoogleExtractionPlugin,
                plugins.ILoginPasswordHostExtractionPlugin
               )
InitializeClass(ERP5GoogleExtractionPlugin)

