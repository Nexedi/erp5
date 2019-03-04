try:
  import zope.globalrequest
except ImportError:
  import sys
  sys.modules['zope.globalrequest'] = sys.modules[__name__]

  from threading import local
  localData = local()

  def getRequest():
    return getattr(localData, 'request', None)

  def setRequest(request):
    localData.request = request

  def clearRequest():
    setRequest(None)
