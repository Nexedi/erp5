from Products.PortalTransforms.interfaces import itransform
from zope.interface import implements
from Products.ERP5OOo.transforms.oood_commandtransform import OOOdCommandTransform, OOoDocumentDataStream


class OdpToSxi:
  """Transforms odp to sxi by using Cloudooo"""

  implements(itransform)

  __name__ = 'odp_to_sxi'
  inputs   = ('application/vnd.oasis.opendocument.presentation',)
  output = 'application/vnd.sun.xml.impress'

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
    sxi = odp.convertTo('sxi')
    if cache is not None:
      cache.setData(sxi)
      return cache
    else:
      stream = OOoDocumentDataStream()
      stream.setData(sxi)
      return stream

def register():
  return OdpToSxi()
