##############################################################################
#
# Copyright (c) 2026 Nexedi SA and Contributors. All Rights Reserved.
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

import json
import ssl

from collections import defaultdict

from six.moves.http_client import HTTPSConnection
from six.moves.urllib.parse import (
  urlencode,
  urljoin,
  urlparse
)
from oauthlib.oauth2 import BackendApplicationClient
import zope.interface

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Timeout import getTimeLeft
from Products.ERP5Type.Utils import bytes2str
from Products.ERP5Type.XMLObject import XMLObject

from erp5.component.interface.IElectronicInvoicingConnector import IElectronicInvoicingConnector

@zope.interface.implementer(IElectronicInvoicingConnector)
class SuperPDPInvoicingConnector(XMLObject):
  """
  Connector for SuperPDP eInvoicing API using OAuth2 authentication.
  """

  meta_type = 'ERP5 SuperPDP Invoicing Connector'
  portal_type = 'SuperPDP Invoicing Connector'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Reference
                    , PropertySheet.Arrow )

  def _callHTTP(self, method, url, header_dict=(), body='', caption=None, source_host=''):
    parsed_url = urlparse(url)
    # Changed in version 3.4.3: HTTPSConnection class now performs all the
    # necessary certificate and hostname checks by default. We want to support
    # earlier Python versions.
    ssl_context = ssl.create_default_context(cadata=None)
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.check_hostname = True
    timeout = getTimeLeft()
    my_timeout = self.getTimeout()
    if timeout is None or timeout > my_timeout:
      timeout = my_timeout
    http_connection = HTTPSConnection(
      context=ssl_context,
      host=parsed_url.hostname,
      port=parsed_url.port,
      timeout=timeout,
      source_address=(source_host, 0),
    )
    http_connection.request(
      method=method,
      url=url,
      body=body,
      headers=dict(header_dict),
    )
    http_response = http_connection.getresponse()
    header_dict = defaultdict(list)
    for name, value in http_response.getheaders():
      header_dict[name.lower()].append(value)
    result = (
      dict(header_dict),
      http_response.read(),
      http_response.status,
    )
    http_connection.close()
    return result

  def _getToken(self):
    url = urljoin(self.getBindAddress(), "/oauth2/token")
    oauth_client = BackendApplicationClient(self.getReference())
    url, header_dict, body = oauth_client.prepare_token_request(
      token_url=url,
      include_client_id=True,
      client_secret=self.getClientSecret(),
    )
    # IMPORTANT: returned header_dict is mutable but is a singleton returned on
    # every call. DO NOT MUTATE IT!
    header_dict = {
      x.encode('ascii'): y.encode('ascii')
      for x, y in header_dict.items()
    }
    header_dict, body, status_code = self._callHTTP(
      method='POST' if body else 'GET',
      url=url,
      header_dict=header_dict,
      body=body.encode('utf-8'),
    )
    if status_code != 200:
      raise ValueError("Error while getting token")
    return oauth_client.parse_request_body_response(body=body)

  def getIncomingInvoiceList(self):
    """
    List incoming (Purchase) invoices.
    """
    access_token = self._getToken()["access_token"]
    header_dict = {
      "Accept": "application/json",
      "Content-Type": "application/json",
      "Authorization": "Bearer %s" % access_token,
    }
    query_params = {
      "direction": "in",
    }
    query_params = "?" + urlencode(query_params)
    url = urljoin(urljoin(self.getBindAddress(), "/v1.beta/invoices"), query_params)

    header_dict, body, status_code = self._callHTTP(
      method="GET",
      url=url,
      header_dict=header_dict,
    )
    if status_code != 200:
      raise ValueError()
    return json.loads(bytes2str(body))["data"]

  def getInvoice(self, invoice_id):
    """
    Get an invoice with a specific id.
    """
    access_token = self._getToken()["access_token"]
    header_dict = {
      "Accept": "application/json",
      "Content-Type": "application/json",
      "Authorization": "Bearer %s" % access_token,
    }
    url = urljoin(urljoin(self.getBindAddress(), "/v1.beta/invoices/"), str(invoice_id))
    header_dict, body, status_code = self._callHTTP(
      method="GET",
      url=url,
      header_dict=header_dict,
    )
    if status_code != 200:
      raise ValueError()
    return bytes2str(body)

  def getInvoiceAsJson(self, invoice_id):
    """
    XXX: remove this method. Debug only.
    """
    return json.dumps(json.loads(self.getInvoice(invoice_id)), indent=2)