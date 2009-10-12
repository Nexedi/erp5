import string
from DummyField import fields
import Widget, Validator
from Persistence import Persistent
import Acquisition
from Field import ZMIField
from AccessControl import getSecurityManager

class MethodWidget(Widget.TextWidget):
    default = fields.MethodField('default',
                                 title='Default',
                                 default="",
                                 required=0)
    
    def render(self, field, key, value, REQUEST, render_prefix=None):
        if value == None:
            method_name = field.get_value('default')
        else:
            if value != "":
                method_name = value.method_name
            else:
                method_name = ""
        return Widget.TextWidget.render(self, field, key, method_name, REQUEST)

MethodWidgetInstance = MethodWidget()

class Method(Persistent, Acquisition.Implicit):
    """A method object; calls method name in acquisition context.
    """
    def __init__(self, method_name):
        self.method_name = method_name
        
    def __call__(self, *arg, **kw):
        # get method from acquisition path
        method = getattr(self, self.method_name)
        # check if we have 'View' permission for this method
        # (raises error if not)
        getSecurityManager().checkPermission('View', method)
        # okay, execute it with supplied arguments
        return apply(method, arg, kw)

class BoundMethod(Method):
    """A bound method calls a method on a particular object.
    Should be used internally only.
    """
    def __init__(self, object, method_name):
        BoundMethod.inheritedAttribute('__init__')(self, method_name)
        self.object = object
          
    def __call__(self, *arg, **kw):
        method = getattr(self.object, self.method_name)
        return apply(method, arg, kw)
    
class MethodValidator(Validator.StringBaseValidator):

    def validate(self, field, key, REQUEST):
        value = Validator.StringBaseValidator.validate(self, field, key,
                                                       REQUEST)

        if value == "" and not field.get_value('required'):
            return value

        return Method(value)
    
MethodValidatorInstance = MethodValidator()

class MethodField(ZMIField):
    meta_type = 'MethodField'

    internal_field = 1

    widget = MethodWidgetInstance
    validator = MethodValidatorInstance
    
    
