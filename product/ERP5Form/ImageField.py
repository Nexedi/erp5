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
from lxml.etree import Element
from Acquisition import aq_base
from lxml import etree

DRAW_URI = 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0'
TEXT_URI = 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'

NSMAP = {
          'draw': DRAW_URI,
          'text': TEXT_URI,
        }

class ImageFieldWidget(Widget.TextWidget):
    """ImageField widget.
    
    Renders an HTML <img> element where the src is the 'default' field value.
    The 'description' field value is used as 'alt' attribute.
    The image size is calculated using 'image_display'.
    """
    property_names = Widget.TextWidget.property_names + \
      ['image_display', 'image_format','image_resolution']

    image_display = fields.StringField('image_display',
                               title='Image Display',
                               description=(
        "The display size. See ERP5.Document.Image.default_displays_id_list "
        "for possible values. This is only used with ERP5 Images."),
                               default='thumbnail',
                               required=1)

    image_format = fields.StringField('image_format',
                               title='Image Format',
                               description=(
        "The format in which the image should be converted to. "
        "This is only used with ERP5 Images."),
                               default='',
                               required=0)

    image_resolution = fields.IntegerField('image_resolution',
                               title='Image Resolution',
                               description=(
        "The resolution used when converting the image. "
        "This is only used with ERP5 Images."),
                               default=75,
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
        display = field.get_value('image_display')
        format = field.get_value('image_format')
        resolution = field.get_value('image_resolution')
        return Widget.render_element(
            "img",
            alt=alt,
            src="%s?display=%s&format=%s&" % (image, display, format),
            css_class=css_class,
            extra=extra,
        )

    def _replaceImage(self, image_frame_node, ooo_builder, image_field,
        printout, REQUEST, attr_dict):
      """
      Replace the image in an odg file using an ERP5Form image field.
      return True if the image have been found, else return False
      """
      image_node = image_frame_node.getchildren()[0]
      path = '/'.join(REQUEST.physicalPathFromURL(image_field.get_value('default')))
      if path in (None, ''):
        # not possible to add image, remove the existing one
        image_frame_node = image_node.getparent()
        image_frame_node.remove(image_node)
        return False
      path = path.encode()
      image_object = image_field.getPortalObject().restrictedTraverse(path)
      image_parameter_dict = {
                    'display': image_field.get_value('image_display'),
                    'format': image_field.get_value('image_format')
                   }
      picture_type, image_data = image_object.convert(**image_parameter_dict)
      if image_data is None:
        # not possible to add image, remove the existing one
        image_frame_node = image_node.getparent()
        image_frame_node.remove(image_node)
        return False
      picture_path = printout._createOdfUniqueFileName(path=path,
          picture_type=picture_type)
      ooo_builder.addFileEntry(picture_path, media_type=picture_type, content=image_data)
      width, height = printout._getPictureSize(image_object, image_node)
      image_node.set('{%s}href' % image_node.nsmap['xlink'], picture_path)
      image_frame_node.set('{%s}width' % image_node.nsmap['svg'], width)
      image_frame_node.set('{%s}height' % image_node.nsmap['svg'], height)
      attr_dict.setdefault(image_node.tag, {}).update(image_node.attrib)
      attr_dict.setdefault(image_frame_node.tag, {}).update(image_frame_node.attrib)
      return True

    def render_odg(self, field, as_string, local_name, target_node, printout,
        REQUEST, ooo_builder, attr_dict=None):
      """
        return an image xml node rendered in odg format
        if as_string is True (default) the returned value is a string (xml
        reprensation of the node), if it's False, the value returned is the node
        object.
        attr_dict can be used for additional parameters (like style).
      """
      # replace the image in the odg document
      if not self._replaceImage(target_node, ooo_builder, field, printout,
          REQUEST, attr_dict):
        # if image is not found, return None
        return None

      if attr_dict is None:
        attr_dict = {}

      draw_frame_tag_name = '{%s}%s' % (DRAW_URI, 'frame')
      draw_frame_node = Element(draw_frame_tag_name, nsmap=NSMAP)
      draw_frame_node.attrib.update(attr_dict.get(draw_frame_tag_name, {}))

      draw_image_tag_name = '{%s}%s' % (DRAW_URI, 'image')
      draw_image_node = Element(draw_image_tag_name, nsmap=NSMAP)
      draw_image_node.attrib.update(attr_dict.get(draw_image_tag_name, {}))

      text_p_tag_name = '{%s}%s' % (TEXT_URI, local_name)
      text_p_node = Element(text_p_tag_name, nsmap=NSMAP)
      text_p_node.attrib.update(attr_dict.get(text_p_tag_name, {}))

      draw_image_node.append(text_p_node)
      draw_frame_node.append(draw_image_node)

      if as_string:
        return etree.tostring(draw_frame_node)
      return draw_frame_node

ImageFieldWidgetInstance = ImageFieldWidget()
ImageFieldValidatorInstance = Validator.StringValidator()

class ImageField(ZMIField):
    meta_type = "ImageField"

    widget = ImageFieldWidgetInstance
    validator = ImageFieldValidatorInstance


