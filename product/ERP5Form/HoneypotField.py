from Products.Formulator.Field import ZMIField
from Products.Formulator import Widget
from Products.Formulator.DummyField import fields
from Products.Formulator import Validator

class HoneypotWidget(Widget.Widget):
  """Honeypot widget
  """
  property_names = Widget.Widget.property_names +\
                    ['extra']
  default = Widget.TextWidget.default
  def render(self, field, key, value, REQUEST, render_prefix=None):
    """Honey pot input field.
    """
    return Widget.render_element("input",
                          type='text',
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

    message_names = Validator.Validator.message_names + ['bot_submit']
    bot_submit = 'A bot may try to submit.'

    def validate(self, field, key, REQUEST):
      value = REQUEST.get(key, None)
      default_value = field.get_value('default')
      if value is None or value != default_value:
        #this field is not sent or sent with value added by bot
        self.raise_error('bot_submit', field)
      return default_value

HoneypotValidatorInstance = HoneypotValidator()

class HoneypotField(ZMIField):
  meta_type = "HoneypotField"

  widget = HoneypotWidgetInstance
  validator = HoneypotValidatorInstance
