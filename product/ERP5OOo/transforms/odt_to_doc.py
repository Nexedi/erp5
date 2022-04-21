# -*- coding: utf-8 -*-
from __future__ import absolute_import
from Products.PortalTransforms.interfaces import itransform
from zope.interface import implementer
from .oood_commandtransform import OOOdCommandTransform, OOoDocumentDataStream
from zLOG import LOG


@implementer(itransform)
class OdtToDoc:
  """Transforms ODT to Doc by using oood"""

  __name__ = 'odt_to_doc'
  inputs   = ('application/vnd.oasis.opendocument.text',)
  output = 'application/msword'

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
    msword = doc.convertTo('doc')
    if cache is not None:
      cache.setData(msword)
      return cache
    else:
      stream = OOoDocumentDataStream()
      stream.setData(msword)
      return stream

def register():
  return OdtToDoc()
