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

import contextlib
from functools import wraps
from io import BytesIO
import json
from os import urandom
from time import time
from six.moves.urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import uuid
from cryptography.hazmat.backends import default_backend
from cryptography import fernet
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
  Encoding,
  NoEncryption,
  PublicFormat,
  PrivateFormat,
)
import jwt
from oauthlib.oauth2 import (
  AuthorizationCodeGrant,
  AuthorizationEndpoint,
  BearerToken,
  IntrospectEndpoint,
  InvalidGrantError,
  InvalidRequestFatalError,
  OAuth2Error,
  RefreshTokenGrant,
  RequestValidator,
  RevocationEndpoint,
  ServerError,
  TokenEndpoint,
)
import six
from AccessControl.SecurityManagement import (
  getSecurityManager,
  setSecurityManager,
)
from AccessControl import (
  ClassSecurityInfo,
  ModuleSecurityInfo,
)
from DateTime import DateTime
from Products.ERP5Type import Permissions
from Products.ERP5Type.Message import translateString
from Products.ERP5Type.UnrestrictedMethod import super_user
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Security.ERP5GroupManager import (
  disableCache as ERP5GroupManager_disableCache,
)
from Products.ERP5Security.ERP5OAuth2ResourceServerPlugin import (
  isAddressInNetworkList,
  encodeAccessTokenPayload,
  decodeAccessTokenPayload,
  JWT_PAYLOAD_KEY,
  JWT_PAYLOAD_AUTHORISATION_SESSION_ID_KEY,
  JWT_PAYLOAD_AUTHORISATION_SESSION_VERSION_KEY,
  JWT_PAYLOAD_CLIENT_REFERENCE_KEY,
  JWT_PAYLOAD_USER_ID_KEY,
  JWT_PAYLOAD_USER_CAPTION_KEY,
  JWT_PAYLOAD_ROLE_LIST_KEY,
  JWT_PAYLOAD_GROUP_LIST_KEY,
  JWT_PAYLOAD_SCOPE_LIST_KEY,
  JWT_CLAIM_NETWORK_LIST_KEY,
)
from ZPublisher.HTTPResponse import HTTPResponse

def ensure_ascii(s):
  if six.PY2:
    return s.encode('ascii')
  else:
    if isinstance(s, str):
      s = bytes(s, 'ascii')
    return s.decode('ascii')

_DEFAULT_BACKEND = default_backend()
_SIGNATURE_ALGORITHM_TO_KEY_BYTE_LENGTH_DICT = {
  'HS256': 32,
  'HS384': 48,
  'HS512': 64,
}

class _MethodNotAllowed(InvalidRequestFatalError):
  status_code = 405

ModuleSecurityInfo(__name__).declarePublic('substituteRequest')
@contextlib.contextmanager
def substituteRequest(
  context,
  request,
  method,
  query_list=(),
  form=(),
  response=None,
):
  """
  Build a new request object containing copies of the environment,
  authorisation, cookies and "other" from given request.
  Allows calling functions expecting their arguments from a request, without
  disturbing the true request to help produce representative error log
  entries.

  For compatibility, replaces the request stored in RequestContainer
  (where context.REQUEST comes from) with given request for the scope of this
  context manager, and restores it during context teardown.

  context (object)
    Any object in an acquisition wrapper, in order to locate the request
    container.
  request (HTTPRequest)
    The request to set for the scope of this context manager.
  method (str)
    HTTP method set on the constructed request.
  query_list (list of 2-tuples of strings)
    List of fields to set as query string and form in the inner request.
  form (list of 2-tuples of strings and objects)
    List of values to set as form in the inner request.
    For use when method is 'POST'.
  response (None, HTTPResponse)
    Response to use for the new request.
    If None, the one from the provided request is used.
  """
  security_manager = getSecurityManager()
  # Expected aq_chain is: [..., <Zope app>, <RequestContainer>]
  aq_chain = context.aq_chain
  environ = request.environ
  inner_environ_dict = environ.copy()
  inner_environ_dict['REQUEST_METHOD'] = method
  inner_environ_dict['QUERY_STRING'] = urlencode(query_list)
  if request._auth:
    inner_environ_dict['HTTP_AUTHORIZATION'] = request._auth

  inner_request = request.__class__(
    stdin=BytesIO(b''),
    environ=inner_environ_dict,
    response=(
      request.RESPONSE
      if response is None else
      response
    ),
  )
  inner_request.processInputs()
  inner_request.form.update(form)
  inner_request['PARENTS'] = [aq_chain[-2]]
  try:
    getCurrentSkinName = context.getCurrentSkinName
  except AttributeError:
    skinname = None
  else:
    skinname = getCurrentSkinName()
    context.changeSkin(skinname=None, REQUEST=inner_request)
  # Note: the only goal of this traversal is to finalise setting up
  # inner_request, by triggering taversal hooks, and especially
  # VirtualHostMonster. The return value is then ignored, because it is whatever
  # object was traversed by REQUEST, which may be a callable.
  # As a consequence, we still have to put inner_request in the RequestContainer
  # object at the top of "context"'s acquisition chain.
  inner_request.traverse(request.environ['PATH_INFO'])
  # Restore our initial security manager.
  # Authentication result of above traversal is ignored and expected consistent
  # with the traversal Zope made with REQUEST. This should be fine, as reasons
  # for inconsistency would also be ignored if we were not replacing the
  # request to begin with.
  # But also, this context manager may be used inside a proxy-roled script, in
  # which case the security cannot be reconstructed by traversal alone.
  setSecurityManager(security_manager)
  request_container = aq_chain[-1]
  request_from_container = request_container.REQUEST
  request_container.REQUEST = inner_request
  try:
    __traceback_info__ = inner_request
    yield inner_request
  finally:
    request_container.REQUEST = request_from_container
    if skinname is not None:
      context.changeSkin(skinname=skinname, REQUEST=request)
    inner_request.clear()

@contextlib.contextmanager
def _substituteRequestAndResponse(context, request, response):
  original_response = request.response
  try:
    request.response = request.other['RESPONSE'] = response
    yield request
  finally:
    request.response = request.other['RESPONSE'] = original_response

class _ERP5AuthorisationEndpoint(AuthorizationEndpoint):
  def __init__(
    self,
    server_connector_path,
    zope_request,
    login_retry_url,
    getSignedLoginRetryUrl,
    **kw
  ):
    super(_ERP5AuthorisationEndpoint, self).__init__(**kw)
    self.__server_connector_path = server_connector_path
    self.__zope_request = zope_request
    self.__login_retry_url = login_retry_url
    self.__getSignedLoginRetryUrl = getSignedLoginRetryUrl

  def create_authorization_response(
    self,
    uri,
    http_method='GET',
    body=None,
    headers=None,
    scopes=None,
    credentials=None,
  ):
    scope_list, request_info_dict = self.validate_authorization_request(
      uri=uri,
      http_method=http_method,
      body=body,
      headers=headers,
    )
    request = request_info_dict.pop('request')
    client_value = request.client.erp5_client_value
    need_login = not _isAuthenticated()
    is_local_client = client_value.isLocal()
    # Trust local clients, as their login must be transformed into a session
    # within the same request, so there is no room for a redirection to the
    # authorisation dialog.
    # XXX: unless we manually propagate the login information...
    # Which Base_callDialogMethod would then risk leaking to browser history
    # and proxies by deciding to redirect to form_action rather than
    # executing it immediately...
    is_trusted_client = is_local_client or client_value.isTrusted()
    if http_method == 'POST' or (
      is_trusted_client and
      http_method == 'GET' and
      not need_login
    ):
      if need_login:
        # Authentication attempt failed ...
        if is_local_client and self.__login_retry_url:
          # ...with a local resource server, redirect user agent to
          # the provided login URL.
          split_login_retry_url = urlsplit(self.__login_retry_url)
          return (
            (
              (
                'Location',
                urlunsplit((
                  split_login_retry_url.scheme,
                  split_login_retry_url.netloc,
                  split_login_retry_url.path,
                  urlencode([
                    (x, y)
                    for x, y in parse_qsl(split_login_retry_url.query)
                    if x != 'portal_status_message'
                  ] + [(
                    'portal_status_message',
                    client_value.Base_translateString("Login and/or password is incorrect."),
                  )]),
                  split_login_retry_url.fragment, # Should be unnecessary, but...
                )),
              ),
            ),
            None,
            302
          )
        # ... with a remote resource server, follow OAuth2 protocol.
        raise InvalidGrantError('Invalid credentials given.', request=request)
      # Authentication attempt succeeded, generate an authorisation code.
      (
        authorization_header_dict,
        authorization_body,
        authorization_status,
      ) = super(
        _ERP5AuthorisationEndpoint,
        self,
      ).create_authorization_response(
        uri=uri,
        http_method=http_method,
        body=body,
        headers=headers,
        scopes=scopes,
        credentials=credentials,
      )
      if authorization_status == 302 and is_local_client:
        split_location = urlsplit(authorization_header_dict['Location'])
        # XXX: to cut down on code complexity, this code has strong expectations on what location is.
        _, client_connector_id, method_id = split_location.path.rsplit('/', 2)
        if method_id != 'loggedIn':
          raise ValueError(split_location.path)
        client_connector_value = client_value.getParentValue().getParentValue()[client_connector_id]
        if client_connector_value.getPortalType() != 'OAuth2 Authorisation Client Connector':
          raise ValueError(split_location.path)
        query_list = parse_qsl(split_location.query)
        # Note: query string generation should not have produce any duplicate
        # entries, so convert into a dict for code simplicity.
        query_dict = {
          ensure_ascii(x): ensure_ascii(y)
          for x, y in query_list
        }
        inner_response = HTTPResponse(stdout=None, stderr=None)
        with substituteRequest(
          context=client_value,
          request=self.__zope_request,
          method='GET',
          query_list=query_list,
          response=inner_response,
        ) as inner_request:
          client_connector_value.loggedIn(
            REQUEST=inner_request,
            RESPONSE=inner_response,
            code=query_dict['code'],
            state=query_dict.get('state'),
          )
        return (
          inner_response.listHeaders(),
          inner_response.body,
          inner_response.status,
        )
      else:
        return (
          authorization_header_dict.items(),
          authorization_body,
          authorization_status,
        )
    if http_method in ('GET', 'HEAD'):
      portal = client_value.getPortalObject()
      # HACK: add support for response_mode (which is not an OAuth2 feature
      # but an OpenID feature), as requested by Romain.
      # oauthlib does not strictly separates both implementations, so this
      # parameter works, but it is ignored by validate_authorization_request
      # and is hence missing in request_info_dict. Run the normal checks and
      # add it ourselves.
      # This may not work if we switch to a stricter oauth2 implementation.
      if 'response_mode' in request.duplicate_params:
        raise InvalidRequestFatalError(
          description='Duplicate response_mode parameter.',
          request=request,
        )
      request_info_dict['response_mode'] = request.response_mode
      # /HACK
      # Make sure request_info_dict only contains string values (so nothing
      # will be lost by representing them in HTML), and strip any None.
      new_request_info_dict = {}
      for key, value in six.iteritems(request_info_dict):
        if value is None:
          continue
        if not isinstance(value, six.text_type):
          raise TypeError((key, repr(value)))
        new_request_info_dict[key] = value
      inner_response = HTTPResponse(stdout=None, stderr=None)
      # XXX: force these headers (by setting them after
      # ERP5Site_viewOAuth2AuthorisationDialog returned) ?
      inner_response.setHeader('Cache-Control', 'no-store')
      inner_response.setHeader('Pragma', 'no-cache')
      neutral_context_value = client_value.getWebSiteValue()
      if neutral_context_value is None:
        neutral_context_value = portal
      with substituteRequest(
        context=portal,
        request=self.__zope_request,
        method=http_method,
        response=inner_response,
      ) as inner_request:
        if need_login:
          # Current URL from client point of view, to use to redirect them back
          # here (ex: after authenticating).
          came_from = (
            # Use the internal path back to us so it can be traversed to while
            # still in the just-authenticated request.
            (
              self.__server_connector_path + '?' + urlsplit(uri).query
            ) if is_local_client else
            # Use the external URL back to us so user can be redirected to it,
            # as they are then authenticated over multiple requests.
            uri
          )
          # Render login form.
          form = inner_request.form
          other = inner_request.other
          other['came_from'] = form['came_from'] = came_from
          login_form_kw = {}
          if is_local_client:
            login_retry_url = self.__getSignedLoginRetryUrl()
            if login_retry_url:
              login_form_kw['login_retry_url'] = other[
                'login_retry_url'
              ] = form['login_retry_url'] = login_retry_url
            login_form = neutral_context_value.login_once_form
          else:
            login_form = neutral_context_value.login_form
          portal_status_message_list = [
            value
            for name, value in parse_qsl(
              urlsplit(came_from).query,
            )
            if name == 'portal_status_message'
          ]
          if portal_status_message_list:
            portal_status_message, = portal_status_message_list
            form['portal_status_message'] = portal_status_message
          else:
            portal_status_message = None
          body = login_form(
            REQUEST=inner_request,
            RESPONSE=inner_response,
            came_from=came_from,
            portal_status_message=portal_status_message,
            **login_form_kw
          )
        else:
          # User is authenticated, ask whether they authorise the client.
          # XXX: we should really have a way to pass parameters to forms other
          # than stuffing them in REQUEST... Because of these parameters,
          # immediately render the form rather than redirect to it.
          other = inner_request.other
          # List of scopes requested by the client (and which are actually
          # allowed for this client to request).
          other['scope_item_list'] = [
            {
              'caption': x.getTranslatedTitle(),
              'value': x.getCategoryRelativeUrl(),
              'description': x.getTranslatedDescription(),
            }
            for x in (
              portal.portal_categories.resolveCategory(
                'oauth2_scope/' + y.encode('utf-8'),
              )
              for y in scope_list
            )
            # scope is allowed for this client but the category does not exist.
            # _ERP5RequestValidator is not functionally required to follow the
            # relation, so it may not have noticed.
            if x is not None
          ]
          other['server_connector_path'] = self.__server_connector_path
          other['client_id'] = client_value.getId()
          other['client_title'] = client_value.getTranslatedTitle()
          other['client_description'] = client_value.getTranslatedDescription()
          other['request_info_json'] = json.dumps(new_request_info_dict)
          body = neutral_context_value.ERP5Site_viewOAuth2AuthorisationDialog(
            REQUEST=inner_request,
            RESPONSE=inner_response,
          )
      return (
        inner_response.listHeaders(),
        (
          ''
          if http_method == 'HEAD' else
          body
        ),
        inner_response.status,
      )
    raise _MethodNotAllowed(
      description='%r is not an acceptable method on this endpoint' % (
        http_method,
      ),
    )

def _isAuthenticated():
  """
  Return whether this request is authenticated.
  """
  user = getSecurityManager().getUser()
  # Note: this is actually what Zope and PAS check.
  return user is not None and user.getUserName() != 'Anonymous User'

class _Client(object):
  """
  Helper class for _ERP5RequestValidator
  Because oauthlib assumes the properties of a client objet
  """
  def __init__(self, client_id, client_value):
    # oauthlib API
    self.client_id = client_id
    # ERP5 API
    self.erp5_client_value = client_value

class _SessionUser(object):
  """
  Helper class for _ERP5RequestValidator
  Because oauthlib assumes the properties of a user objet.

  Current user is authenticated with an OAuth2 grant.
  So an Authorisation Code or a Refresh Token.
  """
  def __init__(self, session_value):
    with super_user():
      user_value = session_value.getSourceSectionValue()
    user_id = (
      session_value.getSourceSectionFreeText()
      if user_value is None else
      user_value.getUserId()
    )
    assert user_id and user_id != 'Anonymous User'
    # oauthlib API
    self.id = user_id
    # ERP5 API
    self.erp5_session_value = session_value

# XXX: decode tokens only once per request, to avoid entirely the risk of
# getting an expiration mid-request ? But what repesentation should be cached ?
class _ERP5RequestValidator(RequestValidator):
  """
  Implement oauthlib.oauth2.RequestValidator API.

  This class mostly deffers the logic to an OAuth2AuthorisationServerConnector instance.
  """

  def __init__(self, authorisation_server_connector_value):
    self._authorisation_server_connector_value = authorisation_server_connector_value

  def _getClientValue(self, client_id):
    try:
      result = self._authorisation_server_connector_value[client_id.encode('utf-8')]
    except KeyError:
      return
    if result.getValidationState() == 'validated':
      return result

  @staticmethod
  def _callForTokenTypeHint(token_type_hint, access_token_callable, refresh_token_callable, kw):
    for token_callable in (
      [refresh_token_callable, access_token_callable]
      if token_type_hint == 'refresh_token' else
      [access_token_callable, refresh_token_callable]
    ):
      try:
        return token_callable(**kw)
      except jwt.InvalidTokenError:
        pass
    raise

  def client_authentication_required(self, request, *args, **kwargs):
    # Use this method, which is called early on most endpoints, to setup request.client .
    client_id = request.client_id
    if client_id is None:
      authorisation_server_connector_value = self._authorisation_server_connector_value
      if request.grant_type == 'refresh_token':
        # token renewal
        try:
          client_id = request.client_id = authorisation_server_connector_value.getRefreshTokenClientId(
            value=request.refresh_token,
            request=request,
          )
        except jwt.DecodeError:
          pass
      elif request.grant_type is None and request.token:
        # token revocation
        try:
          client_id = request.client_id = self._callForTokenTypeHint(
            token_type_hint=request.token_type_hint,
            access_token_callable=authorisation_server_connector_value.getAccessTokenClientId,
            refresh_token_callable=authorisation_server_connector_value.getRefreshTokenClientId,
            kw={
              'value': request.token,
              'request': request,
            },
          )
        except jwt.DecodeError:
          pass
    if client_id is not None:
      client_value = self._getClientValue(client_id)
      if client_value is not None:
        request.client = _Client(
          client_id=client_id,
          client_value=client_value,
        )
    return False

  @staticmethod
  def authenticate_client(*args, **kw):
    # To implement eventually
    raise RuntimeError

  @staticmethod
  def authenticate_client_id(client_id, request, *args, **kwargs):
    return request.client is not None

  def confirm_redirect_uri(self, client_id, code, redirect_uri, client, request, *args, **kwargs):
    # Tolerate inconsistent redirect_uri in case of a local client:
    # The original redirect_uri was generated by client.login in the context of
    # a browser access (typically to a /login_form URL). The produced
    # redirect_uri is consistent with this access:
    # - it represent the browser's view of the path, with any Virtual Host
    #   Monster magic hidden away
    # - it includes the consequence of any Web Site traversal which happened,
    #   which, because the client object it outside the website,
    #   web_site_module/<Web Site id> will be present in redirect_uri.
    # But now, we are being called (strictly in the case of a local client)
    # in the context of a form submission (login_once_form, typically) on the
    # authorisation server persona of this instance, which is outside of
    # the website and should not have traversed it, meaning the Web Site
    # traversal hook was never called. So now, the client is still the same,
    # but web_site_module/<Web Site id> will be absent from the redirect_uri it
    # will produce. And which it did when the form POST hander called
    # client.loggedIn, which then called us with it and the authorisation code
    # in order to receive the final token.
    # So the generated redirect_uri does not match the original one.
    # And because we do not control the entire traversal logic seen by the
    # browser (IOW, the are RewriteRules & friends being handled outside of
    # Zope, which is the entire reason why Virtual Host Monster and Web Site
    # traverse hook exist), we cannot reproduce the same context here, so we
    # cannot obtain the same redirect_uri.
    # ... which is not completely true: we could make an exception in how
    # the client produces its redirect_uri when it finds that it is local:
    # it could somehow provide us with two internal paths:
    # - its PATH_INFO, from its HTTPRequest
    # - its (physical) path
    # then the POST handler could HTTPRequest.travese the PATH_INFO and
    # unrestrictedTraverse the path, and should get in the same environment.
    # But this requires a lot of brittle logic, and a way of fitting two paths
    # in what is supposed to be an URL.
    # Instead, accept any redirect_uri in this case. Sadly.
    return (
      client.erp5_client_value.isLocal() or
      self._authorisation_server_connector_value.getSessionValueByAuthorisationCode(code=code).getRedirectUri() == redirect_uri
    )

  def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
    client_value = self._getClientValue(client_id)
    if client_value is None:
      return
    return client_value.getDefaultRedirectUri()

  @staticmethod
  def get_default_scopes(client_id, request, *args, **kwargs):
    return request.client.erp5_client_value.getOauth2ScopeList()

  @staticmethod
  def get_original_scopes(refresh_token, request, *args, **kwargs):
    return request.user.erp5_session_value.getOauth2ScopeList()

  def introspect_token(self, token, token_type_hint, request, *args, **kwargs):
    authorisation_server_connector_value = self._authorisation_server_connector_value
    return self._callForTokenTypeHint(
      token_type_hint=token_type_hint,
      access_token_callable=authorisation_server_connector_value.getAccessTokenIntrospectionDict,
      refresh_token_callable=authorisation_server_connector_value.getRefreshTokenIntrospectionDict,
      kw={
        'token': token,
        'request': request,
      },
    )

  def invalidate_authorization_code(self, client_id, code, request, *args, **kwargs):
    self._authorisation_server_connector_value.invalidateAuthorisationCode(code=code)

  def revoke_token(self, token, token_type_hint, request, *args, **kwargs):
    authorisation_server_connector_value = self._authorisation_server_connector_value
    session_value = self._callForTokenTypeHint(
      token_type_hint=token_type_hint,
      access_token_callable=authorisation_server_connector_value.getSessionValueFromAccessToken,
      refresh_token_callable=authorisation_server_connector_value.getSessionValueFromRefreshToken,
      kw={
        'token': token,
        'request': request,
      },
    )
    with super_user():
      session_value.invalidate(
        comment=translateString('Revoked from OAuth2 endpoint'),
      )

  def rotate_refresh_token(self, request):
    return self._authorisation_server_connector_value.isRefreshTokenRotationNeeded(
      refresh_token=request.refresh_token,
      request=request,
    )

  def save_authorization_code(self, client_id, code, request, *args, **kwargs):
    self._authorisation_server_connector_value.createSession(
      authorisation_code=code['code'],
      request=request,
      client_value=request.client.erp5_client_value,
      redirect_uri=request.redirect_uri,
      scope_list=[
        x.encode('utf-8')
        for x in request.scopes
      ],
      code_challenge=request.code_challenge,
      code_challenge_method=request.code_challenge_method,
      network_address=request.headers['X_FORWARDED_FOR'],
      user_agent=request.headers.get('USER_AGENT'),
    )

  @staticmethod
  def save_bearer_token(token, request, *args, **kwargs):
    # Nothing to do here, our tokens are self-contained.
    # The only persistent "thing" is the session document, which is created when the authorisation code is issued.
    pass

  @staticmethod
  def validate_bearer_token(*args, **kw):
    # Used for Resource endpoint, which is not used.
    raise RuntimeError

  def validate_client_id(self, client_id, request, *args, **kwargs):
    client_value = self._getClientValue(client_id)
    if client_value is None:
      return False
    if request.client is None:
      request.client = _Client(
        client_id=client_id,
        client_value=client_value,
      )
    return True

  def validate_code(self, client_id, code, client, request, *args, **kwargs):
    session_value = self._authorisation_server_connector_value.getSessionValueByAuthorisationCode(code=code)
    if session_value is None:
      return False
    with super_user():
      source_id = session_value.getSourceId()
    if source_id != client_id:
      return False
    request.user = _SessionUser(session_value)
    request.scopes = session_value.getOauth2ScopeList()
    request.code_challenge = session_value.getCodeChallenge()
    request.code_challenge_method = session_value.getCodeChallengeMethod()
    return True

  @staticmethod
  def validate_grant_type(client_id, grant_type, client, request, *args, **kwargs):
    return (
      # XXX: restrict grant types per client ?
      grant_type in ('authorization_code', 'refresh_token') and
      client.erp5_client_value is not None
    )

  @staticmethod
  def validate_redirect_uri(client_id, redirect_uri, request, *args, **kwargs):
    client_value = request.client.erp5_client_value
    if client_value is None:
      # Unknown client: redirect URI cannot be valid, reject.
      return False
    redirect_uri_set = client_value.getRedirectUriSet()
    if redirect_uri_set:
      # Explicitly-declared URIs: redirect URI is valid if it is in that set.
      return redirect_uri in redirect_uri_set
    if client_value.isLocal():
      # Sadly, it is not possible to just traverse to the client and check if the
      # redirect_uri matches: at the time it was generated, if there was a Web Site
      # in its publication path, the Web Site would do shenanigans to insert itself
      # back into the absolute_url. But now that we are trying to reproduce that,
      # we lost the information of what the website was: it may be present in the
      # redirect_uri path, but it may be under an extra layer of VirtualHost Monster
      # magic.
      # Client is declared local, accept any redirect URI on our scheme and netloc.
      split_my_url = urlsplit(client_value.absolute_url())
      split_redirect_uri = urlsplit(redirect_uri)
      return (
        split_my_url.scheme == split_redirect_uri.scheme and
        split_my_url.netloc == split_redirect_uri.netloc
      )
    # Client is not declared local (or not actually found locally),
    # there is no way to guess an allowed URI, reject.
    return False

  def validate_refresh_token(self, refresh_token, client, request, *args, **kwargs):
    session_value = self._authorisation_server_connector_value.getSessionValueFromRefreshToken(
      token=refresh_token,
      request=request,
    )
    if session_value is not None:
      with super_user():
        session_client_id = session_value.getSourceId()
      if session_client_id == client.client_id:
        request.user = _SessionUser(session_value)
        return True
    return False

  @staticmethod
  def validate_response_type(client_id, response_type, client, request, *args, **kwargs):
    return (
      # XXX: restrict response types per client ?
      response_type in ('code', 'token')
    )

  @staticmethod
  def validate_scopes(client_id, scopes, client, request, *args, **kwargs):
    return not {
      x
      for x in scopes
      # oauthlib inserts an empty-string as scope when no scope is provided
      # ignore it here
      if x
    }.difference(
      client.erp5_client_value.getOauth2ScopeList(),
    )

  @staticmethod
  def validate_user(*args, **kw):
    # This method is only needed for password authentication.
    # This is not implemented (yet ?), as this requires calling into PAS which will probably be quit complex.
    raise RuntimeError

  def is_pkce_required(self, client_id, request):
    return request.client.erp5_client_value.isProofKeyForCodeExchangeRequired()

  def get_code_challenge(self, code, request):
    return request.user.erp5_session_value.getCodeChallenge()

  def get_code_challenge_method(self, code, request):
    return request.user.erp5_session_value.getCodeChallengeMethod()

def _callEndpoint(endpoint, self, REQUEST):
  """
  Convert a Zope HTTPRequest into oauthlib endpoint handler method arguments,
  call given endpoint method with them, and return its production (header_dict,
  body, status).
  """
  environ = REQUEST.environ
  other = REQUEST.other
  request_header_dict = {
    x[5:]: y
    for x, y in six.iteritems(environ)
    if x.startswith('HTTP_')
  }
  content_type = REQUEST.getHeader('CONTENT_TYPE')
  if content_type is not None:
    request_header_dict['CONTENT_TYPE'] = content_type
  # If this is a POST without content-type, assume urlencoded.
  # See cgi.FieldStorage, which has a similar fallback and is used by
  # Zope HTTPRequest. And do it *after* copying received header verbatim,
  # only for purposes internal to this function.
  if content_type is None and environ['REQUEST_METHOD'] == 'POST':
    content_type = 'application/x-www-form-urlencoded'
  if REQUEST._auth:
    request_header_dict['AUTHORIZATION'] = REQUEST._auth
  # There is no way in oauthlib to propagate CGI-style environment,
  # but we need this piece of information to validate client IP.
  # So hijack X_FORWARDED_FOR (overwriting the actual header if
  # present, as Zope already extracted the correct IP as we *should*
  # not have to care about intermediate proxies).
  request_header_dict['X_FORWARDED_FOR'] = REQUEST.getClientAddr()
  request_body = REQUEST.get('BODY')
  if request_body is None and content_type == 'application/x-www-form-urlencoded':
    # XXX: very imperfect, but should be good enough for OAuth2 usage:
    # no standard OAuth2 POST field should be marshalled by Zope.
    request_body = urlencode([
      (x, y)
      for x, y in six.iteritems(REQUEST.form)
      if isinstance(y, six.text_type)
    ])
  uri = other.get('URL', '')
  query_string = environ.get('QUERY_STRING')
  if query_string:
    uri += '?' + query_string
  return endpoint(
    self,
    request_validator=_ERP5RequestValidator(
      authorisation_server_connector_value=self,
    ),
    REQUEST=REQUEST,
  )(
    uri=uri,
    http_method=environ.get('REQUEST_METHOD'),
    body=request_body,
    headers=request_header_dict,
  )

def _handleOAuth2Error(RESPONSE, exc):
  # Setup an OAuth2-compliant error response.
  # Lock status and body, so WSGI does not tamper them later.
  RESPONSE.setStatus(exc.status_code, lock=True)
  RESPONSE.setHeader('Content-Type', 'application/json')
  RESPONSE.setBody(exc.json, lock=True)

# A minimal set of headers which must not be set on an HTTPResponse using addHeader,
# but must be set using setHeader instead because HTTPResponse treat them specially
# (ex: modifies them while rendering the final response form).
_SPECIAL_HEADER_NAME_SET = (
  'content-type',
  'content-length',
)
def _setupZopeResponse(RESPONSE, status, header_item_list, body):
  RESPONSE.setStatus(status, lock=True)
  for key, value in header_item_list:
    (
      RESPONSE.setHeader
      if key.lower() in _SPECIAL_HEADER_NAME_SET else
      RESPONSE.addHeader
    )(key, value)
  return body

def _wrapOAuth2Endpoint(func):
  """
  Wrap an oauthlib endpoint, adapting for ZPublisher request and response.

  func is expected to return a callable whose signature is:
  (uri, http_method, body, headers) -> (header_dict, body, status)
  Return value has a different signature:
  (REQUEST, RESPONSE) -> body
  It mutates RESPONSE to set headers and status.
  """
  @wraps(func)
  def wrapper(self, REQUEST, RESPONSE):
    try:
      header_dict, body, status = _callEndpoint(
        endpoint=func,
        self=self,
        REQUEST=REQUEST,
      )
    except OAuth2Error as exc:
      _handleOAuth2Error(RESPONSE, exc)
      # re-raise exception so Zope aborts transaction and logs the error.
      raise
    except Exception:
      _handleOAuth2Error(RESPONSE, ServerError())
      # re-raise exception so Zope aborts transaction and logs the real error.
      raise
    return _setupZopeResponse(
      RESPONSE=RESPONSE,
      status=status,
      header_item_list=header_dict.items(),
      body=body,
    )
  return wrapper

def _wrapOAuth2HTMLEndpoint(func):
  """
  wrap an oauthlib endoint which returns HTML, or otherwise interacts with a browser
  (rather than a dedicated OAuth2 client), adapting for ZPublisher request.
  """
  @wraps(func)
  def wrapper(self, REQUEST, RESPONSE):
    try:
      header_item_list, body, status = _callEndpoint(
        endpoint=func,
        self=self,
        REQUEST=REQUEST,
      )
    except OAuth2Error as exc:
      # Lock status: oauthlib can tell if this error should be a 4xx or a 5xx,
      # while the error renderer will probably not be able to understand that.
      RESPONSE.setStatus(exc.status_code, lock=True)
      raise
    return _setupZopeResponse(
      RESPONSE=RESPONSE,
      status=status,
      header_item_list=header_item_list,
      body=body,
    )
  return wrapper

class OAuth2AuthorisationServerConnector(XMLObject):
  meta_type = 'OAuth2 Authorisation Server Connector'
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Tuple of 4-tuples:
  # - unix timestamp at which the key was generated, for expiration purposes
  # - signature algorithm
  # - secret key
  # - public key
  __access_token_key_list = ()
  # Tuple of 3-tuples:
  # - unix timestamp at which the key was generated, for expiration purposes
  # - signature algorithm
  # - symetric key (secret)
  __refresh_token_key_list = ()
  # Tuple of 2-tuples:
  # - unix timestamp at which the key was generated, for expiration purposes
  # - fernet key (secret)
  __login_retry_key_list = ()

  def __getAccessTokenKeyList(self):
    result = self.__access_token_key_list
    if not result or result[0][1] != self.getAccessTokenAlgorithm():
      self.renewTokenSecret()
      result = self.__access_token_key_list
      assert result
    return result

  def __getRefreshTokenKeyList(self):
    result = self.__refresh_token_key_list
    if not result or result[0][1] != self.getRefreshTokenAlgorithm():
      self.renewTokenSecret()
      result = self.__refresh_token_key_list
      assert result
    return result

  def __getLoginRetryURLMultiFernet(self):
    key_list = self.__login_retry_key_list
    if not key_list:
      self.renewTokenSecret()
      key_list = self.__login_retry_key_list
    return fernet.MultiFernet([
      fernet.Fernet(key)
      for _, key in key_list
    ])

  #
  #   OAuth2 Endpoints: standard, implemented via oauthlib
  #
  security.declarePublic('authorize')
  @_wrapOAuth2HTMLEndpoint
  def authorize(self, request_validator, REQUEST):
    """
    OAuth2 authorisation endpoint
    https://tools.ietf.org/html/rfc6749#section-4.1.1

    GET requests get authentication forms.
    POST requests get an OAuth2 authorisation response (which normally is
    a redirection to redirect_uri augmented with an authorisation code).

    Only response_type="code" is supported.
    Only Zope-based request authentication is supported
    (ex: "Authorization: Basic ..." request header).
    """
    multi_fernet = self.__getLoginRetryURLMultiFernet()
    # Retrieve posted field, validate signature and extract the url.
    try:
      login_retry_url = multi_fernet.decrypt(REQUEST.form['login_retry_url'])
    except (fernet.InvalidToken, TypeError, KeyError):
      # No login_retry_url provided or its value is unusable: if this is a GET
      # request (trying to display a login form), use the current URL.
      if REQUEST.environ['REQUEST_METHOD'] in ('GET', 'HEAD'):
        login_retry_url = REQUEST.other['ACTUAL_URL']
        query_string = REQUEST.environ['QUERY_STRING']
        if query_string:
          login_retry_url += '?' + query_string
      else:
        login_retry_url = None
    def getSignedLoginRetryUrl():
      if login_retry_url is None:
        return None
      return multi_fernet.encrypt(login_retry_url)
    return _ERP5AuthorisationEndpoint(
      server_connector_path=self.getPath(),
      zope_request=REQUEST,
      login_retry_url=login_retry_url,
      getSignedLoginRetryUrl=getSignedLoginRetryUrl,
      default_response_type='code',
      default_token_type=BearerToken(
        request_validator=request_validator,
      ),
      response_types={
        'code': AuthorizationCodeGrant(
          request_validator=request_validator,
        ),
      },
    ).create_authorization_response

  security.declarePrivate('authorizeLocal')
  def authorizeLocal(self, REQUEST, RESPONSE, query_list, login_retry_url):
    """
    OAuth2 authorisation endpoint for a local resource server.

    Allows providing an unsigned login_retry_url and triggering the first
    authentication attempt.
    """
    method = REQUEST.environ['REQUEST_METHOD']
    assert method in ('GET', 'HEAD')
    with substituteRequest(
      context=self,
      request=REQUEST,
      method=method,
      query_list=query_list + [(
        'login_retry_url',
        self.__getLoginRetryURLMultiFernet().encrypt(login_retry_url),
      )],
    ) as inner_request:
      # pylint: disable=unexpected-keyword-arg, no-value-for-parameter
      return self.authorize(
        REQUEST=inner_request,
        RESPONSE=inner_request.RESPONSE,
      )
      # pylint: enable=unexpected-keyword-arg, no-value-for-parameter

  security.declarePublic('token')
  @_wrapOAuth2Endpoint
  def token(self, request_validator, REQUEST):
    """
    OAuth2 token endpoint
    https://tools.ietf.org/html/rfc6749#section-4.1.3

    - authorization_code (standard)
    - refresh_token (standard)
    - urn:uuid:15a68f81-dbce-4ddd-bfcb-a81f25359cf2
      Zope-based request authentication (ex: "Authorization: Basic ..."
      request header).
    """
    now = int(time())
    def getAccessTokenLifespan(request):
      session_value = request.user.erp5_session_value
      # Note: validating the session (to switch it from Access Code mode to a proper Session) changes
      # its expiration date, and oauthlib (as of this writing) calls "expires_in" before generating
      # the token. So validate the session here, as it's called from "expires_in".
      self._validateSessionValue(session_value)
      session_remaining_lifespan = session_value.getPolicyExpirationDate()
      with super_user():
        user_value = session_value.getSourceSectionValue()
      if user_value is not None:
        getNextSecurityChangeDate = user_value.getTypeBasedMethod('getNextSecurityChangeDate')
        if getNextSecurityChangeDate is not None:
          with super_user():
            security_change_date = getNextSecurityChangeDate()
          if security_change_date is not None:
            if session_remaining_lifespan is None:
              session_remaining_lifespan = security_change_date
            else:
              session_remaining_lifespan = min(session_remaining_lifespan, security_change_date)
      new_lifespan = request.client.erp5_client_value.getAccessTokenLifespan()
      if session_remaining_lifespan is None:
        return new_lifespan
      return min(session_remaining_lifespan.timeTime() - now, new_lifespan)
    # Note: keeping these functions local, as no other part of the code
    # should have any business building tokens.
    def generateAccessToken(request):
      session_value = request.user.erp5_session_value
      # Note: this call should not be necessary if "getAccessTokenLifespan" is called before us.
      # Call order is not documented, and this call is basically free once validated, so let's do it.
      self._validateSessionValue(session_value)
      with super_user():
        user_value = session_value.getSourceSectionValue()
      user_id = (
        session_value.getSourceSectionFreeText()
        if user_value is None else
        user_value.getUserId()
      )
      portal = self.getPortalObject()
      with ERP5GroupManager_disableCache():
        user = portal.acl_users.getUserById(user_id)
      if user is None:
        # User is not found within portal.acl_user, try zope root's.
        # XXX: is there a unified way of looking a user up by id ?
        # aq_inner because we explicitly want to escape the ERP5Site, so we must get rid of acquisition wrapper trickery, like WebSites.
        user = portal.aq_inner.aq_parent.acl_users.getUserById(user_id)
      caption = None
      with super_user():
        source_administration_value = session_value.getSourceAdministrationValue()
      if source_administration_value is not None:
        getUserCaption = source_administration_value.getTypeBasedMethod('getUserCaption')
        if getUserCaption is not None:
          with super_user():
            caption = getUserCaption()
      if caption is None:
        caption = session_value.getSourceAdministrationFreeText()
      _, algorithm, private_key, _ = self.__getAccessTokenKeyList()[0]
      return jwt.encode(
        {
          'exp': now + getAccessTokenLifespan(request),
          'iss': request.client.client_id,
          JWT_CLAIM_NETWORK_LIST_KEY: session_value.getNetworkList(),
          JWT_PAYLOAD_KEY: encodeAccessTokenPayload({
            JWT_PAYLOAD_CLIENT_REFERENCE_KEY: request.client.erp5_client_value.getReference(),
            JWT_PAYLOAD_AUTHORISATION_SESSION_ID_KEY: session_value.getId(),
            JWT_PAYLOAD_AUTHORISATION_SESSION_VERSION_KEY: session_value.getIntIndex(),
            JWT_PAYLOAD_USER_ID_KEY: user_id,
            JWT_PAYLOAD_USER_CAPTION_KEY: caption,
            JWT_PAYLOAD_ROLE_LIST_KEY: user.getRoles(),
            JWT_PAYLOAD_GROUP_LIST_KEY: getattr(
              user,
              'getGroups',
              lambda: (),
            )(),
            JWT_PAYLOAD_SCOPE_LIST_KEY: session_value.getOauth2ScopeList(),
          }),
        },
        key=private_key,
        algorithm=algorithm,
      )
    def generateRefreshToken(request):
      session_value = request.user.erp5_session_value
      expiration_timestamp = now + request.client.erp5_client_value.getRefreshTokenLifespan()
      session_expiration_date = session_value.getPolicyExpirationDate()
      if session_expiration_date is not None:
        expiration_timestamp = min(
          expiration_timestamp,
          int(session_expiration_date.timeTime()),
        )
      session_refresh_token_expiration_date = session_value.getRefreshTokenExpirationDate()
      if (
        session_refresh_token_expiration_date is None or
        session_refresh_token_expiration_date < DateTime(expiration_timestamp)
      ):
        session_value.setRefreshTokenExpirationDate(DateTime(expiration_timestamp))
      _, algorithm, symetric_key = self.__getRefreshTokenKeyList()[0]
      return jwt.encode(
        {
          'exp': expiration_timestamp,
          'iss': request.client.client_id,
          'iat': now,
          JWT_CLAIM_NETWORK_LIST_KEY: session_value.getNetworkList(),
          JWT_PAYLOAD_KEY: {
            JWT_PAYLOAD_AUTHORISATION_SESSION_ID_KEY: session_value.getId(),
          },
        },
        key=symetric_key,
        algorithm=algorithm,
      )
    return TokenEndpoint(
      default_grant_type='authorization_code',
      default_token_type=BearerToken(
        request_validator=request_validator,
        token_generator=generateAccessToken,
        expires_in=getAccessTokenLifespan,
        refresh_token_generator=generateRefreshToken,
      ),
      grant_types={
        'refresh_token': RefreshTokenGrant(
          request_validator=request_validator,
        ),
        'authorization_code': AuthorizationCodeGrant(
          request_validator=request_validator,
        ),
      },
    ).create_token_response

  security.declarePublic('revoke')
  @_wrapOAuth2Endpoint
  def revoke(self, request_validator, REQUEST):
    """
    OAuth2 revocation endpoint
    https://tools.ietf.org/html/rfc7662
    """
    return RevocationEndpoint(
      request_validator=request_validator,
      supported_token_types=('access_token', 'refresh_token'),
      enable_jsonp=False,
    ).create_revocation_response

  security.declarePublic('introspect')
  @_wrapOAuth2Endpoint
  def introspect(self, request_validator, REQUEST):
    """
    OAuth2 introspection endpoint
    https://tools.ietf.org/html/rfc7009
    """
    return IntrospectEndpoint(
      request_validator=request_validator,
      supported_token_types=('access_token', 'refresh_token'),
    ).create_introspect_response

  # XXX: more access points ?

  #
  #   oauthlib-style API: "request" argument is oauthlib-style request
  #

  def _getAccessTokenDict(self, value, request):
    for _, algorithm, _, public_key in self.__getAccessTokenKeyList():
      try:
        token_dict = jwt.decode(
          value,
          key=public_key,
          algorithms=[algorithm],
          issuer=request.client.client_id,
          options={
            'require_exp': True,
            'verify_exp': True,
            'verify_iss': True,
            'verify_signature': True,
          },
        )
        self._checkCustomTokenPolicy(token_dict, request)
      except jwt.InvalidTokenError:
        continue
      else:
        token_dict[JWT_PAYLOAD_KEY] = decodeAccessTokenPayload(
          ensure_ascii(token_dict[JWT_PAYLOAD_KEY]),
        )
        return token_dict
    raise

  def _getRefreshTokenDict(self, value, request):
    for _, algorithm, symetric_key in self.__getRefreshTokenKeyList():
      try:
        token_dict = jwt.decode(
          value,
          key=symetric_key,
          algorithms=[algorithm],
          issuer=request.client.client_id,
          options={
            'require_exp': True,
            'verify_exp': True,
            'verify_iss': True,
            'verify_signature': True,
          },
        )
        self._checkCustomTokenPolicy(token_dict, request)
      except jwt.InvalidTokenError:
        continue
      else:
        return token_dict
    raise

  def _checkCustomTokenPolicy(self, token, request):
    """
    Validate non-standard jwt claims against request.
    """
    if not isAddressInNetworkList(
      address=request.headers['X_FORWARDED_FOR'].decode('utf-8'),
      network_list=token[JWT_CLAIM_NETWORK_LIST_KEY],
    ):
      raise jwt.InvalidTokenError

  security.declarePrivate('getAccessTokenIntrospectionDict')
  def getAccessTokenIntrospectionDict(self, token, request):
    access_token_dict = self._getAccessTokenDict(token, request)
    access_token_payload_dict = access_token_dict[JWT_PAYLOAD_KEY]
    return {
      'scope': ' '.join(access_token_payload_dict[JWT_PAYLOAD_SCOPE_LIST_KEY]),
      'client_id': access_token_dict['iss'],
      'username': access_token_payload_dict[JWT_PAYLOAD_USER_CAPTION_KEY],
      'token_type': 'bearer',
      'exp': access_token_dict['exp'],
      'sub': access_token_payload_dict[JWT_PAYLOAD_USER_ID_KEY],
      # XXX: More ? Like, group list and global role list ?
    }

  security.declarePrivate('getRefreshTokenIntrospectionDict')
  def getRefreshTokenIntrospectionDict(self, token, request):
    refresh_token_dict = self._getRefreshTokenDict(token, request)
    return {
      'client_id': refresh_token_dict['iss'],
      'token_type': 'bearer',
      'exp': refresh_token_dict['exp'],
      'iat': refresh_token_dict['iat'],
    }

  security.declarePrivate('getAccessTokenClientId')
  def getAccessTokenClientId(self, value, request):
    """
    Extracts client ID from given Access Token.
    DOES NOT VALIDATE TOKEN CLAIMS (but does validate the signature)
    """
    # Validate signature to avoid parsing potentially mallicious user input.
    # Do not validate claims, as this method is called to guess the client when revoking a session.
    for _, algorithm, _, public_key in self.__getAccessTokenKeyList():
      try:
        token_dict = jwt.decode(
          value,
          key=public_key,
          algorithms=[algorithm],
          options={
            'verify_exp': False,
            'verify_signature': True,
          },
        )
        self._checkCustomTokenPolicy(token_dict, request)
      except jwt.InvalidTokenError:
        continue
      else:
        return token_dict['iss']
    raise

  security.declarePrivate('getRefreshTokenClientId')
  def getRefreshTokenClientId(self, value, request):
    """
    Extracts client ID from given Refresh Token.
    DOES NOT VALIDATE TOKEN CLAIMS (but does validate the signature)
    """
    # Validate signature to avoid parsing potentially mallicious user input.
    # Do not validate claims, as this method is called to guess the client when revoking a session.
    for _, algorithm, symetric_key in self.__getRefreshTokenKeyList():
      try:
        token_dict = jwt.decode(
          value,
          key=symetric_key,
          algorithms=[algorithm],
          options={
            'verify_exp': False,
            'verify_signature': True,
          },
        )
        self._checkCustomTokenPolicy(token_dict, request)
      except jwt.InvalidTokenError:
        continue
      else:
        return token_dict['iss']
    raise

  def _getSessionValueFromTokenDict(self, token_dict):
    session_value = self._getSessionValue(
      token_dict[JWT_PAYLOAD_KEY][
        JWT_PAYLOAD_AUTHORISATION_SESSION_ID_KEY
      ].encode('utf-8'),
      'validated',
    )
    if session_value is not None:
      with super_user():
        source_id = session_value.getSourceId()
      if source_id == token_dict['iss']:
        return session_value

  security.declarePrivate('getSessionValueFromAccessToken')
  def getSessionValueFromAccessToken(self, token, request):
    """
    Does not check access permission.
    """
    try:
      token_dict = self._getAccessTokenDict(token, request)
    except jwt.InvalidTokenError:
      return
    return self._getSessionValueFromTokenDict(token_dict=token_dict)

  security.declarePrivate('getSessionValueFromRefreshToken')
  def getSessionValueFromRefreshToken(self, token, request):
    """
    Does not check access permission.
    """
    try:
      token_dict = self._getRefreshTokenDict(token, request)
    except jwt.InvalidTokenError:
      return
    return self._getSessionValueFromTokenDict(token_dict=token_dict)

  security.declarePrivate('isRefreshTokenRotationNeeded')
  def isRefreshTokenRotationNeeded(self, refresh_token, request):
    try:
      refresh_token_dict = self._getRefreshTokenDict(refresh_token, request)
    except jwt.InvalidTokenError:
      return False
    # XXX: allow refresh if exp - iat != getRefreshTokenLifespan (within some imprecision) ?
    return time() - refresh_token_dict['iat'] > self[refresh_token_dict['iss']].getRefreshTokenLifespanAccuracy()

  #
  #   Non-oauth2 methods, for use by ERP5 in the role of a resource server
  #

  security.declarePublic('getSessionVersion')
  def getSessionVersion(self, session_id, REQUEST=None, RESPONSE=None):
    """
    Returns the current version of the designated session, if this session exists and is valid.
    Otherwise, returns None.
    If published, the return value is json-encoded.

    session_id (string)
      The session id used when producing the Access Token being used to look this session up.
    """
    session_value = self._getSessionValue(session_id, 'validated')
    result = (
      None
      if session_value is None else
      session_value.getIntIndex()
    )
    if REQUEST is None:
      return result
    RESPONSE.setHeader('Cache-Control', 'no-store')
    RESPONSE.setHeader('Pragma', 'no-cache')
    RESPONSE.setHeader('content-type', 'application/json;charset=UTF-8')
    return json.dumps(result)

  security.declarePrivate('isRemote')
  def isRemote(self):
    return False

  #
  #   Session storage
  #

  def _getSessionContainerValue(self):
    """
    Abstract session storage document container.
    """
    return self.getPortalObject().session_module

  def _getSessionValue(self, session_id, expected_state):
    """
    Lookup session document.
    """
    container_value = self._getSessionContainerValue()
    try:
      session_value = container_value[session_id]
    except KeyError:
      return
    if (
      session_value.getPortalType() != 'OAuth2 Session' or
      expected_state != session_value.getValidationState()
    ):
      return
    # Note: care is taken when issuing tokens to not issue one valid for longer
    # than corresponding session. But this does not prevent the value on the
    # session from being altered later.
    expiration_date = session_value.getPolicyExpirationDate()
    if expiration_date is not None and expiration_date < DateTime():
      return
    return session_value

  def _newSession(self, **kw):
    with super_user():
      return self._getSessionContainerValue().newContent(
        portal_type='OAuth2 Session',
        **kw
      )

  security.declarePrivate('getSessionValueByAuthorisationCode')
  def getSessionValueByAuthorisationCode(self, code):
    """
    Retrieve the session corresponding to given code.
    """
    # XXX: use a non-draft state ?
    return self._getSessionValue(session_id=code, expected_state='draft')

  security.declarePrivate('invalidateAuthorisationCode')
  def invalidateAuthorisationCode(self, code):
    """
    Given session code has been used, make the session unusable (if it was still usable).
    """
    # XXX: session will still be usable if transaction fails to commit.
    # XXX: use a non-draft state ?
    session_value = self._getSessionValue(session_id=code, expected_state='draft')
    if session_value is not None:
      # Only do something if this session is still usable.
      # Otherwise, a token may have already taken over its control.
      with super_user():
        session_value.cancel()

  security.declarePrivate('createSession')
  def createSession(
    self,
    authorisation_code,
    request,
    client_value,
    redirect_uri,
    scope_list,
    code_challenge,
    code_challenge_method,
    network_address,
    user_agent,
  ):
    """
    Called when issuing an Authorisation Code.
    """
    user = getSecurityManager().getUser()
    user_value = user.getUserValue()
    getUserId = getattr(user_value, 'getUserId', None)
    kw = {}
    if user_value is None or getUserId is None:
      # Not an ERP5 user, fallback to a Zope user
      kw['source_section_free_text'] = user.getId()
      kw['source_administration_free_text'] = user.getUserName()
    else:
      assert getUserId() == user.getId()
      kw['source_section_value'] = user_value
      login_value = user.getLoginValue()
      if login_value is None:
        kw['source_administration_free_text'] = user.getUserName() # XXX: not the best
      else:
        kw['source_administration_value'] = login_value
    return self._newSession(
      id=authorisation_code,
      source_value=client_value,
      policy_expiration_date=DateTime(time() + client_value.getAuthorisationCodeLifespan()),
      redirect_uri=redirect_uri,
      oauth2_scope_list=scope_list,
      code_challenge=code_challenge,
      code_challenge_method=code_challenge_method,
      network_address=network_address,
      user_agent=user_agent,
      network_list=request.client.erp5_client_value.getNetworkList(),
      **kw
    )
    # XXX: use a non-draft state ?

  def _validateSessionValue(self, session_value):
    """
    Convert a session from its Authorisation Code persona (draft) to its token persona (validated).
    If the session is already validated, does nothing.
    """
    state = session_value.getValidationState()
    if state == 'draft':
      with super_user():
        session_value.validate()
        session_value.setRedirectUri(None)
        session_value.setCodeChallenge(None)
        session_value.setCodeChallengeMethod(None)
        session_value.setPolicyExpirationDate(None)
        with super_user():
          session_value.OAuth2Session_applyPolicyForExpirationDate()
    elif state != 'validated':
      raise ValueError

  #
  #   Folder API
  #

  def _generateUUID4HexId(self):
    return uuid.uuid4().hex

  id_generator = '_generateUUID4HexId'

  def _postCopy(self, container, op=0):
    """
    Erase key material when we are a copy.

    Because "private" means "private".
    """
    if op == 1: # We are a copy
      self.renewTokenSecret(revoke_until=float('inf'))
    super(OAuth2AuthorisationServerConnector, self)._postCopy(container, op)

  #
  #   Key material API
  #

  security.declarePublic('getSymetricSignatureAlgorithmList')
  def getSymetricSignatureAlgorithmList(self):
    """
    For UI use.
    """
    return [
      x[0]
      for x in sorted(
        six.iteritems(_SIGNATURE_ALGORITHM_TO_KEY_BYTE_LENGTH_DICT),
        key=lambda x: x[1],
      )
    ]

  security.declarePublic('getAsymetricSignatureAlgorithmList')
  def getAsymetricSignatureAlgorithmList(self):
    """
    For UI use.
    """
    return [
      'RS256',
      'RS384',
      'RS512',
    ]

  security.declarePublic('getAccessTokenSignatureAlgorithmAndPublicKeyList')
  def getAccessTokenSignatureAlgorithmAndPublicKeyList(self, RESPONSE=None):
    """
    Return a tuple of 2-tuples:
    - JWT signature algorithm name
    - public key (PEM-encoded)
    for validating Access Tokens.
    If published, the return value is json-encoded.
    """
    result = tuple(
      (signature_algorithm, public_key)
      for _, signature_algorithm, _, public_key in self.__getAccessTokenKeyList()
    )
    if RESPONSE is None:
      return result
    RESPONSE.setHeader('Cache-Control', 'no-store')
    RESPONSE.setHeader('Pragma', 'no-cache')
    RESPONSE.setHeader('content-type', 'application/json;charset=UTF-8')
    return json.dumps(result)

  security.declareProtected(Permissions.ModifyPortalContent, 'renewTokenSecret')
  def renewTokenSecret(self, revoke_until=0.0):
    """
    Start signing tokens with new keys.

    revoke_until (float)
      Revoke keys older than this unix timestamp, making all tokens signed by
      these keys invalid.
      Use float('inf') to revoke all existing keys.
    """
    now = time()
    access_token_signature_algorithm = self.getAccessTokenAlgorithm()
    # XXX: Other values are not implemented. These must be asymetric ciphers.
    assert access_token_signature_algorithm in ('RS256', 'RS384', 'RS512')
    private_key = rsa.generate_private_key(
      public_exponent=65537, # Standard, other values strongly discouraged.
      key_size=2048, # XXX: good enough ? Expose as property ?
      backend=_DEFAULT_BACKEND,
    )
    self.__access_token_key_list = (
      (
        now,
        access_token_signature_algorithm,
        ensure_ascii(private_key.private_bytes(
          encoding=Encoding.PEM,
          format=PrivateFormat.PKCS8,
          encryption_algorithm=NoEncryption(),
        )),
        ensure_ascii(private_key.public_key().public_bytes(
          encoding=Encoding.PEM,
          format=PublicFormat.SubjectPublicKeyInfo,
        )),
      ),
    ) + tuple(
      x
      for x in self.__access_token_key_list
      if x[0] > revoke_until
    )
    refresh_token_signature_algorithm = self.getRefreshTokenAlgorithm()
    self.__refresh_token_key_list = (
      (
        now,
        refresh_token_signature_algorithm,
        # XXX: Other values are not implemented. These must be symetric ciphers,
        # and as of this writing no other is supported by pyjwt.
        urandom(_SIGNATURE_ALGORITHM_TO_KEY_BYTE_LENGTH_DICT[refresh_token_signature_algorithm]),
      ),
    ) + tuple(
      x
      for x in self.__refresh_token_key_list
      if x[0] > revoke_until
    )
    self.__login_retry_key_list = (
      (
        now,
        fernet.Fernet.generate_key(),
      ),
    ) + tuple(
      x
      for x in self.__login_retry_key_list
      if x[0] > revoke_until
    )
