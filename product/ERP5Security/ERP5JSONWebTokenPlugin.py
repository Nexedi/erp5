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
from Products.PluggableAuthService.permissions import ManageUsers
from Products.PluggableAuthService.PluggableAuthService import DumbHTTPExtractor
from AccessControl.SecurityManagement import getSecurityManager, \
  setSecurityManager, newSecurityManager
from Products.ERP5Type.Cache import DEFAULT_CACHE_SCOPE
from os import urandom as SystemRandom
import socket
from Products.ERP5Security.ERP5UserManager import getUserByLogin
from zLOG import LOG, ERROR, INFO

try:
  from itsdangerous import JSONWebSignatureSerializer
except ImportError:
  JSONWebSignatureSerializer = None


#Form for new plugin in ZMI
manage_addERP5JSONWebTokenPluginForm = PageTemplateFile(
  'www/ERP5Security_addERP5JSONWebTokenPlugin', globals(),
  __name__='manage_addERP5JSONWebTokenPluginForm')

def addERP5JSONWebTokenPlugin(dispatcher, id, title=None, REQUEST=None):
  """ Add a ERP5JSONWebTokenPlugin to a Pluggable Auth Service. """

  plugin = ERP5JSONWebTokenPlugin(id, title)
  dispatcher._setObject(plugin.getId(), plugin)

  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect(
      '%s/manage_workspace'
      '?manage_tabs_message='
      'ERP5JSONWebTokenPlugin+added.'
      % dispatcher.absolute_url())

class ERP5JSONWebTokenPlugin(BasePlugin):

  meta_type = "ERP5 JSON Web Token Plugin"
  security = ClassSecurityInfo()
  cookie_name = "boom_jwt"
  default_cookie_name = "__ac"
    
  manage_options = ( ( { 'label': 'Update Secret',
                          'action': 'manage_updateERP5JSONWebTokenPluginForm', }
                        ,
                      )
                      + BasePlugin.manage_options[:]
                    )


  def __init__(self, id, title=None):
    #Register value
    self._setId(id)
    self.title = title
    self.secret = SystemRandom(256)

  ####################################
  #ILoginPasswordHostExtractionPlugin#
  ####################################
  security.declarePrivate('extractCredentials')
  def extractCredentials(self, request):
    """ Extract JWT from the request header. """

    if JSONWebSignatureSerializer is None:
      LOG('ERP5JSONWebTokenPlugin', INFO,
          'No itsdangerous module, install itsdangerous package. '
            'Authentication disabled.')
      return DumbHTTPExtractor().extractCredentials(request)

    login_pw = request._authUserPW()

    serializer = JSONWebSignatureSerializer(self.secret)

    creds = {}
    if login_pw is not None:
      name, password = login_pw
      creds[ 'login' ] = name
      creds[ 'password' ] = password
      #Save this in cookie
      self.updateCredentials(request, request["RESPONSE"], name, password)
    else:
      token = None
      if self.cookie_name in request.cookies:
        # 1st - try to fetch from Authorization header
        token = request.cookies.get(self.cookie_name)
  
      if token is None:
        # no token
        return DumbHTTPExtractor().extractCredentials(request)
  
      data = serializer.loads(token)
      # token is available
      user = data["user"].encode()
  
      if user is None:
        # fallback to default way
        return DumbHTTPExtractor().extractCredentials(request)
  
    creds['external_login'] = user
    creds['remote_host'] = request.get('REMOTE_HOST', '')
    try:
      creds['remote_address'] = request.getClientAddr()
    except AttributeError:
      creds['remote_address'] = request.get('REMOTE_ADDR', '')
    return creds

  ################################
  #   ICredentialsUpdatePlugin   #
  ################################
  security.declarePrivate('updateCredentials')
  def updateCredentials(self, request, response, login, new_password):
    """ Respond to change of credentials"""
    LOG('ERP5JSONWebTokenPlugin', INFO,
        'Updating Credential')
    LOG('ERP5JSONWebTokenPlugin', INFO,
        'Login is %s' % login)
    serializer = JSONWebSignatureSerializer(self.secret)
    response.setCookie(self.cookie_name, serializer.dumps({"user": login}), path='/')
    response.expireCookie(self.default_cookie_name, path='/')

  ################################
  #    ICredentialsResetPlugin   #
  ################################
  security.declarePrivate('resetCredentials')
  def resetCredentials(self, request, response):
    """Expire cookies of authentification """
    response.expireCookie(self.cookie_name, path='/')
    response.expireCookie(self.default_cookie_name, path='/')


  ################################
  # Properties for ZMI managment #
  ################################

  #'Edit' option form
  manage_updateERP5JSONWebTokenPluginForm = PageTemplateFile(
      'www/ERP5Security_updateERP5JSONWebTokenPlugin',
      globals(),
      __name__='manage_updateERP5JSONWebTokenPlugin')

  security.declareProtected(ManageUsers, 'manage_updateERP5JSONWebTokenPlugin')
  def manage_updateERP5JSONWebTokenPlugin(self, RESPONSE=None):
    """Edit the object"""

    #Save user_id_key
    self.secret = SystemRandom(256)

    #Redirect
    if RESPONSE is not None:
      message = "Secret Updated"
      RESPONSE.redirect('%s/manage_updateERP5JSONWebTokenPluginForm'
                        '?manage_tabs_message=%s'
                        % (self.absolute_url(), message)
                        )


#List implementation of class
classImplements( ERP5JSONWebTokenPlugin,
                plugins.ICredentialsResetPlugin,
                plugins.ILoginPasswordHostExtractionPlugin,
                plugins.ICredentialsUpdatePlugin,
               )
InitializeClass(ERP5JSONWebTokenPlugin)
