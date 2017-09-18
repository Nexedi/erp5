# -*- coding: utf-8 -*-
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

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.ERP5Type.Globals import get_request
from Products.PythonScripts.Utility import allow_class

from Products.PythonScripts.standard import url_quote_plus

from AccessControl import ClassSecurityInfo
from MethodObject import Method

from zLOG import LOG, WARNING, DEBUG, PROBLEM
from Acquisition import aq_base, aq_inner, aq_acquire, aq_chain
from Products.ERP5Type.Globals import DTMLFile

from Products.Formulator.TALESField import TALESMethod
from Products.ERP5Form.Form import StaticValue, TALESValue, OverrideValue, \
        DefaultValue, EditableValue, DefaultCheckBoxValue
from Products.ERP5Form.Form import copyMethod, isCacheable

from Products.CMFCore.Skinnable import SKINDATA
from thread import get_ident

_USE_ORIGINAL_GET_VALUE_MARKER = []

class WidgetDelegatedMethod(Method):
  """Method delegated to the proxied field's widget.
  """
  func_code = None

  def __init__(self, method_id, default=''):
    self._method_id = method_id
    self._default = default

  def __call__(self, instance, *args, **kw):
    field = instance
    proxied_field = field.getRecursiveTemplateField()
    if proxied_field:
      proxied_method = getattr(proxied_field.widget, self._method_id)
      try:
        return proxied_method(field, *args, **kw)
      finally:
        self.func_code = getattr(proxied_method, 'func_code', None)
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
  ]

  form_id = fields.StringField(
                                'form_id',
                                title='Form ID',
                                description= \
                                  "ID of the master form.",
                                default="",
                                display_width=40,
                                required=1)

  field_id = fields.StringField(
                                'field_id',
                                title='Field ID',
                                description= \
                                  "ID of the field in the master form.",
                                default="",
                                display_width=40,
                                required=1)

  # Field API Methods, delegated to the template field widget
  render = WidgetDelegatedMethod('render', default='')
  render_htmlgrid = WidgetDelegatedMethod('render_htmlgrid', default='')
  render_view = WidgetDelegatedMethod('render_view', default='')
  render_pdf = WidgetDelegatedMethod('render_pdf', default='')
  render_css = WidgetDelegatedMethod('render_css', default='')
  render_dict = WidgetDelegatedMethod('render_dict', default=None)
  render_odf = WidgetDelegatedMethod('render_odf', default='')
  render_odt = WidgetDelegatedMethod('render_odt', default=None)
  render_odt_view = WidgetDelegatedMethod('render_odt_view', default=None)
  render_odt_variable = WidgetDelegatedMethod('render_odt_variable',
                                              default=None)
  render_odg = WidgetDelegatedMethod('render_odg', default=None)
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
  delegated_list = tuple()
  delegated_message_list = tuple()

  # methods screen
  security.declareProtected('View management screens',
                            'manage_main')
  manage_main = DTMLFile('dtml/proxyFieldEdit', globals())

  # tales screen
  security.declareProtected('View management screens',
                            'manage_talesForm')
  manage_talesForm = DTMLFile('dtml/proxyFieldTales', globals())

  # messages screen
  security.declareProtected('View management screens', 'manage_messagesForm')
  manage_messagesForm = DTMLFile('dtml/proxyFieldMessages', globals())

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

  def manage_edit_surcharged_xmlrpc(self, mapping):
    """Edit surcharged properties
    This method is similar to manage_edit_xmlrpc, and it marks the properties
    as not delegated.
    """
    self._surcharged_edit(mapping, mapping.keys())

  def manage_tales_surcharged_xmlrpc(self, mapping):
    """Edit surcharged TALES
    This method is similar to manage_tales_xmlrpc, and it marks the TALES
    properties as not delegated.
    """
    self._surcharged_tales(mapping, mapping.keys())


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
        if key in self.tales:
          self.tales.pop(key)

    # now do actual update of values
    values.update(result)
    self.values = values
    self.delegated_list = sorted(surcharge_list)

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
        if key in self.values:
          self.values.pop(key)

    # now do actual update of values
    tales.update(result)
    self.tales = tales
    self.delegated_list = sorted(surcharge_list)
    # Put a default value on not delegated parameter
    for key in result.keys():
      if not self.values.has_key(key):
        self.values[key] = self.get_recursive_orig_value(key, include=0)

  security.declareProtected('Change Formulator Fields', 'manage_messages')
  def manage_messages(self, REQUEST):
    """Change message texts.
    """
    surcharge_list = []
    messages = self.message_values
    unicode_mode = self.get_unicode_mode()
    for message_key in self.get_error_names():
      checkbox_key = "surcharge_%s" % message_key
      if not REQUEST.has_key(checkbox_key):
        surcharge_list.append(message_key)
        message = REQUEST[message_key]
        if unicode_mode:
          message = unicode(message, 'UTF-8')
        messages[message_key] = message
      else:
        if message_key in messages:
          messages.pop(message_key)
    self.message_values = messages
    self.delegated_message_list = sorted(surcharge_list)
    if REQUEST:
      message="Content changed."
      return self.manage_messagesForm(self,REQUEST,
                                      manage_tabs_message=message)

  security.declareProtected('View management screens', 'get_error_message')
  def get_error_message(self, name):
    if not self.is_message_delegated(name):
      try:
        return self.message_values[name]
      except KeyError:
        if name in self.validator.message_names:
          return getattr(self.validator, name)
        else:
          return "Unknown error: %s" % name
    else:
      return self.getTemplateField().get_error_message(name)

  security.declareProtected('View management screens', 'get_error_names')
  def get_error_names(self):
    """Get error messages.
    """
    return self.getTemplateField().get_error_names()

  security.declareProtected('Access contents information', 'getTemplateField')
  def getTemplateField(self, cache=True):
    """
    Return template field of the proxy field.
    """
    if cache is True:
      tales = self.tales
      if self._p_oid is None or tales['field_id'] or tales['form_id']:
        cache = False
      else:
        try:
          return self._getTemplateFieldCache()
        except KeyError:
          pass

    portal = self.getPortalObject()
    portal_skins = portal.portal_skins
    form = self.aq_parent
    object = form.aq_parent

    form_id = self.get_value('form_id')
    proxy_field = None
    form_id_with_skin_folder_name_flag = False
    if '/' in form_id:
      # If a / is in the form_id, it means that skin_folder is explicitly
      # defined. If so, prevent acquisition to get the form.
      form_id_with_skin_folder_name_flag = True
      proxy_form = aq_base(portal_skins).unrestrictedTraverse(form_id, None)
      if proxy_form is not None:
        proxy_form = portal_skins.unrestrictedTraverse(form_id)
    else:
      proxy_form = getattr(object, form_id, None)

    if (proxy_form is not None):
      field_id = self.get_value('field_id')
      proxy_field = proxy_form._getOb(field_id, None)
      if proxy_field is None:
        if form_id_with_skin_folder_name_flag is False:
          # Try to get the field from another field library with a lower
          # priority.
          # This should return no field if the skin folder name is defined in
          # form_id.
          skin_info = SKINDATA.get(get_ident())

          if skin_info is not None:
            _, skin_selection_name, ignore, resolve = skin_info

            selection_dict = portal_skins._getSelections()
            candidate_folder_id_list = selection_dict[skin_selection_name].split(',')

            for candidate_folder_id in candidate_folder_id_list:
              candidate_folder = portal_skins._getOb(candidate_folder_id, None)
              if candidate_folder is not None:
                proxy_form = candidate_folder._getOb(form_id, None)
                if proxy_form is not None:
                  proxy_field = proxy_form._getOb(field_id, None)
                  if proxy_field is not None:
                    break

    if proxy_field is None:
      LOG('ProxyField', WARNING,
          'Could not get a field from a proxy field %s in %s' % \
              (self.id, object.id))
    if cache is True:
      self._setTemplateFieldCache(proxy_field)
    return proxy_field

  security.declareProtected('Access contents information', 'getRecursiveTemplateField')
  def getRecursiveTemplateField(self):
    """
    Return template field of the proxy field.
    This result must not be a ProxyField.
    """
    field = self
    chain = []
    while True:
      template_field = field.getTemplateField()
      if template_field.__class__ != ProxyField:
        break
      template_field_base = aq_base(template_field)
      if template_field_base in chain:
        LOG('ProxyField', WARNING, 'Infinite loop detected in %s.' %
            '/'.join(self.getPhysicalPath()))
        return
      chain.append(template_field_base)
      field = template_field
    return template_field

  def _get_sub_form(self, field=None):
    if field is None:
      field = self
    return self.getTemplateField()._get_sub_form(field=field)

  security.declareProtected('Access contents information',
                            'is_delegated')
  def is_delegated(self, id):
    """
    Return true if we get the value from the proxied field.
    No, if we surcharged the value on the proxy field.
    """
    return id not in self.delegated_list

  security.declareProtected('Access contents information',
                            'is_message_delegated')
  def is_message_delegated(self, id):
    """
    Return true if we get the message from the proxied field.
    No, if we surcharged the message on the proxy field.
    """
    return id not in self.delegated_message_list

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
      if proxied_field is None:
        raise AttributeError('The proxy field %r cannot find a template field' % self)
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

  security.declareProtected('Edit target', 'manage_edit_target')
  def manage_edit_target(self, RESPONSE):
    """
    Edit target field of this proxy
    """
    proxy_field = self.getTemplateField()
    if proxy_field:
      RESPONSE.redirect(proxy_field.absolute_url() + "/manage_main")
    else:
      # FIXME: should show some error message
      # ("form_id and field_id don't define a valid template")
      pass

  security.declareProtected('Edit target', 'manage_tales_target')
  def manage_tales_target(self, RESPONSE):
    """
    Edit target field of this proxy
    """
    proxy_field = self.getTemplateField()
    if proxy_field:
      RESPONSE.redirect(proxy_field.absolute_url() + "/manage_talesForm")
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

  security.declareProtected('Access contents information', 'get_orig_value')
  def get_orig_value(self, id):
    """Get value for id; don't do any override calculation.
    """
    if id not in self.widget.property_names and self.is_delegated(id):
      return self.getTemplateField().get_orig_value(id)
    return ZMIField.get_orig_value(self, id)

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

  security.declareProtected('Access contents information', 'getFieldValue')
  def getFieldValue(self, field, id, **kw):
    """
      Return a callable expression and cacheable boolean flag
    """
    # Some field types have their own get_value implementation,
    # then we must use it always. This check must be done at first.
    template_field = self.getRecursiveTemplateField()
    # Old ListBox instance might have default attribute. so we need to check it.
    if checkOriginalGetValue(template_field, id):
      return _USE_ORIGINAL_GET_VALUE_MARKER, True

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
      value = self.get_recursive_orig_value(id)
    except KeyError:
      # For ListBox and other exceptional fields.
      return self._get_value(id, **kw), False

    field_id = field.id

    value = copyMethod(value)
    cacheable = isCacheable(value)

    if id == 'default' and (field_id.startswith('my_') or
                            field_id.startswith('listbox_')):
      # XXX far from object-oriented programming
      if template_field.meta_type == 'CheckBoxField':
        return DefaultCheckBoxValue(field_id, value), cacheable
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
    if id in self.widget.property_names:
      return ZMIField.get_value(self, id, **kw)
    if not self.is_delegated(id):
      original_template_field = self.getRecursiveTemplateField()
      function = getOriginalGetValueFunction(original_template_field, id)
      if function is not None:
        return function(self, id, **kw)
      else:
        return ZMIField.get_value(self, id, **kw)

    field = self
    proxy_field = self.getTemplateField()
    REQUEST = kw.get('REQUEST', get_request())
    if proxy_field is not None and REQUEST is not None:
      field = REQUEST.get(
        'field__proxyfield_%s_%s_%s' % (self.id, self._p_oid, id),
        self)
      REQUEST.set(
        'field__proxyfield_%s_%s_%s' % (proxy_field.id, proxy_field._p_oid, id),
        field)

    # Don't use cache if field is not stored in zodb, or if target field is
    # defined by a TALES
    if self._p_oid is None or self.tales['field_id'] or self.tales['form_id']:
      return self._get_value(id, **kw)
      # XXX: Are these disabled?
      proxy_field = self.getTemplateField(cache=False)
      if proxy_field is not None:
        return proxy_field.get_value(id, **kw)
      else:
        return None

    cache_id = ('ProxyField.get_value',
                self._p_oid,
                field._p_oid,
                id)

    from Products.ERP5Form.Form import field_value_cache
    try:
      value = field_value_cache[cache_id]
    except KeyError:
      # either returns non callable value (ex. "Title")
      # or a FieldValue instance of appropriate class
      value, cacheable = self.getFieldValue(field, id, **kw)
      if cacheable:
        field_value_cache[cache_id] = value

    if value is _USE_ORIGINAL_GET_VALUE_MARKER:
      return proxy_field.get_value(id, **kw)

    if callable(value):
      return value(field, id, **kw)
    return value

  def _get_value(self, id, **kw):
    proxy_field = self.getTemplateField(cache=False)
    if proxy_field is not None:
      return proxy_field.get_value(id, **kw)

  def _getCacheId(self):
    return '%s%s' % ('ProxyField', self._p_oid or repr(self))

  def _setTemplateFieldCache(self, field):
    getTransactionalVariable()[self._getCacheId()] = field

  def _getTemplateFieldCache(self):
    parent = self.aq_parent
    if parent is not None:
      cache = getTransactionalVariable()[self._getCacheId()]
      if cache is not None:
        return cache.__of__(parent)
    raise KeyError


#
# get_value exception dict
#
_get_value_exception_dict = {}

def registerOriginalGetValueClassAndArgument(class_, argument_name_list=(), get_value_function=None):
  """
  if field class has its own get_value implementation and
  must use it rather than ProxyField's one, then register it.

  if argument_name_list is '*' , original get_value is
  applied for all arguments.
  """
  if not isinstance(argument_name_list, (list, tuple)):
    argument_name_list = (argument_name_list,)
  if get_value_function is None:
    get_value_function = ZMIField.get_value
  _get_value_exception_dict[class_] = {'argument_name_list':argument_name_list,
                                       'get_value_function':get_value_function}

def checkOriginalGetValue(instance, argument_name):
  """
  if exception data is registered, then return True
  """
  class_ = aq_base(instance).__class__
  dict_ = _get_value_exception_dict.get(class_, {})
  argument_name_list = dict_.get('argument_name_list')

  if argument_name_list is None:
    return False

  if len(argument_name_list)==1 and argument_name_list[0]=='*':
    return True

  if argument_name in argument_name_list:
    return True
  return False

def getOriginalGetValueFunction(instance, argument_name):
  class_ = aq_base(instance).__class__
  dict_ = _get_value_exception_dict.get(class_, {})
  return dict_.get('get_value_function')
