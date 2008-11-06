############################################################################
#
# Copyright (c) 2007, 2008 Nexedi SARL and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
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

class ClientDisconnected(Exception):
  pass

class ExchangeProtocol:
  """
    Handle data exchange between client and server.
    Kinds of data which can be exchanged:
     - str
       send_field
       recv_field
     - int
       send_int
       recv_int
     - list of str
       send_list
       recv_list
     - list of int
       send_int_list
       recv_int_list
     - dict (key: str, value: int)
       send_dict
       recv_dict
    Forbidden chars:
      Send (raise if present):
        \\n (field separator)
      Receive (stripped silently):
        \\n (field separator)
        \\r (for compatibility)
  """
  def __init__(self, socket):
    self._socket = socket

  def send_field(self, to_send):
    if type(to_send) is not str:
      raise ValueError, 'Value is not of str type: %r' % (type(to_send), )
    if '\n' in to_send:
      raise ValueError, '\\n is a forbidden value.'
    self._socket.send(to_send)
    self._socket.send('\n')

  def recv_field(self):
    received = None
    result = []
    append = result.append
    while received != '\n':
      received = self._socket.recv(1)
      if len(received) == 0:
        raise ClientDisconnected
      if received != '\r':
        append(received)
    return ''.join(result[:-1])

  def send_int(self, to_send):
    self.send_field(str(to_send))

  def recv_int(self):
    return int(self.recv_field())

  def send_list(self, to_send, send_length=True):
    assert isinstance(to_send, (tuple, list))
    if send_length:
      self.send_int(len(to_send))
    for field in to_send:
      self.send_field(field)

  def send_int_list(self, to_send, *args, **kw):
    self.send_list([str(x) for x in to_send], *args, **kw)

  def recv_list(self, length=None):
    result = []
    append = result.append
    if length is None:
      length = int(self.recv_field())
    for field_number in xrange(length):
      append(self.recv_field())
    return result

  def recv_int_list(self, *args, **kw):
    return [int(x) for x in self.recv_list(*args, **kw)]

  def send_dict(self, to_send):
    """
      Key: string
      Value: int
    """
    assert isinstance(to_send, (dict))
    if len(to_send) == 0:
      key_list = value_list = []
    else:
      key_list, value_list = zip(*to_send.items())
    self.send_list(key_list)
    self.send_int_list(value_list, send_length=False)

  def recv_dict(self):
    """
      Key: string
      Value: int
    """
    key_list = self.recv_list()
    value_list = self.recv_int_list(len(key_list))
    result = dict(zip(key_list, value_list))
    return result

