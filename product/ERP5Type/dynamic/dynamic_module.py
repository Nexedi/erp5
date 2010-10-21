from types import ModuleType
import sys

class DynamicModule(ModuleType):
    """This module may generate new objects at runtime."""
    # it's useful to have such a generic utility
    # please subclass it if you need ERP5-specific behaviors

    def __init__(self, name, factory, doc=None):
        super(DynamicModule, self).__init__(name, doc=doc)
        self._factory = factory

    def __getattr__(self, name):
        if name == '__path__':
            raise AttributeError('%s does not have __path__' % (self,))
        obj = self._factory(name)
        if hasattr(obj, '__module__'):
            obj.__module__ = self.__name__
        setattr(self, name, obj)
        return obj

def registerDynamicModule(name, factory):
    d = DynamicModule(name, factory)
    sys.modules[name] = d
    return d
