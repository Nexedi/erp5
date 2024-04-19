##############################################################################
#
# Copyright (c) 2020 Nexedi SARL and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################
import base64
import json
import jwt
import os
import re
import time
import zlib
import ipaddress
import six
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import (
  IExtractionPlugin,
  IAuthenticationPlugin,
  IPropertiesPlugin,
  IGroupsPlugin,
  IRolesPlugin,
  ICredentialsResetPlugin,
)
from Products.ERP5Security import _setUserNameForAccessLog
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Utils import bytes2str, str2bytes, str2unicode, unicode2str

# Public constants. Must not change once deployed.

# Keys used in serialised cookie and Authorization header.
# Use short keys, as these have a limited length.
# Top-level keys, share the same namespace as JWT claims. Avoid 3-letter
# values.
JWT_CLAIM_NETWORK_LIST_KEY = 'n'
JWT_PAYLOAD_KEY = 'p'
# Payload-level keys, in our own namespace.
JWT_PAYLOAD_AUTHORISATION_SESSION_ID_KEY = 's'
JWT_PAYLOAD_AUTHORISATION_SESSION_VERSION_KEY = 'v'
JWT_PAYLOAD_GROUP_LIST_KEY = 'g'
JWT_PAYLOAD_ROLE_LIST_KEY = 'r'
JWT_PAYLOAD_USER_ID_KEY = 'u'
JWT_PAYLOAD_CLIENT_REFERENCE_KEY = 'R'
JWT_PAYLOAD_USER_CAPTION_KEY = 'C'
JWT_PAYLOAD_SCOPE_LIST_KEY = 'S'
# Keys used in request private dict (see __getRequestPrivateDict).
_PRIVATE_USER_PROPERTY_DICT_KEY = 'property_dict'
_PRIVATE_TOKEN_KEY = 'token'
_PRIVATE_EXTRACTED_KEY = 'extracted'
_PRIVATE_GROUP_LIST_KEY = 'group_list'
_PRIVATE_ROLE_LIST_KEY = 'role_list'
_PRIVATE_CLIENT_ID = 'client_id'
# These names are used as user properties.
USER_PROPERTY_TYPE_KEY = 'type'
USER_PROPERTY_TYPE_VALUE = 'erp5_oauth2'
USER_PROPERTY_EXPIRATION_TIMESTAMP_KEY = 'expiration_timestamp'
USER_PROPERTY_CLIENT_ID_KEY = 'client_id'
USER_PROPERTY_CLIENT_REFERENCE_KEY = 'client_reference'
USER_PROPERTY_SCOPE_LIST_KEY = 'scope_list'

_INTERFACE_CLASS_LIST = (
  IExtractionPlugin,
  IAuthenticationPlugin,
  IPropertiesPlugin,
  IGroupsPlugin,
  IRolesPlugin,
  ICredentialsResetPlugin,
)

class OAuth2AuthorisationClientConnectorMixIn(object):
  """
  Empty mix-in class used for type-checking when looking for the proper
  connector to use.
  """
  pass

def isAddressInNetworkList(address, network_list):
  address = ipaddress.ip_address(address)
  return any(
    address in ipaddress.ip_network(network)
    for network in network_list
  )

def encodeAccessTokenPayload(payload):
  """
  Encode given json-safe value into a format suitable for
  decodeAccessTokenPayload.
  """
  return bytes2str(base64.urlsafe_b64encode(
    zlib.compress(
      str2bytes(json.dumps(payload)),
    ),
  ))

def decodeAccessTokenPayload(encoded_payload):
  """
  From a decoded access token, extract and further decode the payload.
  """
  return json.loads(
    zlib.decompress(
      base64.urlsafe_b64decode(
        encoded_payload,
      ),
    ),
  )

# Internal constants. May change anytime.

# Arbitrary value so the IAuthenticationPlugin personality of this plugin can
# access the values extracted by its IExtractionPlugin personality.
# Value structure may change anytime, do not use in any other plugin.
_ERP5_OAUTH2_ACCESS_TOKEN_NAME = 'ERP5OAuth2AccessToken'

# See ZPublisher/HTTPRequest.py
_COOKIE_PADDING = '[\x00- ]*'
_MATCH_COOKIE = re.compile(
  '(' # catch whole cookie record
    + _COOKIE_PADDING +
    '([^\x00- ;,="]+)' # Cookie name
    '(?:' # Match value, do not put in a group
      '="[^"]*"(?:' + _COOKIE_PADDING + '[;,])?|' # well-formed
      '=[^;]*(?:' + _COOKIE_PADDING + '[;,])?|' # non-quoted (MSIE)
      + _COOKIE_PADDING + '[;,]' # Value-less
    ')'
    + _COOKIE_PADDING +
  ')'
).match

manage_addERP5OAuth2ResourceServerPluginForm = PageTemplateFile(
  'www/ERP5Security_addERP5OAuth2ResourceServerPlugin',
  globals(),
  __name__='manage_addERP5OAuth2ResourceServerPluginForm',
)
def addERP5OAuth2ResourceServerPlugin(
  dispatcher,
  id,
  access_cookie_name='__Host-at',
  refresh_cookie_name='__Host-rt',
  title=None,
  RESPONSE=None,
):
  """ Add a ERP5OAuth2ResourceServerPlugin to a Pluggable Auth Service. """
  dispatcher._setObject(
    id,
    ERP5OAuth2ResourceServerPlugin(
      id=id,
      access_cookie_name=access_cookie_name,
      refresh_cookie_name=refresh_cookie_name,
      title=title,
    ),
  )
  activatePlugin = dispatcher.plugins.activatePlugin
  for interface in _INTERFACE_CLASS_LIST:
    activatePlugin(interface, id)
  if RESPONSE is not None:
    RESPONSE.redirect(dispatcher._getOb(id).absolute_url() + '/manage_main')

class ERP5OAuth2ResourceServerPlugin(BasePlugin):
  meta_type = 'ERP5 OAuth2 Resource Server Plugin'
  _properties = (
    {
      'id': 'access_cookie_name',
      'type': 'string',
      'mode': 'w',
      'label': 'Name of the Access Token cookie',
    },
    {
      'id': 'refresh_cookie_name',
      'type': 'string',
      'mode': 'w',
      'label': 'Name of the Refresh Token cookie',
    },
    {
      'id': 'enable_cookie_creation',
      'type': 'boolean',
      'mode': 'w',
      'label': 'Enable cookie creation',
    },
  )

  security = ClassSecurityInfo()

  def __init__(
    self,
    id,
    access_cookie_name='__Host-at',
    refresh_cookie_name='__Host-rt',
    title=None,
  ):
    self.id = id
    self.title = title
    self.access_cookie_name = access_cookie_name
    self.refresh_cookie_name = refresh_cookie_name
    self.enable_cookie_creation = True
    self.__access_token_key_list = ()

  #
  #   Methods not in PAS plugin API
  #

  security.declarePrivate('setCookie')
  def setCookie(
    self,
    request,
    response,
    access_token,
    refresh_token=None,
    cookie_attribute_dict=(),
    refresh_cookie_attribute_dict=None,
  ):
    """
    Tell client to store given access token.

    request (HTTPRequest)
      Request being processed, for environment inspection.
    response (HTTPResponse)
      Response used to communicate with client.
    access_token (bytes)
      Token content.
    cookie_attribute_dict (dict)
      Attributes to set on the cookie.
      Reserved keys (providing them raises a TypeError):
      - "Secure": always true, as per OAuth2 standard
    refresh_cookie_attribute_dict (dict, None)
      If None, defaults to cookie_attribute_dict.
      Otherwise, specifies the cookie attributes for the refresh token, and
      the same rules as cookie_attribute_dict apply.

    If enable_cookie_creation is False, does nothing silently (used when
    migrating away from a PAS plugin and into another one).

    Refresh known Access Token public keys if necessary.
    Raises if the given value does not match any known key.

    Returns whether the cookie was set.
    """
    if not self.enable_cookie_creation:
      return False
    if (
      self.__checkTokenSignature(access_token) is None and
      self.__updateAccessTokenSignatureKeyList(request=request) and
      self.__checkTokenSignature(access_token) is None
    ):
      raise ValueError
    cookie_attribute_dict = {
      x.lower(): y
      for x, y in six.iteritems(dict(cookie_attribute_dict))
    }
    # Note: Calling expireCookie and then setCookie does not overwrites cookie
    # attributes set by expireCookie. So remove any pending cookie with this
    # name.
    response.cookies.pop(self.access_cookie_name, None)
    response.setCookie(
      name=self.access_cookie_name,
      value=access_token,
      secure=True, # OAuth2 requires TLS
      **cookie_attribute_dict
    )
    if refresh_token and self.refresh_cookie_name:
      response.cookies.pop(self.refresh_cookie_name, None)
      response.setCookie(
        name=self.refresh_cookie_name,
        value=refresh_token,
        secure=True, # OAuth2 requires TLS
        **(
          cookie_attribute_dict
          if refresh_cookie_attribute_dict is None else
          {
            x.lower(): y
            for x, y in six.iteritems(dict(refresh_cookie_attribute_dict))
          }
        )
      )
    return True

  #
  #   Some private methods used for PAS API.
  #
  def __expireCookie(self, response):
    """
    Tell client to get rid of its cookies, as they are now unusable.
    """
    # expireCookie does not set cookies attributes which may be required for
    # browser to actually apply the change. So emulate expireCookie using
    # setCookie.
    kw = {
      'value': 'deleted',
      'secure': True,
      'path': '/',
      'max_age': 0,
      'expires': 'Wed, 31-Dec-97 23:59:59 GMT',
    }
    response.setCookie(name=self.access_cookie_name, **kw)
    if self.refresh_cookie_name:
      response.setCookie(name=self.refresh_cookie_name, **kw)

  def __getRequestPrivateDict(self, request):
    """
    Return a mutable dict on a request, specific to this PAS plugin, to
    carry values from extracted token to the PAS plugin methods which use
    them.
    """
    # Note: using __ magic to insert this class' name in the attribute set on
    # request, to ease debugging.
    if request is None:
      return {}
    try:
      typed_container = request.__private
    except AttributeError:
      typed_container = request.__private = {}
    key = self.getPhysicalPath()
    try:
      return typed_container[key]
    except KeyError:
      typed_container[key] = result = {}
      return result

  def __iterClientConnectorValue(self, client_id=None):
    for web_service_value in self.portal_web_services.objectValues():
      if (
        isinstance(web_service_value, OAuth2AuthorisationClientConnectorMixIn) and
        web_service_value.getValidationState() == 'validated' and (
          client_id is None or
          client_id == web_service_value.getReference()
        )
      ):
        yield web_service_value

  def __getWebServiceValue(self, client_id=None, raw_token=None):
    if client_id is None:
      # Peek into token (without checking its signature) to guess the client_id
      # to look for.
      client_id = unicode2str(jwt.decode(
        raw_token,
        # no key.
        # any algorithm is fine.
        options={
          'verify_signature': False,
          'verify_exp': False,
        },
      )['iss'])
    assert client_id is not None
    web_service_value_list = list(self.__iterClientConnectorValue(
      client_id=client_id,
    ))
    if web_service_value_list:
      web_service_value, = web_service_value_list
      return web_service_value

  def __updateAccessTokenSignatureKeyList(self, request):
    """
    Retrieve current public keys used to check token signature, and update our list
    if there is any change.
    Returns a true value if the list was actually updated, a false value otherwise.
    """
    new_access_token_key_set = set()
    for connector_value in self.__iterClientConnectorValue():
      new_access_token_key_set.update(
        connector_value.getAccessTokenSignatureAlgorithmAndPublicKeyList(
          REQUEST=request,
        ),
      )
    if new_access_token_key_set.symmetric_difference(self.__access_token_key_list):
      self.__access_token_key_list = tuple(new_access_token_key_set)
      return True

  def __checkTokenSignature(self, raw_token):
    """
    Check if given token matches any of the known keys and algorithms, and
    return its content.

    Does NOT update known keys and algorithms from Authorisation Server.
    Does NOT apply any non-standard check.
    Does NOT check if the associated session is still valid.
    """
    for signature_algorithm, key in self.__access_token_key_list:
      try:
        return jwt.decode(
          raw_token,
          key=key,
          algorithms=[signature_algorithm],
          options={
            'require_exp': True,
            'verify_exp': True,
            'verify_signature': True,
          },
        )
      except jwt.InvalidTokenError:
        continue

  def __decodeToken(
    self,
    access_token,
    refresh_token,
    request,
    can_update_key,
  ):
    """
    Validate and decode provided raw token.
    Return a dictionary of private token properties for use by further
    authentication plugin personalities of this plugin.
    The schema of this dictionary is purely an internal implementation detail
    of this plugin.
    """
    client_address = str2unicode(request.getClientAddr())
    token = self.__checkTokenSignature(access_token)
    if token is None and can_update_key:
      self.__updateAccessTokenSignatureKeyList(request=request)
      token = self.__checkTokenSignature(access_token)
    if token is None:
      return
    # Non-standard claims
    if not isAddressInNetworkList(
        address=client_address,
        network_list=token[JWT_CLAIM_NETWORK_LIST_KEY],
    ):
      return
    # JWT is known valid. Access its content.
    token_payload = decodeAccessTokenPayload(
      bytes2str(token[JWT_PAYLOAD_KEY].encode('ascii')),
    )
    client_id = unicode2str(token['iss'])
    if self.__getWebServiceValue(
      client_id=client_id,
    ).getSessionVersion(
      REQUEST=request,
      session_id=token_payload[JWT_PAYLOAD_AUTHORISATION_SESSION_ID_KEY],
    ) != token_payload[JWT_PAYLOAD_AUTHORISATION_SESSION_VERSION_KEY]:
      return
    return {
      _PRIVATE_EXTRACTED_KEY: (
        unicode2str(token_payload[JWT_PAYLOAD_USER_ID_KEY]),
        unicode2str(token_payload[JWT_PAYLOAD_USER_CAPTION_KEY]),
      ),
      _PRIVATE_TOKEN_KEY: (access_token, refresh_token),
      _PRIVATE_CLIENT_ID: client_id,
      _PRIVATE_USER_PROPERTY_DICT_KEY: {
        USER_PROPERTY_TYPE_KEY: USER_PROPERTY_TYPE_VALUE,
        USER_PROPERTY_EXPIRATION_TIMESTAMP_KEY: token['exp'],
        USER_PROPERTY_CLIENT_ID_KEY: client_id,
        USER_PROPERTY_SCOPE_LIST_KEY: token_payload[JWT_PAYLOAD_SCOPE_LIST_KEY],
        USER_PROPERTY_CLIENT_REFERENCE_KEY: token_payload[
          JWT_PAYLOAD_CLIENT_REFERENCE_KEY
        ] or '',
      },
      _PRIVATE_GROUP_LIST_KEY: tuple(
        unicode2str(x) for x in token_payload[JWT_PAYLOAD_GROUP_LIST_KEY]
      ),
      _PRIVATE_ROLE_LIST_KEY: tuple(
        unicode2str(x) for x in token_payload[JWT_PAYLOAD_ROLE_LIST_KEY]
      ),
    }

  def __extractAuthorisation(self, request):
    """
    Retrieve token from request Authorisation header.

    If present, and scheme is "Bearer", and the token signature passes our
    validation, remove it from request.
    """
    http_authorisation = request._auth
    if not http_authorisation:
      return
    try:
      (
        authorisation_scheme,
        authorisation_value,
      ) = http_authorisation.split(' ', 1)
    except ValueError:
      return
    if authorisation_scheme != 'Bearer':
      return
    result = self.__decodeToken(
      access_token=authorisation_value,
      refresh_token=None,
      request=request,
      # Allow updating keys, as Authorization header does not require going
      # through us upon issuance, so there was no chance for us to detect any
      # possible new signature key.
      can_update_key=True,
    )
    if result is not None:
      # This token belongs to us, wipe it from request.
      request._auth = None
      # XXX: also remove from Medusa's request ?
    return result

  def __extractCookie(self, request):
    """
    Retrieve token value from request cookies.

    If present, remove it (admin is supposed to have given us a unique cookie
    name, so we take full control of any cookie with that name), both from
    request.cookies and from environ['HTTP_COOKIE'].
    If the token cannot be used, tell client to drop it.
    """
    name_to_strip_set = [
      self.access_cookie_name,
    ]
    raw_token = request.cookies.pop(self.access_cookie_name, None)
    if self.refresh_cookie_name:
      name_to_strip_set.append(self.refresh_cookie_name)
      raw_refresh_token = request.cookies.pop(self.refresh_cookie_name, None)
    found_in_request = bool(raw_token or raw_refresh_token)
    # Remove also from HTTP_COOKIE.
    environ = request.environ
    http_cookie = environ.get('HTTP_COOKIE')
    if http_cookie:
      new_http_cookie = []
      new_http_cookie_append = new_http_cookie.append
      position = 0
      while True:
        matched = _MATCH_COOKIE(http_cookie, position)
        if matched is None:
          break
        matched_string = matched.group(1)
        if matched.group(2) not in name_to_strip_set:
          new_http_cookie_append(matched_string)
        position += len(matched_string)
      environ['HTTP_COOKIE'] = ''.join(new_http_cookie)
    if raw_token:
      result = self.__decodeToken(
        access_token=raw_token,
        refresh_token=raw_refresh_token,
        request=request,
        # Do not try to update: if a cookie was issued, it should have gone
        # through us, at which point we had the opportunity of updating our key
        # list. And if this PAS plugin was re-created, then this will
        # self-stabilise: client will get an Unauthorized response, prompting
        # them to log in, likely using a cookie, which then will trigger the
        # key update.
        can_update_key=False,
      )
    else:
      result = None
    if result is None and raw_refresh_token:
      # This is not a valid access token. and a refresh token is provided.
      # Maybe it can be renewed ?
      raw_token, raw_refresh_token = self.__getWebServiceValue(
        raw_token=raw_refresh_token,
      ).getNewAccessToken(
        request=request,
        refresh_token=raw_refresh_token,
      )
      if raw_token is not None:
        # renewal happened, decode
        result = self.__decodeToken(
          raw_token,
          raw_refresh_token,
          request,
          # Again, do not try to update: if the token was renewedm a cookie was
          # just issued and we just had the opportunity of refreshing the
          # public keys.
          can_update_key=False,
        )
    if found_in_request and result is None:
      # Cookie is present but cannot be used. Tell client to drop it.
      self.__expireCookie(request.RESPONSE)
    return result

  #
  #   IExtractionPlugin implementation
  #
  security.declarePrivate('extractCredentials')
  def extractCredentials(self, request):
    """
    Extract Access Token from request.

    First, look into Authorization header for a Bearer token.
    Then, look into configured cookie.
    First token found wins, others are ignored for authentication purposes.
    All recognised tokens are removed from the request, to reduce the risks of
    leaks (ex: via repr(request) ), even if they are otherwise ignored for
    authentication purposes.
    An Authorization header token is recognised if its signature can be
    validated.
    A cookie token is recognised if it is present.
    """
    # XXX: This plugging is wiping tokens from the request, which is fine as
    # long as authentication happens only once. Which of course is violated
    # in BaseExtensibleTraversableMixin.
    request_private_dict = self.__getRequestPrivateDict(request)
    if not request_private_dict:
      for private_dict in (
        # Note: it is a feature to do all calls even if the loop exits early !
        self.__extractAuthorisation(request),
        self.__extractCookie(request),
      ):
        if private_dict is not None:
          # This token's signature could be verified, use its properties and stop
          # the search. Even if this token cannot be used (ex: because of a wrong
          # version).
          request_private_dict.update(private_dict)
          break
    if not request_private_dict:
      return
    login, caption = request_private_dict[_PRIVATE_EXTRACTED_KEY]
    _setUserNameForAccessLog(login, request)
    return {
      _ERP5_OAUTH2_ACCESS_TOKEN_NAME: (login, caption),
    }

  #
  #   IAuthenticationPlugin implementation
  #
  security.declarePrivate('authenticateCredentials')
  def authenticateCredentials(self, credentials):
    try:
      return credentials[_ERP5_OAUTH2_ACCESS_TOKEN_NAME]
    except KeyError:
      pass

  #
  #   IPropertiesPlugin implementation
  #
  security.declarePrivate('getPropertiesForUser')
  def getPropertiesForUser(self, user, request=None):
    try:
      return self.__getRequestPrivateDict(request)[
        _PRIVATE_USER_PROPERTY_DICT_KEY
      ]
    except KeyError:
      return {}

  #
  #   IGroupsPlugin implementation
  #
  security.declarePrivate('getGroupsForPrincipal')
  def getGroupsForPrincipal(self, principal, request=None):
    try:
      return self.__getRequestPrivateDict(request)[_PRIVATE_GROUP_LIST_KEY]
    except KeyError:
      return []

  #
  #   IRolesPlugin implementation
  #
  security.declarePrivate('getRolesForPrincipal')
  def getRolesForPrincipal(self, principal, request=None):
    try:
      return self.__getRequestPrivateDict(request)[_PRIVATE_ROLE_LIST_KEY]
    except KeyError:
      return []

  #
  #   ICredentialsResetPlugin implementation
  #
  security.declarePrivate('resetCredentials')
  def resetCredentials(self, request, response):
    request_private_dict = self.__getRequestPrivateDict(request)
    try:
      access_token, refresh_token = request_private_dict[
        _PRIVATE_TOKEN_KEY
      ]
    except KeyError:
      return
    for web_service_value in self.__iterClientConnectorValue(
      client_id=request_private_dict[_PRIVATE_CLIENT_ID]
    ):
      web_service_value.terminateSession(
        request=request,
        access_token=access_token,
        refresh_token=refresh_token,
      )
    self.__expireCookie(response)

classImplements(
  ERP5OAuth2ResourceServerPlugin,
  *_INTERFACE_CLASS_LIST
)
InitializeClass(ERP5OAuth2ResourceServerPlugin)
