##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Aurelien Calonne <aurel@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################


from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5 import _dtmldir
from zLOG import LOG

import time
import cgi
import urllib
import random
import urlparse
import hmac
import binascii
from hashlib import sha1


CONSUMER_KEY = "e90f5a97ec5cecd1"
CONSUMER_SECRET = "9b5f6c60bb007b24"
VERSION = "1.0"
SIGNATURE_METHOD = 'PLAINTEXT'
TIMESTAMP_THRESHOLD = 60 # In seconds
HTTP_METHOD = 'GET'

base_url = "http://localhost:7080/erp5/portal_oauth"

REQUEST_TOKEN_URL = '%s/request_token' %(base_url,)
ACCESS_TOKEN_URL = '%s/access_token' %(base_url,)
AUTHORIZATION_URL = '%s/authorize' %(base_url,)
AUTHORIZATION_VERIFIED_URL = '%s/authorizationVerified' %(base_url,)
#CALLBACK_URL = '%s/request_token_ready' %(base_url,)
RESOURCE_URL = '%s/photos' %(base_url,)
REALM = '%s' %(base_url,)
VERIFIER = 'verifier'

class OAuthError(RuntimeError):
    """Generic exception class."""
    def __init__(self, message='OAuth error occured.'):
        self.message = message
def build_authenticate_header(realm=''):
    """Optional WWW-Authenticate header (401 error)"""
    return {'WWW-Authenticate': 'OAuth realm="%s"' % realm}

def escape(s):
    """Escape a URL including any /."""
    return urllib.quote(s, safe='~')

def _utf8_str(s):
    """Convert unicode to utf-8."""
    if isinstance(s, unicode):
        return s.encode("utf-8")
    else:
        return str(s)

def generate_timestamp():
    """Get seconds since epoch (UTC)."""
    return int(time.time())

def generate_nonce(length=8):
    """Generate pseudorandom number."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])

def generate_verifier(length=8):
    """Generate pseudorandom number."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])

class OAuthConsumer(object):
    """Consumer of OAuth authentication.

    OAuthConsumer is a data type that represents the identity of the Consumer
    via its shared secret with the Service Provider.

    """
    key = None
    secret = None

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret


class OAuthToken(object):
    """OAuthToken is a data type that represents an End User via either an access
    or request token.

    key -- the token
    secret -- the token secret

    """
    key = None
    secret = None
    callback = None
    callback_confirmed = None
    verifier = None

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def set_callback(self, callback):
        self.callback = callback
        self.callback_confirmed = 'true'

    def set_verifier(self, verifier=None):
        if verifier is not None:
            self.verifier = verifier
        else:
            self.verifier = generate_verifier()

    def get_callback_url(self):
        if self.callback and self.verifier:
            # Append the oauth_verifier.
            parts = urlparse.urlparse(self.callback)
            scheme, netloc, path, params, query, fragment = parts[:6]
            if query:
                query = '%s&oauth_verifier=%s' % (query, self.verifier)
            else:
                query = 'oauth_verifier=%s' % self.verifier
            # Append the oauth token
            query = '%s&oauth_token=%s' % (query, self.key)
            return urlparse.urlunparse((scheme, netloc, path, params,
                query, fragment))
        return self.callback

    def to_string(self):
        data = {
            'oauth_token': self.key,
            'oauth_token_secret': self.secret,
        }
        if self.callback_confirmed is not None:
            data['oauth_callback_confirmed'] = self.callback_confirmed
        return urllib.urlencode(data)

    def from_string(s):
        """ Returns a token from something like:
        oauth_token_secret=xxx&oauth_token=xxx
        """
        params = cgi.parse_qs(s, keep_blank_values=False)
        key = params['oauth_token'][0]
        secret = params['oauth_token_secret'][0]
        token = OAuthToken(key, secret)
        try:
            token.callback_confirmed = params['oauth_callback_confirmed'][0]
        except KeyError:
            pass # 1.0, no callback confirmed.
        return token
    from_string = staticmethod(from_string)

    def __str__(self):
        return self.to_string()

class OAuthRequest(object):
    """OAuthRequest represents the request and can be serialized.

    OAuth parameters:
        - oauth_consumer_key
        - oauth_token
        - oauth_signature_method
        - oauth_signature
        - oauth_timestamp
        - oauth_nonce
        - oauth_version
        - oauth_verifier
        ... any additional parameters, as defined by the Service Provider.
    """
    parameters = None # OAuth parameters.
    http_method = HTTP_METHOD
    http_url = None
    version = VERSION

    def __init__(self, http_method=HTTP_METHOD, http_url=None, parameters=None):
        self.http_method = http_method
        self.http_url = http_url
        self.parameters = parameters or {}

    def set_parameter(self, parameter, value):
        self.parameters[parameter] = value

    def get_parameter(self, parameter):
        try:
            return self.parameters[parameter]
        except:
            raise OAuthError('Parameter not found: %s' % parameter)

    def _get_timestamp_nonce(self):
        return self.get_parameter('oauth_timestamp'), self.get_parameter(
            'oauth_nonce')

    def get_nonoauth_parameters(self):
        """Get any non-OAuth parameters."""
        parameters = {}
        for k, v in self.parameters.iteritems():
            # Ignore oauth parameters.
            if k.find('oauth_') < 0:
                parameters[k] = v
        return parameters

    def to_header(self, realm=''):
        """Serialize as a header for an HTTPAuth request."""
        auth_header = 'OAuth realm="%s"' % realm
        # Add the oauth parameters.
        if self.parameters:
            for k, v in self.parameters.iteritems():
                if k[:6] == 'oauth_':
                    auth_header += ', %s="%s"' % (k, escape(str(v)))
        return {'Authorization': auth_header}

    def to_postdata(self):
        """Serialize as post data for a POST request."""
        return '&'.join(['%s=%s' % (escape(str(k)), escape(str(v))) \
            for k, v in self.parameters.iteritems()])

    def to_url(self):
        """Serialize as a URL for a GET request."""
        return '%s?%s' % (self.get_normalized_http_url(), self.to_postdata())

    def get_normalized_parameters(self):
        """Return a string that contains the parameters that must be signed."""
        params = self.parameters
        try:
            # Exclude the signature if it exists.
            del params['oauth_signature']
        except:
            pass
        # Escape key values before sorting.
        key_values = [(escape(_utf8_str(k)), escape(_utf8_str(v))) \
            for k,v in params.items()]
        # Sort lexicographically, first after key, then after value.
        key_values.sort()
        # Combine key value pairs into a string.
        return '&'.join(['%s=%s' % (k, v) for k, v in key_values])

    def get_normalized_http_method(self):
        """Uppercases the http method."""
        return self.http_method.upper()

    def get_normalized_http_url(self):
        """Parses the URL and rebuilds it to be scheme://host/path."""
        parts = urlparse.urlparse(self.http_url)
        scheme, netloc, path = parts[:3]
        # Exclude default port numbers.
        if scheme == 'http' and netloc[-3:] == ':80':
            netloc = netloc[:-3]
        elif scheme == 'https' and netloc[-4:] == ':443':
            netloc = netloc[:-4]
        return '%s://%s%s' % (scheme, netloc, path)

    def sign_request(self, signature_method, consumer, token):
        """Set the signature parameter to the result of build_signature."""
        # Set the signature method.
        self.set_parameter('oauth_signature_method',
            signature_method.get_name())
        # Set the signature.
        self.set_parameter('oauth_signature',
            self.build_signature(signature_method, consumer, token))

    def build_signature(self, signature_method, consumer, token):
        """Calls the build signature method within the signature method."""
        return signature_method.build_signature(self, consumer, token)

    def from_request(http_method, http_url, headers=None, parameters=None,
            query_string=None):
        """Combines multiple parameter sources."""
        if parameters is None:
            parameters = {}

        # Headers
        if headers:
            auth_header = headers
            # Check that the authorization header is OAuth.
            if auth_header[:6] == 'OAuth ':
                auth_header = auth_header[6:]
                try:
                    # Get the parameters from the header.
                    header_params = OAuthRequest._split_header(auth_header)
                    parameters.update(header_params)
                except:
                    raise OAuthError('Unable to parse OAuth parameters from '
                        'Authorization header.')

        # GET or POST query string.
        if query_string:
            query_params = OAuthRequest._split_url_string(query_string)
            parameters.update(query_params)

        # URL parameters.
        param_str = urlparse.urlparse(http_url)[4] # query
        url_params = OAuthRequest._split_url_string(param_str)
        parameters.update(url_params)

        if parameters:
            return OAuthRequest(http_method, http_url, parameters)

        return None
    from_request = staticmethod(from_request)

    def from_consumer_and_token(oauth_consumer, token=None,
            callback=None, verifier=None, http_method=HTTP_METHOD,
            http_url=None, parameters=None):
        if not parameters:
            parameters = {}

        defaults = {
            'oauth_consumer_key': oauth_consumer.key,
            'oauth_timestamp': generate_timestamp(),
            'oauth_nonce': generate_nonce(),
            'oauth_version': OAuthRequest.version,
        }

        defaults.update(parameters)
        parameters = defaults

        if token:
            parameters['oauth_token'] = token.key
            if token.callback:
                parameters['oauth_callback'] = token.callback
            # 1.0a support for verifier.
            if verifier:
                parameters['oauth_verifier'] = verifier
        elif callback:
            # 1.0a support for callback in the request token request.
            parameters['oauth_callback'] = callback

        return OAuthRequest(http_method, http_url, parameters)
    from_consumer_and_token = staticmethod(from_consumer_and_token)

    def from_token_and_callback(token, callback=None, http_method=HTTP_METHOD,
            http_url=None, parameters=None):
        if not parameters:
            parameters = {}

        parameters['oauth_token'] = token.key

        if callback:
            parameters['oauth_callback'] = callback

        return OAuthRequest(http_method, http_url, parameters)
    from_token_and_callback = staticmethod(from_token_and_callback)

    def _split_header(header):
        """Turn Authorization: header into parameters."""
        params = {}
        parts = header.split(',')
        for param in parts:
            # Ignore realm parameter.
            if param.find('realm') > -1:
                continue
            # Remove whitespace.
            param = param.strip()
            # Split key-value.
            param_parts = param.split('=', 1)
            # Remove quotes and unescape the value.
            params[param_parts[0]] = urllib.unquote(param_parts[1].strip('\"'))
        return params
    _split_header = staticmethod(_split_header)

    def _split_url_string(param_str):
        """Turn URL string into parameters."""
        parameters = cgi.parse_qs(param_str, keep_blank_values=False)
        for k, v in parameters.iteritems():
            parameters[k] = urllib.unquote(v[0])
        return parameters
    _split_url_string = staticmethod(_split_url_string)


class OAuthSignatureMethod(object):
    """A strategy class that implements a signature method."""
    def get_name(self):
        """-> str."""
        raise NotImplementedError

    def build_signature_base_string(self, oauth_request, oauth_consumer, oauth_token):
        """-> str key, str raw."""
        raise NotImplementedError

    def build_signature(self, oauth_request, oauth_consumer, oauth_token):
        """-> str."""
        raise NotImplementedError

    def check_signature(self, oauth_request, consumer, token, signature):
        built = self.build_signature(oauth_request, consumer, token)
        return built == signature

class OAuthSignatureMethod_HMAC_SHA1(OAuthSignatureMethod):

    def get_name(self):
        return 'HMAC-SHA1'

    def build_signature_base_string(self, oauth_request, consumer, token):
        sig = (
            escape(oauth_request.get_normalized_http_method()),
            escape(oauth_request.get_normalized_http_url()),
            escape(oauth_request.get_normalized_parameters()),
        )

        key = '%s&' % escape(consumer.secret)
        if token:
            key += escape(token.secret)
        raw = '&'.join(sig)
        return key, raw

    def build_signature(self, oauth_request, consumer, token):
        """Builds the base signature string."""
        key, raw = self.build_signature_base_string(oauth_request, consumer,
            token)

        # HMAC object.
        hashed = hmac.new(key, raw, sha1)

        # Calculate the digest base 64.
        return binascii.b2a_base64(hashed.digest())[:-1]


class OAuthSignatureMethod_PLAINTEXT(OAuthSignatureMethod):

    def get_name(self):
        return 'PLAINTEXT'

    def build_signature_base_string(self, oauth_request, consumer, token):
        """Concatenates the consumer key and secret."""
        sig = '%s&' % escape(consumer.secret)
        if token:
            sig = sig + escape(token.secret)
        return sig, sig

    def build_signature(self, oauth_request, consumer, token):
        key, raw = self.build_signature_base_string(oauth_request, consumer,
            token)
        return key


class OAuthTool(BaseTool):
  """
    OAuthTool is used to allow API authentification
  """
  title = 'OAuth Tool'
  id = 'portal_oauth'
  meta_type = 'ERP5 OAuth Tool'
  portal_type = 'OAuth Tool'
  allowed_types = ()

  # Declarative Security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.ManagePortal, 'manage_overview' )
  manage_overview = DTMLFile( 'explainOAuthTool', _dtmldir )
  signature_methods = {}

  def __init__(self, *args, **kw):
    self.signature_methods = PersistentMapping()
    self.add_signature_method(OAuthSignatureMethod_PLAINTEXT())
    self.add_signature_method(OAuthSignatureMethod_HMAC_SHA1())
    self.consumer = OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
    self.my_request_token = OAuthToken('requestkey', 'requestsecret')
    self.my_access_token = OAuthToken('accesskey', 'accesssecret')
    self.nonce = 'nonce'
    self.verifier = VERIFIER


  def add_signature_method(self, signature_method):
      self.signature_methods[signature_method.get_name()] = signature_method
      return self.signature_methods

  def fetch_request_token(self, oauth_request):
      """Processes a request_token request and returns the
      request token on success.
      """
      try:
          # Get the request token for authorization.
          token = self._get_token(oauth_request, 'request')
      except OAuthError:
          LOG("initial token request called", 300, "")
          # No token required for the initial token request.
          version = self._get_version(oauth_request)
          consumer = self._get_consumer(oauth_request)
          try:
              callback = self.get_callback(oauth_request)
          except OAuthError:
              callback = None # 1.0, no callback specified.
          self._check_signature(oauth_request, consumer, None)
          # Fetch a new token.
          if consumer.key == self.consumer.key:
            if callback:
                # want to check here if callback is sensible
                # for mock store, we assume it is
                LOG("setting callback method %s" %(callback), 300, "")
                self.my_request_token.set_callback(callback)
            token = self.my_request_token
          else:
            token = None

      return token

  def fetch_access_token(self, oauth_request):
      """Processes an access_token request and returns the
      access token on success.
      """
      version = self._get_version(oauth_request)
      consumer = self._get_consumer(oauth_request)
      try:
          verifier = self._get_verifier(oauth_request)
      except OAuthError:
          verifier = None
      # Get the request token.
      token = self._get_token(oauth_request, 'request')
      self._check_signature(oauth_request, consumer, token)

      if consumer.key == self.consumer.key and \
             token.key == self.my_request_token.key and \
             verifier == self.verifier:
        # want to check here if token is authorized
        # for mock store, we assume it is
        return self.my_access_token
      return None

  def verify_request(self, oauth_request):
      """Verifies an api call and checks all the parameters."""
      # -> consumer and token
      version = self._get_version(oauth_request)
      consumer = self._get_consumer(oauth_request)
      # Get the access token.
      token = self._get_token(oauth_request, 'access')
      self._check_signature(oauth_request, consumer, token)
      parameters = oauth_request.get_nonoauth_parameters()
      return consumer, token, parameters

  def authorize_token(self, token, user):
      """Authorize a request token."""
      if token.key == self.my_request_token.key:
        return self.my_request_token
      return None

  def get_callback(self, oauth_request):
      """Get the callback URL."""
      return oauth_request.get_parameter('oauth_callback')

  def build_authenticate_header(self, realm=''):
      """Optional support for the authenticate header."""
      return {'WWW-Authenticate': 'OAuth realm="%s"' % realm}

  def _get_version(self, oauth_request):
      """Verify the correct version request for this server."""
      try:
          version = oauth_request.get_parameter('oauth_version')
      except:
          version = VERSION
      if version and version != VERSION:
          raise OAuthError('OAuth version %s not supported.' % str(version))
      return version

  def _get_signature_method(self, oauth_request):
      """Figure out the signature with some defaults."""
      try:
          signature_method = oauth_request.get_parameter(
              'oauth_signature_method')
      except:
          signature_method = SIGNATURE_METHOD
      try:
          # Get the signature method object.
          signature_method = self.signature_methods[signature_method]
      except:
          signature_method_names = ', '.join(self.signature_methods.keys())
          raise OAuthError('Signature method %s not supported try one of the '
              'following: %s' % (signature_method, signature_method_names))

      return signature_method

  def _get_consumer(self, oauth_request):
      consumer_key = oauth_request.get_parameter('oauth_consumer_key')
      if consumer_key != self.consumer.key:
          raise OAuthError('Invalid consumer.')
      return self.consumer

  def _get_token(self, oauth_request, token_type='access'):
      """Try to find the token for the provided request token key."""
      token_field = oauth_request.get_parameter('oauth_token')
      token_attrib = getattr(self, 'my_%s_token' % token_type)
      if token_field == token_attrib.key:
          try:
              callback = self.get_callback(oauth_request)
          except OAuthError:
              callback = None # 1.0, no callback specified.
              LOG("setting callback method %s" %(callback), 300, "in _get_token")
          token_attrib.set_callback(callback)
          return token_attrib
      else:
          raise OAuthError('Invalid %s token: %s' % (token_type, token_field))

  def _get_verifier(self, oauth_request):
      return oauth_request.get_parameter('oauth_verifier')

  def _check_signature(self, oauth_request, consumer, token):
      timestamp, nonce = oauth_request._get_timestamp_nonce()
      self._check_timestamp(timestamp)
      self._check_nonce(consumer, token, nonce)
      signature_method = self._get_signature_method(oauth_request)
      try:
          signature = oauth_request.get_parameter('oauth_signature')
      except:
          raise OAuthError('Missing signature.')
      # Validate the signature.
      valid_sig = signature_method.check_signature(oauth_request, consumer,
          token, signature)
      if not valid_sig:
          key, base = signature_method.build_signature_base_string(
              oauth_request, consumer, token)
          raise OAuthError('Invalid signature. Expected signature base '
              'string: %s' % base)
      built = signature_method.build_signature(oauth_request, consumer, token)

  def _check_timestamp(self, timestamp):
      """Verify that timestamp is recentish."""
      timestamp = int(timestamp)
      now = int(time.time())
      lapsed = abs(now - timestamp)
      if lapsed > TIMESTAMP_THRESHOLD:
          raise OAuthError('Expired timestamp: given %d and now %s has a '
              'greater difference than threshold %d' %
              (timestamp, now, TIMESTAMP_THRESHOLD))

  def _check_nonce(self, consumer, token, nonce):
      """Verify that the nonce is uniqueish."""
      if token and consumer.key == self.consumer.key and \
             (token.key == self.my_request_token.key or token.key == self.my_access_token.key) \
             and nonce == self.nonce:
        raise OAuthError('Nonce already used: %s' % str(nonce))

  def send_oauth_error(self, err, REQUEST):
    """ return error """
    print err
    REQUEST.response.setStatus(status=401, reason=err)
    return REQUEST.response

  def call(self, REQUEST=None, **kw):
    """ this method handle all the call on the portal """

    path = REQUEST.getURL()
    headers = REQUEST._auth
    command = REQUEST['REQUEST_METHOD']
    parameters = REQUEST.form
    postdata = None
    LOG("-------call--------", 300, "\npath %s\nheader %s\ncommand %s\nparameters %s\n\nXXXXXXXXXXXXXXX" %(path, headers, command, parameters))
    # if command == "POST":
    #   import pdb
    #   pdb.set_trace()

    # construct the oauth request from the request parameters
    oauth_request = OAuthRequest.from_request(command, path, headers=headers, parameters=parameters, query_string=postdata)
    # request token
    if path.startswith(REQUEST_TOKEN_URL):
        try:
            # create a request token
            token = self.fetch_request_token(oauth_request)
            LOG("Return %s" %(token.to_string()), 300, "")
            return token.to_string()
            # # send okay response
            # self.send_response(200, 'OK')
            # self.end_headers()
            # # return the token
            # self.wfile.write(token.to_string())
        except OAuthError as err:
            raise
            LOG("Error returned %s" %(err,), 300, "")
            self.send_oauth_error(err, REQUEST)
        return

    # user authorization
    if path.startswith(AUTHORIZATION_URL):
        try:
            return self.manage_oauth_authorize(oauth_token=self._get_token(oauth_request, "request"),
                                               oauth_callback=self.get_callback(oauth_request))
            # get the request token
            # token = self.fetch_request_token(oauth_request)
            # # authorize the token (kind of does nothing for now)
            # token = self.authorize_token(token, None)
            # token.set_verifier(VERIFIER)
            # return token.get_callback_url()
            # send okay response
            # self.send_response(200, 'OK')
            # self.end_headers()
            # # return the callback url (to show server has it)
            # self.wfile.write(token.get_callback_url())
        except OAuthError as err:
            self.send_oauth_error(err, REQUEST)
        return

    if path.startswith(AUTHORIZATION_VERIFIED_URL):
        try:
            # get the request token
            token = self.fetch_request_token(oauth_request)
            # authorize the token (kind of does nothing for now)
            token = self.authorize_token(token, None)
            token.set_verifier(VERIFIER)
            # send okay response
            LOG("calling the callback url %s" %(token.get_callback_url(),), 300, "")
            return REQUEST.RESPONSE.redirect(token.get_callback_url())
        except OAuthError as err:
            self.send_oauth_error(err, REQUEST)
        return


    # access token
    if path.startswith(ACCESS_TOKEN_URL):
        try:
            # create an access token
            token = self.fetch_access_token(oauth_request)
            return token.to_string()
            # # send okay response
            # self.send_response(200, 'OK')
            # self.end_headers()
            # # return the token
            # self.wfile.write(token.to_string())
        except OAuthError as err:
            self.send_oauth_error(err, REQUEST)
        return

    # protected resources
    if path.startswith(RESOURCE_URL):
        try:
            # verify the request has been oauth authorized
            consumer, token, params = self.verify_request(oauth_request)
            # send okay response
            # self.send_response(200, 'OK')
            # self.end_headers()
            # # return the extra parameters - just for something to return
            # self.wfile.write(str(params))
            return str(params)
        except OAuthError as err:
            self.send_oauth_error(err, REQUEST)
        return

  # alias method
  request_token_ready = call
  request_token = call
  authorize = call
  access_token = call
  photos = call
  authorizationVerified = call


InitializeClass(OAuthTool)
