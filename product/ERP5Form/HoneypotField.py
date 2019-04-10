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

    message_names = Validator.Validator.message_names + ['unexpected_value']
    unexpected_value = 'Unexpected value'

    def validate(self, field, key, REQUEST):
      value = REQUEST.get(key, None)
      if value is None or value != '':
        #this field is not sent or sent with value
        self.raise_error('unexpected_value', field)
      return value

HoneypotValidatorInstance = HoneypotValidator()

class HoneypotField(ZMIField):
  #Field to stop auto bot submit
  #https://nedbatchelder.com/text/stopbots.html
  meta_type = "HoneypotField"

  widget = HoneypotWidgetInstance
  validator = HoneypotValidatorInstance
