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
from Products.ERP5Security.ERP5UserManager import SUPER_USER, ERP5UserManager
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
  name_cookie = "n_jwt"
  data_cookie = "d_jwt"
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
    self.erp5usermanager = ERP5UserManager(self.getId() + "_user_manager")

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

    name_serializer = JSONWebSignatureSerializer(self.secret)

    creds = {}
    if login_pw is not None:
      name, password = login_pw
      creds[ 'login' ] = name
      creds[ 'password' ] = password
    else:
      name_token = None
      if self.name_cookie in request.cookies:
        # 1st - try to fetch from Authorization header
        name_token = request.cookies.get(self.name_cookie)
  
      #import pdb; pdb.set_trace()
      if name_token is None:
        # no name_token
        return DumbHTTPExtractor().extractCredentials(request)
      # name_token is available
      
      name = name_serializer.loads(name_token)["user"].encode()
  
      if name is None:
        # fallback to default way
        return DumbHTTPExtractor().extractCredentials(request)
      
      self.erp5usermanager = ERP5UserManager(self.getId() + "_user_manager")
      user = self.erp5usermanager.getUserByLogin(name)[0]

      if not user:
        return DumbHTTPExtractor().extractCredentials(request)
      
      data_token = None
      if self.data_cookie in request.cookies:
        # 1st - try to fetch from Authorization header
        data_token = request.cookies.get(self.data_cookie)
      if data_token is None:
        # no name_token
        return DumbHTTPExtractor().extractCredentials(request)

      data_serializer = JSONWebSignatureSerializer(self.secret + user.getPassword())
      data = data_serializer.loads(data_token)
      #import pdb; pdb.set_trace()
      self.getPortalObject().ERP5Site_processJWTData(data)
      creds['external_login'] = name

      # XXX A script should be called here to deal with the data 

    creds['remote_host'] = request.get('REMOTE_HOST', '')
    try:
      creds['remote_address'] = request.getClientAddr()
    except AttributeError:
      creds['remote_address'] = request.get('REMOTE_ADDR', '')
    return creds

  #
  #   IAuthenticationPlugin implementation
  #
  security.declarePrivate( 'authenticateCredentials' )
  def authenticateCredentials(self, credentials):
    LOG('ERP5JSONWebTokenPlugin', INFO,
        'authenticating Credential')
    #if self.erp5usermanager is None:
    self.erp5usermanager = ERP5UserManager(self.getId() + "_user_manager")
    authentication_result = self.erp5usermanager.authenticateCredentials(credentials)
    LOG('ERP5JSONWebTokenPlugin', INFO,
        'authentication result: %s' % str(authentication_result))
    if authentication_result is not None:
      #Save this in cookie
      name = authentication_result[0]
      user = self.erp5usermanager.getUserByLogin(name)[0]
      name_serializer = JSONWebSignatureSerializer(self.secret)
      data_serializer = JSONWebSignatureSerializer(self.secret + user.getPassword())

      request = self.REQUEST
      response = request.response
      response.setCookie(self.name_cookie, name_serializer.dumps({"user": name}), path='/')
      # Update data if needed
      data_token = None
      data = {}
      if self.data_cookie in request.cookies:
        # 1st - try to fetch from Authorization header
        data_token = request.cookies.get(self.data_cookie)
        if data_token is not None:
          # no name_token
          data = data_serializer.loads(data_token)
      data = self.getPortalObject().ERP5Site_updateJWTData(data)
      response.setCookie(self.data_cookie, data_serializer.dumps(data), path='/')
      response.expireCookie(self.default_cookie_name, path='/')
                      
    return authentication_result  

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
    response.setCookie(self.name_cookie, serializer.dumps({"user": login}), path='/')
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
                plugins.IAuthenticationPlugin,
                plugins.ICredentialsResetPlugin,
                plugins.ILoginPasswordHostExtractionPlugin,
                plugins.ICredentialsUpdatePlugin,
               )
InitializeClass(ERP5JSONWebTokenPlugin)
