# -*- coding: utf-8 -*-

import sys

from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Base import Base as ERP5Base
from ExtensionClass import ExtensionClass, pmc_init_of

from zope.interface import classImplements
from ZODB.broken import Broken, PersistentBroken
from zLOG import LOG, WARNING, BLATHER

from portal_type_class import generatePortalTypeClass
from accessor_holder import AccessorHolderType

# PersistentBroken can't be reused directly
# because its « layout differs from 'GhostPortalType' »
ERP5BaseBroken = type('ERP5BaseBroken', (Broken, ERP5Base), dict(x
  for x in PersistentBroken.__dict__.iteritems()
  if x[0] not in ('__dict__', '__module__', '__weakref__')))


# the meta class of a derived class must be a subclass of all of its bases:
# since a portal type derives from both Zope Extension classes and
# from Accessor Holders, both metaclasses are required, even if
# only ExtensionClass is needed to run the house
class GhostBaseMetaClass(ExtensionClass, AccessorHolderType):
  """
  Generate classes that will be used as bases of portal types to
  mark portal types as non-loaded and to force loading it.
  """

  ghost_doc = """\
  Ghost state for a portal type class that is not loaded.

  When an instance of this portal type class is loaded (a new object is
  created, or an attribute of an existing object is accessed) this class will
  force loading the portal type real inheritance and properties from the ZODB.

  The portal type class will then update its __bases__ so that it points to
  the correct Document+Mixin+interfaces+AccessorHolder classes: after the first
  load, a portal type class does not use GhostPortalType in its __bases__
  anymore.
  """
  def __init__(cls, name, bases, dictionary):
    super(GhostBaseMetaClass, cls).__init__(name, bases, dictionary)

    def __init__(self, *args, **kw):
      self.__class__.loadClass()
      getattr(self, '__init__')(*args, **kw)

    def __getattribute__(self, attr):
      """
      This is only called once to load the class.
      Because __bases__ is changed, the behavior of this object
      will change after the first call.
      """
      # very special case used to bootstrap an instance:
      # calling _setObject() requires accessing the meta_type of the
      # object we're setting, but when creating portal_types it's way
      # too early to load erp5.portal_type.Types Tool
      if attr == "meta_type" and self.__class__.__name__ == "Types Tool":
          return "ERP5 Types Tool"

      # Class must be loaded if '__of__' is requested because otherwise,
      # next call to __getattribute__ would lose any acquisition wrapper.
      if attr in ('__class__',
                  '__getnewargs__',
                  '__getstate__',
                  '__dict__',
                  '__module__',
                  '__name__',
                  '__repr__',
                  '__str__') or attr[:3] in ('_p_', '_v_'):
        return super(cls, self).__getattribute__(attr)
      #LOG("ERP5Type.Dynamic", BLATHER,
      #    "loading attribute %s.%s..." % (name, attr))
      self.__class__.loadClass()
      return getattr(self, attr)

    cls.__getattribute__ = __getattribute__
    cls.__init__ = __init__
    cls.__doc__ = GhostBaseMetaClass.ghost_doc
    # This prevents serialize (ZODB) from reloading the class during commit
    # (which would even trigger migration, resulting in a ConflictError).
    cls.__getnewargs__ = None

InitGhostBase = GhostBaseMetaClass('InitGhostBase', (ERP5Base,), {})

class PortalTypeMetaClass(GhostBaseMetaClass):
  """
  Meta class that is used by portal type classes

  - Tracks subclasses of portal type classes
  - Takes care of ghosting/unghosting

  Instances of this metaclass have __isghost__ class attributes.
  - If True, this attribute marks classes awaiting a load from the
    ZODB. An instance of GhostBaseMetaClass should be in the mro()
    and will be removed after loading.
  - If False, the class is fully-loaded and functional.
  """

  # register which classes subclass portal type classes
  subclass_register = {} # XXX ideal defaultdict(list) wannabe

  def __init__(cls, name, bases, dictionary):
    """
    This method is called when a portal type class is
    created, or when a class inheriting a portal type
    class is created
    """
    for parent in bases:
      if issubclass(type(parent), PortalTypeMetaClass):
        PortalTypeMetaClass.subclass_register.setdefault(parent, []).append(cls)

    cls.__isghost__ = True
    super(GhostBaseMetaClass, cls).__init__(name, bases, dictionary)

  @classmethod
  def getSubclassList(metacls, cls):
    """
    Returns classes deriving from cls
    """
    return metacls.subclass_register.get(cls, [])

  def getAccessorHolderPropertyList(cls):
    """
    Get all the properties as defined in the accessor holders,
    meaningful for _propertyMap for example

    @see Products.ERP5Type.Base.Base._propertyMap
    """
    property_list = []
    for klass in cls.mro():
      if klass.__module__ == 'erp5.accessor_holder':
        property_list.extend(klass._properties)

    return property_list

  def resetAcquisitionAndSecurity(cls):
    # First, fill the __get__ slot of the class
    # that has been null'ed after resetting its __bases__
    # This descriptor is the magic allowing __of__ and our
    # _aq_dynamic trick
    pmc_init_of(cls)
    # Then, call __class_init__ on the class for security
    InitializeClass(cls)

    # And we need to do the same thing on subclasses
    for subclass in PortalTypeMetaClass.getSubclassList(cls):
      pmc_init_of(subclass)
      InitializeClass(subclass)

  def restoreGhostState(cls):
    """
    Insert in the __bases__ hierarchy an instance of GhostBaseMetaClass
    that will force reloading the class.
    - mro before reset:
       erp5.portal_type.XXX, *TAIL
    - after reset:
       erp5.portal_type.XXX, GhostBaseMetaClass instance, *TAIL
    """
    if not cls.__isghost__:
      for attr in cls.__dict__.keys():
        if attr not in ('__module__',
                        '__doc__',
                        '__isghost__',
                        'portal_type'):
          delattr(cls, attr)
      # generate a ghostbase that derives from all previous bases
      ghostbase = GhostBaseMetaClass('GhostBase', cls.__bases__, {})
      cls.__bases__ = (ghostbase,)
      cls.__isghost__ = True
      cls.resetAcquisitionAndSecurity()

  def __getattr__(cls, name):
    """
    Load the class before trying to access a class attribute (for
    example, Standard Property document defines a class method to
    import a filesystem property)
    """
    # Perform the loadClass only on erp5.portal_type classes
    if cls.__module__ != 'erp5.portal_type':
      return getattr(cls.__bases__[0], name)

    if not name.startswith('__') and cls.__isghost__:
      cls.loadClass()
      return getattr(cls, name)

    raise AttributeError

  def loadClass(cls):
    """
    - mro before load:
      erp5.portal_type.XXX, GhostBaseMetaClass instance, *TAIL
    - mro after:
      erp5.portal_type.XXX, *new_bases_fetched_from_ZODB
    """
    # Do not load the class again if it has already been loaded
    if not cls.__isghost__:
      return

    # cls might be a subclass of a portal type class
    # we need to find the right class to change
    for klass in cls.__mro__:
      # XXX hardcoded, this doesnt look too good
      if klass.__module__ == "erp5.portal_type":
        break
    else:
      raise AttributeError("Could not find a portal type class in"
                           " class hierarchy")

    ERP5Base.aq_method_lock.acquire()
    portal_type = klass.__name__
    from Products.ERP5.ERP5Site import getSite
    site = getSite()
    try:
      try:
        class_definition = generatePortalTypeClass(site, portal_type)
      except AttributeError:
        LOG("ERP5Type.Dynamic", WARNING,
            "Could not access Portal Type Object for type %r"
            % portal_type, error=sys.exc_info())
        base_tuple = (ERP5BaseBroken, )
        attribute_dict = {}
        interface_list = []
        base_category_list = []
      else:
        base_tuple, interface_list, base_category_list, attribute_dict = class_definition

      klass.__isghost__ = False
      klass.__bases__ = base_tuple

      klass.resetAcquisitionAndSecurity()

      for key, value in attribute_dict.iteritems():
        setattr(klass, key, value)

      klass._categories = base_category_list

      for interface in interface_list:
        classImplements(klass, interface)
    finally:
      ERP5Base.aq_method_lock.release()

def generateLazyPortalTypeClass(portal_type_name):
  return PortalTypeMetaClass(portal_type_name,
                             (InitGhostBase,),
                             dict(portal_type=portal_type_name))
