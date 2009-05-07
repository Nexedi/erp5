"""
ProductForm.py

This file is an adaptation from part of Plone's FormTool.py tool.
It provides a wrapping around Formulator.BasicForm, allowing it
to be created inside a product but used outside it.
"""

import string

from AccessControl import ClassSecurityInfo

from Globals import InitializeClass
import FormValidationError, BasicForm
import StandardFields

class ProductForm(BasicForm):
    """Wraps Formulator.BasicForm and provides some convenience methods that
       make BasicForms easier to work with from external methods."""
    security = ClassSecurityInfo()
    security.declareObjectPublic()

    security.declareProtected('View', 'get_field')
    def get_field(self, id):
        """Get a field of a certain id, wrapping in context of self
        """
        return self.fields[id].__of__(self)

    security.declarePublic('addField')
    def addField(self, field_id, fieldType, group=None, **kwargs):
        """
        Adds a Formulator Field to the wrapped BasicForm.

        fieldType: An abbreviation for the Field type.
            'String' generates a StringField, 'Int' generates an IntField, etc.
            Uses a StringField if no suitable Field type is found.
        field_id: Name of the variable in question.  Note that Formulator adds
            'field_' to variable names, so you will need to refer to the variable
            foo as field_foo in form page templates.
        group: Formulator group for the field.

        Additional arguments: addField passes all other arguments on to the
            new Field object.  In addition, it allows you to modify the
            Field's error messages by passing in arguments of the form
            name_of_message = 'New error message'

        See Formulator.StandardFields for details.
        """

        if fieldType[-5:]!='Field':
            fieldType = fieldType+'Field'

        formulatorFieldClass = None

        if hasattr(StandardFields, fieldType):
            formulatorFieldClass = getattr(StandardFields, fieldType)
        else:
            formulatorFieldClass = getattr(StandardFields, 'StringField')

        # pass a title parameter to the Field
        kwargs['title'] = field_id

        fieldObject = apply(formulatorFieldClass, (field_id, ), kwargs)

        # alter Field error messages
        # Note: This messes with Formulator innards and may break in the future.
        # Unfortunately, Formulator doesn't do this already in Field.__init__
        # and there isn't a Python-oriented method for altering message values
        # so at present it's the only option.
        for arg in kwargs.keys():
            if fieldObject.message_values.has_key(arg):
                fieldObject.message_values[arg] = kwargs[arg]

        # Add the new Field to the wrapped BasicForm object
        BasicForm.add_field(self, fieldObject, group)


    security.declarePublic('validate')
    def validate(self, REQUEST, errors=None):
        """
        Executes the validator for each field in the wrapped BasicForm.add_field
        Returns the results in a dictionary.
        """

        if errors is None:
            errors = REQUEST.get('errors', {})

        # This is a bit of a hack to make some of Formulator's quirks
        # transparent to developers.  Formulator expects form fields to be
        # prefixed by 'field_' in the request.  To remove this restriction,
        # we mangle the REQUEST, renaming keys from key to 'field_' + key
        # before handing off to Formulator's validators.  We will undo the
        # mangling afterwards.
        for field in self.get_fields():
            key = field.id
            value = REQUEST.get(key)
            if value:
                # get rid of the old key
                try:
                    del REQUEST[key]
                except:
                    pass
                # move the old value to 'field_' + key
                # if there is already a value at 'field_' + key,
                #    move it to 'field_field_' + key, and repeat
                #    to prevent key collisions
                newKey = 'field_' + key
                newValue = REQUEST.get(newKey)
                while newValue:
                    REQUEST[newKey] = value
                    newKey = 'field_' + newKey
                    value = newValue
                    newValue = REQUEST.get(newKey)
                REQUEST[newKey] = value

        try:
            result=self.validate_all(REQUEST)
        except FormValidationError, e:
            for error in e.errors:
                errors[error.field.get_value('title')]=error.error_text

        # unmangle the REQUEST
        for field in self.get_fields():
            key = field.id
            value = 1
            while value:
                key = 'field_' + key
                value = REQUEST.get(key)
                if value:
                    REQUEST[key[6:]] = value
                    try:
                        del REQUEST[key]
                    except:
                        pass

        return errors

InitializeClass(ProductForm)
