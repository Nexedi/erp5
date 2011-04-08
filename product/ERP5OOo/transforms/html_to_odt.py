# -*- coding: utf-8 -*-
from Products.PortalTransforms.interfaces import itransform
from zope.interface import implements
from oood_commandtransform import OOOdCommandTransform, OOoDocumentDataStream
from zLOG import LOG
from lxml import etree, html
from lxml.etree import Element, SubElement

html_parser = etree.HTMLParser(remove_blank_text=True, encoding='utf-8')

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
    # Try to recover broken HTML documents, specially regarding encoding used
    html_node = etree.XML(orig, parser=html_parser)
    html_tree = html_node.getroottree()
    head = html_tree.find('head')
    if head is None:
      # This part of code is supposed to be useless
      # lxml.html.tostring function with include_meta_content_type
      # parameter to True, should do the same things. But it does not.
      head = Element('head')
      html_node.insert(0, head)
      SubElement(head, 'meta', **{'http-equiv': 'Content-Type',
                                  'content': 'text/html; charset=utf-8'})
    orig = html.tostring(html_node, encoding='utf-8', method='xml')

    # workaround a Bug in LibreOffice HTML import filter.
    # https://bugs.freedesktop.org/show_bug.cgi?id=36080
    orig = orig.replace('<title/>', '<title></title>')
    import pdb;pdb.set_trace()
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
