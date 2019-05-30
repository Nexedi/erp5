try:
  import zope.globalrequest
except ImportError:
  import sys
  sys.modules['zope.globalrequest'] = sys.modules[__name__]

  from threading import local
  localData = local()

  def getRequest():
    value = getattr(localData, 'request', None)
    if value is None:
      setattr(localData, 'request', value)
    return value

  def setRequest(request):
    setattr(localData, 'request', request)

  def clearRequest():
    setRequest(None)
