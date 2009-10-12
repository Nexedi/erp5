from Products.PortalTransforms.interfaces import itransform
from zope.interface import implements
from oood_commandtransform import OOOdCommandTransform, OOoDocumentDataStream
from zLOG import LOG


class OdtToPdf:
  """Transforms ODT to PDF by using oood"""

  implements(itransform)

  __name__ = 'odt_to_pdf'
  inputs   = ('application/vnd.oasis.opendocument.text',)
  output = 'application/pdf'

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
    data = str(orig)
    doc = OOOdCommandTransform(context, filename, data, self.inputs[0])
    doc.convert()
    pdf = doc.convertTo('pdf')
    if cache is not None:
      cache.setData(pdf)
      return cache
    else:
      stream = OOoDocumentDataStream()
      stream.setData(pdf)
      return stream

def register():
  return OdtToPdf()
