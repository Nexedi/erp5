# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011-2013 Nexedi SA and Contributors. All Rights Reserved.
#                    Francois-Xavier Algrain <fxalgrain@tiolive.com>
#                    Romain Courteaud <romain@nexedi.com>
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

from Products.ERP5Type.Globals import InitializeClass

from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.PluggableAuthService.interfaces import plugins
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin

from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod

class ERP5AccessTokenExtractionPlugin(BasePlugin):
  """
    Access Token PAS plugin which support custom access token creation in an
    ERP5 module.

    It depends on the erp5_access_token bt5.
  """

  meta_type = "ERP5 Access Token Extraction Plugin"
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
    # Extract token from HTTP Header
    token = request.getHeader("X-ACCESS-TOKEN", request.form.get("access_token", None))
    if token:
      creds['erp5_access_token_id'] = token
      creds['remote_host'] = request.get('REMOTE_HOST', '')
      try:
        creds['remote_address'] = request.getClientAddr()
      except AttributeError:
        creds['remote_address'] = request.get('REMOTE_ADDR', '')
    return creds

  #######################
  #IAuthenticationPlugin#
  #######################
  security.declarePrivate('authenticateCredentials')
  @UnrestrictedMethod
  def authenticateCredentials(self, credentials):
    """ Map credentials to a user ID. """
    if 'erp5_access_token_id' in credentials:
      erp5_access_token_id = credentials['erp5_access_token_id']
      token_document = self.getPortalObject().access_token_module.\
                     _getOb(erp5_access_token_id, None)
      # Access Token should be validated
      # Check restricted access of URL
      # Extract login information
      if token_document is not None:
        user_id = None
        method = token_document._getTypeBasedMethod('getUserId')
        if method is not None:
          user_id = method()

        if user_id is not None:
          return (user_id, 'token {erp5_access_token_id} for {user_id}'.format(**locals()))


#Form for new plugin in ZMI
manage_addERP5AccessTokenExtractionPluginForm = PageTemplateFile(
  'www/ERP5Security_addERP5AccessTokenExtractionPlugin', globals(),
  __name__='manage_addERP5AccessTokenExtractionPluginForm')

def addERP5AccessTokenExtractionPlugin(dispatcher, id, title=None, REQUEST=None):
  """ Add an ERP5AccessTokenExtractionPlugin to a Pluggable Auth Service. """

  plugin = ERP5AccessTokenExtractionPlugin(id, title)
  dispatcher._setObject(plugin.getId(), plugin)

  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect(
      '%s/manage_workspace'
      '?manage_tabs_message='
      'ERP5AccessTokenExtractionPlugin+added.'
      % dispatcher.absolute_url())

#List implementation of class
classImplements(ERP5AccessTokenExtractionPlugin,
                plugins.ILoginPasswordHostExtractionPlugin,
                plugins.IAuthenticationPlugin,
                )
InitializeClass(ERP5AccessTokenExtractionPlugin)
