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
from Products.Formulator import MethodField
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.CMFCore.utils import getToolByName

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Globals import get_request
from Products.PythonScripts.Utility import allow_class

from Products.PythonScripts.standard import url_quote_plus

from AccessControl import ClassSecurityInfo
from MethodObject import Method

from zLOG import LOG, WARNING, DEBUG, PROBLEM
from Acquisition import aq_base, aq_inner, aq_acquire, aq_chain
from Globals import DTMLFile

from Products.Formulator.TALESField import TALESMethod
from Products.ERP5Form.Form import StaticValue, TALESValue, OverrideValue, DefaultValue, EditableValue
from Products.ERP5Form.Form import copyMethod, isCacheable

_USE_ORIGINAL_GET_VALUE_MARKER = []

_field_value_cache = {}
def purgeFieldValueCache():
  _field_value_cache.clear()

class WidgetDelegatedMethod(Method):
  """Method delegated to the proxied field's widget.
  """
  def __init__(self, method_id, default=''):
    self._method_id = method_id
    self._default = default

  def __call__(self, instance, *args, **kw):
    field = instance
    proxied_field = field.getRecursiveTemplateField()
    if proxied_field:
      proxied_method = getattr(proxied_field.widget, self._method_id)
      return proxied_method(field, *args, **kw)
    return self._default


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

  # Field API Methods, delegated to the template field widget
  render = WidgetDelegatedMethod('render', default='')
  render_htmlgrid = WidgetDelegatedMethod('render_htmlgrid', default='')
  render_view = WidgetDelegatedMethod('render_view', default='')
  render_pdf = WidgetDelegatedMethod('render_pdf', default='')
  render_css = WidgetDelegatedMethod('render_css', default='')
  get_javascript_list = WidgetDelegatedMethod(
                            'get_javascript_list', default=[])


class ProxyValidator(Validator.Validator):
  """
    Validation of entered value through proxy field
  """
  property_names = []

  def validate(self, field, key, REQUEST):
    proxy_field = field.getRecursiveTemplateField()
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
    # Put a default value on not delegated parameter
    for key in result.keys():
      if not self.values.has_key(key):
        self.values[key] = self.get_recursive_orig_value(key, include=0)

  def getTemplateField(self):
    """
    Return template field of the proxy field.
    """
    try:
      return self._getTemplateFieldCache()
    except KeyError:
      pass

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
    self._setTemplateFieldCache(proxy_field)
    return proxy_field

  def getRecursiveTemplateField(self):
    """
    Return template field of the proxy field.
    This result must not be a ProxyField.
    """
    field = self
    while True:
      template_field = field.getTemplateField()
      if template_field.__class__ != ProxyField:
        break
      field = template_field
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
       ((not self.is_delegated(id)) and \
       (self.values.has_key(id)))):
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

  security.declareProtected('Access contents information', '_get_user_input_value')
  def _get_user_input_value(self, key, REQUEST):
    """
    Try to get a value of the field from the REQUEST
    """
    proxy_field = self.getTemplateField()
    if proxy_field is not None:
      result = proxy_field._get_user_input_value(key, REQUEST)
    else:
      result = ZMIField._get_user_input_value(self, key, REQUEST)
    return result


  #
  # Performance improvement
  #
  def get_tales_expression(self, id):
    field = self
    while True:
      if (id in field.widget.property_names or
          not field.is_delegated(id)):
        tales = field.get_tales(id)
        if tales:
          return TALESMethod(tales._text)
        else:
          return None
      proxied_field = field.getTemplateField()
      if proxied_field.__class__ == ProxyField:
        field = proxied_field
      elif proxied_field is None:
        raise ValueError, "Can't find the template field of %s" % self.id
      else:
        tales = proxied_field.get_tales(id)
        if tales:
          return TALESMethod(tales._text)
        else:
          return None

  def getFieldValue(self, field, id, **kw):
    """
      Return a callable expression and cacheable boolean flag
    """
    try:
      tales_expr = self.get_tales_expression(id)
    except ValueError:
      return None, False
    if tales_expr:
      tales_expr = copyMethod(tales_expr)
      return TALESValue(tales_expr), isCacheable(tales_expr)

    # FIXME: backwards compat hack to make sure overrides dict exists
    if not hasattr(self, 'overrides'):
        self.overrides = {}

    override = self.overrides.get(id, "")
    if override:
      override = copyMethod(override)
      return OverrideValue(override), isCacheable(override)

    # Get a normal value.
    try:
      template_field = self.getRecursiveTemplateField()
      # Old ListBox instance might have default attribute. so we need to check it.
      if checkOriginalGetValue(template_field, id):
        return _USE_ORIGINAL_GET_VALUE_MARKER, True
      value = self.get_recursive_orig_value(id)
    except KeyError:
      # For ListBox and other exceptional fields.
      return self._get_value(id, **kw), False

    field_id = field.id

    value = copyMethod(value)
    cacheable = isCacheable(value)

    if id == 'default' and field_id.startswith('my_'):
      return DefaultValue(field_id, value), cacheable

    # For the 'editable' value, we try to get a default value
    if id == 'editable':
      return EditableValue(value), cacheable

    # Return default value in callable mode
    if callable(value):
      return StaticValue(value), cacheable

    # Return default value in non callable mode
    return_value = StaticValue(value)(field, id, **kw)
    return return_value, isCacheable(return_value)

  security.declareProtected('Access contents information', 'get_value')
  def get_value(self, id, **kw):
    REQUEST = get_request()
    if ((id in self.widget.property_names) or
        (not self.is_delegated(id))):
      return ZMIField.get_value(self, id, **kw)

    field = self
    proxy_field = self.getTemplateField()
    if proxy_field is not None and REQUEST is not None:
      field = REQUEST.get('field__proxyfield_%s_%s' % (self.id, id), self)
      REQUEST.set('field__proxyfield_%s_%s' % (proxy_field.id, id), field)

    # Don't use cache if field is not stored in zodb, or if target field is
    # defined by a TALES
    if self._p_oid is None or self.tales['field_id'] or self.tales['form_id']:
      return self._get_value(id, **kw)

    cache_id = ('ProxyField.get_value',
                self._p_oid,
                field._p_oid,
                id)

    try:
      value = _field_value_cache[cache_id]
    except KeyError:
      # either returns non callable value (ex. "Title")
      # or a FieldValue instance of appropriate class
      value, cacheable = self.getFieldValue(field, id, **kw)
      if cacheable:
        _field_value_cache[cache_id] = value

    if value is _USE_ORIGINAL_GET_VALUE_MARKER:
      return self.getTemplateField().get_value(id, **kw)

    if callable(value):
      return value(field, id, **kw)
    return value

  def _get_value(self, id, **kw):
    proxy_field = self.getTemplateField()
    if proxy_field is not None:
      return proxy_field.get_value(id, **kw)

  def _getCacheId(self):
    return '%s%s' % ('ProxyField', self._p_oid or repr(self))

  def _setTemplateFieldCache(self, field):
    getTransactionalVariable(self)[self._getCacheId()] = field

  def _getTemplateFieldCache(self):
    if self.aq_parent:
      raise KeyError
    return getTransactionalVariable(self)[self._getCacheId()].__of__(self.aq_parent)


#
# get_value exception dict
#
_get_value_exception_dict = {}

def registerOriginalGetValueClassAndArgument(class_, argument_name_list=()):
  """
  if field class has its own get_value implementation and
  must use it rather than ProxyField's one, then register it.

  if argument_name_list is '*' , original get_value is
  applied for all arguments.
  """
  if not isinstance(argument_name_list, (list, tuple)):
    argument_name_list = (argument_name_list,)
  _get_value_exception_dict[class_] = argument_name_list

def checkOriginalGetValue(instance, argument_name):
  """
  if exception data is registered, then return True
  """
  class_ = aq_base(instance).__class__
  argument_name_list = _get_value_exception_dict.get(class_)

  if argument_name_list is None:
    return False
  
  if len(argument_name_list)==1 and argument_name_list[0]=='*':
    return True

  if argument_name in argument_name_list:
    return True
  return False
