from Products.Formulator.Field import ZMIField
from Products.Formulator import Widget
from Products.Formulator.DummyField import fields
from Products.Formulator import Validator
from zLOG import LOG, ERROR
from cStringIO import StringIO
from json import dumps
from Acquisition import aq_base
from urlparse import urljoin

class GadgetWidget(Widget.Widget):
  """
  A widget that displays a renderjs gadget
  """
  property_names = Widget.Widget.property_names + \
       ['gadget_url', 'js_sandbox', 'extra', 'renderjs_extra']

  default = Widget.TextWidget.default

  renderjs_extra = fields.ListTextAreaField('renderjs_extra',
                          title="RenderJS extra",
                                 description=(
        "More parameters passed to the renderJS's render method."),
                                 default=[],
                                 required=0)

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
    kw = {
      'data-gadget-sandbox': field.get_value('js_sandbox'),
      # Duplicate the absolute url logic of xhtml style
      'data-gadget-url': urljoin(field.getPortalObject().absolute_url() + '/', field.get_value('gadget_url')),
      'data-gadget-value': value,
      'data-gadget-renderjs-extra': dumps(dict(field.get_value('renderjs_extra')))
    }
    if key is not None:
      kw['data-gadget-editable'] = key
    return Widget.render_element("div", extra=field.get_value('extra'), **kw)

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

    property_names = Validator.Validator.property_names + [
      'data_url',
      'validator_form_id',
      'validator_field_id'
    ]

    data_url = fields.CheckBoxField('data_url',
                                title='Data Url',
                                description=(
                                  "Checked if gadget return data url."),
                                default=0)

    validator_form_id = fields.StringField(
      'validator_form_id',
      title='Validator Form ID',
      description= "ID of the validator field's form. Default is the current form",
      default="",
      display_width=40,
      required=0
    )

    validator_field_id = fields.StringField(
      'validator_field_id',
      title='Validator Field ID',
      description= "ID of the validator field.",
      default="",
      display_width=40,
      required=0
    )

    message_names = Validator.Validator.message_names + ['no_validator']

    no_validator = 'Does not support this operation.'

    def getValidatorField(self, field):
      """Get an external validator field located in the same form.
      """
      field_id = field.id
      validator_form_id = field.get_value('validator_form_id')
      validator_field_id = field.get_value('validator_field_id')

      validator_form = field.aq_parent
      if (validator_form_id):
        if '/' in validator_form_id:
          portal = field.getPortalObject()
          portal_skins = portal.portal_skins
          # If a / is in the form_id, it means that skin_folder is explicitly
          # defined. If so, prevent acquisition to get the form.
          aq_validator_form = aq_base(portal_skins).unrestrictedTraverse(validator_form_id, None)
          if aq_validator_form is not None:
            validator_form = portal_skins.unrestrictedTraverse(validator_form_id)
        else:
          validator_form = getattr(validator_form, validator_form_id, None)

      if (validator_form is not None) and validator_field_id:
        if validator_form.has_field(validator_field_id,
                                    include_disabled=1):
          return validator_form.get_field(validator_field_id,
                                          include_disabled=1)
      return None

    def validate(self, field, key, REQUEST):
      validator_field = self.getValidatorField(field)
      if validator_field is None:
        # not editable if no validator
        self.raise_error('no_validator', field)
      else:
        value = validator_field._validate_helper(key, REQUEST)
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
