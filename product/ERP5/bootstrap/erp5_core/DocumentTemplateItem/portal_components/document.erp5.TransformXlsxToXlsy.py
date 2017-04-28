from Products.PortalTransforms.interfaces import itransform
from zope.interface import implements
from Products.ERP5OOo.transforms.oood_commandtransform import OOOdCommandTransform, OOoDocumentDataStream


class XlsxToXlsy:
  """Transforms xlsx to xlsy by using Cloudooo"""

  implements(itransform)

  __name__ = 'xlsx_to_xlsy'
  inputs   = ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
  output = 'application/x-asc-spreadsheet'

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
    xlsx = OOOdCommandTransform(context, filename, data, self.inputs[0])
    xlsy = xlsx.convertTo('xlsy')
    if cache is not None:
      cache.setData(xlsy)
      return cache
    else:
      stream = OOoDocumentDataStream()
      stream.setData(xlsy)
      return stream

def register():
  return XlsxToXlsy()
