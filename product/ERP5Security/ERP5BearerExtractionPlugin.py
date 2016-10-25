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
from Products.ERP5Type.UnrestrictedMethod import super_user
from Products.PluggableAuthService.PluggableAuthService import DumbHTTPExtractor
from AccessControl.SecurityManagement import getSecurityManager, \
  setSecurityManager, newSecurityManager

#Form for new plugin in ZMI
manage_addERP5BearerExtractionPluginForm = PageTemplateFile(
  'www/ERP5Security_addERP5BearerExtractionPlugin', globals(),
  __name__='manage_addERP5BearerExtractionPluginForm')

def addERP5BearerExtractionPlugin(dispatcher, id, title=None, REQUEST=None):
  """ Add a ERP5BearerExtractionPlugin to a Pluggable Auth Service. """

  plugin = ERP5BearerExtractionPlugin(id, title)
  dispatcher._setObject(plugin.getId(), plugin)

  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect(
      '%s/manage_workspace'
      '?manage_tabs_message='
      'ERP5BearerExtractionPlugin+added.'
      % dispatcher.absolute_url())

class ERP5BearerExtractionPlugin(BasePlugin):
  """
  Plugin to authenicate as machines.
  """

  meta_type = "ERP5 Bearer Extraction Plugin"
  security = ClassSecurityInfo()

  def __init__(self, id, title=None):
    #Register value
    self._setId(id)
    self.title = title

  ####################################
  #ILoginPasswordHostExtractionPlugin#
  ####################################
  security.declarePrivate('extractCredentials')
  def extractCredentials(self, request):
    """ Extract credentials from the request header. """
    creds = {}
    token = None
    if request._auth is not None:
      # 1st - try to fetch from Authorization header
      if 'bearer' in request._auth.lower():
        l = request._auth.split()
        if len(l) == 2:
          token = l[1]

    if token is None:
      # 2nd - try to fetch from Form-Encoded Body Parameter
      #   Not implemented as not required and enforced with high
      #   security considerations
      pass

    if token is None:
      # 3rd - try to fetch from URI Query Parameter
      #   Not implemented as considered as unsecure.
      pass

    if token is not None:
      with super_user():
        reference = self.Base_extractBearerTokenInformation(token)
        if reference is not None:
          creds['external_login'] = reference
      if 'external_login' in  creds:
        creds['remote_host'] = request.get('REMOTE_HOST', '')
        try:
          creds['remote_address'] = request.getClientAddr()
        except AttributeError:
          creds['remote_address'] = request.get('REMOTE_ADDR', '')
        return creds

    # fallback to default way
    return DumbHTTPExtractor().extractCredentials(request)

  manage_editERP5BearerExtractionPluginForm = PageTemplateFile(
      'www/ERP5Security_editERP5BearerExtractionPlugin',
      globals(),
      __name__='manage_editERP5BearerExtractionPluginForm')

#List implementation of class
classImplements( ERP5BearerExtractionPlugin,
                plugins.ILoginPasswordHostExtractionPlugin
               )
InitializeClass(ERP5BearerExtractionPlugin)
