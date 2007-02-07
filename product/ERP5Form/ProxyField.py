##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets <jp@nexedi.com>
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
from Products.Formulator.Errors import ValidationError
from Products.ERP5Type.Utils import convertToUpperCase
from Products.CMFCore.utils import getToolByName

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Globals import get_request
from Products.PythonScripts.Utility import allow_class

from Products.PythonScripts.standard import url_quote_plus

from AccessControl import ClassSecurityInfo
import string

from zLOG import LOG, WARNING, DEBUG
from Acquisition import aq_base, aq_inner, aq_acquire, aq_chain
from Globals import DTMLFile

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
    'target',
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

  target = fields.HyperLinkField(
                                'target',
                                title='Proxy Target',
                                description="Link to the master field edit form",
                                default='Click to edit the target',
                                href='manage_edit_target',
                                required=0)

  def render(self, field, key, value, REQUEST):
    """
    Render proxy field
    """
    result = ''
    proxy_field = field.getRecursiveTemplateField()
    if proxy_field is not None:
      result = proxy_field.widget.render(field, key, value, REQUEST)
    return result

  def render_htmlgrid(self, field, key, value, REQUEST):
    """
    Render proxy field
    """
    result = ''
    proxy_field = field.getRecursiveTemplateField()
    if proxy_field is not None:
      result = proxy_field.widget.render_htmlgrid(field, key, value, REQUEST)
    return result

  def render_view(self, field, value):
    """
      Display proxy field
    """
    result = ''
    proxy_field = field.getRecursiveTemplateField()
    if proxy_field is not None:
      result = proxy_field.widget.render_view(field, value)
    return result

class ProxyValidator(Validator.Validator):
  """
    Validation of entered value through proxy field
  """
  property_names = []

  def validate(self, field, key, REQUEST):
    proxy_field = field.getTemplateField()
    try:
      result = proxy_field.validator.validate(field, key, REQUEST)
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

  # methods screen
  security.declareProtected('View management screens',
                            'manage_main')
  manage_main = DTMLFile('dtml/proxyFieldEdit', globals())

  # tales screen
  security.declareProtected('View management screens',
                            'manage_talesForm')
  manage_talesForm = DTMLFile('dtml/proxyFieldTales', globals())

  # proxy field list header
  security.declareProtected('View management screens', 'proxyFieldListHeader')
  proxyFieldListHeader = DTMLFile('dtml/proxyFieldListHeader', globals())

  security.declareProtected('Change Formulator Forms', 'manage_edit')
  def manage_edit(self, REQUEST):
    """
    Surcharged values from proxied field.
    """
    # Edit template field attributes
    template_field = self.getRecursiveTemplateField()
    if template_field is not None:

      # Check the surcharged checkboxes
      surcharge_list = []
      for group in template_field.form.get_groups():
        for field in template_field.form.get_fields_in_group(group):
          field_id = field.id
          checkbox_key = "surcharge_%s" % field_id
          if not REQUEST.has_key(checkbox_key):
            surcharge_list.append(field_id)

      try:
        # validate the form and get results
        result = template_field.form.validate(REQUEST)
      except ValidationError, err:
        if REQUEST:
          message = "Error: %s - %s" % (err.field.get_value('title'),
                                        err.error_text)
          return self.manage_main(self, REQUEST,
                                  manage_tabs_message=message)
        else:
          raise

      self._surcharged_edit(result, surcharge_list)
    
    # Edit standards attributes
    # XXX It is not possible to call ZMIField.manage_edit because
    # it returns at the end...
    # we need to had a parameter to the method
    try:
      # validate the form and get results
      result = self.form.validate(REQUEST)
    except ValidationError, err:
      if REQUEST:
        message = "Error: %s - %s" % (err.field.get_value('title'),
                                      err.error_text)
        return self.manage_main(self,REQUEST,
                                manage_tabs_message=message)
      else:
        raise

    self._edit(result)
        
    if REQUEST:
      message="Content changed."
      return self.manage_main(self, REQUEST,
                              manage_tabs_message=message)

  def _surcharged_edit(self, result, surcharge_list):
    # first check for any changes  
    values = self.values
    # if we are in unicode mode, convert result to unicode
    # acquire get_unicode_mode and get_stored_encoding from form..
    if self.get_unicode_mode():
      new_result = {}
      for key, value in result.items():
        if type(value) == type(''):
          # in unicode mode, Formulator UI always uses UTF-8
          value = unicode(value, 'UTF-8')
        new_result[key] = value
      result = new_result

    changed = []
    for key, value in result.items():
      # XXX Remove old values
      values.pop(key, None)
      # store keys for which we want to notify change
      if not values.has_key(key) or values[key] != value:
        changed.append(key)

    proxied_field = self.getTemplateField()
    for key, value in result.items():
      if key not in surcharge_list:
        result.pop(key)

    # now do actual update of values
    values.update(result)
    self.values = values
    self.delegated_list = surcharge_list

    # finally notify field of all changed values if necessary
    for key in changed:
      method_name = "on_value_%s_changed" % key
      if hasattr(self, method_name):
        getattr(self, method_name)(values[key])

  security.declareProtected('Change Formulator Forms', 'manage_tales')
  def manage_tales(self, REQUEST):
    """
    Surcharged talesfrom proxied field.
    """
    template_field = self.getRecursiveTemplateField()
    if template_field is not None:

      # Check the surcharged checkboxes
      surcharge_list = []
      for group in template_field.tales_form.get_groups():
        for field in template_field.tales_form.get_fields_in_group(group):
          field_id = field.id
          checkbox_key = "surcharge_%s" % field_id
          if not REQUEST.has_key(checkbox_key):
            surcharge_list.append(field_id)


      try:
        # validate the form and get results
        result = template_field.tales_form.validate(REQUEST)
      except ValidationError, err:
        if REQUEST:
          message = "Error: %s - %s" % (err.field.get_value('title'),
                                        err.error_text)
          return self.manage_talesForm(self, REQUEST,
                                       manage_tabs_message=message)
        else:
          raise

      self._surcharged_tales(result, surcharge_list)

    try:
      # validate the form and get results
      result = self.tales_form.validate(REQUEST)
    except ValidationError, err:
      if REQUEST:
        message = "Error: %s - %s" % (err.field.get_value('title'),
                                      err.error_text)
        return self.manage_talesForm(self,REQUEST,
                                     manage_tabs_message=message)
      else:
        raise

    self._edit_tales(result)

    
    if REQUEST:
      message="Content changed."
      return self.manage_talesForm(self, REQUEST,
                                            manage_tabs_message=message)

  def _surcharged_tales(self, result, surcharge_list):
    # first check for any changes  
    tales = self.tales

    changed = []
    for key, value in result.items():
      # XXX Remove old values
      tales.pop(key, None)

    proxied_field = self.getTemplateField()
    for key, value in result.items():
      if key not in surcharge_list:
        result.pop(key)

    # now do actual update of values
    tales.update(result)
    self.tales = tales
    self.delegated_list = surcharge_list

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

  def getRecursiveTemplateField(self):
    """
    Return template field of the proxy field.
    This result must not be a ProxyField.
    """
    template_field = self.getTemplateField()
    if template_field.__class__ == ProxyField:
      return template_field.getTemplateField()
    else:
      return template_field

  security.declareProtected('Access contents information', 
                            'is_delegated')
  def is_delegated(self, id):
    """
    Return true if we get the value from the proxied field.
    No, if we surcharged the value on the proxy field.
    """
    # Update old proxied field
    try:
      if id in self.delegated_list:
        return False
      else:
        return True
    except AttributeError:
      # Update old proxied field
      self.delegated_list = []
      return True

  security.declareProtected('Access contents information', 
                            'get_recursive_orig_value')
  def get_recursive_orig_value(self, id, include=1):
    """
    Get value for id recursively.
    """
    if include and \
      ((id in self.widget.property_names) or \
       not self.is_delegated(id)):
      return self.get_orig_value(id)
    else:
      proxied_field = self.getTemplateField()
      if proxied_field.__class__ == ProxyField:
        return proxied_field.get_recursive_orig_value(id)
      else:
        return proxied_field.get_orig_value(id)

  security.declareProtected('View management screens', 'get_recursive_tales')
  def get_recursive_tales(self, id, include=1):
    """
    Get tales expression method for id.
    """
    if include and \
      ((id in self.widget.property_names) or \
       not self.is_delegated(id)):
      return self.get_tales(id)
    else:
      proxied_field = self.getTemplateField()
      if proxied_field.__class__ == ProxyField:
        return proxied_field.get_recursive_tales(id)
      else:
        return proxied_field.get_tales(id)
    
  # XXX Not implemented
  security.declareProtected('View management screens', 'get_recursive_override')
  def get_recursive_override(self, id):
    """
    Get override method for id (not wrapped).
    """
    return self.overrides.get(id, "")

  security.declareProtected('View management screens', 'get_error_message')
  def get_error_message(self, name):
    """
    """
    try:
      return self.message_values[name]
    except KeyError:
      proxied_field = self.getTemplateField()
      if proxied_field is not None:
        return proxied_field.get_error_message(name)
      else:
        return ZMIField.get_error_message(self, name)


  security.declareProtected('Edit target', 'manage_edit_target')
  def manage_edit_target(self, REQUEST):
    """ 
    Edit target field of this proxy
    """
    proxy_field = self.getTemplateField()
    if proxy_field:
      url='/'.join((self.absolute_url(),
                    self.get_value('form_id'),
                    self.get_value('field_id'),
                    'manage_main'))
      REQUEST.RESPONSE.redirect(url)
    else:
      # FIXME: should show some error message 
      # ("form_id and field_id don't define a valid template")
      pass

  security.declareProtected('Access contents information', 'get_value')
  def get_value(self, id, **kw):
    """Get value for id.

    Optionally pass keyword arguments that get passed to TALES
    expression.
    """
    result = None
    if (id in self.widget.property_names) or \
       (not self.is_delegated(id)):
      result = ZMIField.get_value(self, id, **kw)
    else:
      proxy_field = self.getTemplateField()
      if proxy_field is not None:
        result = proxy_field.get_value(id, **kw)
    return result

  security.declareProtected('Access contents information', 'has_value')
  def has_value(self, id):
    """
    Return true if the field defines such a value.
    """
    result = None
    if (id in self.widget.property_names) or \
       (not self.is_delegated(id)):
      result = ZMIField.has_value(self, id)
    else:
      proxy_field = self.getTemplateField()
      if proxy_field is not None:
        result = proxy_field.has_value(id)
    return result
