from Products.ERP5Type.TransactionalVariable import getTransactionalVariable

def getActivityRuntimeEnvironment():
  """
    Raises KeyError if called outside activity.
  """
  return getTransactionalVariable()['activity_runtime_environment']

def _getActivityRuntimeEnvironment():
  try:
    return getActivityRuntimeEnvironment()
  except KeyError:
    return


class BaseMessage:

  def __property(**kw):
    (k, v), = kw.items()
    return property(lambda self: self.activity_kw.get(k, v))

  delay = __property(delay=None)
  # None means infinite retry
  max_retry = __property(max_retry=3)
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

  def __init__(self, message):
    self._message = message

  def edit(self, **kw):
    # There is no point allowing to modify other attributes from a message
    for k in kw:
      getattr(BaseMessage, k)
      if k == 'on_error_callback' and \
         self._message.activity_kw.get(k) is not None:
        raise RuntimeError("An error callback is already registered")
    self._message.activity_kw.update(kw)
