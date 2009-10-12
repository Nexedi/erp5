from Products.PortalTransforms.interfaces import itransform
from reStructuredText import HTML
import sys
from zope.interface import implements

class rest:
    implements(itransform)

    __name__ = "rest_to_html"
    inputs  = ("text/x-rst", "text/restructured",)
    output = "text/html"

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):
        # do the format
        encoding        = kwargs.get('encoding', 'utf-8')
        input_encoding  = kwargs.get('input_encoding', encoding)
        output_encoding = kwargs.get('output_encoding', encoding)
        language        = kwargs.get('language', 'en') 
        warnings        = kwargs.get('warnings', None) 
        settings = {'documentclass': '',
                    'traceback': 1,
               }
        html = HTML(orig, 
                    report_level=2,
                    input_encoding=input_encoding, 
                    output_encoding=output_encoding, 
                    language_code=language, 
                    warnings=warnings, 
                    settings=settings)
        html = html.replace(' class="document"', '', 1)
        data.setData(html)
        return data

def register():
    return rest()
