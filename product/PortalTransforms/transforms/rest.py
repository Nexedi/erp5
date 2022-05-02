from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implementer
from reStructuredText import HTML
import sys

@implementer(ITransform)
class rest:
    r"""Converts from reST to HTML.

      >>> transform = rest()
      >>> class D:
      ...     def setData(self, data):
      ...         self.value = data

      >>> data = transform.convert('*hello world*', D())
      >>> print data.value
      <p><em>hello world</em></p>
      <BLANKLINE>

    We want the 'raw' and 'include' directives to be disabled by
    default:

      >>> try:
      ...     out = transform.convert('.. raw:: html\n  :file: <isonum.txt>', D())
      ... except NotImplementedError:
      ...     print 'Good'
      ... else:
      ...     if "&quot;raw&quot; directive disabled." in out.value:
      ...         print 'Good'
      ...     else:
      ...         print 'Failure'
      Good

      >>> try:
      ...     out = transform.convert('.. include:: <isonum.txt>', D())
      ... except NotImplementedError:
      ...     print 'Good'
      ... else:
      ...     if "&quot;include&quot; directive disabled." in out.value:
      ...         print 'Good'
      ...     else:
      ...         print 'Failure'
      Good
    """

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
