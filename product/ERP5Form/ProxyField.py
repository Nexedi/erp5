##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
import string

from zLOG import LOG, WARNING
from Acquisition import aq_base, aq_inner, aq_acquire, aq_chain

class ProxyWidget(Widget.Widget):
  """
      A widget that renders itself as a field from another form
      after changing its title and id. It is recommended to define
      a master form on which complex fields with a lot of TALES
      are defined in order to minimize code duplication.
  """

  property_names = [
    'form_id',
    'field_id',
    'extra_context',
  ]

  form_id = fields.StringField(
                                'form_id',
                                title='Form ID',
                                description= \
                                  "ID of the master form.",
                                default="",
                                required=1)

  field_id = fields.StringField(
                                'field_id',
                                title='Field ID',
                                description= \
                                  "ID of the field in the master form.",
                                default="",
                                required=1)

  # XXX FIXME This seems against the definition of proxy field...
  # Remove it as soon as possible
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
    result = ''
    proxy_field = field.getTemplateField()
    if proxy_field is not None:
      REQUEST = field.updateContext(REQUEST)
      result = proxy_field.widget.render(proxy_field, key, value, REQUEST)
    return result

  def render_view(self, field, value):
    """
      Display proxy field
    """
    result = ''
    proxy_field = field.getTemplateField()
    if proxy_field is not None:
      result = proxy_field.widget.render_view(proxy_field, value)
    return result

class ProxyValidator(Validator.Validator):
  """
    Validation of entered value through proxy field
  """
  property_names = []

  def validate(self, field, key, REQUEST):
    proxy_field = field.getTemplateField()
    REQUEST = field.updateContext(REQUEST)
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
  security = ClassSecurityInfo()

  widget = ProxyWidgetInstance
  validator = ProxyValidatorInstance

  def getTemplateField(self):
    """
    Return template field of the proxy field.
    """
    form = self.aq_parent
    object = form.aq_parent
    try:
      proxy_form = getattr(object, self.get_value('form_id'))
      proxy_field = aq_base(getattr(proxy_form, self.get_value('field_id')))
      proxy_field = proxy_field.__of__(form)
    except AttributeError:
      LOG('ProxyField', WARNING, 
          'Could not get a field from a proxy field %s in %s' % \
              (self.id, object.id))
      proxy_field = None
    return proxy_field

  def updateContext(self, REQUEST):
    """
    Update the REQUEST
    """
    extra_context = REQUEST.other.get('erp5_extra_context', {})
    for k, v in self.get_value('extra_context'):
      extra_context[k] = v
    REQUEST.other['erp5_extra_context'] = extra_context
    return REQUEST

  security.declareProtected('Access contents information', 'get_value')
  def get_value(self, id, **kw):
    """Get value for id.

    Optionally pass keyword arguments that get passed to TALES
    expression.
    """
    if id in self.widget.property_names:
      result = ZMIField.get_value(self, id, **kw)
    else:
      proxy_field = self.getTemplateField()
      if proxy_field is not None:
        result = proxy_field.get_value(id, **kw)
    return result
