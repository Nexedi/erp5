from Products.PortalTransforms.interfaces import itransform
from zope.interface import implements
from oood_commandtransform import OOOdCommandTransform, OOoDocumentDataStream
from zLOG import LOG

class HTMLToOdt:
  """Transforms HTML to odt by using oood"""

  implements(itransform)

  __name__ = 'html_to_odt'
  inputs   = ('text/html',)
  output = 'application/vnd.oasis.opendocument.text'

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
    doc = OOOdCommandTransform(context, filename, orig, self.inputs[0])
    doc.convert()
    odt = doc.convertTo('odt')
    if cache is not None:
      cache.setData(odt)
      return cache
    else:
      stream = OOoDocumentDataStream()
      stream.setData(odt)
      return stream

def register():
  return HTMLToOdt()
