from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implementer
from zope.structuredtext import stx2html

DEFAULT_STX_LEVEL = 2
STX_LEVEL = DEFAULT_STX_LEVEL

@implementer(ITransform)
class st:

    __name__ = "st_to_html"
    inputs   = ("text/structured",)
    output   = "text/html"

    def name(self):
        return self.__name__

    def convert(self, orig, data, level=None, **kwargs):
        if level is None:
            level = STX_LEVEL
        data.setData(stx2html(orig, level=level, header=0))
        return data

def register():
    return st()
