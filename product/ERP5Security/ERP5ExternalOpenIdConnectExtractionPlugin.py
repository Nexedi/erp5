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

from Products.ERP5Security.ERP5ExternalOauth2ExtractionPlugin import ERP5ExternalOauth2ExtractionPlugin

from AccessControl.SecurityManagement import getSecurityManager, \
  setSecurityManager, newSecurityManager
from Products.ERP5Type.Cache import DEFAULT_CACHE_SCOPE
import time
import socket
import http.client
import urllib.request, urllib.parse, urllib.error
import json
from zLOG import LOG, ERROR, INFO


#Form for new plugin in ZMI
manage_addERP5OpenIdConnectExtractionPluginForm = PageTemplateFile(
  'www/ERP5Security_addERP5OpenIdConnectExtractionPlugin', globals(),
  __name__='manage_addERP5OpenIdConnectExtractionPluginForm')

def addERP5OpenIdConnectExtractionPlugin(dispatcher, id, title=None, REQUEST=None):
  """ Add a ERP5OpenIdConnectExtractionPlugin to a Pluggable Auth Service. """

  plugin = ERP5OpenIdConnectExtractionPlugin(id, title)
  dispatcher._setObject(plugin.getId(), plugin)

  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect(
      '%s/manage_workspace'
      '?manage_tabs_message='
      'ERP5OpenIdConnectExtractionPlugin+added.'
      % dispatcher.absolute_url())

class ERP5OpenIdConnectExtractionPlugin(ERP5ExternalOauth2ExtractionPlugin, BasePlugin):
  """
  Plugin to authenticate with OpenId Connect.
  """

  meta_type = "ERP5 OpenId Connect Extraction Plugin"
  login_portal_type = "OpenId Connect Login"
  cookie_name = "__ac_openidconnect_hash"
  cache_factory_name = "openid_connect_server_auth_token_cache_factory"

  def refreshTokenIfExpired(self, key, cache_value):
    expires_in = cache_value.get("token_response", {}).get("expires_in")
    refresh_token = cache_value.get("refresh_token")
    if expires_in and refresh_token:
      if (time.time() - cache_value["response_timestamp"]) >= float(expires_in):
        credential = self.portal.ERP5Site_getAccessTokenFromRefreshToken(
          response_dict={
            'access_token': cache_value["access_token"],
            'token_type': cache_value["token_type"],
            'expires_in': cache_value["expires_in"],
            'refresh_token': cache_value["refresh_token"],
          }
        )
        cache_value = credential
        cache_value["response_timestamp"] = time.time()
        self.setToken(key, cache_value)
    return cache_value

  def getUserEntry(self, token):
    return self.getPortalObject().ERP5Site_getOpenIdUserEntry(token)

#List implementation of class
classImplements( ERP5OpenIdConnectExtractionPlugin,
                plugins.ILoginPasswordHostExtractionPlugin
               )
InitializeClass(ERP5OpenIdConnectExtractionPlugin)