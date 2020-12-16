from threading import local
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass

DEFAULT_MAX_RETRY = 3
_activity_runtime_environment = local()

def getActivityRuntimeEnvironment():
  """
    Raises KeyError if called outside activity.
  """
  try:
    return _activity_runtime_environment.value
  except AttributeError:
    raise KeyError

def _getActivityRuntimeEnvironment():
  return getattr(_activity_runtime_environment, 'value', None)


class BaseMessage:

  def __property(**kw):
    (k, v), = kw.items()
    return property(lambda self: self.activity_kw.get(k, v))

  delay = __property(delay=None)
  # None means infinite retry
  max_retry = __property(max_retry=DEFAULT_MAX_RETRY)
  # For errors happening after message invocation (ConflictError),
  # should we retry quickly without increasing 'retry' count ?
  conflict_retry = __property(conflict_retry=True)
  # Called if any error happened, after the transaction is aborted.
  # The message is cancelled if a non zero value is returned.
  # A transaction commit is done after it is called.
  # If the callback fails, the transaction is aborted again and the
  # notification contains this failure instead of the original one.
  on_error_callback = __property(on_error_callback=None)


class ActivityRuntimeEnvironment(object):
  security = ClassSecurityInfo()

  def __init__(self, message, priority=None):
    self._message = message
    self._priority = priority

  def __enter__(self):
    assert not hasattr(_activity_runtime_environment, 'value')
    _activity_runtime_environment.value = self

  def __exit__(self, exc_type, exc_val, exc_tb):
    assert _activity_runtime_environment.value is self
    del _activity_runtime_environment.value

  security.declarePublic('getTag')
  def getTag(self, default=None):
    return self._message.activity_kw.get('tag', default)

  security.declarePublic('getPriority')
  def getPriority(self):
    result = self._priority
    if result is None:
      return self._message.line.priority
    return result

  security.declarePublic('edit')
  def edit(self, **kw):
    # There is no point allowing to modify other attributes from a message
    for k in kw:
      getattr(BaseMessage, k)
      if k == 'on_error_callback' and \
         self._message.activity_kw.get(k) is not None:
        raise RuntimeError("An error callback is already registered")
    self._message.activity_kw.update(kw)

InitializeClass(ActivityRuntimeEnvironment)
