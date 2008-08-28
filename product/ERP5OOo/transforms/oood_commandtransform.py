from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.PortalTransforms.interfaces import idatastream
from Products.ERP5Type.Document import newTempOOoDocument
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base
try:
  from Products.ERP5OOo.OOoUtils import OOoBuilder
  import re
  from libxml2 import parseDoc, parserError
  import_succeed = 1
except ImportError:
  import_succeed = 0
from zLOG import LOG

REMOTE_URL_PATTERN = '^((?P<protocol>http(s)?://)(?P<domain>[.a-zA-Z0-9]+)+)?(?P<port>:\d{4})?(?P<path>/?\S*)'

class TransformError(Exception):
  pass

class OOoDocumentDataStream:
  """Handle OOoDocument in Portal Transforms"""
  __implements__ = idatastream

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
    if name:
      self.__name__ = name
    self.mimetype = mimetype
    self.context = context
    if import_succeed and self.mimetype == 'text/html':
      data = self.includeExternalCssList(data)
    self.data = data

  def name(self):
    return self.__name__

  def includeImageList(self, data):
    """
      Include Images in ODF archive
    """
    builder = OOoBuilder(data)
    content = builder.extract('content.xml')
    xml_doc = parseDoc(content)
    image_tag_list = xml_doc.xpathEval('//*[name() = "draw:image"]')
    svg_ns = xml_doc.getRootElement().searchNs(xml_doc, 'svg')
    ratio_px_cm = 2.54 / 100.
    for image_tag in image_tag_list:
      frame = image_tag.parent
      #Try to get image file from ZODB
      href_attribute_list = image_tag.xpathEval('.//@*[name() = "xlink:href"]')
      href_attribute = href_attribute_list[0]
      url = href_attribute.get_content()
      matching = re.match(REMOTE_URL_PATTERN, url)
      if matching is not None:
        path = matching.groupdict().get('path')
        try:
          image = self.context.restrictedTraverse(path)
        except (AttributeError, KeyError):
          #Image not found, this image is probably not hosted by ZODB. Do nothing
          image = None
        if image is not None:
          content_type = image.getContentType()
          mimetype_list = getToolByName(self.context,
                                        'mimetypes_registry').lookup(content_type)
          #Need to improve default format handling
          format = 'png'
          if mimetype_list:
            format = mimetype_list[0].minor()
          try:
            #ERP5 API
            data = image.getData()
            height = image.getHeight()
            width = image.getWidth()
          except (AttributeError, KeyError):
            #OFS API
            data = image.data
            height = image.height
            width = image.width
          if height:
            frame.setNsProp(svg_ns, 'height', '%.3fcm' % (height * ratio_px_cm))
          if width:
            frame.setNsProp(svg_ns, 'width', '%.3fcm' % (width * ratio_px_cm))
          new_path = builder.addImage(data, format=format)
          href_attribute.setContent(new_path)
    builder.replace('content.xml', xml_doc.serialize('utf-8', 0))
    xml_doc.freeDoc()
    return builder.render()

  def includeExternalCssList(self, data):
    """
      Replace external Css link by style Element
    """
    try:
      xml_doc = parseDoc(data)
    except parserError:
      #If not valid xhtml do nothing
      return data
    xpath = '//*[local-name() = "link"][@type = "text/css"]'
    css_link_tag_list = xml_doc.xpathEval(xpath)
    for css_link_tag in css_link_tag_list:
      #Try to get css from ZODB
      href_attribute_list = css_link_tag.xpathEval('.//@href')
      href_attribute = href_attribute_list[0]
      url = href_attribute.get_content()
      matching = re.match(REMOTE_URL_PATTERN, url)
      if matching is not None:
        path = matching.groupdict().get('path')
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
          style_node = xml_doc.newChild(None, 'style', css_as_text)
          style_node.setProp('type', 'text/css')
          css_link_tag.replaceNode(style_node)
    #omit xml-declaration
    data = xml_doc.serialize('utf-8', 0)\
                     .replace('<?xml version="1.0" encoding="utf-8"?>\n', '')
    xml_doc.freeDoc()
    return data

  def convert(self):
    tmp_ooo = newTempOOoDocument(self.context, self.name)
    tmp_ooo.edit( base_data=self.data,
                  fname=self.name,
                  source_reference=self.name,
                  base_content_type=self.mimetype,)
    tmp_ooo.oo_data = self.data
    self.ooo = tmp_ooo

  def convertTo(self, format):
    if self.ooo.isTargetFormatAllowed(format):
      mime, data = self.ooo.convert(format)
      if import_succeed and self.mimetype == 'text/html':
        data = self.includeImageList(data)
      return data
    else:
      raise TransformError
