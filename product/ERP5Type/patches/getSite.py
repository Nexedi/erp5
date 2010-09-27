from Products.ERP5Type import Globals
module_name = 'zope.site.hooks'
try:
  hooks = __import__(module_name, {}, {}, module_name)
  _getSite = hooks.getSite
  _setSite = hooks.setSite
except ImportError:
  # backwards compatibility for Zope < 2.12
  import imp, sys
  import zope
  try:
    site = zope.site
  except:
    sys.modules['zope.site'] = zope.site = imp.new_module('zope.site')
  sys.modules[module_name] = hooks = imp.new_module(module_name)

  def _getSite():
    return None
  def _setSite(site=None):
    request = Globals.get_request()
    if site is not None and site not in request.get('PARENTS', ()):
      request['PARENTS'] = [site]

# patch getSite so that it works everywhere
def getSite():
  site = _getSite()
  if site is None:
    parents = Globals.get_request()['PARENTS']
    for site in parents[::-1]:
      if getattr(site, 'getPortalObject', None) is not None:
        break
    else:
      raise AttributeError("getSite() can't retrieve the site")
  return site
hooks.getSite = getSite

last_cookie_value = None
def setSite(site=None):
  _setSite(site)
  from Products.ERP5Type.Dynamic.portaltypeclass import synchronizeDynamicModules
  synchronizeDynamicModules(site)
hooks.setSite = setSite
