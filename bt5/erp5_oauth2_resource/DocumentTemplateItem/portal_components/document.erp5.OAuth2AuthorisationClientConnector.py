##############################################################################
#
# Copyright (c) 2020 Nexedi SA and Contributors. All Rights Reserved.
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

import base64
from collections import defaultdict
import email.utils
import functools
import hashlib
import hmac
from six.moves.http_client import HTTPConnection, HTTPSConnection
import json
from os import urandom
import random
from time import time
from six.moves.urllib.parse import urlencode, urljoin, urlparse
import ssl
from AccessControl import (
  ClassSecurityInfo,
  getSecurityManager,
)
from cryptography import fernet
import jwt
from oauthlib.oauth2 import OAuth2Error
import oauthlib.oauth2.rfc6749.errors as oauthlib_errors
import six
from OFS.Traversable import NotFound
from Products.ERP5Type import Permissions
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Timeout import getTimeLeft
from Products.ERP5Security.ERP5OAuth2ResourceServerPlugin import (
  OAuth2AuthorisationClientConnectorMixIn,
  ERP5OAuth2ResourceServerPlugin,
)
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from zLOG import LOG, INFO, WARNING

# How long to wait for a remote Authorisation Server to respond.
_TIMEOUT = 1
# Name of the cookie used to prevent Cross-Site request forgery.
# Prevent (on browsers which support it) this cookie from being set by
# javascript.
_ANTI_CSRF_COOKIE_NAME_BASE = '__Host-login-state-'
_STATE_IDENTIFIER_NAME = 'i'
_STATE_CAME_FROM_NAME = 'c'
_STATE_CODE_VERIFIER_NAME = 'v'

# Unit tests may need to run on plain http, or on https with an unknown CA.
# Normally, resource-server-to-authorisation-server comunications strictly
# require https with a known CA, which would make such tests fail.
# Allow tests to downgrade security by requiring them to jump through hoops,
# so that it would be very difficult to do this on an actual instance:
# - require a boolean property to be set (is_insecure), property which is
#   only visible in the UI if already set, so that users are not tempted to
#   set it when not set, and are still informed and able to unset it when set.
# - require the request to the resource server which would trigger such
#   access to have a magic value as environ['SERVER_SOFTWARE']: unit tests
#   can control this value per-request, which in normal use this is set by
#   Zope (medusa/waitress).
#   And make this value change on every module reload, to make accidental
#   activation as unlikely as desired.
INSECURE_REQUEST_ENVIRON_SERVER_SOFTWARE = 'insecure_oauth2_%016x' % (
  random.randrange(2**64),
)

_OAUTHLIB_EXCEPTION_DICT = {
  (error_klass.status_code, error_klass.error): error_klass
  for error_klass in six.itervalues(oauthlib_errors.__dict__)
  if (
    isinstance(error_klass, type) and
    issubclass(error_klass, OAuth2Error) and
    error_klass.__dict__.get('error') is not None
  )
}

# Minimal implementations for use as REQUEST and RESPONSE arguments to call
# methods wrapped by
# document.erp5.OAuth2AuthorisationServerConnector.wrapOAuth2Endpoint .

class _SimpleHTTPResponse(object):
  def __init__(self):
    self.status = 200
    self.header_dict = defaultdict(list)
    self.body = ''

  def setStatus(self, code, lock=None):
    assert not self.body
    self.status = code

  def setHeader(self, name, value):
    # lock: ignored, nothing other than OAuth2AuthorisationServerConnector
    # should touch such instance, and it should be careful enough not to
    # contradict itself.
    # Sanity check for medusa-type usage (headers are sent once body had
    # been written to, so further setHeader calls are without effect).
    assert not self.body
    self.header_dict[name.replace('-', '_').upper()] = [value]

  def addHeader(self, name, value):
    assert not self.body
    self.header_dict[name.replace('-', '_').upper()].append(value)

  def setBody(self, body, lock=None):
    # lock: ignored, nothing other than OAuth2AuthorisationServerConnector
    # should touch such instance, and it should be careful enough not to
    # contradict itself.
    self.write(body)

  def write(self, body):
    assert not self.body
    self.body = body

  def __repr__(self):
    return '<%s status=%r, header_dict=%r, body=%r>' % (
      self.__class__.__name__,
      self.status,
      self.header_dict,
      self.body,
    )

class _SimpleHTTPRequest(object):
  def __init__(self, url, client_address, environ=(), form=()):
    self.environ = environ = dict(environ)
    # OAuth2 uses stereotypical requests, so hardcode these values.
    environ['REQUEST_METHOD'] = 'POST'
    environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
    self._auth = environ.pop('AUTHORIZATION', '')
    self._client_address = client_address
    self.form = dict(form)
    self.other = {
      'URL': url,
    }

  def _authUserPW(self):
    if self._auth.lower().startswith('basic '):
      return base64.decodestring(
        self._auth.split(None, 1)[1],
      ).split(':', 1)

  def get(self, name):
    if name == 'BODY':
      return None
    raise ValueError

  def getHeader(self, name):
    return self.environ.get(name)

  def getClientAddr(self):
    return self._client_address

class _OAuth2AuthorisationServerProxy(object):
  """
  Access a remote Authorisation Server web service document as if it were
  local.
  Hence, public methods present on this class *must* follow the API of
  OAuth2AuthorisationServerConnector (after taing any wrapper into account).

  Only expose the subset of methods actually needed by
  OAuth2AuthorisationClientConnector, for simplicity.
  """

  def __init__(
    self,
    authorisation_server_url,
    timeout,
    bind_address,
    ca_certificate_pem,
    insecure,
  ):
    scheme = urlsplit(authorisation_server_url).scheme
    if scheme != 'https' and not insecure:
      raise ValueError('Only https access to Authorisation Server is allowed')
    self._scheme = scheme
    self._insecure = insecure
    self._authorisation_server_url = authorisation_server_url.rstrip('/')
    self._timeout = timeout
    self._bind_address = (bind_address, 0) if bind_address else None
    if ca_certificate_pem is not None:
      # On python2 cadata is expected as an unicode object only.
      ca_certificate_pem = ca_certificate_pem.decode('utf-8')
    self._ca_certificate_pem = ca_certificate_pem

  #
  #   Private helper methods for this proxy class.
  #

  def _query(self, method_id, body, header_dict=()):
    plain_url = self._authorisation_server_url + '/' + method_id
    parsed_url = urlparse(plain_url)
    if self._scheme == 'https':
      ssl_context = ssl.create_default_context(
        cadata=self._ca_certificate_pem,
      )
      if self._insecure:
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
      else:
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.check_hostname = True
      Connection = functools.partial(
        HTTPSConnection,
        context=ssl_context,
      )
    else:
      Connection = HTTPConnection
    timeout = getTimeLeft()
    if timeout is None or timeout > self._timeout:
      timeout = self._timeout
    http_connection = Connection(
      host=parsed_url.hostname,
      port=parsed_url.port,
      strict=True,
      timeout=timeout,
      source_address=self._bind_address,
    )
    http_connection.request(
      method='POST',
      url=plain_url,
      body=body,
      headers=dict(header_dict),
    )
    http_response = http_connection.getresponse()
    return (
      {
        name.lower(): value
        for name, value in http_response.getheaders()
      },
      http_response.read(),
      http_response.status,
    )

  def _queryERP5(self, method_id, kw=()):
    header_dict, body, status = self._query(
      method_id=method_id,
      body=urlencode(kw),
      header_dict={
        'Accept': 'application/json;charset=UTF-8',
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    )
    if not 200 <= status < 300:
      raise ValueError(status)
    content_type = header_dict['content-type']
    # encoding is optional in content type, but avoid a simple prefix match,
    # which could match unexpected content types.
    if content_type.split(';', 1)[0] != 'application/json':
      raise ValueError(repr(content_type))
    return json.loads(body)

  def _queryOAuth2(self, method, REQUEST, RESPONSE):
    header_dict, body, status = self._query(
      method,
      body=urlencode(REQUEST.form.items()),
      header_dict={
        'CONTENT_TYPE': REQUEST.environ['CONTENT_TYPE'],
      },
    )
    RESPONSE.setStatus(status)
    for key, value in six.iteritems(header_dict):
      RESPONSE.setHeader(key, value)
    if 200 <= status < 300:
      return body
    RESPONSE.write(body)
    if header_dict['content-type'].split(';', 1)[0] == 'application/json':
      exception_class = _OAUTHLIB_EXCEPTION_DICT.get(
        (
          status,
          json.loads(body).get('error'),
        ),
      )
      if exception_class is not None:
        raise exception_class
    raise ValueError

  #
  #   OAuth2AuthorisationServerConnector API.
  #
  def isRemote(self):
    return True

  def absolute_url(self):
    return self._authorisation_server_url

  def getSessionVersion(self, session_id):
    return self._queryERP5(
      'getSessionVersion',
      kw={'session_id': session_id},
    )

  def getAccessTokenSignatureAlgorithmAndPublicKeyList(self):
    return tuple(
      (signature_algorithm.encode('ascii'), public_key.encode('ascii'))
      for signature_algorithm, public_key in self._queryERP5(
        'getAccessTokenSignatureAlgorithmAndPublicKeyList',
      )
    )

  def token(self, REQUEST, RESPONSE):
    return self._queryOAuth2('token', REQUEST, RESPONSE)

  def revoke(self, REQUEST, RESPONSE):
    return self._queryOAuth2('revoke', REQUEST, RESPONSE)

class OAuth2AuthorisationClientConnector(
  XMLObject,
  OAuth2AuthorisationClientConnectorMixIn, # This is just an isinstance marker.
):
  meta_type = 'OAuth2 Authorisation Client Connector'
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  __state_fernet_key_list = ()

  #
  #   Internal helper methods
  #

  # Forbid keeping the login page opened for more than 14 days
  # (14 * 24 * 60 * 60), just to avoid having unbounded-validity values.
  # Used both for the login state cookie and the OAuth2 "state" parameter,
  # which are generated and checked together.
  _SESSION_STATE_VALIDITY = 1209600

  def __getStateFernetKeyList(self):
    result = self.__state_fernet_key_list
    if not result:
      self.renewStateSecret()
      result = self.__state_fernet_key_list
      assert result
    return result

  def __getMultiFernet(self):
    return fernet.MultiFernet([
      fernet.Fernet(key)
      for _, key in self.__getStateFernetKeyList()
    ])

  security.declarePublic('isAuthorisationServerRemote')
  def isAuthorisationServerRemote(self):
    """
    Whether the associated authorisation server is local or remote.
    """
    return '/' in self.getAuthorisationServerUrl('')

  def _getAuthorisationServerValue(self, REQUEST):
    """
    Return an object implementing the Authorisation Server API.
    It may be:
    - an ERP5 Document, if the Authorisation Server is local
    - a proxy object, if the Authorisation Server is remote
    """
    authorisation_server_url = self.getAuthorisationServerUrl()
    if '/' in authorisation_server_url:
      # Remote Authorisation Server
      return _OAuth2AuthorisationServerProxy(
        authorisation_server_url=urljoin(
          # In case authorisation_server_url contains slashes but is still
          # relative (to the scheme or to the netloc - path-relative is not
          # supported by urljoin)
          self._getNeutralContextValue().absolute_url(),
          authorisation_server_url,
        ),
        timeout=_TIMEOUT,
        bind_address=self.getBindAddress(),
        ca_certificate_pem=self.getCertificationAuthorityCertificate(),
        insecure=(
          self.isInsecure() and
          REQUEST.environ.get(
            'SERVER_SOFTWARE',
          ) == INSECURE_REQUEST_ENVIRON_SERVER_SOFTWARE
        ),
      )
    # Local Authorisation Server, authorisation_server_url is
    # its portal_web_service ID.
    return self.getParentValue()[authorisation_server_url]

  def _callOAuth2(
    self,
    request,
    method,
    authorisation=None,
    header_dict=(),
    data_dict=(),
  ):
    inner_response = _SimpleHTTPResponse()
    authorisation_server = self._getAuthorisationServerValue(REQUEST=request)
    environ = {
      'HTTP_' + key.upper(): value
      for key, value in six.iteritems(dict(header_dict))
    }
    environ['AUTHORIZATION'] = authorisation
    try:
      environ.setdefault('HTTP_USER_AGENT', request['HTTP_USER_AGENT'])
    except KeyError:
      pass
    try:
      body = getattr(authorisation_server, method)(
        REQUEST=_SimpleHTTPRequest(
          url=authorisation_server.absolute_url() + '/' + method,
          client_address=request.getClientAddr(),
          environ=environ,
          form=dict(data_dict),
        ),
        RESPONSE=inner_response,
      )
    except OAuth2Error:
      pass
    else:
      inner_response.write(body)
    return inner_response

  def _setCookieFromTokenResponse(
    self,
    request,
    response,
    inner_response,
    user=None,
  ):
    """
    user
      When not None, once the new tokens presence is confirmed and before
      storing them in cookies, log this user out, cleanly terminating any
      pre-existing session.
      Note: only affects PAS-controlled sessions (so not CookieCrumbler's
      __ac).
    """
    full_content_type, = inner_response.header_dict.get('CONTENT_TYPE', ('', ))
    content_type = full_content_type.split(';', 1)[0]
    if content_type != 'application/json':
      LOG(
        'OAuth2AuthorisationClientConnector',
        INFO,
        'Unhandled CONTENT_TYPE when renewing Access Token cookie: %r' % (
          inner_response,
        ),
      )
      return (None, None, 'bad server response')
    oauth2_response = json.loads(inner_response.body)
    error = oauth2_response.get('error')
    if error is not None:
      if error != 'invalid_grant':
        LOG(
          'OAuth2AuthorisationClientConnector',
          INFO,
          'OAuth2 error when renewing Access Token cookie: %r' % (
            oauth2_response,
          ),
        )
      return (None, None, error)
    assert inner_response.status == 200
    access_token = oauth2_response['access_token']
    refresh_token = oauth2_response.get('refresh_token')
    parsed_actual_url = urlparse(request.other.get('ACTUAL_URL'))
    same_site = self.ERP5Site_getAuthCookieSameSite(
      scheme=parsed_actual_url.scheme,
      hostname=parsed_actual_url.hostname,
      port=parsed_actual_url.port,
      path=parsed_actual_url.path,
      user_agent=request.getHeader('USER_AGENT'),
    )
    cookie_attribute_dict = {
      # 'secure' is implicitly True (https required by oauth2, flag forced by
      # PAS plugin)
      'http_only': True,
      'same_site': (
        same_site
        if same_site in ('None', 'Lax', 'Strict') else
        None
      ),
      'path': '/',
    }
    kw = {
      'request': request,
      'response': response,
      'access_token': access_token,
      'refresh_token': refresh_token,
      'cookie_attribute_dict': cookie_attribute_dict,
    }
    if refresh_token and self.isCookiePersistence():
      refresh_cookie_attribute_dict = cookie_attribute_dict.copy()
      # generalisation of the formation used in HTTPResponse.expireCookie,
      # checked to be rfc6265-compliant.
      refresh_cookie_attribute_dict['expires'] = email.utils.formatdate(
        jwt.decode(
          refresh_token,
          # Note: we cannot validate this token (signature is with
          # Authorisation Server's symetric - and hence private - key). But:
          # - this value comes straight from the Authorisation Server, so we
          #   have no reason to doubt its authenticity
          # - this is not used to grant access, just to extract the end of
          #   validity
          options={
            'verify_signature': False,
            'verify_exp': False,
          },
        )['exp'],
        localtime=False,
        usegmt=True,
      )
      kw['refresh_cookie_attribute_dict'] = refresh_cookie_attribute_dict
    if user is not None:
      getattr(
        user,
        'resetCredentials',
        lambda **kw: None,
      )(
        request=request,
        response=response,
      )
    result = False
    # Note: pick IExtractionPlugin just because it is implemented by
    # ERP5OAuth2ResourceServerPlugin plugin and should be a rare plugin type.
    # But we will be calling non-PAS API on it.
    # XXX: register an "OAuth2 Resource Server" plugin type and use this
    # instead ?
    for _, plugin_value in self.acl_users.plugins.listPlugins(
      IExtractionPlugin,
    ):
      if isinstance(plugin_value, ERP5OAuth2ResourceServerPlugin):
        result |= plugin_value.setCookie(**kw)
    if not result:
      # No PAS plugin set a cookie, this session is lost.
      # So terminate it cleanly...
      self.terminateSession(
        request=request,
        access_token=access_token,
        refresh_token=refresh_token,
      )
      # ...signal an issue to caller...
      access_token = refresh_token = None
      # ...and log.
      LOG(
        'OAuth2AuthorisationClientConnector',
        WARNING,
        'No PAS plugin accepted to set cookies, terminating session.',
      )
    return access_token, refresh_token, None

  def _getStateCookieNamePrefix(self):
    return _ANTI_CSRF_COOKIE_NAME_BASE + self.getId()

  def _setStateCookie(self, RESPONSE, content, name=None, **kw):
    if name is None:
      # User may be opening multiple login forms in parallel, and we must avoid
      # one overwriting the state cookie of the other, so any login page
      # succeeds and not just the last one to load.
      # This should not require expensive, cryptographically-secure value as
      # the user is not expected to open more than a dozen pages within the
      # time needed for a single response to reach their browser and further
      # requests start containing one of the generated cookies. So getting
      # 16bits from the python prng to get an N in 64k collision probability,
      # N=number of parallel requests, should be a reasonable balance.
      # Note: "-" is not part of _getStateCookieNamePrefix for transitory
      # backward compatibility reasons.
      name = self._getStateCookieNamePrefix() + '-' + str(
        random.getrandbits(16),
      )
    RESPONSE.setCookie(
      name=name,
      value=base64.urlsafe_b64encode(content),
      # prevent this cookie from being read over the network
      # (assuming an uncompromised SSL setup, but if it is compromised
      # then the attacker may just as well impersonate the victim using
      # their tokens).
      secure=True,
      # Prevent this cookie from being read by javascript.
      http_only=True,
      path='/',
      same_site='Strict',
      **kw
    )

  def _getRawStateCookieDict(self, REQUEST):
    """
    Retrieve all possible state cookies for context, without
    validating nor decoding their content.
    For debugging/tracing purposes only.
    """
    result = {}
    prefix = self._getStateCookieNamePrefix()
    for name, value in six.iteritems(REQUEST.cookies):
      if name.startswith(prefix):
        result[name] = value
    return result

  def _getStateCookieDict(self, REQUEST, RESPONSE):
    """
    Retrieve and decode all state cookies valid for context.
    """
    result = {}
    decrypt = self.__getMultiFernet().decrypt
    ttl = self._SESSION_STATE_VALIDITY
    for name, value in six.iteritems(self._getRawStateCookieDict(REQUEST)):
      try:
        result[name] = decrypt(
          base64.urlsafe_b64decode(value),
          ttl=ttl,
        )
      except (fernet.InvalidToken, TypeError):
        self._expireStateCookie(RESPONSE, name)
    return result

  def _expireStateCookie(self, RESPONSE, name):
    self._setStateCookie(
      RESPONSE=RESPONSE,
      content='deleted',
      name=name,
      max_age=0,
      expires='Wed, 31-Dec-97 23:59:59 GMT',
    )

  def _getNeutralContextValue(self):
    """
    Where to send user in case of doubt.
    """
    result = self.getWebSiteValue()
    if result is None:
      return self.getPortalObject()
    return result

  def _getUser(self):
    user = getSecurityManager().getUser()
    if (
      user is not None and
      user.getUserName() != 'Anonymous User'
    ):
      return user
    return None

  def _getOAuth2User(self):
    user = getSecurityManager().getUser()
    if (
      user is not None and
      user.getUserName() != 'Anonymous User' and
      getattr(user, 'isFromOAuth2Token', lambda: False)()
    ):
      return user
    return None

  #
  #   Local API.
  #

  security.declareProtected(
    Permissions.ModifyPortalContent,
    'renewStateSecret',
  )
  def renewStateSecret(self, revoke_until=0.0):
    """
    Start signing and encrypting state with a new key.

    revoke_until (float)
      Revoke keys older than this unix timestamp, making all states signed by
      these keys invalid.
      Use float('inf') to revoke all existing keys.
    """
    self.__state_fernet_key_list = (
      (
        time(),
        fernet.Fernet.generate_key(),
      ),
    ) + tuple(
      x
      for x in self.__state_fernet_key_list
      if x[0] > revoke_until
    )

  security.declarePublic('login')
  def login(
    self,
    REQUEST,
    RESPONSE,
    scope_list=(),
    came_from=None,
    portal_status_message=None,
  ):
    """
    Initiate an OAuth2 session creation.

    Redirect the User-Agent to our Authorisation Server to get an Authorisation
    Code.
    """
    if self.getValidationState() != 'validated':
      raise NotFound
    # redirect_uri is used so the User-Agent can tell the Authorisation Server
    # how to come back to us.
    redirect_uri = self.getRedirectUri()
    # came_from is what the user was trying to do just before they ended up
    # here, so we can redirect them there once they are authenticated.
    if came_from:
      parsed_came_from = urlparse(came_from)
      parsed_redirect_uri = urlparse(redirect_uri)
      if (
        parsed_came_from.scheme != parsed_redirect_uri.scheme or
        parsed_came_from.netloc != parsed_redirect_uri.netloc
      ):
        self._getNeutralContextValue().Base_redirect(
          keep_items={
            'portal_status_message': self.Base_translateString(
              'Redirection to an external site prevented.',
            ),
          },
        )
    else:
      # Caller did not provide a came_from. Pick one for them.
      # Add trailing slash to make ERP5JS happy.
      came_from = self._getNeutralContextValue().absolute_url() + '/'
    if self._getUser() is not None:
      # User is authenticated (in any way, for consistency with a local
      # Authorisation Server's /authorize endpoint), we cannot do anything
      # more for them.
      # So send them to came_from, with instructions to not come back here.
      self.Base_redirect(
        self.ERP5Site_preventLoginAttemptRetry(came_from),
      )
      return
    try:
      # If user is comming with a valid state cookie, reuse it rather than
      # generating a new value. This allows this method to be called while a
      # login process is already underway (ex: user opening multiple tabs,
      # getting redirected to login form, and picking any but the last login
      # form to log in).
      # The cookie will be stored again to extend its validity, in case the
      # existing cookie is old.
      # Any existing cookie is fine.
      name, identifier = next(six.iteritems(self._getStateCookieDict(
        REQUEST=REQUEST,
        RESPONSE=RESPONSE,
      )))
    except StopIteration:
      name = None
      identifier = base64.urlsafe_b64encode(urandom(32))
    code_verifier = base64.urlsafe_b64encode(urandom(32))
    _, state_key = self.__getStateFernetKeyList()[0]
    encrypt = fernet.Fernet(state_key).encrypt
    query_list = [
      ('response_type', 'code'),
      ('client_id', self.getReference()),
      ('redirect_uri', redirect_uri),
      (
        'state',
        # Note: fernet both signs and encrypts the content.
        # It uses on AES128-CBC, PKCS7 padding, and SHA256 HMAC, with
        # independent keys for encryption and authentication.
        encrypt(json.dumps({
          # Identifier is also stored in User-Agent as a cookie.
          # This is used to prevent an attacker from tricking a user into
          # giving us an Authorisation Code under the control of the attacker.
          # To successfuly fake this value, the attacker would need to set a
          # cookie on user's browser (despite the cookie being marked as
          # "should not be writable by javascript" using the "__Host-" prefix)
          # for our domain (or get access to an existing cookie's value,
          # despite the cookie being marked as "should not be readable by
          # javascript" using the "http-only" flag) and then guess our fernet
          # key to produce this encrypted value.
          # Note: as identifier is accessible in cleartext to the user, this
          # means the key may be attaked using (partially) known-cleartext
          # (if AES128 is found vulnerable to such attack).
          _STATE_IDENTIFIER_NAME: identifier,
          # The came_from value, which must not be altered now that we
          # validated it, and should be kept secret from 3rd-parties to protect
          # user's privacy.
          # Note: as came_from is under user control (modulo the sanity checks
          # done above), this means the key may be attacked using (partially)
          # chosen-cleartext (if AES128 is found vulnerable to such attack).
          _STATE_CAME_FROM_NAME: (
            came_from.decode('utf-8')
            if came_from else
            came_from
          ),
          # The value to submit to Authorisation Server to have the
          # Authorisation Code converted into tokens. To be kept secret from
          # everyone other than this server.
          _STATE_CODE_VERIFIER_NAME: code_verifier,
        })),
      ),
      ('code_challenge_method', 'S256'),
      (
        'code_challenge',
        # S256 standard PKCE encoding
        base64.urlsafe_b64encode(
          hashlib.sha256(code_verifier).digest(),
        ).rstrip('='),
      ),
    ]
    if scope_list:
      query_list.append(
        ('scope', ' '.join(scope_list)),
      )
    if portal_status_message:
      query_list.append( # Non-standard parameter
        ('portal_status_message', portal_status_message),
      )
    self._setStateCookie(
      RESPONSE=RESPONSE,
      name=name,
      content=encrypt(identifier),
    )
    if (
      self.isAuthorisationServerRemote() or
      REQUEST.environ['REQUEST_METHOD'] not in ('GET', 'HEAD')
    ):
      RESPONSE.setStatus(302)
      RESPONSE.setHeader(
        'Location',
        self._getAuthorisationServerValue(
          REQUEST=REQUEST,
        ).absolute_url() + '/authorize?' + urlencode(query_list),
      )
    else:
      # Provide the current URL to authorize, so that it can redirect the
      # user agent to it in the event of an authentication failure: the login
      # form's action URL may not be suitable for rendering a new login form.
      # This is not necessary when the authorisation server is remote, as it
      # has full control of its own URLs and can compute its own redirects to
      # retry an authentication.
      login_retry_url = REQUEST.other['ACTUAL_URL']
      query_string = REQUEST.environ['QUERY_STRING']
      if query_string:
        login_retry_url += '?' + query_string
      # Authorisation Server is local, but as we are using the same codepath
      # as regular accesses (to keep code branch count down in order to keep
      # complexity and attack surface down) it will expect arguments from the
      # request, and will write to our response.
      return self._getAuthorisationServerValue(
        REQUEST=REQUEST,
      ).authorizeLocal(
        REQUEST=REQUEST,
        RESPONSE=RESPONSE,
        query_list=query_list,
        login_retry_url=login_retry_url,
      )

  security.declarePublic('loggedIn')
  def loggedIn(self, REQUEST, RESPONSE, code=None, state=None):
    """
    Using provided authorisation_code, request tokens from Authorisation
    Server, and set them as cookies.
    """
    try:
      state_dict = json.loads(
        self.__getMultiFernet().decrypt(
          state,
          ttl=self._SESSION_STATE_VALIDITY,
        ),
      )
    except (fernet.InvalidToken, ValueError) as exc:
      state_dict = {}
      state_error = exc
    else:
      state_error = None
    def redirect(message=None):
      kw = {
        'keep_items': {},
      }
      if message is not None:
        kw['keep_items']['portal_status_message'] = message
      came_from = state_dict.get(_STATE_CAME_FROM_NAME)
      if came_from:
        context = self # whatever
        kw['redirect_url'] = came_from.encode('utf-8')
      else:
        context = self._getNeutralContextValue()
      context.Base_redirect(**kw)
    # User may be already authenticated, for example if they opened multiple
    # login forms, and then submitted more than one, little by little.
    # If we do not have everything we need, pretend authentication was
    # successful but do not change the user's session cookies (and do not
    # bother about login state cookie).
    # If we have everything we need, log the user out of their current session
    # and in to the new one.
    user = self._getOAuth2User()
    if user is None:
      def error(message):
        LOG(
          'OAuth2AuthorisationClientConnector',
          INFO,
          'Rejected login code=%r, reason=%r' % (code, message),
        )
        # Force redirection to a safe place
        state_dict.pop(_STATE_CAME_FROM_NAME, None)
        redirect(
          self.Base_translateString('Login and/or password is incorrect.'),
        )
    else:
      def error(message):
        # User is authenticated with oauth2. This means their authentication
        # cookie reached us, which means navigation is not happening in a
        # cross-site context.
        # If authentication cookies were submitted despite a cross-site
        # context, then an attacker could just as well send the user to the
        # came_from themselves, without going through the trouble of
        # constructing a loggedIn request.
        redirect()
    if (
      code is None or
      _STATE_CAME_FROM_NAME not in state_dict or
      _STATE_CODE_VERIFIER_NAME not in state_dict or
      _STATE_IDENTIFIER_NAME not in state_dict
    ):
      error(
        message='Malformed state: %r reason=%r' % (state_dict, state_error),
      )
      return
    state_cookie_dict = self._getStateCookieDict(
      REQUEST=REQUEST,
      RESPONSE=RESPONSE,
    )
    identifier_from_state = state_dict[_STATE_IDENTIFIER_NAME].encode('ascii')
    for (
      state_cookie_name,
      identifier_from_cookie,
    ) in six.iteritems(state_cookie_dict):
      # Use data-invariant comparison function to not expose the
      # "identifier_*" value to timing attacks.
      if hmac.compare_digest(identifier_from_cookie, identifier_from_state):
        break
    else:
      # Note: DO NOT try to salvage this request if the user is anonymous: a
      # CSRF attacker *can* get everything valid except this correspondance
      # (this is why it is checked to begin with). For example, it is not
      # possible to trust the came_from if this check fails: an attacker could
      # have provided their own value to a login page, which will have produced
      # a valid state. So we must not try to send the user back to the login
      # page with such came_from, otherwise we just reopened the CSRF
      # vulnerability this check is designed to close.
      error(
        message='Inconsistent identifiers, cookie=%r (raw: %r) '
        'parameter=%r' % (
          state_cookie_dict,
          self._getRawStateCookieDict(REQUEST),
          identifier_from_state,
        ),
      )
      return
    inner_response = self._callOAuth2(
      request=REQUEST,
      method='token',
      data_dict={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': self.getRedirectUri(),
        'client_id': self.getReference(),
        'code_verifier': state_dict[_STATE_CODE_VERIFIER_NAME].encode('ascii'),
      },
    )
    access_token, _, error_message = self._setCookieFromTokenResponse(
      request=REQUEST,
      response=RESPONSE,
      inner_response=inner_response,
      user=user,
    )
    if access_token is None:
      error(message='Token retrieval failed: %s' % (error_message))
      return
    # Only expire the cookie we used to log in, in an attempt to keep
    # functional other login forms the user may have opened. Not all will be
    # working: they could have reused the cookie we just deleted. Which is fine
    # if the user stays connected: then, we will detect that they are still
    # authenticated and will redirect them to their respective came_from. But
    # for those which did not reuse this cookie, they will be fully functional
    # even if the user logs out before using them.
    self._expireStateCookie(RESPONSE=RESPONSE, name=state_cookie_name)
    redirect()

  security.declareProtected(
    Permissions.AccessContentsInformation,
    'getRedirectUri',
  )
  def getRedirectUri(self):
    """
    Return the redirect URI which will allow the Authorisation Server to send
    the User-Agent back to us so we can retrieve the Authorisation Code.
    Note: the URL generated here depends on how we are accessed (which domain,
    VirtualHostMonter, ...).
    """
    return self.absolute_url() + '/loggedIn'

  #
  #   Local API used by PAS plugin.
  #

  security.declarePrivate('getSessionVersion')
  def getSessionVersion(self, session_id, REQUEST):
    return self._getAuthorisationServerValue(
      REQUEST=REQUEST,
    ).getSessionVersion(session_id)

  security.declarePrivate('getAccessTokenSignatureAlgorithmAndPublicKeyList')
  def getAccessTokenSignatureAlgorithmAndPublicKeyList(self, REQUEST):
    return self._getAuthorisationServerValue(
      REQUEST=REQUEST,
    ).getAccessTokenSignatureAlgorithmAndPublicKeyList()

  security.declarePrivate('getNewAccessToken')
  def getNewAccessToken(self, request, refresh_token):
    """
    Called by an ERP5OAuth2ResourceServerPlugin instance when if could find
    an Access Token cookie, but could not use it. Try to renew it, and return
    the token generated for that plugin, if any, and any new refresh token.
    """
    access_token, refresh_token, _ = self._setCookieFromTokenResponse(
      request=request,
      response=request.RESPONSE,
      inner_response=self._callOAuth2(
        request=request,
        method='token',
        data_dict={
          'grant_type': 'refresh_token',
          'refresh_token': refresh_token,
        },
      ),
    )
    return access_token, refresh_token

  security.declarePrivate('terminateSession')
  def terminateSession(self, request, access_token, refresh_token):
    """
    Called by an ERP5OAuth2ResourceServerPlugin instance when logging out.
    Do a best-effort to log the user out:
    - use its refresh token if provided
    - otherwise use its access token
    - do not complain if Authorisation Server rejects the revocation:
    it means these the token is unusable, which is the point of calling
    this method.
    """
    if refresh_token:
      token = refresh_token
      token_type_hint = 'refresh_token'
    else:
      token = access_token
      token_type_hint = 'access_token'
    inner_response = self._callOAuth2(
      request=request,
      method='revoke',
      data_dict={
        'token': token,
        'token_type_hint': token_type_hint,
      },
    )
    if inner_response.status not in (200, 204):
      LOG(
        'OAuth2AuthorisationClientConnector',
        INFO,
        'Unhandled error when revoking session: %r' % (inner_response, ),
      )
