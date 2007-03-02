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

class ParallelListWidget(Widget.MultiListWidget,
                         Widget.ListWidget):
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
                     Widget.ListWidget.property_names + \
      ['hash_script_id']

    hash_script_id = fields.StringField('hash_script_id',
                               title='Hash script',
                               description=(
        "The method to call to hash items list."),
                               required=0)

    # delete double in order to keep a usable ZMI...
    # XXX need to keep order !
    #property_names = dict([(i,0) for i in property_names]).keys()
    _v_dict = {}
    _v_property_name_list = []
    for property_name in property_names:
      if not _v_dict.has_key(property_name):
        _v_property_name_list.append(property_name)
        _v_dict[property_name] = 1
    property_names = _v_property_name_list

    def __init__(self):
      """
      Generate some subwidget used for rendering.
      """
      self.sub_widget = {
        'ListField': Widget.ListWidgetInstance,
        'MultiListField': Widget.MultiListWidgetInstance,
      }

    def render(self, field, key, value, REQUEST):
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

    def render_htmlgrid(self, field, key, value, REQUEST):
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
                        sub_field_property_dict):
      """
      Render dynamically a subfield
      """
      REQUEST.set('_v_plf_title', sub_field_property_dict['title'])
      REQUEST.set('_v_plf_required', sub_field_property_dict['required'])
      REQUEST.set('_v_plf_default', "")
      REQUEST.set('_v_plf_first_item', 0)
      REQUEST.set('_v_plf_items', sub_field_property_dict['item_list'])
      REQUEST.set('_v_plf_size', sub_field_property_dict['size'])
      if sub_field_property_dict.get('editable', 1):
        return self.sub_widget[sub_field_property_dict['field_type']].render(
                field,
                field.generate_subfield_key(sub_field_property_dict['key'],
                                            key=key),
                sub_field_property_dict['value'],
                REQUEST)
      else:
        return self.sub_widget[sub_field_property_dict['field_type']].render_view(
                field,
                sub_field_property_dict['value'],
                )

class ParallelListValidator(Validator.MultiSelectionValidator):

  property_names = Validator.MultiSelectionValidator.property_names 

  def __init__(self):
    """
    Generate some subvalidator used for rendering.
    """
    self.sub_validator = {
      'ListField': Validator.SelectionValidatorInstance,
      'MultiListField': Validator.MultiSelectionValidatorInstance,
    }

  def validate(self, field, key, REQUEST):    

    result_list = []
    hash_list = generateSubForm(field, None, REQUEST)
    is_sub_field_required = 0
    for sub_field_property_dict in hash_list:
      try:
        sub_result_list = self.validate_sub_field(
                                  field,
                                  field.generate_subfield_key(
                                      sub_field_property_dict['key'], 
                                      validation=1, key=key),
                                  REQUEST,
                                  sub_field_property_dict)
        if not isinstance(sub_result_list, (list, tuple)):
          sub_result_list = [sub_result_list]
        else:
          sub_result_list = list(sub_result_list)
        result_list.extend(sub_result_list)
      except ValidationError:
        is_sub_field_required = 1
    
    result_list = [x for x in result_list if x!='']
    if result_list == []:
      if field.get_value('required'):
        self.raise_error('required_not_found', field)
    else:
      if is_sub_field_required:
        self.raise_error('required_not_found', field)
    return result_list

  def validate_sub_field(self, field, id, REQUEST, sub_field_property_dict):
    """
    Validates a subfield (as part of field validation).
    """
    REQUEST.set('_v_plf_title', sub_field_property_dict['title'])
    REQUEST.set('_v_plf_required', sub_field_property_dict['required'])
    REQUEST.set('_v_plf_default', "")
    REQUEST.set('_v_plf_items', sub_field_property_dict['item_list'])
    REQUEST.set('_v_plf_size', sub_field_property_dict['size'])
    return self.sub_validator[sub_field_property_dict['field_type']].validate(
        field, id, REQUEST)

ParallelListWidgetInstance = ParallelListWidget()
ParallelListFieldValidatorInstance = ParallelListValidator()

class ParallelListField(ZMIField):
  security = ClassSecurityInfo()
  meta_type = "ParallelListField"

  widget = ParallelListWidgetInstance
  validator = ParallelListFieldValidatorInstance 

  def render_htmlgrid(self, value=None, REQUEST=None, key=None):
    """
    render_htmlgrid returns a list of tuple (title, html render)
    We will use title generated by the widget.
    """
    key = self.generate_field_key(key=key)
    value = self._get_default(key, value, REQUEST)
    html = self.widget.render_htmlgrid(self, key, value, REQUEST)
    return html

  security.declareProtected('Access contents information', 'get_value')
  def get_value(self, id, REQUEST=None, **kw):
    """
    Get value for id.
    Optionally pass keyword arguments that get passed to TALES
    expression.
    """
    key = '_v_plf_%s' % id
    if (REQUEST is not None) and \
       (REQUEST.has_key(key)):
      result = REQUEST.get(key)
    else:
      result = ZMIField.get_value(self, id, REQUEST=REQUEST, **kw)
    return result

def generateSubForm(self, value, REQUEST):
  item_list = [x for x in self.get_value('items') \
               if x not in (('',''), ['',''])]

  value_list = value
  if not isinstance(value_list, (list, tuple)):
    value_list = [value_list]

  empty_sub_field_property_dict = {
    'key': 'default',
    'title': self.get_value('title'),
    'required': 0,
    'field_type': 'MultiListField',
    'item_list': [],
    'value': [],
    'is_right_display': 0,
    'size': 5,
    'editable' : self.get_value('editable', REQUEST=REQUEST)
  }

  hash_list = []
  hash_script_id = self.get_value('hash_script_id')
  if hash_script_id not in [None, '']:
    script = getattr(self, hash_script_id)
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
    default_sub_field_property_dict.update({
        'item_list': item_list,
        'value': value_list,
    })
    hash_list.append(default_sub_field_property_dict)
  # XXX Clean up old ParallelListField
  if hasattr(self, 'sub_form'):
     delattr(self, 'sub_form')
  return hash_list
