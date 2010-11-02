# -*- coding: utf-8 -*-

import sys
from Products.ERP5Type.Base import Base as ERP5Base
from ExtensionClass import Base as ExtensionBase
from ZODB.broken import Broken, PersistentBroken
from zLOG import LOG, ERROR, BLATHER

# PersistentBroken can't be reused directly
# because its « layout differs from 'GhostPortalType' »
ERP5BaseBroken = type('ERP5BaseBroken', (Broken, ERP5Base), dict(x
  for x in PersistentBroken.__dict__.iteritems()
  if x[0] not in ('__dict__', '__module__', '__weakref__')))

ExtensionClass = type(ExtensionBase)

class PortalTypeMetaClass(ExtensionClass):
  """
  Meta class that will be used by portal type classes
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

def InitializePortalTypeClass(klass):
  ExtensionClass.__init__(klass, klass)
  for klass in PortalTypeMetaClass.getSubclassList(klass):
    ExtensionClass.__init__(klass, klass)

def generateLazyPortalTypeClass(portal_type_name,
                                portal_type_class_loader):
    def load(self, attr):
        # self might be a subclass of a portal type class
        # we need to find the right parent class to change
        for klass in self.__class__.__mro__:
          # XXX hardcoded, this doesnt look too good
          if klass.__module__ == "erp5.portal_type":
            break
        else:
          raise AttributeError("Could not find a portal type class in class hierarchy")

        portal_type = klass.__name__
        try:
          baseclasses, attributes = portal_type_class_loader(portal_type)
        except AttributeError:
          LOG("ERP5Type.Dynamic", ERROR,
              "Could not access Portal Type Object for type %r"
              % portal_type, error=sys.exc_info())
          baseclasses = (ERP5BaseBroken, )
          attributes = {}

        # save the old bases to be able to restore a ghost state later
        klass.__ghostbase__ = klass.__bases__
        klass.__bases__ = baseclasses

        for key, value in attributes.iteritems():
          setattr(klass, key, value)

        InitializePortalTypeClass(klass)

        return getattr(self, attr)

    class GhostPortalType(ERP5Base): #SimpleItem
        """
        Ghost state for a portal type that is not loaded.

        One instance of this class exists per portal type class on the system.
        When an object of this portal type is loaded (a new object is created,
        or an attribute of an existing object is accessed) this class will
        change the bases of the portal type class so that it points to the
        correct Document+Mixin+interfaces+AccessorHolder classes.
        """
        def __init__(self, *args, **kw):
            load(self, '__init__')(*args, **kw)

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
            return load(self, attr)

    return PortalTypeMetaClass(portal_type_name, (GhostPortalType,), dict())
