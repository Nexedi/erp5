##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
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
from Products.ERP5Type.Utils import convertToUpperCase
from Products.CMFCore.utils import getToolByName
from Globals import get_request
from Products.PythonScripts.Utility import allow_class

import string
from zLOG import LOG
from Products.Formulator.Widget import ItemsWidget
from AccessControl import ClassSecurityInfo
from Form import BasicForm

from Products.Formulator.Errors import ValidationError

class ParallelListWidget(Widget.MultiListWidget):
    """
      Make the MultilistField more usable for the user.

      ParallelListWidget display a list of (Multi)ListField.
      Each can be required.

      Separation of items list is made with a Hash Script, which take 
      the items list in input, and return a list of dictionnaries.

      Each dictionnary describes a (Multi)Listfield.
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

    property_names = Widget.MultiListWidget.property_names + \
      ['hash_script_id']

    hash_script_id = fields.StringField('hash_script_id',
                               title='Hash script',
                               description=(
        "The method to call to hash items list."),
                               required=0)

    def render(self, field, key, value, REQUEST):

      item_list = filter(lambda x: x not in [ ('',''), ['',''] ], 
                         field.get_value('items'))

      value_list = value
      if type(value_list) not in (type([]), type(())):
        value_list = [value_list]

      empty_sub_field_property_dict = {
        'key': 'default',
        'required': 0,
        'field_type': 'MultiListField',
        'item_list': [],
        'value': [],
        'is_right_display': 0,
        'size': 5
      }

      hash_list = []
      hash_script_id = field.get_value('hash_script_id')
      if hash_script_id not in [None, '']:
        here = REQUEST['here']
        script = getattr(here, hash_script_id)
        script_hash_list = script(
                item_list,
                value_list,
                default_sub_field_property_dict=empty_sub_field_property_dict,
                is_right_display=0)
        hash_list.extend(script_hash_list)
      else:
        # No hash_script founded, generate a little hash_script 
        # to display only a MultiListField
        default_sub_field_property_dict = empty_sub_field_property_dict.copy()
        default_sub_field_property_dict['item_list'] = item_list 
        default_sub_field_property_dict['value'] = value_list
        hash_list.append(default_sub_field_property_dict)

      # XXX Regenerate fields each time....
      field.sub_form = create_aggregated_list_sub_form(hash_list)

      sub_field_render_list = []
      for sub_field_property_dict in hash_list:
        sub_field_render_list.append(field.render_sub_field(
                          sub_field_property_dict['key'], 
                          sub_field_property_dict['value'], REQUEST,
                          key=key))

      html_string = string.join(sub_field_render_list, 
                                field.get_value('view_separator'))
      return html_string

class ParallelListValidator(Validator.MultiSelectionValidator):

  property_names = Validator.MultiSelectionValidator.property_names 

  def validate(self, field, key, REQUEST):    
    result_list = []

    sub_field_id_list = field.sub_form.get_field_ids()
    is_sub_field_required = 0
    for sub_field_id in sub_field_id_list:
      try:
        sub_result_list = field.validate_sub_field(sub_field_id, REQUEST,key=key)
        if type(sub_result_list) not in (type([]), type(())):
          sub_result_list = [sub_result_list]
        else:
          sub_result_list = list(sub_result_list)
        result_list.extend(sub_result_list)
      except ValidationError:
        is_sub_field_required = 1

    result_list = filter( lambda x: x!='', result_list)
    if result_list == []:
      if field.get_value('required'):
        self.raise_error('required_not_found', field)
    else:
      if is_sub_field_required:
        self.raise_error('required_not_found', field)

    return result_list

ParallelListWidgetInstance = ParallelListWidget()
ParallelListFieldValidatorInstance = ParallelListValidator()

class ParallelListField(ZMIField):
    meta_type = "ParallelListField"

    widget = ParallelListWidgetInstance
    validator = ParallelListFieldValidatorInstance 

def create_aggregated_list_sub_form(hash_list):
  """
    Generate ParallelListField sub field.
  """
  sub_form = BasicForm()
  sub_list_field_list = []

  for sub_field_property_dict in hash_list:
    field_class = getattr(StandardFields,
                          sub_field_property_dict['field_type'])
    sub_field = field_class(sub_field_property_dict['key'],
                            title=sub_field_property_dict['key'],
                            required=sub_field_property_dict['required'],
                            default="",
                            items=sub_field_property_dict['item_list'],
                            size=sub_field_property_dict['size'])
    sub_list_field_list.append(sub_field)

  sub_form.add_group("sub_list")
  sub_form.add_fields(sub_list_field_list, "sub_list")

  return sub_form

