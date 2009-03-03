# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
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

import socket
import time

from ExchangeProtocol import ExchangeProtocol

class TIDClient:
  def __init__(self, address):
    self._to_server = socket.socket()
    self._to_server.connect(address)
    self._exchange_protocol = ExchangeProtocol(self._to_server)

  def _dump(self, test_id=None):
    self._exchange_protocol.send_field('dump')
    received_dict = self._exchange_protocol.recv_dict()
    if test_id is None:
      result = received_dict
    else:
      id_len = len(test_id) + 1 # Add 1 to strip underscore.
      result = dict([(key[id_len:], value) \
                     for key, value in received_dict.iteritems() \
                     if key.startswith(test_id)])
    return dict([(key, int(value)) for key, value in result.iteritems()])

  def dump(self, test_id):
    return self._dump(test_id=test_id)

  def dump_all(self):
    return self._dump()

  def begin(self, test_id, transaction_id, storage_id_list):
    self._exchange_protocol.send_field('begin')
    self._exchange_protocol.send_field(transaction_id)
    internal_storage_id_list = ['%s_%s' % (test_id, x) \
                                for x in storage_id_list]
    self._exchange_protocol.send_list(internal_storage_id_list)

  def abort(self, test_id, transaction_id):
    self._exchange_protocol.send_field('abort')
    self._exchange_protocol.send_field(transaction_id)

  def commit(self, test_id, transaction_id, storage_tid_dict):
    self._exchange_protocol.send_field('commit')
    self._exchange_protocol.send_field(transaction_id)
    internal_storage_tid_dict = {}
    for key, value in storage_tid_dict.iteritems():
      internal_storage_tid_dict['%s_%s' % (test_id, key)] = value
    self._exchange_protocol.send_dict(internal_storage_tid_dict)

  def bootstraped(self):
    self._exchange_protocol.send_field('bootstraped')
    return self._exchange_protocol.recv_int()

  def waitForBootstrap(self):
    while not self.bootstraped():
      time.sleep(0.1)


