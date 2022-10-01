import PIL.Image as PIL_Image
import os
import transaction
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class FileUpload(file):
  """Act as an uploaded file.
  """
  __allow_access_to_unprotected_subobjects__ = 1
  def __init__(self, path, name):
    self.filename = name
    file.__init__(self, path)
    self.headers = {}

def makeFilePath(name):
 # return os.path.join(os.path.dirname(__file__), 'tmp', name)
  return name

def makeFileUpload(name, as_name=None):
  if as_name is None:
    as_name = name
  path = makeFilePath(name)
  return FileUpload(path, as_name)


def uploadImage(self):
    portal = self.getPortalObject()
    image = portal.restrictedTraverse('portal_skins/erp5_safeimage/img/image_test.jpg')
    path_image = "tmp/selenium_image_test.jpg"
    fd = os.open(path_image, os.O_CREAT | os.O_RDWR)
    os.write(fd,str(image.data))
    os.close(fd)
    tile_image_transformed = makeFileUpload(path_image)
    tile_transformed = self.image_module.newContent(portal_type='Image Tile Transformed',
          title='testTileTransformed', id='testTileTransformed',
          file=tile_image_transformed, filename='testTileTransformed')
    if tile_transformed:
      return True
    else:
      return False

def cleanUp(self):
    portal = self.getPortalObject()
    print("exists path: %r" %os.path.exists("tmp/selenium_image_test.jpg"))
    if os.path.exists("tmp/selenium_image_test.jpg"):
      print("REMOVE IMAGE: %s" %(os.remove("tmp/selenium_image_test.jpg")))
      portal.image_module.manage_delObjects(ids=['testTileTransformed'])
      return True
    else:
      return False
