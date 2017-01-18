from Products.PortalTransforms.interfaces import itransform
from zope.interface import implements
from Products.ERP5OOo.transforms.oood_commandtransform import OOOdCommandTransform, OOoDocumentDataStream


class OdpToPdf:
  """Transforms odp to pdf by using Cloudooo"""

  implements(itransform)

  __name__ = 'odp_to_pdf'
  inputs   = ('application/vnd.oasis.opendocument.presentation',)
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
    odp = OOOdCommandTransform(context, filename, data, self.inputs[0])
    pdf = odp.convertTo('pdf')
    if cache is not None:
      cache.setData(pdf)
      return cache
    else:
      stream = OOoDocumentDataStream()
      stream.setData(pdf)
      return stream

def register():
  return OdpToPdf()
