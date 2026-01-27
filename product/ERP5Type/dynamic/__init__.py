import threading
aq_method_lock = threading.RLock()

import six
if six.PY3:
  import _imp
else:
  import imp as _imp
class global_import_lock:
  @staticmethod
  def acquire():
    return _imp.acquire_lock()
  @staticmethod
  def release():
    return _imp.release_lock()
  @staticmethod
  def held():
    return _imp.lock_held()
  def __enter__(self):
    self.acquire()
  def __exit__(self, exc_type, exc, traceback):
    self.release()
    return False
global_import_lock = global_import_lock()
