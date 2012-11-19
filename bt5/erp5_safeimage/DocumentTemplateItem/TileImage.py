from cStringIO import StringIO
from Products.ERP5.Document.Image import Image
from Products.ZoomifyImage.ZoomifyZopeProcessor import ZoomifyZopeProcessor
from Products.ZoomifyImage.ZoomifyBase import ZoomifyBase
from zLOG import LOG,INFO,ERROR,WARNING

class ERP5ZoomifyZopeProcessor(ZoomifyZopeProcessor):

  def __init__(self, document):
     self.document = document

  def createTileContainer(self, tileContainerName=None):
    """ create each TileGroup """

    self.document.newContent(portal_type="Image Tile Group",title=tileContainerName, id=tileContainerName,filename=tileContainerName)
    return 

  def createDefaultViewer(self):
    """ add the default Zoomify viewer to the Zoomify metadata """
                                                   
    pass
    return
   
  def createDataContainer(self, imageName="None"):
    """Creates nothing coz we are already in the container"""
    
    pass
    return

  def saveTile(self, image, scaleNumber, column,row):
    """save the cropped region"""
    
    tileFileName = self.getTileFileName(scaleNumber, column, row)
    tileContainerName = self.getAssignedTileContainerName(tileFileName=tileFileName)
    namesplit = tileFileName.split('.')
    w,h = image.size
    if w != 0 and h !=0:
      tile_group_id = self.getAssignedTileContainerName()
      tile_group=self.document[tile_group_id]
      tileImageData= StringIO()
      image.save(tileImageData,'JPEG',quality=self.qualitySetting)
      tileImageData.seek(0)

      if tile_group is None:
        raise AttributeError('unable to fine tile group %r' % tile_group_id)
      w = tile_group.newContent(portal_type='Image',title=namesplit[0],id=namesplit[0],file=tileImageData,filename=namesplit[0]) 
    return 

  def saveXMLOutput(self):
    """save the xml file"""

    my_string = StringIO()
    my_string.write(self.getXMLOutput())
    my_string.seek(0)
    self.document.newContent(portal_type='Embedded File',id='ImageProperties.xml',file=my_string, filename='ImageProperties.xml')
    return
 
class TileImage(Image):
  """
  Tile Images split images in many small parts and then store informations as sub objects
  """

  def _setFile(self, *args, **kw):
    """Set the file content and reset image information."""

    if "TileGroup0" in self.objectIds():
        self.manage_delObjects("TileGroup0")

    if "ImageProperties.xml" in self.objectIds():
        self.manage_delObjects("ImageProperties.xml")

    self._update_image_info()
    processor = ERP5ZoomifyZopeProcessor(self)
    processor.ZoomifyProcess(self.getId(),*args)



