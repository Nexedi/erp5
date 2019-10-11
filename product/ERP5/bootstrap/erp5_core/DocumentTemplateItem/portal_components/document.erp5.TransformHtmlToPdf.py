# -*- coding: utf-8 -*-

from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
from erp5.component.module.TransformLib import DocumentTransform, DocumentDataStream
class TransformHtmlToPdf:
  """
  Transforms HTML to PDF through document conversion server
  """
  implements(ITransform)

  __name__ = 'html_to_pdf'
  inputs   = ('text/html',)
  output = 'application/pdf'

  tranform_engine = DocumentTransform.__module__

  def name(self):
    return self.__name__

  def __getattr__(self, attr):
    if attr == 'inputs':
      return self.config['inputs']
    if attr == 'output':
      return self.config['output']
    raise AttributeError(attr)

  def convert(self, orig, data, cache=None, filename=None, context=None, **kwargs):
    print "filename=%r, context=%r, kwargs=%r" % (
      filename, context, kwargs)
    data = str(orig)
    doc = DocumentTransform(context, filename, data, self.inputs[0])
    pdf = doc.convertTo('pdf')
    if cache is not None:
      cache.setData(pdf)
      return cache
    else:
      stream = DocumentDataStream()
      stream.setData(pdf)
      return stream

def register():
  return TransformHtmlToPdf()