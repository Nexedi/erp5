from Products.ERP5Type.TransactionalVariable import getTransactionalVariable

def getActivityRuntimeEnvironment():
  """
    Raises KeyError if called outside activity.
  """
  return getTransactionalVariable(None)['activity_runtime_environment']

def _getActivityRuntimeEnvironment():
  try:
    return getActivityRuntimeEnvironment()
  except KeyError:
    return


class BaseMessage:

  delay = None
  # None means infinite retry
  max_retry = 5
  # For errors happening after message invocation (ConflictError),
  # should we retry quickly without increasing 'retry' count ?
  conflict_retry = True


class ActivityRuntimeEnvironment(object):

  def __init__(self, message):
    self._message = message

  def edit(self, **kw):
    # There is no point allowing to modify other attributes from a message
    for k in kw:
      getattr(BaseMessage, k)
    self._message.__dict__.update(kw)
