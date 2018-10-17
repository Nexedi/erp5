from Products.Formulator.Field import ZMIField
from Products.Formulator import Widget
from Products.Formulator.DummyField import fields
from Products.Formulator import Validator

class HoneypotWidget(Widget.Widget):
  """Honeypot widget
  """
  property_names = Widget.Widget.property_names +\
                    ['input_type', 'extra']

  default = Widget.TextWidget.default

  input_type = fields.StringField('input_type',
                                  title='Input type',
                                  description=(
      "The type of the input field like 'color', 'date', 'email' etc."
      "Note input types, not supported by old web browsers, will behave "
      "as input type text."),
                                  default="text",
                                  required=0)

  def render(self, field, key, value, REQUEST, render_prefix=None):
    """Honey pot input field.
    """
    input_type = field.get_value('input_type') or 'text'
    return Widget.render_element("input",
                          type=input_type,
                          name=key,
                          css_class=field.get_value('css_class'),
                          value=value,
                          extra=field.get_value('extra'))

  def render_view(self, field, value, REQUEST=None, render_prefix=None, key=None):
    return self.render(field, key, value, REQUEST, render_prefix)

HoneypotWidgetInstance = HoneypotWidget()

class HoneypotValidator(Validator.Validator):
    """Simple honeypot validator.
    """
    property_names = Validator.Validator.property_names

    message_names = Validator.Validator.message_names + ['no_validator']
    no_validator = 'A bot may try to submit.'

    def validate(self, field, key, REQUEST):
      # We had to add this patch for hidden fields of type "list"
      value = REQUEST.get(key, REQUEST.get('default_%s' % (key, )))
      default_value = field.get_value('default')
      if value is None or value != default_value:
        #this field is not sent or sent with value added by bot
        self.raise_error('no_validator', field)
      return default_value

HoneypotValidatorInstance = HoneypotValidator()

class HoneypotField(ZMIField):
  meta_type = "HoneypotField"

  widget = HoneypotWidgetInstance
  validator = HoneypotValidatorInstance
