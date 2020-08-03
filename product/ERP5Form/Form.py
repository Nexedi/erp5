# -*- coding: utf-8 -*-
#############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Products.Formulator.Form import BasicForm
from Products.Formulator.DummyField import fields

from urllib import quote
from Products.ERP5Type.Globals import DTMLFile, get_request
from AccessControl import Unauthorized
from ZODB.POSException import ConflictError
from zExceptions import Redirect
from Acquisition import aq_base
from Products.PageTemplates.Expressions import SecureModuleImporter

from Products.ERP5Type.PsycoWrapper import psyco

class FieldValueCacheDict(dict):
  _last_sync = -1

  def clear(self):
    super(FieldValueCacheDict, self).clear()

    from Products.ERP5.ERP5Site import getSite
    try:
      portal = getSite()
    except IndexError:
      pass
    else:
      portal.newCacheCookie('form_field_value_cache')
      self._last_sync = portal.getCacheCookie('form_field_value_cache')

  def __getitem__(self, cache_id):
    from Products.ERP5.ERP5Site import getSite
    try:
      portal = getSite()
    except IndexError:
      pass
    else:
      cookie = portal.getCacheCookie('form_field_value_cache')
      if cookie != self._last_sync:
        LOG("ERP5Form.Form", 0, "Resetting form field value cache")
        self._last_sync = cookie
        super(FieldValueCacheDict, self).clear()
        raise KeyError('Field cache is outdated and has been reset')

    return super(FieldValueCacheDict, self).__getitem__(cache_id)

field_value_cache = FieldValueCacheDict()

# Patch the fiels methods to provide improved namespace handling

from Products.Formulator.Field import Field
from Products.Formulator.MethodField import Method, BoundMethod
from Products.Formulator.TALESField import TALESMethod

from zLOG import LOG, PROBLEM


def isCacheable(value):
  value = aq_base(value)
  if type(value) is BoundMethod:
    return False

  jar = getattr(value, '_p_jar', None)
  if jar is not None:
    return False

  dic = getattr(value, '__dict__', None)
  if dic is not None:
    for i in dic.values():
      jar = getattr(i, '_p_jar', None)
      if jar is not None:
        return False
  return True


def copyMethod(value):
    if type(aq_base(value)) is Method:
      value = Method(value.method_name)
    elif type(aq_base(value)) is TALESMethod:
      value = TALESMethod(value._text)
    return value

def getFieldDict(field, value_type):
    result = {}
    if field.meta_type=='ProxyField':
        if value_type=='values':
            get_method = getattr(field, 'get_recursive_orig_value')
        elif value_type=='tales':
            get_method = getattr(field, 'get_recursive_tales')
        else:
            raise ValueError, 'value_type must be values or tales'
        template_field = field.getRecursiveTemplateField()
        for ui_field_id in template_field.form.fields.keys():
            result[ui_field_id] = get_method(ui_field_id)
    else:
        if value_type=='values':
            get_method = getattr(field, 'get_orig_value')
        elif value_type=='tales':
            get_method = getattr(field, 'get_tales')
        else:
            raise ValueError, 'value_type must be values or tales'
        for ui_field_id in field.form.fields.keys():
            result[ui_field_id] = get_method(ui_field_id)
    return result


class StaticValue:
  """
    Encapsulated a static value in a class
    (quite heavy, would be faster to store the
    value as is)
  """
  def __init__(self, value):
    self.value = value

  def __call__(self, field, id, **kw):
    return self.returnValue(field, id, self.value)

  def returnValue(self, field, id, value):
    # if normal value is a callable itself, wrap it
    if callable(value):
      value = value.__of__(field)
      #value=value() # Mising call ??? XXX Make sure compatible with listbox methods

    if id == 'default':
      # We make sure we convert values to empty strings
      # for most fields (so that we do not get a 'value'
      # message on screen)
      # This can be overriden by using TALES in the field
      if value is None: value = ''

    return value

class TALESValue(StaticValue):
  def __init__(self, tales_expr):
    self.tales_expr = tales_expr

  def __call__(self, field, id, **kw):
    REQUEST = kw.get('REQUEST', get_request())
    if REQUEST is not None:
      # Proxyfield stores the "real" field in the request. Look if the
      # corresponding field exists in request, and use it as field in the
      # TALES context
      field = REQUEST.get(
        'field__proxyfield_%s_%s_%s' % (field.id, field._p_oid, id),
        field)

    kw['field'] = field

    form = field.aq_parent # XXX (JPS) form for default is wrong apparently in listbox - double check
    obj = getattr(form, 'aq_parent', None)
    if obj is not None:
        container = obj.aq_inner.aq_parent
    else:
        container = None

    kw['form'] = form
    kw['request'] = REQUEST
    kw['here'] = obj
    kw['context'] = obj
    kw['modules'] = SecureModuleImporter
    kw['container'] = container
    try :
      kw['preferences'] = obj.getPortalObject().portal_preferences
    except AttributeError :
      LOG('ERP5Form', PROBLEM,
          'portal_preferences not put in TALES context (not installed?)')
    # This allows to pass some pointer to the local object
    # through the REQUEST parameter. Not very clean.
    # Used by ListBox to render different items in a list
    if kw.get('cell') is None:
      request = kw.get('REQUEST')
      if request is not None:
        if getattr(request, 'cell', None) is not None:
          kw['cell'] = request.cell
        else:
          kw['cell'] = request
        if 'cell_index' not in kw and\
            getattr(request, 'cell_index', None) is not None:
          kw['cell_index'] = request.cell_index
      elif getattr(REQUEST, 'cell', None) is not None:
        kw['cell'] = REQUEST.cell
    if 'cell_index' not in kw and \
      getattr(REQUEST, 'cell_index', None) is not None:
        kw['cell_index'] = REQUEST.cell_index
    # on Zope 2.12, only path expressions can access the CONTEXTS name
    # but ERP5 has many python expressions that try to access CONTEXTS, so
    # we try to keep backward compatibility
    if self.tales_expr._text.startswith("python:"):
      kw['CONTEXTS'] = kw
    try:
      value = self.tales_expr.__of__(field)(**kw)
    except (ConflictError, RuntimeError, Redirect):
      raise
    except:
      # We add this safety exception to make sure we always get
      # something reasonable rather than generate plenty of errors
      LOG('ERP5Form', PROBLEM,
          'Field.get_value %r [%s], exception on tales_expr: ' %
          (field, id), error=True)
      # field may be ProxyField
      # here we avoid calling field.get_recursive_orig_value
      # on all fields because it can be acquired from another
      # field in context. ie, from a listbox field.
      # So, test condition on meta_type attribute to avoid
      # non desirable side effects.
      if field.meta_type == 'ProxyField':
        value = field.get_recursive_orig_value(id)
      else:
        value = field.get_orig_value(id)

    return self.returnValue(field, id, value)

class OverrideValue(StaticValue):
  def __init__(self, override):
    self.override = override

  def __call__(self, field, id, **kw):
    return self.returnValue(field, id, self.override.__of__(field)())

class DefaultValue(StaticValue):
  def __init__(self, field_id, value):
    self.key = field_id.split('_', 1)[1]
    self.value = value

  def __call__(self, field, id, **kw):
    REQUEST = kw.get('REQUEST', None) or get_request()
    try:
      form = field.aq_parent
      ob = REQUEST.get('cell', getattr(form, 'aq_parent', None))
      value = self.value
      try:
        if value not in (None, ''):
          # If a default value is defined on the field, it has precedence
          value = ob.getProperty(self.key, d=value)
        else:
          # else we should give a chance to the accessor to provide
          # a default value (including None)
          value = ob.getProperty(self.key)
      except Unauthorized:
        value = ob.getProperty(self.key, d=value, checked_permission='View')
        if REQUEST is not None:
          REQUEST.set('read_only_%s' % self.key, 1)
    except (KeyError, AttributeError):
      value = None
    return self.returnValue(field, id, value)

class DefaultCheckBoxValue(DefaultValue):
  def __call__(self, field, id, **kw):
    try:
      form = field.aq_parent
      ob = getattr(form, 'aq_parent', None)
      value = self.value
      try:
        value = ob.getProperty(self.key)
      except Unauthorized:
        value = ob.getProperty(self.key, d=value, checked_permission='View')
        REQUEST = kw.get('REQUEST', get_request())
        if REQUEST is not None:
          REQUEST.set('read_only_%s' % self.key, 1)
    except (KeyError, AttributeError):
      value = None
    return self.returnValue(field, id, value)

class EditableValue(StaticValue):

  def __call__(self, field, id, **kw):
    # By default, pages are editable and
    # fields are editable if they are set to editable mode
    # However, if the REQUEST defines editable_mode to 0
    # then all fields become read only.
    # This is useful to render ERP5 content as in a web site (ECommerce)
    # editable_mode should be set for example by the page template
    # which defines the current layout
    REQUEST = kw.get('REQUEST', get_request())
    if REQUEST is not None:
      if not REQUEST.get('editable_mode', 1):
        return 0
    return self.value

def getFieldValue(self, field, id, **kw):
  """
    Return a callable expression and cacheable boolean flag
  """
  tales_expr = self.tales.get(id, "")
  if tales_expr:
    # TALESMethod is persistent object, so that we cannot cache original one.
    # Becase if connection which original talesmethod uses is closed,
    # RuntimeError must occurs in __setstate__.
    tales_expr = copyMethod(tales_expr)
    return TALESValue(tales_expr), isCacheable(tales_expr)

  override = self.overrides.get(id, "")
  if override:
    override = copyMethod(override)
    return OverrideValue(override), isCacheable(override)

  # Get a normal value.
  value = self.get_orig_value(id)
  value = copyMethod(value)
  cacheable = isCacheable(value)

  field_id = field.id

  if id == 'default' and (field_id.startswith('my_') or
                          field_id.startswith('listbox_')):
    if field.meta_type == 'ProxyField' and \
        field.getRecursiveTemplateField().meta_type == 'CheckBoxField' or \
        self.meta_type == 'CheckBoxField':
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

def get_value(self, id, REQUEST=None, **kw):
  if REQUEST is None:
    REQUEST = get_request()
  if REQUEST is not None:
    field = REQUEST.get(
      'field__proxyfield_%s_%s_%s' % (self.id, self._p_oid, id),
      self)
  else:
    field = self

  cache_id = ('Form.get_value',
              self._p_oid,
              field._p_oid,
              id)

  try:
    value = field_value_cache[cache_id]
  except KeyError:
    # either returns non callable value (ex. "Title")
    # or a FieldValue instance of appropriate class
    value, cacheable = getFieldValue(self, field, id, **kw)
    # Do not cache if the field is not stored in zodb,
    # because such field must be used for editing field in ZMI
    # and caching sometimes break these field settings at initialization.
    # As the result, we would see broken field editing screen in ZMI.
    if cacheable and self._p_oid:
      field_value_cache[cache_id] = value

  if callable(value):
    return value(field, id, REQUEST=REQUEST, **kw)
  return value

psyco.bind(get_value)

def om_icons(self):
    """Return a list of icon URLs to be displayed by an ObjectManager"""
    icons = ({'path': self.icon,
              'alt': self.meta_type, 'title': self.meta_type},)
    return icons


def _get_default(self, key, value, REQUEST):
    if value is not None:
        return value
    try:
        value = self._get_user_input_value(key, REQUEST)
    except (KeyError, AttributeError):
        # fall back on default
        return self.get_value('default', REQUEST=REQUEST) # It was missing on Formulator

    # if we enter a string value while the field expects unicode,
    # convert to unicode first
    # this solves a problem when re-rendering a sticky form with
    # values from request
    if (self.has_value('unicode') and self.get_value('unicode') and
        type(value) == type('')):
        return unicode(value, self.get_form_encoding())
    else:
        return value


# Dynamic Patch
Field.get_value = get_value
Field._get_default = _get_default
Field.om_icons = om_icons

# Constructors

manage_addForm = DTMLFile("dtml/form_add", globals())

def addERP5Form(self, id, title="", REQUEST=None):
    """Add form to folder.
    id     -- the id of the new form to add
    title  -- the title of the form to add
    Result -- empty string
    """
    # add actual object
    type_info = self.getPortalObject().portal_types.getTypeInfo('ERP5 Form')
    type_info.constructInstance(container=self, id=id, title=title)
    # respond to the add_and_edit button if necessary
    add_and_edit(self, id, REQUEST)
    return ''

def add_and_edit(self, id, REQUEST):
    """Helper method to point to the object's management screen if
    'Add and Edit' button is pressed.
    id -- id of the object we just added
    """
    if REQUEST is None:
        return
    try:
        u = self.DestinationURL()
    except AttributeError:
        u = REQUEST['URL1']
    if REQUEST['submit'] == " Add and Edit ":
        u = "%s/%s" % (u, quote(id))
    REQUEST.RESPONSE.redirect(u+'/manage_main')

def initializeForm(field_registry, form_class=None):
    """Sets up ZMIForm with fields from field_registry.
    """
    if form_class is None: form_class = ERP5Form

    meta_types = []
    for meta_type, field in field_registry.get_field_classes().items():
        # don't set up in form if this is a field for internal use only
        if field.internal_field:
            continue

        # set up individual add dictionaries for meta_types
        dict = { 'name': field.meta_type,
                 'permission': 'Add Formulator Fields',
                 'action':
                 'manage_addProduct/Formulator/manage_add%sForm' % meta_type }
        meta_types.append(dict)
        # set up add method
        setattr(form_class,
                'manage_add%sForm' % meta_type,
                DTMLFile('dtml/fieldAdd', globals(), fieldname=meta_type))

    # set up meta_types that can be added to form
    form_class._meta_types = tuple(meta_types)

    # set up settings form
    form_class.settings_form._realize_fields()

# Special Settings

def create_settings_form():
    """Create settings form for ZMIForm.
    """
    form = BasicForm('manage_settings')

    title = fields.StringField('title',
                               title="Title",
                               required=0,
                               default="")
    description = fields.TextAreaField('description',
                               title="Description",
                               required=0,
                               default="")
    row_length = fields.IntegerField('row_length',
                                     title='Number of groups in row (in order tab)',
                                     required=1,
                                     default=4)
    name = fields.StringField('name',
                              title="Form name",
                              required=0,
                              default="")
    pt = fields.StringField('pt',
                              title="Page Template",
                              required=0,
                              default="")
    action = fields.StringField('action',
                                title='Form action',
                                required=0,
                                default="")
    action_title = fields.StringField('action_title',
                               title="Action Title",
                               required=0,
                               default="")
    update_action = fields.StringField('update_action',
                                title='Form update action',
                                required=0,
                                default="")
    update_action_title = fields.StringField('update_action_title',
                               title="Update Action Title",
                               required=0,
                               default="")
    method = fields.ListField('method',
                              title='Form method',
                              items=[('POST', 'POST'),
                                     ('GET', 'GET')],
                              required=1,
                              size=1,
                              default='POST')
    enctype = fields.ListField('enctype',
                               title='Form enctype',
                               items=[('No enctype', ""),
                                      ('application/x-www-form-urlencoded',
                                       'application/x-www-form-urlencoded'),
                                      ('multipart/form-data',
                                       'multipart/form-data')],
                               required=0,
                               size=1,
                               default=None)
    encoding = fields.StringField('encoding',
                                  title='Encoding of pages the form is in',
                                  default="UTF-8",
                                  required=1)
    stored_encoding = fields.StringField('stored_encoding',
                                      title='Encoding of form properties',
                                      default='UTF-8',
                                      required=1)
    unicode_mode = fields.CheckBoxField('unicode_mode',
                                        title='Form properties are unicode',
                                        default=0,
                                        required=0)
    edit_order = fields.LinesField('edit_order',
                                   title='Setters for these properties should be'
                                   '<br /> called by edit() in the defined order')

    form.add_fields([title, description, row_length, name, pt, action, action_title, update_action, update_action_title,
                     method, enctype, encoding, stored_encoding, unicode_mode, edit_order])
    return form

# utility function
def get_field_meta_type_and_proxy_flag(field):
    if field.meta_type=='ProxyField':
        try:
            return field.getRecursiveTemplateField().meta_type, True
        except AttributeError:
            raise AttributeError, 'The proxy target of %s.%s field does not '\
                  'exists. Please check the field setting.' % \
                  (field.aq_parent.id, field.getId())
    else:
        return field.meta_type, False


# More optimizations
#psyco.bind(ERP5Field)
# XXX Not useful, as we patch those methods in FormulatorPatch
psyco.bind(Field.render)
psyco.bind(Field._render_helper)
psyco.bind(Field.get_value)

#from Products.PageTemplates.PageTemplate import PageTemplate
#from TAL import TALInterpreter
#psyco.bind(TALInterpreter.TALInterpreter)
#psyco.bind(TALInterpreter.TALInterpreter.interpret)
#psyco.bind(PageTemplate.pt_render)
#psyco.bind(PageTemplate.pt_macros)

#from Products.CMFCore.ActionsTool import ActionsTool
#psyco.bind(ActionsTool.listFilteredActionsFor)

