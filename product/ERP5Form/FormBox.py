# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets <jp@nexedi.com>
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

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.ERP5Type.Globals import get_request
from Products.PythonScripts.Utility import allow_class

from Products.PythonScripts.standard import url_quote_plus
from Products.Formulator.Errors import FormValidationError, ValidationError

import string

class FormBoxWidget(Widget.Widget):
  """
      A widget that display a form within a form.

      A first purpose of this widget is to display addresses in
      a different order for every localisation.

      A second purpose of this widget is to represent a single value
      (ex. a number, a date) into multiple forms. We need for that
      purpose a script to assemble a value out of

      A third purpose is to display values on subobjects and,
      if necessary, create such objects ?

      WARNING: this is still pre-alpha code for experimentation. Do not
      use in production.
  """

  property_names = Widget.Widget.property_names + [
    'formbox_target_id', \
    'context_method_id', \
  ]

  # This name was changed to prevent naming collision with ProxyField
  formbox_target_id = fields.StringField(
                                'formbox_target_id',
                                title='Form ID',
                                description=(
    "ID of the form which must be rendered in this box."),
                                default="",
                                required=0)

  context_method_id = fields.StringField(
                                'context_method_id',
                                title='Context method ID',
                                description=(
    "ID of the method that returns a context for this box."),
                                default="",
                                required=0)

  default = fields.StringField(
                                'default',
                                title='Default',
                                description=(
    "A default value (not used)."),
                                default="",
                                required=0)

  def render_view(self, field, value, REQUEST, render_prefix=None):
    """
        Render a view form in a field
    """
    return self.render(field, None, value, REQUEST, render_prefix)

  def render(self, field, key, value, REQUEST, render_prefix=None):
    """
        Render a form in a field
    """
    target_id = field.get_value('formbox_target_id')
    if target_id:
      other = REQUEST.other
      here = other['here']
      context_method_id = field.get_value('context_method_id')
      try:
        cell = other.pop('cell', None)
        context = cell or here
        if context_method_id:
          context = getattr(context, context_method_id)(
            field=field, REQUEST=REQUEST)
        return getattr(context, target_id)(REQUEST=REQUEST, key_prefix=key)
      finally:
        other['here'] = here
        if cell:
          other['cell'] = cell
    return ''

class FormBoxEditor:
  """
  A class holding all values required to update the object
  """
  def __init__(self, field_id, result):
    self.field_id = field_id
    self.result = result

  def view(self):
    return self.__dict__

  def __call__(self, REQUEST):
    pass

  def edit(self, context):
    context.edit(**self.result[0])
    for encapsulated_editor in self.result[1]:
      encapsulated_editor.edit(context)

  def as_dict(self):
    """
    This method is used to return parameter dict.
    XXX This API is probably not stable and may change, as some editors are used to
    edit multiple objects.
    """
    result_dict = self.result[0]
    for encapsulated_editor in self.result[1]:
      if hasattr(encapsulated_editor, 'as_dict'):
        result_dict.update(
            encapsulated_editor.as_dict())
    return result_dict

allow_class(FormBoxEditor)

class FormBoxValidator(Validator.Validator):
  """
    Validate all fields of the form and return
    the result as a single variable.
  """
  property_names = Validator.Validator.property_names
  message_names = Validator.Validator.message_names + \
                  ['form_invalidated', 'required_not_found']

  form_invalidated = "Form invalidated."
  required_not_found = 'Input is required but no input given.'

  def validate(self, field, key, REQUEST):
    # XXX hardcoded acquisition
    # TODO: Handle 'cell' for validation inside listboxes,
    #       like it is done for rendering.
    here = field.aq_parent.aq_parent
    context_method_id = field.get_value('context_method_id')
    if context_method_id:
      here = getattr(here, context_method_id)(field=field, REQUEST=REQUEST)
    formbox_target_id = field.get_value('formbox_target_id')

    # Get current error fields
    current_field_errors = REQUEST.get('field_errors', [])

    # XXX Hardcode script name
    result, result_type = here.Base_edit(formbox_target_id, silent_mode=1, key_prefix=key)
    if result_type == 'edit':
      return FormBoxEditor(field.id, result)
    elif result_type == 'form':
      formbox_field_errors = REQUEST.get('field_errors', [])
      current_field_errors.extend(formbox_field_errors)
      REQUEST.set('field_errors', current_field_errors)
      getattr(here, formbox_target_id).validate_all_to_request(REQUEST, key_prefix=key)
    else:
      raise NotImplementedError, result_type

FormBoxWidgetInstance = FormBoxWidget()
FormBoxValidatorInstance = FormBoxValidator()

class FormBox(ZMIField):
  meta_type = "FormBox"

  widget = FormBoxWidgetInstance
  validator = FormBoxValidatorInstance
