from Products.ERP5Type.Base import Base as ERP5Base
from ExtensionClass import Base as ExtensionBase

from zLOG import LOG, ERROR, BLATHER

def newLazyClass(name, portal_type_class_attr_getter):
    def load(self, attr):
        klass = None
        # self might be a subclass of a portal type class
        # we need to find the right parent class to change
        for candidate_klass in self.__class__.__mro__:
          # XXX hardcoded, this doesnt look too good
          if candidate_klass.__module__ == "erp5.portal_type":
            klass = candidate_klass
            break
        if klass is None:
          raise AttributeError("Could not find a portal type class in class hierarchy")

        portal_type = klass.__name__
        try:
          baseclasses, attributes = portal_type_class_attr_getter(portal_type)
        except AttributeError:
          LOG("ERP5Type.Dynamic", ERROR,
              "Could not access Portal Type Object for type %s" % name)
          import traceback; traceback.print_exc()
          raise AttributeError("Could not access Portal Type Object for type %s" % name)

        # save the old bases to be able to restore a ghost state later
        klass.__ghostbase__ = klass.__bases__
        klass.__bases__ = baseclasses

        for key, value in attributes.iteritems():
          setattr(klass, key, value)

        # beware of the scary meta type
        type(ExtensionBase).__init__(klass, klass)

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
            if attr in ('__class__',
                        '__dict__',
                        '__module__',
                        '__name__',
                        '__repr__',
                        '__str__') or attr[:3] in ('_p_', '_v_'):
                return super(GhostPortalType, self).__getattribute__(attr)
            #LOG("ERP5Type.Dynamic", BLATHER,
            #    "loading attribute %s.%s..." % (name, attr))
            return load(self, attr)

    return type(name, (GhostPortalType,), dict())
