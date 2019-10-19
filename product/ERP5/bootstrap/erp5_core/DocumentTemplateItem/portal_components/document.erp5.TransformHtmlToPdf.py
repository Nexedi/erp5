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

  def convert(self, *args, **kwargs):
    # wkhtmltopdf handler currently requires conversion_kw (hack in convertFile())...
    if 'conversion_kw' not in kwargs:
      kwargs['conversion_kw'] = {'encoding': 'utf-8'}

    return DocumentConversionServerTransform.convert(self, *args, **kwargs)


def register():
  return TransformHtmlToPdf()