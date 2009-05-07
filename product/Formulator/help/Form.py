class Form:
    """A Formulator Form; this is the base class of all forms.
    """
    def move_field_up(field_id, group):
        """
        Move the field with 'field_id' up in the group with name 'group'.
        Returns 1 if move succeeded, 0 if it failed.
        
        Permission -- 'Change Formulator Forms'
        """

    def move_field_down(field_id, group):
        """
        Move the field with 'field_id' down in the group with name 'group'.
        Returns 1 if move succeeded, 0 if it failed.
        
        Permission -- 'Change Formulator Forms'
        """

    def move_field_group(field_ids, from_group, to_group):
        """
        Move a number of field ids in the list 'field_ids' from 'from_group'
        to 'to_group'.
        Returns 1 if move succeeded, 0 if it failed.

        Permission -- 'Change Formulator Forms'
        """

    def add_group(group):
        """
        Add a new group with the name 'group'. The new group must have
        a unique name in this form and will be added to the bottom of the
        list of groups.
        
        Returns 1 if the new group could be added, 0 if it failed.

        Permission -- 'Change Formulator Forms'
        """

    def remove_group(group):
        """
        Remove an existing group with the name 'group'. All fields that
        may have been in the group will be moved to the end of the
        first group. The first group can never be removed.

        Returns 1 if the group could be removed, 0 if it failed.

        Permission -- 'Change Formulator Forms'
        """

    def rename_group(group, name):
        """
        Give an existing group with the name 'group' a new name. The
        new name must be unique.

        Returns 1 if the rename succeeded, 0 if it failed.

        Permission -- 'Change Formulator Forms'
        """

    def move_group_up(group):
        """
        Move the group with name 'group' up in the list of groups.

        Returns 1 if the move succeeded, 0 if it failed

        Permission -- 'Change Formulator Forms'
        """

    def move_group_down(group):
        """
        Move the group with name 'group' down in the list of groups.

        Returns 1 if the move succeeded, 0 if it failed.

        Permission -- 'Change Formulator Forms'
        """
        
    def get_fields():
        """
        Returns a list of all fields in the form (in all groups). The
        order of the fields will be field order in the groups, and the
        groups will be in the group order.

        Permission -- 'View'
        """

    def get_field_ids():
        """
        As 'get_fields()', but instead returns a list of ids of all the fields.

        Permission -- 'View'
        """

    def get_fields_in_group(group):
        """
        Get a list in field order in a particular group.

        Permission -- 'View'
        """

    def has_field(id):
        """
        Check whether the form has a field of a certain id. Returns true
        if the field exists.

        Permission -- 'View'
        """

    def get_field(id):
        """
        Get a field with a certain id.

        Permission -- 'View'
        """

    def get_groups():
        """
        Get a list of all groups in the form, in group order.

        Permission -- 'View'
        """

    def render(self, dict=None, REQUEST=None):
        """
        Returns a basic HTML rendering (in a table) of this form.
        For more sophisticated renderings you'll have to write
        DTML or ZPT code yourself.

        You can supply an optional 'dict' argument; this should be a
        dictionary ('_', the namespace stack, is legal). The
        dictionary can contain data that should be pre-filled in the
        form (indexed by field id). The optional 'REQUEST' argument
        can contain raw form data, which will be used in case nothing
        can be found in the dictionary (or if the dictionary does not
        exist).

        Permission -- 'View'
        """
        
    def validate(REQUEST):
        """
        Validate all the fields in this form, looking in REQUEST for
        the raw field values. If any validation error occurs,
        ValidationError is raised and validation is stopped.

        Returns a dictionary with as keys the field ids and as values
        the validated and processed field values.

        Exceptions that are raised can be caught in the following way
        (also in through the web Python scripts)::

          from Products.Formulator.Errors import ValidationError
          try:
             myform.validate(REQUEST)
          except ValidationError, e:
             print 'error' # handle error 'e'
          
        Permission -- 'View'
        """

    def validate_to_request(REQUEST):
        """
        Validate all the fields in this form, looking in REQUEST for
        the raw field values. If any validation error occurs,
        ValidationError is raised and validation is stopped.

        Returns a dictionary with as keys the field ids and as values
        the validated and processed field values. In addition, this
        result will also be added to REQUEST (also with the field ids
        as keys).

        Exceptions that are raised can be caught in the following way
        (also in through the web Python scripts)::

          from Products.Formulator.Errors import ValidationError
          try:
             myform.validate_to_request(REQUEST)
          except ValidationError, e:
             print 'error' # handle error 'e'

        Permission -- 'View'
        """

    def validate_all(REQUEST):
        """
        Validate all the fields in this form, looking in REQUEST for
        the raw field values. If any ValidationError occurs, they are
        caught and added to a list of errors; after all validations a
        FormValidationError is then raised with this list of
        ValidationErrors as the 'errors' attribute.

        Returns a dictionary with as keys the field ids and as values
        the validated and processed field values.

        Exceptions that are raised can be caught in the following way
        (also in through the web Python scripts)::

          from Products.Formulator.Errors import ValidationError, FormValidationError
          try:
             myform.validate_all(REQUEST)
          except FormValidationError, e:
             print 'error' # handle error 'e', which contains 'errors'

        Permission -- 'View'
        """
        
    def validate_all_to_request(REQUEST):
        """
        Validate all the fields in this form, looking in REQUEST for
        the raw field values. If any ValidationError occurs, they are
        caught and added to a list of errors; after all validations a
        FormValidationError is then raised with this list of
        ValidationErrors as the 'errors' attribute.

        Returns a dictionary with as keys the field ids and as values
        the validated and processed field values. In addition, the
        validated fields will be added to REQUEST, as in
        'validate_to_request()'. This will always be done for all
        fields that validated successfully, even if the validation of
        other fields failed and a FormValidationError is raised.

        Exceptions that are raised can be caught in the following way
        (also in through the web Python scripts)::

          from Products.Formulator.Errors import ValidationError, FormValidationError
          try:
             myform.validate_all_to_request(REQUEST)
          except FormValidationError, e:
             print 'error' # handle error 'e', which contains 'errors'

        Permission -- 'View'
        """

    def session_store(session, REQUEST):
        """
        Store any validated form data in REQUEST in a session object
        (Core Session Tracking).

        Permission -- 'View'
        """

    def session_retrieve(session, REQUEST):
        """
        Retrieve validated form data from session (Core Session
        Tracking) into REQUEST.

        Permission -- 'View'
        """
        
    def header():
        """
        Get the HTML code for the start of a form. This produces a
        '<form>' tag with the 'action' and 'method' attributes
        that have been set in the Form.

        Permission -- 'View'
        """

    def footer():
        """
        Get the code for the end of the form ('</form>').

        Permission -- 'View'
        """



