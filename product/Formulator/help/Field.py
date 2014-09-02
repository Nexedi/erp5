class Field:
    """Formulator field base class; shared functionality of all
    fields.
    """
    def initialize_values(dict):
        """
        Initialize the values of field properties. 'dict' is a
        dictionary. A dictionary entry has as key the property id,
        and as value the value the property should take initially.
        If there is no entry in the dictionary for a particular
        property, the default value for that property will be used.
        All old property values will be cleared.

        Permission -- 'Change Formulator Fields'
        """

    def initialize_overrides():
        """
        Clear (initialize to nothing) overrides for all properties.

        Permission -- 'Change Formulator Fields'
        """

    def has_value(id):
        """
        Returns true if a property with name 'id' exists.

        Permission -- 'Access contents information'
        """

    def get_orig_value(id):
        """
        Get value of property without looking at possible overrides.

        Permission -- 'Access contents information'
        """

    def get_value(id, **kw):
        """
        Get property value for an id. Call override if override is
        defined, otherwise use property value. Alternatively the
        dictionary interface can also be used ('__getitem__()').

        Keywords arguments can optionally be passed, which will end up
        in the namespace of any TALES expression that gets called.

        Permission -- 'Access contents information'
        """

    def __getitem__(self, key):
        """
        Get property value for an id. Call override if override is
        defined, otherwise use property value. Alternatively
        'get_value()' can be used to do this explicitly.

        In Python, you can access property values using::

          form.field['key']

        and in Zope Page Templates you can use the following path
        notation::

          form/field/key

        Permission -- 'Access contents information'
        """

    def get_override(id):
        """
        Get the override method for an id, or empty string
        if no such override method exists.

        Permission -- 'Access contents information'
        """

    def is_required():
        """
        A utility method that returns true if this field is required.
        (checks for 'required' property).

        Permission -- 'Access contents information'
        """

    def get_error_names():
        """
        Get all keys of error messages that the validator
        of this field provides.

        Permission -- 'View management screens'
        """

    def get_error_message(name):
        """
        Get the contents of a particular error message with key
        'name'.

        Permission -- 'View management screens'
        """

    def render(value=None, REQUEST=None):
        """
        Get the rendered HTML for the widget of this field, to
        display the fields on a form.

        'value' -- If the 'value' parameter is not None, this will be
        the pre-filled value of the field on the form.

        'REQUEST' -- If the 'value' parameter is 'None' and 'REQUEST' is
        supplied, raw (unvalidated) values will be looked up in
        'REQUEST' to display in the field.

        If neither 'value' or 'REQUEST' are supplied, the field's
        default value will be used instead.

        Permission -- 'View'
        """

    def render_from_request(REQUEST):
        """
        A convenience method to render the field widget using
        the raw data from 'REQUEST' if any is available. The field's
        default value will be used if no raw data can be found.

        Pemrissions -- 'View'
        """

    def render_sub_field(id, value=None, REQUEST=None):
        """
        Render a sub field of this field. This is used by composite
        fields that are composed of multiple sub fields such as
        'DateTimeField'. 'id' is the id of the sub field. 'value' and
        'REQUEST' work like in 'render()', but for the sub field.

        Permission -- 'View'
        """

    def render_sub_field_from_request(id, REQUEST):
        """
        A convenience method to render a sub field widget from
        'REQUEST' (unvalidated data).

        Permission -- 'View'
        """

    def validate(REQUEST):
        """
        Validate this field using the raw unvalidated data found
        in 'REQUEST'.

        Returns the validated and processed value, or raises a
        ValidationError.

        Permission -- 'View'
        """

    def validate_sub_field(id, REQUEST):
        """
        Validate a sub field of this field using the raw unvalidated
        data found in 'REQUEST'. This is used by composite fields
        composed of multiple sub fields such as 'DateTimeField'.

        Returns the validated and processed value, or raises a
        ValidationError.

        Permission -- 'View'
        """

    def render_view(value):
        """
        Render supplied value for viewing, not editing. This can be used
        to show form results, for instance.

        Permission -- 'View'
        """





