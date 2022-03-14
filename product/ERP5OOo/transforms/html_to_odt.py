# -*- coding: utf-8 -*-
from __future__ import absolute_import
from Products.PortalTransforms.interfaces import itransform
from zope.interface import implementer
from .oood_commandtransform import OOOdCommandTransform, OOoDocumentDataStream
from .oood_commandtransform import includeMetaContentType
from zLOG import LOG
from lxml import etree, html
from lxml.etree import Element, SubElement

html_parser = etree.HTMLParser(remove_blank_text=True, encoding='utf-8')

@implementer(itransform)
class HTMLToOdt:
  """Transforms HTML to odt by using oood"""

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
    # Try to recover broken HTML documents, specially regarding encoding used
    html_node = etree.XML(orig, parser=html_parser)
    includeMetaContentType(html_node)
    orig = html.tostring(html_node, encoding='utf-8',
                         include_meta_content_type=True)

    doc = OOOdCommandTransform(context, filename, orig, self.inputs[0])
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
