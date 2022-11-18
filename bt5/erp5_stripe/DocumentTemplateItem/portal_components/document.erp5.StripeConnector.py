##############################################################################
#
# Copyright (c) 2022 Nexedi SARL and Contributors. All Rights Reserved.
#                    Gabriel Monnerat <gabriel@nexedi.com>
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

from six.moves import urllib

import requests
import six

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject

TIMEOUT = 10 # 10 seconds

class StripeConnector(XMLObject):
  """
    Holds an Stripe connection to a remote Stripe API.
  """
  # CMF Type Definition
  meta_type = 'Stripe Connector'
  portal_type = 'Stripe Connector'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.XMLObject,
    PropertySheet.CategoryCore,
    PropertySheet.DublinCore
  )

  def serializeSessionParameter(self, request_data, key, value):
    if isinstance(value, list) or isinstance(value, dict):
      iterator = six.iteritems(value) if isinstance(value, dict) else enumerate(value)
      for subkey, subvalue in iterator:
        self.serializeSessionParameter(
          request_data,
          "{}[{}]".format(key, subkey),
          subvalue)
    else:
      request_data[key] = value

  def createSession(self, data, **kw):
    """
      Create Session in Stripe using Stripe API and return a checkout.session

      data is a dict, see https://stripe.com/docs/api/checkout/sessions/create
    """
    end_point = "checkout/sessions"
    header_dict = {
      'Content-Type': 'application/x-www-form-urlencoded',
    }
    url_string = self.getUrlString()
    if not url_string.endswith("/"):
      url_string += "/"
    url_string += end_point
    request_data = {}
    for key, value in six.iteritems(data):
      self.serializeSessionParameter(request_data, key, value)

    if "mode" not in request_data:
      request_data["mode"] = "payment"

    response = requests.post(
      url_string,
      headers=header_dict,
      data=urllib.parse.urlencode(request_data),
      auth=((self.getPassword() or "").strip(), ''),
      timeout=self.getTimeout() or TIMEOUT)
    if not response.ok:
      __traceback_info__ = ( # pylint:disable=unused-variable
        response.request.url,
        response.request.body,
        response.text
      )
      response.raise_for_status()
    return response.json()

  def retrieveSession(self, session_id, **kw):
    """
      Retrieve Session in Stripe using Stripe API and return a checkout.session
    """
    url_string = self.getUrlString()
    if not url_string.endswith("/"):
      url_string += "/"
    url_string += "checkout/sessions/%(session_id)s" % {"session_id": session_id}
    response = requests.get(
      url_string,
      auth=((self.getPassword() or "").strip(), ''),
      timeout=self.getTimeout() or TIMEOUT)
    if not response.ok:
      __traceback_info__ = ( # pylint:disable=unused-variable
        response.request.url,
        response.request.body,
        response.text
      )
      response.raise_for_status()
    return response.json()
