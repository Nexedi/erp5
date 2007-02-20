##############################################################################
#
# Copyright (c) 2002, 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
from Products.Formulator.DummyField import fields
from Products.ERP5Type.Utils import convertToUpperCase
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.Utility import allow_class
from Products.ERP5Type.Message import Message
from Products.ERP5Form import MultiRelationField
from Products.ERP5Form.MultiRelationField import MAX_SELECT, \
                                            NEW_CONTENT_PREFIX, \
                                            SUB_FIELD_ID, ITEM_ID, \
                                            NO_VALUE
from types import StringType
from AccessControl import ClassSecurityInfo
from zLOG import LOG

class RelationStringFieldWidget(
                  MultiRelationField.MultiRelationStringFieldWidget):
  """
  RelationStringField widget
  Works like a string field but includes one buttons
  - one search button which updates the field and sets a relation
  - creates object if not there
  """
  property_names = Widget.TextWidget.property_names + \
       MultiRelationField.MultiRelationStringFieldWidget.local_property_names

  default_widget_rendering_instance = Widget.TextWidgetInstance
  default = Widget.TextWidget.default

  def _generateRenderValueList(self, field, key, value, REQUEST):
#     value = value or NO_VALUE
    relation_field_id = field.generate_subfield_key(SUB_FIELD_ID, key=key)
    relation_item_key = field.generate_subfield_key(ITEM_ID, key=key)
    relation_item_list = REQUEST.get(relation_item_key, [])
    return [(Widget.TextWidgetInstance, relation_field_id, 
             relation_item_list, value, None)]

class RelationEditor(MultiRelationField.MultiRelationEditor):
  """
  A class holding all values required to update a relation
  """
  def __call__(self, REQUEST):
    MultiRelationField.MultiRelationEditor.__call__(self, REQUEST)
    value = REQUEST.get(self.field_id)
    if value is not None:
      REQUEST.set(self.field_id, value[0])

allow_class(RelationEditor)

class RelationStringFieldValidator(
               MultiRelationField.MultiRelationStringFieldValidator,
               Validator.StringValidator):
  """
      Validation includes lookup of relared instances
  """

  message_names = Validator.StringValidator.message_names + \
            MultiRelationField.MultiRelationStringFieldValidator.message_names
  property_names = Validator.StringValidator.property_names + \
          MultiRelationField.MultiRelationStringFieldValidator.property_names

  # Delete double in order to keep a usable ZMI...
  # Need to keep order !
  _v_dict = {}
  _v_message_name_list = []
  for message_name in message_names:
    if not _v_dict.has_key(message_name):
      _v_message_name_list.append(message_name)
      _v_dict[message_name] = 1
  message_names = _v_message_name_list
  
  _v_dict = {}
  _v_property_name_list = []
  for property_name in property_names:
    if not _v_dict.has_key(property_name):
      _v_property_name_list.append(property_name)
      _v_dict[property_name] = 1
  property_names = _v_property_name_list

  # Relation field variable
  editor = RelationEditor
  default_validator_instance = Validator.StringValidatorInstance

  def _generateItemUidList(self, field, key, relation_uid_list, REQUEST=None):
    """
    Generate list of uid, item_key
    """
    relation_item_id = field.generate_subfield_key(ITEM_ID,
                                                   key=key)
    if isinstance(relation_uid_list, (list, tuple)):
      try:
        relation_uid_list = relation_uid_list[0]
      except IndexError:
        # No object was selected
        return []
    value = self.default_validator_instance.validate(field, 
                                                     key, REQUEST)
    return [(relation_item_id, relation_uid_list, value)]

  def _generateFieldValueList(self, field, key, 
                              value_list, current_value_list):
    """
    Generate list of value, item_key
    """
    if value_list == current_value_list:
      return []
    else:
      relation_field_id = field.generate_subfield_key("%s" % \
                                                      SUB_FIELD_ID, key=key)
      relation_item_key = field.generate_subfield_key(ITEM_ID, key=key)
      return [(relation_field_id, value_list, relation_item_key)]

RelationStringFieldWidgetInstance = RelationStringFieldWidget()
RelationStringFieldValidatorInstance = RelationStringFieldValidator()

# Should RelationStringField be a subclass of MultiRelationStringField ?
class RelationStringField(ZMIField):
  meta_type = "RelationStringField"
  security = ClassSecurityInfo()

  widget = RelationStringFieldWidgetInstance
  validator = RelationStringFieldValidatorInstance

  security.declareProtected('Access contents information', 'get_orig_value')
  def get_orig_value(self, id):
    """
    Get value for id; don't do any override calculation.
    """
    if id == 'is_relation_field': 
      result = 1
    elif id == 'is_multi_relation_field':
      result = 0
    else:
      result = ZMIField.get_orig_value(self, id)
    return result

  security.declareProtected('Access contents information', 'get_value')
  def get_value(self, id, REQUEST=None, **kw):
    """Get value for id.

    Optionally pass keyword arguments that get passed to TALES
    expression.
    """
    # XXX FIXME Same code as MultiRelationStringField
    if (id == 'items') and (REQUEST is not None):
      # relation_item_list is not editable for the RelationField
      result = REQUEST.get('relation_item_list', None)
    else:
      result = ZMIField.get_value(self, id, REQUEST=REQUEST, **kw)
    return result
