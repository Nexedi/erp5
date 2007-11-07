##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
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
from Products.ERP5Form import FormulatorPatch

from zLOG import LOG
from AccessControl import ClassSecurityInfo
from Products.Formulator.Errors import ValidationError

MINUTE_IN_SECOND = 60
HOUR_IN_SECOND = 3600
# DAY_IN_SECOND = 86400

class DurationWidget(FormulatorPatch.IntegerWidget):
  """
  Duration Widget is used to enter time duration.
  It may be used in movement of Labour (in Task, Calendat Period, ...).

  Time duration in ERP5 are saved ALWAYS IN SECOND.
  
  The field purpose is to display second quantity in hour, minute and second,
  in order to make it more readable.

  XXX This field is experimental, and unstable.
  Do not use it.
  """

  title = fields.StringField('title',
      title='Title. ' \
          '(Warning! Do not use this field!)',
                             description=(
      "The title of this field. This is the title of the field that "
      "will appear in the form when it is displayed. Required."),
                             default="",
                             required=1)

  def render_view(self, field, value):
    sub_field_render_list = []
    for title, sub_key, convertion in (('Hour', 'hour', HOUR_IN_SECOND),
                                ('Minute', 'minute', MINUTE_IN_SECOND)):
      if value == '':
        sub_value = ''
      else:
        sub_value, value = divmod(value, convertion)
      
      sub_field_render_list.append(self.render_sub_field_view(
                                        field,sub_value))
    # Render second
    sub_field_render_list.append(self.render_sub_field_view(
                                      field, value))
    return ':'.join(sub_field_render_list)

  def render(self, field, key, value, REQUEST):
    sub_field_render_list = []
    for title, sub_key, convertion in (('Hour', 'hour', HOUR_IN_SECOND),
                                ('Minute', 'minute', MINUTE_IN_SECOND)):
      if value == '':
        sub_value = ''
      else:
        sub_value, value = divmod(value, convertion)
      sub_field_render_list.append(self.render_sub_field(
                        field, key,
                        sub_value, REQUEST, sub_key))
    # Render second
    sub_field_render_list.append(self.render_sub_field(
                      field, key,
                      value, REQUEST, 'second'))
    return ':'.join(sub_field_render_list)

  def render_sub_field_view(self, field, value):
    """
    Render dynamically a subfield
    """
    return FormulatorPatch.IntegerFieldWidgetInstance.render_view(field,
                                                                  value)

  def render_sub_field(self, field, key, value, REQUEST, keyword):
    """
    Render dynamically a subfield
    """
    return FormulatorPatch.IntegerFieldWidgetInstance.render(
              field,
              field.generate_subfield_key(keyword,
                                          key=key),
              value,
              REQUEST)

class DurationValidator(Validator.IntegerValidator):
  """
  Duration Validator
  """
  def validate(self, field, key, REQUEST):    
    second_value = None
    for sub_key, convertion in (('hour', HOUR_IN_SECOND),
                                ('minute', MINUTE_IN_SECOND),
                                ('second', 1)):
      second_value = self._validate_sub_field(
          field, key, REQUEST, sub_key, convertion, second_value,
      )
    return second_value
    
  def _validate_sub_field(self, field, key, REQUEST, sub_key, 
                          convertion, second_value):
    """
    Validates a subfield (as part of field validation).
    """
    sub_field_value = Validator.IntegerValidatorInstance.validate(
                              field,
                              field.generate_subfield_key(
                                sub_key, 
                                validation=1, key=key),
                              REQUEST
                              )
    if sub_field_value not in (None, ''):
      if second_value is not None:
        second_value += sub_field_value * convertion
      else:
        second_value = sub_field_value * convertion
    return second_value

DurationWidgetInstance = DurationWidget()
DurationFieldValidatorInstance = DurationValidator()

class DurationField(ZMIField):
  security = ClassSecurityInfo()
  meta_type = "DurationField"

  widget = DurationWidgetInstance
  validator = DurationFieldValidatorInstance
