# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005, 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
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
from Products.Formulator import StandardFields
from Products.Formulator.DummyField import fields
from Products.PythonScripts.Utility import allow_class

from zLOG import LOG
from AccessControl import ClassSecurityInfo
from Products.Formulator.Errors import ValidationError

# Field is is not used in keyword in order to be compatible with Proxyfield
KEYWORD = '_v_plf_%s'
MARKER = []

class ParallelListWidget(Widget.MultiListWidget,
                         Widget.ListWidget):
    """
      Make the MultilistField more usable for the user.

      ParallelListWidget display a list of (Multi)ListField.
      Each can be required.

      Separation of items list is made with a Hash Script, which take
      the items list in input, and return a list of dictionnaries.

      Each dictionnary describes a (Multi)ListField.
      The keys are:
        - key:
            default: default
        - required: {1, 0}
            default: 0
        - field_type: {ListField, MultiListField}
            default: MultiListField
        - item_list: [(display, value), ...]
            default: []
        - value:
            default: []
        - is_right_display: {1, 0}
            default: 0
    """

    property_names = (lambda name_list, name_set=set():
      # delete double (but preserve order) in order to keep a usable ZMI...
      [x for x in name_list if not (x in name_set or name_set.add(x))])(
        Widget.MultiListWidget.property_names +
        Widget.ListWidget.property_names +
        ['hash_script_id'])

    hash_script_id = fields.StringField('hash_script_id',
                               title='Hash script',
                               description=(
        "The method to call to hash items list."),
                               required=0)

    def __init__(self):
      """
      Generate some subwidget used for rendering.
      """
      self.sub_widget = {
        'ListField': Widget.ListWidgetInstance,
        'MultiListField': Widget.MultiListWidgetInstance,
      }

    def render(self, field, key, value, REQUEST, render_prefix=None):
      hash_list = generateSubForm(field, value, REQUEST)
      # Call render on each sub field
      sub_field_render_list = []
      for sub_field_property_dict in hash_list:
        sub_field_render_list.append(self.render_sub_field(
                          field, key,
                          sub_field_property_dict['value'], REQUEST,
                          sub_field_property_dict))
      # Aggregate all renders
      html_string = field.get_value('view_separator').\
                                join(sub_field_render_list)
      return html_string

    def render_htmlgrid(self, field, key, value, REQUEST, render_prefix=None):
      hash_list = generateSubForm(field, value, REQUEST)
      # Call render on each sub field
      sub_field_render_list = []
      for sub_field_property_dict in hash_list:
        sub_field_render_list.append((
                          sub_field_property_dict['title'],
                          self.render_sub_field(
                            field, key,
                            sub_field_property_dict['value'], REQUEST,
                            sub_field_property_dict)))
      return sub_field_render_list

    def render_sub_field(self, field, key, value, REQUEST,
                        sub_field_property_dict, render_prefix=None):
      """
      Render dynamically a subfield
      """
      for parameter in ('title', 'required', 'size'):
        REQUEST.set(KEYWORD % parameter, sub_field_property_dict[parameter])
      REQUEST.set(KEYWORD % 'default', "")
      REQUEST.set(KEYWORD % 'first_item', 0)
      REQUEST.set(KEYWORD % 'items', sub_field_property_dict['item_list'])
      sub_widget = self.sub_widget[sub_field_property_dict['field_type']]
      if sub_field_property_dict.get('editable', 1):
        result = sub_widget.render(field,
                                   field.generate_subfield_key(
                                     sub_field_property_dict['key'], key=key),
                                   sub_field_property_dict['value'],
                                   REQUEST=REQUEST)
      else:
        result = sub_widget.render_view(field,
                                        sub_field_property_dict['value'],
                                        REQUEST)
      for parameter in ('title', 'required', 'size', 'default', 'first_item',
                        'items'):
        # As it doesn't seem possible to delete value in the REQUEST,
        # use a marker
        REQUEST.set(KEYWORD % parameter, MARKER)
      return result

    def render_odt(self, field, value, as_string, ooo_builder, REQUEST,
                        render_prefix, attr_dict, local_name):
      """
      """
      return Widget.MultiListWidget.render_odt(self, field, value, as_string,
                                          ooo_builder, REQUEST, render_prefix,
                                          attr_dict, local_name)


    def render_odt_view(self, field, value, as_string, ooo_builder, REQUEST,
                        render_prefix, attr_dict, local_name):
      """
      """
      return Widget.MultiListWidget.render_odt_view(self, field, value, as_string,
                                               ooo_builder, REQUEST,
                                               render_prefix, attr_dict,
                                               local_name)

class ParallelListValidator(Validator.MultiSelectionValidator):

  property_names = Validator.MultiSelectionValidator.property_names

  sub_validator = {
    'ListField': Validator.SelectionValidatorInstance,
    'MultiListField': Validator.MultiSelectionValidatorInstance,
  }

  def validate(self, field, key, REQUEST):
    result_list = []
    hash_list = generateSubForm(field, (), REQUEST)
    for sub_field_property_dict in hash_list:
      id = field.generate_subfield_key(sub_field_property_dict['key'],
                                       validation=1, key=key)
      sub_result_list = self.validate_sub_field(field, id, REQUEST,
                                                sub_field_property_dict)
      if not isinstance(sub_result_list, (list, tuple)):
        sub_result_list = [sub_result_list]
      result_list.extend(sub_result_list)
    REQUEST.form[key] = result_list
    return result_list

  def validate_sub_field(self, field, id, REQUEST, sub_field_property_dict):
    """
    Validates a subfield (as part of field validation).
    """
    try:
      for parameter in ('title', 'required', 'size'):
        REQUEST.set(KEYWORD % parameter, sub_field_property_dict[parameter])
      REQUEST.set(KEYWORD % 'default', "")
      REQUEST.set(KEYWORD % 'items', sub_field_property_dict['item_list'])
      field_type = sub_field_property_dict['field_type']
      if id[-5:] == ':list':
        id = id[:-5]
        field_type = 'Multi' + field_type
        REQUEST.set(id, [x for x in REQUEST.get(id, ()) if x != ''])
      return self.sub_validator[field_type].validate(field, id, REQUEST)
    finally:
      for parameter in ('title', 'required', 'size', 'default', 'first_item',
                        'items'):
        # As it doesn't seem possible to delete value in the REQUEST,
        # use a marker
        REQUEST.set(KEYWORD % parameter, MARKER)

ParallelListWidgetInstance = ParallelListWidget()
ParallelListFieldValidatorInstance = ParallelListValidator()

class ParallelListField(ZMIField):
  security = ClassSecurityInfo()
  meta_type = "ParallelListField"

  widget = ParallelListWidgetInstance
  validator = ParallelListFieldValidatorInstance

  security.declareProtected('Access contents information', 'get_value')
  def get_value(self, id, REQUEST=None, **kw):
    """
    Get value for id.
    Optionally pass keyword arguments that get passed to TALES
    expression.
    """
    return paralellListFieldGetValue(self, id, REQUEST=REQUEST, **kw)

def generateSubForm(self, value, REQUEST):
  item_list = [x for x in self.get_value('items', REQUEST=REQUEST)
                 if x[0] != '' and x[1] != '']

  value_list = value
  if not isinstance(value_list, (list, tuple)):
    value_list = [value_list]

  empty_sub_field_property_dict = {
    'key': 'default',
    'field_type': 'MultiListField',
    'item_list': [],
    'value': [],
    'is_right_display': 0,
  }
  for property in 'title', 'size', 'required', 'editable':
    empty_sub_field_property_dict[property] = self.get_value(property,
                                                             REQUEST=REQUEST)

  hash_script_id = self.get_value('hash_script_id', REQUEST=REQUEST)
  if hash_script_id:
    return getattr(self, hash_script_id)(
            item_list,
            value_list,
            default_sub_field_property_dict=empty_sub_field_property_dict,
            is_right_display=0)
  else:
    # No hash_script founded, generate a little hash_script
    # to display only a MultiListField
    empty_sub_field_property_dict['item_list'] = item_list
    empty_sub_field_property_dict['value'] = value_list
    return [empty_sub_field_property_dict]

def paralellListFieldGetValue(field, id, REQUEST=None, **kw):
  result = MARKER
  key = KEYWORD % id
  if REQUEST is not None and key in REQUEST:
    result = REQUEST.get(key)
  if result is MARKER:
    result = ZMIField.get_value(field, id, REQUEST=REQUEST, **kw)
  return result

# Register get_value
from Products.ERP5Form.ProxyField import registerOriginalGetValueClassAndArgument
registerOriginalGetValueClassAndArgument(
    ParallelListField,
    ('title', 'required', 'size', 'default', 'first_item', 'items'),
    paralellListFieldGetValue)


