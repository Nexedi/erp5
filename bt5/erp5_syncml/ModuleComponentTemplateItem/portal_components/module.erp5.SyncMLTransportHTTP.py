# -*- coding: utf-8 -*-
## Copyright (c) 2012 Nexedi SARL and Contributors. All Rights Reserved.
#          Aurélien Calonne <aurel@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from os import environ
from logging import getLogger
from requests import post

syncml_logger = getLogger('ERP5SyncML')

class ConnectionError(Exception):  # pylint:disable=redefined-builtin
  pass


class HTTPTransport:

  def getProxyMapping(self):
    """
    Return a mapping of protocol to proxy
    Based on environment variable
    """
    return {'http' : environ.get('http_proxy'),
            'https' : environ.get('https_proxy'),
            }

  def getHeaders(self, content_type, xml):
    """
    SyncML defined specifications about http bindings
    Follow advices given about headerds
    """
    return {
      # XXX- Syncml content-type is not supported by Zope server
      # for now disable it until ZServer get patched
      # 'Content-Type' : content_type,
      'Cache-control' : 'no-store',
      'Accept' : 'application/vnd.syncml+xml',
      'Accept-Charset' : 'UTF-8',
      'User-Agent' : 'ERP5SyncML Tool',
      }


  def send(self, to_url, data, sync_id, content_type):
    syncml_logger.debug("HTTP.send : %s", to_url)
    data = {
      'text' : data,
      'sync_id': sync_id
      }
    r = post(to_url,data=data,
             headers=self.getHeaders(content_type, data),
             timeout=60,
             proxies=self.getProxyMapping())
    syncml_logger.debug("Status code : %s - %s", r.status_code, r.headers)
    r.raise_for_status()
