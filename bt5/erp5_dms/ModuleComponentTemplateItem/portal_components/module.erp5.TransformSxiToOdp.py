from Products.PortalTransforms.interfaces import itransform
from zope.interface import implementer
from Products.ERP5OOo.transforms.oood_commandtransform import OOOdCommandTransform, OOoDocumentDataStream


@implementer(itransform)
class SxiToOdp:
  """Transforms sxi to odp by using Cloudooo"""

  __name__ = 'sxi_to_odp'
  inputs   = ('application/vnd.sun.xml.impress',)
  output = 'application/vnd.oasis.opendocument.presentation'

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
    sxi = OOOdCommandTransform(context, filename, data, self.inputs[0])
    odp = sxi.convertTo('odp')
    if cache is not None:
      cache.setData(odp)
      return cache
    else:
      stream = OOoDocumentDataStream()
      stream.setData(odp)
      return stream

def register():
  return SxiToOdp()
