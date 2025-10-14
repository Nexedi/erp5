import six
import threading

aq_method_lock = threading.RLock()


if six.PY3:
  import_lock = threading.Lock()

else:
  import imp

  class import_lock:
    def acquire(self):
      return imp.acquire_lock()
    def release(self):
      return imp.release_lock()
    def __enter__(self):
      return self.acquire()
    def __exit__(self, exc_type, exc, tb):
      self.release()
      return False
  import_lock = import_lock()
