# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
#                    Tristan Cavelier <tristan.cavelier@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

from base64 import standard_b64encode

from Products.ERP5Type.Globals import InitializeClass

from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.PluggableAuthService.interfaces import plugins
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.PluggableAuthService import DumbHTTPExtractor

from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod

class ERP5DumbHTTPExtractionPlugin(BasePlugin):
  """
    Default authentication behavior
  """

  meta_type = "ERP5 Dumb HTTP Extraction Plugin"
  security = ClassSecurityInfo()

  def __init__(self, id, title=None):
    #Register value
    self._setId(id)
    self.title = title
    self.cookie_name = "__ac"

  security.declarePrivate('extractCredentials')
  @UnrestrictedMethod
  def extractCredentials(self, request):
    return DumbHTTPExtractor().extractCredentials(request);

  ################################
  #   ICredentialsUpdatePlugin   #
  ################################
  security.declarePrivate('updateCredentials')
  def updateCredentials(self, request, response, login, password):
    """ Respond to change of credentials"""
    kw = {}
    portal = self.getPortalObject()
    expire_interval = portal.portal_preferences.getPreferredMaxUserInactivityDuration()
    if expire_interval in ('', None):
      ac_renew = float('inf')
    else:
      expire_interval /= 86400. # seconds -> days
      now = DateTime()
      kw['expires'] = (now + expire_interval).toZone('GMT').rfc822()
      ac_renew = (now + expire_interval / 2).millis()
    portal.portal_sessions[
      portal.Base_getAutoLogoutSessionKey(username=login)
    ]['ac_renew'] = ac_renew
    response.setCookie(
      name="__ac",
      value=standard_b64encode('%s:%s' % (login, password)),
      path='/',
      secure=getattr(portal, 'REQUEST', {}).get('SERVER_URL', '').startswith('https:'),
      http_only=True,
      **kw
    )

  ################################
  #    ICredentialsResetPlugin   #
  ################################
  security.declarePrivate( 'resetCredentials' )
  def resetCredentials( self, request, response ):

    """ Logout
    """
    response.expireCookie("__ac", path="/")


#Form for new plugin in ZMI
manage_addERP5DumbHTTPExtractionPluginForm = PageTemplateFile(
  'www/ERP5Security_addERP5DumbHTTPExtractionPlugin', globals(),
  __name__='manage_addERP5DumbHTTPExtractionPluginForm')

def addERP5DumbHTTPExtractionPlugin(dispatcher, id, title=None, REQUEST=None):
  """ Add an ERP5DumbHTTPExtractionPlugin to a Pluggable Auth Service. """

  plugin = ERP5DumbHTTPExtractionPlugin(id, title)
  dispatcher._setObject(plugin.getId(), plugin)

  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect(
      '%s/manage_workspace'
      '?manage_tabs_message='
      'ERP5DumbHTTPExtractionPlugin+added.'
      % dispatcher.absolute_url())

#List implementation of class
classImplements(ERP5DumbHTTPExtractionPlugin,
                plugins.ILoginPasswordHostExtractionPlugin,
                plugins.ICredentialsResetPlugin,
                plugins.ICredentialsUpdatePlugin,
               )
InitializeClass(ERP5DumbHTTPExtractionPlugin)
