from Products.PortalTransforms.interfaces import itransform
from DocumentTemplate.DT_Util import html_quote
from zope.interface import implements

__revision__ = '$Id: text_pre_to_html.py 3658 2005-02-23 16:29:54Z tiran $'

class TextPreToHTML:
    """simple transform which wraps raw text into a <pre> tag"""

    implements(itransform)

    __name__ = "text-pre_to_html"
    inputs   = ('text/plain-pre',)
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
        data.setData('<pre class="data">%s</pre>' % html_quote(orig))
        return data

def register():
    return TextPreToHTML()
