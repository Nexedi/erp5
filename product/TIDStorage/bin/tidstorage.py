#!/usr/bin/python

##############################################################################
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

# About errors in TIDStorage logs:
# - CRITICAL: Decreasing update ignored
#   This error means that any backup started prior to this error can contain
#   incomplete transaction data.
#   This error can happen when TIDStorage did not handle received data in the
#   right order.
#   Example:
#     3 storages (S1, S2, S3):
#       They all start at TID=1 value.
#     2 transaction (T1, T2):
#       T1 commits TID 3 on S2, TID 2 on S3
#       T2 commits TID 2 on S1, TID 2 on S2
#     Due to those TIDs, TIDStorage *should* handle data in this order:
#       T2begin, T2commit, T1begin, T1commit
#     Or:
#       T2begin, T1begin, T2commit, T1commit
#     Or even, though it denotes a late handling of T2commit:
#       T2begin, T1begin, T1commit, T2commit
#     But, if TIDStorage handles data in the following order:
#       T1begin, T1commit, T2begin, T2commit
#     *AND* a backup dumps TIDStorage content at a point between T1commit and
#     T2commit, then the backup will contain T2's commit on S2, which has a
#     lower TID than T1's commit on that same storage.
#
# - Abort received, but never began
# and
# - Commit received, but never began
#   These erros means that packets were lost/never received.
#   This should not happen, since network connection is TCP, and TCP
#   retransmits data.
#   But it happens frequently if TIDStorage is started when Zope is under
#   load. This is because Zope attemped to contact TIDStorage at "begin"
#   step, but could not reach it. Then, at commit (or abort) it could reach
#   TIDStorage, causing the error message.
#   This error is bening, because:
#     - Until bootstrap is complete, no TID is available for backup
#     - When bootstrap is complete, it means that every ZODB got unlocked
#       at some point (since TIDStorage commit happens after ZODB tpc_finish
#       lock release).
#     - When a transaction sends data to multiple ZODBs, there is a point in
#       time when ALL impacted ZODBs are locked.
#     The conclusion of all this is that any transaction started before
#     TIDStorage was available has necesarily finished (commit or abort) at
#     the time bootstrap finished.
#     So no backup can be affected by such message (but backup feasability can
#     get delayed as locks would delay bootstrap end, and hence TID data
#     availability).

import os
import imp
import sys
import pwd
import grp
import sets
import time
import urllib
import socket
import signal
import getopt
import SocketServer
import threading
import traceback
from ExchangeProtocol import ClientDisconnected, ExchangeProtocol

class TransactionException(Exception):
  pass

class AlwaysIncreasingDict(dict):
  """
    When inserting/updating a value, check that the new one is strictly
    greater than existing key (or integer 0 value if no value existed for
    given key).
    Values are converted to integers before comparison.
    
    TODO:
     - Do not descend from dict to prevent users from avoiding checks.
  """
  def __init__(self, strict=False, *args, **kw):
    dict.__init__(self, *args, **kw)
    self._strict = strict
 
  def __setitem__(self, key, value):
    if self.get(key, 0) < value:
      dict.__setitem__(self, key, value)
    else:
      if self._strict:
        log('CRITICAL: Decreasing update ignored: key=%r %r <= %r' % \
            (key, value, self.get(key, 0)))

  def update(self, other):
    """
      To check for decreases.
    """
    for key, value in other.iteritems():
      self[key] = value
 
class TransactionTracker:
  """
    Implement transaction tracking.
    This class is not thread-safe.
    A transaction starts with a call to "begin" and ends with a call to
    "finish" with the same identifier.
    "finish" returns payload provided at begin (or True if no payload was
    given) if nothing illegal was detected, otherwise returns False.

    Illegal cases:
     - "begin" called twice without intermediate "finish" call
     - "finish" called without a corresponding "begin" call (this includes
       calling "finish" twice)
  """
  def __init__(self):
    self._container = {}

  def begin(self, identifier, payload=True):
    if identifier in self._container:
      raise TransactionException, 'Begin called twice in a row.'
    self._container[identifier] = payload

  def finish(self, identifier):
    if identifier not in self._container:
      raise TransactionException, 'Finish called without former "begin" call.'
    return self._container.pop(identifier)

class TIDServer(SocketServer.BaseRequestHandler):
  """
    Exchange data with connected peer.

    TODO:
     - Implement socket buffering.
  """
  def log(self, message):
    log('%r: %s' % (self.client_address, message))

  def dump(self):
    tid_dict = self._tid_storage.dump()
    self._field_exchange.send_dict(tid_dict)

  def begin(self):
    identifier = self._field_exchange.recv_field()
    storage_id_list = self._field_exchange.recv_list()
    self._tid_storage.begin(identifier, storage_id_list)

  def abort(self):
    identifier = self._field_exchange.recv_field()
    self._tid_storage.abort(identifier)

  def commit(self):
    identifier = self._field_exchange.recv_field()
    tid_dict = self._field_exchange.recv_dict()
    self._tid_storage.commit(identifier, tid_dict)

  def bootstraped(self):
    self._field_exchange.send_int(has_bootstraped and 1 or 0)

  def handle(self):
    global tid_storage
    self._tid_storage = tid_storage
    self._field_exchange = ExchangeProtocol(socket=self.request)
    command_mapping = {
      'begin': self.begin,
      'abort': self.abort,
      'commit': self.commit,
      'dump': self.dump,
      'bootstraped': self.bootstraped,
    }
    self.log('Connected')
    try:
      # Intercept ClientDisconnected exception to stop thread nicely instead
      # of crashing.
      # Log all others exceptions.
      while True:
        received = self._field_exchange.recv_field()
        command_str = received.lower()
        if command_str == 'quit':
          break
        method = command_mapping.get(command_str)
        if method is not None:
          # Intercept all errors to log it instead of causing disconnection.
          # Except, of course, the ClientDisconnected exception itself.
          try:
            method()
          except ClientDisconnected:
            raise
          except:
            self.log('\n'.join(traceback.format_exception(*sys.exc_info())))
    except ClientDisconnected:
      pass
    except:
      self.log('\n'.join(traceback.format_exception(*sys.exc_info())))
    self.log('Client disconnected')
    self.request.shutdown(socket.SHUT_RDWR)
    self.request.close()
    return

class TIDStorage:
  """
    Store ZODB TIDs for multiple ZODBs.
    Designed to be a singleton.
    Thread-safe.
    
    Consequently, transactions are not bound to a specific connection: If a
    connection is cut after a "begin", reconnecting and issuing "abort" or
    "commit" is valid.

    TODO:
     - Use smaller locking areas
     - Improve decision taking algorythm in _unregisterTransactionID (implies
       modifying _registerTransactionIDAndStorageID).
  """
  _storage_id_lock = threading.RLock()
  _next_full_dump = None
  _next_dump = None
  _tid_file = None
  _burst_period = None
  _full_dump_period = None
  
  def __init__(self, tid_file_path=None, burst_period=None, full_dump_period=None):
    self._transaction_tracker = TransactionTracker()
    self._storage = AlwaysIncreasingDict(strict=True)
    self._transcient = AlwaysIncreasingDict()
    self._storage_id_to_transaction_id_list_dict = {}
    self._transaction_id_to_storage_id_list_dict = {}
    self._storage_id_to_storage_id_set_dict = {}
    if tid_file_path is not None:
      self._tid_file = openTIDLog()
      self._burst_period = burst_period
      self._full_dump_period = full_dump_period
      now = time.time()
      if full_dump_period is not None:
        self._next_full_dump = now
      if burst_period is not None:
        self._next_dump = now
        self._since_last_burst = sets.Set()

  def __repr__(self):
    result = []
    append = result.append
    self._storage_id_lock.acquire()
    try:
      append('_storage_id_to_transaction_id_list_dict=' + \
             repr(self._storage_id_to_transaction_id_list_dict))
      append('_transaction_id_to_storage_id_list_dict=' + \
             repr(self._transaction_id_to_storage_id_list_dict))
      append('_storage_id_to_storage_id_set_dict=' + \
             repr(self._storage_id_to_storage_id_set_dict))
      append('_transcient=' + repr(self._transcient))
      append('_storage=' + repr(self._storage))
    finally:
      self._storage_id_lock.release()
    return '\n'.join(result)

  def _registerTransactionIDAndStorageID(self, transaction_id, storage_id_list):
    assert len(storage_id_list) != 0
    assert self._storage_id_lock.acquire(False)
    try:
      # Update transaction_id -> storage_id_list
      assert transaction_id not in self._transaction_id_to_storage_id_list_dict
      self._transaction_id_to_storage_id_list_dict[transaction_id] = storage_id_list
      storage_id_set = sets.Set(storage_id_list)
      storage_id_set_id_set = sets.Set()
      for storage_id in storage_id_list:
        # Update storage_id -> transaction_id_list
        identifier_set = self._storage_id_to_transaction_id_list_dict.get(storage_id)
        if identifier_set is None:
          identifier_set = self._storage_id_to_transaction_id_list_dict[storage_id] = sets.Set()
        assert transaction_id not in identifier_set
        identifier_set.add(transaction_id)
        # Prepare the update storage_id -> storage_id_set
        existing_storage_id_set = self._storage_id_to_storage_id_set_dict.get(storage_id, None)
        if existing_storage_id_set is not None:
          storage_id_set.union_update(existing_storage_id_set)
          storage_id_set_id_set.add(id(existing_storage_id_set))
      # Update storage_id -> storage_id_set
      # Cannot use iteritems because dict is modified in the loop.
      for key, value in self._storage_id_to_storage_id_set_dict.items():
        if id(value) in storage_id_set_id_set:
          self._storage_id_to_storage_id_set_dict[key] = storage_id_set
      for storage_id in storage_id_set:
        self._storage_id_to_storage_id_set_dict[storage_id] = storage_id_set
    finally:
      self._storage_id_lock.release()

  def _unregisterTransactionID(self, transaction_id):
    """
      Also transfers from self._transcient to self._storage.
    """
    assert self._storage_id_lock.acquire(False)
    try:
      # Update transaction_id -> storage_id_list and retrieve storage_id_list
      # Raises if not found
      storage_id_list = self._transaction_id_to_storage_id_list_dict.pop(transaction_id)
      # Update storage_id -> transaction_id_list
      for storage_id in storage_id_list:
        identifier_set = self._storage_id_to_transaction_id_list_dict[storage_id]
        # Raises if not found
        identifier_set.remove(transaction_id)
        if len(identifier_set) == 0:
          del self._storage_id_to_transaction_id_list_dict[storage_id]
          # Update storage_id -> storage_id_set
          # Raises if not found
          storage_id_set = self._storage_id_to_storage_id_set_dict[storage_id]
          # Raises if not found
          storage_id_set.remove(storage_id)
      if has_bootstraped:
        if self._tid_file is not None:
          now = time.time()
          can_full_dump = (self._next_full_dump is not None) and (self._next_full_dump < now)
          can_dump = (not can_full_dump) and (self._next_dump is not None) and (self._next_dump < now)
          record_for_dump = can_dump or (self._next_dump is not None)
          append_to_file = (can_dump or can_full_dump)
        else:
          append_to_file = record_for_dump = can_dump = can_full_dump = False
        for key, value in self._storage_id_to_storage_id_set_dict.iteritems():
          if len(value) == 0 and key in self._transcient:
            self._storage[key] = self._transcient.pop(key)
            if record_for_dump:
              self._since_last_burst.add(key)
        if append_to_file:
          if can_full_dump:
            to_dump_dict = self._storage
            dump_code = 'f'
          else:
            to_dump_dict = dict([(key, self._storage[key]) for key in self._since_last_burst])
            dump_code = 'd'
          if len(to_dump_dict):
            self._tid_file.write('%.02f %s %r\n' % (now, dump_code, to_dump_dict))
            if can_full_dump:
              self._next_full_dump = now + self._full_dump_period
            if self._next_dump is not None:
              self._next_dump = now + self._burst_period
              self._since_last_burst.clear()
      else:
        doBootstrap()
    finally:
      self._storage_id_lock.release()

  def dump(self):
    self._storage_id_lock.acquire()
    try:
      return self._storage.copy()
    finally:
      self._storage_id_lock.release()

  def dump_transcient(self):
    self._storage_id_lock.acquire()
    try:
      return self._transcient.copy()
    finally:
      self._storage_id_lock.release()

  def begin(self, transaction_id, storage_id_list):
    self._storage_id_lock.acquire()
    try:
      self._transaction_tracker.begin(transaction_id, storage_id_list)
      self._registerTransactionIDAndStorageID(transaction_id, storage_id_list)
    finally:
      self._storage_id_lock.release()

  def abort(self, transaction_id):
    self._storage_id_lock.acquire()
    try:
      try:
        self._transaction_tracker.finish(transaction_id)
      except TransactionException:
        # Overwrite exception message
        raise TransactionException, 'Abort received, but never began'
      self._unregisterTransactionID(transaction_id)
    finally:
      self._storage_id_lock.release()

  def commit(self, transaction_id, tid_dict):
    self._storage_id_lock.acquire()
    try:
      try:
        storage_id_list = self._transaction_tracker.finish(transaction_id)
      except TransactionException:
        # Overwrite exception message
        raise TransactionException, 'Commit received, but never began'
      check_dict = tid_dict.copy()
      for storage_id in storage_id_list:
        del check_dict[storage_id]
      assert len(check_dict) == 0
      self._transcient.update(tid_dict)
      self._unregisterTransactionID(transaction_id)
    finally:
      self._storage_id_lock.release()

class BootstrapContent(threading.Thread):
  """
    Thread used to bootstrap TIDStorage content.
    This must be started at first client request, and must be run only once.
    Global boolean "has_bootstraped" is set to true once it succeeded.
  """

  def __init__(self, *args, **kw):
    threading.Thread.__init__(self, *args, **kw)
    self.setDaemon(True)

  def run(self):
    """
      Contact all zopes to serialize all their storages.
    """
    global has_bootstraped
    base_url = options.base_url
    if base_url is not None:
      log('Bootstrap started')
      storage_id_to_object_path_dict = {}
      for key, value in options.known_tid_storage_identifier_dict.iteritems():
        mountpoint = value[2]
        if mountpoint is None:
          log('Skipping bootstrap of storage %s because its mountpoint is unknown.' % (key, ))
        else:
          storage_id_to_object_path_dict[key] = mountpoint
      target_storage_id_set = sets.ImmutableSet(storage_id_to_object_path_dict.keys())
      known_storage_id_set = sets.ImmutableSet(tid_storage.dump_transcient().keys())
      to_check_storage_id_set = target_storage_id_set - known_storage_id_set
      while len(to_check_storage_id_set) and can_bootstrap:
        serialize_url = None
        for storage_id in to_check_storage_id_set:
          if can_bootstrap and storage_id not in tid_storage.dump_transcient().keys():
            serialize_url = base_url % (storage_id_to_object_path_dict[storage_id], )
            try:
              # Query a Zope, which will contact this process in return to store
              # the new TID number, making the given storage known.
              page = urllib.urlopen(serialize_url)
            except Exception, message:
              log('Exception during bootstrap (%r):\n%s' % (serialize_url, ''.join(traceback.format_exception(*sys.exc_info()))))
            else:
              log('Opened %r: %r' % (serialize_url, page.read()))
        # Let some time for zope to contact TIDStorage back and fill the gaps.
        time.sleep(5)
        known_storage_id_set = sets.ImmutableSet(tid_storage.dump_transcient().keys())
        to_check_storage_id_set = target_storage_id_set - known_storage_id_set
        if len(to_check_storage_id_set):
          log('Bootstrap in progress... Missing storages: %r' % (to_check_storage_id_set, ))
          # Retry a bit later
          time.sleep(60)
      if len(to_check_storage_id_set) == 0:
        log('Bootstrap done (%i storages).' % (len(target_storage_id_set), ))
        has_bootstraped = True
    else:
      log('Bootstrap did not happen because base_url was not given.')
      has_bootstraped = True

bootstrap_content = BootstrapContent()
has_bootstraped = False
can_bootstrap = True
bootstrap_lock = threading.RLock()

def doBootstrap():
  acquired = bootstrap_lock.acquire(False)
  if acquired:
    try:
      if not bootstrap_content.isAlive():
        bootstrap_content.start()
    finally:
      bootstrap_lock.release()

def log(message):
  print >> sys.stdout, '%s: %s' % (time.asctime(), message)

class PoliteThreadingTCPServer(SocketServer.ThreadingTCPServer):
  daemon_threads = True
  allow_reuse_address = True

def main(address, port):
  server = PoliteThreadingTCPServer((address, port), TIDServer)
  try:
    try:
      log('Server listening.')
      server.serve_forever()
    except KeyboardInterrupt:
      log('Shuting down (received KeyboardInterrupt).')
  finally:
    global can_bootstrap
    can_bootstrap = False
    server.server_close()

def openLog():
  return open(options.logfile_name, 'a', 0)

def openTIDLog():
  return open(options.status_file, 'a', 0)

def HUPHandler(signal_number, stack):
  log('Rotating logfile...')
  sys.stdout = sys.stderr = openLog()
  log('Logfile rotated')

def USR1Handler(signal_number, stack):
  log(repr(tid_storage))

def TERMHandler(signal_number, stack):
  log('Received SIGTERM, exiting.')
  raise KeyboardInterrupt, 'Killed by SIGTERM'

def usage():
  print """
Usage: %(arg0)s [-h] [-n|--nofork|--fg] [-l|--log] [-p|--port] [-a|--address]
       [--pidfile] [--user] [--group] [-s|--status-file] [-b|--burst-period]
       [-F|--full-dump-period] [-c|--config]

  -h
    Display this help.

  -n
  --nofork
  --fg
    Do not fork in background.

  -l filename
  --log filename
    Log to given filename, instead of default %(logfile_name)s.

  -p number
  --port number
    Listen to given port number, intead of default %(port)i.

  -a address
  --address address
    Listen to interface runing given address, instead of default %(address)s.

  --pidfile file_path
    If forking, this file will contain the pid of forked process.
    If this argument is not provided, pid is written to %(pidfile_name)s.

  --user user_name
    Run as specified user.
    Also, retrieve user's group and run as this group.

  --group group_name
    Run as specified group.
    If both --user and --group are specified, --group must come last.

  -s file_name
  --status-file file_name
    Append stored TIDs to file.
    See also "burst-period" and "full-dump-period".
    If not provided, no dump ever happens.

  -b seconds
  --burst-period seconds
    Defines the age of last write after which an incremental write can happen.
    Such write only contain what changed since last write.
    If not provided, no incremental write is done.

  -F seconds
  --full-dump-period seconds
    How many seconds must separate complete dumps to status file.
    Those writes contain the complete current state.
    If both a full dump and an incremental write can happen, full dump takes
    precedence.
    If not provided, no full dump is done.

  -c file_name
  --config file_name
    Use given file as options file.
    It must be a python file. See sample_options.py for possible values.
    If provided and if configuration file defines base_url and
    known_tid_storage_identifier_dict variables, this program will cause
    generation of all tids before first write to status file.
""" % {'arg0': sys.argv[0],
       'logfile_name': Options.logfile_name,
       'pidfile_name': Options.pidfile_name,
       'port': Options.port,
       'address': Options.address}

class Options:
  port = 9001
  address = '0.0.0.0'
  logfile_name = 'tidstorage.log'
  pidfile_name = 'tidstorage.pid'
  fork = True
  setuid = None
  setgid = None
  status_file = None
  burst_period = None
  full_dump_period = None
  known_tid_storage_identifier_dict = {}
  base_url = None

config_file_name = None

options = Options()

try:
  opts, args = getopt.getopt(sys.argv[1:],
                             'hnfl:p:a:s:b:F:c:',
                             ['help', 'nofork', 'fg', 'log=', 'port=',
                              'address=', 'pidfile=', 'user=', 'group=',
                              'status-file=', 'burst-period=',
                              'full-dump-period=', 'config='])
except:
  usage()
  raise

for opt, arg in opts:
  if opt in ('-h', '--help'):
    usage()
    sys.exit()
  elif opt in ('-n', '--fg', '--nofork'):
    options.fork = False
  elif opt in ('-l', '--log'):
    options.logfile_name = arg
  elif opt in ('-p', '--port'):
    options.port = int(arg)
  elif opt in ('-a', '--address'):
    options.address = arg
  elif opt == '--pidfile':
    options.pidfile_name = arg
  elif opt == '--user':
    pw = pwd.getpwnam(arg)
    options.setuid = pw.pw_uid
    options.setgid = pw.pw_gid
  elif opt == '--group':
    options.setgid = grp.getgrnam(arg).gr_gid
  elif opt in ('-s', '--status-file'):
    options.status_file = arg
  elif opt in ('-b', '--burst-period'):
    options.burst_period = int(arg)
  elif opt in ('-F', '--full-dump-period'):
    options.full_dump_period = int(arg)
  elif opt in ('-c', '--config'):
    config_file_name = arg

if config_file_name is not None:
  config_file = os.path.splitext(os.path.basename(config_file_name))[0]
  config_path = os.path.dirname(config_file_name)
  if len(config_path):
    config_path = [config_path]
  else:
    config_path = sys.path
  file, path, description = imp.find_module(config_file, config_path)
  module = imp.load_module(config_file, file, path, description)
  file.close()
  for option_id in [x for x in dir(Options) if x[:1] != '_']:
    if option_id not in options.__dict__ and hasattr(module, option_id):
      setattr(options, option_id, getattr(module, option_id))

if options.pidfile_name is not None:
  options.pidfile_name = os.path.abspath(options.pidfile_name)
if options.logfile_name is not None:
  options.logfile_name = os.path.abspath(options.logfile_name)
if options.status_file is not None:
  options.status_file = os.path.abspath(options.status_file)

if options.setgid is not None:
  os.setgid(options.setgid)

if options.setuid is not None:
  os.setuid(options.setuid)

tid_storage = TIDStorage(tid_file_path=options.status_file,
                         burst_period=options.burst_period,
                         full_dump_period=options.full_dump_period)

signal.signal(signal.SIGHUP, HUPHandler)
signal.signal(signal.SIGUSR1, USR1Handler)
signal.signal(signal.SIGTERM, TERMHandler)

if options.fork:
  os.chdir('/')
  os.umask(027)
  logfile = openLog()
  pidfile = open(options.pidfile_name, 'w')
  pid = os.fork()
  if pid == 0:
    os.setsid()
    pid = os.fork()
    if pid == 0:
      pidfile.close()
      os.close(0)
      os.close(1)
      os.close(2)
      sys.stdout = sys.stderr = logfile
      main(options.address, options.port)
      log('Exiting.')
    else:
      pidfile.write(str(pid))
      pidfile.close()
      os._exit(0)
  else:
    os._exit(0)
else:
  main(options.address, options.port)

