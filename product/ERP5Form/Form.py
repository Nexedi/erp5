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
import hashlib

from copy import deepcopy

from Products.Formulator.Form import BasicForm, ZMIForm
from Products.Formulator.Errors import FormValidationError, ValidationError
from Products.Formulator.DummyField import fields
from Products.Formulator.XMLToForm import XMLToForm
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.CMFCore.utils import _checkPermission, getToolByName
from Products.CMFCore.exceptions import AccessControl_Unauthorized
from Products.ERP5Type import PropertySheet, Permissions

from urllib import quote
from Products.ERP5Type.Globals import DTMLFile, get_request
from AccessControl import Unauthorized, ClassSecurityInfo
from DateTime import DateTime
from ZODB.POSException import ConflictError
from zExceptions import Redirect
from Acquisition import aq_base
from Products.PageTemplates.Expressions import SecureModuleImporter
from zExceptions import Forbidden

from Products.ERP5Type.PsycoWrapper import psyco
from Products.ERP5Type.Base import Base

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
    id = self._setObject(id, ERP5Form(id, title))
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


from OFS.Cache import filterCacheTab

class ERP5Form(Base, ZMIForm, ZopePageTemplate):
    """
        A Formulator form with a built-in rendering parameter based
        on page templates or DTML.
    """
    meta_type = "ERP5 Form"
    portal_type = "ERP5 Form"
    icon = "www/Form.png"

    # Declarative Security
    security = ClassSecurityInfo()

    # Tabs in ZMI
    manage_options = (ZMIForm.manage_options[:5] +
                      ({'label':'Proxify', 'action':'formProxify'},
                       {'label':'UnProxify', 'action':'formUnProxify'},
                       {'label':'RelatedProxy',
                         'action':'formShowRelatedProxyFields'},
                       {'label': 'Cache',
                        'action': 'ZCacheable_manage',
                        'filter': filterCacheTab,
                        'help': ('OFSP', 'Cacheable-properties.stx')}
                      )+
                      ZMIForm.manage_options[5:])

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.Folder
                      , PropertySheet.CategoryCore
                      )

    # Constructors
    constructors =   (manage_addForm, addERP5Form)

    # This is a patched dtml formOrder
    security.declareProtected('View management screens', 'formOrder')
    formOrder = DTMLFile('dtml/formOrder', globals())

    # Proxify form
    security.declareProtected('View management screens', 'formProxify')
    formProxify = DTMLFile('dtml/formProxify', globals())

    # Proxify form
    security.declareProtected('View management screens', 'formUnProxify')
    formUnProxify = DTMLFile('dtml/formUnProxify', globals())

    # Related Proxy Fields
    security.declareProtected('View management screens',
        'formShowRelatedProxyFields')
    formShowRelatedProxyFields = DTMLFile('dtml/formShowRelatedProxyFields',
        globals())

    # Default Attributes
    pt = 'form_view'
    action_title = ''
    update_action = ''
    update_action_title = ''
    edit_order = []

    # Special Settings
    settings_form = create_settings_form()

    manage_main = ZMIForm.manage_main
    objectIds = ZMIForm.objectIds
    objectItems = ZMIForm.objectItems
    objectValues = ZMIForm.objectValues

    # If content_type is not text/html ZopePageTemplate will check that the
    # source is well formed XML, but this does not really applies to Forms,
    # they don't have source. By setting content_type here we make sure we
    # don't get ERP5Type's Base default content_type.
    content_type = ZopePageTemplate.content_type

    def __init__(self, id, title, unicode_mode=0, encoding='UTF-8',
                 stored_encoding='UTF-8'):
        """Initialize form.
        id    -- id of form
        title -- the title of the form
        """
        ZMIForm.inheritedAttribute('__init__')(self, "", "POST", "", id,
                                               encoding, stored_encoding,
                                               unicode_mode)
        self.id = id
        self.title = title
        self.row_length = 4
        self.group_list = ["left", "right", "center", "bottom", "hidden"]
        groups = {}
        for group in self.group_list:
          groups[group] = []
        self.groups = groups

    # Proxy method to PageTemplate
    def __call__(self, *args, **kwargs):
        # Security
        #
        # The minimal action consists in checking that
        # we have View permission on the current object
        # before rendering a form. Otherwise, object with
        # AccessContentInformation can be viewed by invoking
        # a form directly.
        #
        # What would be better is to prevent calling certain
        # forms to render objects. This can not be done
        # through actions since we are using sometimes forms
        # to render the results of a report dialog form.
        # An a appropriate solutions could consist in adding
        # a permission field to the form. Another solutions
        # is the use of REFERER in the rendering process.
        #
        # Both solutions are not perfect if the goal is, for
        # example, to prevent displaying private information of
        # staff. The only real solution is to use a special
        # permission (ex. AccessPrivateInformation) for those
        # properties which are sensitive.
        kwargs.setdefault('args', args)
        key_prefix = kwargs.pop('key_prefix', None)
        obj = getattr(self, 'aq_parent', None)
        if obj is not None:
          container = obj.aq_inner.aq_parent
          if not _checkPermission(Permissions.View, obj):
            raise AccessControl_Unauthorized('This document is not authorized for view.')
        else:
          container = None
        pt = getattr(self,self.pt)
        extra_context = dict( container=container,
                              template=self,
                              form=self,
                              key_prefix=key_prefix,
                              options=kwargs,
                              here=obj,
                              context=obj,
                            )
        return pt.pt_render(extra_context=extra_context)

    def _exec(self, bound_names, args, kw):
        pt = getattr(self,self.pt)
        return pt._exec(self, bound_names, args, kw)

    def manage_renameObject(self, id, new_id, REQUEST=None):
      # overriden to keep the order of a field after rename
      groups = deepcopy(self.groups)
      ret = ZMIForm.manage_renameObject(self, id, new_id, REQUEST=REQUEST)
      for group_id, field_id_list in groups.items():
        if id in field_id_list:
          index = field_id_list.index(id)
          field_id_list.pop(index)
          field_id_list.insert(index, new_id)
          groups[group_id] = field_id_list
      self.groups = groups
      return ret

    # Utilities
    security.declareProtected('View', 'ErrorFields')
    def ErrorFields(self, validation_errors):
        """
            Create a dictionnary of validation_errors
            with field id as key
        """
        ef = {}
        for e in validation_errors.errors:
            ef[e.field_id] = e
        return ef

    def om_icons(self):
        """Return a list of icon URLs to be displayed by an ObjectManager"""
        icons = ({'path': 'misc_/ERP5Form/Form.png',
                  'alt': self.meta_type, 'title': self.meta_type},)
        return icons

    # Pached validate_all to support ListBox validation
    security.declareProtected('View', 'validate_all')
    def validate_all(self, REQUEST, key_prefix=None):
        """Validate all enabled fields in this form, catch any ValidationErrors
        if they occur and raise a FormValidationError in the end if any
        Validation Errors occured.
        """
        result = {}
        errors = []
        for group in self.get_groups():
            if group.lower() == 'hidden':
                continue
            for field in self.get_fields_in_group(group):
                # skip any field we don't need to validate
                if not field.need_validate(REQUEST, key_prefix=key_prefix):
                    continue
                if not (field.get_value('editable',REQUEST=REQUEST)):
                    continue
                try:
                    value = field.validate(REQUEST, key_prefix=key_prefix)
                    # store under id
                    result[field.id] = value
                    # store as alternate name as well if necessary
                    alternate_name = field.get_value('alternate_name')
                    if alternate_name:
                        result[alternate_name] = value
                except FormValidationError, e: # XXX JPS Patch for listbox
                    errors.extend(e.errors)
                    result.update(e.result)
                except ValidationError, err:
                    errors.append(err)
                except KeyError, err:
                    LOG('ERP5Form/Form.py:validate_all', 0, 'KeyError : %s' % (err, ))

        if len(errors) > 0:
            raise FormValidationError(errors, result)
        return result

    security.declareProtected('View', 'hash_validated_data')
    def hash_validated_data(self, validated_data):
      return hashlib.sha256(
        "".join(
          str(validated_data[key])
          for key in sorted(validated_data.keys())
          if isinstance(validated_data[key], (str, unicode, int, long, float, DateTime)))
      ).hexdigest()

    # FTP/DAV Access
    manage_FTPget = ZMIForm.get_xml

    def PUT(self, REQUEST, RESPONSE):
        """Handle HTTP PUT requests."""
        self.dav__init(REQUEST, RESPONSE)
        self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)
        if REQUEST.environ['REQUEST_METHOD'] != 'PUT':
            raise Forbidden, 'REQUEST_METHOD should be PUT.'
        body=REQUEST.get('BODY', '')
        # Empty the form (XMLToForm is unable to empty things before reopening)
        for k in self.get_field_ids():
          try:
            self._delObject(k)
          except AttributeError:
            pass
        self.groups = {}
        self.group_list = []
        # And reimport
        XMLToForm(body, self)
        self.ZCacheable_invalidate()
        RESPONSE.setStatus(204)
        return RESPONSE

    manage_FTPput = PUT

    security.declarePrivate('getSimilarSkinFolderIdList')
    def getSimilarSkinFolderIdList(self):
      """
      Find other skins id installed in the same time
      """
      portal = self.getPortalObject()
      folder_id = self.aq_parent.id
      # Find a business template which manages the context skin folder.
      folder_id_set = {folder_id}
      for template in portal.portal_templates.getInstalledBusinessTemplateList():
        template_skin_id_list = template.getTemplateSkinIdList()
        if folder_id in template_skin_id_list:
          folder_id_set.update(template_skin_id_list)

          # Find folders which can be surcharged by this skin folder
          if '_' in folder_id:
            surcharged_folder_id = 'erp5_%s' % folder_id.split('_')[-1]
            if (surcharged_folder_id != folder_id) and \
              (getattr(portal.portal_skins, surcharged_folder_id, None) \
                                                             is not None):
              folder_id_set.add(surcharged_folder_id)

          break
      return list(folder_id_set)

    #Methods for Proxify tab.
    security.declareProtected('View management screens', 'getFormFieldList')
    def getFormFieldList(self):
        """
        find fields and forms which name ends with 'FieldLibrary' in
        the same business template or in erp5_core.
        """
        form_list = []
        def iterate(obj):
            for i in obj.objectValues():
                if (i.meta_type=='ERP5 Form' and
                    i.id.startswith('Base_view') and
                    i.id.endswith('FieldLibrary') and
                    '_view' in i.getId()):
                    form_id = i.getId()
                    form_path = '%s.%s' % (obj.getId(), form_id)
                    field_list = []
                    form_list.append({'form_path':form_path,
                                      'form_id':form_id,
                                      'field_list':field_list})
                    for field in i.objectValues():
                        field_type, proxy_flag = get_field_meta_type_and_proxy_flag(field)
                        if proxy_flag:
                            field_type = '%s(Proxy)' % field_type
                        field_list.append({'field_object':field,
                                           'field_type':field_type,
                                           'proxy_flag':proxy_flag})
                if i.meta_type=='Folder':
                    iterate(i)

        skins_tool = self.portal_skins
        folder_id = self.aq_parent.id
        # for skin_folder_id in self.getSimilarSkinFolderIdList():
        for skin_folder_id in self.getPortalObject().portal_skins.objectIds():
          iterate(getattr(skins_tool, skin_folder_id))
        iterate(skins_tool.erp5_core)
        return form_list

    security.declareProtected('View management screens', 'getProxyableFieldList')
    def getProxyableFieldList(self, field, form_field_list=None):
        """"""
        def extract_keyword(name):
            keyword_list = [i for i in name.split('_') if not i in \
                    ('my', 'default', 'listbox', 'your')]
            if len(keyword_list) == 0:
              # This means that the name is one of the exception keywords,
              # so we have to keep it
              keyword_list = [name]
            return keyword_list

        def check_keyword_list(name, keyword_list):
            count = 0
            for i in keyword_list:
                if i in name:
                    count += 1
            return count/float(len(keyword_list))

        def match(field_data):
            if not field_data['field_type'].startswith(field.meta_type):
                return 0
            field_object = field_data['field_object']
            if field_object.aq_base is field.aq_base:
                return 0
            field_id = field_object.getId()
            # All proxy fields in field libraries should define their
            # technical context
            # XXX Theses 3 following lines will need to be uncommented
            # as soon as proxy guideline is fully validated on erp5_trade
            #if field.meta_type == 'ProxyField' and \
            #    re.match('my_.*_mode', field_id) is None:
            #  return 0
            # XXX keyword match is not useful anymore.Need different approach.
            keyword_match_rate = check_keyword_list(field_id, extract_keyword(id_))
            if keyword_match_rate>0.3:
                return keyword_match_rate
            else:
                def split(string):
                    result = []
                    temporary = []
                    for char in string:
                        if char.isupper():
                            if temporary:
                                result.append(''.join(temporary))
                            temporary = []
                        temporary.append(char)
                    result.append(''.join(temporary))
                    return result

                if ''.join(field_id.split('_')[1:]).startswith(
                    split(field.meta_type)[0].lower()):
                    # At least it seems a generic template field of the meta_type.
                    return 0.1

        def make_dict_list_append_function(dic, order_list):
            def append(key, item):
                if not key in order_list:
                    order_list.append(key)
                    dic[key] = []
                dic[key].append(item)
            return append

        def add_default_field_library():
            portal_url = getToolByName(self, 'portal_url')
            portal = portal_url.getPortalObject()
            portal_skins = getToolByName(self, 'portal_skins')

            default_field_library_path = portal.getProperty(
                                  'erp5_default_field_library_path',
                                  'erp5_core.Base_viewFieldLibrary')
            if (not default_field_library_path or
                len(default_field_library_path.split('.'))!=2):
                return

            skinfolder_id, form_id = default_field_library_path.split('.')

            skinfolder = getattr(portal_skins, skinfolder_id, None)
            default_field_library = getattr(skinfolder, form_id, None)
            if default_field_library is None:
                return
            for i in default_field_library.objectValues():
                field_meta_type, proxy_flag = get_field_meta_type_and_proxy_flag(i)
                if meta_type==field_meta_type:
                    if proxy_flag:
                        field_meta_type = '%s(Proxy)' % field_meta_type
                    matched_item = {'form_id':form_id,
                                    'field_type':field_meta_type,
                                    'field_object':i,
                                    'proxy_flag':proxy_flag,
                                    'matched_rate':0
                                    }

                    if not i in [item['field_object']
                                 for item in matched.get(default_field_library_path, ())]:
                      matched_append(default_field_library_path, matched_item)
                    if not i in [item['field_object']
                                 for item in perfect_matched.get(default_field_library_path, ())]:
                      perfect_matched_append(default_field_library_path, matched_item)

        id_ = field.getId()
        meta_type = field.meta_type

        matched = {}
        form_order = []
        matched_append = make_dict_list_append_function(matched, form_order)

        perfect_matched = {}
        perfect_matched_form_order = []
        perfect_matched_append = make_dict_list_append_function(perfect_matched, perfect_matched_form_order)

        if form_field_list is None:
            form_field_list = self.getFormFieldList()

        for i in form_field_list:
            for data in i['field_list']:
                tmp = []
                matched_rate = match(data)
                if matched_rate>0:
                    form_path = i['form_path']
                    form_id = i['form_id']
                    field_type = data['field_type']
                    field_object = data['field_object']
                    proxy_flag = data['proxy_flag']

                    matched_item = {'form_id':form_id,
                                    'field_type':field_type,
                                    'field_object':field_object,
                                    'proxy_flag':proxy_flag,
                                    'matched_rate':matched_rate
                                    }
                    if matched_rate==1:
                        perfect_matched_append(form_path, matched_item)
                    elif not perfect_matched:
                        matched_append(form_path, matched_item)

        if perfect_matched:
            perfect_matched_form_order.sort()
            add_default_field_library()
            return perfect_matched_form_order, perfect_matched

        form_order.sort()
        add_default_field_library()
        return form_order, matched

    security.declareProtected('View management screens', 'getUnProxyableFieldList')
    def getUnProxyableFieldList(self):
      """
      Return ProxyFields
      """
      return sorted([f for f in self.objectValues() \
          if f.meta_type == 'ProxyField'], key = lambda x: x.id)

    security.declareProtected('View management screens',
        'getRelatedProxyFieldDictList')
    def getRelatedProxyFieldDictList(self, **kw):
      """
      Retrieve all proxy using proxy in this form
      """
      form_id = self.id
      proxy_dict = {}
      for document in self.objectValues():
        short_path = "%s.%s" % (form_id, document.id)
        proxy_dict[short_path] = {'proxy': document,
                                  'short_path': short_path,
                                  'related_proxy_list': []}
      def iterate(document):
        for i in document.objectValues():
          if i.meta_type == 'ERP5 Form':
            for field in i.objectValues():
              if field.meta_type == 'ProxyField':
                key = "%s.%s" % (field.get_value('form_id'),
                                 field.get_value('field_id'))
                if proxy_dict.has_key(key):
                  proxy_dict[key]['related_proxy_list'].append(
                      {'short_path': "%s.%s" % \
                      (field.aq_parent.id, field.id),
                       'proxy': field})
          if i.meta_type == 'Folder':
            iterate(i)

      skins_tool = self.portal_skins
      proxy_dict_list = []
      if len(proxy_dict):
        # for skin_folder_id in self.getSimilarSkinFolderIdList():
        for skin_folder_id in self.getPortalObject().portal_skins.objectIds():
          iterate(getattr(skins_tool, skin_folder_id))
        proxy_dict_list = proxy_dict.values()
        proxy_dict_list.sort(key=lambda x: x['short_path'])
        for item in proxy_dict_list:
          item['related_proxy_list'].sort(key=lambda x: x['short_path'])

      return proxy_dict_list

    _proxy_copy_type_list = (bytes, unicode, int, long, float, bool, list,
                             tuple, dict, DateTime)

    security.declareProtected('Change Formulator Forms', 'proxifyField')
    def proxifyField(self, field_dict=None, force_delegate=False,
                     keep_empty_value=False, REQUEST=None):
        """Convert fields to proxy fields
        If the field value is not empty and different from the proxyfield
        value, the value is kept on the proxyfield, otherwise it is delegated.
        If you specify force_delegate, values will be delegated even if they
        are different. And if you specify keep_empty_value, then empty values
        will not be delegated(force_delegate option is high priority).
        """
        def copy(field, value_type):
            new_dict = {}
            for key, value in getFieldDict(field, value_type).iteritems():
                if isinstance(aq_base(value), (Method, TALESMethod)):
                    value = copyMethod(value)
                elif not (value is None or
                          isinstance(value, self._proxy_copy_type_list)):
                    raise ValueError('%s:%r' % (type(value), value))
                elif not (keep_empty_value or value):
                    continue
                new_dict[key] = value
            return new_dict

        def is_equal(a, b):
            type_a = type(a)
            type_b = type(b)
            if type_a is not type_b:
                return False
            elif type_a is Method:
                return a.method_name==b.method_name
            elif type_a is TALESMethod:
                return a._text==b._text
            else:
                return a==b

        def remove_same_value(new_dict, target_dict):
            for key, value in new_dict.items():
                target_value = target_dict.get(key)
                if force_delegate or is_equal(value, target_value):
                    del new_dict[key]
            return new_dict

        def get_group_and_position(field_id):
            for i in self.groups.keys():
                if field_id in self.groups[i]:
                    return i, self.groups[i].index(field_id)

        def set_group_and_position(group, position, field_id):
            self.field_removed(field_id)
            self.groups[group].insert(position, field_id)
            # Notify changes explicitly.
            self.groups = self.groups

        if field_dict is None:
            return

        for field_id in field_dict.keys():
            target = field_dict[field_id]
            target_form_id, target_field_id = target.split('.')

            # keep current group and position.
            group, position = get_group_and_position(field_id)

            # create proxy field
            old_field = getattr(self, field_id)
            self.manage_delObjects(field_id)
            self.manage_addField(id=field_id, title='', fieldname='ProxyField')
            proxy_field = getattr(self, field_id)
            proxy_field.values['form_id'] = target_form_id
            proxy_field.values['field_id'] = target_field_id

            target_field = proxy_field.getTemplateField()
            if target_field is None:
              raise ValueError("Unable to find template : %s.%s" % (
                               target_form_id, target_field_id))

            # copy data
            new_values = remove_same_value(copy(old_field, 'values'),
                                           getFieldDict(target_field, 'values'))
            new_tales = remove_same_value(copy(old_field, 'tales'),
                                          getFieldDict(target_field, 'tales'))

            if target_field.meta_type=='ProxyField':
                for i in new_values.keys():
                    if not i in target_field.delegated_list:
                        # obsolete variable check
                        try:
                            target_field.get_recursive_orig_value(i)
                        except KeyError:
                            # then `i` is obsolete!
                            del new_values[i]
                        else:
                            if is_equal(target_field.get_recursive_orig_value(i),
                                        new_values[i]):
                                del new_values[i]
                for i in new_tales.keys():
                    if not i in target_field.delegated_list:
                        # obsolete variable check
                        try:
                            target_field.get_recursive_tales(i)
                        except KeyError:
                            # then `i` is obsolete!
                            del new_tales[i]
                        else:
                            if is_equal(target_field.get_recursive_tales(i),
                                        new_tales[i]):
                                del new_tales[i]

            delegated_list = []
            for i in (new_values.keys()+new_tales.keys()):
                if not i in delegated_list:
                    delegated_list.append(i)
            proxy_field.values.update(new_values)
            proxy_field.tales.update(new_tales)
            proxy_field.delegated_list = delegated_list

            # move back to the original group and position.
            set_group_and_position(group, position, field_id)

        if REQUEST is not None:
            return self.formProxify(manage_tabs_message='Changed')

    psyco.bind(__call__)
    psyco.bind(_exec)

    security.declareProtected('Change Formulator Forms', 'unProxifyField')
    def unProxifyField(self, field_dict=None, copy_delegated_values=False,
                       REQUEST=None):
        """
        Convert proxy fields to fields
        """
        def copy(field, value_type):
            new_dict = {}
            for key, value in getFieldDict(field, value_type).iteritems():
                if isinstance(aq_base(value), (Method, TALESMethod)):
                    value = copyMethod(value)
                elif not (value is None or
                          isinstance(value, self._proxy_copy_type_list)):
                    raise ValueError('%s:%r' % (type(value), value))
                new_dict[key] = value
            return new_dict

        def is_equal(a, b):
            type_a = type(a)
            type_b = type(b)
            if type_a is not type_b:
                return False
            elif type_a is Method:
                return a.method_name==b.method_name
            elif type_a is TALESMethod:
                return a._text==b._text
            else:
                return a==b

        def remove_same_value(new_dict, target_dict):
            for key, value in new_dict.items():
                target_value = target_dict.get(key)
                if is_equal(value, target_value):
                    del new_dict[key]
            return new_dict

        def get_group_and_position(field_id):
            for i in self.groups.keys():
                if field_id in self.groups[i]:
                    return i, self.groups[i].index(field_id)

        def set_group_and_position(group, position, field_id):
            self.field_removed(field_id)
            self.groups[group].insert(position, field_id)
            # Notify changes explicitly.
            self.groups = self.groups

        if field_dict is None:
            return

        for field_id in field_dict.keys():
            # keep current group and position.
            group, position = get_group_and_position(field_id)

            # create field
            old_proxy_field = getattr(self, field_id)
            delegated_field = old_proxy_field.getRecursiveTemplateField()
            if delegated_field is None:
              break
            self.manage_delObjects(field_id)
            self.manage_addField(id=field_id,
                                 title='',
                                 fieldname=delegated_field.meta_type)
            field = getattr(self, field_id)
            # copy data
            new_values = remove_same_value(copy(old_proxy_field, 'values'),
                                           field.values)
            new_tales = remove_same_value(copy(old_proxy_field, 'tales'),
                                          field.tales)

            field.values.update(new_values)
            field.tales.update(new_tales)

            # move back to the original group and position.
            set_group_and_position(group, position, field_id)

        if REQUEST is not None:
            return self.formUnProxify(manage_tabs_message='Changed')

    # Overload of the Form method
    #   Use the include_disabled parameter since
    #   we should consider all fields to render the group tab
    #   moreoever, listbox rendering fails whenever enabled
    #   is based on the cell parameter.
    security.declareProtected('View', 'get_largest_group_length')
    def get_largest_group_length(self):
        """Get the largest group length available; necessary for
        'order' screen user interface.
        XXX - Copyright issue
        """
        max = 0
        for group in self.get_groups(include_empty=1):
            fields = self.get_fields_in_group(group, include_disabled=1)
            if len(fields) > max:
                max = len(fields)
        return max

    security.declareProtected('View', 'get_groups')
    def get_groups(self, include_empty=0):
        """Get a list of all groups, in display order.

        If include_empty is false, suppress groups that do not have
        enabled fields.
        XXX - Copyright issue
        """
        if include_empty:
            return self.group_list
        return [group for group in self.group_list
                if self.get_fields_in_group(group, include_disabled=1)]

    # Find support in ZMI. This is useful for development.
    def PrincipiaSearchSource(self):
      return str((self.pt, self.name, self.action, self.update_action,
                  self.encoding, self.stored_encoding, self.enctype))

    # XXX: This class is a mix between a document class and a regular class.
    # Ideally, it should be made an alias to "erp5.portal_type.ERP5 Form",
    # which is the corresponding fully-functional document class.
    # Until then, hardcode some methods expected to exist on all document
    # classes so that they can be removed from Base.
    def _getAcquireLocalRoles(self):
      return True

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

