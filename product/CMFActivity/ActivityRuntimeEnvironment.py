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


class ActivityRuntimeEnvironment(object):

  def __init__(self, message):
    self._message = message

  def edit(self, **kw):
    # There is no point allowing to modify other attributes from a message
    for k in kw:
      getattr(BaseMessage, k)
    self._message.activity_kw.update(kw)
