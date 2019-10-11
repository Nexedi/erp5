# -*- coding: utf-8 -*-

from zope.interface import implements
from Products.PortalTransforms.interfaces import IDataStream
class DocumentDataStream:
  """Handle OOoDocument in Portal Transforms"""
  implements(IDataStream)

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

from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.ERP5.Document.Document import DocumentConversionServerProxy, ConversionError, enc, dec
class DocumentTransform(commandtransform):
  """
  Transformer using conversion server
  """
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
    # TODO?
    return data

  def includeExternalCssList(self, data):
    # TODO?
    return data

  def convertTo(self, format):
    server_proxy = DocumentConversionServerProxy(self.context)
    _, response_dict, _ = server_proxy.getAllowedTargetItemList(self.mimetype)
    allowed_extension_list = response_dict['response_data']
    if format in dict(allowed_extension_list):
      _, response_dict, _ = server_proxy.run_generate(
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