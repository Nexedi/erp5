from Products.Formulator.Field import ZMIField
from Products.Formulator import Widget
from Products.Formulator.DummyField import fields
from Products.Formulator import Validator
from zLOG import LOG

class GadgetWidget(Widget.TextWidget):
  """
  A widget that displays a renderjs gadget 
  """
  property_names = Widget.TextWidget.property_names + \
       ['gadget_html', 'gadget_cached', 'gadget_cache_id', 'gadget_property',
        'gadget_connection', 'gadget_id']

  gadget_html = fields.StringField('gadget_html',
                         title='Gadget Html',
                         description=("The id of the html page containing the \
                                      gadget"),
                         default='',
                         required=0)

  gadget_id = fields.StringField('gadget_id',
                         title='Gadget Id',
                         description=("The id of the gadget"),
                         default='',
                         required=0)

  gadget_cache_id = fields.StringField('gadget_cache_id',
                         title='Gadget Cache Id',
                         description=("The id of the cache in localstorage"),
                         default='',
                         required=0)

  gadget_property = fields.StringField('gadget_property',
                         title='Gadget Properties',
                         description=("Json Data used to initialize the gadget"),
                         default='',
                         required=0)

  gadget_connection = fields.StringField('gadget_connection',
                         title='Gadget Connections',
                         description=("Json Data used to define interactions"),
                         default='',
                         required=0)

  gadget_cached = fields.CheckBoxField('gadget_cached',
                         title='Gadget Cached',
                         description=("The rendering of the gadget will be \
                                       cached in localstorage."),
                         default=0,
                         required=0)

  def render(self, field, key, value, REQUEST, render_prefix=None):
      return self.render_view(field, value, REQUEST, render_prefix)

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    kw = {}
    gadget_mapping = {"gadget_cached": "data-gadget-cacheable",
                      "gadget_cache_id": "data-gadget-cache-id",
                      "gadget_html": "data-gadget",
                      "gadget_id": "id",
                      "gadget_connection": "data-gadget-connection",
                      "gadget_property": "data-gadget-property"}
    for property_name in gadget_mapping.keys():
      property_value = field.get_value(property_name)
      if property_value or property_name=="gadget_html":
        kw[gadget_mapping[property_name]] = property_value
    return Widget.render_element("div",
                      **kw)

GadgetWidgetInstance = GadgetWidget()

class GadgetField(ZMIField):
    """ Gadget field
    """
    meta_type = "GadgetField"

    widget = GadgetWidgetInstance
    validator = Validator.SuppressValidatorInstance
