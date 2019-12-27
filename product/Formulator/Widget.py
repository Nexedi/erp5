# -*- coding: utf-8 -*-
import string
from DummyField import fields
from DocumentTemplate.DT_Util import html_quote
from DateTime import DateTime, Timezones
from cgi import escape
import types
from DocumentTemplate.ustr import ustr
from urlparse import urljoin
from lxml import etree
from lxml.etree import Element, SubElement
from lxml.builder import ElementMaker
import re

DRAW_URI = 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0'
TEXT_URI = 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
FORM_URI = 'urn:oasis:names:tc:opendocument:xmlns:form:1.0'
OFFICE_URI = 'urn:oasis:names:tc:opendocument:xmlns:office:1.0'
STYLE_URI = 'urn:oasis:names:tc:opendocument:xmlns:style:1.0'

NSMAP = {
          'draw': DRAW_URI,
          'text': TEXT_URI,
          'form': FORM_URI,
          'office': OFFICE_URI,
          'style': STYLE_URI,
        }

EForm = ElementMaker(namespace=FORM_URI, nsmap=NSMAP)

RE_OOO_ESCAPE = re.compile(r'([\n\t])?([^\n\t]*)')
class OOoEscaper:
  """Replacement function to use inside re.sub expression.
  This function replace \t by <text:tab/>
                        \n by <text:line-break/>
  The parent node is passed to the constructor.
  """
  def __init__(self, parent_node):
    self.parent_node = parent_node
  def __call__(self, match_object):
    match_value = match_object.group(1)
    if match_value is None:
      self.parent_node.text = match_object.group(2)
    elif match_value == '\n':
      line_break = SubElement(self.parent_node, '{%s}%s' % (TEXT_URI, 'line-break'))
      line_break.tail = match_object.group(2)
    elif match_value == '\t':
      line_break = SubElement(self.parent_node, '{%s}%s' % (TEXT_URI, 'tab'))
      line_break.tail = match_object.group(2)

def convertToString(value):
  if not isinstance(value, (str, unicode)):
    return str(value)
  return value

class Widget:
  """A field widget that knows how to display itself as HTML.
  """

  property_names = ['title', 'description',
                    'default', 'css_class', 'alternate_name',
                    'hidden']

  title = fields.StringField('title',
                              title='Title',
                              description=(
      "The title of this field. This is the title of the field that "
      "will appear in the form when it is displayed. Required."),
                              default="",
                              required=1)

  description = fields.TextAreaField('description',
                                      title='Description',
                                      description=(
      "Description of this field. The description property can be "
      "used to add a short description of what a field does; such as "
      "this one."),
                                      default="",
                                      width="20", height="3",
                                      required=0)

  css_class = fields.StringField('css_class',
                                  title='CSS class',
                                  description=(
      "The CSS class of the field. This can be used to style your "
      "formulator fields using cascading style sheets. Not required."),
                                  default="",
                                  required=0)

  alternate_name = fields.StringField('alternate_name',
                                      title='Alternate name',
                                      description=(
      "An alternative name for this field. This name will show up in "
      "the result dictionary when doing validation, and in the REQUEST "
      "if validation goes to request. This can be used to support names "
      "that cannot be used as Zope ids."),
                                      default="",
                                      required=0)

  hidden = fields.CheckBoxField('hidden',
                                title="Hidden",
                                description=(
      "This field will be on the form, but as a hidden field. The "
      "contents of the hidden field will be the default value. "
      "Hidden fields are not visible but will be validated."),
                                default=0)

  # NOTE: for ordering reasons (we want extra at the end),
  # this isn't in the base class property_names list, but
  # instead will be referred to by the subclasses.
  extra = fields.StringField('extra',
                              title='Extra',
                              description=(
      "A string containing extra HTML code for attributes. This "
      "string will be literally included in the rendered field."
      "This property can be useful if you want "
      "to add an onClick attribute to use with JavaScript, for instance."),
                              default="",
                              required=0)

  gadget_url_js = fields.StringField('gadget_url_js',
                                      title='Gadget javascript URL',
                                      description=(
      "A url specifying the customised gadget javascript in renderjs_ui."),
                              default="",
                              required=0)

  def render(self, field, key, value, REQUEST):
      """Renders this widget as HTML using property values in field.
      """
      return "[widget]"

  def render_hidden(self, field, key, value, REQUEST, render_prefix=None):
    """Renders this widget as a hidden field.
    """
    try:
      extra = field.get_value('extra')
    except KeyError:
    # In case extra is not defined as in DateTimeWidget
      extra = ''
    try:
      gadget_url_js = field.get_value('gadget_url_js')
    except KeyError:
      gadget_url_js = ''
    result = ''
    # We must adapt the rendering to the type of the value
    # in order to get the correct type back
    if isinstance(value, (tuple, list)):
      for v in value:
        result += render_element("input",
                          type="hidden",
                          name="%s:list" % key,
                          value=v,
                          extra=extra,
                          gadget_url_js=gadget_url_js)
    else:
      result = render_element("input",
                          type="hidden",
                          name=key,
                          value=value,
                          extra=extra,
                          gadget_url_js=gadget_url_js)
    return result

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    """Renders this widget for public viewing.
    """
    # default implementation
    if value is None:
      return ''
    return value

  render_pdf = render_view

  def render_html(self, *args, **kw):
    return self.render(*args, **kw)

  def render_htmlgrid(self, field, key, value, REQUEST, render_prefix=None):
    """
    render_htmlgrid returns a list of tuple (title, html render)
    """
    # XXX Calling _render_helper on the field is not optimized
    return ((field.get_value('title'),
            field._render_helper(key, value, REQUEST, render_prefix=render_prefix)),)
  def render_css(self, field, REQUEST):
    """
      Default render css for widget - to be overwritten in field classes.
      Should return valid css code as string.
      The value returned by this method will be used as inline style for a field.
    """
    pass

  def get_css_list(self, field, REQUEST):
    """
      Return CSS needed by the widget - to be overwritten in field classes.
      Should return a list of CSS file names.
      These names will be appended to global css_list and included in a rendered page.
    """
    return []

  def get_javascript_list(self, field, REQUEST):
    """
      Return JS needed by the widget - to be overwritten in field classes.
      Should return a list of javascript file names.
      These names will be appended to global js_list and included in a rendered page.
    """
    return []

  def render_dict(self, field, value):
    """
    This is yet another field rendering. It is designed to allow code to
    understand field's value data by providing its type and format when
    applicable.
    """
    return None

  def render_odt(self, field, value, as_string, ooo_builder, REQUEST,
                 render_prefix, attr_dict, local_name):
    """This render dedicated to render fields inside OOo document
      (eg. editable mode)
    """
    # XXX By default fallback to render_odt_view
    return self.render_odt_view(field, value, as_string, ooo_builder, REQUEST,
      render_prefix, attr_dict, local_name)

  def render_odt_view(self, field, value, as_string, ooo_builder, REQUEST,
                      render_prefix, attr_dict, local_name, escape=False):
    """
      Return a field value rendered in odt format as read-only mode.
      - as_string return value as string or as xml object
      - attr_dict can be used for additional attributes (like style).
      - ooo_builder wrapper of ODF zipped archive usefull to insert images
      - local_name local-name of the node returned by this render
    """
    if attr_dict is None:
      attr_dict = {}
    if isinstance(value, str):
      #required by lxml
      value = value.decode('utf-8')
    if value is None:
      value = ''
    text_node = Element('{%s}%s' % (TEXT_URI, local_name), nsmap=NSMAP)
    if escape:
      RE_OOO_ESCAPE.sub(OOoEscaper(text_node), value)
    else:
      text_node.text = value
    text_node.attrib.update(attr_dict)
    if as_string:
      return etree.tostring(text_node)
    return text_node

  def render_odt_variable(self, field, value, as_string, ooo_builder, REQUEST,
                      render_prefix, attr_dict, local_name):
    """
      Return a field value rendered in odt format as read-only mode.
      - as_string return value as string or as xml object
      - attr_dict can be used for additional attributes (like style).
      - ooo_builder wrapper of ODF zipped archive usefull to insert images
      - local_name local-name of the node returned by this render
    """
    if attr_dict is None:
      attr_dict = {}
    attr_dict['{%s}value-type' % OFFICE_URI] = 'string'
    if isinstance(value, str):
      #required by lxml
      value = value.decode('utf-8')
    if value is None:
      value = ''
    text_node = Element('{%s}%s' % (TEXT_URI, local_name), nsmap=NSMAP)
    text_node.text = value
    text_node.attrib.update(attr_dict)
    if as_string:
      return etree.tostring(text_node)
    return text_node

  def render_odg(self, field, value, as_string, ooo_builder, REQUEST,
                 render_prefix, attr_dict, local_name):
    """This render dedicated to render fields inside OOo document
      (eg. editable mode)
    """
    # XXX By default fallback to render_odg_view
    return self.render_odg_view(field, value, as_string, ooo_builder, REQUEST,
                                render_prefix, attr_dict, local_name)

  def render_odg_view(self, field, value, as_string, ooo_builder, REQUEST,
                      render_prefix, attr_dict, local_name):
    """
      Default render odg for widget - to be overwritten in field classes.
      Return a field node rendered in odg format.
      - as_string return value as string or as xml object
      - attr_dict can be used for additional attributes (like style).
      - ooo_builder wrapper of ODF zipped archive usefull to insert images
      - local_name local-name of the node returned by this render
    <draw:frame draw:name="my_string_field" draw:style-name="gr11"
                draw:text-style-name="P5" draw:layer="layout"
                svg:width="5cm" svg:height="0.725cm"
                svg:x="6.5cm" svg:y="2.5cm">
      <draw:text-box>
        <text:p text:style-name="P5">
          <text:span text:style-name="T4">my_string_field value</text:span>
        </text:p>
      </draw:text-box>
    </draw:frame>
    """
    if attr_dict is None:
      attr_dict = {}
    if isinstance(value, str):
      #required by lxml
      value = value.decode('utf-8')
    if value is None:
      value = ''
    draw_frame_tag_name = '{%s}%s' % (DRAW_URI, 'frame')
    draw_frame_node = Element(draw_frame_tag_name, nsmap=NSMAP)
    draw_frame_attribute_list = attr_dict.get(draw_frame_tag_name)
    if draw_frame_attribute_list:
      draw_frame_node.attrib.update(draw_frame_attribute_list[0])

    draw_tag_name = '{%s}%s' % (DRAW_URI, 'text-box')
    draw_node = Element(draw_tag_name, nsmap=NSMAP)
    draw_tag_attribute_list = attr_dict.get(draw_tag_name)
    if draw_tag_attribute_list:
      draw_node.attrib.update(draw_tag_attribute_list[0])

    text_p_tag_name = '{%s}%s' % (TEXT_URI, 'p')
    text_p_node = Element(text_p_tag_name, nsmap=NSMAP)
    text_p_attribute_list = attr_dict.get(text_p_tag_name)
    if text_p_attribute_list:
      text_p_node.attrib.update(text_p_attribute_list[0])

    text_span_tag_name = '{%s}%s' % (TEXT_URI, 'span')
    text_span_node =  Element(text_span_tag_name, nsmap=NSMAP)
    text_span_attribute_list = attr_dict.get(text_span_tag_name)
    if text_span_attribute_list:
      text_span_node.attrib.update(text_span_attribute_list[0])

    text_p_node.append(text_span_node)
    draw_node.append(text_p_node)
    draw_frame_node.append(draw_node)

    RE_OOO_ESCAPE.sub(OOoEscaper(text_span_node), value)
    if as_string:
      return etree.tostring(draw_frame_node)
    return draw_frame_node

class TextWidget(Widget):
  """Text widget
  """
  property_names = Widget.property_names +\
                    ['display_width', 'display_maxwidth', 'input_type', 'extra',
                     'gadget_url_js']

  default = fields.StringField('default',
                                title='Default',
                                description=(
      "You can place text here that will be used as the default "
      "value of the field, unless the programmer supplies an override "
      "when the form is being generated."),
                                default="",
                                required=0)

  display_width = fields.IntegerField('display_width',
                                      title='Display width',
                                      description=(
      "The width in characters. Required."),
                                      default=20,
                                      required=1)

  display_maxwidth = fields.IntegerField('display_maxwidth',
                                          title='Maximum input',
                                          description=(
      "The maximum input in characters that the widget will allow. "
      "Required. If set to 0 or is left empty, there is no maximum. "
      "Note that is client side behavior only."),
                                          default="",
                                          required=0)

  input_type = fields.StringField('input_type',
                                  title='Input type',
                                  description=(
      "The type of the input field like 'color', 'date', 'email' etc."
      "Note input types, not supported by old web browsers, will behave "
      "as input type text."),
                                  default="text",
                                  required=0)

  def render(self, field, key, value, REQUEST, render_prefix=None):
    """Render text input field.
    """
    display_maxwidth = field.get_value('display_maxwidth') or 0
    input_type = field.get_value('input_type') or 'text'
    if display_maxwidth > 0:
      return render_element("input",
                            type=input_type,
                            name=key,
                            css_class=field.get_value('css_class'),
                            value=value,
                            size=field.get_value('display_width'),
                            maxlength=display_maxwidth,
                            extra=field.get_value('extra'),
                            gadget_url_js=field.get_value('gadget_url_js'))
    else:
      return render_element("input",
                            type=input_type,
                            name=key,
                            css_class=field.get_value('css_class'),
                            value=value,
                            size=field.get_value('display_width'),
                            extra=field.get_value('extra'),
                            gadget_url_js=field.get_value('gadget_url_js'))

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    """Render text as non-editable.
      This renderer is designed to be type error resistant.
      in we get a non string value. It does escape the result
      and produces clean xhtml.
      Patch the render_view of TextField to enclose the value within <span> html tags if css class defined
    """
    if value is None:
      return ''
    if isinstance(value, types.ListType) or isinstance(value, types.TupleType):
      old_value = value
    else:
      old_value = [str(value)]
    value = []
    for line in old_value:
      value.append(escape(line))
    value = '<br/>'.join(value)

    extra = field.get_value('extra')
    if extra not in (None, ''):
      value = "<div %s>%s</div>" % (extra, value)

    css_class = field.get_value('css_class')
    if css_class not in ('', None):
      # All strings should be escaped before rendering in HTML
      # except for editor field
      return "<span class='%s'>%s</span>" % (css_class, value)
    return value

  def render_odt_view(self, field, value, as_string, ooo_builder, REQUEST,
                      render_prefix, attr_dict, local_name):
    if value is None:
      value = ['']
    elif not isinstance(value, (types.ListType, types.TupleType)):
      value = [str(value)]
    return Widget.render_odt_view(
      self, field, '\n'.join(value), as_string, ooo_builder, REQUEST,
      render_prefix, attr_dict, local_name, escape=True,
    )

TextWidgetInstance = TextWidget()

class PasswordWidget(TextWidget):

  def render(self, field, key, value, REQUEST, render_prefix=None):
      """Render password input field.
      """
      display_maxwidth = field.get_value('display_maxwidth') or 0
      if display_maxwidth > 0:
          return render_element("input",
                                type="password",
                                name=key,
                                css_class=field.get_value('css_class'),
                                value=value,
                                size=field.get_value('display_width'),
                                maxlength=display_maxwidth,
                                extra=field.get_value('extra'))
      else:
          return render_element("input",
                                type="password",
                                name=key,
                                css_class=field.get_value('css_class'),
                                value=value,
                                size=field.get_value('display_width'),
                                extra=field.get_value('extra'))

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
      return "[password]"

PasswordWidgetInstance = PasswordWidget()

class CheckBoxWidget(Widget):
  property_names = Widget.property_names + ['extra']

  default = fields.CheckBoxField('default',
                                  title='Default',
                                  description=(
      "Default setting of the widget; either checked or unchecked. "
      "(true or false)"),
                                  default=0)

  def render(self, field, key, value, REQUEST, render_prefix=None):
    """Render checkbox.
    """
    rendered = [render_element("input",
                              type="hidden",
                              name="default_%s:int" % (key, ),
                              value="0")
              ]

    if value:
      rendered.append(render_element("input",
                                    type="checkbox",
                                    name=key,
                                    css_class=field.get_value('css_class'),
                                    checked=None,
                                    extra=field.get_value('extra'))
                    )
    else:
      rendered.append(render_element("input",
                                    type="checkbox",
                                    name=key,
                                    css_class=field.get_value('css_class'),
                                    extra=field.get_value('extra'))
                    )
    return "".join(rendered)

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    """Render checkbox in view mode.
    """
    if value:
      return render_element("input",
                            type="checkbox",
                            css_class=field.get_value('css_class'),
                            checked='checked',
                            extra=field.get_value('extra'),
                            disabled='disabled')
    else:
      return render_element("input",
                            type="checkbox",
                            css_class=field.get_value('css_class'),
                            extra=field.get_value('extra'),
                            disabled='disabled')

  def render_odt(self, field, value, as_string, ooo_builder, REQUEST,
      render_prefix, attr_dict, local_name):
    """
    <form:checkbox form:name="is_accepted"
                   form:control-implementation="ooo:com.sun.star.form.component.CheckBox"
                   form:current-state="checked"
                   form:id="control1"
                   form:image-position="center">
      <form:properties>
        <form:property form:property-name="DefaultControl" office:value-type="string" office:string-value="com.sun.star.form.control.CheckBox"/>
        <form:property form:property-name="SecondaryRefValue" office:value-type="string" office:string-value=""/>
      </form:properties>
    </form:checkbox>
    """
    if attr_dict is None:
      attr_dict = {}
    form_node = EForm.checkbox(
                  EForm.properties(
                    EForm.property(**{'{%s}property-name' % FORM_URI: 'DefaultControl',
                                      '{%s}value-type' % OFFICE_URI: 'string',
                                      '{%s}string-value' % OFFICE_URI: 'com.sun.star.form.control.CheckBox'}),
                    EForm.property(**{'{%s}property-name' % FORM_URI: 'SecondaryRefValue',
                                      '{%s}value-type' % OFFICE_URI: 'string',
                                      '{%s}string-value' % OFFICE_URI: ''}),
                  )
                )

    current_state_attribute_name = '{%s}current-state'% FORM_URI
    if value:
      attr_dict.update({current_state_attribute_name: 'checked'})
    elif attr_dict.has_key(current_state_attribute_name):
      del attr_dict[current_state_attribute_name]
    form_node.attrib.update(attr_dict)
    if as_string:
      return etree.tostring(form_node)
    return form_node

  def render_odt_view(self, field, value, as_string, ooo_builder, REQUEST,
      render_prefix, attr_dict, local_name):
    """
    """
    if attr_dict is None:
      attr_dict = {}
    if isinstance(value, int):
      value = str(value)
    if isinstance(value, str):
      #required by lxml
      value = value.decode('utf-8')
    text_node = Element('{%s}%s' % (TEXT_URI, local_name), nsmap=NSMAP)
    text_node.text = value
    text_node.attrib.update(attr_dict)
    if as_string:
      return etree.tostring(text_node)
    return text_node

  def render_odt_variable(self, field, value, as_string, ooo_builder, REQUEST,
                      render_prefix, attr_dict, local_name):
    """
      Return a field value rendered in odt format as read-only mode.
      - as_string return value as string or as xml object
      - attr_dict can be used for additional attributes (like style).
      - ooo_builder wrapper of ODF zipped archive usefull to insert images
      - local_name local-name of the node returned by this render
    """
    if attr_dict is None:
      attr_dict = {}
    attr_dict['{%s}value-type' % OFFICE_URI] = 'boolean'
    text_node = Element('{%s}%s' % (TEXT_URI, local_name), nsmap=NSMAP)
    attr_dict['{%s}boolean-value' % NSMAP['office']] = str(value).lower()
    text_node.text = str(value).upper()
    text_node.attrib.update(attr_dict)
    if as_string:
      return etree.tostring(text_node)
    return text_node

  def render_odg_view(self, field, value, as_string, ooo_builder, REQUEST,
                      render_prefix, attr_dict, local_name):
    """Convert boolean value into integer (1/0) then into string.
    """
    if value is None:
      value = False
    value = str(int(value))
    return Widget.render_odg_view(self, field, value, as_string, ooo_builder,
                                  REQUEST, render_prefix, attr_dict,
                                  local_name)

CheckBoxWidgetInstance = CheckBoxWidget()

class TextAreaWidget(Widget):
    """Textarea widget
    """
    property_names = Widget.property_names +\
                     ['width', 'height', 'extra']

    default = fields.TextAreaField('default',
                                   title='Default',
                                   description=(
        "Default value of the text in the widget."),
                                   default="",
                                   width=20, height=3,
                                   required=0)

    width = fields.IntegerField('width',
                                title='Width',
                                description=(
        "The width (columns) in characters. Required."),
                                default=40,
                                required=1)

    height = fields.IntegerField('height',
                                 title="Height",
                                 description=(
        "The height (rows) in characters. Required."),
                                 default=5,
                                 required=1)

    def render(self, field, key, value, REQUEST, render_prefix=None):
      width = field.get_value('width', REQUEST=REQUEST)
      height = field.get_value('height', REQUEST=REQUEST)

      return render_element("textarea",
                            name=key,
                            css_class=field.get_value('css_class'),
                            cols=width,
                            rows=height,
                            contents=html_quote(value),
                            extra=field.get_value('extra'))

    def render_view(self, field, value, REQUEST, render_prefix=None):
        if value is None:
            return ''
        if not isinstance(value, (tuple, list)):
            if not isinstance(value, basestring):
                value = str(value)
            value = value.split('\n')
        line_separator = '<br/>'
        value_list = [escape(part).replace('\n', line_separator) for part in value]
        value = line_separator.join(value_list)
        return render_element("div",
                              css_class=field.get_value('css_class'),
                              contents=value,
                              extra=field.get_value('extra'))

    def render_odt_view(self, field, value, as_string, ooo_builder, REQUEST,
        render_prefix, attr_dict, local_name):
        if attr_dict is None:
            attr_dict = {}
        if isinstance(value, str):
            #required by lxml
            value = value.decode('utf-8')
        text_node = Element('{%s}%s' % (TEXT_URI, local_name), nsmap=NSMAP)

        RE_OOO_ESCAPE.sub(OOoEscaper(text_node), value)
        text_node.attrib.update(attr_dict)
        if as_string:
            return etree.tostring(text_node)
        return text_node

TextAreaWidgetInstance = TextAreaWidget()

class LinesTextAreaWidget(TextAreaWidget):
  property_names = Widget.property_names +\
                    ['width', 'height', 'view_separator', 'extra']

  default = fields.LinesField('default',
                              title='Default',
                              description=(
      "Default value of the lines in the widget."),
                              default=[],
                              width=20, height=3,
                              required=0)

  view_separator = fields.StringField('view_separator',
                                      title='View separator',
                                      description=(
      "When called with render_view, this separator will be used to "
      "render individual items."),
                                      width=20,
                                      default='<br />\n',
                                      whitespace_preserve=1,
                                      required=1)

  def render(self, field, key, value, REQUEST, render_prefix=None):
    """
    If type definition is missing for LinesField, the input text will be
    splitted into list like ['f', 'o', 'o'] with original Formulator's
    implementation. So explicit conversion to list is required before
    passing to LinesTextAreaWidget's render and render_view methods.
    """
    if isinstance(value, (str, unicode)):
      value = [value]
    value = string.join(map(convertToString, value), "\n")
    return TextAreaWidget.render(self, field, key, value, REQUEST)

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    if value is None:
      return ''
    if isinstance(value, (str, unicode)):
      value = value.split('\n')
    line_separator = field.get_value('view_separator')

    value_list = [escape(convertToString(part)).replace('\n', line_separator) for part in value]
    value = line_separator.join(value_list)
    return render_element("div",
                          css_class=field.get_value('css_class'),
                          contents=value,
                          extra=field.get_value('extra'))


  def render_odt_view(self, field, value, as_string, ooo_builder, REQUEST,
      render_prefix, attr_dict, local_name):
    if value is None:
      value = ['']
    elif isinstance(value, (str, unicode)):
      value = [value]
    value = '\n'.join(map(convertToString, value))
    return TextAreaWidget.render_odt_view(self, field, value, as_string,
                                     ooo_builder, REQUEST, render_prefix,
                                     attr_dict, local_name)

LinesTextAreaWidgetInstance = LinesTextAreaWidget()

class FileWidget(TextWidget):

    def render(self, field, key, value, REQUEST, render_prefix=None):
        """Render text input field.
        """
        display_maxwidth = field.get_value('display_maxwidth') or 0
        if display_maxwidth > 0:
            return render_element("input",
                                  type="file",
                                  name=key,
                                  css_class=field.get_value('css_class'),
                                  size=field.get_value('display_width'),
                                  maxlength=display_maxwidth,
                                  extra=field.get_value('extra'))
        else:
            return render_element("input",
                                  type="file",
                                  name=key,
                                  css_class=field.get_value('css_class'),
                                  size=field.get_value('display_width'),
                                  extra=field.get_value('extra'))

    def render_view(self, field, value, REQUEST=None, render_prefix=None):
        return "[File]"

FileWidgetInstance = FileWidget()

class ItemsWidget(Widget):
    """A widget that has a number of items in it.
    """

    items = fields.ListTextAreaField('items',
                                     title='Items',
                                     description=(
        "Items in the field. Each row should contain an "
        "item. Use the | (pipe) character to separate what is shown "
        "to the user from the submitted value. If no | is supplied, the "
        "shown value for the item will be identical to the submitted value. "
        "Internally the items property returns a list. If a list item "
        "is a single value, that will be used for both the display and "
        "the submitted value. A list item can also be a tuple consisting "
        "of two elements. The first element of the tuple should be a string "
        "that is name of the item that should be displayed. The second "
        "element of the tuple should be the value that will be submitted. "
        "If you want to override this property you will therefore have "
        "to return such a list."),

                                     default=[],
                                     width=20,
                                     height=5,
                                     required=0)

    # NOTE: for ordering reasons (we want extra at the end),
    # this isn't in the base class property_names list, but
    # instead will be referred to by the subclasses.
    extra_item = fields.StringField('extra_item',
                               title='Extra per item',
                               description=(
        "A string containing extra HTML code for attributes. This "
        "string will be literally included each of the rendered items of the "
        "field. This property can be useful if you want "
        "to add a disabled attribute to disable all contained items, for "
        "instance."),
                               default="",
                               required=0)

    @staticmethod
    def render_element(tag, **kw):
        """
        Similar to global render_element, but render None values as disabled
        elements.
        """
        if kw['value'] is None:
            kw.pop('value')
            kw['disabled'] = None
        return render_element(tag, **kw)

class SingleItemsWidget(ItemsWidget):
  """A widget with a number of items that has only a single
  selectable item.
  """
  default = fields.StringField('default',
                                title='Default',
                                description=(
      "The default value of the widget; this should be one of the "
      "elements in the list of items."),
                                default="",
                                required=0)

  first_item = fields.CheckBoxField('first_item',
                                    title="Select First Item",
                                    description=(
      "If checked, the first item will always be selected if "
      "no initial default value is supplied."),
                                    default=0)

  def render_items(self, field, key, value, REQUEST, render_prefix=None):
    # get items
    cell = getattr(REQUEST, 'cell', None)
    items = field.get_value('items', REQUEST=REQUEST, cell=cell)
    if not items:
      return []

    # check if we want to select first item
    if not value and field.get_value('first_item', REQUEST=REQUEST,
                                    cell=cell) and len(items) > 0:
      try:
        text, value = items[0]
      except ValueError:
        value = items[0]

    css_class = field.get_value('css_class')
    extra_item = field.get_value('extra_item')

    # if we run into multiple items with same value, we select the
    # first one only (for now, may be able to fix this better later)
    selected_found = 0
    rendered_items = []
    for item in items:
      try:
        item_text, item_value = item
      except ValueError:
        item_text = item
        item_value = item

      if item_value == value and not selected_found:
        rendered_item = self.render_selected_item(escape(ustr(item_text)),
                                                  item_value,
                                                  key,
                                                  css_class,
                                                  extra_item)
        selected_found = 1
      else:
        rendered_item = self.render_item(escape(ustr(item_text)),
                                          item_value,
                                          key,
                                          css_class,
                                          extra_item)

      rendered_items.append(rendered_item)

    # XXX We want to make sure that we always have the current value in items. -yo
    if not selected_found and value:
      value = escape(ustr(value))
      rendered_item = self.render_selected_item('??? (%s)' % value,
                                                value,
                                                key,
                                                css_class,
                                                extra_item)
      rendered_items.append(rendered_item)

    return rendered_items

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    """
    This method is not as efficient as using a StringField in read only.
    Always consider to change the field in your Form.
    """
    if value is None:
        return ''
    title_list = [x[0] for x in field.get_value("items", REQUEST=REQUEST) if x[1]==value]
    if len(title_list) == 0:
      return "??? (%s)" % escape(value)
    else:
      return title_list[0]
    return value

  render_pdf = render_view

  def render_odt_view(self, field, value, as_string, ooo_builder, REQUEST,
      render_prefix, attr_dict, local_name):

    items = field.get_value('items',
                            REQUEST=REQUEST,
                            cell=getattr(REQUEST, 'cell', None))
    # XXX this code can be factorized
    d = {}
    for item in items:
      try:
        item_text, item_value = item
      except ValueError:
        item_text = item
        item_value = item
      d[item_value] = item_text

    if value is None:
      value = ''

    value = d.get(value, '??? (%s)' % value)

    if attr_dict is None:
      attr_dict = {}
    if isinstance(value, str):
      #required by lxml
      value = value.decode('utf-8')
    text_node = Element('{%s}%s' % (TEXT_URI, local_name), nsmap=NSMAP)

    RE_OOO_ESCAPE.sub(OOoEscaper(text_node), value)
    text_node.attrib.update(attr_dict)
    if as_string:
      return etree.tostring(text_node)
    return text_node


class MultiItemsWidget(ItemsWidget):
  """A widget with a number of items that has multiple selectable
  items.
  """
  default = fields.LinesField('default',
                              title='Default',
                              description=(
      "The initial selections of the widget. This is a list of "
      "zero or more values. If you override this property from Python "
      "your code should return a Python list."),
                              width=20, height=3,
                              default=[],
                              required=0)

  view_separator = fields.StringField('view_separator',
                                      title='View separator',
                                      description=(
      "When called with render_view, this separator will be used to "
      "render individual items."),
                                      width=20,
                                      default='<br />\n',
                                      whitespace_preserve=1,
                                      required=1)

  def render_items(self, field, key, value, REQUEST, render_prefix=None):
    # list is needed, not a tuple
    if isinstance(value, tuple):
      value = list(value)
    # need to deal with single item selects
    if not isinstance(value, list):
      value = [value]

    # XXX -yo
    selected_found = {}

    items = field.get_value('items', REQUEST=REQUEST, cell=getattr(REQUEST, 'cell', None)) # Added request
    from Products.ERP5Form.MultiLinkField import MultiLinkFieldWidget
    if not items:
      return []

    css_class = field.get_value('css_class')
    extra_item = field.get_value('extra_item')
    rendered_items = []

    for item in items:
      try:
        item_text, item_value = item
      except ValueError:
        item_text = item
        item_value = item

      if item_value in value:
        rendered_item = self.render_selected_item(
            escape(ustr(item_text)),
            escape(ustr(item_value)),
            key,
            css_class,
            extra_item)
        # XXX -yo
        index = value.index(item_value)
        selected_found[index] = 1
      else:
        rendered_item = self.render_item(
            escape(ustr(item_text)),
            escape(ustr(item_value)),
            key,
            css_class,
            extra_item)
      rendered_items.append(rendered_item)

    # XXX We want to make sure that we always have the current value in items. -yo
    for index in range(len(value)):
      v = value[index]
      if index not in selected_found and v:
        v = escape(v)
        rendered_item = self.render_selected_item('??? (%s)' % v,
                                                  v,
                                                  key,
                                                  css_class,
                                                  extra_item)
        rendered_items.append(rendered_item)

    # Moved marked field to Render
    # rendered_items.append(render_element('input', type='hidden', name="default_%s:int" % (key, ), value="0"))
    return rendered_items

  def render_items_view(self, field, value, REQUEST):
      if type(value) is not type([]):
          value = [value]

      items = field.get_value('items',
                              REQUEST=REQUEST,
                              cell=getattr(REQUEST, 'cell', None))
      d = {}
      for item in items:
          try:
              item_text, item_value = item
          except ValueError:
              item_text = item
              item_value = item
          d[item_value] = item_text
      result = []
      for e in value:
          result.append(d[e])
      return result

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
      if value is None:
          return ''
      return string.join(self.render_items_view(field, value, REQUEST),
                          field.get_value('view_separator'))

  def render_items_odf(self, field, value, REQUEST):
    if type(value) is not type([]):
      value = [value]

    items = field.get_value('items',
                            REQUEST=REQUEST,
                            cell=getattr(REQUEST, 'cell', None))
    d = {}
    for item in items:
      try:
        item_text, item_value = item
      except ValueError:
        item_text = item
        item_value = item
      d[item_value] = item_text
    result = []
    for e in value:
      result.append(d[e].replace('\xc2\xa0', ''))
    return result

  def render_odg(self, field, value, as_string, ooo_builder, REQUEST,
                 render_prefix, attr_dict, local_name):
    if value is None:
      return None
    value_list = self.render_items_odf(field, value, REQUEST)
    value = ', '.join(value_list).decode('utf-8')
    return Widget.render_odg(self, field, value, as_string, ooo_builder,
                             REQUEST, render_prefix, attr_dict, local_name)

  def render_odt_view(self, field, value, as_string, ooo_builder, REQUEST,
      render_prefix, attr_dict, local_name):

    items = field.get_value('items',
                            REQUEST=REQUEST,
                            cell=getattr(REQUEST, 'cell', None))
    d = {}
    for item in items:
      try:
        item_text, item_value = item
      except ValueError:
        item_text = item
        item_value = item
      d[item_value] = item_text

    if value is None:
      value = ['']
    elif isinstance(value, basestring):
      value = [value]

    result = []
    for e in value:
      result.append(d.get(e, '??? (%s)' % e))

    value = '\n'.join(result)

    if attr_dict is None:
      attr_dict = {}
    if isinstance(value, str):
      #required by lxml
      value = value.decode('utf-8')
    text_node = Element('{%s}%s' % (TEXT_URI, local_name), nsmap=NSMAP)

    RE_OOO_ESCAPE.sub(OOoEscaper(text_node), value)
    text_node.attrib.update(attr_dict)
    if as_string:
      return etree.tostring(text_node)
    return text_node


class ListWidget(SingleItemsWidget):
    """List widget.
    """
    property_names = Widget.property_names +\
                     ['first_item', 'items', 'size', 'extra', 'extra_item']

    size = fields.IntegerField('size',
                               title='Size',
                               description=(
        "The display size in rows of the field. If set to 1, the "
        "widget will be displayed as a drop down box by many browsers, "
        "if set to something higher, a list will be shown. Required."),
                               default=5,
                               required=1)

    def render(self, field, key, value, REQUEST, render_prefix=None):
      rendered_items = self.render_items(field, key, value, REQUEST)
      input_hidden = render_element('input', type='hidden',
                                    name="default_%s:int" % (key, ), value="0")
      list_widget = render_element(
                    'select',
                    name=key,
                    css_class=field.get_value('css_class', REQUEST=REQUEST),
                    size=field.get_value('size', REQUEST=REQUEST),
                    contents=string.join(rendered_items, "\n"),
                    extra=field.get_value('extra', REQUEST=REQUEST))

      return "\n".join([list_widget, input_hidden])

    def render_item(self, text, value, key, css_class, extra_item):
        if text:
          return self.render_element('option', contents=text, value=value,
                                     extra=extra_item)
        else:
          return self.render_element('option', label=' ', value=value,
                                     extra=extra_item)

    def render_selected_item(self, text, value, key, css_class, extra_item):
        if text:
          return self.render_element('option', contents=text, value=value,
                                     selected=None, extra=extra_item)
        else:
          return self.render_element('option', label=' ', value=value,
                                     selected=None, extra=extra_item)

ListWidgetInstance = ListWidget()

class MultiListWidget(MultiItemsWidget):
    """List widget with multiple select.
    """
    property_names = Widget.property_names +\
                     ['items', 'size', 'view_separator', 'extra', 'extra_item']

    size = fields.IntegerField('size',
                               title='Size',
                               description=(
        "The display size in rows of the field. If set to 1, the "
        "widget will be displayed as a drop down box by many browsers, "
        "if set to something higher, a list will be shown. Required."),
                               default=5,
                               required=1)

    def render(self, field, key, value, REQUEST, render_prefix=None):
      rendered_items = self.render_items(field, key, value, REQUEST)
      input_hidden = render_element('input', type='hidden', name="default_%s:int" % (key, ), value="0")
      multi_list = render_element(
                    'select',
                    name=key,
                    multiple=None,
                    css_class=field.get_value('css_class', REQUEST=REQUEST),
                    size=field.get_value('size', REQUEST=REQUEST),
                    contents=string.join(rendered_items, "\n"),
                    extra=field.get_value('extra', REQUEST=REQUEST))

      return "\n".join([multi_list,input_hidden])

    def render_item(self, text, value, key, css_class, extra_item):
        if text:
          return self.render_element('option', contents=text, value=value,
                                     extra=extra_item)
        else:
          return self.render_element('option', label=' ', value=value,
                                     extra=extra_item)

    def render_selected_item(self, text, value, key, css_class, extra_item):
        if text:
          return self.render_element('option', contents=text, value=value,
                                     selected=None, extra=extra_item)
        else:
          return self.render_element('option', label=' ', value=value,
                                     selected=None, extra=extra_item)

MultiListWidgetInstance = MultiListWidget()

class RadioWidget(SingleItemsWidget):
  """radio buttons widget.
  """
  property_names = Widget.property_names +\
                    ['first_item', 'items', 'orientation', 'extra_item']

  orientation = fields.ListField('orientation',
                                  title='Orientation',
                                  description=(
      "Orientation of the radio buttons. The radio buttons will "
      "be drawn either vertically or horizontally."),
                                  default="vertical",
                                  required=1,
                                  size=1,
                                  items=[('Vertical', 'vertical'),
                                        ('Horizontal', 'horizontal')])

  def render(self, field, key, value, REQUEST, render_prefix=None):
    input_hidden = render_element('input', type='hidden',
                                  name="default_%s" % (key, ), value="")
    rendered_items = self.render_items(field, key, value, REQUEST)
    rendered_items.append(input_hidden)
    orientation = field.get_value('orientation')
    if orientation == 'horizontal':
      return string.join(rendered_items, "&nbsp;&nbsp;")
    else:
      return string.join(rendered_items, "<br />")

  def render_item(self, text, value, key, css_class, extra_item):
    return self.render_element('input',
                          type="radio",
                          css_class=css_class,
                          name=key,
                          value=value,
                          extra=extra_item) + text

  def render_selected_item(self, text, value, key, css_class, extra_item):
    return self.render_element('input',
                          type="radio",
                          css_class=css_class,
                          name=key,
                          value=value,
                          checked=None,
                          extra=extra_item) + text

RadioWidgetInstance = RadioWidget()

class MultiCheckBoxWidget(MultiItemsWidget):
    """multiple checkbox widget.
    """
    property_names = Widget.property_names +\
                     ['items', 'orientation', 'view_separator', 'extra_item']

    orientation = fields.ListField('orientation',
                                   title='Orientation',
                                   description=(
        "Orientation of the check boxes. The check boxes will "
        "be drawn either vertically or horizontally."),
                                   default="vertical",
                                   required=1,
                                   size=1,
                                   items=[('Vertical', 'vertical'),
                                          ('Horizontal', 'horizontal')])

    def render(self, field, key, value, REQUEST, render_prefix=None):
      rendered_items = self.render_items(field, key, value, REQUEST)
      rendered_items.append(render_element('input', type='hidden', name="default_%s:int" % (key, ), value="0"))
      orientation = field.get_value('orientation')
      if orientation == 'horizontal':
        return string.join(rendered_items, "&nbsp;&nbsp;")
      else:
        return string.join(rendered_items, "<br />")

    def render_item(self, text, value, key, css_class, extra_item):
        return self.render_element('input',
                              type="checkbox",
                              css_class=css_class,
                              name=key,
                              value=value,
                              extra=extra_item) + text

    def render_selected_item(self, text, value, key, css_class, extra_item):
        return self.render_element('input',
                              type="checkbox",
                              css_class=css_class,
                              name=key,
                              value=value,
                              checked=None,
                              extra=extra_item) + text

MultiCheckBoxWidgetInstance = MultiCheckBoxWidget()

gmt_timezones = [(x, x) for x in sorted(set(Timezones()))]

class DateTimeWidget(Widget):
  """
    Added support for key in every call to render_sub_field
  """

  sql_format_year  = '%Y'
  sql_format_month = '%m'
  sql_format_day   = '%d'
  format_to_sql_format_dict = {'dmy': (sql_format_day  , sql_format_month, sql_format_year),
                                'ymd': (sql_format_year , sql_format_month, sql_format_day ),
                                'mdy': (sql_format_month, sql_format_day  , sql_format_year),
                                'my' : (sql_format_month, sql_format_year ),
                                'ym' : (sql_format_year , sql_format_month)
                              }
  sql_format_default = format_to_sql_format_dict['ymd']

  hide_day = fields.CheckBoxField('hide_day',
                                title="Hide Day",
                                description=(
      "The day will be hidden on the output. Instead the default"
      "Day will be taken"),
                                default=0)

  hidden_day_is_last_day = fields.CheckBoxField('hidden_day_is_last_day',
                                title="Hidden Day is last day of the Month",
                                description=(
      "Defines wether hidden day means, you want the last day of the month"
      "Else it will be the first day"),
                                default=0)

  timezone_style = fields.CheckBoxField('timezone_style',
                                    title="Display timezone",
                                    description=("Display timezone"),
                                    default=0)

  default = fields.DateTimeField('default',
                                   title="Default",
                                   description=("The default datetime."),
                                   default=None,
                                   display_style="text",
                                   display_order="ymd",
                                   input_style="text",
                                   required=0)

  default_now = fields.CheckBoxField('default_now',
                                      title="Default to now",
                                      description=(
      "Default date and time will be the date and time at showing of "
      "the form (if the default is left empty)."),
                                      default=0)

  date_separator = fields.StringField('date_separator',
                                      title='Date separator',
                                      description=(
      "Separator to appear between year, month, day."),
                                      default="/",
                                      required=0,
                                      display_width=2,
                                      display_maxwith=2,
                                      max_length=2)

  time_separator = fields.StringField('time_separator',
                                      title='Time separator',
                                      description=(
      "Separator to appear between hour and minutes."),
                                      default=":",
                                      required=0,
                                      display_width=2,
                                      display_maxwith=2,
                                      max_length=2)

  input_style = fields.ListField('input_style',
                                  title="Input style",
                                  description=(
      "The type of input used. 'text' will show the date part "
      "as text, while 'list' will use dropdown lists instead."),
                                  default="text",
                                  items=[("text", "text"),
                                        ("list", "list"),
                                        ("number", "number")],
                                  size=1)

  default_timezone = fields.ListField('default_timezone',
                                  title="Default Timezone",
                                  description=(
      "The default timezone display when inputing a new date"),
                                  default="GMT",
                                  items=gmt_timezones,
                                  required=1,
                                  size=1)

  input_order = fields.ListField('input_order',
                                  title="Input order",
                                  description=(
      "The order in which date input should take place. Either "
      "year/month/day, day/month/year or month/day/year."),
                                  default="ymd",
                                  items=[("year/month/day", "ymd"),
                                        ("day/month/year", "dmy"),
                                        ("month/day/year", "mdy")],
                                  required=1,
                                  size=1)

  date_only = fields.CheckBoxField('date_only',
                                    title="Display date only",
                                    description=(
      "Display the date only, not the time."),
                                    default=0)

  ampm_time_style = fields.CheckBoxField('ampm_time_style',
                                           title="AM/PM time style",
                                           description=(
        "Display time in am/pm format."),
                                           default=0)

  property_names = Widget.property_names +\
                    ['default_now', 'date_separator', 'time_separator',
                     'input_style', 'input_order', 'date_only',
                     'ampm_time_style', 'timezone_style', 'default_timezone',
                     'hide_day', 'hidden_day_is_last_day']

  def getInputOrder(self, field):
    input_order = field.get_value('input_order')
    if field.get_value('hide_day'):
      if input_order == 'ymd':
        input_order = 'ym'
      elif input_order in ('dmy', 'mdy'):
        input_order = 'my'
    return input_order

  def render_dict(self, field, value, render_prefix=None):
    """
      This is yet another field rendering. It is designed to allow code to
      understand field's value data by providing its type and format when
      applicable.

      It returns a dict with 3 keys:
        type  : Text representation of value's type.
        format: Type-dependant-formated formating information.
                This only describes the field format settings, not the actual
                format of provided value.
        query : Passthrough of given value.
    """
    if not value:
      return None
    format_dict = self.format_to_sql_format_dict
    input_order = format_dict.get(self.getInputOrder(field),
                                  self.sql_format_default)
    if isinstance(value, unicode):
      value = value.encode(field.get_form_encoding())
    return {'query': value,
            'format': field.get_value('date_separator').join(input_order),
            'type': 'date'}

  def render(self, field, key, value, REQUEST, render_prefix=None):
    use_ampm = field.get_value('ampm_time_style')
    use_timezone = field.get_value('timezone_style')

    # Is it still usefull to test the None value,
    # as DateTimeField should be considerer as the other field
    # and get an empty string as default value?
    # XXX hasattr(REQUEST, 'form') seems useless,
    # because REQUEST always has a form property
    if (value in (None, '')) and (field.get_value('default_now')) and \
        ((REQUEST is None) or (not hasattr(REQUEST, 'form')) or \
        (not REQUEST.form.has_key('subfield_%s_%s' % (key, 'year')))):
      value = DateTime()
    year   = None
    month  = None
    day    = None
    hour   = None
    minute = None
    ampm   = None
    timezone = field.get_value("default_timezone")
    if isinstance(value, DateTime):
      year = "%04d" % value.year()
      month = "%02d" % value.month()
      day = "%02d" % value.day()
      if use_ampm:
          hour = "%02d" % value.h_12()
      else:
          hour = "%02d" % value.hour()
      minute = "%02d" % value.minute()
      ampm = value.ampm()
      timezone = value.timezone()
    input_order = self.getInputOrder(field)
    if input_order == 'ymd':
      order = [('year', year),
                ('month', month),
                ('day', day)]
    elif input_order == 'dmy':
      order = [('day', day),
                ('month', month),
                ('year', year)]
    elif input_order == 'mdy':
      order = [('month', month),
                ('day', day),
                ('year', year)]
    elif input_order == 'my':
      order = [('month', month),
                ('year', year)]
    elif input_order == 'ym':
      order = [('year', year),
                ('month', month)]
    else:
      order = [('year', year),
                ('month', month),
                ('day', day)]
    result = []
    for sub_field_name, sub_field_value in order:
      result.append(field.render_sub_field(sub_field_name,
                                            sub_field_value, REQUEST, key=key))
    date_result = string.join(result, field.get_value('date_separator'))
    if not field.get_value('date_only'):
      time_result = (field.render_sub_field('hour', hour, REQUEST, key=key) +
                      field.get_value('time_separator') +
                      field.render_sub_field('minute', minute, REQUEST, key=key))

      if use_ampm:
        time_result += '&nbsp;' + field.render_sub_field('ampm',
                                                      ampm, REQUEST, key=key)
      if use_timezone:
        time_result += '&nbsp;' + field.render_sub_field('timezone',
                                                      timezone, REQUEST, key=key)
      return date_result + '&nbsp;&nbsp;&nbsp;' + time_result
    else:
      return date_result

  def format_value(self, field, value, mode='html'):
    # Is it still usefull to test the None value,
    # as DateTimeField should be considerer as the other field
    # and get an empty string as default value?
    if not isinstance(value, DateTime):
      if value is None:
        value = ''
      return value

    use_ampm = field.get_value('ampm_time_style')
    use_timezone = field.get_value('timezone_style')

    year = "%04d" % value.year()
    month = "%02d" % value.month()
    day = "%02d" % value.day()
    if use_ampm:
      hour = "%02d" % value.h_12()
    else:
      hour = "%02d" % value.hour()
    minute = "%02d" % value.minute()
    ampm = value.ampm()
    timezone = value.timezone()

    order = self.getInputOrder(field)
    if order == 'ymd':
      output = [year, month, day]
    elif order == 'dmy':
      output = [day, month, year]
    elif order == 'mdy':
      output = [month, day, year]
    elif order == 'my':
      output = [month, year]
    elif order == 'ym':
      output = [year, month]
    else:
      output = [year, month, day]
    date_result = string.join(output, field.get_value('date_separator'))

    if mode in ('html', ):
      space = '&nbsp;'
    else:
      space = ' '

    if not field.get_value('date_only'):
      time_result = hour + field.get_value('time_separator') + minute
      if use_ampm:
          time_result += space + ampm
      if use_timezone:
          time_result += space + timezone
      return date_result + (space * 3) + time_result
    else:
      return date_result

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    return self.format_value(field, value, mode='html')

  def render_pdf(self, field, value, render_prefix=None):
    return self.format_value(field, value, mode='pdf')

  def render_odt_view(self, field, value, as_string, ooo_builder, REQUEST,
      render_prefix, attr_dict, local_name):
    """
      Return a field value rendered in odt format.
      - as_string return value as string or as xml object
      - attr_dict can be used for additional attributes (like style).
    """
    if attr_dict is None:
      attr_dict = {}
    text_node = Element('{%s}%s' % (TEXT_URI, local_name), nsmap=NSMAP)
    # get the field value
    if not value and field.get_value('default_now'):
      value = DateTime()
    text_node.text = self.format_value(field, value, mode='pdf').decode('utf-8')
    text_node.attrib.update(attr_dict)
    if as_string:
      return etree.tostring(text_node)
    return text_node

  def render_odt_variable(self, field, value, as_string, ooo_builder, REQUEST,
                      render_prefix, attr_dict, local_name):
    """
      Return a field value rendered in odt format as read-only mode.
      - as_string return value as string or as xml object
      - attr_dict can be used for additional attributes (like style).
      - ooo_builder wrapper of ODF zipped archive usefull to insert images
      - local_name local-name of the node returned by this render
    """
    if attr_dict is None:
      attr_dict = {}
    attr_dict['{%s}value-type' % OFFICE_URI] = 'date'
    if not value and field.get_value('default_now'):
      value = DateTime()
    text_node = Element('{%s}%s' % (TEXT_URI, local_name), nsmap=NSMAP)
    if value:
      # http://www.w3.org/TR/2004/REC-xmlschema-2-20041028/#dateTime
      attr_dict['{%s}date-value' % OFFICE_URI] = value.ISO8601()
      # According http://wiki.services.openoffice.org/wiki/Documentation/How_Tos/Calc:_Date_%26_Time_functions
      # default offset is 30/12/1899
      number_of_second_in_day = 86400 #24 * 60 * 60
      timestamp = float(value)
      ooo_offset_timestamp = float(DateTime(1899, 12, 30, 0, 0, 0, value.timezone()))
      days_value = (timestamp - ooo_offset_timestamp) / number_of_second_in_day
      attr_dict['{%s}formula' % TEXT_URI] = 'ooow:%f' % days_value
      text_node.attrib.update(attr_dict)
    if as_string:
      return etree.tostring(text_node)
    return text_node

  def render_odg_view(self, field, value, as_string, ooo_builder, REQUEST,
                      render_prefix, attr_dict, local_name):
    """Transform DateTime into string then call default renderer
    """
    if not value and field.get_value('default_now'):
      value = DateTime()
    value_as_text = self.format_value(field, value, mode='pdf').decode('utf-8')
    return Widget.render_odg_view(self, field, value_as_text, as_string,
                                      ooo_builder, REQUEST, render_prefix,
                                      attr_dict, local_name)

DateTimeWidgetInstance = DateTimeWidget()

class LabelWidget(Widget):
    """Widget that is a label only. It simply returns its default value.
    """
    property_names = ['title', 'description',
                      'default', 'css_class', 'hidden', 'extra']

    default = fields.TextAreaField(
        'default',
        title="Label text",
        description="Label text to render",
        default="",
        width=20, height=3,
        required=0)

    def render(self, field, key, value, REQUEST=None, render_prefix=None):
        return render_element("div",
                              css_class=field.get_value('css_class'),
                              contents=field.get_value('default'))

    # XXX should render view return the same information as render?
    def render_view(self, field, value, REQUEST=None, render_prefix=None):
        return field.get_value('default')

LabelWidgetInstance = LabelWidget()

def render_tag(tag, **kw):
  """Render the tag. Well, not all of it, as we may want to / it.
  """
  attr_list = []

  # special case handling for css_class
  if kw.has_key('css_class'):
    if kw['css_class'] != "":
      attr_list.append('class="%s"' % kw['css_class'])
    del kw['css_class']

  # special case handling for extra 'raw' code
  if kw.has_key('extra'):
    extra = kw['extra'] # could be empty string but we don't care
    del kw['extra']
  else:
    extra = ""

  # handle other attributes
  for key, value in kw.items():
    if value == None:
        value = key
    attr_list.append('%s="%s"' % (key, html_quote(value)))

  attr_str = string.join(attr_list, " ")
  return "<%s %s %s" % (tag, attr_str, extra)

VOID_ELEMENT_LIST = ('area', 'base', 'br', 'col', 'embed', 'hr', 'img',
                     'input', 'link', 'meta', 'param', 'source', 'track',
                     'wbr')
def render_element(tag, **kw):
  # https://www.w3.org/TR/html5/syntax.html#start-tags
  # End tags are forbidden on void HTML elements
  if tag in VOID_ELEMENT_LIST:
    if kw.has_key('contents'):
      raise ValueError('Void element %s does not accept content' % tag)
    return apply(render_tag, (tag, ), kw) + " />"
  else:
    if kw.has_key('contents'):
      contents = kw['contents']
      del kw['contents']
      if tag == 'textarea':
        # Newlines at the start of textarea elements are ignored as an authoring convenience
        # https://www.w3.org/TR/html52/syntax.html#the-in-body-insertion-mode
        contents = '\n%s' % contents
    else:
      contents = ''
    return "%s>%s</%s>" % (apply(render_tag, (tag, ), kw), contents, tag)


##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean Paul Smets <jp@nexedi.com>
#                    Jerome Perrin <jerome@nexedi.com>
#                    Yoshinori Okuji <yo@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################


class IntegerWidget(TextWidget) :
  def render(self, field, key, value, REQUEST, render_prefix=None) :
    """Render an editable integer.
    """
    if isinstance(value, float):
      value = int(value)
    display_maxwidth = field.get_value('display_maxwidth') or 0
    input_type = field.get_value('input_type') or 'text'
    if display_maxwidth > 0:
      return render_element("input",
                            type=input_type,
                            name=key,
                            css_class=field.get_value('css_class'),
                            value=value,
                            size=field.get_value('display_width'),
                            maxlength=display_maxwidth,
                            extra=field.get_value('extra'))
    else:
      return render_element("input",
                            type=input_type,
                            name=key,
                            css_class=field.get_value('css_class'),
                            value=value,
                            size=field.get_value('display_width'),
                            extra=field.get_value('extra'))

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    """Render a non-editable interger."""
    if isinstance(value, float):
      value = int(value)
    return TextWidget.render_view(self, field, value, REQUEST=REQUEST)

  def render_odt_view(self, field, value, as_string, ooo_builder, REQUEST,
                      render_prefix, attr_dict, local_name):
    """This renderer is dedicated to render values inside OOo document
    It renderer convert explicitely numeric values into strings
    """
    if isinstance(value, (int, float)):
      # convert into string
      value = '%s' % value
    return TextWidget.render_odt_view(self, field, value, as_string,
                                      ooo_builder, REQUEST, render_prefix,
                                      attr_dict, local_name)

  def render_odt_variable(self, field, value, as_string, ooo_builder, REQUEST,
                      render_prefix, attr_dict, local_name):
    """
      Return a field value rendered in odt format as read-only mode.
      - as_string return value as string or as xml object
      - attr_dict can be used for additional attributes (like style).
      - ooo_builder wrapper of ODF zipped archive usefull to insert images
      - local_name local-name of the node returned by this render
    """
    if attr_dict is None:
      attr_dict = {}
    attr_dict['{%s}value-type' % OFFICE_URI] = 'float'
    if isinstance(value, str):
      #required by lxml
      value = value.decode('utf-8')
    text_node = Element('{%s}%s' % (TEXT_URI, local_name), nsmap=NSMAP)
    text_node.text = str(value)
    attr_dict['{%s}value' % OFFICE_URI] = str(value)
    formula_attribute_name = '{%s}formula' % TEXT_URI
    if formula_attribute_name in attr_dict:
      del attr_dict[formula_attribute_name]
    text_node.attrib.update(attr_dict)
    if as_string:
      return etree.tostring(text_node)
    return text_node

  def render_odg_view(self, field, value, as_string, ooo_builder, REQUEST,
                      render_prefix, attr_dict, local_name):
    """convert interger into string then use TextWidget renderer
    """
    if isinstance(value, int):
      # convert into string
      value = str(value)
    return TextWidget.render_odg_view(self, field, value, as_string,
                                      ooo_builder, REQUEST, render_prefix,
                                      attr_dict, local_name)

IntegerWidgetInstance = IntegerWidget()
class FloatWidget(TextWidget):

  property_names = TextWidget.property_names +\
                    ['input_style','precision']

  input_style = fields.ListField('input_style',
                                  title="Input style",
                                  description=(
      "The type of float we should enter. "),
                                  default="-1234.5",
                                  items=[("-1234.5",  "-1234.5"),
                                         ("-1 234.5", "-1 234.5"),
                                         ("-1 234,5", "-1 234,5"),
                                         ("-1.234,5", "-1.234,5"),
                                         ("-1,234.5", "-1,234.5"),
                                         ("-12.3%", "-12.3%"),],
                                  required=1,
                                  size=1)

  precision = fields.IntegerField('precision',
                                      title='Precision',
                                      description=(
      "Number of digits after the decimal point"),
                                      default='',
                                      required=0)

  def format_value(self, field, value):
    """Formats the value as requested"""
    if value not in (None,''):
      precision = field.get_value('precision')
      input_style = field.get_value('input_style')
      percent = '%' in input_style
      try:
        float_value = float(value)
        if percent:
          float_value *= 100
        if precision not in (None, '') and (
           # ignore precision for too big absolute numbers
           abs(float_value) * 10**precision < 2**53):
          # if we have a precision, then use it now
          value = ('%%0.%sf' % precision) % float_value
        else:
          value = str(float_value)
        # if this number is displayed in scientific notification,
        # just return it as is
        if 'e' in value:
          return value
        if precision != 0:
          value, fpart = value.split('.')
      except ValueError:
        return value

      decimal_separator = ''
      decimal_point = '.'
      if input_style == "-1234.5":
        pass
      elif input_style == '-1 234.5':
        decimal_separator = ' '
      elif input_style == '-1 234,5':
        decimal_separator = ' '
        decimal_point = ','
      elif input_style == '-1.234,5':
        decimal_separator = '.'
        decimal_point = ','
      elif input_style == '-1,234.5':
        decimal_separator = ','

      if decimal_separator in input_style:
        if value.startswith('-'):
          sign = '-'
          value = value[1:]
        else:
          sign = ''
        i = len(value) % 3 or 3
        integer = value[:i]
        while i < len(value):
          integer += decimal_separator + value[i:i+3]
          i += 3
        value = sign + integer
      if precision != 0:
        value += decimal_point
        if precision:
          value += fpart[:precision].ljust(precision, '0')
        else:
          value += fpart
      if percent:
        value += '%'
      return value
    return ''

  def render(self, field, key, value, REQUEST, render_prefix=None):
    """Render Float input field
    """
    value = self.format_value(field, value)
    display_maxwidth = field.get_value('display_maxwidth') or 0
    extra_keys = {}
    if display_maxwidth > 0:
      extra_keys['maxlength'] = display_maxwidth
    return render_element( "input",
                            type="text",
                            name=key,
                            css_class=field.get_value('css_class'),
                            value=value,
                            size=field.get_value('display_width'),
                            extra=field.get_value('extra'),
                            **extra_keys)

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    """
      Render Float display field.
      This patch add:
        * replacement of spaces by unbreakable spaces if the content is float-like
        * support of extra CSS class when render as pure text
    """
    value = self.format_value(field, value)

    float_value = None
    try:
      float_value = float(value.replace(' ', ''))
    except:
      pass
    if float_value != None:
      value = value.replace(' ', '&nbsp;')

    extra = field.get_value('extra')
    if extra not in (None, ''):
      value = "<div %s>%s</div>" % (extra, value)

    css_class = field.get_value('css_class')
    if css_class not in ('', None):
      return "<span class='%s'>%s</span>" % (css_class, value)
    return value

  def render_pdf(self, field, value, render_prefix=None):
    """Render the field as PDF."""
    return self.format_value(field, value)

  def render_dict(self, field, value, render_prefix=None):
    """
      This is yet another field rendering. It is designed to allow code to
      understand field's value data by providing its type and format when
      applicable.

      It returns a dict with 3 keys:
        type  : Text representation of value's type.
        format: Type-dependant-formated formating information.
                This only describes the field format settings, not the actual
                format of provided value.
        query : Passthrough of given value.
    """
    if not value:
      return None
    precision = field.get_value('precision')
    format = '0'
    if precision:
      format = '0.'
      # in 'format', the only important thing is the number of decimal places,
      # so we add some places until we reach the precision defined on the
      # field.
      for x in xrange(0, precision):
        format += '0'
    if isinstance(value, unicode):
      value = value.encode(field.get_form_encoding())
    return {'query': value,
            'format': format,
            'type': 'float'}

  def render_odt_view(self, field, value, as_string, ooo_builder, REQUEST,
      render_prefix, attr_dict, local_name):
    if attr_dict is None:
      attr_dict = {}
    text_node = Element('{%s}%s' % (TEXT_URI, local_name), nsmap=NSMAP)
    text_node.text = self.format_value(field, value).decode('utf-8')
    text_node.attrib.update(attr_dict)
    if as_string:
      return etree.tostring(text_node)
    return text_node

  def render_odt_variable(self, field, value, as_string, ooo_builder, REQUEST,
                      render_prefix, attr_dict, local_name):
    """
      Return a field value rendered in odt format as read-only mode.
      - as_string return value as string or as xml object
      - attr_dict can be used for additional attributes (like style).
      - ooo_builder wrapper of ODF zipped archive usefull to insert images
      - local_name local-name of the node returned by this render
    """
    if attr_dict is None:
      attr_dict = {}
    attr_dict['{%s}value-type' % OFFICE_URI] = 'float'
    if isinstance(value, str):
      #required by lxml
      value = value.decode('utf-8')
    text_node = Element('{%s}%s' % (TEXT_URI, local_name), nsmap=NSMAP)
    text_node.text = str(value)
    attr_dict['{%s}value' % OFFICE_URI] = str(value)
    text_node.attrib.update(attr_dict)
    if as_string:
      return etree.tostring(text_node)
    return text_node

  def render_odg(self, field, value, as_string, ooo_builder, REQUEST,
      render_prefix, attr_dict, local_name):
    if attr_dict is None:
      attr_dict = {}
    value = field.render_pdf(value)
    return Widget.render_odg(self, field, value, as_string, ooo_builder,
                             REQUEST, render_prefix, attr_dict, local_name)

FloatWidgetInstance = FloatWidget()

class LinkWidget(TextWidget):
  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    """Render link.
    """
    link_type = field.get_value('link_type', REQUEST=REQUEST)
    if REQUEST is None:
      # stop relying on get_request bein patched in Globals
      REQUEST = field.REQUEST

    if link_type == 'internal':
      value = urljoin(REQUEST['BASE0'], value)
    elif link_type == 'relative':
      value = urljoin(REQUEST['URL1'], value)

    return '<a href="%s">%s</a>' % (value,
        field.get_value('title', cell=getattr(REQUEST,'cell',None)))

LinkWidgetInstance = LinkWidget()

