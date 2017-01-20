from Products.PortalTransforms.interfaces import itransform
from zope.interface import implements
from Products.ERP5OOo.transforms.oood_commandtransform import OOOdCommandTransform, OOoDocumentDataStream

class OdsToXlsx:
  """Transforms ods to xlsx by using Cloudooo"""

  implements(itransform)

  __name__ = 'ods_to_xlsx'
  inputs   = ('application/vnd.oasis.opendocument.spreadsheet',)
  output = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

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
    xlsx = ods.convertTo('xlsx')
    if cache is not None:
      cache.setData(xlsx)
      return cache
    else:
      stream = OOoDocumentDataStream()
      stream.setData(xlsx)
      return stream

def register():
  return OdsToXlsx()
