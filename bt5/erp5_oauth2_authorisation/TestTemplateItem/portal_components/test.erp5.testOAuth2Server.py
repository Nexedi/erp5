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
from __future__ import print_function
import base64
from collections import defaultdict
from functools import partial, wraps
import hashlib
from six.moves.html_parser import HTMLParser
from io import BytesIO
import json
import random
import pprint
from time import time
import unittest
from six.moves.urllib.parse import parse_qsl, quote, unquote, urlencode, urlsplit, urlunsplit
import six
from AccessControl.SecurityManagement import getSecurityManager, setSecurityManager
from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Utils import bytes2str, str2bytes
from Products.ERP5.ERP5Site import (
  ERP5_AUTHORISATION_EXTRACTOR_USERNAME_NAME,
  ERP5_AUTHORISATION_EXTRACTOR_PASSWORD_NAME,
)
import Zope2
from ZPublisher.mapply import mapply
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from six.moves import xrange

_TEST_ACCESS_COOKIE_NAME = '__Site-test_at'
_TEST_REFRESH_COOKIE_NAME = '__Site-test_rt'
_TEST_USER_LOGIN = 'test_user_login'
_EXTERNAL_CLIENT_REDIRECT_URI = 'livetest://callback'
_HTML_FIELD_TAG_SET = {
  'input',
  'button',
  'submit',
  # Very incomplete, but enough for this tests' purpose: ignores "select"s...
}
class FormExtractor(HTMLParser):
  def reset(self):
    self.__in_form = False
    self.form_list = []
    HTMLParser.reset(self)

  def handle_starttag(self, tag, attribute_item_list):
    attr_dict = dict(attribute_item_list)
    if tag == 'form':
      assert not self.__in_form
      self.__in_form = True
      self.form_list.append((attr_dict['action'], []))
    elif self.__in_form and tag in _HTML_FIELD_TAG_SET:
      self.form_list[-1][1].append((
        attr_dict['name'],
        attr_dict.get('value', '').encode('utf-8'),
      ))

  def handle_endtag(self, tag):
    if tag == 'form':
      self.__in_form = False

class TestOAuth2(ERP5TypeTestCase):
  __cleanup_list = None
  __port = None
  __query_trace = None

  # Note: this is a function, not a method. It is defined inside the class to
  # be able to reach __* attributes, but is deleted before the class
  # declaration is completed as it cannot function as a method. It cannot be
  # wrapped into a staticmethod, as these are not considered callable when used
  # as a decorator, for some reason (maybe because I did not access it as a
  # class attribute, but that would complexify the code).
  # pylint: disable=no-self-argument
  def _printQueryTraceOnFailure(func):
    """
    Wrapper for test methods so __query_trace is printed when the test fails.
    """
    @wraps(func)
    def wrapper(self, *args, **kw):
      try:
        return func(self, *args, **kw)
      except unittest.SkipTest:
        raise
      except Exception:
        print(
          '\n###################################\n'.join(
            self.__query_trace or (),
          ),
        )
        raise
    return wrapper
  # pylint: enable=no-self-argument

  def getBusinessTemplateList(self):
    return (
      'erp5_oauth2_authorisation',
      'erp5_oauth2_resource',
    )

  def __forCleanup(self, document_value):
    self.__cleanup_list.append(document_value)
    return document_value

  def __declareClient(self, server_connector_value, title, local=None, **kw):
    """
    Register a new client on given server connector,
    create the client connector web service, and link both together.
    """
    client_declaration_value = server_connector_value.newContent(
      portal_type='OAuth2 Client',
      title=title,
      local=local,
      **kw
    )
    # Web Service implementing OAuth2 protocol as a client for the
    # Authorisation Server - so the personality on a Resource Server.
    client_connector_value = self.__forCleanup(
      self.portal.portal_web_services.newContent(
        portal_type='OAuth2 Authorisation Client Connector',
        title=title,
        description='This is an OAuth2 client declaration for use in a live test',
        reference=client_declaration_value.getId(),
        authorisation_server_url=(
          server_connector_value.getId()
          if local else
          server_connector_value.getPath()
        ),
        # Disable https requirement & CA validation when accessing
        # Authorisation Server. Allows the test environment to be
        # accessed over plain http or via a non-recognised certificate.
        insecure=True,
      ),
    )
    client_connector_value.validate()
    # Finalise client declaration creation
    client_declaration_value.setRedirectUriList([
      client_connector_value.getRedirectUri(),
    ])
    client_declaration_value.validate()
    return client_declaration_value, client_connector_value

  def __searchOAuth2Session(self, **kw):
    """
    Similar to searchFolder or portal_catalog, but limited to
    OAuth2 sessions related to current test.
    """
    return self.portal.portal_catalog(
      portal_type='OAuth2 Session',
      strict__any__uid=[
        self.__oauth2_server_connector_value.getUid(),
      ] + [
        x.getUid()
        for x in self.__oauth2_server_connector_value.objectValues()
      ],
      **kw
    )

  def afterSetUp(self):
    super(TestOAuth2, self).afterSetUp()
    parsed_site_url = urlsplit(self.portal.absolute_url())
    self.__scheme = parsed_site_url.scheme
    context_netloc_list = parsed_site_url.netloc.rsplit(':', 1)
    try:
      self.__host, self.__port = context_netloc_list
    except ValueError:
      self.__host, = context_netloc_list
    self.tic()
    assert self.__cleanup_list is None
    self.__cleanup_list = []
    forCleanup = self.__forCleanup
    portal = self.portal
    # Web Service implementing OAuth2 Authorisation Server protocol.
    self.__oauth2_server_connector_value = server_connector_value = forCleanup(portal.portal_web_services.newContent(
      portal_type='OAuth2 Authorisation Server Connector',
      title='live test oauth2 server connector',
    ))
    server_connector_value.validate()
    # Trigger initial generation of key material. Otherwise, this could
    # cause conflict errors during tests: some client connectors will
    # trigger key generation within the local transaction, while others
    # will urlopen to this same document, causing an unavoidable conflict
    # error, which is irrelevant to real usage, as this only happens because
    # we are tricking some clients into thinking the authorisation server
    # is remote, while it is actually local.
    server_connector_value.renewTokenSecret()
    # default client: local, so that the "remote" authorisation server
    # uses it to authenticate users. Nesting (authorisation server itself
    # deferring to another authorisation server) is in theory possible in
    # real-life setups (although the use is dubious), but it basically
    # causes infinite recursion in such single-zope tests with
    # pretend-to-be-remote cases.
    (
      self.__oauth2_default_client_declaration_value,
      self.__oauth2_default_client_connector_value,
    ) = self.__declareClient(
      server_connector_value=server_connector_value,
      title='live test default client',
      local=True,
      usable_as_default=True,
    )
    # trusted client: implicitly trusted, not local
    (
      self.__oauth2_trusted_client_declaration_value,
      self.__oauth2_trusted_client_connector_value,
    ) = self.__declareClient(
      server_connector_value=server_connector_value,
      title='live test trusted client',
      trusted=True,
    )
    # local client: local
    (
      self.__oauth2_local_client_declaration_value,
      self.__oauth2_local_client_connector_value,
    ) = self.__declareClient(
      server_connector_value=server_connector_value,
      title='live test local client',
      local=True,
    )
    # remote client: not implicitly trusted, pretends to be remote but uses
    # same instance.
    (
      self.__oauth2_remote_client_declaration_value,
      self.__oauth2_remote_client_connector_value,
    ) = self.__declareClient(
      server_connector_value=server_connector_value,
      title='live test remote client',
    )
    # out-of-ERP5 oauth2 client, for example some browser-side code
    self.__oauth2_external_client_declaration = server_connector_value.newContent(
      portal_type='OAuth2 Client',
      title='live test external client',
      local=False,
      redirect_uri_list=[
        'unused://callback', # to exercise multi-redirect-uri code
        _EXTERNAL_CLIENT_REDIRECT_URI, # the one actually used in this test
      ],
    )
    self.__oauth2_external_client_declaration.validate()
    # PAS plugins for the above
    acl_users = portal.acl_users
    # Resource Server personality: setup this plugin so it issues and manages
    # cookies under a non-default name.
    acl_users.manage_addProduct['ERP5Security'].addERP5OAuth2ResourceServerPlugin(
      id='test_oauth2_resource_server',
      access_cookie_name=_TEST_ACCESS_COOKIE_NAME,
      refresh_cookie_name=_TEST_REFRESH_COOKIE_NAME,
    )
    forCleanup(acl_users.test_oauth2_resource_server)
    # Test user account
    self.__user_value = user_value = forCleanup(portal.person_module.newContent(
      portal_type='Person',
      first_name='Test User',
      last_name=DateTime().strftime('%Y-%m-%dT%H:%M:%S'),
    ))
    self.__password = password = str(random.getrandbits(32))
    user_value.newContent(
      portal_type='ERP5 Login',
      reference=_TEST_USER_LOGIN,
      password=password,
    ).validate()
    user_value.newContent(
      portal_type='Assignment',
    ).open()
    self.tic()

  def beforeTearDown(self):
    self.abort()
    cleanup_list = self.__cleanup_list
    # XXX: imperfect cleanup if indexation did not complete
    cleanup_list.extend(
      x.getObject() for x in self.__searchOAuth2Session()
    )
    parent_dict = defaultdict(list)
    for document_value in cleanup_list:
      document_id = document_value.getId()
      parent_value = document_value.aq_parent
      document_value_from_parent = parent_value[document_id]
      if document_value_from_parent == document_value:
        parent_dict[parent_value].append(document_id)
    for parent_value, id_list in six.iteritems(parent_dict):
      parent_value.manage_delObjects(ids=id_list)
    self.tic()
    super(TestOAuth2, self).beforeTearDown()

  def _query(
    self,
    path,
    method,
    query='',
    client_ip='127.0.0.1',
    header_dict=(),
    cookie_dict=(),
    content_type=None,
    body=None,
  ):
    """
    Run <path>(REQUEST, RESPONSE) as if it were executed as part of an HTTP
    <method> request, with <header_dict> HTTP headers, plus <cookie_dict>
    cookies (separated from header_dict for usage convenience) and <query>
    query string, and <body> body.
    cookie_dict values are dicts of its attributes, or None for unset cookies.
    Returns the a 4-tuple with the response's content:
    - status
    - header_dict
    - cookie_dict (as set by response headers)
    - body
    """
    query_trace = self.__query_trace
    if query_trace is not None:
      query_trace_request = pprint.pformat({
        'path': path,
        'method': method,
        'query': query,
        'client_ip': client_ip,
        'header_dict': header_dict,
        'cookie_dict': cookie_dict,
        'content_type': content_type,
        'body': body,
      })
    response = HTTPResponse(
      stdout=BytesIO(), # XXX: ignored
      stderr=BytesIO(), # XXX: ignored
    )
    # Build CGI environment as per rfc3875
    environ_dict = {
      'HTTP_' + x.upper().replace('-', '_'): y
      for x, y in six.iteritems(dict(header_dict))
    }
    cookie_header = ';'.join(
      '%s="%s"' % (
        name,
        quote(cookie_dict['value']),
      ) for name, cookie_dict in six.iteritems(dict(cookie_dict))
      if cookie_dict
    )
    if cookie_header:
      environ_dict['HTTP_COOKIE'] = cookie_header
    if body is not None:
      environ_dict['CONTENT_LENGTH'] = len(body)
    if content_type is not None:
      environ_dict['CONTENT_TYPE'] = content_type
    # Non-top-level import as this imports a component from a Business Template
    # this test requests the installation of.
    from erp5.component.document.OAuth2AuthorisationClientConnector import (
      INSECURE_REQUEST_ENVIRON_SERVER_SOFTWARE,
    )
    environ_dict['GATEWAY_INTERFACE'] = 'CGI/1.1'
    environ_dict['PATH_INFO'] = path
    environ_dict['QUERY_STRING'] = query
    environ_dict['REMOTE_ADDR'] = client_ip
    environ_dict['REQUEST_METHOD'] = method
    environ_dict['SCRIPT_NAME'] = '/'
    environ_dict['SERVER_NAME'] = self.__host
    environ_dict['SERVER_PORT'] = self.__port
    environ_dict['SERVER_PROTOCOL'] = 'HTTP/1.1'
    environ_dict['SERVER_SOFTWARE'] = INSECURE_REQUEST_ENVIRON_SERVER_SOFTWARE
    # Not part of rfc3875
    if self.__scheme == 'https':
      environ_dict['HTTPS'] = '1'
    current_security_manager = getSecurityManager()
    request = HTTPRequest(
      stdin=BytesIO(body or b''),
      environ=environ_dict,
      response=response,
    )
    request.processInputs()
    request['PARENTS'] = [
      # Get the Zope application object, but without opening a new connection.
      Zope2.app(connection=self.portal._p_jar),
    ]
    published_callable = request.traverse(path)
    exc = None
    try:
      response.setBody(
        mapply(
          object=published_callable,
          keyword=request,
          maybe=1,
          context=request,
          bind=1,
        ),
      )
    except Exception as e:
      exc = e
      raise
    finally:
      setSecurityManager(current_security_manager)
      cookie_dict = {}
      response_header_dict = {}
      for key, value in response.listHeaders():
        key = key.lower()
        if key == 'set-cookie':
          # XXX: minimal Set-Cookie parser
          cookie_name, cookie_body = value.split('=', 1)
          # RFC6265 makes quoting obsolete
          # assert cookie_body[0] == '"', repr(cookie_body)
          cookie_value, cookie_attributes = cookie_body.split(';', 1)
          cookie_value = cookie_value.strip('"')
          cookie_value_dict = {
            'value': urllib.unquote(cookie_value),
          }
          for cookie_attribute in cookie_attributes.split(';'):
            cookie_attribute = cookie_attribute.lstrip()
            if '=' in cookie_attribute:
              cookie_attribute_name, cookie_attribute_value = cookie_attribute.split('=', 1)
            else:
              cookie_attribute_name = cookie_attribute
              cookie_attribute_value = True
            cookie_attribute_name = cookie_attribute_name.lower()
            if cookie_attribute_name == 'max-age':
              cookie_attribute_name = 'max_age'
              cookie_attribute_value = int(cookie_attribute_value, 10)
            elif cookie_attribute_name == 'httponly':
              cookie_attribute_name = 'http_only'
            assert cookie_attribute_name not in cookie_value_dict, (cookie_attribute_name, value)
            cookie_value_dict[cookie_attribute_name] = cookie_attribute_value
          assert cookie_name not in cookie_dict, (cookie_name, cookie_value_dict)
          cookie_dict[cookie_name] = cookie_value_dict
        else:
          response_header_dict[key] = value
      if query_trace is not None:
        self.__query_trace.append('request=%s\nresponse=%s' % (
          query_trace_request,
          pprint.pformat(
            (
              {
                'status': response.status,
                'headers': response_header_dict,
                'cookies': cookie_dict,
                'body': response.body,
              }
              if exc is None else
              exc
            ),
          ),
        ))
    if response.body:
      response.headers.setdefault('content-type', 'text/html; charset=utf-8')
    return (
      response.status,
      response_header_dict,
      {
        name: (
          cookie_dict if cookie_dict.get('max_age', True) else
          None
        ) for name, cookie_dict in six.iteritems(cookie_dict)
      },
      response.body,
    )

  def assertIsRedirect(
    self,
    query_result,
    reference_location,
    reference_status=302,
  ):
    """
    Assert that given call redirects to given location with given status.
    Only scheme, netloc and path are matched (ex: query is ignored).
    """
    parsed_reference_location = urlsplit(reference_location)
    status, header_dict, cookie_dict, body = query_result
    self.assertIn(
      body.strip(),
      (
        b'',
        # XXX: Tolerate the redirect URL being returned in the body.
        # This is a bug, body should really be empty.
        header_dict.get('location', b''),
      ),
    )
    parsed_location = urlsplit(header_dict.get('location', ''))
    self.assertEqual(
      (
        status,
        parsed_location.scheme,
        parsed_location.netloc,
        parsed_location.path,
      ),
      (
        reference_status,
        parsed_reference_location.scheme,
        parsed_reference_location.netloc,
        parsed_reference_location.path,
      ),
    )
    return parsed_location, header_dict, cookie_dict

  def assertContentTypeEqual(self, header_dict, content_type):
    self.assertEqual(header_dict.get('content-type', '').split(';', 1)[0], content_type)

  def _submitDialog(
    self,
    query_result,
    value_callback=lambda field_item_list: field_item_list,
    client_ip='127.0.0.1',
    header_dict=(),
    cookie_dict=(),
  ):
    """
    Sumbit given HTML form. It must be a dialog form (template is form_dialog).

    query_result (as returned by _query)
      Response containing an HTML page with the form to submit.
      Status must be 200.
      Content-Type must be text/html.
      The body must contain exactly one <form> tag.
    value_callback ((field_item_list) -> field_item_list)
      Called with an iterable containing 2-tuples for each field found in body,
      in parsing order:
      - name (str)
        Name of the field.
      - value (None, str)
        Value of the field from HTML source.
      The same name may be present multiple times if there are homonymous fields.
    client_ip
    header_dict
    cookie_dict
      See _query.
    """
    portal = self.portal
    result_status, result_header_dict, _, result_body = query_result
    # Extract form data
    self.assertEqual(result_status, 200, (result_status, result_header_dict))
    self.assertContentTypeEqual(result_header_dict, 'text/html')
    assert result_body
    parser = FormExtractor()
    parser.feed(bytes2str(result_body))
    parser.close()
    (action_url, field_list), = parser.form_list # pylint: disable=unbalanced-tuple-unpacking
    for field_name, _ in field_list:
      if field_name.endswith(':method'):
        script_id, _ = field_name.rsplit(':', 1)
        break
    else:
      raise ValueError('No field name ending with ":method"')
    # Call Base_callDialogMethod
    status, inner_header_dict, inner_cookie_dict, body = self._query(
      path=urlsplit(action_url).path + '/' + script_id,
      method='POST',
      client_ip=client_ip,
      content_type='application/x-www-form-urlencoded',
      header_dict=header_dict,
      cookie_dict=cookie_dict,
      body=str2bytes(urlencode(list(value_callback(
        field_item_list=tuple(
          (key, value)
          for key, value in field_list
          if not key.endswith(':method')
        ),
      )))),
    )
    if script_id == 'Base_callDialogMethod' and status == 302:
      # Base_callDialogMethod ended in redirection. It may be that the action
      # script decided to redirect us (which would mean we are done), or that
      # Base_callDialogMethod itself decided to redirect us to its
      # dialog_action script (which means we are not done).
      # Inspect Location header to decide which one it is. This is not perfect,
      # as the action script could itself decide to redirect us to itself, but
      # should be good enough).
      assert not inner_cookie_dict, repr(inner_cookie_dict)
      assert not body, repr(body)
      location = inner_header_dict['location']
      # Base_callDialogMethod should always redirect to somewhere on the
      # portal, so if it is outside we know the redirection comes from the
      # action script and we are done.
      if location.startswith(portal.absolute_url()):
        parsed_location = urlsplit(location)
        dialog_method, = [
          value
          for key, value in field_list
          if key == 'dialog_method'
        ]
        if parsed_location.path.rsplit('/', 1)[-1] == dialog_method:
          # We are being redirected to the action script, follow the redirection.
          status, inner_header_dict, inner_cookie_dict, body = self._query(
            path=parsed_location.path,
            method='GET',
            query=parsed_location.query,
            client_ip=client_ip,
            header_dict=header_dict,
            cookie_dict=cookie_dict,
          )
    return status, inner_header_dict, inner_cookie_dict, body

  def _authorise(
    self,
    path,
    query,
    redirect_uri,
    expect_authorisation_dialog,
    scope_filter_callback=lambda field_item_list: field_item_list,
    authentication_callback=None,
    authentication_is_local=False,
    client_ip='127.0.0.1',
    cookie_dict=(),
    header_dict=(),
  ):
    """
    Call the {server connector}/authorize endpoint and complete the authorization process.

    path (str)
      URL path of "{server connector}/authorize"
    query (str)
      Query string to provide to "{server connector}/authorize"
    redirect_uri (str)
      The URI signaling the end of the authentication process.
      Only scheme, netloc and path matter, the rest should be empty.
    expect_authorisation_dialog (bool)
      Whether the authorization dialog is expected.
      If false and the authorisation dialog is displayed, the test fails.
      If true and the authorisation dialog is not displayed, the test fails.
    scope_filter_callback ((scope_category_relative_url_set) -> (scope_category_relative_url_set))
      Ignored if expect_authorisation_dialog is false.
      Called when the authorisation dialog is displayed, to decide which scopes are to be granted access to.
    authentication_callback (None, (parsed_location, ...) -> ...)
      Called when the login form is displayed.
      If the login form is displayed but this is None, test fails.
      If the login for is not displayed and this is not None, test fails.
      Called with:
        parsed_location (urlsplit)
          Parsed locator. Use this if you want, for example, to access the portal_status_message.
      See _submitDialog for further signature definitions.
    authentication_is_local (bool)
      Ignored if authentication_callback is None.
      If false, expect the login form name to be "login_form".
      If true, expect the login form to be "login_once_form".
    client_ip
    cookie_dict
    header_dict
      See _query
      header_dict is passed to all queries.
      cookie_dict is used as a basis for a cookie jar, maintained
      throughout the course of this method.

    Returns:
    parsed_location (urlsplit)
      Parsed version of the actual redirection location aimed at redirect_uri.
    cookie_dict (dict)
      Flattened view of all response set-cookie headers.
    time_before (int)
    time_after (int)
      Unix timestamps surrounding the operation which redirected to redirect_uri,
      for purposes of checking OAuth2 Session expiration date.
    """
    cookie_dict = {}
    cookie_jar = dict(cookie_dict)
    def updateCookieDictAndJar(set_cookie_dict):
      for key, value in six.iteritems(set_cookie_dict):
        if value is None:
          cookie_jar.pop(key, None)
        else:
          cookie_jar[key] = value
        cookie_dict[key] = value
    parsed_redirect_uri = urlsplit(redirect_uri)
    def isRedirectURI(parsed_location):
      return (
        parsed_location.scheme == parsed_redirect_uri.scheme and
        parsed_location.netloc == parsed_redirect_uri.netloc and
        parsed_location.path == parsed_redirect_uri.path
      )
    assert not parsed_redirect_uri.query
    assert not parsed_redirect_uri.fragment
    # XXX: just to satisfy authentication_callback
    parsed_location = urlsplit(urlunsplit((
      '',
      '',
      path,
      query,
      None,
    )))
    # Open authorize
    time_before = int(time())
    status, inner_header_dict, inner_cookie_dict, _ = query_result = self._query(
      path=path,
      method='GET',
      query=query,
      cookie_dict=cookie_jar,
      client_ip=client_ip,
      header_dict=header_dict,
    )
    time_after = int(time())
    authentication_happened = authentication_callback is None
    # Prevent infinite loop
    query_quota = 10
    while True:
      assert query_quota, self.__query_trace
      query_quota -= 1
      updateCookieDictAndJar(inner_cookie_dict)
      if status == 302:
        # Being redirected...
        parsed_location = urlsplit(inner_header_dict.get('location', ''))
        if isRedirectURI(parsed_location):
          # ...to client: check if this is expected and leave
          self.assertTrue(
            authentication_happened,
            (
              authentication_happened,
              authentication_callback,
              parsed_location,
            ),
          )
          break
        # ...to server: follow and continue
        status, inner_header_dict, inner_cookie_dict, _ = query_result = self._query(
          path=parsed_location.path,
          method='GET',
          query=parsed_location.query,
          cookie_dict=cookie_jar,
          client_ip=client_ip,
          header_dict=header_dict,
        )
      else:
        # Not being redirected, this must be a form
        if authentication_happened:
          # This should be the authorisation form
          value_callback = scope_filter_callback
        else:
          authentication_happened = True
          # This should be the login form
          value_callback = partial(
            authentication_callback,
            parsed_location=parsed_location,
          )
        # Fill and sumbit the form
        time_before = int(time())
        status, inner_header_dict, inner_cookie_dict, _ = self._submitDialog(
          query_result=query_result,
          value_callback=value_callback,
          cookie_dict=cookie_jar,
          client_ip=client_ip,
          header_dict=header_dict,
        )
        time_after = int(time())
    return parsed_location, cookie_dict, time_before, time_after

  def _injectUsernamePassword(
    self,
    username_field_id,
    password_field_id,
    field_item_list,
  ):
    username_found = password_found = False
    for name, value in field_item_list:
      if name == username_field_id:
        username_found = True
        value = _TEST_USER_LOGIN
      elif name == password_field_id:
        password_found = True
        value = self.__password
      yield (name, value)
    assert username_found
    assert password_found

  @_printQueryTraceOnFailure
  def test_basicOAuth2Use(self):
    """
    Get a token, renew it, terminate session.
    """
    basic_auth = 'Basic ' + bytes2str(base64.encodestring(
      str2bytes(_TEST_USER_LOGIN + ':' + self.__password),
    )).rstrip()
    oauth2_server_connector = self.__oauth2_server_connector_value.getPath()
    oauth2_client_declaration_value = self.__oauth2_external_client_declaration
    authorisation_code_lifespan = oauth2_client_declaration_value.getAuthorisationCodeLifespan()
    access_token_lifespan = oauth2_client_declaration_value.getAccessTokenLifespan()
    refresh_token_lifespan = oauth2_client_declaration_value.getRefreshTokenLifespan()

    # Sanity check: there must be no valid OAuth2 session for the test user
    self.assertItemsEqual(
      self.__searchOAuth2Session(
        select_list=['creation_date', 'title']
      ).dictionaries(),
      [],
    )

    self.__query_trace = []
    # Client produces a PKCE secret and sends the Resource Owner to the Authorisation Server
    # to authorise them, getting an ahutorisation code.
    code_verifier = base64.urlsafe_b64encode(
      b'this is not a good secret6789012', # 32 bytes
    )
    reference_state = 'dummy'
    client_id = oauth2_client_declaration_value.getId()
    parsed_location, cookie_dict, time_before, time_after = response = self._authorise(
      path=oauth2_server_connector + '/authorize',
      query=urlencode({
        'response_type': 'code',
        'client_id': client_id,
        'state': reference_state,
        'code_challenge_method': 'S256',
        'code_challenge': bytes2str(base64.urlsafe_b64encode(
          hashlib.sha256(code_verifier).digest(),
        )).rstrip('='),
        'redirect_uri': _EXTERNAL_CLIENT_REDIRECT_URI,
      }),
      redirect_uri=_EXTERNAL_CLIENT_REDIRECT_URI,
      expect_authorisation_dialog=True,
      # User needs to be authenticated in whatever non-OAuth2-specified way.
      # Use basic auth.
      header_dict={
        'authorization': basic_auth,
      },
    )
    self.assertEqual(cookie_dict, {})
    query_list = parse_qsl(parsed_location.query)
    query_dict = dict(query_list)
    self.assertEqual(len(query_list), len(query_dict), (query_list, query_dict))
    authorisation_code = query_dict['code']
    state = query_dict['state']
    self.assertEqual(state, reference_state)
    self.tic()
    # OAuth2 Session is now created
    user_session, = self.__searchOAuth2Session()
    user_session = user_session.getObject()
    self.assertEqual(user_session.getValidationState(), 'draft')
    expiration_date = int(user_session.getExpirationDate())
    self.assertLessEqual(time_before + authorisation_code_lifespan, expiration_date)
    self.assertLessEqual(expiration_date, time_after + authorisation_code_lifespan)

    # Client exchanges the Authorisation Code and PKCE value for a pair of tokens.
    time_before = int(time())
    status, header_dict, cookie_dict, body = response = self._query(
      path=oauth2_server_connector + '/token',
      method='POST',
      content_type='application/x-www-form-urlencoded',
      body=urlencode({
        'grant_type': 'authorization_code',
        'code': authorisation_code,
        'client_id': client_id,
        'code_verifier': code_verifier,
        'redirect_uri': _EXTERNAL_CLIENT_REDIRECT_URI,
      }),
    )
    time_after = int(time())
    self.assertEqual(status, 200, response)
    self.assertEqual(cookie_dict, {}, response)
    self.assertContentTypeEqual(header_dict, 'application/json')
    token_dict = json.loads(body)
    self.assertIn('access_token', token_dict)
    refresh_token = token_dict['refresh_token']
    self.assertLessEqual(token_dict['expires_in'], access_token_lifespan)
    self.tic()
    # OAuth2 Session is now validated
    self.assertEqual(user_session.getValidationState(), 'validated')
    expiration_date = int(user_session.getExpirationDate())
    self.assertLessEqual(time_before + refresh_token_lifespan, expiration_date)
    self.assertLessEqual(expiration_date, time_after + refresh_token_lifespan)

    # Request a new access token
    status, header_dict, cookie_dict, body = self._query(
      path=oauth2_server_connector + '/token',
      method='POST',
      content_type='application/x-www-form-urlencoded',
      body=urlencode({
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
      }),
    )
    self.assertEqual(status, 200)
    self.assertEqual(cookie_dict, {})
    self.assertContentTypeEqual(header_dict, 'application/json')
    token_dict = json.loads(body)
    self.assertIn('access_token', token_dict)
    refresh_token = token_dict['refresh_token']

    # Now, revoke the session (can be done with any token)
    status, header_dict, cookie_dict, body = self._query(
      path=oauth2_server_connector + '/revoke',
      method='POST',
      content_type='application/x-www-form-urlencoded',
      body=urlencode({
        'token_type_hint': 'refresh_token',
        'token': refresh_token,
      }),
    )
    self.assertEqual(status, 200)
    self.assertEqual(cookie_dict, {})
    self.tic()
    # OAuth2 Session is now invalidated
    self.assertEqual(user_session.getValidationState(), 'invalidated')

    # and check that it reuses to renew tokens
    status, header_dict, cookie_dict, body = self._query(
      path=oauth2_server_connector + '/token',
      method='POST',
      content_type='application/x-www-form-urlencoded',
      body=urlencode({
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
      }),
    )
    self.assertEqual(status, 400)
    self.assertEqual(cookie_dict, {})
    self.assertContentTypeEqual(header_dict, 'application/json')
    token_dict = json.loads(body)
    self.assertIn(token_dict['error'], 'invalid_grant')

  @_printQueryTraceOnFailure
  def test_basicERP5UseRemoteAuthorisationServer(self):
    """
    Login with a remote AuthorisationServer.
    """
    def injectUsernamePassword(field_item_list):
      assert not inject_username_password_called, '\n'.join(self.__query_trace)
      inject_username_password_called.append(None)
      return self._injectUsernamePassword(
        username_field_id=ERP5_AUTHORISATION_EXTRACTOR_USERNAME_NAME, #'__ac_name',
        password_field_id=ERP5_AUTHORISATION_EXTRACTOR_PASSWORD_NAME, #'__ac_password',
        field_item_list=field_item_list,
      )
    self.__query_trace = []
    inject_username_password_called = []
    self._test_basicERP5Use(
      oauth2_client_connector_value=self.__oauth2_remote_client_connector_value,
      expect_authorisation_dialog=True,
      authentication_callback=injectUsernamePassword,
      authentication_is_local=False,
    )

  @_printQueryTraceOnFailure
  def test_basicERP5UseRemoteAuthorisationServerTrusted(self):
    """
    Login with a remote Authorisation Server which trusts this client.
    """
    def injectUsernamePassword(field_item_list):
      assert not inject_username_password_called, '\n'.join(self.__query_trace)
      inject_username_password_called.append(None)
      return self._injectUsernamePassword(
        username_field_id=ERP5_AUTHORISATION_EXTRACTOR_USERNAME_NAME, #'__ac_name',
        password_field_id=ERP5_AUTHORISATION_EXTRACTOR_PASSWORD_NAME, #'__ac_password',
        field_item_list=field_item_list,
      )
    self.__query_trace = []
    inject_username_password_called = []
    self._test_basicERP5Use(
      oauth2_client_connector_value=self.__oauth2_trusted_client_connector_value,
      expect_authorisation_dialog=False,
      authentication_callback=injectUsernamePassword,
      authentication_is_local=False,
    )

  @_printQueryTraceOnFailure
  def test_basicERP5UseLocalAuthorisationServer(self):
    """
    Login with a local Authorisation Server.
    """
    def injectUsernamePassword(field_item_list):
      return self._injectUsernamePassword(
        username_field_id=ERP5_AUTHORISATION_EXTRACTOR_USERNAME_NAME,
        password_field_id=ERP5_AUTHORISATION_EXTRACTOR_PASSWORD_NAME,
        field_item_list=field_item_list,
      )
    self.__query_trace = []
    self._test_basicERP5Use(
      oauth2_client_connector_value=self.__oauth2_local_client_connector_value,
      expect_authorisation_dialog=False,
      authentication_callback=injectUsernamePassword,
      authentication_is_local=True,
    )

  def _test_basicERP5Use(
    self,
    oauth2_client_connector_value,
    expect_authorisation_dialog,
    authentication_callback,
    authentication_is_local,
  ):
    oauth2_server_connector_value = self.__oauth2_server_connector_value
    portal = self.portal
    portal_path = portal.getPath()
    portal_url = portal.absolute_url() + '/'
    # Sanity check: there must be no valid OAuth2 session for the test user
    self.assertItemsEqual(
      self.__searchOAuth2Session(
        select_list=['creation_date', 'title']
      ).dictionaries(),
      [],
    )

    resource_server_cookie_jar = {}
    authorisation_server_cookie_jar = {}
    # Access portal, get redirected to login form
    parsed_location, _, cookie_dict = self.assertIsRedirect(
      self._query(
        path=portal_path + '/index_html',
        method='GET',
        cookie_dict=resource_server_cookie_jar,
      ),
      reference_location=portal_url + 'login_form',
    )
    self.assertEqual(cookie_dict, {})
    # Open login form, inject client_id
    _, _, cookie_dict, _ = query_result = self._query(
      path=parsed_location.path,
      method='GET',
      query=urlencode(
        parse_qsl(parsed_location.query) + [
          ('client_id', oauth2_client_connector_value.getReference()),
        ],
      ),
      cookie_dict=resource_server_cookie_jar,
    )
    # In any case, the response must set the login state cookie.
    self.assertEqual(len(cookie_dict), 1, cookie_dict)
    login_state_cookie_name, = cookie_dict
    self.assertRegex(login_state_cookie_name, '^__Host-login-state-')
    resource_server_cookie_jar.update(cookie_dict)
    if authentication_is_local:
      login_form_cookie_jar = resource_server_cookie_jar
    else:
      # Response is a redirection to Authorisation Server's oauth2
      # /authorize endpoint.
      parsed_location, _, cookie_dict = self.assertIsRedirect(
        query_result,
        reference_location=oauth2_server_connector_value.absolute_url() + '/authorize',
      )
      # Open the login form by following the redirect
      _, _, cookie_dict, _ = query_result = self._query(
        path=parsed_location.path,
        method='GET',
        query=parsed_location.query,
      )
      authorisation_server_cookie_jar.update(cookie_dict)
      login_form_cookie_jar = authorisation_server_cookie_jar
    # Fill & submit the login form
    query_result = self._submitDialog(
      query_result,
      value_callback=authentication_callback,
      cookie_dict=login_form_cookie_jar,
    )
    self.tic()
    if authentication_is_local:
      assert not expect_authorisation_dialog
    else:
      # Response is a redirection to Authorisation Server's oauth2
      # /authorize endpoint, now that we are (should be) authenticated.
      parsed_location, _, cookie_dict = self.assertIsRedirect(
        query_result,
        reference_location=oauth2_server_connector_value.absolute_url() + '/authorize',
      )
      # Process any cookie the authorisation server gave us - its
      # authentication is a black box as far as this test is concerned.
      authorisation_server_cookie_jar.update(cookie_dict)
      # Follow it
      _, _, cookie_dict, _ = query_result = self._query(
        path=parsed_location.path,
        method='GET',
        query=parsed_location.query,
        cookie_dict=authorisation_server_cookie_jar,
      )
      authorisation_server_cookie_jar.update(cookie_dict)
      self.tic()
      if expect_authorisation_dialog:
        query_result = self._submitDialog(
          query_result,
          cookie_dict=authorisation_server_cookie_jar,
        )
        self.tic()
        # Process any cookie the authorisation server gave us - its
        # authentication is a black box as far as this test is concerned.
        authorisation_server_cookie_jar.update(cookie_dict)
    # OAuth2 Session is now created for the Resource Server.
    # Another session may have been created for the Authorisation Server
    # itself, if it is using oauth2 for its own local authentication needs.
    user_session, = self.__searchOAuth2Session(
      strict__source__uid=oauth2_server_connector_value[
        oauth2_client_connector_value.getReference()
      ].getUid(),
    )
    user_session = user_session.getObject()
    if not authentication_is_local:
      # Response is a redirection to Resource Server's return uri
      parsed_location, _, _ = self.assertIsRedirect(
        query_result,
        reference_location=oauth2_client_connector_value.absolute_url() + '/loggedIn',
      )
      self.assertEqual(user_session.getValidationState(), 'draft')
      # Open the return uri
      query_result = self._query(
        path=parsed_location.path,
        method='GET',
        query=parsed_location.query,
        cookie_dict=resource_server_cookie_jar,
      )
      self.tic()
    # We are being redirected to portal with a pair of OAuth2 cookies
    parsed_location, _, cookie_dict = self.assertIsRedirect(
      query_result,
      reference_location=portal_url,
    )
    # There may be more cookies if current instance has its own OAuth2 PAS plugins.
    # Ignore these extra cookies, and require our 3 set-cookies, one of which is a deletion.
    self.assertIn(_TEST_ACCESS_COOKIE_NAME, cookie_dict)
    self.assertIn(_TEST_REFRESH_COOKIE_NAME, cookie_dict)
    self.assertIn(login_state_cookie_name, cookie_dict)
    self.assertEqual(cookie_dict[login_state_cookie_name], None)
    del resource_server_cookie_jar[login_state_cookie_name]
    resource_server_cookie_jar.update((
      (key, value)
      for key, value in six.iteritems(cookie_dict)
      if key in (
        _TEST_ACCESS_COOKIE_NAME,
        _TEST_REFRESH_COOKIE_NAME,
      )
    ))
    # OAuth2 Session is now validated
    self.assertEqual(user_session.getValidationState(), 'validated')
    # Access portal, DO NOT get redirected to login form: authentication worked
    status, _, cookie_dict, _ = self._query(
      path=portal_path + '/index_html',
      method='GET',
      cookie_dict=resource_server_cookie_jar,
    )
    self.assertEqual(status, 200)
    self.assertEqual(cookie_dict, {})

    # Open logout page, cookies are removed
    parsed_location, _, cookie_dict = self.assertIsRedirect(
      self._query(
        path=portal_path + '/logout',
        method='POST',
        cookie_dict=resource_server_cookie_jar,
        query=parsed_location.query,
      ),
      reference_location=portal_url + 'logged_out',
    )
    # Similarly to token retrieval, we may have more than 2 cookied being deleted.
    self.assertIn(_TEST_ACCESS_COOKIE_NAME, cookie_dict)
    self.assertEqual(cookie_dict[_TEST_ACCESS_COOKIE_NAME], None)
    self.assertIn(_TEST_REFRESH_COOKIE_NAME, cookie_dict)
    self.assertEqual(cookie_dict[_TEST_REFRESH_COOKIE_NAME], None)
    # OAuth2 Session is now invalidated
    self.tic()
    self.assertEqual(user_session.getValidationState(), 'invalidated')

    # Trying to continue to use the tokens does not work.
    # Access portal, get redirected to login form
    self.assertIsRedirect(
      self._query(
        path=portal_path + '/index_html',
        method='GET',
        cookie_dict=resource_server_cookie_jar,
      ),
      reference_location=portal_url + 'login_form',
    )
    # Remove the tokens
    del resource_server_cookie_jar[_TEST_ACCESS_COOKIE_NAME]
    del resource_server_cookie_jar[_TEST_REFRESH_COOKIE_NAME]

    status, header_dict, cookie_dict, _ = self._query(
      path=parsed_location.path,
      method='GET',
      cookie_dict=resource_server_cookie_jar,
      query=parsed_location.query,
    )
    # Check that logged_out page does not error-out
    self.assertLess(status, 400, (parsed_location, status, header_dict))

  @_printQueryTraceOnFailure
  def test_multipleLoginForm(self):
    """
    Test opening multiple login_form in parallel, each starting with no login
    state cookies, then using them (in ay order).
    """
    injectUsernamePassword = partial(
      self._injectUsernamePassword,
      username_field_id=ERP5_AUTHORISATION_EXTRACTOR_USERNAME_NAME,
      password_field_id=ERP5_AUTHORISATION_EXTRACTOR_PASSWORD_NAME,
    )
    self.__query_trace = []
    portal = self.portal
    portal_url = portal.absolute_url() + '/'
    portal_path = portal.getPath()
    parsed_login_form_location, _, _ = self.assertIsRedirect(
      self._query(
        path=portal_path + '/index_html',
        method='GET',
      ),
      reference_location=portal_url + 'login_form',
    )
    login_form_query = urlencode(
      parse_qsl(parsed_login_form_location.query) + [
        # Pick the local client_id, for simplicity
        ('client_id', self.__oauth2_local_client_connector_value.getReference()),
      ],
    )
    cookie_jar = {}
    login_form_response_dict = {}
    ATTEMPT_COUNT = 10
    # Open ATTEMPT_COUNT login forms, each starting with an empty cookie jar and
    # accumulating their produced cookies in the same jar.
    for _ in xrange(ATTEMPT_COUNT):
      _, _, cookie_dict, _ = query_result = self._query(
        path=parsed_login_form_location.path,
        method='GET',
        query=login_form_query,
      )
      self.assertEqual(len(cookie_dict), 1, cookie_dict)
      login_state_cookie_name, = cookie_dict
      self.assertRegex(login_state_cookie_name, '^__Host-login-state-')
      cookie_jar.update(cookie_dict)
      login_form_response_dict[login_state_cookie_name] = query_result
    # Tolerate some amount of state cookie collision: this means that some login form
    # became unusable. This is supposed to be very rare, compared to the number of login
    # forms opened in parallel and then actually used.
    # XXX: what boundary is acceptable ? floor(x * .99) ?
    original_cookie_count = len(cookie_jar)
    self.assertGreaterEqual(original_cookie_count, ATTEMPT_COUNT - 1)

    # Open one more login form, this time providing it the existing cookie jar.
    # It should pick one cookie (any cookie is fine) and refresh it.
    _, _, cookie_dict, _ = self._query(
      path=parsed_login_form_location.path,
      method='GET',
      query=login_form_query,
      cookie_dict=cookie_jar,
    )
    self.assertEqual(len(cookie_dict), 1, cookie_dict)
    login_state_cookie_name, = cookie_dict
    self.assertRegex(login_state_cookie_name, '^__Host-login-state-')
    self.assertIn(login_state_cookie_name, cookie_jar)
    cookie_jar.update(cookie_dict)
    # Do not store the received login page, to check that the original one is still working.

    # Fill and submit each login form (with the filled cookie jar), they must
    # all work (but there may be fewer than ATTEMPT_COUNT in case of cookie name
    # collision).
    for index, (login_state_cookie_name, query_result) in enumerate(
      six.iteritems(login_form_response_dict),
    ):
      # We are being redirected to portal with a pair of OAuth2 cookies
      parsed_location, _, cookie_dict = self.assertIsRedirect(
        self._submitDialog(
          query_result,
          value_callback=injectUsernamePassword,
          cookie_dict=cookie_jar,
        ),
        reference_location=portal_url,
      )
      # There may be more cookies if current instance has its own OAuth2 PAS plugins.
      # Ignore these extra cookies, and require our 3 set-cookies, one of which is a deletion.
      self.assertIn(_TEST_ACCESS_COOKIE_NAME, cookie_dict)
      self.assertIn(_TEST_REFRESH_COOKIE_NAME, cookie_dict)
      self.assertIn(login_state_cookie_name, cookie_dict)
      self.assertEqual(cookie_dict[login_state_cookie_name], None)
      del cookie_jar[login_state_cookie_name]
      cookie_jar.update((
        (key, value)
        for key, value in six.iteritems(cookie_dict)
        if key in (
          _TEST_ACCESS_COOKIE_NAME,
          _TEST_REFRESH_COOKIE_NAME,
        )
      ))
      # Access portal, DO NOT get redirected to login form: authentication worked
      status, _, _, _ = self._query(
        path=parsed_location.path,
        method='GET',
        query=parsed_location.query,
        cookie_dict=cookie_jar,
      )
      self.assertEqual(status, 200)
      if index & 1:
        # logout before the next login attempt. This must not disturb the next iteration.
        parsed_location, _, cookie_dict = self.assertIsRedirect(
          self._query(
            path=portal_path + '/logout',
            method='POST',
            cookie_dict=cookie_jar,
            query=parsed_location.query,
          ),
          reference_location=portal_url + 'logged_out',
        )
        # Similarly to token retrieval, we may have more than 2 cookied being deleted.
        self.assertIn(_TEST_ACCESS_COOKIE_NAME, cookie_dict)
        self.assertEqual(cookie_dict[_TEST_ACCESS_COOKIE_NAME], None)
        self.assertIn(_TEST_REFRESH_COOKIE_NAME, cookie_dict)
        self.assertEqual(cookie_dict[_TEST_REFRESH_COOKIE_NAME], None)
        # Remove the tokens
        del cookie_jar[_TEST_ACCESS_COOKIE_NAME]
        del cookie_jar[_TEST_REFRESH_COOKIE_NAME]

  del _printQueryTraceOnFailure
