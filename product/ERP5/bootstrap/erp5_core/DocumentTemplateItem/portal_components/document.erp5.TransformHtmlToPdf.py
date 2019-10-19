# -*- coding: utf-8 -*-

## XXX module.erp5.TransformLib: Backported for KR not having ModuleComponent yet...
from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
from Products.ERP5.Document.Document import DocumentConversionServerProxy, ConversionError, enc, dec
class DocumentConversionServerTransform:
  """
  Transformer using Conversion Server
  """
  implements(ITransform)

  # Name of the Transform as registered in portal_transforms
  __name__ = None
  # Tuple of source MIME types
  inputs = ()
  # Destination MIME type
  output = ''

  def __init__(self, name=None):
    if name is not None:
      self.__name__ = name

  def name(self):
    return self.__name__

  def _getFormatFromMimetype(self, mimetype):
    """
    XXX: This should not be done here but Conversion Server API to get
         supported Format/Extension is deprecated (topic under discussion)
    """
    import mimetypes
    extension = mimetypes.guess_extension(mimetype)
    if extension is None:
      raise ConversionError("Could not guess extension from mimetype '%s'" % mimetype)
    return extension.split('.', 1)[1]

  def convert(self, orig, data, context=None, **kwargs):
    server_proxy = DocumentConversionServerProxy(context)
    data.setData(dec(server_proxy.convertFile(
      enc(orig),
      "html",
      "pdf",
      # Default values are ConversionServer default ones
      kwargs.get('zip', False),
      kwargs.get('refresh', False),
      kwargs.get('conversion_kw', {}))))
    return data

from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
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

    return DocumentConversionServerTransform.convert(self, *args, **kwargs)

def register():
  return TransformHtmlToPdf()