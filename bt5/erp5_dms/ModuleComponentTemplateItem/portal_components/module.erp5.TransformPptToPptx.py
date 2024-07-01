from Products.PortalTransforms.interfaces import itransform
from zope.interface import implementer
from Products.ERP5OOo.transforms.oood_commandtransform import OOOdCommandTransform, OOoDocumentDataStream


@implementer(itransform)
class PptToPptx:
  """Transforms ppt to pptx by using Cloudooo"""

  __name__ = 'ppt_to_pptx'
  inputs   = ('application/vnd.ms-powerpoint',
              'application/powerpoint',
              'application/mspowerpoint',
              'application/x-mspowerpoint')
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
    data = bytes(orig)
    ppt = OOOdCommandTransform(context, filename, data, self.inputs[0])
    pptx = ppt.convertTo('pptx')
    if cache is not None:
      cache.setData(pptx)
      return cache
    else:
      stream = OOoDocumentDataStream()
      stream.setData(pptx)
      return stream

def register():
  return PptToPptx()
