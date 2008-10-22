from StructuredText.StructuredText import HTML
from Products.PortalTransforms.interfaces import itransform

DEFAULT_STX_LEVEL = 2
STX_LEVEL = DEFAULT_STX_LEVEL

class st:
    __implements__ = itransform

    __name__ = "st_to_html"
    inputs   = ("text/structured",)
    output   = "text/html"

    def name(self):
        return self.__name__

    def convert(self, orig, data, level=None, **kwargs):
        if level is None:
            level = STX_LEVEL
        data.setData(HTML(orig, level=level, header=0))
        return data

def register():
    return st()
