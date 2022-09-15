# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Francois-Xavier Algrain <fxalgrain@tiolive.com>
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

from base64 import encodestring, decodestring
from six.moves.urllib.parse import quote, unquote
from DateTime import DateTime
from zLOG import LOG, PROBLEM
from Products.ERP5Type.Globals import InitializeClass
from zope.interface import Interface

from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.PluggableAuthService.interfaces import plugins
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.permissions import ManageUsers
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.plugins.CookieAuthHelper import CookieAuthHelper

from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5Type.Utils import bytes2str
from Products.ERP5Security.ERP5UserManager import ERP5UserManager, \
                                                  _AuthenticationFailure
from Products import ERP5Security

from Crypto.Cipher import AES
from Crypto import Random
from base64 import urlsafe_b64decode, urlsafe_b64encode

class AESCipher:
  mode = AES.MODE_CFB

  def __init__(self, encryption_key):
    # AES key must be either 16, 24, or 32 bytes long
    self.encryption_key = encryption_key.ljust(32)[:32]

  def encrypt(self, login):
    iv = Random.new().read(AES.block_size)
    encryptor = AES.new(self.encryption_key, self.mode, IV=iv)
    return urlsafe_b64encode(iv + encryptor.encrypt(login.ljust(((len(login)-1)//16+1)*16)))

  def decrypt(self, crypted_login):
    decoded_crypted_login = urlsafe_b64decode(crypted_login)
    iv = decoded_crypted_login[:AES.block_size]
    decryptor = AES.new(self.encryption_key, self.mode, IV=iv)
    return decryptor.decrypt(decoded_crypted_login[AES.block_size:]).rstrip()

# This cipher is weak. Do not use.
class CesarCipher:
  block_length = 3

  def __init__(self, encryption_key):
    self.encryption_key = encryption_key
    self.encrypted_key = self.transformKey(self.encryption_key);

  def transformKey(self, key):
    """Transform the key to number for encryption"""
    encrypt_key = []
    for letter in key:
      encrypt_key.append(ord(letter))
    return encrypt_key

  def encrypt(self, login):
    crypted_login = ''
    key_length = len(self.encrypted_key)
    for i in range(0, len(login)):
      delta = i % key_length
      crypted_letter = str(ord(login[i]) + self.encrypted_key[delta])
      #ord is the inverse of chr() for 8-bit (1111 1111 = 256)
      #so crypted_letter max id 512
      #we ajust length to be able to decrypt by block
      crypted_letter = crypted_letter.rjust(self.block_length, '0')
      crypted_login += crypted_letter
    return crypted_login

  def decrypt(self, crypted_login):
    login = ''
    clogin_length = len(crypted_login)
    if clogin_length % self.block_length != 0:
      raise ValueError("Invalid length")
    #decrypt block per block
    position = 0
    key_length = len(self.encrypted_key)
    for block in range(0, clogin_length, self.block_length):
      delta = position % key_length
      crypted_letter = crypted_login[block:block + self.block_length]
      crypted_letter = int(crypted_letter) - self.encrypted_key[delta]
      letter = chr(crypted_letter)
      login += letter
      position += 1
    return login

class ILoginEncryptionPlugin(Interface):
  """Contract for possible ERP5 Key Auth Plugin"""

  def encrypt(self, login):
    """Encrypt the login"""

  def decrypt(self, crypted_login):
    """Decrypt string and return the login"""


#Form for new plugin in ZMI
manage_addERP5KeyAuthPluginForm = PageTemplateFile(
    'www/ERP5Security_addERP5KeyAuthPlugin', globals(),
    __name__='manage_addERP5KeyAuthPluginForm')

def addERP5KeyAuthPlugin(dispatcher, id, title=None,
                         encryption_key='', cipher='AES', cookie_name='',
                         default_cookie_name='',REQUEST=None):
  """ Add a ERP5KeyAuthPlugin to a Pluggable Auth Service. """

  plugin = ERP5KeyAuthPlugin(id=id, title=title, encryption_key=encryption_key,
                             cipher=cipher, cookie_name=cookie_name,
                             default_cookie_name=default_cookie_name)
  dispatcher._setObject(plugin.getId(), plugin)

  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect(
      '%s/manage_workspace'
      '?manage_tabs_message='
      'ERP5KeyAuthPlugin+added.'
      % dispatcher.absolute_url())

class ERP5KeyAuthPlugin(ERP5UserManager, CookieAuthHelper):
  """
    Key authentication PAS plugin which support key authentication in URL.

    <ERP5_Root>/web_page_module/1?__ac_key=207221200213146153166

    where value of __ac_key contains an encrypted reference of a user

  TODO: We should use a real PKI (Public Key Infrastructure) so that we
  can revoke a part of already provided keys without changing the
  encryption key or a user's reference.
  """

  meta_type = "ERP5 Key Authentication"
  login_path = 'login_form'
  security = ClassSecurityInfo()
  cookie_name = "__ac_key"
  default_cookie_name = "__ac"
  encryption_key = ''

  manage_options = ( ( { 'label': 'Edit',
                          'action': 'manage_editERP5KeyAuthPluginForm', }
                        ,
                      )
                      + BasePlugin.manage_options[:]
                      #+ CookieAuthHelper.manage_options[:] //don't need folder option today
                    )

  _properties = ( ( { 'id':'default_cookie_name',
                      'type':'string',
                      'mode':'w',
                      'label':'Default Cookie Name'
                    },
                    )
                    + BasePlugin._properties[:]
                    + CookieAuthHelper._properties[:]
                  )

  def __init__(self, id, title=None, encryption_key='', cipher='AES',
               cookie_name='', default_cookie_name=''):
    #Check parameters
    if cookie_name is None or cookie_name == '':
      cookie_name = id
    if encryption_key is None or encryption_key == '':
      encryption_key = id
    if "__ac_key" in [cookie_name, default_cookie_name]:
      raise ValueError("Cookie name must be different of __ac_key")

    #Register value
    self._setId(id)
    self.title = title
    self.cookie_name = cookie_name
    self.default_cookie_name = default_cookie_name
    self.encryption_key = encryption_key
    self.cipher = cipher

  def _getCipher(self):
    # If self.cipher does not exist, we use CesarCipher only for
    # backward compatibility.
    return getattr(self, 'cipher', 'Cesar')

  ################################
  #    ILoginEncryptionPlugin    #
  ################################
  security.declarePublic('encrypt')
  def encrypt(self, login):
    """Encrypt the login"""
    cipher = globals()['%sCipher' % self._getCipher()](self.encryption_key)
    return bytes2str(cipher.encrypt(login))

  security.declarePrivate('decrypt')
  def decrypt(self, crypted_login):
    """Decrypt string and return the login"""
    cipher = globals()['%sCipher' % self._getCipher()](self.encryption_key)
    return bytes2str(cipher.decrypt(crypted_login))

  ####################################
  #ILoginPasswordHostExtractionPlugin#
  ####################################
  security.declarePrivate('extractCredentials')
  def extractCredentials(self, request):
    """ Extract credentials from cookie or 'request'. """
    try:
      creds = {}
      #Search __ac_key
      key = request.get('__ac_key', None)
      if key is not None:
        creds['key'] = key
        #Save this in cookie
        self.updateCredentials(request, request["RESPONSE"], None, None)
      else:
        # Look in the request for the names coming from the login form
        #It's default method
        login_pw = request._authUserPW()

        if login_pw is not None:
          name, password = login_pw
          creds[ 'login' ] = name
          creds[ 'password' ] = password
          #Save this in cookie
          self.updateCredentials(request, request["RESPONSE"], name, password)

        else:
          #search in cookies
          cookie = request.get(self.cookie_name, None)
          if cookie is not None:
            #Cookie is found
            cookie_val = unquote(cookie)
            creds['key'] = cookie_val
          else:
            #Default cookie if needed
            default_cookie = request.get(self.default_cookie_name, None)
            if default_cookie is not None:
              #Cookie is found
              cookie_val = decodestring(unquote(default_cookie))
              if cookie_val is not None:
                login, password = cookie_val.split(':')
                creds['login'] = login
                creds['password'] = password

      #Complete credential with some information
      if creds:
        creds['remote_host'] = request.get('REMOTE_HOST', '')
        try:
          creds['remote_address'] = request.getClientAddr()
        except AttributeError:
          creds['remote_address'] = request.get('REMOTE_ADDR', '')
    except Exception as e:
      #Log standard error to check error
      LOG('ERP5KeyAuthPlugin.extractCredentials', PROBLEM, str(e))

    return creds

  ################################
  #   ICredentialsUpdatePlugin   #
  ################################
  security.declarePrivate('updateCredentials')
  def updateCredentials(self, request, response, login, new_password):
    """ Respond to change of credentials"""

    #Update credential for key auth or standard of.
    #Remove conflict between both systems
    cookie_val = request.get("__ac_key", None)
    if cookie_val is not None:
      #expires = (DateTime() + 365).toZone('GMT').rfc822()
      cookie_val = cookie_val.rstrip()
      response.setCookie(self.cookie_name, quote(cookie_val), path='/')#, expires=expires)
      response.expireCookie(self.default_cookie_name, path='/')
    elif login is not None and new_password is not None:
      cookie_val = encodestring('%s:%s' % (login, new_password))
      cookie_val = cookie_val.rstrip()
      response.setCookie(self.default_cookie_name, quote(cookie_val), path='/')
      response.expireCookie(self.cookie_name, path='/')


  ################################
  #    ICredentialsResetPlugin   #
  ################################
  security.declarePrivate('resetCredentials')
  def resetCredentials(self, request, response):
    """Expire cookies of authentication """
    response.expireCookie(self.cookie_name, path='/')
    response.expireCookie(self.default_cookie_name, path='/')


  ################################
  #     IAuthenticationPlugin    #
  ################################
  security.declarePrivate('authenticateCredentials')
  def authenticateCredentials( self, credentials ):
    """Authenticate with credentials"""
    key = credentials.get('key', None)
    if key != None:
      login = self.decrypt(key)
      # Forbidden the usage of the super user.
      if login == ERP5Security.SUPER_USER:
        return None

      #Function to allow cache
      @UnrestrictedMethod
      def _authenticateCredentials(login):
        if not login:
          return None

        #Search the user by his login
        user = self.getUser(login)
        if user is None:
          raise _AuthenticationFailure()
        user_value = user.getUserValue()

        if True:
          try:
            # get assignment list
            assignment_list = [x for x in user_value.contentValues(portal_type="Assignment") \
                                 if x.getValidationState() == "open"]
            valid_assignment_list = []
            # check dates if exist
            login_date = DateTime()
            for assignment in assignment_list:
              if assignment.getStartDate() is not None and \
                        assignment.getStartDate() > login_date:
                continue
              if assignment.hasStopDate() and \
                  assignment.getStopDate() < login_date:
                continue
              valid_assignment_list.append(assignment)

            # validate
            if len(valid_assignment_list) > 0:
              return (user.getId(), user.getUserName())
          finally:
            pass

          raise _AuthenticationFailure()

      #Cache Method for best performance
      _authenticateCredentials = CachingMethod(_authenticateCredentials,
                                                id='ERP5KeyAuthPlugin_authenticateCredentials',
                                                cache_factory='erp5_content_short')
      try:
        return _authenticateCredentials(login=login)
      except _AuthenticationFailure:
        return None
      except Exception as e:
        #Log standard error
        LOG('ERP5KeyAuthPlugin.authenticateCredentials', PROBLEM, str(e))
        return None

  #################################
  # Properties for ZMI management #
  #################################

  #'Edit' option form
  manage_editERP5KeyAuthPluginForm = PageTemplateFile(
      'www/ERP5Security_editERP5KeyAuthPlugin',
      globals(),
      __name__='manage_editERP5KeyAuthPluginForm' )

  security.declareProtected( ManageUsers, 'manage_editKeyAuthPlugin' )
  def manage_editKeyAuthPlugin(self, encryption_key, cipher, cookie_name,
                               default_cookie_name, RESPONSE=None):
    """Edit the object"""
    error_message = ''

    #Test parameters
    if "__ac_key" in [cookie_name, default_cookie_name]:
      raise ValueError("Cookie name must be different of __ac_key")

    #Save key
    if encryption_key == '' or encryption_key is None:
      error_message += 'Invalid key value '
    else:
      self.encryption_key = encryption_key

    #Save cipher
    if cipher == '' or cipher is None:
      error_message += 'Invalid cipher value '
    else:
      self.cipher = cipher

    #Save cookie name
    if cookie_name == '' or cookie_name is None:
      error_message += 'Invalid cookie name '
    else:
      self.cookie_name = cookie_name

    #Save default_cookie_name
    if default_cookie_name == '' or default_cookie_name is None:
      error_message += 'Invalid default cookie name '
    else:
      self.default_cookie_name = default_cookie_name

    #Redirect
    if RESPONSE is not None:
      if error_message != '':
        self.REQUEST.form['manage_tabs_message'] = error_message
        return self.manage_editERP5KeyAuthPluginForm(RESPONSE)
      else:
        message = "Updated"
        RESPONSE.redirect( '%s/manage_editERP5KeyAuthPluginForm'
                            '?manage_tabs_message=%s'
                            % ( self.absolute_url(), message )
                          )

#List implementation of class
classImplements(ERP5KeyAuthPlugin,
                ILoginEncryptionPlugin,
                plugins.IAuthenticationPlugin,
                plugins.ILoginPasswordHostExtractionPlugin,
                plugins.ICredentialsResetPlugin,
                plugins.ICredentialsUpdatePlugin)

InitializeClass(ERP5KeyAuthPlugin)
