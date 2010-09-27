
import dynamicmodule

import lazyclass
import sys
import inspect
from types import ModuleType

from zope.site.hooks import getSite
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Utils import setDefaultClassProperties

from Products.ERP5Type import document_class_registry, mixin_class_registry

from ExtensionClass import Base as ExtensionBase
from zLOG import LOG, ERROR, BLATHER

def _import_class(classpath):
  try:
    module_path, class_name = classpath.rsplit('.', 1)
    module = __import__(module_path, {}, {}, (module_path,))
    klass = getattr(module, class_name)

    # XXX is this required? (here?)
    setDefaultClassProperties(klass)
    InitializeClass(klass)

    return klass
  except:
    import traceback; traceback.print_exc()
    raise ImportError('Could not import document class %s' % classpath)

def portal_type_factory(portal_type_name):
  """
  Given a portal type, look up in Types Tool the corresponding
  Base Type object holding the definition of this portal type,
  and computes __bases__ and __dict__ for the class that will
  be created to represent this portal type
  """
  LOG("ERP5Type.Dynamic", 0, "Loading portal type %s..." % portal_type_name)

  type_class = None
  mixin_list = []
  interface_list = []
  # two exceptions that cant be loaded from types tool:
  if portal_type_name == "Base Type":
    # avoid chicken and egg issue:
    # you can access portal_types/Foo if you havent
    # loaded Base Type class, but you cant load
    # Base Type class without accessing portal_types/Base Type
    type_class = "ERP5TypeInformation"
  elif portal_type_name == "Business Template":
    # When installing a BT, Business Templates are loaded
    # before creating any Base Type object
    type_class = "BusinessTemplate"
  else:
    site = getSite()

    type_tool = site.portal_types
    try:
      portal_type = getattr(type_tool, portal_type_name)
    except:
      import traceback; traceback.print_stack()
      raise AttributeError('portal type %s not found in Types Tool' \
                              % portal_type_name)

    # type_class has a compatibility getter that should return
    # something even if the field is not set (i.e. Base Type object
    # was not migrated yet)
    type_class = portal_type.getTypeClass()

    # But no such getter exist for Mixins and Interfaces:
    # in reality, we can live with such a failure
    try:
      mixin_list = portal_type.getTypeMixinList()
      interface_list = portal_type.getTypeInterfaceList()
    except:
      # log loudly the error, but it's not _critical_
      LOG("ERP5Type.Dynamic", ERROR,
          "Could not load interfaces or Mixins for portal type %s" \
              % portal_type)

  if type_class is not None:
    type_class = document_class_registry.get(type_class)
  if type_class is None:
    raise AttributeError('Document class is not defined on Portal Type %s' % portal_type_name)

  mixin_path_list = []
  if mixin_list:
    mixin_path_list = map(mixin_class_registry.__getitem__, mixin_list)

  ##
  # XXX initialize interfaces here too
  # XXX adding accesor_holder for property sheets should be done here
  ##

  classpath_list = [type_class] + mixin_path_list

  baseclasses = map(_import_class, classpath_list)

  #LOG("ERP5Type.Dynamic", BLATHER,
  #    "Portal type %s loaded with bases %s" \
  #        % (portal_type_name, repr(baseclasses)))
  return tuple(baseclasses), dict(portal_type=portal_type_name)

def initializeDynamicModules():
  """
  Create erp5 module and its submodules
    erp5.portal_type
      holds portal type classes
    erp5.temp_portal_type
      holds portal type classes for temp objects
    erp5.document
      holds document classes that have no physical import path,
      for example classes created through ClassTool that are in
      $INSTANCE_HOME/Document
  """

  def portal_type_loader(portal_type_name):
    """
    Returns a lazily-loaded "portal-type as a class"
    """
    return lazyclass.lazyclass(portal_type_name, portal_type_factory)

  erp5 = ModuleType("erp5")
  sys.modules["erp5"] = erp5
  erp5.document = ModuleType("erp5.document")
  sys.modules["erp5.document"] = erp5.document

  portal_type_container = dynamicmodule.dynamicmodule('erp5.portal_type',
                                            portal_type_loader)
  erp5.portal_type = portal_type_container

  def temp_portal_type_loader(portal_type_name):
    """
    Returns a class suitable for a temporary portal type

    This class will in fact be a subclass of erp5.portal_type.xxx, which
    means that loading an attribute on this temporary portal type loads
    the lazily-loaded parent class, and that any changes on the parent
    class will be reflected on the temporary objects.
    """
    klass = getattr(portal_type_container, portal_type_name)

    from Products.ERP5Type.Accessor.Constant import PropertyGetter as \
      PropertyConstantGetter

    class TempDocument(klass):
      isTempDocument = PropertyConstantGetter('isTempDocument', value=True)
      __roles__ = None
    TempDocument.__name__ = "Temp" + portal_type_name

    # Replace some attributes.
    for name in ('isIndexable', 'reindexObject', 'recursiveReindexObject',
                 'activate', 'setUid', 'setTitle', 'getTitle', 'getUid'):
      setattr(TempDocument, name, getattr(klass, '_temp_%s' % name))

    # Make some methods public.
    for method_id in ('reindexObject', 'recursiveReindexObject',
                      'activate', 'setUid', 'setTitle', 'getTitle',
                      'edit', 'setProperty', 'getUid', 'setCriterion',
                      'setCriterionPropertyList'):
      setattr(TempDocument, '%s__roles__' % method_id, None)
    return TempDocument

  erp5.temp_portal_type = dynamicmodule.dynamicmodule('erp5.temp_portal_type',
                                                   temp_portal_type_loader)


last_sync = 0
def synchronizeDynamicModules(context, force=False):
  """
  Allow resetting all classes to ghost state, most likely done after
  adding and removing mixins on the fly

  Most of the time, this reset is only hypothetic:
  * with force=False, the reset is only done if another node resetted
    the classes since the last reset on this node.
  * with force=True, forcefully reset the classes on the current node
    and send out an invalidation to other nodes
  """
  return # XXX disabled for now
  LOG("ERP5Type.Dynamic", 0, "Resetting dynamic classes")

  portal = context.getPortalObject()

  global last_sync
  if force:
    # hard invalidation to force sync between nodes
    portal.newCacheCookie('dynamic_classes')
    last_sync = portal.getCacheCookie('dynamic_classes')
  else:
    cookie = portal.getCacheCookie('dynamic_classes')
    if cookie == last_sync:
      # up to date, nothing to do
      return
    last_sync = cookie

  import erp5.portal_type
  for class_name, klass in inspect.getmembers(erp5.portal_type, inspect.isclass):
    ghostbase = getattr(klass, '__ghostbase__', None)
    if ghostbase is not None:
      for attr in klass.__dict__.keys():
        if attr != '__module__':
          delattr(klass, attr)
      klass.__bases__ = ghostbase
      type(ExtensionBase).__init__(klass, klass)

