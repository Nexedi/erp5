# -*- coding: utf-8 -*-
from App.class_init import default__class_init__ as InitializeClass
import Acquisition
from Persistence import Persistent
from App.special_dtml import DTMLFile
from AccessControl import ClassSecurityInfo
import OFS
from Shared.DC.Scripts.Bindings import Bindings
from Errors import ValidationError
from Products.Formulator.Widget import MultiItemsWidget
from zLOG import LOG
from lxml import etree


class Field:
    """Base class of all fields.
    A field is an object consisting of a widget and a validator.
    """
    security = ClassSecurityInfo()

    # this is a field
    is_field = 1
    # this is not an internal field (can be overridden by subclass)
    internal_field = 0
    # can alternatively render this field with Zope's :record syntax
    # this will be the record's name
    field_record = None

    def __init__(self, id, **kw):
        self.id = id
        # initialize values of fields in form
        self.initialize_values(kw)
        # initialize tales expression for fields in form
        self.initialize_tales()
        # initialize overrides of fields in form
        self.initialize_overrides()

        # initialize message values with defaults
        message_values = {}
        for message_name in self.validator.message_names:
            message_values[message_name] = getattr(self.validator,
                                                   message_name)
        self.message_values = message_values

    security.declareProtected('Change Formulator Fields', 'initialize_values')
    def initialize_values(self, dict):
        """Initialize values for properties, defined by fields in
        associated form.
        """
        values = {}
        for field in self.form.get_fields(include_disabled=1):
            id = field.id
            value = dict.get(id, field.get_value('default'))
            values[id] = value
        self.values = values

    security.declareProtected('Change Formulator Fields',
                              'initialize_tales')
    def initialize_tales(self):
        """Initialize tales expressions for properties (to nothing).
        """
        tales = {}
        for field in self.form.get_fields():
            id = field.id
            tales[id] = ""
        self.tales = tales

    security.declareProtected('Change Formulator Fields',
                              'initialize_overrides')
    def initialize_overrides(self):
        """Initialize overrides for properties (to nothing).
        """
        overrides = {}
        for field in self.form.get_fields():
            id = field.id
            overrides[id] = ""
        self.overrides = overrides

    security.declareProtected('Access contents information', 'has_value')
    def has_value(self, id):
        """Return true if the field defines such a value.
        """
        if self.values.has_key(id) or self.form.has_field(id):
            return 1
        else:
            return 0

    security.declareProtected('Access contents information', 'get_orig_value')
    def get_orig_value(self, id):
        """Get value for id; don't do any override calculation.
        """
        if self.values.has_key(id):
            return self.values[id]
        else:
            return self.form.get_field(id).get_value('default')

    security.declareProtected('Access contents information', 'get_value')
    def get_value(self, id, **kw):
        """Get value for id.

        Optionally pass keyword arguments that get passed to TALES
        expression.
        """
        tales_expr = self.tales.get(id, "")

        if tales_expr:
            # For some reason, path expressions expect 'here' and 'request'
            # to exist, otherwise they seem to fail. python expressions
            # don't seem to have this problem.

            # add 'here' if not in kw
            if not kw.has_key('here'):
                kw['here'] = self.aq_parent
            if not kw.has_key('request'):
                kw['request'] = self.REQUEST
            value = tales_expr.__of__(self)(
                field=self,
                form=self.aq_parent, **kw)
        else:
            override = self.overrides.get(id, "")
            if override:
                # call wrapped method to get answer
                value = override.__of__(self)()
            else:
                # get normal value
                value = self.get_orig_value(id)

        # if normal value is a callable itself, wrap it
        if callable(value):
            return value.__of__(self)
        else:
            return value

    security.declareProtected('View management screens', 'get_override')
    def get_override(self, id):
        """Get override method for id (not wrapped)."""
        return self.overrides.get(id, "")

    security.declareProtected('View management screens', 'get_tales')
    def get_tales(self, id):
        """Get tales expression method for id."""
        return self.tales.get(id, "")

    security.declareProtected('Access contents information', 'is_required')
    def is_required(self):
        """Check whether this field is required (utility function)
        """
        return self.has_value('required') and self.get_value('required')

    security.declareProtected('View management screens', 'get_error_names')
    def get_error_names(self):
        """Get error messages.
        """
        return self.validator.message_names

    security.declareProtected('Access contents information',
                              'generate_field_key')
    def generate_field_key(self, validation=0, key=None, key_prefix=None):
      """Generate the key Silva uses to render the field in the form.
      """
      # Patched by JPS for ERP5 in order to
      # dynamically change the name
      if key_prefix is None:
        key_prefix = 'field'
      if key is not None:
        return '%s_%s' % (key_prefix, key)
      if self.field_record is None:
        return '%s_%s' % (key_prefix, self.id)
      elif validation:
        return self.id
      elif isinstance(self.widget, MultiItemsWidget):
        return "%s.%s:record:list" % (self.field_record, self.id)
      else:
        return '%s.%s:record' % (self.field_record, self.id)

    security.declareProtected('Access contents information',
                              'generate_subfield_key')
    def generate_subfield_key(self, id, validation=0, key=None):
      """Generate the key Silva uses to render a sub field.
         Added key parameter for ERP5 in order to be compatible with listbox/matrixbox
      """
      if key is None: key = self.id
      if self.field_record is None or validation:
          return 'subfield_%s_%s' % (key, id)
      return '%s.subfield_%s_%s:record' % (self.field_record, key, id)

    security.declareProtected('View management screens', 'get_error_message')
    def get_error_message(self, name):
        try:
            return self.message_values[name]
        except KeyError:
            if name in self.validator.message_names:
                return getattr(self.validator, name)
            else:
                return "Unknown error: %s" % name

    security.declarePrivate('_render_helper')
    def _render_helper(self, key, value, REQUEST, render_prefix=None, editable=None, **kw):
      value = self._get_default(key, value, REQUEST)
      __traceback_info__ = ('key=%s value=%r' % (key, value))
      if self.get_value('hidden', REQUEST=REQUEST):
        return self.widget.render_hidden(self, key, value, REQUEST)
      else:
        if editable is None:
          editable = self.get_value('editable', REQUEST=REQUEST)
        if not editable:
          return self.widget.render_view(self, value, REQUEST=REQUEST,
                                         render_prefix=render_prefix, **kw)
        else:
          return self.widget.render(self, key, value, REQUEST,
                                    render_prefix=render_prefix, **kw)

    security.declarePrivate('_render_odt_helper')
    def _render_odt_helper(self, key, value, as_string, ooo_builder,
                           REQUEST, render_prefix, attr_dict, local_name):
      value = self._get_default(key, value, REQUEST)
      __traceback_info__ = ('key=%s value=%r' % (key, value))
      if not self.get_value('editable', REQUEST=REQUEST):
        return self.widget.render_odt_view(self, value, as_string, ooo_builder,
                                           REQUEST, render_prefix, attr_dict,
                                           local_name)
      else:
        return self.widget.render_odt(self, value, as_string, ooo_builder,
                                      REQUEST, render_prefix, attr_dict,
                                      local_name)

    security.declarePrivate('_render_odt_variable_helper')
    def _render_odt_variable_helper(self, key, value, as_string, ooo_builder,
                           REQUEST, render_prefix, attr_dict, local_name):
      value = self._get_default(key, value, REQUEST)
      __traceback_info__ = ('key=%s value=%r' % (key, value))
      return self.widget.render_odt_variable(self, value, as_string,
                                             ooo_builder, REQUEST,
                                             render_prefix, attr_dict,
                                             local_name)

    security.declarePrivate('_get_default')
    def _get_default(self, key, value, REQUEST):
        if value is not None:
            return value
        try:
            value = REQUEST.form[key]
        except (KeyError, AttributeError):
            # fall back on default
            return self.get_value('default')

        # if we enter a string value while the field expects unicode,
        # convert to unicode first
        # this solves a problem when re-rendering a sticky form with
        # values from request
        if (self.has_value('unicode') and self.get_value('unicode') and
            type(value) == type('')):
            return unicode(value, self.get_form_encoding())
        else:
            return value

    security.declarePrivate('_get_user_input_value')
    def _get_user_input_value(self, key, REQUEST):
      """
      Try to get a value of the field from the REQUEST
      """
      return REQUEST.form[key]

    security.declareProtected('View', 'render')
    def render(self, value=None, REQUEST=None, key=None, render_prefix=None, key_prefix=None, editable=None, **kw):
      """Render the field widget.
      value -- the value the field should have (for instance
                from validation).
      REQUEST -- REQUEST can contain raw (unvalidated) field
                information. If value is None, REQUEST is searched
                for this value.
      editable -- if not None, this boolean can override the Editable property
                 of the rendered field
      if value and REQUEST are both None, the 'default' property of
      the field will be used for the value.
      """
      return self._render_helper(
        self.generate_field_key(key=key, key_prefix=key_prefix),
        value,
        REQUEST,
        render_prefix=render_prefix,
        editable=editable,
        **kw
      )

    security.declareProtected('View', 'render_view')
    def render_view(self, value=None, REQUEST=None, render_prefix=None):
      """Render value to be viewed.
      """
      return self.widget.render_view(self, value, REQUEST=REQUEST)

    security.declareProtected('View', 'render_pdf')
    def render_pdf(self, value=None, REQUEST=None, key=None, **kw):
      """
      render_pdf renders the field for reportlab
      """
      return self.widget.render_pdf(self, value)

    security.declareProtected('View', 'render_html')
    def render_html(self, *args, **kw):
      """
      render_html is used to as definition of render method in Formulator.
      """
      return self.render(*args, **kw)

    security.declareProtected('View', 'render_htmlgrid')
    def render_htmlgrid(self, value=None, REQUEST=None, key=None, render_prefix=None, key_prefix=None):
      """
      render_htmlgrid returns a list of tuple (title, html render)
      """
      # What about CSS ? What about description ? What about error ?
      widget_key = self.generate_field_key(key=key, key_prefix=key_prefix)
      value = self._get_default(widget_key, value, REQUEST)
      __traceback_info__ = ('key=%s value=%r' % (key, value))
      return self.widget.render_htmlgrid(self, widget_key, value, REQUEST, render_prefix=render_prefix)

    security.declareProtected('View', 'render_odf')
    def render_odf(self, field=None, key=None, value=None, REQUEST=None,
                     render_format='ooo', render_prefix=None):
      return self.widget.render_odf(self, key, value, REQUEST, render_format,
                                render_prefix)

    security.declareProtected('View', 'render_odt')
    def render_odt(self, key=None, value=None, as_string=True, ooo_builder=None,
        REQUEST=None, render_prefix=None, attr_dict=None, local_name='p',
        key_prefix=None):
      field_key = self.generate_field_key(key=key, key_prefix=key_prefix)
      return self._render_odt_helper(field_key, value, as_string,
                                     ooo_builder, REQUEST, render_prefix,
                                     attr_dict, local_name)

    security.declareProtected('View', 'render_odt_variable')
    def render_odt_variable(self, key=None, value=None, as_string=True,
        ooo_builder=None, REQUEST=None, render_prefix=None, attr_dict=None,
        local_name='variable-set', key_prefix=None):
      field_key = self.generate_field_key(key=key, key_prefix=key_prefix)
      return self._render_odt_variable_helper(field_key, value, as_string,
                                     ooo_builder, REQUEST, render_prefix,
                                     attr_dict, local_name)

    security.declareProtected('View', 'render_odt_view')
    def render_odt_view(self, value=None, as_string=True, ooo_builder=None,
        REQUEST=None, render_prefix=None, attr_dict=None, local_name='p'):
      """Call read-only renderer
      """
      return self.widget.render_odt_view(self, value, as_string, ooo_builder,
                                         REQUEST, render_prefix, attr_dict,
                                         local_name)

    security.declareProtected('View', 'render_odg')
    def render_odg(self, key=None, value=None, as_string=True, ooo_builder=None,
        REQUEST=None, render_prefix=None, attr_dict=None, local_name='p',
        key_prefix=None):
      widget_key = self.generate_field_key(key=key, key_prefix=key_prefix)
      value = self._get_default(widget_key, value, REQUEST)
      return self.widget.render_odg(self, value, as_string, ooo_builder,
                                    REQUEST, render_prefix, attr_dict,
                                    local_name)

    security.declareProtected('View', 'render_css')
    def render_css(self, REQUEST=None):
      """
      Generate css content which will be added inline.

      XXX key parameter may be needed.
      """
      return self.widget.render_css(self, REQUEST)

    security.declareProtected('View', 'get_css_list')
    def get_css_list(self, REQUEST=None):
      """
        Returns list of css sheets needed by the field
        to be included in global css imports
      """
      return self.widget.get_css_list(self, REQUEST)

    security.declareProtected('View', 'get_javascript_list')
    def get_javascript_list(self, REQUEST=None):
      """
        Returns list of javascript needed by the field
        to be included in global js imports
      """
      return self.widget.get_javascript_list(self, REQUEST)

    security.declareProtected('View', 'render_dict')
    def render_dict(self, value=None, REQUEST=None, key=None, **kw):
      """
      This is yet another field rendering. It is designed to allow code to
      understand field's value data by providing its type and format when
      applicable.
      """
      return self.widget.render_dict(self, value)

    security.declareProtected('View', 'render_from_request')
    def render_from_request(self, REQUEST, key_prefix=None):
        """Convenience method; render the field widget from REQUEST
        (unvalidated data), or default if no raw data is found.
        """
        return self._render_helper(self.generate_field_key(key_prefix=key_prefix), None, REQUEST)

    security.declareProtected('View', 'render_sub_field')
    def render_sub_field(self, id, value=None, REQUEST=None, key=None, render_prefix=None):
      """Render a sub field, as part of complete rendering of widget in
      a form. Works like render() but for sub field.
          Added key parameter for ERP5 in order to be compatible with listbox/matrixbox
      """
      return self._get_sub_form().get_field(id)._render_helper(
          self.generate_subfield_key(id, key=key), value, REQUEST, render_prefix)

    security.declareProtected('View', 'render_sub_field_from_request')
    def render_sub_field_from_request(self, id, REQUEST):
        """Convenience method; render the field widget from REQUEST
        (unvalidated data), or default if no raw data is found.
        """
        return self._get_sub_form().get_field(id)._render_helper(
            self.generate_subfield_key(id), None, REQUEST)

    security.declarePrivate('_validate_helper')
    def _validate_helper(self, key, REQUEST):
        value = self.validator.validate(self, key, REQUEST)
        # now call external validator after all other validation
        external_validator = self.get_value('external_validator')
        if external_validator and not external_validator(value, REQUEST):
            self.validator.raise_error('external_validator_failed', self)
        return value

    security.declareProtected('View', 'validate')
    def validate(self, REQUEST, key_prefix=None):
        """Validate/transform the field.
        """
        return self._validate_helper(
            self.generate_field_key(validation=1, key_prefix=key_prefix), REQUEST)

    security.declareProtected('View', 'need_validate')
    def need_validate(self, REQUEST, key_prefix=None):
        """Return true if validation is needed for this field.
        """
        return self.validator.need_validate(
            self, self.generate_field_key(validation=1, key_prefix=key_prefix), REQUEST)

    security.declareProtected('View', 'validate_sub_field')
    def validate_sub_field(self, id, REQUEST, key=None):
      """Validates a subfield (as part of field validation).
      """
      return self._get_sub_form().get_field(id)._validate_helper(
      self.generate_subfield_key(id, validation=1, key=key), REQUEST)

    def PrincipiaSearchSource(self):
      from Products.Formulator import MethodField
      from Products.Formulator import TALESField
      def getSearchSource(obj):
        obj_type = type(obj)
        if obj_type is MethodField.Method:
          return obj.method_name
        elif obj_type is TALESField.TALESMethod:
          return obj._text
        elif obj_type is unicode:
          return obj.encode('utf-8')
        return str(obj)
      return ' '.join(map(getSearchSource,
                         (self.values.values()+self.tales.values()+
                          self.overrides.values())))

InitializeClass(Field)

class ZMIField(
    OFS.SimpleItem.Item,
    Acquisition.Implicit,
    Persistent,
    Field,
    ):
    """Base class for a field implemented as a Python (file) product.
    """
    security = ClassSecurityInfo()

    security.declareObjectProtected('View')

    # the various tabs of a field
    manage_options = (
        {'label':'Edit',       'action':'manage_main',
         'help':('Formulator', 'fieldEdit.txt')},
        {'label':'TALES',      'action':'manage_talesForm',
         'help':('Formulator', 'fieldTales.txt')},
        {'label':'Override',    'action':'manage_overrideForm',
         'help':('Formulator', 'fieldOverride.txt')},
        {'label':'Messages',   'action':'manage_messagesForm',
         'help':('Formulator', 'fieldMessages.txt')},
        {'label':'Test',       'action':'fieldTest',
         'help':('Formulator', 'fieldTest.txt')},
        ) + OFS.SimpleItem.SimpleItem.manage_options

    security.declareProtected('View', 'title')
    def title(self):
        """The title of this field."""
        return self.get_value('title')

    # display edit screen as main management screen
    security.declareProtected('View management screens', 'manage_main')
    manage_main = DTMLFile('dtml/fieldEdit', globals())

    security.declareProtected('Change Formulator Fields', 'manage_edit')
    def manage_edit(self, REQUEST):
        """Submit Field edit form.
        """
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
            return self.manage_main(self,REQUEST,
                                    manage_tabs_message=message)

    security.declareProtected('Change Formulator Fields', 'manage_edit_xmlrpc')
    def manage_edit_xmlrpc(self, map):
        """Edit Field Properties through XMLRPC
        """
        # BEWARE: there is no validation on the values passed through the map
        self._edit(map)

    def _edit(self, result):
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
            # store keys for which we want to notify change
            if not values.has_key(key) or values[key] != value:
                changed.append(key)

        # now do actual update of values
        values.update(result)
        self.values = values

        # finally notify field of all changed values if necessary
        for key in changed:
            method_name = "on_value_%s_changed" % key
            if hasattr(self, method_name):
                getattr(self, method_name)(values[key])


    security.declarePrivate('manage_beforeDelete')
    def manage_beforeDelete(self, item, container):
        """Remove name from list if object is deleted.
        """
        # update group info in form
        if hasattr(item.aq_explicit, 'is_field'):
            container.field_removed(item.id)

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        """What happens when we add a field.
        """
        # update group info in form
        if hasattr(item.aq_explicit, 'is_field'):
            container.field_added(item.id)

    # methods screen
    security.declareProtected('View management screens',
                              'manage_overrideForm')
    manage_overrideForm = DTMLFile('dtml/fieldOverride', globals())

    security.declareProtected('Change Formulator Forms', 'manage_override')
    def manage_override(self, REQUEST):
        """Change override methods.
        """
        try:
            # validate the form and get results
            result = self.override_form.validate(REQUEST)
        except ValidationError, err:
            if REQUEST:
                message = "Error: %s - %s" % (err.field.get_value('title'),
                                              err.error_text)
                return self.manage_overrideForm(self,REQUEST,
                                                manage_tabs_message=message)
            else:
                raise

        # update overrides of field with results
        if not hasattr(self, "overrides"):
            self.overrides = result
        else:
            self.overrides.update(result)
            self.overrides = self.overrides

        if REQUEST:
            message="Content changed."
            return self.manage_overrideForm(self,REQUEST,
                                            manage_tabs_message=message)

    # tales screen
    security.declareProtected('View management screens',
                              'manage_talesForm')
    manage_talesForm = DTMLFile('dtml/fieldTales', globals())

    security.declareProtected('Change Formulator Forms', 'manage_tales')
    def manage_tales(self, REQUEST):
        """Change TALES expressions.
        """
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

    def _edit_tales(self, result):
        if not hasattr(self, 'tales'):
            self.tales = result
        else:
            self.tales.update(result)
            self.tales = self.tales

    security.declareProtected('Change Formulator Forms', 'manage_tales_xmlrpc')
    def manage_tales_xmlrpc(self, map):
        """Change TALES expressions through XMLRPC.
        """
        # BEWARE: there is no validation on the values passed through the map
        from TALESField import TALESMethod
        result = {}
        for key, value in map.items():
            if value:
                result[key] = TALESMethod(value)
            else:
                result[key] = ''  # do not create empty methods
        self._edit_tales(result)

    # display test screen
    security.declareProtected('View management screens', 'fieldTest')
    fieldTest = DTMLFile('dtml/fieldTest', globals())

    # messages screen
    security.declareProtected('View management screens', 'manage_messagesForm')
    manage_messagesForm = DTMLFile('dtml/fieldMessages', globals())

    # field list header
    security.declareProtected('View management screens', 'fieldListHeader')
    fieldListHeader = DTMLFile('dtml/fieldListHeader', globals())

    # field description display
    security.declareProtected('View management screens', 'fieldDescription')
    fieldDescription = DTMLFile('dtml/fieldDescription', globals())

    security.declareProtected('Change Formulator Fields', 'manage_messages')
    def manage_messages(self, REQUEST):
        """Change message texts.
        """
        messages = self.message_values
        unicode_mode = self.get_unicode_mode()
        for message_key in self.get_error_names():
            message = REQUEST[message_key]
            if unicode_mode:
                message = unicode(message, 'UTF-8')
            messages[message_key] = message

        self.message_values = messages
        if REQUEST:
            message="Content changed."
            return self.manage_messagesForm(self,REQUEST,
                                            manage_tabs_message=message)

    security.declareProtected('View', 'index_html')
    def index_html(self, REQUEST):
        """Render this field.
        """
        return self.render(REQUEST=REQUEST)

    security.declareProtected('Access contents information', '__getitem__')
    def __getitem__(self, key):
        return self.get_value(key)

    security.declareProtected('View management screens', 'isTALESAvailable')
    def isTALESAvailable(self):
        """Return true only if TALES is available.
        """
        try:
            from Products.PageTemplates.Expressions import getEngine
            return 1
        except ImportError:
            return 0

    def getTemplateField(self):
        return self
    getRecursiveTemplateField = getTemplateField

InitializeClass(ZMIField)
PythonField = ZMIField # NOTE: for backwards compatibility

class ZClassField(Field):
    """Base class for a field implemented as a ZClass.
    """
    pass



