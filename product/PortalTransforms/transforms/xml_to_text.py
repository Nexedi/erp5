from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
from lxml import etree

class xml_to_text:
    implements(ITransform)

    __name__ = 'xml_to_text'
    inputs  = ('text/xml', 'application/xml')
    output = 'text/plain'

    def name(self):
        return self.__name__

    def convert(self, data, cache, **kw):
        text_list = etree.fromstring(data).itertext()
        out = ' '.join([text for text in text_list if text]).encode('utf-8')
        cache.setData(out)
        return cache

def register():
    return xml_to_text()
