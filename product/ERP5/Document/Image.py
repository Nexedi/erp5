# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# Based on Photo by Ron Bickers
# Copyright (c) 2001 Logic Etc, Inc.  All rights reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import os
import string
import struct
import sys
import time
import subprocess
from cStringIO import StringIO

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base

from DocumentTemplate.DT_Util import html_quote
from Products.CMFCore.utils import _setCacheHeaders, _ViewEmulator
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5.Document.File import File
from Products.ERP5.Document.Document import ConversionError

from OFS.Image import Image as OFSImage
from OFS.Image import getImageInfo
from OFS.content_types import guess_content_type

from zLOG import LOG, WARNING

from Products.CMFCore.utils import getToolByName

default_displays_id_list = ('nano', 'micro', 'thumbnail',
                            'xsmall', 'small', 'medium',
                            'large', 'large', 'xlarge',)

default_formats = ['jpg', 'jpeg', 'png', 'gif', 'pnm', 'ppm']

class Image(File, OFSImage):
  """
    An Image is a File which contains image data. It supports
    various conversions of format, size, resolution through
    imagemagick. imagemagick was preferred due to its ability
    to support PDF files (incl. Adobe Illustrator) which make
    it very useful in the context of a graphic design shop.

    Image inherits from XMLObject and can be synchronized
    accross multiple sites.

    Subcontent: Image can only contain role information.

    TODO:
    * extend Image to support more image file formats,
      including Xara Xtreme (http://www.xaraxtreme.org/)
    * include upgrade methods so that previous images
      in ERP5 get upgraded automatically to new class
  """
  # CMF Type Definition
  meta_type = 'ERP5 Image'
  portal_type = 'Image'
  isPortalContent = 1
  isRADContent = 1

  # Default attribute values
  width = 0
  height = 0

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Version
                    , PropertySheet.Reference
                    , PropertySheet.Document
                    , PropertySheet.Data
                    , PropertySheet.ExternalDocument
                    , PropertySheet.Url
                    , PropertySheet.Periodicity
                    )

  #
  # Original photo attributes
  #

  def _update_image_info(self):
    """
      This method tries to determine the content type of an image and
      its geometry. It uses currently OFS.Image for this purpose.
      However, this method is known to be too simplistic.

      TODO:
      - use image magick or PIL
    """
    self.size = len(self.data)
    content_type, width, height = getImageInfo(self.data)
    if not content_type:
      if self.size >= 30 and self.data[:2] == 'BM':
        header = struct.unpack('<III', self.data[14:26])
        if header[0] >= 12:
          content_type = 'image/x-bmp'
          width, height = header[1:]
    self.height = height
    self.width = width
    self._setContentType(content_type)

  def _upradeImage(self):
    """
      This method upgrades internal data structures is required
    """
    # Quick hack to maintain just enough compatibility for existing sites
    # Convert to new BTreeFolder2 based class
    if getattr(aq_base(self), '_count', None) is None:
      self._initBTrees()

    # Make sure old Image objects can still be accessed
    if not hasattr(aq_base(self), 'data') and hasattr(self, '_original'):
      self.data = self._original.data
      self.height = self._original.height
      self.width = self._original.width

    # Make sure old Image objects can still be accessed
    if not hasattr(aq_base(self), 'data') and hasattr(aq_base(self), '_data'):
      self.data = self._data

    # Make sure size is defined
    if (not hasattr(aq_base(self), 'size') or not self.size) and \
                      hasattr(aq_base(self), 'data'):
      self.size = len(self.data)

  security.declareProtected(Permissions.AccessContentsInformation, 'getWidth')
  def getWidth(self):
    """
      Tries to get the width from the image data. 
    """
    self._upradeImage()
    if self.get_size() and not self.width: self._update_image_info()
    return self.width

  security.declareProtected(Permissions.AccessContentsInformation, 'getHeight')
  def getHeight(self):
    """
      Tries to get the height from the image data.
    """
    self._upradeImage()
    if self.get_size() and not self.height: self._update_image_info()
    return self.height

  security.declareProtected(Permissions.AccessContentsInformation, 'getContentType')
  def getContentType(self, format=''):
    """Original photo content_type."""
    self._upradeImage()
    if self.get_size() and not self._baseGetContentType(): self._update_image_info()
    if format == '':
      return self._baseGetContentType()
    else:
      return guess_content_type('myfile.' + format)[0]

  #
  # Photo display methods
  #

  security.declareProtected('View', 'tag')
  def tag(self, display=None, height=None, width=None, cookie=0,
                alt=None, css_class=None, format='', quality=75,
                resolution=None, frame=None, **kw):
    """Return HTML img tag."""
    self._upradeImage()

    # Get cookie if display is not specified.
    if display is None:
      display = self.REQUEST.cookies.get('display', None)

    # display may be set from a cookie.
    image_size = self.getSizeFromImageDisplay(display)
    if (display is not None or resolution is not None or quality!=75 or format != ''\
                            or frame is not None) and image_size:
      kw = dict(display=display, format=format, quality=quality,
                resolution=resolution, frame=frame, image_size=image_size)
      try:
        mime, image = self.getConversion(**kw)
      except KeyError:
        # Generate photo on-the-fly
        mime, image = self._makeDisplayPhoto(**kw)
        self.setConversion(image, mime, **kw)
      width, height = (image.width, image.height)
      # Set cookie for chosen size
      if cookie:
        self.REQUEST.RESPONSE.setCookie('display', display, path="/")
    else:
      # TODO: Add support for on-the-fly resize?
      height = self.getHeight()
      width = self.getWidth()

    if display:
      result = '<img src="%s?display=%s"' % (self.absolute_url(), display)
    else:
      result = '<img src="%s"' % (self.absolute_url())

    if alt is None:
      alt = getattr(self, 'title', '')
    if alt == '':
      alt = self.getId()
    result = '%s alt="%s"' % (result, html_quote(alt))

    if height:
      result = '%s height="%s"' % (result, height)

    if width:
      result = '%s width="%s"' % (result, width)

    if not 'border' in map(string.lower, kw.keys()):
      result = '%s border="0"' % (result)

    if css_class is not None:
      result = '%s class="%s"' % (result, css_class)

    for key in kw.keys():
      value = kw.get(key)
      result = '%s %s="%s"' % (result, key, value)

    result = '%s />' % (result)

    return result

  def __str__(self):
    return self.tag()

  security.declareProtected('Access contents information', 'displayIds')
  def displayIds(self, exclude=('thumbnail',)):
    """Return list of display Ids."""
    id_list = list(default_displays_id_list)
    # Exclude specified displays
    if exclude:
      for id in exclude:
        if id in id_list:
          id_list.remove(id)
    # Sort by desired photo surface area
    def getSurfaceArea(img):
      x, y = self.getSizeFromImageDisplay(img)
      return x * y
    id_list.sort(key=getSurfaceArea)
    return id_list

  security.declareProtected('Access contents information', 'displayLinks')
  def displayLinks(self, exclude=('thumbnail',)):
    """Return list of HTML <a> tags for displays."""
    links = []
    for display in self.displayIds(exclude):
        links.append('<a href="%s?display=%s">%s</a>' % (self.REQUEST['URL'], display, display))
    return links

  security.declareProtected('Access contents information', 'displayMap')
  def displayMap(self, exclude=None, format='', quality=75, resolution=None):
    """Return list of displays with size info."""
    displays = []
    for id in self.displayIds(exclude):
      if self._isGenerated(id, format=format, quality=quality, resolution=resolution):
        photo_width = self._photos[(id,format)].width
        photo_height = self._photos[(id,format)].height
        bytes = self._photos[(id,format)]._size()
        age = self._photos[(id,format)]._age()
      else:
        (photo_width, photo_height, bytes, age) = (None, None, None, None)
      displays.append({'id': id,
                        'width': self.getSizeFromImageDisplay(id)[0],
                        'height': self.getSizeFromImageDisplay(id)[1],
                        'photo_width': photo_width,
                        'photo_height': photo_height,
                        'bytes': bytes,
                        'age': age
                        })
    return displays


  security.declarePrivate('_convertToText')
  def _convertToText(self, format):
    """
    Convert the image to text with portaltransforms
    """
    mime_type = getToolByName(self, 'mimetypes_registry').\
                                lookupExtension('name.%s' % format)
    mime_type = str(mime_type)
    src_mimetype = self.getContentType()
    content = '%s' % self.getData()
    portal_transforms = getToolByName(self, 'portal_transforms')
    result = portal_transforms.convertToData(mime_type, content,
                                             object=self, context=self,
                                             filename=self.getTitleOrId(),
                                             mimetype=src_mimetype)
    if result is None:
      # portal_transforms fails to convert.
      LOG('TextDocument.convert', WARNING,
          'portal_transforms failed to convert to %s: %r' % (mime_type, self))
      result = ''
    return mime_type, result

  # Conversion API
  security.declareProtected(Permissions.ModifyPortalContent, 'convert')
  def convert(self, format, display=None, quality=75, resolution=None, frame=None, **kw):
    """
    Implementation of conversion for Image files
    """
    if format in ('text', 'txt', 'html', 'base_html', 'stripped-html'):
      try:
        return self.getConversion(format=format)
      except KeyError:
        mime_type, data = self._convertToText(format)
        data = aq_base(data)
        self.setConversion(data, mime=mime_type, format=format)
        return mime_type, data
    image_size = self.getSizeFromImageDisplay(display)
    if (display is not None or resolution is not None or quality != 75 or format != ''\
                            or frame is not None) and image_size:
      kw = dict(display=display, format=format, quality=quality,
                resolution=resolution, frame=frame, image_size=image_size)
      try:
        return self.getConversion(**kw)
      except KeyError:
        mime, image = self._makeDisplayPhoto(**kw)
        self.setConversion(image.data, mime, **kw)
        return mime, image.data
    return self.getContentType(), self.getData()

  security.declareProtected(Permissions.View, 'getSearchableText')
  def getSearchableText(self, md=None):
    """
      Converts the content of the document to a textual representation.
    """
    mime, data = self.convert(format='txt')
    return str(data)

  # Compatibility with CMF Catalog
  SearchableText = getSearchableText

  # Display
  security.declareProtected('View', 'index_html')
  def index_html(self, REQUEST, RESPONSE, display=None, format='', quality=75,
                       resolution=None, frame=None):
    """Return the image data."""
    self._upradeImage()

    # display may be set from a cookie (?)
    image_size = self.getSizeFromImageDisplay(display)
    kw = dict(display=display, format=format, quality=quality,
              resolution=resolution, frame=frame, image_size=image_size)
    _setCacheHeaders(_ViewEmulator().__of__(self), kw)

    if (display is not None or resolution is not None or quality != 75 or format != ''\
                            or frame is not None) and image_size:
      try:
        mime, image = self.getConversion(**kw)
      except KeyError:
        # Generate photo on-the-fly
        mime, image = self._makeDisplayPhoto(**kw)
        self.setConversion(image, mime, **kw)
      RESPONSE.setHeader('Content-Type', mime)
      return image.index_html(REQUEST, RESPONSE)

    # Return original image
    return OFSImage.index_html(self, REQUEST, RESPONSE)


  #
  # Photo processing
  #

  def _resize(self, display, width, height, quality=75, format='',
                    resolution=None, frame=None):
    """Resize and resample photo."""
    newimg = StringIO()

    parameter_list = ['convert']
    parameter_list.extend(['-colorspace', 'RGB'])
    if resolution:
      parameter_list.extend(['-density', '%sx%s' % (resolution, resolution)])
    parameter_list.extend(['-quality', str(quality)])
    parameter_list.extend(['-geometry', '%sx%s' % (width, height)])
    if frame is not None:
      parameter_list.append('-[%s]' % frame)
    else:
      parameter_list.append('-')

    if format:
      parameter_list.append('%s:-' % format)
    else:
      parameter_list.append('-')

    process = subprocess.Popen(parameter_list,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               close_fds=True)
    imgin, imgout, err = process.stdin, process.stdout, process.stderr

    def writeData(stream, data):
      if isinstance(data, str):
        stream.write(str(self.getData()))
      else:
        # Use PData structure to prevent
        # consuming too much memory
        while data is not None:
          stream.write(data.data)
          data = data.next

    writeData(imgin, self.getData())
    imgin.close()
    newimg.write(imgout.read())
    imgout.close()
    if not newimg.tell():
      raise ConversionError('Image conversion failed (%s).' % err.read())
    newimg.seek(0)
    return newimg

  def _getDisplayData(self, display, format='', quality=75, resolution=None, frame=None,
                      image_size=None):
    """Return raw photo data for given display."""
    if display is None:
      (width, height) = (self.getWidth(), self.getHeight())
    elif image_size is None:
      (width, height) = self.getSizeFromImageDisplay(display)
    else:
      (width, height) = image_size
    if width == 0 and height == 0:
      width = self.getWidth()
      height = self.getHeight()
    (width, height) = self._getAspectRatioSize(width, height)
    if (width, height) == (0, 0):return self.getData()
    return self._resize(display, width, height, quality, format=format,
                        resolution=resolution, frame=frame)

  def _getDisplayPhoto(self, display, format='', quality=75, resolution=None, frame=None,
                       image_size=None):
    """Return photo object for given display."""
    try:
        base, ext = string.split(self.id, '.')
        id = base + '_' + display + '.' + ext
    except ValueError:
        id = self.id +'_'+ display
    image = OFSImage(id, self.getTitle(), self._getDisplayData(display, format=format,
                         quality=quality, resolution=resolution, frame=frame,
                         image_size=image_size))
    return image

  def _makeDisplayPhoto(self, display, format='', quality=75, resolution=None, frame=None,
                        image_size=None):
    """Create given display."""
    image = self._getDisplayPhoto(display, format=format, quality=quality,
                                           resolution=resolution, frame=frame,
                                           image_size=image_size)
    return (image.content_type, aq_base(image))

  def _getAspectRatioSize(self, width, height):
    """Return proportional dimensions within desired size."""
    img_width, img_height = (self.getWidth(), self.getHeight())
    if img_width == 0:
      return (0, 0)

    #XXX This is a temporary dirty fix!!!
    width = int(width)
    height = int(height)
    img_width = int(img_width)
    img_height = int(img_height)

    if height > img_height * width / img_width:
      height = img_height * width / img_width
    else:
      width =  img_width * height / img_height
    return (width, height)

  def _validImage(self):
    """At least see if it *might* be valid."""
    return self.getWidth() and self.getHeight() and self.getData() and self.getContentType()

  security.declareProtected('View', 'getSizeFromImageDisplay')
  def getSizeFromImageDisplay(self, image_display):
    """
    Return the size for this image display, or None if this image display name
    is not known. If the preference is not set, (0, 0) is returned.
    """
    if image_display in default_displays_id_list:
      preference_tool = self.getPortalObject().portal_preferences
      height_preference = 'preferred_%s_image_height' % (image_display,)
      width_preferece = 'preferred_%s_image_width' % (image_display,)
      height = preference_tool.getPreference(height_preference, 0)
      width = preference_tool.getPreference(width_preferece, 0)
      return (height, width)
    return None

  def _setFile(self, *args, **kw):
    """set the file content and reset image information.
    """
    File._setFile(self, *args, **kw)
    self._update_image_info()

  def PUT(self, REQUEST, RESPONSE):
    """set the file content by HTTP/FTP and reset image information.
    """
    File.PUT(self, REQUEST, RESPONSE)
    self._update_image_info()

  #
  # FTP/WebDAV support
  #

      #if hasattr(self, '_original'):
          ## Updating existing Photo
          #self._original.manage_upload(file, self.content_type())
          #if self._validImage():
              #self._makeDisplayPhotos()

  # Maybe needed
  #def manage_afterClone(self, item):

  # Maybe needed
  #def manage_afterAdd(self, item, container):
