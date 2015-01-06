from Products.Formulator.Field import ZMIField
from Products.Formulator import Widget
from Products.Formulator.DummyField import fields
from Products.Formulator import Validator
from zLOG import LOG, ERROR
from cStringIO import StringIO

class GadgetWidget(Widget.TextWidget):
  """
  A widget that displays a renderjs gadget
  """
  property_names = Widget.TextWidget.property_names + \
       ['gadget_url', 'js_sandbox']

  gadget_url = fields.StringField('gadget_url',
                         title='Gadget Url',
                         description=("The url of the html page containing the \
                                      gadget"),
                         default='',
                         required=0)

  js_sandbox = fields.StringField('js_sandbox',
                          title='Gadget Sandbox',
                          description=("Gadget sandbox"),
                          default='',
                          required=0)

  def render(self, field, key, value, REQUEST, render_prefix=None):
      return self.render_view(field, value, REQUEST, render_prefix, key)

  def render_view(self, field, value, REQUEST=None, render_prefix=None, key=None):
     kw = {}
     kw['data-gadget-url'] = field.get_value('gadget_url')
     kw['data-gadget-scope'] = field.id
     if key is not None:
       kw['data-gadget-editable'] = key
     kw['class'] = "gadget"
     kw['data-gadget-value'] = value
     kw['data-gadget-sandbox'] = field.get_value('js_sandbox')
     return Widget.render_element("div",
                      **kw)

  def get_javascript_list(self, field, REQUEST=None):
     """
     Returns list of javascript needed by the widget
     """
     js_list = ['rsvp.js', 'renderjs.js', 'erp5_gadgetfield.js']
     result = []
     try:
       for js_file in js_list:
         result.append(field.restrictedTraverse(js_file).absolute_url())
     except KeyError:
       LOG('keyError:', ERROR, 'Error Value: %s' % js_file)
       return []
     return result

class GadgetFieldValidator(Validator.Validator):

    property_names = Validator.Validator.property_names + ['data_url']

    data_url = fields.CheckBoxField('data_url',
                                title='Data Url',
                                description=(
                                  "Checked if gadget return data url."),
                                default=0)

    def validate(self, field, key, REQUEST):
        value = REQUEST.get(key, None)
        if value is not None:
          if field.get_value('data_url'):
            value=value.split(",")[1]
            return StringIO(value.decode('base64'))
          return value


GadgetWidgetInstance = GadgetWidget()
GadgetFieldValidatorInstance = GadgetFieldValidator()

class GadgetField(ZMIField):
    meta_type = "GadgetField"

    widget = GadgetWidgetInstance
    validator = GadgetFieldValidatorInstance
