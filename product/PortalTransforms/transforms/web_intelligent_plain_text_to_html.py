from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
from plone.intelligenttext.transforms import convertWebIntelligentPlainTextToHtml

class WebIntelligentPlainTextToHtml:
    """Transform which replaces urls and email into hyperlinks"""

    implements(ITransform)

    __name__ = "web_intelligent_plain_text_to_html"
    output = "text/html"

    def __init__(self, name=None, inputs=('text/x-web-intelligent',), tab_width = 4):
        self.config = { 'inputs' : inputs, 'tab_width' : 4}
        self.config_metadata = {
            'inputs' : ('list', 'Inputs', 'Input(s) MIME type. Change with care.'),
            'tab_width' : ('string', 'Tab width', 'Number of spaces for a tab in the input')
            }
        if name:
            self.__name__ = name
        
    def name(self):
        return self.__name__

    def __getattr__(self, attr):
        if attr in self.config:
            return self.config[attr]
        raise AttributeError(attr)

    def convert(self, orig, data, **kwargs):
        text = convertWebIntelligentPlainTextToHtml(orig, tab_width=self.tab_width)
        data.setData(text)
        return data

def register():
    return WebIntelligentPlainTextToHtml()
