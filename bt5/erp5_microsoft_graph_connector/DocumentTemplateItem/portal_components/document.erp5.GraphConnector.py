# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Nexedi SA and Contributors. All Rights Reserved.
#                    Aurélien Calonne <aurel@nexedi.com>
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
from Products.ERP5Type.XMLObject import XMLObject
import requests

class GraphConnector(XMLObject):

  def getConnectionHeaders(self, client_id=None, client_secret=None, tenant_id=None):

    token_url = "https://login.microsoftonline.com/%s/oauth2/v2.0/token" %tenant_id
    token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    token_params = {
      'grant_type': 'client_credentials',
      'client_id': client_id,
      'scope': 'https://graph.microsoft.com/.default',
      'client_secret': client_secret,
    }

    token_request = requests.post(token_url, headers=token_headers, data=token_params)
    token = token_request.json()
    access_token = token["access_token"]

    headers = {'Content-Type': 'application/json',
               'Authorization': access_token}

    return headers
