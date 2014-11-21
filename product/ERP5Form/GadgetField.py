from Products.Formulator.Field import ZMIField
from Products.Formulator import Widget
from Products.Formulator.DummyField import fields
from Products.Formulator import Validator
from zLOG import LOG, ERROR

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
       kw['editable'] = key
     kw['class'] = "gadget"
     kw['value'] = value
     kw['data-gadget-sandbox'] = field.get_value('js_sandbox')
     return Widget.render_element("section",
                      **kw)

  def get_javascript_list(self, field, REQUEST=None):
    """
    Returns list of javascript needed by the widget
    """
    js_list = ['rsvp.js', 'renderjs.js', 'erp5_gadgetfield.js',
               'jio_sha256.amd.js', 'jio.js']
    result = []
    try:
      for js_file in js_list:
        result.append(field.restrictedTraverse(js_file).absolute_url()) 
    except KeyError:
      LOG('keyError:', ERROR, 'Error Value: %s' % js_file)
      return []

    return result


GadgetWidgetInstance = GadgetWidget()

class GadgetField(ZMIField):
    meta_type = "GadgetField"

    widget = GadgetWidgetInstance
    validator = Validator.SuppressValidatorInstance
