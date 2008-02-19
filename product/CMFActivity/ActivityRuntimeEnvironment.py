import threading
import copy

activity_runtime_environment_container = threading.local()

def getActivityRuntimeEnvironment():
  """
    Raises AttributeError if called outside activity.
  """
  return copy.deepcopy(activity_runtime_environment_container.current)

def _getActivityRuntimeEnvironment():
  current = getattr(activity_runtime_environment_container, 'current', None)
  if current is None:
    current = activity_runtime_environment_container.current = {}
  return current

def setActivityRuntimeValue(key, value):
  """
    TODO: protect against unauthorized use ?
  """
  _getActivityRuntimeEnvironment()[key] = value

def updateActivityRuntimeValue(new_dict):
  """
    TODO: protect against unauthorized use ?
  """
  _getActivityRuntimeEnvironment().update(new_dict)

def clearActivityRuntimeEnvironment():
  if getattr(activity_runtime_environment_container, 'current', None) is not None:
    delattr(activity_runtime_environment_container, 'current')

