# -*- coding: utf-8 -*-
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.PortalTransforms.interfaces import idatastream
from Products.ERP5Type.Document import newTempOOoDocument
from Products.ERP5.Document.Document import ConversionError
from Acquisition import aq_base
from zope.interface import implements
from OFS.Image import Image as OFSImage
from zLOG import LOG

from Products.ERP5OOo.OOoUtils import OOoBuilder
import re
from lxml import etree
from lxml import html
from lxml.etree import ParseError, Element
from lxml.etree import SubElement

from urllib import unquote
from urlparse import parse_qsl, urlparse

# XXX Must be replaced by portal_data_adapters soon
from Products.ERP5.Document.Document import DocumentConversionServerProxy
from Products.ERP5.Document.Document import enc
from Products.ERP5.Document.Document import dec

def includeMetaContentType(html_node):
  """XXX Temp workaround time to fix issue
  in lxml when include_meta_content_type is not honoured
  Force encondig into utf-8
  """
  head = html_node.find('head')
  if head is None:
    head = Element('head')
    html_node.insert(0, head)
  meta_content_type_node_list = head.xpath('meta[translate('\
               'attribute::http-equiv, "CONTEYP", "conteyp") = "content-type"]')
  for meta_content_type_node in meta_content_type_node_list:
    head.remove(meta_content_type_node)
  SubElement(head, 'meta', **{'http-equiv': 'Content-Type',
                              'content': 'application/xhtml+xml; charset=utf-8'})

CLEAN_RELATIVE_PATH = re.compile('^../')

class OOoDocumentDataStream:
  """Handle OOoDocument in Portal Transforms"""
  implements(idatastream)

  def setData(self, value):
    """set the main"""
    self.value = value

  def getData(self):
    return self.value

  def setSubObjects(self, objects):
    pass

  def getSubObjects(self):
    return {}

  def getMetadata(self):
    """return a dict-like object with any optional metadata from
    the transform
    You can modify the returned dictionnary to add/change metadata
    """
    return {}

  def isCacheable(self):
    """
     True by Default
    """
    return getattr(self, '_is_cacheable', True)

  def setCachable(self, value):
    self._is_cacheable = value

class OOOdCommandTransform(commandtransform):
  """Transformer using oood"""

  def __init__(self, context, name, data, mimetype):
    commandtransform.__init__(self, name)
    self.__name__ = name
    self.mimetype = mimetype
    self.context = context
    if self.mimetype == 'text/html':
      data = self.includeExternalCssList(data)
    self.data = data

  def name(self):
    return self.__name__

  def includeImageList(self, data):
    """Include Images in ODF archive

    - data: zipped archive content
    """
    builder = OOoBuilder(data)
    content = builder.extract('content.xml')
    xml_doc = etree.XML(content)
    image_tag_list = xml_doc.xpath('//*[name() = "draw:image"]')
    SVG_NAMESPACE = 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0'
    XLINK_NAMESPACE = 'http://www.w3.org/1999/xlink'
    ratio_px_cm = 2.54 / 100.
    # Flag to enable modification of OOoBuilder
    odt_content_modified = False
    for image_tag in image_tag_list:
      frame = image_tag.getparent()
      #Try to get image file from ZODB
      href_attribute_list = image_tag.xpath('.//@*[name() = "xlink:href"]')
      url = href_attribute_list[0]
      parse_result = urlparse(unquote(url))
      # urlparse return a 6-tuple: scheme, netloc, path, params, query, fragment
      netloc = parse_result[1]
      path = parse_result[2]
      if path and netloc in ('', None):
        # it makes sense to include only relative to current site images not remote ones which can be taken by OOo
        # OOo corrupt relative Links inside HTML content during odt conversion
        # <img src="REF.TO.IMAGE" ... /> become <draw:image xlink:href="../REF.TO.IMAGE" ... />
        # So remove "../" added by OOo
        path = CLEAN_RELATIVE_PATH.sub('', path)
        # in some cases like Web Page content "/../" can be contained in image URL which will break
        # restrictedTraverse calls, our best guess is to remove it
        path = path.replace('/../', '')
        # remove occurencies of '//' or '///' in path (happens with web pages) and leave
        # a traversable relative URL
        path = '/'.join([x for x in path.split('/') if x.strip()!=''])
        # retrieve http parameters and use them to convert image
        query_parameter_string = parse_result[4]
        image_parameter_dict = dict(parse_qsl(query_parameter_string))
        try:
          image = self.context.restrictedTraverse(path)
        except (AttributeError, KeyError):
          #Image not found, this image is probably not hosted by ZODB. Do nothing
          image = None
        if image is not None:
          odt_content_modified = True
          content_type = image.getContentType()
          format = image_parameter_dict.pop('format', None)
          # convert API accepts only a certail range of arguments
          for key, value in image_parameter_dict.items():
            if key not in ('format', 'display', 'quality', 'resolution',):
              image_parameter_dict.pop(key)
          if getattr(image, 'convert', None) is not None:
            # The document support conversion so perform conversion
            # according given parameters
            mime, image_data = image.convert(format, **image_parameter_dict)
            # wrapp converted data into OFSImage in order to compute metadatas
            # on converted result
            image = OFSImage(image.getId(), image.getTitle(), image_data)

          # image should be OFSImage
          data = str(image.data)
          width = image.width
          height = image.height
          if height:
            frame.attrib.update({'{%s}height' % SVG_NAMESPACE: '%.3fcm' % (height * ratio_px_cm)})
          if width:
            frame.attrib.update({'{%s}width' % SVG_NAMESPACE: '%.3fcm' % (width * ratio_px_cm)})
          if not format:
            mimetype_list = self.context.getPortalObject().mimetypes_registry.lookup(content_type)
            # guess a format with help of mimetypes_registry
            for mimetype_object in mimetype_list:
              if mimetype_object.extensions:
                format = mimetype_object.extensions[0]
                break
              elif mimetype_object.globs:
                format = mimetype_object.globs[0].strip('*.')
                break
          new_path = builder.addImage(data, format=format)
          image_tag.attrib.update({'{%s}href' % XLINK_NAMESPACE: new_path})
    if odt_content_modified:
      builder.replace('content.xml', etree.tostring(xml_doc, encoding='utf-8',
                                                    xml_declaration=True,
                                                    pretty_print=False))
    return builder.render()

  def includeExternalCssList(self, data):
    """Replace external Css link by style Element,
    to avoid ooo querying portal without crendentials through http.

    - data: html content
    """
    try:
      xml_doc = etree.XML(data)
    except ParseError:
      #If not valid xhtml do nothing
      return data
    xpath = '//*[local-name() = "link"][@type = "text/css"]'
    css_link_tag_list = xml_doc.xpath(xpath)
    for css_link_tag in css_link_tag_list:
      #Try to get css from ZODB
      href_attribute_list = css_link_tag.xpath('.//@href')
      url = href_attribute_list[0]
      parse_result = urlparse(unquote(url))
      # urlparse return a 6-tuple: scheme, netloc, path, params, query, fragment
      path = parse_result[2]
      if path:
        try:
          css_object = self.context.restrictedTraverse(path)
        except (AttributeError, KeyError):
          #Image not found, this image is probably not hosted by ZODB. Do nothing
          css_object = None
        if css_object is not None:
          if callable(aq_base(css_object)):
            #In case of DTMLDocument
            css_as_text = css_object(client=self.context.getPortalObject())
          else:
            #Other cases like files
            css_as_text = str(css_object)
          parent_node = css_link_tag.getparent()
          style_node = Element('style')
          style_node.text = css_as_text
          parent_node.append(style_node)
          style_node.attrib.update({'type': 'text/css'})
          parent_node.remove(css_link_tag)

    includeMetaContentType(xml_doc)
    xml_output = html.tostring(xml_doc, encoding='utf-8',
                               include_meta_content_type=True)

    return xml_output

  def convertTo(self, format):
    server_proxy = DocumentConversionServerProxy(self.context)
    response_code, response_dict, message = \
                           server_proxy.getAllowedTargetItemList(self.mimetype)
    allowed_extension_list = response_dict['response_data']
    if format in dict(allowed_extension_list):
      response_code, response_dict, message = server_proxy.run_generate(
                                                                '',
                                                                enc(self.data),
                                                                None,
                                                                format,
                                                                self.mimetype)
      data = dec(response_dict['data'])
      if self.mimetype == 'text/html':
        data = self.includeImageList(data)
      return data
    else:
      raise ConversionError('Format not allowed %s' % format)
