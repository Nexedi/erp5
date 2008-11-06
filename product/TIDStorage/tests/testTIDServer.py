#!/usr/bin/python

from ExchangeProtocol import ExchangeProtocol
import traceback
import socket
import sys

assert len(sys.argv) == 3, 'Requires exactly 2 arguments: <address> <port>'

address = sys.argv[1]
port = int(sys.argv[2])

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

class TestTIDServerV2:
  def __init__(self, address, port):
    self._client = TIDClient((address, port))
 
  def assertEqual(self, value, target):
    assert value == target, 'value %r does not match target %r' % (value, target)
 
  def testInitialValue(self, test_id):
    """
      Check that the storage is empty
    """
    self.assertEqual(self._client.dump_all(), {})

  def testScenario1(self, test_id):
    """
      Simple begin - commit case.
    """
    storage_tid_dict = {'s1': 1}
    self.assertEqual(self._client.dump(test_id), {})
    self._client.begin(test_id, 't1', storage_tid_dict.keys())
    self.assertEqual(self._client.dump(test_id), {})
    self._client.commit(test_id, 't1', storage_tid_dict)
    self.assertEqual(self._client.dump(test_id), storage_tid_dict)

  def testScenario2(self, test_id):
    """
      Simple begin - abort case.
    """
    storage_tid_dict = {'s1': 1}
    self.assertEqual(self._client.dump(test_id), {})
    self._client.begin(test_id, 't1', storage_tid_dict.keys())
    self.assertEqual(self._client.dump(test_id), {})
    self._client.abort(test_id, 't1')
    self.assertEqual(self._client.dump(test_id), {})

  def testScenario3(self, test_id):
    """
      2 concurent transactions impacting a common storage.
      Second transaction begins after first does, and commits before
      first does.
    """
    t1_storage_tid_dict = {'s1': 1, 's2': 1}
    t2_storage_tid_dict = {'s1': 2, 's3': 1}
    self.assertEqual(self._client.dump(test_id), {})
    self._client.begin(test_id, 't1', t1_storage_tid_dict.keys())
    self.assertEqual(self._client.dump(test_id), {})
    self._client.begin(test_id, 't2', t2_storage_tid_dict.keys())
    self.assertEqual(self._client.dump(test_id), {})
    self._client.commit(test_id, 't2', t2_storage_tid_dict)
    self.assertEqual(self._client.dump(test_id), {})
    self._client.commit(test_id, 't1', t1_storage_tid_dict)
    self.assertEqual(self._client.dump(test_id), {'s1': 2, 's2': 1, 's3': 1})

  def testScenario4(self, test_id):
    """
      3 concurent transactions.
      Transactions 1 and 2 impact same storage s1.
      Transaction 3 impacts storage s3 after transaction 2 commited.
      Still, as storage 3  was part of a non-commitable-yet transaction,
      it must not be commited untill all blockable (here, t1) transaction have
      ended.
    """
    t1_storage_tid_dict = {'s1': 1, 's2': 2}
    t2_storage_tid_dict = {'s1': 2, 's3': 1}
    t3_storage_tid_dict = {'s3': 1}
    self.assertEqual(self._client.dump(test_id), {})
    self._client.begin(test_id, 't1', t1_storage_tid_dict.keys())
    self.assertEqual(self._client.dump(test_id), {})
    self._client.begin(test_id, 't2', t2_storage_tid_dict.keys())
    self.assertEqual(self._client.dump(test_id), {})
    self._client.commit(test_id, 't2', t2_storage_tid_dict)
    self.assertEqual(self._client.dump(test_id), {})
    self._client.begin(test_id, 't3', t3_storage_tid_dict.keys())
    self.assertEqual(self._client.dump(test_id), {})
    self._client.commit(test_id, 't3', t3_storage_tid_dict)
    self.assertEqual(self._client.dump(test_id), {})
    self._client.commit(test_id, 't1', t1_storage_tid_dict)
    self.assertEqual(self._client.dump(test_id), {'s1': 2, 's2': 2, 's3': 1})

  def testScenario4bis(self, test_id):
    """
      3 concurent transactions.
      Transactions 1 and 2 impact same storage s1.
      Transaction 3 impacts storage s3 after transaction 2 commited.
      Still, as storage 3  was part of a non-commitable-yet transaction,
      it must not be commited untill all blockable (here, t1) transaction have
      ended.
      In this version, t1 aborts: for example, tpc_vote failed. As the data
      was already sent to storage, it might be already present on disk (and
      anyway, tid is not to be used anymore), so it's valid for t2 to commit
      with tid 2 even if t1 aborted tid 1.
    """
    t1_storage_tid_dict = {'s1': 1, 's2': 2}
    t2_storage_tid_dict = {'s1': 2, 's3': 1}
    t3_storage_tid_dict = {'s3': 1}
    self.assertEqual(self._client.dump(test_id), {})
    self._client.begin(test_id, 't1', t1_storage_tid_dict.keys())
    self.assertEqual(self._client.dump(test_id), {})
    self._client.begin(test_id, 't2', t2_storage_tid_dict.keys())
    self.assertEqual(self._client.dump(test_id), {})
    self._client.commit(test_id, 't2', t2_storage_tid_dict)
    self.assertEqual(self._client.dump(test_id), {})
    self._client.begin(test_id, 't3', t3_storage_tid_dict.keys())
    self.assertEqual(self._client.dump(test_id), {})
    self._client.commit(test_id, 't3', t3_storage_tid_dict)
    self.assertEqual(self._client.dump(test_id), {})
    self._client.abort(test_id, 't1')
    self.assertEqual(self._client.dump(test_id), {'s1': 2, 's3': 1})

  def testScenario5(self, test_id):
    """
      2 concurent transactions impacting a common storage.
      Second transaction begins after first does, and commits after
      first does.
    """
    t1_storage_tid_dict = {'s1': 2}
    t2_storage_tid_dict = {'s1': 1, 's2': 1}
    self.assertEqual(self._client.dump(test_id), {})
    self._client.begin(test_id, 't1', t1_storage_tid_dict.keys())
    self.assertEqual(self._client.dump(test_id), {})
    self._client.begin(test_id, 't2', t2_storage_tid_dict.keys())
    self.assertEqual(self._client.dump(test_id), {})
    self._client.commit(test_id, 't1', t1_storage_tid_dict)
    self.assertEqual(self._client.dump(test_id), {})
    self._client.commit(test_id, 't2', t2_storage_tid_dict)
    self.assertEqual(self._client.dump(test_id), {'s1': 2, 's2': 1})

  def testScenario6(self, test_id):
    """
      2 concurent transactions impacting separate sets of storages.
      Check that the first commit impacts dump data immediately.
    """
    t1_storage_tid_dict = {'s1': 1}
    t2_storage_tid_dict = {'s2': 1}
    self.assertEqual(self._client.dump(test_id), {})
    self._client.begin(test_id, 't1', t1_storage_tid_dict.keys())
    self.assertEqual(self._client.dump(test_id), {})
    self._client.begin(test_id, 't2', t2_storage_tid_dict.keys())
    self.assertEqual(self._client.dump(test_id), {})
    self._client.commit(test_id, 't1', t1_storage_tid_dict)
    self.assertEqual(self._client.dump(test_id), {'s1': 1})
    self._client.commit(test_id, 't2', t2_storage_tid_dict)
    self.assertEqual(self._client.dump(test_id), {'s1': 1, 's2': 1})

  def testScenario7(self, test_id):
    """
      3 concurent transactions.
      t1 and t2 impact a set of different storages.
      t3 impacts a set of storage containing the ones from t1 and the ones
      from t2.
      Check that nothing impacts dump data until everything is commited.
    """
    t1_storage_tid_dict = {'s1': 1}
    t2_storage_tid_dict = {'s2': 2}
    t3_storage_tid_dict = {'s1': 2, 's2': 2}
    self.assertEqual(self._client.dump(test_id), {})
    self._client.begin(test_id, 't1', t1_storage_tid_dict.keys())
    self.assertEqual(self._client.dump(test_id), {})
    self._client.begin(test_id, 't2', t2_storage_tid_dict.keys())
    self.assertEqual(self._client.dump(test_id), {})
    self._client.begin(test_id, 't3', t3_storage_tid_dict.keys())
    self.assertEqual(self._client.dump(test_id), {})
    self._client.commit(test_id, 't1', t1_storage_tid_dict)
    self.assertEqual(self._client.dump(test_id), {})
    self._client.commit(test_id, 't2', t2_storage_tid_dict)
    self.assertEqual(self._client.dump(test_id), {})
    self._client.commit(test_id, 't3', t3_storage_tid_dict)
    self.assertEqual(self._client.dump(test_id), {'s1': 2, 's2': 2})

  def testScenario8(self, test_id):
    """
      Simple increase case.
    """
    self.assertEqual(self._client.dump(test_id), {})
    t1_storage_tid_dict = {}
    for s1_value in (1, 2):
      previous_t1_storage_tid_dict = t1_storage_tid_dict
      t1_storage_tid_dict = {'s1': s1_value}
      self._client.begin(test_id, 't1', t1_storage_tid_dict.keys())
      self.assertEqual(self._client.dump(test_id), previous_t1_storage_tid_dict)
      self._client.commit(test_id, 't1', t1_storage_tid_dict)
      self.assertEqual(self._client.dump(test_id), t1_storage_tid_dict)

  def run(self):
    for test_method_id in [x for x in dir(self) if x.startswith('test')]:
      self.log("Runing %s..." % (test_method_id, ))
      try:
        try:
          getattr(self, test_method_id)(test_id=test_method_id)
        except AssertionError:
          self.log('F\n')
          self.log('\n'.join(traceback.format_exception(*sys.exc_info())))
      finally:
        self.log('\n')

  def log(self, message):
    sys.stdout.write(message)

test = TestTIDServerV2(address, port)
test.run()

