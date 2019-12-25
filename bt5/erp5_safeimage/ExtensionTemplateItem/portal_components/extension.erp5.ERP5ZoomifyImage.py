##############################################################################
# Copyright (C) 2005  Adam Smith  asmith@agile-software.com
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##############################################################################

import os, sys, shutil, tempfile
from cStringIO import StringIO
from zLOG import LOG,ERROR,INFO,WARNING
from OFS.Image import File, Image
import os, transaction
from AccessControl import getSecurityManager, ClassSecurityInfo
from Globals import package_home
import PIL.Image as PIL_Image
import thread
import random
import base64
from OFS.Folder import Folder 

class ZoomifyBase:

  _v_imageFilename = ''
  format = ''
  originalWidth = 0
  originalHeight = 0
  _v_scaleInfo = []
  numberOfTiles = 0
  _v_tileGroupMappings = {}
  qualitySetting = 80
  tileSize = 256
  my_file = StringIO() 

  def openImage(self):
    """ load the image data """

    pass
    return

  def getImageInfo(self):
    """ """

    image = self.openImage()
    self.format = image.format
    self.originalWidth, self.originalHeight = image.size
    image = None
    width, height = (self.originalWidth, self.originalHeight)
    self._v_scaleInfo = [(width, height)]
    while (width > self.tileSize) or (height > self.tileSize):
      width, height = (width / 2, height / 2)
      self._v_scaleInfo.insert(0, (width, height))
    totalTiles=0
    tier, rows, columns = (0,0,0)
    for tierInfo in self._v_scaleInfo:
      rows = height/self.tileSize
      if height % self.tileSize > 0:
        rows +=1
      columns = width/self.tileSize
      if width%self.tileSize > 0:
        columns += 1
      totalTiles += rows * columns
      tier += 1

  def getImageMetadata(self):
    """ given an image name, load it and extract metadata """

    image = self.openImage()
    self.format = image.format
    self.originalWidth, self.originalHeight = image.size
    image = None
    # get scaling information
    width, height = (self.originalWidth, self.originalHeight)
    self._v_scaleInfo = [(width, height)]
    while (width > self.tileSize) or (height > self.tileSize):
      width, height = (width / 2, height / 2)
      self._v_scaleInfo.insert(0, (width, height))
    # tile and tile group information
    self.preProcess()
    return

  def createDataContainer(self, imageName):
    """ create a container for tile groups and tile metadata """

    pass
    return

  def getAssignedTileContainerName(self, tileFileName=None):
    """ return the name of the tile group for the indicated tile """
    if tileFileName:
      if hasattr(self, '_v_tileGroupMappings') and self._v_tileGroupMappings:
        containerName = self._v_tileGroupMappings.get(tileFileName, None)
        if containerName:
          return containerName
    x = self.getNewTileContainerName()
    return x

  def getNewTileContainerName(self, tileGroupNumber=0):
    """ return the name of the next tile group container """

    return 'TileGroup' + str(tileGroupNumber)

  def createTileContainer(self, tileContainerName=None):
    """ create a container for the next group of tiles within the data container """

    pass
    return

  def getTileFileName(self, scaleNumber, columnNumber, rowNumber):
    """ get the name of the file the tile will be saved as """

    return '%s-%s-%s.jpg' % (str(scaleNumber), str(columnNumber), str(rowNumber))

  def getFileReference(self, scaleNumber, columnNumber, rowNumber):
    """ get the full path of the file the tile will be saved as """

    pass
    return

  def getNumberOfTiles(self):
    """ get the number of tiles generated 
        Should this be implemented as a safeguard, or just use the count of 
        tiles gotten from processing? (This would make subclassing a little
        easier.) """

    return self.numberOfTiles

  def getXMLOutput(self):
    """ create xml metadata about the tiles """

    numberOfTiles = self.getNumberOfTiles()
    xmlOutput = '<IMAGE_PROPERTIES WIDTH="%s" HEIGHT="%s" NUMTILES="%s" NUMIMAGES="1" VERSION="1.8" TILESIZE="%s" />'
    xmlOutput = xmlOutput % (str(self.originalWidth),
            str(self.originalHeight), str(numberOfTiles), str(self.tileSize))
    return xmlOutput

  def saveXMLOutput(self):
    """ save xml metadata about the tiles """

    pass
    return

  def saveTile(self, image, scaleNumber, column, row):
    """ save the cropped region """

    pass
    return

  def processImage(self):
    """ starting with the original image, start processing each row """
    tier=(len(self._v_scaleInfo) -1)
    row = 0
    ul_y, lr_y = (0,0)
    root, ext = os.path.splitext(self._v_imageFilename)
    if not root:
      root = self._v_imageFilename
    ext = '.jpg'
    image = self.openImage()
    while row * self.tileSize < self.originalHeight:
      ul_y = row * self.tileSize
      if (ul_y + self.tileSize) < self.originalHeight:
        lr_y = ul_y + self.tileSize
      else:
        lr_y = self.originalHeight
      print "Going to open image"
      imageRow = image.crop([0, ul_y, self.originalWidth, lr_y])
      saveFilename = root + str(tier) + '-' + str(row) +  ext
      if imageRow.mode != 'RGB':
        imageRow = imageRow.convert('RGB')
      imageRow.save(os.path.join(tempfile.gettempdir(), saveFilename),
                                                        'JPEG', quality=100)
      print "os path exist : %r" % os.path.exists(os.path.join(
                                        tempfile.gettempdir(), saveFilename))
      if os.path.exists(os.path.join(tempfile.gettempdir(), saveFilename)): 
        self.processRowImage(tier=tier, row=row)
      row += 1

  def processRowImage(self, tier=0, row=0):
    """ for an image, create and save tiles """

    print '*** processing tier: ' + str(tier) + ' row: ' + str(row)
    tierWidth, tierHeight = self._v_scaleInfo[tier]
    rowsForTier = tierHeight/self.tileSize
    if tierHeight % self.tileSize > 0:
      rowsForTier +=1
    root, ext = os.path.splitext(self._v_imageFilename)  
    if not root:
      root = self._v_imageFilename
    ext = '.jpg'
    imageRow = None
    if tier == (len(self._v_scaleInfo) -1):
      firstTierRowFile = root + str(tier) + '-' + str(row) + ext
      if os.path.exists(os.path.join(tempfile.gettempdir(),firstTierRowFile)):
        imageRow = PIL_Image.open(os.path.join(tempfile.gettempdir(), 
                                                    firstTierRowFile))
    else:
      # create this row from previous tier's rows
      imageRow = PIL_Image.new('RGB', (tierWidth, self.tileSize))
      firstRowFile = root + str(tier+1) + '-' + str(row + row) + ext
      firstRowWidth, firstRowHeight = (0,0)
      secondRowWidth, secondRowHeight = (0,0)
      if os.path.exists(os.path.join(tempfile.gettempdir(),firstRowFile)):
        firstRowImage = PIL_Image.open(os.path.join(tempfile.gettempdir(),
                                                         firstRowFile))
        firstRowWidth, firstRowHeight = firstRowImage.size
        imageRow.paste(firstRowImage, (0,0))
        os.remove(os.path.join(tempfile.gettempdir(), firstRowFile))
      secondRowFile = root + str(tier+1) + '-' + str(row + row +1) + ext
      # there may not be a second row at the bottom of the image...
      if os.path.exists(os.path.join(tempfile.gettempdir(), secondRowFile)):
        secondRowImage = PIL_Image.open(os.path.join(tempfile.gettempdir(),
                                                        secondRowFile))
        secondRowWidth, secondRowHeight = secondRowImage.size
        imageRow.paste(secondRowImage, (0, firstRowHeight))
        os.remove(os.path.join(tempfile.gettempdir(), secondRowFile))
      # the last row may be less than self.tileSize...
      if (firstRowHeight + secondRowHeight) < (self.tileSize*2):
        imageRow = imageRow.crop((0, 0, tierWidth,
                               (firstRowHeight+secondRowHeight)))
    if imageRow:
      # cycle through columns, then rows
      column = 0
      imageWidth, imageHeight = imageRow.size
      ul_x, ul_y, lr_x, lr_y = (0,0,0,0) # final crop coordinates
      while not ((lr_x == imageWidth) and (lr_y == imageHeight)):
        # set lower right cropping point
        if (ul_x + self.tileSize) < imageWidth:
          lr_x = ul_x + self.tileSize
        else:
          lr_x = imageWidth
        if (ul_y + self.tileSize) < imageHeight:
          lr_y = ul_y + self.tileSize
        else:
          lr_y = imageHeight
        self.saveTile(imageRow.crop([ul_x, ul_y, lr_x, lr_y]), tier,
                                                        column, row)
        self.numberOfTiles += 1
        # set upper left cropping point
        if (lr_x == imageWidth):
          ul_x=0
          ul_y = lr_y
          column = 0
        else:
          ul_x = lr_x
          column += 1
      if tier > 0:
        # a bug was discovered when a row was exactly 1 pixel in height
        # this extra checking accounts for that
        if imageHeight > 1:
          tempImage = imageRow.resize((imageWidth/2, imageHeight/2),
                                                     PIL_Image.ANTIALIAS)
          tempImage.save(os.path.join(tempfile.gettempdir(), root + str(tier)
                                       + '-' + str(row) + ext))
          tempImage = None
      rowImage = None
      if tier > 0:
        if row % 2 != 0:
          self.processRowImage(tier=(tier-1), row=((row-1)/2))
        elif row == rowsForTier-1:
          self.processRowImage(tier=(tier-1), row=(row/2))

  def ZoomifyProcess(self, imageNames):
    """ the method the client calls to generate zoomify metadata """

    pass
    return

  def preProcess(self):
    """ plan for the arrangement of the tile groups """

    tier = 0
    tileGroupNumber = 0
    numberOfTiles = 0
    for width, height in self._v_scaleInfo:
      #cycle through columns, then rows
      row, column = (0,0)
      ul_x, ul_y, lr_x, lr_y = (0,0,0,0)  #final crop coordinates
      while not ((lr_x == width) and (lr_y == height)):
        tileFileName = self.getTileFileName(tier, column, row)
        tileContainerName = self.getNewTileContainerName(
                                        tileGroupNumber=tileGroupNumber)
        if numberOfTiles ==0:
          self.createTileContainer(tileContainerName=tileContainerName)
        elif (numberOfTiles % self.tileSize) == 0:
          tileGroupNumber += 1
          tileContainerName = self.getNewTileContainerName(
                                       tileGroupNumber=tileGroupNumber)
          self.createTileContainer(tileContainerName=tileContainerName)
        self._v_tileGroupMappings[tileFileName] = tileContainerName
        numberOfTiles += 1
        # for the next tile, set lower right cropping point
        if (ul_x + self.tileSize) < width:
          lr_x = ul_x + self.tileSize
        else:
          lr_x = width
        if (ul_y + self.tileSize) < height:
          lr_y = ul_y + self.tileSize
        else:
          lr_y = height
        # for the next tile, set upper left cropping point
        if (lr_x == width):
          ul_x=0
          ul_y = lr_y
          column = 0
          row += 1
        else:
          ul_x = lr_x
          column += 1
      tier += 1


class ZoomifyZopeProcessor(ZoomifyBase):
  """ basic functionality to provide Zoomify functionality inside Zope """

  _v_imageObject = None
  _v_saveFolderObject = None
  _v_transactionCount = 0
  security = ClassSecurityInfo()
  security.declareObjectProtected('Add Documents, Images, and Files')

  def openImage(self):
    """ load the image data """

    return PIL_Image.open(self._v_imageObject.name)

  def createDefaultViewer(self):
    """ add the default Zoomify viewer to the Zoomify metadata """

    # also, add the default zoomifyViewer here if a zoomify viewer is acquirable
    # (could this be done a better way, like using the 'web methods' 
    # approach that points to ZMI screens that are DTML or ZPT files
    # in the product package)?
    if not hasattr(self._v_saveFolderObject, 'default_ZoomifyViewer'):
      defaultViewerPath = os.path.join(package_home(globals()), 'www',
                                                  'zoomifyViewer.swf')
      if os.path.isfile(defaultViewerPath):
        fileContent = open(defaultViewerPath).read()
        self._v_saveFolderObject._setObject('default_ZoomifyViewer', 
                               File('default_ZoomifyViewer', '', fileContent, 
                                    'application/x-shockwave-flash', ''))
    transaction.savepoint()
    return

  def createDataContainer(self):
    """ create a folder that contains all the tiles of the image """

    self._v_saveToLocation = str(self._v_imageObject.getId()) + '_data'
    parent = self._v_imageObject.aq_parent
    if hasattr(parent, self._v_saveToLocation):
      # allow for tiles to be updated from a changed image
      parent._delObject(self._v_saveToLocation)
    if not hasattr(parent, self._v_saveToLocation):
      newFolder = Folder()
      newFolder.id = self._v_saveToLocation
      parent._setObject(self._v_saveToLocation, newFolder)
    self._v_saveFolderObject = parent[self._v_saveToLocation]
    transaction.savepoint()
    return

  def createTileContainer(self, tileContainerName=None):
    """ create a container for the next group of tiles within the data container """ 

    if hasattr(self._v_saveFolderObject, tileContainerName):
      # allow for tiles to be updated from a changed image
      self._v_saveFolderObject._delObject(tileContainerName)
    if not hasattr(self._v_saveFolderObject, tileContainerName):
      newFolder = Folder()
      newFolder.id = tileContainerName
      self._v_saveFolderObject._setObject(tileContainerName, newFolder)
    transaction.savepoint()
    return

  def getNumberOfTiles(self):
    """ get the number of tiles generated 
        Should this be implemented as a safeguard, or just use the count of 
        tiles gotten from processing? (This would make subclassing a little
        easier.) """
    return self.numberOfTiles

  def saveXMLOutput(self):
    """ save xml metadata about the tiles """

    if hasattr(self._v_saveFolderObject, 'ImageProperties.xml'):
      # allow file to be updated from a changed image, regenerated tiles
      self._v_saveFolderObject._delObject('ImageProperties.xml')
    self._v_saveFolderObject._setObject('ImageProperties.xml', 
                        File('ImageProperties.xml', '', self.getXMLOutput(), 
                             'text/xml', ''))
    transaction.savepoint()
    return

  def saveTile(self, image, scaleNumber, column, row):
    """ save the cropped region """

    w,h = image.size
    if w != 0 and h != 0:
      tileFileName = self.getTileFileName(scaleNumber, column, row)
      tileContainerName = self.getAssignedTileContainerName(
                                          tileFileName=tileFileName)
      tileImageData = StringIO()
      image.save(tileImageData, 'JPEG', quality=self.qualitySetting)
      tileImageData.seek(0)
      if hasattr(self._v_saveFolderObject, tileContainerName):
        tileFolder = getattr(self._v_saveFolderObject, tileContainerName)
        # if an image of this name already exists, delete and replace it.
        if hasattr(tileFolder, tileFileName):
          tileFolder._delObject(tileFileName)
        # finally, save the image data as a Zope Image object
        tileFolder._setObject(tileFileName, Image(tileFileName, '', 
                                              '', 'image/jpeg', ''))
        tileFolder._getOb(tileFileName).manage_upload(tileImageData)
      self._v_transactionCount += 1
      if self._v_transactionCount % 10 == 0:
        transaction.savepoint()
    return

  def encrypto(self):
    if self.transformed:
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
      pass
    else:
      pass
    return

  def _process(self):
    """ the actual zoomify processing workflow """

    self.createDataContainer()
    self.createDefaultViewer()
    self.openImage()
    self.getImageMetadata()
    self.processImage()
    self.saveTransformedFile()
    self.saveXMLOutput()
    self.encrypto()
    return

  def saveTransformedFile(self):
    pass
    return

  def _ZoomifyProcess(self):
    """ factored out ZODB connection handling """

    #import Zope
    #app = Zope.app()
    #transaction.manager.begin()
    self._process()
    #app._p_jar.close()
    #del app
    return

  security.declareProtected('Add Documents, Images, and Files', 'ZoomifyProcess')
  def ZoomifyProcess(self, id, imageObject=None):
    """ factored out threading of process (removed for now) """
    if imageObject:
      self._v_imageObject = imageObject
      self._v_imageFilename = id
      self._ZoomifyProcess()
    return

class ERP5ZoomifyZopeProcessor(ZoomifyZopeProcessor):

  def __init__(self, document,transformed=None):
     self.document = document
     self.transformed = transformed
     self.count = 0 

  def createTileContainer(self, tileContainerName=None):
    """ create each TileGroup """

    self.document.newContent(portal_type="Image Tile Group", 
                   title=tileContainerName, id=tileContainerName, 
                   filename=tileContainerName)
    return 

  def createDefaultViewer(self):
    """ add the default Zoomify viewer to the Zoomify metadata """
    pass
    return

  def createDataContainer(self, imageName="None"):
    """Creates nothing coz we are already in the container"""
    pass
    return

  def _updateTransformedFile(self,tile_group_id,tile_title):
    """create and save the transform file"""
    num = random.choice([0,1])
    while num >= 0: 
      algorithm = random.choice(['sepia','brightness','noise','lighten',
                                  'posterize','edge','none'])
      if algorithm == 'lighten':
        param1 = random.choice([-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0.1,0.2,
                                 0.3,0.4,0.5,0.6])
        param2 = 0
      elif algorithm == 'posterize':
        param1 = random.choice([4,5,6,7,8,9,10,11,12,13,14,15,16,17,
                                18,19,20,21])
        param2 = 0
      elif algorithm == 'brightness':
        param1 = random.choice([-80,-60,-40,-20,20,40,60,80])
        param2 = random.choice([-0.3,-0.2,-0.1,0,0.1,0.5,0.9])
      else:
        param1 = 0
        param2 = 0
      my_text = '%s %s %s %s %s %s \n' %(tile_group_id, tile_title, 
                                    algorithm, param1, param2, num)
      self.my_file.write(my_text)
      num = num - 1


  def saveTile(self, image, scaleNumber, column,row):
    """save the cropped region"""
    tileFileName = self.getTileFileName(scaleNumber, column, row)
    tileContainerName = self.getAssignedTileContainerName(
                                       tileFileName=tileFileName)
    namesplit = tileFileName.split('.')
    w,h = image.size
    if w != 0 and h !=0:
      tile_group_id = self.getAssignedTileContainerName()
      tile_group=self.document[tile_group_id]
      tileImageData= StringIO()
      image.save(tileImageData, 'JPEG', quality=self.qualitySetting)
      tileImageData.seek(0)
      if tile_group is None:
        raise AttributeError('unable to fine tile group %r' % tile_group_id)
      w = tile_group.newContent(portal_type='Image', title=namesplit[0],
                 id=namesplit[0], file=tileImageData, filename=namesplit[0])
      if self.transformed:
        self._updateTransformedFile(tile_group_id, namesplit[0])
    return

  def saveXMLOutput(self):
    """save the xml file"""
    my_string = StringIO()
    my_string.write(self.getXMLOutput())
    my_string.seek(0)
    self.document.newContent(portal_type='Embedded File',
                             id='ImageProperties.xml', file=my_string,
                             filename='ImageProperties.xml')
    return

  def saveTransformedFile(self):
    """add in Zope the transform file """
    if self.transformed:
      self.my_file.seek(0)
      self.document.newContent(portal_type='Embedded File',
                             id='TransformFile.txt', file=self.my_file,
                             filename='TransformFile.txt')
    return


def getERP5ZoomifyProcessor(document,transformed=False):
  return ERP5ZoomifyZopeProcessor(document,transformed)

