from Products.PortalTransforms.interfaces import itransform
from zope.interface import implementer
from Products.ERP5OOo.transforms.oood_commandtransform import OOOdCommandTransform, OOoDocumentDataStream


@implementer(itransform)
class PdfToBmp:
  """Transforms pdf to bmp by using Cloudooo"""

  __name__ = 'pdf_to_bmp'
  inputs   = ('application/pdf',)
  output = 'image/x-ms-bmp'  # image/bmp

  tranform_engine = OOOdCommandTransform.__module__

  def name(self):
    return self.__name__

  def __getattr__(self, attr):
    if attr == 'inputs':
      return self.config['inputs']
    if attr == 'output':
      return self.config['output']
    raise AttributeError(attr)

  def convert(self, orig, data, cache=None, filename=None, context=None, **kwargs):
    data = bytes(orig)
    pdf = OOOdCommandTransform(context, filename, data, self.inputs[0])
    bmp = pdf.convertTo('bmp')
    if cache is not None:
      cache.setData(bmp)
      return cache
    else:
      stream = OOoDocumentDataStream()
      stream.setData(bmp)
      return stream

def register():
  return PdfToBmp()
