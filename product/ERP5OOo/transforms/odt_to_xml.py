from Products.PortalTransforms.interfaces import itransform
from oood_commandtransform import OOOdCommandTransform, OOoDocumentDataStream
from zLOG import LOG
from Products.ERP5OOo.OOoUtils import OOoBuilder
import re

class OdtToXml:
  """Transforms ODT to Doc by using oood"""

  __implements__ = itransform

  __name__ = 'odt_to_xml'
  inputs   = ('application/vnd.oasis.opendocument.text',)
  output = 'text/xml'

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
    builder = OOoBuilder(doc)
    content = builder.extract('content.xml')
    if cache is not None:
      cache.setData(content)
      return cache
    else:
      stream = OOoDocumentDataStream()
      stream.setData(content)
      return stream

def register():
  return OdtToXml()
