# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Products.Formulator import Widget, Validator
from Products.Formulator.Field import ZMIField
from Products.Formulator.DummyField import fields
from OFS.Image import Image as OFSImage
from lxml.etree import Element
from lxml import etree
import re

DRAW_URI = 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0'
TEXT_URI = 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
XLINK_URI = 'http://www.w3.org/1999/xlink'
SVG_URI = 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0'


NSMAP = {
          'draw': DRAW_URI,
          'text': TEXT_URI,
          'xlink': XLINK_URI,
          'svg': SVG_URI
        }

class ImageFieldWidget(Widget.TextWidget):
    """ImageField widget.

    Renders an HTML <img> element where the src is the 'default' field value.
    The 'description' field value is used as 'alt' attribute.
    The image size is calculated using 'image_display'.
    """
    property_names = Widget.TextWidget.property_names + \
      ['image_display', 'image_format','image_quality', 'image_pre_converted_only']

    image_display = fields.StringField('image_display',
                               title='Image Display',
                               description=(
        "The display size. See erp5.component.document.Image.default_displays_id_list "
        "for possible values. This is only used with ERP5 Images."),
                               default='thumbnail',
                               required=0)

    image_format = fields.StringField('image_format',
                               title='Image Format',
                               description=(
        "The format in which the image should be converted to. "
        "This is only used with ERP5 Images."),
                               default='',
                               required=0)

    image_quality = fields.IntegerField('image_quality',
                               title='Image Quality',
                               description=(
        "The quality used when converting the image. "
        "This is only used with ERP5 Images."),
                               default=75,
                               required=0)

    image_pre_converted_only = fields.CheckBoxField('image_pre_converted_only',
                               title='Image Pre Converted Only',
                               description=(
        "Return image only if it is already pre converted in cache. "
        "This is only used with ERP5 Images."),
                               default=False,
                               required=0)

    def render(self, field, key, value, REQUEST, render_prefix=None):
        """Render image field as a link to the image
        """
        return self.render_view(field, value, REQUEST=REQUEST)

    def render_view(self, field, value, REQUEST=None, render_prefix=None):
        """Render image field as a link to the image
        """
        # Url is already defined in value
        if value is None:
          return ''
        image = value
        alt = field.get_value('description') or \
              field.get_value('title')
        css_class = field.get_value('css_class')
        extra = field.get_value('extra')
        options = {}
        options['display'] = field.get_value('image_display')
        options['format'] = field.get_value('image_format')
        options['quality'] = field.get_value('image_quality')
        pre_converted_only = field.get_value('image_pre_converted_only')
        if pre_converted_only:
          # only add if it's True as conversion machine assume that if it is missing
          # then conversion should happen "on the fly"
          options['pre_converted_only'] = pre_converted_only
        parameters = '&'.join(['%s=%s' % (k, v) for k, v in options.items() \
                               if v])
        if parameters:
            image = '%s?%s' % (image, parameters)
        return Widget.render_element(
            "img",
            alt=alt,
            src=image,
            css_class=css_class,
            extra=extra,
        )

    def render_odg_view(self, field, value, as_string, ooo_builder, REQUEST,
                        render_prefix, attr_dict, local_name):
      """
        return an image xml node rendered in odg format
        if as_string is True (default) the returned value is a string (xml
        reprensation of the node), if it's False, the value returned is the node
        object.
        attr_dict can be used for additional parameters (like style).
      """
      if attr_dict is None:
        attr_dict = {}
      draw_frame_node = None
      if value in ('', None):
        return None
      path = '/'.join(REQUEST.physicalPathFromURL(value))
      path = path.encode()
      image_object = field.getPortalObject().restrictedTraverse(path)
      display = field.get_value('image_display')
      format = field.get_value('image_format')
      quality = field.get_value('image_quality')
      image_parameter_dict = {'format': format}
      if display:
        image_parameter_dict['display'] = display
      if quality:
        image_parameter_dict['quality'] = quality
      # convert the image using fields parameters. In this way, if an image
      # is displayed in the form as a thumbnail, it will be added in the odg
      # document as thumbnail size/quality
      content_type, image_data = image_object.convert(**image_parameter_dict)
      image = OFSImage('', '', image_data)
      width = image.width
      height = image.height
      if image_data is None:
        return draw_frame_node

      # Big images are cut into smaller chunks, so it's required to cast to
      # str. See OFS/Image -> _read_data method for more information
      image_data = str(image_data)

      format = content_type.split('/')[-1]
      # add the image to the odg document
      picture_path = ooo_builder.addImage(image=image_data,
                                          format=format,
                                          content_type=content_type)

      # create the xml nodes related to the image
      draw_frame_tag_name = '{%s}%s' % (DRAW_URI, 'frame')
      draw_frame_node = Element(draw_frame_tag_name, nsmap=NSMAP)
      draw_frame_node.attrib.update(attr_dict.get(draw_frame_tag_name,
        {}).pop(0))

      # set the size of the image
      if display is not None:
        # if the image width and height are not on defined, use current
        # width and height
        if (image_object.getWidth(), image_object.getHeight()) not in \
          ((-1, -1), (0,0)):
          width, height = image_object._getAspectRatioSize(width, height)
          if draw_frame_node.attrib.get('{%s}width' % SVG_URI) and \
            draw_frame_node.attrib.get('{%s}height' % SVG_URI):
            # if a size already exist from attr_dict, try to resize the image to
            # fit this size (image should not be biger than size from attr_dict)
            # devide the value by 20 to have cm instead of px
            width, height = self._getPictureSize(width/20., height/20.,
                target_width=draw_frame_node.attrib.get('{%s}width' % SVG_URI, ''),
                target_height=draw_frame_node.attrib.get('{%s}height' % SVG_URI, ''))

          draw_frame_node.set('{%s}width' % SVG_URI, str(width))
          draw_frame_node.set('{%s}height' % SVG_URI, str(height))

      image_tag_name = '{%s}%s' % (DRAW_URI, 'image')
      image_node = Element(image_tag_name, nsmap=NSMAP)
      image_node.attrib.update(attr_dict.get(image_tag_name, []).pop())
      image_node.set('{%s}href' % XLINK_URI, picture_path)

      draw_frame_node.append(image_node)
      if as_string:
        return etree.tostring(draw_frame_node)
      return draw_frame_node

    def _getPictureSize(self, picture_width, picture_height, target_width,
        target_height):
      # if not match causes exception
      width_tuple = re.match("(\d[\d\.]*)(.*)", target_width).groups()
      height_tuple = re.match("(\d[\d\.]*)(.*)", target_height).groups()
      unit = width_tuple[1]
      w = float(width_tuple[0])
      h = float(height_tuple[0])
      aspect_ratio = 1
      try: # try image properties
        aspect_ratio = picture_width / picture_height
      except (TypeError, ZeroDivisionError):
        try: # try Image Document API
          height = picture_height
          if height:
            aspect_ratio = picture_width / height
        except AttributeError: # fallback to Photo API
          height = float(picture_height)
          if height:
            aspect_ratio = picture_width / height
      resize_w = h * aspect_ratio
      resize_h = w / aspect_ratio
      if resize_w < w:
        w = resize_w
      elif resize_h < h:
        h = resize_h
      return (str(w) + unit, str(h) + unit)

ImageFieldWidgetInstance = ImageFieldWidget()
ImageFieldValidatorInstance = Validator.StringValidator()

class ImageField(ZMIField):
    meta_type = "ImageField"

    widget = ImageFieldWidgetInstance
    validator = ImageFieldValidatorInstance


