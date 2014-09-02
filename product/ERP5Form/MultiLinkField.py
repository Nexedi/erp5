##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
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

class MultiLinkFieldWidget(Widget.MultiItemsWidget):
  """A widget that displays multiples link fields.
  """
  property_names = Widget.Widget.property_names +\
                         ['items', 'view_separator', 'extra', 'extra_item']

  def render_item(self, item_text, item_value, key, css_class, extra_item, render_prefix=None) :
    """Render an Item."""
    return Widget.render_element('a',
                                href=item_value,
                                contents = item_text,
                                name = key,
                                css_class = css_class,
                                extra_item = extra_item)
  render_selected_item = render_item

  def render(self, field, key, value, REQUEST, render_prefix=None):
    """Render the field."""
    rendered_items = self.render_items(field, key, value, REQUEST)
    return field.get_value('view_separator').join(rendered_items)

MultiLinkFieldWidgetInstance = MultiLinkFieldWidget()

class MultiLinkField(ZMIField):
  meta_type = "MultiLinkField"

  widget = MultiLinkFieldWidgetInstance
  # No validation for now
  validator = Validator.SuppressValidatorInstance

