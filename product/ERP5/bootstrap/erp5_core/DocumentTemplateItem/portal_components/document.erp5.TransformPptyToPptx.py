from Products.PortalTransforms.interfaces import itransform
from zope.interface import implements
from Products.ERP5OOo.transforms.oood_commandtransform import OOOdCommandTransform, OOoDocumentDataStream

class PptyToPptx:
  """Transforms ppty to pptx by using Cloudooo"""

  implements(itransform)

  __name__ = 'ppty_to_pptx'
  inputs   = ('application/x-asc-presentation',)
  output = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'

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
    ppty = OOOdCommandTransform(context, filename, data, self.inputs[0])
    pptx = ppty.convertTo('pptx')
    if cache is not None:
      cache.setData(pptx)
      return cache
    else:
      stream = OOoDocumentDataStream()
      stream.setData(pptx)
      return stream

def register():
  return PptyToPptx()
