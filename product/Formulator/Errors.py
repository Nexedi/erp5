"""Exception Classes for Formulator"""

# These classes are placed here so that they can be imported into TTW Python
# scripts. To do so, add the following line to your Py script:
# from Products.Formulator.Errors import ValidationError, FormValidationError

from Products.PythonScripts.Utility import allow_class

class FormValidationError(Exception):

    def __init__(self, errors, result):
        Exception.__init__(self,"Form Validation Error")
        self.errors = errors
        self.result = result
        
allow_class(FormValidationError)

class ValidationError(Exception):
    
    def __init__(self, error_key, field):
        Exception.__init__(self, error_key)
        self.error_key = error_key
        self.field_id = field.id
        self.field = field
        self.error_text = field.get_error_message(error_key)

allow_class(ValidationError)

class FieldDisabledError(AttributeError):

    def __init__(self, error_key, field):
        AttributeError.__init__(self, error_key)
        self.field_id = field.id
        self.field = field

allow_class(FieldDisabledError)
