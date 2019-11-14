# -*- coding: utf-8 -*-

from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
from erp5.component.module.TransformLib import DocumentConversionServerTransform
class TransformHtmlToPdf(DocumentConversionServerTransform):
  """
  Transforms HTML to PDF through document conversion server
  """
  implements(ITransform)

  __name__ = 'html_to_pdf'
  inputs = ('text/html',)
  output = 'application/pdf'

  def _getFormatFromMimetype(self, mimetype):
    # XXX: mimetypes.guess_extension() for text/html may returns either '.htm'
    # or '.html' but the former is not supported by wkhtmltopdf Handler
    # (https://lab.nexedi.com/nexedi/cloudooo/merge_requests/20)
    return 'html' if mimetype == 'text/html' else 'pdf'

  def convert(self, *args, **kwargs):
    # wkhtmltopdf handler currently requires conversion_kw (hack in convertFile())...
    if 'conversion_kw' not in kwargs:
      kwargs['conversion_kw'] = {'encoding': 'utf-8'}

#    raise RuntimeError
    return DocumentConversionServerTransform.convert(self, *args, **kwargs)

def register():
  return TransformHtmlToPdf()