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
from urllib import urlencode
from urllib2 import URLError, HTTPError, Request, urlopen
from Products.ERP5Type.Tool.WebServiceTool import ConnectionError


class MethodWrapper(object):

  def __init__(self, method, conn):
    self._method = method
    self._conn = conn

  def __call__(self, *args, **kw):

    data_kw = {'Method' : self._method,
               'Token' : self._conn._password,
               'Data' : kw.get('data')}
    request_data = urlencode(data_kw)
    request = Request(self._conn.url, request_data)
    try:
      response = urlopen(request)
      return self._conn.url, response.read()
    except HTTPError as msg:
      error = "Impossible to access to the plugin, error code is %s - %s" %(msg.msg, msg.code,)
      raise ConnectionError(error)
    except URLError as msg:
      error = "Impossible to connect to the plugin, reason is %s" %(msg.reason,)
      raise ConnectionError(error)



class RESTConnection:
  """
    Holds a REST connection to a remote web server.
  """
  __allow_access_to_unprotected_subobjects__ = 1

  def __init__(self, url, user_name = None, password = None, credentials = None):
    """
    url (string)
      The requested url
    user_name (string or None)
    password (string is None)
      The transport-level (http) credentials to use.
    credentials (AuthenticationBase subclass instance or None)
      The interface-level (http) credentials to use.
    """
    self.url = url
    self._user_name = user_name
    self._password = password
    self._credentials = credentials

  def connect(self):
    """nothing to do here."""
    return self

  def __getattr__(self, name):
    if not name.startswith("_"):
      return MethodWrapper(name, self)



