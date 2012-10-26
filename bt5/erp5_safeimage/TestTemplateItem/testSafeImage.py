#from Products.ERP5.Document.Image import Image
#from Products.ERP5Type.tests.utils import FileUpload
import Image
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import transaction
from zLOG import LOG,INFO,ERROR 
import json 
from cStringIO import StringIO
import os


class FileUpload(file):
  """Act as an uploaded file.
  """
  __allow_access_to_unprotected_subobjects__ = 1
  def __init__(self, path, name):
    self.filename = name
    file.__init__(self, path)
    self.headers = {}


def makeFilePath(name):
  return os.path.join(os.path.dirname(__file__), 'tmp', name)

def makeFileUpload(name, as_name=None):
  if as_name is None:
    as_name = name
  path = makeFilePath(name)
  return FileUpload(path, as_name)

class TestSafeImage(ERP5TypeTestCase):

  def afterSetUp(self):
    portal = self.getPortalObject()
    self.image_module = self.portal.getDefaultModule(portal_type = 'Image Module')
    self.assertTrue(self.image_module is not None)
    
    if getattr(self.image_module,'testfruit',None) is not None: 
      LOG('DELETE IMAGEEEEEEE',INFO,'DELETEEEEEEEEE  IMAGEEEE!!!!!')
      self.image_module.manage_delObjects(ids=['testfruit'])
   
    if getattr(self.image_module,'testTile',None) is not None: 
      LOG('DELETE TEST TILE',INFO,'DELETEEEEEEEEE!!!!!')
      self.image_module.manage_delObjects(ids=['testTile'])
   
    if getattr(self.image_module,'testTileTransformed',None) is not None: 
      self.image_module.manage_delObjects(ids=['testTileTransformed'])
      LOG('DELETE TEST TILETRANSFORMED!!!!!!!',INFO,'DELETEEEEEEEEE TTTTTTT!!!!!')
    transaction.commit()
    self.tic()  


  def _createImage(self):
    portal = self.getPortalObject()
    image_path = portal.portal_skins.erp5_safeimage.fruit
    image_buffer = StringIO()
    image_buffer.write(image_path.data.__str__())
    image_buffer.seek(0)
    image = self.image_module.newContent(portal_type='Image',title='testfruit',
                                id='testfruit',file=image_buffer,filename='testfruit')   
    return image 
 
  def _createTileImage(self):
    portal = self.getPortalObject()
    tile_image = makeFileUpload('fruit.jpg')
    tile = self.image_module.newContent(portal_type='Image Tile',title='testTile',
                             id='testTile',file=tile_image,filename='testTile')
    return tile 
  
  def _createTileImageTransformed(self):
    portal = self.getPortalObject()
    tile_image_transformed = makeFileUpload('fruit.jpg')
    tile_transformed = self.image_module.newContent(portal_type='Image Tile Transformed',
                             title='testTileTransformed',id='testTileTransformed',
                             file=tile_image_transformed,filename='testTileTransformed')
    return tile_transformed 
 
  def test_01_CreateImage(self):
    image = self._createImage()
    self.assertTrue(image.hasData())
    transaction.commit()
    self.tic()
    self.assertNotEqual(image,None) 
  
  def test_02_CreateTileImage(self):
    tile = self._createTileImage()
    transaction.commit()
    self.tic()
    self.assertNotEqual(tile,None)
    tile_image_list = tile.objectValues() 
    LOG('len TILE:',INFO,'%s' %(len(tile_image_list)))
    self.assertEquals(len(tile_image_list),2)

  def test_03_CreateTileImageTransformed(self):
    tile_transformed = self._createTileImageTransformed()
    transaction.commit()
    self.tic()
    self.assertNotEqual(tile_transformed,None)   
    tile_image_transformed_list = tile_transformed.objectValues()
    LOG('len TRANSFOR:',INFO,'%s' %(len(tile_image_transformed_list)))
    self.assertEquals(len(tile_image_transformed_list),3)    
