##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
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
from Products.Formulator.DummyField import fields
from Products.Formulator.XMLToForm import XMLToForm
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.ERP5Type import PropertySheet

from urllib import quote
from Globals import InitializeClass, PersistentMapping, DTMLFile
from AccessControl import Unauthorized, getSecurityManager, ClassSecurityInfo

from Products.ERP5Type.Utils import UpperCase

import psyco

# Patch the fiels methods to provide improved namespace handling

from Products.Formulator.Field import Field

from zLOG import LOG

class ERP5Field(Field):
    """
      The ERP5Field provides here, request,
      container etc. names to TALES expressions. It is used to dynamically
      patch the standard Formulator
    """
    security = ClassSecurityInfo()

    # this is a field
    is_field = 1

    security.declareProtected('Access contents information', 'get_value')
    def get_value(self, id, **kw):
        """Get value for id."""
        # FIXME: backwards compat hack to make sure tales dict exists
        if not hasattr(self, 'tales'):
            self.tales = {}

        tales_expr = self.tales.get(id, "")
        if tales_expr:
            form = self.aq_parent
            object = getattr(form, 'aq_parent', None)
            if object:
                # NEEDS TO BE CHECKED
                # container = object.aq_inner.aq_parent ORIGINAL VERSION - not so good ?
                container = object.aq_parent
                #container = object.getParentNode()
            else:
                container = None
            kw['field'] = self
            kw['form'] = form
            kw['here'] = object
            kw['container'] = container
            # This allows to pass some pointer to the local object
            # through the REQUEST parameter. Not very clean.
            # Used by ListBox to render different items in a list
            if kw.has_key('REQUEST') and not kw.has_key('cell'): kw['cell'] = kw['REQUEST']
            try:
              value = tales_expr.__of__(self)(**kw)
            except:
              # We add this safety exception to make sure we always get
              # something reasonable rather than generate plenty of errors
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
                # get normal value
                value = self.get_orig_value(id)
                # Only for the default value
                if id == 'default':
                  if (value is None or value == '' or value == [] or value == ()) \
                                                and self.meta_type != 'MethodField' :
                    # If nothing was provided then try to
                    # find a default method to get the value
                    # for that field
                    # NEEDS TO BE CLEANED UP
                    try:
                      form = self.aq_parent
                      object = getattr(form, 'aq_parent', None)
                      key = self.id
                      key = key[3:]
                      value = object.getProperty(key, d=value)
                    except:
                      value = None

        # if normal value is a callable itself, wrap it
        if callable(value):
            value = value.__of__(self)
            #value=value() # Mising call ??? XXX Make sure compatible with listbox methods

        if id == 'default':
          if self.meta_type != 'DateTimeField':
            # We make sure we convert values to empty strings
            # for most fields (so that we do not get a 'value'
            # message on screeen)
            # This can be overriden by useing TALES in the field
            if value is None: value = ''

        return value

    def om_icons(self):
        """Return a list of icon URLs to be displayed by an ObjectManager"""
        icons = ({'path': self.icon,
                  'alt': self.meta_type, 'title': self.meta_type},)
        return icons

    psyco.bind(get_value)        

# Dynamic Patch
Field.get_value = ERP5Field.get_value
Field.om_icons = ERP5Field.om_icons

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
    except:
        u = REQUEST['URL1']
    if REQUEST['submit'] == " Add and Edit ":
        u = "%s/%s" % (u, quote(id))
    REQUEST.RESPONSE.redirect(u+'/manage_main')

def initializeForm(field_registry):
    """Sets up ZMIForm with fields from field_registry.
    """
    form_class = ERP5Form

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

    form.add_fields([title, row_length, name, pt, action, method, enctype])
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

    # Default Attributes
    pt = 'form_view'

    # Special Settings
    settings_form = create_settings_form()

    # Proxy method to PageTemplate
    def __call__(self, *args, **kwargs):
        if not kwargs.has_key('args'):
            kwargs['args'] = args
        form = self
        object = getattr(form, 'aq_parent', None)
        if object:
          container = object.aq_inner.aq_parent
        else:
          container = None
        pt = getattr(self,self.pt)
        extra_context = self.pt_getContext()
        extra_context['options'] = kwargs
        extra_context['form'] = self
        extra_context['container'] = container ## PROBLEM NOT TAKEN INTO ACCOUNT
        extra_context['here'] = object
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
          except:
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

	
