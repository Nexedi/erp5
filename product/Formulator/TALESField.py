import string
from DummyField import fields
import Widget, Validator
from Globals import Persistent
import Acquisition
from Field import ZMIField
from AccessControl import getSecurityManager
   
class TALESWidget(Widget.TextWidget):
  default = fields.MethodField('default',
                                title='Default',
                                default="",
                                required=0)

  def render(self, field, key, value, REQUEST, render_prefix=None):
    if value == None:
      text = field.get_value('default')
    else:
      if value != "":
        text = value._text
      else:
        text = ""
    return Widget.TextWidget.render(self, field, key, text, REQUEST)

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    """
    Render TALES as read only
    """
    if value == None:
      text = field.get_value('default', REQUEST=REQUEST)
    else:
      if value != "":
        text = value._text
      else:
        text = ""
    return text

TALESWidgetInstance = TALESWidget()

class TALESNotAvailable(Exception):
    pass

try:
    # try to import getEngine from TALES
    from Products.PageTemplates.Expressions import getEngine
    
    class TALESMethod(Persistent, Acquisition.Implicit):
        """A method object; calls method name in acquisition context.
        """
        def __init__(self, text):
            self._text = text
            
        def __call__(self, **kw):
            expr = getattr(self, '_v_expr', None)
            if expr is None:
                self._v_expr = expr = getEngine().compile(self._text)
            return getEngine().getContext(kw).evaluate(expr)

            # check if we have 'View' permission for this method
            # (raises error if not)
            # getSecurityManager().checkPermission('View', method)

    TALES_AVAILABLE = 1
    
except ImportError:
    # cannot import TALES, so supply dummy TALESMethod
    class TALESMethod(Persistent, Acquisition.Implicit):
        """A dummy method in case TALES is not available.
        """
        def __init__(self, text):
            self._text = text

        def __call__(self, **kw):
            raise TALESNotAvailable
    TALES_AVAILABLE = 0
    
class TALESValidator(Validator.StringBaseValidator):

    def validate(self, field, key, REQUEST):
        value = Validator.StringBaseValidator.validate(self, field, key,
                                                       REQUEST)

        if value == "" and not field.get_value('required'):
            return value

        return TALESMethod(value)
    
TALESValidatorInstance = TALESValidator()

class TALESField(ZMIField):
    meta_type = 'TALESField'

    internal_field = 1

    widget = TALESWidgetInstance
    validator = TALESValidatorInstance
    
    
