##############################################################################
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
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.exceptions import AccessControl_Unauthorized
from Products.ERP5Type import PropertySheet, Permissions

from urllib import quote
from Globals import InitializeClass, PersistentMapping, DTMLFile, get_request
from AccessControl import Unauthorized, getSecurityManager, ClassSecurityInfo
from ZODB.POSException import ConflictError
from Products.PageTemplates.Expressions import SecureModuleImporter
from Products.ERP5Type.Utils import UpperCase

from Products.ERP5Type.PsycoWrapper import psyco
import sys

# Patch the fiels methods to provide improved namespace handling

from Products.Formulator.Field import Field

from zLOG import LOG, PROBLEM

def get_value(self, id, **kw):
    """Get value for id."""
    # FIXME: backwards compat hack to make sure tales dict exists
    if not hasattr(self, 'tales'):
        self.tales = {}

    tales_expr = self.tales.get(id, "")
    if tales_expr:
        REQUEST = get_request()
        form = self.aq_parent # XXX (JPS) form for default is wrong apparently in listbox - double check
        obj = getattr(form, 'aq_parent', None)
        if obj is not None:
            container = obj.aq_inner.aq_parent
        else:
            container = None
        kw['field'] = self
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
        if kw.has_key('REQUEST') and kw.get('cell',None) is None:
          if getattr(kw['REQUEST'],'cell',None) is not None:
            kw['cell'] = getattr(kw['REQUEST'],'cell')
          else:
            kw['cell'] = kw['REQUEST']
        elif kw.get('cell',None) is None:
          if getattr(REQUEST,'cell',None) is not None:
            kw['cell'] = getattr(REQUEST,'cell')
        try:
            value = tales_expr.__of__(self)(**kw)
        except (ConflictError, RuntimeError):
            raise
        except:
            # We add this safety exception to make sure we always get
            # something reasonable rather than generate plenty of errors
            LOG('ERP5Form', PROBLEM,
                'Field.get_value ( %s/%s [%s]), exception on tales_expr: ' %
                ( form.getId(), self.getId(), id), error=sys.exc_info())
            value = self.get_orig_value(id)
    else:
        # FIXME: backwards compat hack to make sure overrides dict exists
        if not hasattr(self, 'overrides'):
            self.overrides = {}

        override = self.overrides.get(id, "")
        if override:
            # call wrapped method to get answer
            value = override.__of__(self)()
        else:
            # Get a normal value.
            value = self.get_orig_value(id)

            # For the 'default' value, we try to get a property value
            # stored in the context, only if the field is prefixed with my_.
            if id == 'default' and self.id[:3] == 'my_':
              try:
                form = self.aq_parent
                ob = getattr(form, 'aq_parent', None)
                key = self.id[3:]
                if value not in (None, ''):
                  # If a default value is defined on the field, it has precedence
                  value = ob.getProperty(key, d=value)
                else:
                  # else we should give a chance to the accessor to provide
                  # a default value (including None)
                  value = ob.getProperty(key)
              except (KeyError, AttributeError):
                value = None
            # For the 'editable' value, we try to get a default value
            elif id == 'editable':
                # By default, pages are editable and
                # fields are editable if they are set to editable mode
                # However, if the REQUEST defines editable_mode to 0
                # then all fields become read only.
                # This is useful to render ERP5 content as in a web site (ECommerce)
                # editable_mode should be set for example by the page template
                # which defines the current layout
                if kw.has_key('REQUEST'):
                  if not getattr(kw['REQUEST'], 'editable_mode', 1):
                    value = 0

    # if normal value is a callable itself, wrap it
    if callable(value):
        value = value.__of__(self)
        #value=value() # Mising call ??? XXX Make sure compatible with listbox methods

    if id == 'default':
        # We make sure we convert values to empty strings
        # for most fields (so that we do not get a 'value'
        # message on screen)
        # This can be overriden by using TALES in the field
        if value is None: value = ''

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

    form.add_fields([title, row_length, name, pt, action, update_action, method,
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

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem)

    # Constructors
    constructors =   (manage_addForm, addERP5Form)

    # This is a patched dtml formOrder
    security.declareProtected('View management screens', 'formOrder')
    formOrder = DTMLFile('dtml/formOrder', globals())

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

    psyco.bind(__call__)
    psyco.bind(_exec)

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
