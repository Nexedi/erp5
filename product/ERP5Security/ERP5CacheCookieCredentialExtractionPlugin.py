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
from zLOG import LOG, WARNING
from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces import plugins
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from .utils import getHostFromRequest

class ERP5CacheCookieCredentialExtractionPlugin(BasePlugin):
  """
  Extracts credentials from a ram cache, based on a cookie value received
  from request.
  """
  security = ClassSecurityInfo()
  meta_type = 'ERP5 Cache Cookie Credential Extraction Plugin'

  _properties=(
      {'id': 'cookie_id', 'type': 'string', 'mode': 'w'},
      {'id': 'cache_factory_id', 'type': 'string', 'mode': 'w'},
      {'id': 'cache_scope', 'type': 'string', 'mode': 'w'},
  )

  def __init__(self, id, cookie_id, cache_factory_id, title=None,
      cache_scope=None):
    self._setId(id)
    self.title = title
    self.cookie_id = cookie_id
    self.cache_factory_id = cache_factory_id
    self.cache_scope = cache_scope

  security.declarePrivate('extractCredentials')
  def extractCredentials(self, request):
    try:
      cookie = request.cookies[self.cookie_id]
    except KeyError:
      pass
    else:
      portal_caches = self.getPortalObject().portal_caches
      try:
        # TODO: When portal_cache allows accessing factories from persistent
        # objects, catch AttributeError instead of KeyError and replace the
        # following line with this:
        #cache_factory = getattr(portal_caches, self.cache_factory_id)
        # XXX: getRamCacheRoot is misnamed: its return value contains all kinds
        # of caches, actually.
        cache_factory = portal_caches.getRamCacheRoot()[self.cache_factory_id]
      except KeyError:
        LOG(self.id, WARNING, 'Cache factory not found: %r' % (
          self.cache_factory_id, ))
      else:
        for cache_plugin in cache_factory.getCachePluginList():
          cache_entry = cache_plugin.get(cookie, self.cache_scope or
            self.cookie_id, None)
          if cache_entry is not None:
            entry_value = cache_entry.getValue()
            try:
              login = entry_value['login']
            except KeyError:
              pass
            else:
              remote_host, remote_address = getHostFromRequest(request)
              return {
                'external_login': login,
                'remote_host': remote_host,
                'remote_address': remote_address,
              }
    return {}

classImplements(ERP5CacheCookieCredentialExtractionPlugin,
  plugins.IExtractionPlugin,
)
InitializeClass(ERP5CacheCookieCredentialExtractionPlugin)

manage_addERP5CacheCookieCredentialExtractionPluginForm = PageTemplateFile(
  'www/ERP5Security_addERP5CacheCookieCredentialExtractionPlugin', globals(),
  __name__='manage_addERP5CacheCookieCredentialExtractionPluginForm')

def addERP5CacheCookieCredentialExtractionPlugin(dispatcher, id, cookie_id,
    cache_scope, cache_factory_id, title=None, REQUEST=None):
  """ bla bla, mandatory docstring """
  if not cookie_id:
    raise ValueError('cookie_id is mandatory')
  if not cache_factory_id:
    raise ValueError('cache_factory_id is mandatory')
  plugin = ERP5CacheCookieCredentialExtractionPlugin(
    id=id,
    title=title,
    cookie_id=cookie_id,
    cache_scope=cache_scope,
    cache_factory_id=cache_factory_id,
  )
  dispatcher._setObject(plugin.getId(), plugin)
  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect(
      dispatcher.absolute_url() + '/manage_workspace?manage_tabs_message='
        'Add+ERP5+Cache+Cookie+Credential+Extraction+Plugin+added.',
    )
