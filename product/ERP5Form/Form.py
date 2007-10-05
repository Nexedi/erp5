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

from Products.Formulator.Form import Form, BasicForm, ZMIForm
from Products.Formulator.Form import manage_addForm, manage_add, initializeForm
from Products.Formulator.Errors import FormValidationError, ValidationError
from Products.Formulator.DummyField import fields
from Products.Formulator.XMLToForm import XMLToForm
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.CMFCore.utils import _checkPermission, getToolByName
from Products.CMFCore.exceptions import AccessControl_Unauthorized
from Products.ERP5Type import PropertySheet, Permissions

from urllib import quote
from Globals import InitializeClass, PersistentMapping, DTMLFile, get_request
from AccessControl import Unauthorized, getSecurityManager, ClassSecurityInfo
from ZODB.POSException import ConflictError
from Acquisition import aq_base
from Products.PageTemplates.Expressions import SecureModuleImporter
from Products.ERP5Type.Utils import UpperCase

from Products.ERP5Type.PsycoWrapper import psyco
import sys

_field_value_cache = {}
def purgeFieldValueCache():
  _field_value_cache.clear()

# Patch the fiels methods to provide improved namespace handling

from Products.Formulator.Field import Field
from Products.Formulator.MethodField import Method, BoundMethod
from Products.Formulator.TALESField import TALESMethod

from zLOG import LOG, PROBLEM


def copyMethod(value):
    if type(aq_base(value)) is Method:
      value = Method(value.method_name)
    elif type(aq_base(value)) is TALESMethod:
      value = TALESMethod(value._text)
    elif type(aq_base(value)) is BoundMethod:
      value = BoundMethod(value.object, value.method_name)
    return value


class StaticValue:
  """
    Encapsulated a static value in a class
    (quite heavy, would be faster to store the
    value as is)
  """
  def __init__(self, value):
    if isinstance(aq_base(value), (Method, TALESMethod)):
      value = copyMethod(value)
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
    REQUEST = get_request()
    if REQUEST is not None:
      # Proxyfield stores the "real" field in the request. Look if the
      # corresponding field exists in request, and use it as field in the
      # TALES context 
      field = REQUEST.get('field__proxyfield_%s_%s' % (field.id, id), field)

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
    if kw.has_key('REQUEST') and kw.get('cell', None) is None:
      if getattr(kw['REQUEST'],'cell', None) is not None:
        kw['cell'] = getattr(kw['REQUEST'],'cell')
      else:
        kw['cell'] = kw['REQUEST']
    elif kw.get('cell', None) is None:
      if getattr(REQUEST, 'cell', None) is not None:
        kw['cell'] = getattr(REQUEST, 'cell')
    try:
      value = self.tales_expr.__of__(field)(**kw)
    except (ConflictError, RuntimeError):
      raise
    except:
      # We add this safety exception to make sure we always get
      # something reasonable rather than generate plenty of errors
      LOG('ERP5Form', PROBLEM,
          'Field.get_value ( %s/%s [%s]), exception on tales_expr: ' %
          ( form.getId(), field.getId(), id), error=sys.exc_info())
      # field may be ProxyField
      try:
        value = field.get_recursive_orig_value(id)
      except AttributeError:
        value = field.get_orig_value(id)

    return self.returnValue(field, id, value)

class OverrideValue(StaticValue):
  def __init__(self, override):
    if isinstance(aq_base(override), (Method, TALESMethod)):
      override = copyMethod(override)
    self.override = override

  def __call__(self, field, id, **kw):
    return self.returnValue(field, id, self.override.__of__(field)())

class DefaultValue(StaticValue):
  def __init__(self, field_id, value):
    self.key = field_id[3:]
    if isinstance(aq_base(value), (Method, TALESMethod)):
      value = copyMethod(value)
    self.value = value

  def __call__(self, field, id, **kw):
    try:
      form = field.aq_parent
      ob = getattr(form, 'aq_parent', None)
      value = self.value
      if value not in (None, ''):
        # If a default value is defined on the field, it has precedence
        value = ob.getProperty(self.key, d=value)
      else:
        # else we should give a chance to the accessor to provide
        # a default value (including None)
        value = ob.getProperty(self.key)
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
    if kw.get('REQUEST', None) is not None:
      if not getattr(kw['REQUEST'], 'editable_mode', 1):
        return 0
    return self.value

def getFieldValue(self, field, id, **kw):
  """
    Return a callable expression
  """
  tales_expr = self.tales.get(id, "")
  if tales_expr:
    # TALESMethod is persistent object, so that we cannot cache original one.
    # Becase if connection which original talesmethod uses is closed,
    # RuntimeError must occurs in __setstate__.
    clone = TALESMethod(tales_expr._text)
    return TALESValue(clone)

  override = self.overrides.get(id, "")
  if override:
    return OverrideValue(override)

  # Get a normal value.
  value = self.get_orig_value(id)

  field_id = field.id

  if id == 'default' and field_id.startswith('my_'):
    return DefaultValue(field_id, value)

  # For the 'editable' value, we try to get a default value
  if id == 'editable':
    return EditableValue(value)

  # Return default value in callable mode
  if callable(value):
    return StaticValue(value)

  # Return default value in non callable mode
  return StaticValue(value)(field, id, **kw)

def get_value(self, id, **kw):
  REQUEST = get_request()
  if REQUEST is not None:
    field = REQUEST.get('field__proxyfield_%s_%s' % (self.id, id), self)
  else:
    field = self

  # If field is not stored in zodb, then must use original get_value instead.
  # Because field which is not stored in zodb must be used for editing field
  # in ZMI and field value cache sometimes break these field settings at
  # initialization. As the result, we will see broken field editing screen
  # in ZMI.
  if self._p_oid is None:
    return self._original_get_value(id, **kw)

  cache_id = ('Form.get_value',
              self._p_oid,
              field._p_oid,
              id)

  try:
    value = _field_value_cache[cache_id]
  except KeyError:
    # either returns non callable value (ex. "Title")
    # or a FieldValue instance of appropriate class
    value = _field_value_cache[cache_id] = getFieldValue(self, field, id, **kw)

  if callable(value):
    return value(field, id, **kw)
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
original_get_value = Field.get_value
Field.get_value = get_value
Field._original_get_value = original_get_value
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
    update_action = fields.StringField('update_action',
                                title='Form update action',
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
                                        required=1)

    form.add_fields([title, description, row_length, name, pt, action, update_action, method,
                     enctype, encoding, stored_encoding, unicode_mode])
    return form

class ERP5Form(ZMIForm, ZopePageTemplate):
    """
        A Formulator form with a built-in rendering parameter based
        on page templates or DTML.
    """
    meta_type = "ERP5 Form"
    icon = "www/Form.png"

    # Declarative Security
    security = ClassSecurityInfo()

    # Tabs in ZMI
    manage_options = (ZMIForm.manage_options[:5] +
                      ({'label':'Proxify', 'action':'formProxify'},)+
                      ZMIForm.manage_options[5:])

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem)

    # Constructors
    constructors =   (manage_addForm, addERP5Form)

    # This is a patched dtml formOrder
    security.declareProtected('View management screens', 'formOrder')
    formOrder = DTMLFile('dtml/formOrder', globals())

    # Proxify form
    security.declareProtected('View management screens', 'formProxify')
    formProxify = DTMLFile('dtml/formProxify', globals())

    # Default Attributes
    pt = 'form_view'
    update_action = ''

    # Special Settings
    settings_form = create_settings_form()

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
        if not kwargs.has_key('args'):
            kwargs['args'] = args
        form = self
        obj = getattr(form, 'aq_parent', None)
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
                              options=kwargs,
                              here=obj )
        return pt.pt_render(extra_context=extra_context)

    def _exec(self, bound_names, args, kw):
        pt = getattr(self,self.pt)
        return pt._exec(self, bound_names, args, kw)

    # Utilities
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
    def validate_all(self, REQUEST):
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
                if not field.need_validate(REQUEST):
                    continue
                if not (field.get_value('editable',REQUEST=REQUEST)):
                    continue
                try:
                    value = field.validate(REQUEST)
                    # store under id
                    result[field.id] = value
                    # store as alternate name as well if necessary
                    alternate_name = field.get_value('alternate_name')
                    if alternate_name:
                        result[alternate_name] = value
                except FormValidationError, e: # XXX JPS Patch for listbox
                    #LOG('validate_all', 0, 'FormValidationError: field = %s, errors=%s' % (repr(field), repr(errors)))
                    errors.extend(e.errors)
                    result.update(e.result)
                except ValidationError, err:
                    #LOG('validate_all', 0, 'ValidationError: field.id = %s, err=%s' % (repr(field.id), repr(err)))
                    errors.append(err)
                except KeyError, err:
                    LOG('ERP5Form/Form.py:validate_all', 0, 'KeyError : %s' % (err, ))
                
        if len(errors) > 0:
            raise FormValidationError(errors, result)
        return result

    # FTP/DAV Access
    manage_FTPget = ZMIForm.get_xml

    def PUT(self, REQUEST, RESPONSE):
        """Handle HTTP PUT requests."""
        self.dav__init(REQUEST, RESPONSE)
        self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)
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

    #Methods for Proxify tab.
    security.declareProtected('View management screens', 'getFormFieldList')
    def getFormFieldList(self):
        """
        find fields and forms which name ends with 'FieldLibrary' in
        same skin folder.
        """
        form_list = []
        def iterate(obj):
            for i in obj.objectValues():
                if (i.meta_type=='ERP5 Form' and
                    i.getId().endswith('FieldLibrary')):
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
        iterate(getToolByName(self, 'portal_skins'))
        return form_list

    security.declareProtected('View management screens', 'getProxyableFieldList')
    def getProxyableFieldList(self, field, form_field_list=None):
        """"""
        def extract_keyword(name):
            return [i for i in name.split('_') if not i in ('my', 'default')]

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
            if id_.startswith('my_') and not field_id.startswith('my_'):
                return 0
            return check_keyword_list(field_id, extract_keyword(id_))

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
                    if not default_field_library_path in form_order:
                        matched_append(default_field_library_path,
                                       matched_item)
                    if not default_field_library_path in \
                                          perfect_matched_form_order:
                        perfect_matched_append(default_field_library_path,
                                               matched_item)

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
                if matched_rate>=0.5:
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

    security.declareProtected('Change Formulator Forms', 'proxifyField')
    def proxifyField(self, field_dict=None, REQUEST=None):
        """Convert fields to proxy fields"""
        from Products.ERP5Form.ProxyField import ProxyWidget

        def copy(_dict):
            new_dict = {}
            for key, value in _dict.items():
                if value=='':
                    continue
                if isinstance(aq_base(value), (Method, TALESMethod)):
                    value = copyMethod(value)
                elif value is not None and not isinstance(value,
                        (str, unicode, int, long, bool, list, tuple, dict)):
                    raise ValueError, repr(value)
                new_dict[key] = value
            return new_dict

        def is_equal(a, b):
            type_a = type(a)
            type_b = type(b)
            if type_a is not type_b:
                return False
            elif type_a is Method or type_a is BoundMethod:
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

            # copy data
            new_values = remove_same_value(copy(old_field.values),
                                           target_field.values)
            new_tales = remove_same_value(copy(old_field.tales),
                                          target_field.tales)

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


# utility function
def get_field_meta_type_and_proxy_flag(field):
    if field.meta_type=='ProxyField':
        try:
            return field.getRecursiveTemplateField().meta_type, True
        except AttributeError:
            raise AttributeError, 'The proxy target of %s field does not '\
                  'exists. Please check the field setting.' % field.getId()
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

# install interactor
# we need to install interactor after to apply get_value patch.
from Products.ERP5Type.Interactor import fielf_value_interactor
fielf_value_interactor.install()
