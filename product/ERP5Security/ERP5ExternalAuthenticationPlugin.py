# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.PluggableAuthService.permissions import ManageUsers
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.PluggableAuthService import DumbHTTPExtractor

#Form for new plugin in ZMI
manage_addERP5ExternalAuthenticationPluginForm = PageTemplateFile(
  'www/ERP5Security_addERP5ExternalAuthenticationPlugin', globals(),
  __name__='manage_addERP5ExternalAuthenticationPluginForm')

def addERP5ExternalAuthenticationPlugin(dispatcher, id, title=None, user_id_key='',
                 login_portal_type_list=None, REQUEST=None):
  """ Add a ERP5ExternalAuthenticationPlugin to a Pluggable Auth Service. """

  plugin = ERP5ExternalAuthenticationPlugin(id, title, user_id_key, login_portal_type_list)
  dispatcher._setObject(plugin.getId(), plugin)

  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect(
      '%s/manage_workspace'
      '?manage_tabs_message='
      'ERP5ExternalAuthenticationPlugin+added.'
      % dispatcher.absolute_url())

class ERP5ExternalAuthenticationPlugin(BasePlugin):
  """
  External authentification PAS plugin which extracts the user id from HTTP
  request header, like REMOTE_USER, openAMid, etc.
  """

  meta_type = "ERP5 External Authentication Plugin"
  security = ClassSecurityInfo()
  user_id_key = ''

  manage_options = (({'label': 'Edit',
                      'action': 'manage_editERP5ExternalAuthenticationPluginForm',},
                     )
                    + BasePlugin.manage_options[:]
                    )

  _properties = (({'id':'user_id_key',
                   'type':'string',
                   'mode':'w',
                   'label':'HTTP request header key where the user_id is stored'
                   },
                  {'id': 'login_portal_type_list',
                   'type':'lines',
                   'mode':'w',
                   'label': 'List of Login Portal Types to search'
                   },

                  )
                 + BasePlugin._properties[:]
                 )

  def __init__(self, id, title=None, user_id_key='', login_portal_type_list=None):
    #Register value
    self._setId(id)
    self.title = title
    self.user_id_key = user_id_key

    if login_portal_type_list is None:
      # Keep at least one portal type as Login
      login_portal_type_list = ["ERP5 Login"]

    self.login_portal_type_list = login_portal_type_list

  ####################################
  #ILoginPasswordHostExtractionPlugin#
  ####################################
  security.declarePrivate('extractCredentials')
  def extractCredentials(self, request):
    """ Extract credentials from the request header. """
    creds = {}
    getHeader = getattr(request, 'getHeader', None)
    if getHeader is None:
      # use get_header instead for Zope-2.8
      getHeader = request.get_header
    external_login = getHeader(self.user_id_key)
    if external_login is not None:
      creds['external_login'] = external_login
      creds['login_portal_type'] = self.login_portal_type_list
    else:
      # fallback to default way
      return DumbHTTPExtractor().extractCredentials(request)

    #Complete credential with some information
    if creds:
      creds['remote_host'] = request.get('REMOTE_HOST', '')
      try:
        creds['remote_address'] = request.getClientAddr()
      except AttributeError:
        creds['remote_address'] = request.get('REMOTE_ADDR', '')

    return creds

  ################################
  # Properties for ZMI managment #
  ################################

  #'Edit' option form
  manage_editERP5ExternalAuthenticationPluginForm = PageTemplateFile(
      'www/ERP5Security_editERP5ExternalAuthenticationPlugin',
      globals(),
      __name__='manage_editERP5ExternalAuthenticationPluginForm')

  security.declareProtected(ManageUsers, 'manage_editERP5ExternalAuthenticationPlugin')
  def manage_editERP5ExternalAuthenticationPlugin(self, user_id_key, login_portal_type_list, RESPONSE=None):
    """Edit the object"""
    error_message = ''

    #Save user_id_key
    if user_id_key == '' or user_id_key is None:
      error_message += 'Invalid key value '
    else:
      self.user_id_key = user_id_key

    if login_portal_type_list == '' or login_portal_type_list is None:
      error_message += 'Invalid portal type value '
    else:
      self.login_portal_type_list = login_portal_type_list

    #Redirect
    if RESPONSE is not None:
      if error_message != '':
        self.REQUEST.form['manage_tabs_message'] = error_message
        return self.manage_editERP5ExternalAuthenticationPluginForm(RESPONSE)
      else:
        message = "Updated"
        RESPONSE.redirect('%s/manage_editERP5ExternalAuthenticationPluginForm'
                          '?manage_tabs_message=%s'
                          % (self.absolute_url(), message)
                          )

#List implementation of class
classImplements(ERP5ExternalAuthenticationPlugin,
                plugins.ILoginPasswordHostExtractionPlugin)

InitializeClass(ERP5ExternalAuthenticationPlugin)
