import string
from DummyField import fields
from DocumentTemplate.DT_Util import html_quote
from DateTime import DateTime
from cgi import escape
import types
from DocumentTemplate.ustr import ustr
from urlparse import urljoin

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
    result = ''
    # We must adapt the rendering to the type of the value
    # in order to get the correct type back
    if isinstance(value, (tuple, list)):
      for v in value:
        result += render_element("input",
                          type="hidden",
                          name="%s:list" % key,
                          value=v,
                          extra=extra)
    else:
      result = render_element("input",
                          type="hidden",
                          name=key,
                          value=value,
                          extra=extra)
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

class TextWidget(Widget):
  """Text widget
  """
  property_names = Widget.property_names +\
                    ['display_width', 'display_maxwidth', 'extra']

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

  def render(self, field, key, value, REQUEST, render_prefix=None):
    """Render text input field.
    """
    display_maxwidth = field.get_value('display_maxwidth') or 0
    if display_maxwidth > 0:
      return render_element("input",
                            type="text",
                            name=key,
                            css_class=field.get_value('css_class'),
                            value=value,
                            size=field.get_value('display_width'),
                            maxlength=display_maxwidth,
                            extra=field.get_value('extra'))
    else:
      return render_element("input",
                            type="text",
                            name=key,
                            css_class=field.get_value('css_class'),
                            value=value,
                            size=field.get_value('display_width'),
                            extra=field.get_value('extra'))

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
    css_class = field.get_value('css_class')
    if css_class not in ('', None):
      # All strings should be escaped before rendering in HTML
      # except for editor field
      return "<span class='%s'>%s</span>" % (css_class, value)
    return value

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
                            checked=1,
                            extra=field.get_value('extra'),
                            disabled='disabled')
    else:
      return render_element("input",
                            type="checkbox",
                            css_class=field.get_value('css_class'),
                            extra=field.get_value('extra'),
                            disabled='disabled')
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
        return value

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
    value = string.join(value, "\n")
    return TextAreaWidget.render(self, field, key, value, REQUEST)

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    if value is None:
      return ''
    elif isinstance(value, (str, unicode)):
      value = [value]
    return string.join(value, field.get_value('view_separator'))

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
                                  value=value,
                                  size=field.get_value('display_width'),
                                  maxlength=display_maxwidth,
                                  extra=field.get_value('extra'))
        else:
            return render_element("input",
                                  type="file",
                                  name=key,
                                  css_class=field.get_value('css_class'),
                                  value=value,
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
      # single item widget should have at least one child in order to produce
      # valid XHTML; disable it so user can not select it
      return [self.render_item('', '', '', '', 'disabled="disabled"')]

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
    if not items and not isinstance(self, MultiLinkFieldWidget):
      # multi items widget should have at least one child in order to produce
      # valid XHTML; disable it so user can not select it.
      # This cannot be applied to MultiLinkFields, which are just some <a>
      # links
      return [self.render_item('', '', '', '', 'disabled="disabled"')]

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

  def render_items_view(self, field, value):
      if type(value) is not type([]):
          value = [value]

      items = field.get_value('items')
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
      return string.join(self.render_items_view(field, value),
                          field.get_value('view_separator'))

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
        return render_element('option', contents=text, value=value, 
                              extra=extra_item)

    def render_selected_item(self, text, value, key, css_class, extra_item):
        return render_element('option', contents=text, value=value,
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
        return render_element('option', contents=text, value=value, 
                              extra=extra_item)

    def render_selected_item(self, text, value, key, css_class, extra_item):
        return render_element('option', contents=text, value=value,
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
    return render_element('input',
                          type="radio",
                          css_class=css_class,
                          name=key,
                          value=value,
                          extra=extra_item) + text

  def render_selected_item(self, text, value, key, css_class, extra_item):
    return render_element('input',
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
        return render_element('input',
                              type="checkbox",
                              css_class=css_class,
                              name=key,
                              value=value,
                              extra=extra_item) + text
    
    def render_selected_item(self, text, value, key, css_class, extra_item):
        return render_element('input',
                              type="checkbox",
                              css_class=css_class,
                              name=key,
                              value=value,
                              checked=None,
                              extra=extra_item) + text

MultiCheckBoxWidgetInstance = MultiCheckBoxWidget()

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
                                        ("list", "list")],
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
                     'ampm_time_style', 'timezone_style', 'hide_day',
                     'hidden_day_is_last_day']

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
    # FIXME: backwards compatibility hack:
    if not hasattr(field, 'sub_form'):
      field.sub_form = create_datetime_text_sub_form()
        
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
    timezone = None
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
    if value in (None, ''):
      return ''

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

def render_element(tag, **kw):
  if kw.has_key('contents'):
    contents = kw['contents']
    del kw['contents']
    return "%s>%s</%s>" % (apply(render_tag, (tag, ), kw), contents, tag)
  else:
    return apply(render_tag, (tag, ), kw) + " />"


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
    if display_maxwidth > 0:
      return render_element("input",
                            type="text",
                            name=key,
                            css_class=field.get_value('css_class'),
                            value=value,
                            size=field.get_value('display_width'),
                            maxlength=display_maxwidth,
                            extra=field.get_value('extra'))
    else:
      return render_element("input",
                            type="text",
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
                                        ("-12.3%", "-12.3%"),],
                                  required=1,
                                  size=1)

  precision = fields.IntegerField('precision',
                                      title='Precision',
                                      description=(
      "Number of digits after the decimal point"),
                                      default=None,
                                      required=0)

  def format_value(self, field, value):
    """Formats the value as requested"""
    if value not in (None,''):
      precision = field.get_value('precision')
      input_style = field.get_value('input_style')
      percent = 0
      original_value = value
      if input_style.find('%')>=0:
        percent=1
        try:
          value = float(value) * 100
        except ValueError:
          return value
      try :
        float_value = float(value)
        if precision not in (None, ''):
          float_value = round(float_value, precision)
        value = str(float_value)
      except ValueError:
        return value
      else:
        if 'e' in value:
          # %f will not use exponential format
          value = '%f' % float(original_value)
      value_list = value.split('.')
      integer = value_list[0]
      if input_style.find(' ')>=0:
        integer = value_list[0]
        i = len(integer)%3
        value = integer[:i]
        while i != len(integer):
          value += ' ' + integer[i:i+3]
          i += 3
      else:
        value = value_list[0]
      if precision != 0:
        value += '.'
      if precision not in (None,''):
        for i in range(0,precision):
          if i < len(value_list[1]):
            value += value_list[1][i]
          else:
            value += '0'
      else:
        value += value_list[1]
      if percent:
        value += '%'
      return value.strip()
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
    input_style = field.get_value('input_style')
    precision = field.get_value('precision')      
    if precision not in (None, '') and precision != 0:
      for x in xrange(1, precision):
        input_style += '5'
    else:
      input_style = input_style.split('.')[0]
    if isinstance(value, unicode):
      value = value.encode(field.get_form_encoding())
    return {'query': value,
            'format': input_style,
            'type': 'float'}

FloatWidgetInstance = FloatWidget()

class LinkWidget(TextWidget):
  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    """Render link.
    """
    link_type = field.get_value('link_type', REQUEST=REQUEST)
    if REQUEST is None:
      REQUEST = get_request()

    if link_type == 'internal':
      value = urljoin(REQUEST['BASE0'], value)
    elif link_type == 'relative':
      value = urljoin(REQUEST['URL1'], value)

    return '<a href="%s">%s</a>' % (value,
        field.get_value('title', cell=getattr(REQUEST,'cell',None)))

LinkWidgetInstance = LinkWidget()

