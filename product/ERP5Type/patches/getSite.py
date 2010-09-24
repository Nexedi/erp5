from zLOG import LOG
module_name = 'zope.site.hooks'
native_setsite = False
try:
  hooks = __import__(module_name, {}, {}, module_name)
  native = True
except ImportError:
  # backwards compatibility for Zope < 2.12
  import imp, sys
  sys.modules[module_name] = hooks = imp.new_module(module_name)
  def setSite(foo=None):
    pass
  hooks.setSite = setSite
  def getSite(foo=None):
    return None
  hooks.getSite = getSite

# patch getSite so that it works everywhere
from Products.ERP5Type.Globals import get_request

oldgetsite = hooks.getSite
def getSite():
  try:
    x = oldgetsite()
    # this should be enough for Zope 2.12
    if x is not None:
      return x
  except:
    if native_setsite:
      # this should not happen on 2.12, log it
      import traceback; traceback.print_stack()
      LOG('getSite() cant retrieve the site', 100,
          'setSite() should have been called earlier on')
    pass
  # and Zope 2.8 needs to use the request
  parents = get_request()['PARENTS']

  portal = None
  for item in parents:
    if item.meta_type == 'ERP5 Site':
      portal = item
      break

  if portal is None:
    # not perfect?
    try:
      portal = parents[-1].getPortalObject()
    except:
      import traceback; traceback.print_stack()
      raise AttributeError("getSite() cant retrieve the site.")

  return portal
hooks.getSite = getSite

from Products.CMFActivity.ActivityTool import ActivityTool
ActivityTool_process_timer = ActivityTool.process_timer
def process_timer(self, *args, **kw):
  portal = self.getPortalObject()
  hooks.setSite(portal)
  return ActivityTool_process_timer(self, *args, **kw)
ActivityTool.process_timer = process_timer

