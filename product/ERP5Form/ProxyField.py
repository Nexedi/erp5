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

import six
from _thread import get_ident

from AccessControl import allow_class, ClassSecurityInfo
from Acquisition import aq_base
from MethodObject import Method
from zLOG import LOG, WARNING


from Products.Formulator import Widget, Validator
from Products.Formulator.Field import ZMIField
from Products.Formulator.DummyField import fields
from Products.Formulator.Errors import ValidationError
from Products.Formulator.TALESField import TALESMethod
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.ObjectMessage import ObjectMessage
from Products.ERP5Type.Globals import DTMLFile


class BrokenProxyField(Exception):
  pass
allow_class(BrokenProxyField)

class WidgetDelegatedMethod(Method):
  """Method delegated to the proxied field's widget.
  """
  __code__ = func_code = None

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
        self.__code__ = self.func_code = getattr(proxied_method, '__code__', None)
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
                                css_class="form-control",
                                default="",
                                display_width=40,
                                required=1)

  field_id = fields.StringField(
                                'field_id',
                                title='Field ID',
                                description= \
                                  "ID of the field in the master form.",
                                css_class="form-control",
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
    except ValidationError as error:
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
    template_field = self.getTemplateField()
    if template_field is not None:
      template_field = self.getRecursiveTemplateField()

      # Check the surcharged checkboxes
      surcharge_list = []
      for group in template_field.form.get_groups():
        for field in template_field.form.get_fields_in_group(group):
          field_id = field.id
          checkbox_key = "surcharge_%s" % field_id
          if checkbox_key not in REQUEST:
            surcharge_list.append(field_id)

      try:
        # validate the form and get results
        result = template_field.form.validate(REQUEST)
      except ValidationError as err:
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
    except ValidationError as err:
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
        if isinstance(value, six.binary_type):
          # in unicode mode, Formulator UI always uses UTF-8
          value = six.text_type(message, 'utf-8')
        new_result[key] = value
      result = new_result

    changed = []
    for key, value in result.items():
      # XXX Remove old values
      values.pop(key, None)
      # store keys for which we want to notify change
      if key not in values or values[key] != value:
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
          if checkbox_key not in REQUEST:
            surcharge_list.append(field_id)


      try:
        # validate the form and get results
        result = template_field.tales_form.validate(REQUEST)
      except ValidationError as err:
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
    except ValidationError as err:
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
    for key in six.iterkeys(result):
      if key not in self.values:
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
      if checkbox_key not in REQUEST:
        surcharge_list.append(message_key)
        message = REQUEST[message_key]
        if unicode_mode:
          message = six.text_type(message, 'utf-8')
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
    if cache:
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
      try:
        proxy_field = proxy_form._getOb(field_id, None)
      except AttributeError:
        # If the proxy_form is not an ERP5 Form, but a Page Template,
        # accessing _getOb method fails
        proxy_field = None
      if proxy_field is None:
        if form_id_with_skin_folder_name_flag is False:
          # Try to get the field from another field library with a lower
          # priority.
          # This should return no field if the skin folder name is defined in
          # form_id.
          skin_selection_name = object.getCurrentSkinName()
          if skin_selection_name is not None:
            selection_dict = portal_skins._getSelections()
            candidate_folder_id_list = selection_dict[skin_selection_name].split(',')

            for candidate_folder_id in candidate_folder_id_list:
              candidate_folder = portal_skins._getOb(candidate_folder_id, None)
              if candidate_folder is not None:
                proxy_form = candidate_folder._getOb(form_id, None)
                if proxy_form is not None:
                  # proxy_form was retrieved outside of skin magic, fake the
                  # acquisition context skin magic would have produced so it
                  # works the same (ex: for acquired permissions).
                  # The drawback is that the form the field is actually comming
                  # from will be harder to identify, but that's just how skins
                  # work.
                  proxy_field = aq_base(proxy_form).__of__(portal)._getOb(
                    field_id,
                    None,
                  )
                  if proxy_field is not None:
                    break

    if proxy_field is None:
      LOG('ProxyField', WARNING,
          'Could not get a field from a proxy field %s in %s' % \
              (self.id, object.id))
    if cache:
      self._setTemplateFieldCache(proxy_field)
    return proxy_field

  security.declareProtected('Access contents information', 'getRecursiveTemplateField')
  def getRecursiveTemplateField(self, delegated_id=None):
    """
    Return template field of the proxy field.
    If delegated_id is None, the result is not a ProxyField,
    else it is the field that defines the value (possibly an
    intermediate proxy field).
    """
    seen = [aq_base(self)]
    while delegated_id is None or self.is_delegated(delegated_id):
      field = self.getTemplateField()
      if not isinstance(field, ProxyField):
        if field is None:
          error = "Can't find the template field of %r"
          break
        return field
      self = field
      field = aq_base(field)
      if field in seen:
        error = "Infinite loop when searching template field of %r"
        break
      seen.append(field)
    else:
      return self
    raise BrokenProxyField(error % self)

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
       (id in self.values))):
      return self.get_orig_value(id)
    else:
      proxied_field = self.getTemplateField()
      if proxied_field.__class__ == ProxyField:
        return proxied_field.get_recursive_orig_value(id)
      else:
        return proxied_field.get_orig_value(id)

  security.declareProtected('View management screens', 'get_recursive_tales')
  def get_recursive_tales(self, id):
    """
    Get tales expression method for id.
    """
    if id not in self.widget.property_names:
      self = self.getRecursiveTemplateField(id)
    tales = self.get_tales(id)
    if tales:
      return TALESMethod(tales._text)

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

  security.declareProtected('View', 'title')
  def title(self):
    """The title of this field."""
    try:
      return super(ProxyField, self).title()
    except BrokenProxyField:
      return 'broken'

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

  security.declareProtected('Access contents information', 'get_value')
  def get_value(self, id, **kw):
    if id in self.widget.property_names:
      return ZMIField.get_value(self, id, **kw)
    try:
      field = self.getRecursiveTemplateField(id)
      if isinstance(field, ProxyField):
        cls = field.getRecursiveTemplateField().__class__
        try:
          _ProxyField = cls.__ProxyField
        except AttributeError:
          class _ProxyField(cls):
            def __init__(self):
              pass
          cls.__ProxyField = _ProxyField
        tmp_field = _ProxyField()
        for attr in 'values', 'tales', 'overrides':
          setattr(tmp_field, attr, getattr(field, attr).copy())
        field = tmp_field
    except BrokenProxyField:
      # do not break Form.get_field
      if id != 'enabled':
        raise
    else:
      return field.get_value(id, field=self, **kw)

  def _getCacheId(self):
    assert self._p_oid
    return 'ProxyField', self._p_oid

  def _setTemplateFieldCache(self, field):
    getTransactionalVariable()[self._getCacheId()] = field

  def _getTemplateFieldCache(self):
    parent = self.aq_parent
    if parent is not None:
      cache = getTransactionalVariable()[self._getCacheId()]
      if cache is not None:
        return cache.__of__(parent)
    raise KeyError

  security.declareProtected('Change Formulator Fields', 'checkConsistency')
  def checkConsistency(self, fixit=False):
    """Check the proxy field internal data structures are consistent
    """
    object_relative_url = '/'.join(self.getPhysicalPath())[len(self.getPortalObject().getPath()):]
    difference = set(self.tales).difference(self.values)
    if difference:
      if fixit:
        for key in difference:
          if key in self.delegated_list:
            self.values[key] = self.get_recursive_orig_value(key, include=0)
          else:
            self.tales.pop(key)
        # XXX since we are modifying the field, let's take this opportunity
        # to sort delegated_list if it was not sorted.
        self.delegated_list = sorted(self.delegated_list)
        self._p_changed = True

      return [
        ObjectMessage(
             object_relative_url=object_relative_url,
             message="Internal proxy field data structures are inconsistent. "
                     "Differences: {}".format(difference))]
    return []
