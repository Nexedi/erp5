from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
from plone.intelligenttext.transforms import convertHtmlToWebIntelligentPlainText

class HtmlToWebIntelligentPlainText:
    """Transform which replaces urls and email into hyperlinks"""

    implements(ITransform)

    __name__ = "html_to_web_intelligent_plain_text"
    output = "text/x-web-intelligent"

    def __init__(self, name=None, inputs=('text/html',), tab_width = 4):
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
        text = convertHtmlToWebIntelligentPlainText(orig)            
        data.setData(text)
        return data

def register():
    return HtmlToWebIntelligentPlainText()
