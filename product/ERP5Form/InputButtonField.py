##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

class InputButtonWidget(Widget.Widget):
    """
    InputButton widget

    Displays an input button.

    """
    property_names = Widget.Widget.property_names + ['name', 'extra']

    default = fields.StringField('default',
                                 title='Button text',
                                 description=(
        "You can place text here that will be used as the value (button text)"),
                                 default="Submit",
                                 required=1)

    name = fields.StringField('name',
                          title='Name',
                          description=(
        "The Name of the submit button."),
                          default='',
                          required=0)

    css_class = fields.StringField('css_class',
                                   title='CSS class',
                                   description=(
        "The CSS class of the field. This can be used to style your "
        "formulator fields using cascading style sheets. Not required."),
                                   default="hiddenLabel",
                                   required=0)

    def render(self, field, key, value, REQUEST):
        """Render input button.
        """
        return Widget.render_element("input",
                              type="submit",
                              name=field.get_value('name'),
                              css_class=field.get_value('css_class'),
                              value=field.get_value('default'),
                              extra=field.get_value('extra'))

InputButtonWidgetInstance = InputButtonWidget()

class InputButtonField(ZMIField):
    meta_type = "InputButtonField"

    widget = InputButtonWidgetInstance
    validator = Validator.SuppressValidatorInstance
