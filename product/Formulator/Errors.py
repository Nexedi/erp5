"""Exception Classes for Formulator"""

# These classes are placed here so that they can be imported into TTW Python
# scripts. To do so, add the following line to your Py script:
# from Products.Formulator.Errors import ValidationError, FormValidationError

from Products.PythonScripts.Utility import allow_class
from AccessControl import ClassSecurityInfo

class FormValidationError(Exception):

    def __init__(self, errors, result):
        Exception.__init__(self,"Form Validation Error")
        self.errors = errors
        self.result = result

allow_class(FormValidationError)

class ValidationError(Exception):

    security = ClassSecurityInfo()

    def __init__(self, error_key, field, error_text=None):
        Exception.__init__(self, error_key)
        self.error_key = error_key
        self.field_id = field.id
        self.field = field
        if error_text is not None:
          self.error_text = error_text
          self.is_message_to_translate = False
        else:
          self.error_text = field.get_error_message(error_key)
          self.is_message_to_translate = True

    security.declarePublic('getMessage')
    def getMessage(self, translation_service=None):
      if not self.is_message_to_translate:
        return self.error_text
      if translation_service is None:
        return self.error_text
      return translation_service(self.error_text)

allow_class(ValidationError)

class FieldDisabledError(AttributeError):

    def __init__(self, error_key, field):
        AttributeError.__init__(self, error_key)
        self.field_id = field.id
        self.field = field

allow_class(FieldDisabledError)
