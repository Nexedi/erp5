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


