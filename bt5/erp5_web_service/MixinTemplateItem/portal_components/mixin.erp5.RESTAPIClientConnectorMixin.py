##############################################################################
#
# Copyright (c) 2021 Nexedi SA and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
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
import time
import ssl
import json
from six.moves.http_client import HTTPSConnection
from six.moves.urllib.parse import urlparse
from six import string_types as basestring
from Products.ERP5Type.Timeout import getTimeLeft
from contextlib import contextmanager
from Products.ERP5Type.XMLObject import XMLObject
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Timeout import Deadline, TimeoutReachedError
from Products.ERP5Type.UnrestrictedMethod import super_user
from zLOG import LOG, ERROR
from six import string_types as basestring

def isJson(header_dict):
  return header_dict.get('content-type', '').split(';', 1)[0] == 'application/json'

class TimeTracker(object):
  def __init__(self):
    self.__stack = []
    self.__history = []

  @contextmanager
  def __call__(self, reason):
    stack = self.__stack
    entry = [len(stack), reason, time.time(), None]
    stack.append(entry)
    self.__history.append(entry)
    try:
      yield
    finally:
      stack.pop()[3] = time.time()

  def __str__(self):
    return '\n'.join(
      '%s%s: %.3fs' % ('  ' * depth, reason, end - begin)
      for depth, reason, begin, end in self.__history
      if end is not None
    )

class RESTAPIClientConnectorMixin(XMLObject):
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)
  __EXPIRED_TOKEN = (0, None)

  # Credential scheme:
  # - primary credentials (client_id and client_secret) are persistent,
  #   set by admin on the connector instance
  # - refresh token is persistent on the connector instance, and is
  #   expected to virtually never change once set
  # - access token is volatile on connector instances
  #   so as to be per-ZODB.Connection. 2-tuple:
  #   - expiration timestamp
  #   - access token
  _v_access_token = __EXPIRED_TOKEN

  def _clearAccessToken(self):
    """
    Forget current access token, so next _getAccessToken call retrieves a new one.
    """
    self._v_access_token = self._EXPIRED_TOKEN

  def _call(self, method, path, header_dict=(), body=None):
    """
    body (None, string, json-serialisable objects)
      If body is not None and not a string, it is serialised in json,
      and the appropriate content-type is added to the headers.

    Returns a 3-tuple:
    - response header dict (header names lower-cased)
    - response body
      If response header content type is "application/json", the body
      is json-decoded before being returned
    - response status
    """
    header_dict = dict(header_dict)
    if body is not None and not isinstance(body, basestring):
      header_dict['content-type'] = 'application/json'
      body = json.dumps(body)
    plain_url = self.getBaseUrl().rstrip('/') + '/' + path.lstrip('/')
    parsed_url = urlparse(plain_url)
    ssl_context = ssl.create_default_context(
      cadata=self.getCaCertificatePem(),
    )
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.check_hostname = True
    bind_address = self.getBindAddress()
    if bind_address:
      bind_address = (bind_address, 0)
    time_left_before_timeout = getTimeLeft()
    http_connection = HTTPSConnection(
      host=parsed_url.hostname,
      port=parsed_url.port,
      timeout=time_left_before_timeout,
      source_address=bind_address,
      context=ssl_context,
    )
    request_start_time = time.time()
    http_connection.request(
      method=method,
      url=path,
      body=body,
      headers=header_dict,
    )

    try:
      http_response = http_connection.getresponse()
      request_stop_time = time.time()
    except ssl.SSLError as exc:
      if 'The read operation timed out' == exc.message:
        LOG(__name__, ERROR, "Call to %s %s raised Timeout (%ss)" %(
          method, path, round(time_left_before_timeout, 6)
        ), error=True)
        raise TimeoutReachedError
      raise
    except Exception:
      LOG(__name__, ERROR, "Call to %s %s raised after %ss" %(
          method, path, round(time_left_before_timeout, 6)
        ), error=True)
      raise

    response_body = http_response.read()
    response_header_dict = {
      name.lower(): value
      for name, value in http_response.getheaders()
    }
    if isJson(response_header_dict):
      response_body = json.loads(response_body)
    return (
      response_header_dict,
      response_body,
      http_response.status,
      request_stop_time - request_start_time,
    )

  security.declarePrivate('call')
  def call(
    self,
    archive_resource,
    method,
    path,
    header_dict=(),
    body=None,
    archive_kw=None,
    archive_document_relative_url=None,
    archive_value_list=None,
    timeout=None,
  ):
    # default timeout should be kept very low
    # to not block an instance with default zope configuration
    timeout = timeout if timeout is not None else self.getTimeout(1)
    original_header_dict = header_dict
    header_dict = dict(header_dict)
    time_tracker = TimeTracker()
    try:
      with time_tracker('call'), Deadline(timeout):
        # Limit numbers of retries, in case the authentication API succeeds
        # but the token is not usable.
        for _ in range(2):
          with time_tracker('token'):
            access_token = self._getAccessToken()
            if access_token is not None:
              header_dict['Authorization'] = 'Bearer ' + self._getAccessToken()
          with time_tracker('_call'):
            (
              response_header_dict,
              response_body,
              response_status,
              response_time_duration,
            ) = self._call(
              path=path,
              method=method,
              header_dict=header_dict,
              body=body,
            )
          if response_status == 401:
            self._clearAccessToken()
          else:
            # Success (or at least not an authentication failure), exit retry loop
            break
    except Exception:
      LOG(__name__, ERROR, str(time_tracker), error=True)
      raise
    if archive_resource is not None:
      archiveExchange = self._getTypeBasedMethod('archiveExchange')
      if archiveExchange is not None:
        with super_user():
          archiveExchange(
            resource_path=archive_resource,
            raw_request=(
              # XXX: how to avoid double request serialisation ?
              path
              if body is None else
              json.dumps(body)
            ),
            raw_response=(
              # XXX: how to avoid deserialisation and then re-serialisation ?
              response_body
              if isinstance(response_body, basestring) else
              json.dumps(response_body)
            ),
            time_duration=response_time_duration,
            archive_kw=archive_kw,
            archive_document_relative_url=archive_document_relative_url,
            archive_value_list=archive_value_list,
          )
    if response_status >= 300:
      __traceback_info__ = { # pylint: disable=unused-variable
        'request': {
          'method': method,
          'path': path,
          # Do not put authentication headers in logs
          'header_dict': original_header_dict,
          'body': body,
        },
        'response': {
          'header_dict': response_header_dict,
          'body': response_body,
          'status': response_status,
        },
      }
      raise self.ClientConnectorError(
        header_dict=response_header_dict,
        body=response_body,
        status=response_status,
      )
    return (
      response_header_dict,
      response_body,
      response_status,
    )
