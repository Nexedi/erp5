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
from DocumentTemplate.DT_Util import html_quote


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
        display = field.get_value('image_display')
        format = field.get_value('image_format')
        resolution = field.get_value('image_resolution')
        html_string = '<img src="%s?display=%s&amp;format=%s&amp;'\
                      'resolution=%s" alt="%s"/>' % \
            (html_quote(image),
             html_quote(display),
             html_quote(format),
             html_quote(resolution),
             html_quote(alt))
        return html_string

ImageFieldWidgetInstance = ImageFieldWidget()
ImageFieldValidatorInstance = Validator.StringValidator()

class ImageField(ZMIField):
    meta_type = "ImageField"

    widget = ImageFieldWidgetInstance
    validator = ImageFieldValidatorInstance


