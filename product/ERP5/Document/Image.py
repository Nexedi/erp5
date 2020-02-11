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
import struct
import subprocess
from cStringIO import StringIO

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Utils import fill_args_from_request
from Products.ERP5.Document.File import File
from Products.ERP5.Document.Document import Document, ConversionError,\
                     VALID_TEXT_FORMAT_LIST, VALID_TRANSPARENT_IMAGE_FORMAT_LIST,\
                     DEFAULT_DISPLAY_ID_LIST, _MARKER
from os.path import splitext
from OFS.Image import Image as OFSImage
from OFS.Image import getImageInfo
from zLOG import LOG, WARNING

from Products.ERP5Type.ImageUtil import transformUrlToDataURI

# import mixin
from Products.ERP5.mixin.text_convertable import TextConvertableMixin

def getDefaultImageQuality(portal, format=None):
  preference_tool = portal.portal_preferences
  return preference_tool.getPreferredImageQuality()

class Image(TextConvertableMixin, File, OFSImage):
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
    self._setContentType(content_type or 'application/unknown')

  def _upgradeImage(self):
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
    size = len(self.data)
    if getattr(aq_base(self), 'size', None) != size:
      self.size = size

  security.declareProtected(Permissions.AccessContentsInformation, 'getWidth')
  def getWidth(self):
    """
      Tries to get the width from the image data.
    """
    self._upgradeImage()
    if self.hasData() and not self.width:
      self._update_image_info()
    return self.width

  security.declareProtected(Permissions.AccessContentsInformation, 'getHeight')
  def getHeight(self):
    """
      Tries to get the height from the image data.
    """
    self._upgradeImage()
    if self.hasData() and not self.height:
      self._update_image_info()
    return self.height

  security.declareProtected(Permissions.AccessContentsInformation, 'getContentType')
  def getContentType(self, default=_MARKER):
    """Original photo content_type."""
    self._upgradeImage()
    if self.hasData() and not self.hasContentType():
      self._update_image_info()
    if default is _MARKER:
      return self._baseGetContentType()
    else:
      return self._baseGetContentType(default)

  security.declareProtected(Permissions.AccessContentsInformation, 'displayIds')
  def displayIds(self, exclude=('thumbnail',)):
    """Return list of display Ids."""
    id_list = list(DEFAULT_DISPLAY_ID_LIST)
    # Exclude specified displays
    if exclude:
      for id_ in exclude:
        if id_ in id_list:
          id_list.remove(id_)
    # Sort by desired photo surface area
    def getSurfaceArea(img):
      x, y = self.getSizeFromImageDisplay(img)
      return x * y
    id_list.sort(key=getSurfaceArea)
    return id_list

  security.declareProtected(Permissions.AccessContentsInformation, 'displayLinks')
  def displayLinks(self, exclude=('thumbnail',)):
    """Return list of HTML <a> tags for displays."""
    links = []
    for display in self.displayIds(exclude):
      links.append('<a href="%s?display=%s">%s</a>' % (self.REQUEST['URL'], display, display))
    return links

  security.declareProtected(Permissions.AccessContentsInformation, 'displayMap')
  def displayMap(self, exclude=None, format=None, quality=_MARKER,\
                                                              resolution=None):
    """Return list of displays with size info."""
    displays = []
    if quality is _MARKER:
      quality = self.getDefaultImageQuality(format)
    for id_ in self.displayIds(exclude):
      if self._isGenerated(id_, format=format, quality=quality,\
                                                        resolution=resolution):
        photo_width = self._photos[(id_,format)].width
        photo_height = self._photos[(id_,format)].height
        bytes_ = self._photos[(id_,format)]._size()
        age = self._photos[(id_,format)]._age()
      else:
        (photo_width, photo_height, bytes_, age) = (None, None, None, None)
      image_size = self.getSizeFromImageDisplay(id_)
      displays.append({'id': id_,
                        'width': image_size[0],
                        'height': image_size[1],
                        'photo_width': photo_width,
                        'photo_height': photo_height,
                        'bytes': bytes_,
                        'age': age
                        })
    return displays


  security.declarePrivate('_convertToText')
  def _convertToText(self, format):
    """
    Convert the image to text with portaltransforms
    """
    portal = self.getPortalObject()
    mime_type = portal.mimetypes_registry.lookupExtension('name.%s' % format)
    mime_type = str(mime_type)
    src_mimetype = self.getContentType()
    content = self.getData()
    portal_transforms = portal.portal_transforms
    result = portal_transforms.convertToData(mime_type, content,
                                             object=self, context=self,
                                             filename=self.getFilename(),
                                             mimetype=src_mimetype)
    if result is None:
      # portal_transforms fails to convert.
      LOG('TextDocument.convert', WARNING,
          'portal_transforms failed to convert to %s: %r' % (mime_type, self))
      result = ''
    return mime_type, result

  # Conversion API
  def _convert(self, format, **kw):
    """
    Implementation of conversion for Image files
    """
    if format == 'svg' and self.getContentType()=='image/svg+xml':
      # SVG format is a textual data which can be returned as it is
      # so client (browser) can draw an image out of it
      return self.getContentType(), self.getData()

    if format in VALID_TEXT_FORMAT_LIST:
      try:
        return self.getConversion(format=format)
      except KeyError:
        mime_type, data = self._convertToText(format)
        data = aq_base(data)
        self.setConversion(data, mime=mime_type, format=format)
        return mime_type, data
    if not (format or kw):
      # User asked for original content
      return self.getContentType(), self.getData()
    image_size = self.getSizeFromImageDisplay(kw.get('display'))
    # store all keys usefull to convert or resize an image
    # 'display' parameter can be discarded
    quality = kw.get('quality', _MARKER)
    if quality is _MARKER:
      quality = self.getDefaultImageQuality(format)
    kw['format'] = format
    kw['quality'] = quality
    try:
      mime, image_data = self.getConversion(**kw)
    except KeyError:
      # we need to convert string representation (i.e. display=small) to a
      # pixel (number of it = 128x128)
      kw['image_size'] = image_size
      display = kw.pop('display', None)
      crop = kw.pop('crop', None)
      mime, image = self._makeDisplayPhoto(crop=crop, **kw)
      image_data = image.data
      # as image will always be requested through a display not by passing exact
      # pixels we need to restore this way in cache
      if display is not None:
        # only set if we have a real value
        kw['display'] = display
      if crop:
        kw['crop'] = crop
      image_size = kw.pop('image_size', None)
      self.setConversion(image_data, mime, **kw)
    return mime, image_data

  # Display
  security.declareProtected(Permissions.View, 'index_html')
  @fill_args_from_request('display', 'quality', 'resolution', 'frame', 'crop')
  def index_html(self, REQUEST, *args, **kw):
    """Return the image data."""
    self._upgradeImage()
    return Document.index_html(self, REQUEST, *args, **kw)

  #
  # Photo processing
  #

  def _resize(self, quality, width, height, format, resolution, frame, crop=False):
    """Resize and resample photo."""
    icc_profile = os.path.join(os.path.dirname(__file__),
                               '..', 'misc', 'sRGB.icc')
    parameter_list = ['convert', '-colorspace', 'sRGB', '-depth', '8',
                      '-profile', icc_profile]
    if crop :
      parameter_list += '-thumbnail', '%sx%s^' % (width, height),\
                        '-gravity', 'center',\
                        '-extent','%sx%s' % (width, height)
    else:
      parameter_list += '-geometry', '%sx%s' % (width, height)
    parameter_list += '-quality', str(quality)
    if format not in VALID_TRANSPARENT_IMAGE_FORMAT_LIST:
      # ImageMagick way to remove transparent that works with multiple
      # images. http://www.imagemagick.org/Usage/masking/#remove
      parameter_list += '-bordercolor', 'white', '-border', '0'
    if resolution:
      parameter_list += '-density', '%sx%s' % (resolution, resolution)
    if frame is not None:
      parameter_list.append('-[%s]' % frame)
    else:
      parameter_list.append('-')

    if format:
      # Is there a way to make 'convert' fail if the format is unknown,
      # instead of treating this whole parameter as an output file path?
      # As a workaround, we run 'convert' in a non-writeable directory.
      if '/' in format or os.access('/', os.W_OK):
        raise ConversionError
      parameter_list.append('%s:-' % format)
    else:
      parameter_list.append('-')

    data = str(self.getData())
    if self.getContentType() == "image/svg+xml":
      data = transformUrlToDataURI(data)

    env = os.environ.copy()
    env.update({'LC_NUMERIC':'C'})
    process = subprocess.Popen(parameter_list,
                               env=env,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd='/',
                               close_fds=True)
    try:
      # XXX: The only portable way is to pass what stdin.write can accept,
      #      which is a string for PIPE.
      image, err = process.communicate(data)
    finally:
      del process
    if image:
      return StringIO(image)
    raise ConversionError('Image conversion failed (%s).' % err)

  def _getDisplayData(self, format, quality, resolution, frame, image_size, crop):
    """Return raw photo data for given display."""
    if crop:
      width, height = image_size
    else:
      width, height = self._getAspectRatioSize(*image_size)
    if ((width, height) == image_size or (width, height) == (0, 0))\
       and quality == self.getDefaultImageQuality(format) and resolution is None and frame is None\
       and not format:
      # No resizing, no conversion, return raw image
      return self.getData()
    return self._resize(quality, width, height, format, resolution, frame, crop)

  def _makeDisplayPhoto(self, format=None, quality=_MARKER,
                                 resolution=None, frame=None, image_size=None,
                                 crop=False):
    """Create given display."""
    if quality is _MARKER:
      quality = self.getDefaultImageQuality(format)
    width, height = image_size
    base, ext = splitext(self.id)
    id_ = '%s_%s_%s.%s'% (base, width, height, ext,)
    image = OFSImage(id_, self.getTitle(),
                     self._getDisplayData(format, quality, resolution,
                                                            frame, image_size,
                                                            crop))
    return image.content_type, aq_base(image)

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

  security.declareProtected(Permissions.AccessContentsInformation, 'getSizeFromImageDisplay')
  def getSizeFromImageDisplay(self, image_display):
    """Return the size for this image display,
       or dimension of this image.
    """
    if image_display in DEFAULT_DISPLAY_ID_LIST:
      preference_tool = self.getPortalObject().portal_preferences
      height_preference = 'preferred_%s_image_height' % (image_display,)
      width_preference = 'preferred_%s_image_width' % (image_display,)
      height = preference_tool.getPreference(height_preference)
      width = preference_tool.getPreference(width_preference)
      return (width, height)
    return self.getWidth(), self.getHeight()

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

  security.declareProtected(Permissions.AccessContentsInformation, 'getDefaultImageQuality')
  def getDefaultImageQuality(self, format=None):
    """
    Get default image quality for a format.
    """
    return getDefaultImageQuality(self.getPortalObject(), format)
