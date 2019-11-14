from Products.PortalTransforms.interfaces import itransform
from zope.interface import implements
from Products.ERP5OOo.transforms.oood_commandtransform import OOOdCommandTransform, OOoDocumentDataStream


class OdsToHtml:
  """Transforms ods to html by using Cloudooo"""

  implements(itransform)

  __name__ = 'ods_to_html'
  inputs   = ('application/vnd.oasis.opendocument.spreadsheet',)
  output = 'text/html'

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
    ods = OOOdCommandTransform(context, filename, data, self.inputs[0])
    html = ods.convertTo('html')
    if cache is not None:
      cache.setData(html)
      return cache
    else:
      stream = OOoDocumentDataStream()
      stream.setData(html)
      return stream

def register():
  return OdsToHtml()
