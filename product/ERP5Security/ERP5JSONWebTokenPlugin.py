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

from datetime import datetime
from urlparse import urlparse
from os import urandom
from zLOG import LOG, INFO, ERROR

from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces import plugins
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.ERP5Security.ERP5UserManager import ERP5UserManager
from Products.PluggableAuthService.permissions import ManageUsers
from Products.PluggableAuthService.PluggableAuthService import DumbHTTPExtractor
from ZODB.utils import u64
from zope.interface import implementer

try:
  import jwt
except ImportError:
  jwt = None


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

@implementer(
  plugins.ILoginPasswordHostExtractionPlugin,
  )
class ERP5JSONWebTokenPlugin(ERP5UserManager):

  meta_type = "ERP5 JSON Web Token Plugin"
  security = ClassSecurityInfo()
  same_site_cookie = "erp5_jwt"
  cors_cookie = "erp5_cors_jwt"

  manage_options = ( ( { 'label': 'Update Secret',
                          'action': 'manage_updateERP5JSONWebTokenPluginForm', }
                        ,
                      )
                      + BasePlugin.manage_options
                    )


  def __init__(self, *args, **kw):
    super(ERP5JSONWebTokenPlugin, self).__init__(*args, **kw)
    self.manage_updateERP5JSONWebTokenPlugin()

  ####################################
  #ILoginPasswordHostExtractionPlugin#
  ####################################
  security.declarePrivate('extractCredentials')
  def extractCredentials(self, request):
    """ Extract JWT from the request header. """
    if jwt is None:
      LOG('ERP5JSONWebTokenPlugin', INFO,
          'No jwt module, install pyjwt package. '
            'Authentication disabled.')
      return DumbHTTPExtractor().extractCredentials(request)

    creds = {}

    login_pw = request._authUserPW()
    if login_pw is not None:
      creds[ 'login' ], creds[ 'password' ] = login_pw
    else:
      # SameSite Policy is implemented serverside
      origin = request.getHeader("Origin", None)
      if origin is None:
        referer_url = request.getHeader("Referer", None)
        if referer_url is not None:
          # Extract origin from Referer Header
          referer_url = urlparse(referer_url)
          origin = referer_url.scheme + "://" + referer_url.netloc

      # If the Origin is None or match the current URL it is ignored
      if origin is None or origin == request.get('BASE0'):
        cookie = self.same_site_cookie
        origin = None
      else:
        cookie = self.cors_cookie

      token = request.cookies.get(cookie)
      if not token:
        return None

      try:
        data = jwt.decode(token, self._secret)
      except (
          jwt.InvalidIssuedAtError,
          jwt.ExpiredSignatureError,
          jwt.InvalidTokenError,
          jwt.DecodeError,
          ):
        request.response.expireCookie(self.same_site_cookie, path='/')
        request.response.expireCookie(self.cors_cookie, path='/')
        return None

      person_relative_url = data["sub"].encode()
      user = self.getPortalObject().unrestrictedTraverse(person_relative_url)

      user.password._p_activate()
      if data["ptid"] == u64(user.password._p_serial) \
          and (not origin or data and \
               origin in data.get('cors', ())):
        creds['person_relative_url'] = person_relative_url

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
    authentication_result = super(
      ERP5JSONWebTokenPlugin,
      self
      ).authenticateCredentials(credentials)

    # In case the password is present in the request, the token is updated
    if authentication_result is not None and "password" in credentials:
      if jwt is None:
        LOG('ERP5JSONWebTokenPlugin', INFO,
            'No jwt module, install pyjwt package. '
              'Authentication disabled.')
        return authentication_result

      if "person_relative_url" not in credentials:
        user = self.getUserByLogin(authentication_result[0])[0]
      else:
        user = self.getPortalObject().unrestrictedTraverse(
          credentials["person_relative_url"]
        )

      user.password._p_activate()
      data = {
        "sub": user.getRelativeUrl(),
        "iat": datetime.utcnow(),
        "ptid": u64(user.password._p_serial)
      }
      cookie_parameters = {
        "path": '/',
        "secure": True,
        "http_only": True,
      }

      request = self.REQUEST

      new_cors_origin = request.form.get('new_cors_origin')
      if new_cors_origin is not None:
        cookie = self.cors_cookie

        authorized_cors_origin_list = []
        token = request.cookies.get(cookie)
        if token is not None:
          try:
            authorized_cors_origin_list = jwt.decode(token, self._secret)[
              "cors"]
          except (
              jwt.InvalidIssuedAtError,
              jwt.ExpiredSignatureError,
              jwt.InvalidTokenError,
              jwt.DecodeError,
              ):
            # Mistakes of the past should stay in the past
            pass
        authorized_cors_origin_list.append(new_cors_origin)
        data["cors"] = authorized_cors_origin_list
      else:
        cookie = self.same_site_cookie
        cookie_parameters["same_site"] = "Lax"

      request.response.setCookie(
        cookie,
        jwt.encode(data, self._secret),
        **cookie_parameters
      )

      # Expire default cookie set by default
      # (even with plugin deactivated)
      request.response.expireCookie('__ac')

    return authentication_result  

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

    self._secret = urandom(16)

    #Redirect
    if RESPONSE is not None:
      message = "Secret Updated"
      RESPONSE.redirect('%s/manage_updateERP5JSONWebTokenPluginForm'
                        '?manage_tabs_message=%s'
                        % (self.absolute_url(), message)
                        )

InitializeClass(ERP5JSONWebTokenPlugin)
