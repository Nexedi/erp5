
class BasicForm:
    """
    Use BasicForm to construct and use Formulator forms from
    Python code.
    """

    __extends__ = ('Formulator.Form.Form',)

    def add_field(field, group=None):
        """
        Add a field to a group on
        the form. The 'group' argument is optional, and if no group is
        given the field is added to the first group. The field is
        always added to the bottom of the group.

        Permission -- 'Change Formulator Forms'
        """

    def add_fields(fields, group=None):
        """
        Add a list of fields to a on the form. The 'group' argument is
        optional; if no group is given the fields are added to the first
        group. Fields are added in the order given to the bottom of the
        group.

        Permission -- 'Change Formulator Forms'
        """

    def remove_field(field):
        """
        Remove a particular field from the form.

        Permission -- 'Change Formulator Forms'
        """




