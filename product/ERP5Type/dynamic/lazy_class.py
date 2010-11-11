# -*- coding: utf-8 -*-

import sys

from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Base import Base as ERP5Base
from ExtensionClass import ExtensionClass, pmc_init_of

from zope.interface import classImplements
from ZODB.broken import Broken, PersistentBroken
from zLOG import LOG, WARNING, BLATHER

from portal_type_class import generatePortalTypeClass

# PersistentBroken can't be reused directly
# because its « layout differs from 'GhostPortalType' »
ERP5BaseBroken = type('ERP5BaseBroken', (Broken, ERP5Base), dict(x
  for x in PersistentBroken.__dict__.iteritems()
  if x[0] not in ('__dict__', '__module__', '__weakref__')))

class GhostPortalType(ERP5Base): #SimpleItem
  """
  Ghost state for a portal type class that is not loaded.

  When an instance of this portal type class is loaded (a new object is
  created, or an attribute of an existing object is accessed) this class will
  force loading the portal type real inheritance and properties from the ZODB.

  The portal type class will then update its __bases__ so that it points to
  the correct Document+Mixin+interfaces+AccessorHolder classes: after the first
  load, a portal type class does not use GhostPortalType in its __bases__
  anymore.
  """
  def __init__(self, *args, **kw):
    self.__class__.loadClass()
    getattr(self, '__init__')(*args, **kw)

  def __getattribute__(self, attr):
    """
    This is only called once to load the class.
    Because __bases__ is changed, the behavior of this object
    will change after the first call.
    """
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
      return super(GhostPortalType, self).__getattribute__(attr)
    #LOG("ERP5Type.Dynamic", BLATHER,
    #    "loading attribute %s.%s..." % (name, attr))
    self.__class__.loadClass()
    return getattr(self, attr)

class PortalTypeMetaClass(ExtensionClass):
  """
  Meta class that is used by portal type classes

  - Tracks subclasses of portal type classes
  - Takes care of ghosting/unghosting
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

    super(PortalTypeMetaClass, cls).__init__(name, bases, dictionary)

  @classmethod
  def getSubclassList(metacls, cls):
    """
    Returns classes deriving from cls
    """
    return metacls.subclass_register.get(cls, [])

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
    ghostbase = getattr(cls, '__ghostbase__', None)
    if ghostbase is not None:
      for attr in cls.__dict__.keys():
        if attr not in ('__module__', '__doc__',):
          delattr(cls, attr)
      cls.__bases__ = ghostbase
      cls.resetAcquisitionAndSecurity()

  def loadClass(cls):
    # cls might be a subclass of a portal type class
    # we need to find the right class to change
    for klass in cls.__mro__:
      # XXX hardcoded, this doesnt look too good
      if klass.__module__ == "erp5.portal_type":
        break
    else:
      raise AttributeError("Could not find a portal type class in"
                           " class hierarchy")

    portal_type = klass.__name__
    try:
      class_definition = generatePortalTypeClass(portal_type)
    except AttributeError:
      LOG("ERP5Type.Dynamic", WARNING,
          "Could not access Portal Type Object for type %r"
          % portal_type, error=sys.exc_info())
      base_list = (ERP5BaseBroken, )
      attribute_dict = {}
      interface_list = []
    else:
      base_list, interface_list, attribute_dict = class_definition


    # save the old bases to be able to restore a ghost state later
    if not hasattr(klass, '__ghostbase__'):
      # but only do it if we're in the innermost call, otherwise
      # klass.__bases__ might just be the Document without accessor
      # holders, and we would override the real ghost class
      klass.__ghostbase__ = klass.__bases__
    klass.__bases__ = base_list

    for key, value in attribute_dict.iteritems():
      setattr(klass, key, value)

    klass.resetAcquisitionAndSecurity()
    for interface in interface_list:
      classImplements(klass, interface)

def generateLazyPortalTypeClass(portal_type_name):
  return PortalTypeMetaClass(portal_type_name, (GhostPortalType,), {})
