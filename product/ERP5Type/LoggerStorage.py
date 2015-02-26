# XXX license

# from Products.ERP5Type.LoggerStorage import LoggerStorage

import ZODB.interfaces
import zope.interface

from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
import transaction
import time
from zLOG import LOG

class UnsetMinimum:
  def __lt__(self, value):
    return False
  def __gt__(self, value):
    return True

def logStorageStatistics(duration_list):
  count = 0
  min = UnsetMinimum()
  max = 0
  avg = 0
  tot = 0
  for i in duration_list:
    count += 1
    if i < min: min = i
    if i > max: max = i
    tot += i
  if count != 0:
    avg = tot / count
  LOG("Storage request statistics:", 0, 'count %d, ' % count +
                                        'total duration %s s, ' % tot +
                                        'min/avg/max = %s/%s/%s s' % (min, avg, max))

class LoggerStorage(object):

  zope.interface.implements(ZODB.interfaces.IStorageWrapper)

  def __init__(self, base):
    self.base = base
    self._collecting_statistics = False # for inter method call protection
    zope.interface.directlyProvides(self, zope.interface.providedBy(base))

  def __getattr__(self, name):
    return getattr(self.base, name)

  def _wrapAndCall(self, method, args, kw):
    if not self._collecting_statistics:
      self._collecting_statistics = True
      # subscribe to hooks
      tv = getTransactionalVariable()
      if not tv.get("LoggerStorageHooked", False):
        tv["LoggerStorageHooked"] = True
        duration_list = []
        tv["LoggerStorage_transaction_statistics"] = duration_list
        transaction.get().addAfterCommitHook(lambda *ignored: logStorageStatistics(duration_list))
      # measure method duration
      try:
        start_timestamp = time.time()
        result = method(*args, **kw)
        duration = time.time() - start_timestamp
      finally:
        self._collecting_statistics = False
      # update statistics
      tv["LoggerStorage_transaction_statistics"].append(duration)
      return result
    return method(*args, **kw)

  def load(self, *args, **kw):
    return self._wrapAndCall(self.base.load, args, kw)

  def loadBefore(self, *args, **kw):
    return self._wrapAndCall(self.base.loadBefore, args, kw)

  def loadSerial(self, *args, **kw):
    return self._wrapAndCall(self.base.loadSerial, args, kw)


class LoggerStorageConfig:

  _factory = LoggerStorage

  def __init__(self, config):
    self.config = config
    self.name = config.getSectionName()

  def open(self):
    return self._factory(self.config.base.open())
