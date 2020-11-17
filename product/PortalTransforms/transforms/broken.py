from __future__ import print_function
from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
from Products.PortalTransforms.utils import log
WARNING=100

class BrokenTransform:
    implements(ITransform)

    __name__ = "broken transform"
    inputs  = ("BROKEN",)
    output = "BROKEN"

    def __init__(self, id, module, error):
        self.id = id
        self.module = module
        self.error = error

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):
        # do the format
        msg = "Calling convert on BROKEN transform %s (%s). Error: %s" % \
              (self.id, self.module, self.error)
        log(msg, severity=WARNING)
        print(msg)
        data.setData('')
        return data

def register():
    return broken()
