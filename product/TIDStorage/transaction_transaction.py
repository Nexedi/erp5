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

from ExchangeProtocol import ExchangeProtocol
from transaction._transaction import Transaction
from zLOG import LOG, WARNING, INFO
import socket
import thread
import struct
import sys

GET_LAST_COMMITED_TID_METHOD_ID = 'getLastCommitedTID'
TID_STORAGE_ADDRESS = ('127.0.0.1', 9001)

tid_storage = None
zope_identifier = None

LOG('TIDStorage',INFO,'Monkey patching transaction._transaction.Transaction._commitResources')

# Borrowed from CMFActivity.ActivityTool.getCurrentNode
def getZopeId():
  """ Return current node in form ip:port """
  global zope_identifier
  if zope_identifier is None:
    port = ''
    from asyncore import socket_map
    for k, v in socket_map.items():
      if hasattr(v, 'port'):
        # see Zope/lib/python/App/ApplicationManager.py: def getServers(self)
        type = str(getattr(v, '__class__', 'unknown'))
        if type == 'ZServer.HTTPServer.zhttp_server':
          port = v.port
          break
    assert port != '', 'zhttp_server not started yet'
    ip = socket.gethostbyname(socket.gethostname())
    if TID_STORAGE_ADDRESS[0] != '127.0.0.1':
      assert ip != '127.0.0.1', 'self address must not be 127.0.0.1 if TIDStorage is remote'
    zope_identifier = '%s:%s' %(ip, port)
  return zope_identifier

def getFilestorageList(resource_list):
  return getFilestorageToTIDMapping(resource_list).keys()

def getFilestorageToTIDMapping(resource_list):
  datafs_tid_update_dict = {}
  for resource in resource_list:
    storage = getattr(resource, '_storage', None)
    if storage is not None:
      getLastCommitedTID = getattr(storage, GET_LAST_COMMITED_TID_METHOD_ID,
                                   None)
      if getLastCommitedTID is not None:
        tid = getLastCommitedTID()
        _addr = tuple([tuple(x) for x in getattr(storage, '_addr', [])])
        _storage = getattr(storage, '_storage', '')
        datafs_id = repr((_addr, _storage))
        assert datafs_id not in datafs_tid_update_dict
        if tid is None:
          datafs_tid_update_dict[datafs_id] = None
        else:
          # unpack stolen from ZODB/utils.py:u64
          datafs_tid_update_dict[datafs_id] = struct.unpack(">Q", tid)[0]
  return datafs_tid_update_dict

class BufferedSocket:
  """
    Write-only thread-safe buffered socket.
    Attemps to reconnect at most once per flush.
  """

  _socket_lock = thread.allocate_lock()
  _connected = False
  
  def __init__(self, address):
    self._socket = socket.socket()
    self._address = address
    self._send_buffer_dict = {}

  def _connect(self):
    try:
      self._socket.connect(self._address)
      self._notifyConnected()
    except socket.error, message:
      # We don't want to have an error line per failed connection attemp, to
      # avoid flooding the logfile.
      pass

  def _getSendBuffer(self, ident):
    send_buffer = self._send_buffer_dict.get(ident)
    if send_buffer is None:
      send_buffer = self._send_buffer_dict[ident] = []
    return send_buffer

  def _notifyDisconnected(self, message):
    if self._connected:
      self._connected = False
      LOG('TIDStorage', WARNING, 'Disconnected: %s' % (message, ))

  def _notifyConnected(self):
    if not self._connected:
      self._connected = True
      # Display a log message at WARNING level, so that reconnection message
      # are visible when disconnection messages are visible, even if it is
      # not a warning, properly speaking.
      LOG('TIDStorage', WARNING, 'Connected')

  def send(self, to_send):
    send_buffer = self._getSendBuffer(thread.get_ident())
    send_buffer.append(to_send)

  def flush(self):
    """
      Flush send buffer and actually send data, with extra checks to behave
      nicely if connection is broken.
      Do not retry to send if something goes wrong (data is then lost !).
      Here, most important thing is speed, not data.
      Serialize usage.
    """
    ident = thread.get_ident()
    self._socket_lock.acquire()
    try:
      if not self._connected:
        self._connect()
      if self._connected:
        try:
          self._socket.sendall(''.join(self._getSendBuffer(ident)))
        except socket.error, message:
          self._notifyDisconnected(message)
          try:
            self._socket.shutdown(socket.SHUT_RDWR)
          except socket.error:
            self._socket.close()
          self._socket = socket.socket()
    finally:
      self._socket_lock.release()
    self._send_buffer_dict[ident] = []

class TIDClient:
  """Simple by design write only TIDClient using BufferedSocket"""
  def __init__(self, address):
    self._buffered_socket = BufferedSocket(address)
    self._field_exchange = ExchangeProtocol(socket=self._buffered_socket)

  def commit(self, tid_update_dict):
    """
      Send given dict to TIDStorage server.
    """
    self._send_command('commit')
    self._field_exchange.send_dict(tid_update_dict)
    self._buffered_socket.flush()

  def begin(self, storage_id_list):
    """
      Inform TIDStorage connection tracking that commit was initiated.
    """
    self._send_command('begin')
    self._field_exchange.send_list(storage_id_list)
    self._buffered_socket.flush()
  
  def abort(self):
    """
      Inform TIDStorage connection tracking that commit was aborted.
    """
    self._send_command('abort')
    self._buffered_socket.flush()

  def _send_command(self, command):
    """
      Every command must be followed by an identifier.
      This identifier is used to track transactions, so the same identifier
      must not be used twice at the same time, but can be reused later.
    """
    self._field_exchange.send_field(command)
    self._field_exchange.send_field('%s_%x' % (getZopeId(), thread.get_ident()))

original__commitResources = Transaction._commitResources
def _commitResources(self, *args, **kw):
  """
    Hook Transaction's _commitResources.

    Before:
     - Initialise TIDClient if needed
     - Check if there is any storage we are interested in in current commit
     - If so, issue a begin
    
    After (2 cases):
     - original__commitResources raised:
       - Issue an abort
     - otherwise:
       - Issue a commit

    Note to editors: Prevent your code from raising anything ! This method
    MUST NOT raise any exception, except that it MUST NOT hide any exception
    raised by original__commitResources.
    """
  has_storages = False
  try:
    global tid_storage
    if tid_storage is None:
      tid_storage = TIDClient(TID_STORAGE_ADDRESS)
    filestorage_list = getFilestorageList(self._resources)
    if len(filestorage_list):
      has_storages = True
      tid_storage.begin(filestorage_list)
  except:
    LOG('TIDStorage _commitResources', WARNING, 'Exception in begin phase', error=sys.exc_info())
  try:
    result = original__commitResources(self, *args, **kw)
  except:
    if has_storages:
      exception = sys.exc_info()
      try:
        tid_storage.abort()
      except:
        LOG('TIDStorage _commitResources', WARNING, 'Exception in abort phase', error=sys.exc_info())
      # Re-raise original exception, in case sendTIDCommitAbort tainted
      # last exception value.
      raise exception[0], exception[1], exception[2]
    else:
      raise
  else:
    if has_storages:
      # Now that everything has been commited, all exceptions relative to added
      # code must be swalowed (but still reported) to avoid confusing transaction
      # system.
      try:
        tid_storage.commit(getFilestorageToTIDMapping(self._resources))
      except:
        LOG('TIDStorage _commitResources', WARNING, 'Exception in commit phase', error=sys.exc_info())
  return result
 
Transaction._commitResources = _commitResources

