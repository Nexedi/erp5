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

from xmlrpc.client import ProtocolError
from xmlrpc.client import Transport
from xmlrpc.client import SafeTransport
import socket

class TimeoutTransport(SafeTransport):
  """A xmlrpc transport with configurable timeout.
  """
  def __init__(self, timeout=None, scheme='http'):
    SafeTransport.__init__(self)
    transport_class = Transport if scheme == 'http' else SafeTransport
    def make_connection(*args, **kw):
      connection = transport_class.make_connection(self, *args, **kw)
      if timeout is not None:
        connection.timeout = timeout
      return connection
    self.make_connection = make_connection

  def send_content(self, connection, request_body):
    try:
      return SafeTransport.send_content(self, connection, request_body)
    except socket.error:
      raise ProtocolError(connection.host, -1,
                          "Could not connect to server", None)
