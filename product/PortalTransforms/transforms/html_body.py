from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
from Products.ERP5Type.Utils import bodyfinder

class HTMLBody:
    """Simple transform which extracts the content of the body tag"""

    implements(ITransform)

    __name__ = "html_body"
    inputs   = ('text/html',)
    output = "text/html"

    def __init__(self, name=None):
        self.config_metadata = {
            'inputs' : ('list', 'Inputs', 'Input(s) MIME type. Change with care.'),
            }
        if name:
            self.__name__ = name

    def name(self):
        return self.__name__

    def __getattr__(self, attr):
        if attr == 'inputs':
            return self.config['inputs']
        if attr == 'output':
            return self.config['output']
        raise AttributeError(attr)

    def convert(self, orig, data, **kwargs):
        body = bodyfinder(orig)
        data.setData(body)
        return data

def register():
    return HTMLBody()
