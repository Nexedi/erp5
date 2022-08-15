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

import requests
import urllib

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

  def buildLineKey(self, prefix, key_list):
    for key in key_list:
      prefix += "[%s]" % key
    return prefix
  
  def buildLine(self, data_dict, prefix, key_list, value):
    if not isinstance(value, dict):
      data_dict[self.buildLineKey(prefix, key_list)] = value
    elif isinstance(value, dict):
      for subkey, subvalue in value.items():
        self.buildLine(data_dict, prefix, key_list + [subkey,], subvalue)
 
  def buildLineItemList(self, prefix, line_item_list):
    data_dict = {}
    for key, value in enumerate(line_item_list):
      self.buildLine(data_dict, prefix, [key,], value)
    return data_dict

  def createSession(self, data, **kw):
    """
      Create Session in Stripe using Stripe API and return a checkout.session      
    """
    end_point = "checkout/sessions"
    # copy data, other we will change the real data request
    request_data = data.copy()

    if "mode" not in request_data:
      request_data["mode"] = "payment"

    header_dict = {
      'Content-Type': 'application/x-www-form-urlencoded',
    }
    header_dict.update(kw.get("extra_header") or {})
    url_string = self.getUrlString()
    if not url_string.endswith("/"):
      url_string += "/"
    url_string += end_point
    line_item_list = request_data.pop("line_items")
    request_data.update(self.buildLineItemList("line_items", line_item_list))
    response = requests.post(
      url_string,
      headers=header_dict,
      data=urllib.urlencode(request_data),
      auth=((self.getDescription() or "").strip(), ''),
      timeout=TIMEOUT)
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
      headers={
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      auth=((self.getDescription() or "").strip(), ''),
      timeout=TIMEOUT)
    return response.json()