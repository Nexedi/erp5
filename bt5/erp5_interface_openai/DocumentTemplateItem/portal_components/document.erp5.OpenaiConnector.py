# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2025 Nexedi SA and Contributors. All Rights Reserved.
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

import requests
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.XMLObject import XMLObject


class OpenaiConnector(XMLObject):
  # CMF Type Definition
  meta_type = 'ERP5 Openai Connector'
  portal_type = 'Openai Connector'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _getBaseUrl(self):
    url = self.getUrlString() or 'https://api.openai.com/v1'
    return url.rstrip('/')

  security.declarePublic('getResponse')
  def getResponse(self, prompt, attachment_data=None, attachment_filename=None,
                  attachment_media_type='application/pdf', model='gpt-4o'):
    api_key = self.getPassword()
    base_url = self._getBaseUrl()
    auth_headers = {'Authorization': 'Bearer %s' % api_key}

    file_id = None
    try:
      if attachment_data is not None:
        fname = attachment_filename or 'attachment.pdf'
        upload_resp = requests.post(
          base_url + '/files',
          headers=auth_headers,
          files={'file': (fname, attachment_data, attachment_media_type)},
          data={'purpose': 'user_data'},
          timeout=120,
        )
        upload_resp.raise_for_status()
        file_id = upload_resp.json()['id']
        messages = [
          {
            'role': 'user',
            'content': [
              {'type': 'text', 'text': prompt},
              {'type': 'file', 'file': {'file_id': file_id}},
            ],
          }
        ]
      else:
        messages = [{'role': 'user', 'content': prompt}]

      chat_headers = dict(auth_headers)
      chat_headers['Content-Type'] = 'application/json'
      chat_resp = requests.post(
        base_url + '/chat/completions',
        headers=chat_headers,
        json={'model': model, 'messages': messages},
        timeout=120,
      )
      chat_resp.raise_for_status()
      return chat_resp.json()['choices'][0]['message']['content']

    finally:
      if file_id is not None:
        try:
          requests.delete(
            base_url + '/files/' + file_id,
            headers=auth_headers,
            timeout=30,
          )
        except Exception:
          pass
