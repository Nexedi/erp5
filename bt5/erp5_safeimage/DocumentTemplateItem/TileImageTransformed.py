import random
import base64
from cStringIO import StringIO
from Products.ERP5.Document.Image import Image
from Products.ZoomifyImage.ZoomifyZopeProcessor import ZoomifyZopeProcessor
from Products.ZoomifyImage.ZoomifyBase import ZoomifyBase
from zLOG import LOG,INFO,ERROR,WARNING
#from Crypto.Cipher import AES
#from Crypto import Random


class ERP5ZoomifyZopeProcessor(ZoomifyZopeProcessor):

  def __init__(self, document):
    self.document = document
    self.count = 0

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
      #msg = self.encrypto(tileImageData.getvalue())
    
      if tile_group is None:
        raise AttributeError('unable to fine tile group %r' % tile_group_id)
      w = tile_group.newContent(portal_type='Image',title=namesplit[0],id=namesplit[0],file=tileImageData,filename=namesplit[0])
      LOG('SAVE TILE',INFO,'Title: %s' %(namesplit[0],))
      self._updateTransformedFile(tile_group_id,namesplit[0])
    return


  def saveXMLOutput(self):
    """save the xml file"""

    my_string = StringIO()
    my_string.write(self.getXMLOutput())
    my_string.seek(0)
    self.document.newContent(portal_type='Embedded File',id='ImageProperties.xml',file=my_string, filename='ImageProperties.xml')
    return

  def _updateTransformedFile(self,tile_group_id,tile_title):
    """create and save the transform file"""
   
    num = random.choice([0,1])
    while num >= 0: 
      algorithm = random.choice(['sepia','brightness','noise','lighten','posterize','edge','none'])
      if algorithm == 'lighten':
        param1 = random.choice([-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0.1,0.2,0.3,0.4,0.5,0.6])
        param2 = 0
      elif algorithm == 'posterize':
        param1 = random.choice([4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21])
        param2 = 0
      elif algorithm == 'brightness':
        param1 = random.choice([-80,-60,-40,-20,20,40,60,80])
        param2 = random.choice([-0.3,-0.2,-0.1,0,0.1,0.5,0.9])
      else:
        param1 = 0
        param2 = 0
      my_text = '%s %s %s %s %s %s \n' %(tile_group_id,tile_title,algorithm,param1,param2,num)
      self.my_file.write(my_text)
      num = num - 1     
      
  def saveTransformedFile(self):
    """add in Zope the transform file """
    
    self.my_file.seek(0)
    self.document.newContent(portal_type='Embedded File', id='TransformFile.txt',file=self.my_file,filename='TransformFile.txt')
    return

 # def encrypto(self,message='Attack at dawn'):
 #   """encrypto each thing"""
 #   key ='abcdefghijklmnop'
 #   iv = Random.new().read(AES.block_size)
 #   EncodeIV = lambda : base64.b64encode(iv)
 #   EncodeAES = lambda c, s: base64.b64encode(c.encrypt(message))
 #   IVcoded  = EncodeIV()
 #   cipher = AES.new(key,AES.MODE_CFB,iv)
 #   msg  = EncodeAES(cipher,key)
 #   return msg    
    

class TileImageTransformed(Image):
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



                       
