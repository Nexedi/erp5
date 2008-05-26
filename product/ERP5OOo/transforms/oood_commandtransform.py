from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.PortalTransforms.interfaces import idatastream
from Products.ERP5Type.Document import newTempOOoDocument
from zLOG import LOG

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
    self.data = data
    self.context = context
    self.mimetype = mimetype

  def name(self):
    return self.__name__

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
      return data
    else:
      raise TransformError