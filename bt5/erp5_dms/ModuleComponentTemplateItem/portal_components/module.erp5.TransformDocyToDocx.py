from Products.PortalTransforms.interfaces import itransform
from zope.interface import implements
from Products.ERP5OOo.transforms.oood_commandtransform import OOOdCommandTransform, OOoDocumentDataStream

class TransformDocyToDocx:
  """Transforms docy to docx by using Cloudooo"""

  implements(itransform)

  __name__ = 'docy_to_docx'
  inputs   = ('application/x-asc-text',)
  output = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

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
    docy = OOOdCommandTransform(context, filename, data, self.inputs[0])
    docx = docy.convertTo('docx')
    if cache is not None:
      cache.setData(docx)
      return cache
    else:
      stream = OOoDocumentDataStream()
      stream.setData(docx)
      return stream

def register():
  return TransformDocyToDocx()
