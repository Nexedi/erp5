##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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

from xmlrpclib import Fault, ProtocolError
from xmlrpclib import Transport
from xmlrpclib import SafeTransport
import socket

class TimeoutTransport(SafeTransport):
  """A xmlrpc transport with configurable timeout.
  """
  def __init__(self, timeout=None, scheme='http'):
    self._timeout = timeout
    self._scheme = scheme
    SafeTransport.__init__(self)

  def send_content(self, connection, request_body):
    try:
      connection.putheader("Content-Type", "text/xml")
      connection.putheader("Content-Length", str(len(request_body)))
      connection.endheaders()
      if self._timeout:
        connection._conn.sock.settimeout(self._timeout)
      if request_body:
        connection.send(request_body)
    except socket.error, e:
      raise ProtocolError(connection._conn.host, -1,
                          "Could not connect to server", None)

  def make_connection(self, host):
    try:
      if self._scheme == 'http':
        return Transport.make_connection(self, host)
      return SafeTransport.make_connection(self, host)
    except socket.error, e:
      raise ProtocolError(host, -1, "Could not connect to server", None)
