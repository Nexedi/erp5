# -*- coding: utf-8 -*-

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

  def _getAllowedSourceMimetypeFromConversionServer(self, server_proxy):
    for mimetype in self.inputs:
      for allowed_mimetype, _ in server_proxy.getAllowedConversionFormatList(mimetype):
        if mimetype == allowed_mimetype:
          return mimetype

    return None

  def convert(self, orig, data, context=None, **kwargs):
    server_proxy = DocumentConversionServerProxy(context)

    source_mimetype = self._getAllowedSourceMimetypeFromConversionServer(server_proxy)
    if source_mimetype is None:
      raise ConversionError('Formats not allowed %s' % self.inputs)

    return dec(server_proxy.convertFile(
      enc(orig),
      source_mimetype,
      self.output,
      # Default values are ConversionServer default ones
      kwargs.get('zip', False),
      kwargs.get('refresh', False),
      kwargs.get('conversion_kw', {})))
