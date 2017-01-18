from Products.PortalTransforms.interfaces import itransform
from zope.interface import implements
from Products.ERP5OOo.transforms.oood_commandtransform import OOOdCommandTransform, OOoDocumentDataStream

class DocxToDocy:
  """Transforms docx to docy by using Cloudooo"""

  implements(itransform)

  __name__ = 'docx_to_docy'
  inputs   = ('application/vnd.openxmlformats-officedocument.wordprocessingml.document',)
  output = 'application/x-asc-text'

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
    docx = OOOdCommandTransform(context, filename, data, self.inputs[0])
    docy = docx.convertTo('docy')
    if cache is not None:
      cache.setData(docy)
      return cache
    else:
      stream = OOoDocumentDataStream()
      stream.setData(docy)
      return stream

def register():
  return DocxToDocy()
