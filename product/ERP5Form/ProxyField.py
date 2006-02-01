##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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
from Products.Formulator.Errors import ValidationError
from Products.ERP5Type.Utils import convertToUpperCase
from Products.CMFCore.utils import getToolByName

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Globals import get_request
from Products.PythonScripts.Utility import allow_class

from Products.PythonScripts.standard import url_quote_plus

import string

from zLOG import LOG, WARNING

class ProxyWidget(Widget.Widget):
  """
      A widget that renders itself as a field from another form
      after changing its title and id. It is recommended to define
      a master form on which complex fields with a lot of TALES
      are defined in order to minimize code duplication.
  """

  property_names = Widget.Widget.property_names + [
    'form_id', \
    'field_id', \
    'extra_context', \
  ]

  form_id = fields.StringField(
                                'form_id',
                                title='Form ID',
                                description=(
    "ID of the master form."),
                                default="",
                                required=1)

  field_id = fields.StringField(
                                'field_id',
                                title='Field ID',
                                description=(
    "ID of the field in the master form."),
                                default="",
                                required=1)

  default = fields.StringField(
                                'default',
                                title='Default',
                                description=(
    "Default value."),
                                default="",
                                required=0)

  extra_context = fields.ListTextAreaField(
                                'extra_context', 
                                title='Extra Context', 
                                description='Additional context variables.', 
                                default=(), 
                                required=0)

 
  def render(self, field, key, value, REQUEST):
    """
      Render proxy field
    """
    form = field.aq_parent
    try:
      proxy_form = getattr(form, field.get_value('form_id'))
      proxy_field = getattr(proxy_form, field.get_value('field_id'))
    except AttributeError:
      LOG('ProxyField', WARNING, 'could not get a field from a proxy field %s in %s' % (field.id, form.id))
      return ''
    extra_context = REQUEST.get('erp5_extra_context', {})
    for k, v in field.get_value('extra_context'):
      extra_context[k] = v
    REQUEST['erp5_extra_context'] = extra_context
    return proxy_field.widget.render(proxy_field, key, value, REQUEST)

  def render_view(self, field, value):
    """
      Display proxy field
    """
    form = field.aq_parent
    try:
      proxy_form = getattr(form, field.get_value('form_id'))
      proxy_field = getattr(proxy_form, field.get_value('field_id'))
    except AttributeError:
      LOG('ProxyField', WARNING, 'could not get a field from a proxy field %s in %s' % (field.id, form.id))
      return ''
    REQUEST = get_request()
    extra_context = REQUEST.get('erp5_extra_context', {})
    for k, v in field.get_value('extra_context'):
      extra_context[k] = v
    REQUEST['erp5_extra_context'] = extra_context
    return proxy_field.widget.render_view(proxy_field, key, value)


class ProxyValidator(Validator.Validator):
  """
    Validation of entered value through proxy field
  """
  property_names = Validator.Validator.property_names

  def validate(self, field, key, REQUEST):
    form = field.aq_parent
    proxy_form = getattr(form, field.get_value('form_id'))
    proxy_field = getattr(proxy_form, field.get_value('field_id'))
    try:
      result = proxy_field.validator.validate(proxy_field, key, REQUEST)
    except ValidationError, error:
      error.field_id = field.id
      raise error
    return result

ProxyWidgetInstance = ProxyWidget()
ProxyValidatorInstance = ProxyValidator()

class ProxyField(ZMIField):
  meta_type = "ProxyField"

  widget = ProxyWidgetInstance
  validator = ProxyValidatorInstance
