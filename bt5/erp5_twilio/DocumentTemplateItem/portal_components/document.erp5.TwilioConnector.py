# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2024 Nexedi SA and Contributors. All Rights Reserved.
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
from requests.auth import HTTPBasicAuth

import json
import requests

from six.moves.urllib.parse import urljoin

from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type import Permissions
from Products.ERP5Type.Timeout import getTimeLeft

# Twilio API constants
TWILIO_API_BASE_URL = 'https://api.twilio.com/2010-04-01/'
TWILIO_MESSAGES_ENDPOINT = '/Accounts/{account_sid}/Messages.json'
DEFAULT_HTTP_TIMEOUT = 10

class TwilioConnector(XMLObject):
  meta_type = 'ERP5 Twilio Connector'
  portal_type = 'Twilio Connector'
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _getTimeout(self):
    """Compute the time left according to publisher deadline."""
    time_left = getTimeLeft()
    if time_left is None:
      time_left = DEFAULT_HTTP_TIMEOUT
    return min(self.getTimeout() or DEFAULT_HTTP_TIMEOUT, time_left)

  @security.private
  def _makeAPIRequest(self, method, endpoint, headers=None, data=None):
    """Make authenticated request to Twilio API."""
    method = method.upper()
    assert method in ("POST", "GET"), "Method not supported"
    url = urljoin(TWILIO_API_BASE_URL, endpoint.lstrip('/'))

    account_sid = self.getClientId()
    auth_token = self.getSecretKey()
    assert account_sid and auth_token, "Account SID and Auth Token must be configured"

    timeout = self._getTimeout()
    response = requests.request(
      method=method,
      auth=HTTPBasicAuth(account_sid, auth_token),
      url=url,
      data=data if method == 'POST' else None,
      params=data if method == 'GET' else None,
      headers=headers,
      timeout=timeout
    )

    return response

  def sendWhatsAppMessage(self, to_number, content_sid, content_variables=None):
    """Send WhatsApp message via Twilio API using template.

    Args:
      to_number: Recipient phone number (E.164 format)
      content_sid: Twilio template content SID
      content_variables: Dict of template variables to substitute

    Returns:
      dict: Response containing status, message_sid, error_code if any
    """
    account_sid = self.getClientId()
    assert account_sid, "Account SID not configured"
    endpoint = TWILIO_MESSAGES_ENDPOINT.format(account_sid=account_sid)

    from_number = self.getFromNumber()
    assert from_number, "From Number is missing"
    # Prepare message data
    message_data = {
      'To': 'whatsapp:{}'.format(to_number),
      'From': 'whatsapp:{}'.format(from_number),
      'ContentSid': content_sid
    }

    # Add template variables if provided
    if content_variables:
      content_variables_json = json.dumps(content_variables)
      message_data['ContentVariables'] = content_variables_json


    response = self._makeAPIRequest('POST', endpoint, data=message_data)
    response_data = response.json()
    result = {
      'status_code': response.status_code,
      'response_data': response_data,
      'success': response.status_code in (200, 201)
    }

    if result['success']:
      result['message_sid'] = response_data.get('sid')
      result['status'] = response_data.get('status')
    else:
      # Check for specific error codes
      error_code = response_data.get('code')
      result['error_code'] = str(error_code) if error_code else None
      result['error_message'] = response_data.get('message', 'Unknown error')

    return result