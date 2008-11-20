##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2003 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
#          Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from Products.Formulator.Field import Field
from Products.Formulator.Widget import Widget
from Products.Formulator.Widget import render_element
from Products.Formulator.FieldRegistry import FieldRegistry
from Products.Formulator import TALESField
from Products.Formulator import MethodField
from Products.Formulator.Widget import ListWidget
from Products.Formulator.Widget import RadioWidget
from Products.Formulator.Widget import MultiItemsWidget
from ProxyField import ProxyField
from MultiLinkField import MultiLinkFieldWidget
from AccessControl import ClassSecurityInfo
from DocumentTemplate.ustr import ustr
from cgi import escape
import types
from zLOG import LOG

def noop(*args, **kw):
  pass

# XXX: this is a quick fix to avoid bloating the ZODB.
# Proper fix should only add FieldHelp when it's missing.
FieldRegistry.registerFieldHelp = noop

def Field_generate_field_key(self, validation=0, key=None):
    """Generate the key Silva uses to render the field in the form.
    """
    # Patched by JPS for ERP5 in order to
    # dynamically change the name
    if key is not None:
      return 'field_%s' % key
    if self.field_record is None:
        return 'field_%s' % self.id
    elif validation:
        return self.id
    elif isinstance(self.widget, MultiItemsWidget):
        return "%s.%s:record:list" % (self.field_record, self.id)
    else:
        return '%s.%s:record' % (self.field_record, self.id)

def Field_render(self, value=None, REQUEST=None, key=None, render_prefix=None):
    """Render the field widget.
    value -- the value the field should have (for instance
              from validation).
    REQUEST -- REQUEST can contain raw (unvalidated) field
              information. If value is None, REQUEST is searched
              for this value.
    if value and REQUEST are both None, the 'default' property of
    the field will be used for the value.
    """
    return self._render_helper(self.generate_field_key(key=key), value, REQUEST, render_prefix)

def Field_render_view(self, value=None, REQUEST=None, render_prefix=None):
    """Render value to be viewed.
    """
    return self.widget.render_view(self, value, REQUEST=REQUEST)

def Field_render_sub_field(self, id, value=None, REQUEST=None, key=None, render_prefix=None):
    """Render a sub field, as part of complete rendering of widget in
    a form. Works like render() but for sub field.
        Added key parameter for ERP5 in order to be compatible with listbox/matrixbox
    """
    return self.sub_form.get_field(id)._render_helper(
        self.generate_subfield_key(id, key=key), value, REQUEST, render_prefix)

def Field_generate_subfield_key(self, id, validation=0, key=None):
    """Generate the key Silva uses to render a sub field.
        Added key parameter for ERP5
        Added key parameter for ERP5 in order to be compatible with listbox/matrixbox
    """
    if key is None: key = self.id
    if self.field_record is None or validation:
        return 'subfield_%s_%s'%(key, id)
    return '%s.subfield_%s_%s:record' % (self.field_record, key, id)

def Field_validate_sub_field(self, id, REQUEST, key=None):
    """Validates a subfield (as part of field validation).
    """
    return self.sub_form.get_field(id)._validate_helper(
        self.generate_subfield_key(id, validation=1, key=key), REQUEST)

def Field_render_helper(self, key, value, REQUEST, render_prefix=None):
    value = self._get_default(key, value, REQUEST)
    __traceback_info__ = ('key=%s value=%r' % (key, value))
    if self.get_value('hidden', REQUEST=REQUEST):
        return self.widget.render_hidden(self, key, value, REQUEST)
    elif (not self.get_value('editable', REQUEST=REQUEST)):
      # XXX: API transition try..except..log..raise. Remove after a while.
      try:
        return self.widget.render_view(self, value, REQUEST=REQUEST, render_prefix=render_prefix)
      except TypeError:
        LOG('FormulatorPatch', 0, 'To update: %r (%r)' % (self.widget.render_view, getattr(self.widget.render_view, 'func_code', None)))
        raise
    else:
      # XXX: API transition try..except..log..raise. Remove after a while.
      try:
        return self.widget.render(self, key, value, REQUEST, render_prefix=render_prefix)
      except TypeError:
        LOG('FormulatorPatch', 0, 'To update: %r (%r)' % (self.widget.render, getattr(self.widget.render, 'func_code', None)))
        raise

def Field_get_user_input_value(self, key, REQUEST):
  """
  Try to get a value of the field from the REQUEST
  """
  return REQUEST.form[key]

def Field_render_odf(self, field=None, key=None, value=None, REQUEST=None,
                     render_format='ooo', render_prefix=None):
  return self.widget.render_odf(self, key, value, REQUEST, render_format,
                                render_prefix)

Field.generate_field_key = Field_generate_field_key
Field.render = Field_render
Field.render_view = Field_render_view
Field.render_sub_field = Field_render_sub_field
Field.generate_subfield_key = Field_generate_subfield_key
Field.validate_sub_field = Field_validate_sub_field
Field._render_helper = Field_render_helper
Field._get_user_input_value = Field_get_user_input_value
Field.render_odf = Field_render_odf

ProxyField._render_helper = Field_render_helper

from Products.Formulator.Validator import SelectionValidator
from Products.Formulator.Validator import StringBaseValidator
# The required field should have a default value to 0
from Products.Formulator.DummyField import fields

StringBaseValidator_required = fields.CheckBoxField('required',
                                title='Required',
                                description=(
    "Checked if the field is required; the user has to fill in some "
    "data."),
                                default=0)
StringBaseValidator.required = StringBaseValidator_required

def SelectionValidator_validate(self, field, key, REQUEST):
    value = StringBaseValidator.validate(self, field, key, REQUEST)

    if value == "" and not field.get_value('required'):
        return value

    # get the text and the value from the list of items
    for item in list(field.get_value('items', cell=getattr(REQUEST,'cell',None))) + [field.get_value('default', cell=getattr(REQUEST,'cell',None))]:
        try:
            item_text, item_value = item
        except (ValueError, TypeError):
            item_text = item
            item_value = item

        # check if the value is equal to the string/unicode version of
        # item_value; if that's the case, we can return the *original*
        # value in the list (not the submitted value). This way, integers
        # will remain integers.
        # XXX it is impossible with the UI currently to fill in unicode
        # items, but it's possible to do it with the TALES tab
        if field.get_value('unicode') and isinstance(item_value, unicode):
            str_value = item_value.encode(field.get_form_encoding())
        else:
            str_value = str(item_value)

        if str_value == value:
            return item_value

    # if we didn't find the value, return error
    self.raise_error('unknown_selection', field)

SelectionValidator.validate = SelectionValidator_validate

from Products.Formulator.Validator import MultiSelectionValidator

def MultiSelectionValidator_validate(self, field, key, REQUEST):
    if REQUEST.get('default_%s' % (key, )) is None:
      LOG('MultiSelectionValidator_validate', 0, 'Field %s is not present in request object (marker field default_%s not found).' % (repr(field.id), key))
      raise KeyError, 'Field %s is not present in request object (marker field default_%s not found).' % (repr(field.id), key)
    values = REQUEST.get(key, [])
    # NOTE: a hack to deal with single item selections
    if not isinstance(values, list):
        # put whatever we got in a list
        values = [values]
    # if we selected nothing and entry is required, give error, otherwise
    # give entry list
    if len(values) == 0:
        if field.get_value('required'):
            self.raise_error('required_not_found', field)
        else:
            return values
    # convert everything to unicode if necessary
    if field.get_value('unicode'):
        values = [unicode(value, field.get_form_encoding())
                  for value in values]

    # create a dictionary of possible values
    value_dict = {}
    for item in field.get_value('items', cell=getattr(REQUEST,'cell',None)): # Patch by JPS for Listbox
        try:
            item_text, item_value = item
        except ValueError:
            item_text = item
            item_value = item
        value_dict[item_value] = 0
    default_value = field.get_value('default', cell=getattr(REQUEST,'cell',None))
    if isinstance(default_value, (list, tuple)):
      for v in default_value:
        value_dict[v] = 0
    else:
      value_dict[default_value] = 0


    # check whether all values are in dictionary
    result = []
    for value in values:
        # FIXME: hack to accept int values as well
        try:
            int_value = int(value)
        except ValueError:
            int_value = None
        if int_value is not None and value_dict.has_key(int_value):
            result.append(int_value)
            continue
        if value_dict.has_key(value):
            result.append(value)
            continue
        self.raise_error('unknown_selection', field)
    # everything checks out
    return result

MultiSelectionValidator.validate = MultiSelectionValidator_validate

from Products.Formulator.Validator import BooleanValidator

def BooleanValidator_validate(self, field, key, REQUEST):
    result = REQUEST.get(key, REQUEST.get('default_%s' % (key, )))
    if result is None:
       raise KeyError, 'Field %s is not present in request object.' % (repr(field.id), )
    if (not not result)==True:
       return 1
    else:
       return 0

BooleanValidator.validate = BooleanValidator_validate

from Products.Formulator.Widget import CheckBoxWidget
def CheckBoxWidget_render(self, field, key, value, REQUEST, render_prefix=None):
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

CheckBoxWidget.render = CheckBoxWidget_render

def CheckBoxWidget_render_view(self, field, value, REQUEST=None, render_prefix=None):
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

CheckBoxWidget.render_view = CheckBoxWidget_render_view

# Patch the render_view of LinkField so that it is clickable in read-only mode.
from Products.Formulator.Widget import TextWidget
from Products.Formulator.StandardFields import LinkField
from Globals import get_request
from urlparse import urljoin

class PatchedLinkWidget(TextWidget):
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

PatchedLinkWidgetInstance = PatchedLinkWidget()
LinkField.widget = PatchedLinkWidgetInstance


# Patch the render_view of TextField to enclose the value within <span> html tags if css class defined
def TextWidget_patched_render_view(self, field, value, REQUEST=None, render_prefix=None):
  """Render text as non-editable.
     This renderer is designed to be type error resistant.
     in we get a non string value. It does escape the result
     and produces clean xhtml.
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

from Products.Formulator.Widget import TextWidget
TextWidget.render_view = TextWidget_patched_render_view

original_TextWidget_render = TextWidget.render
def TextWidget_render(self, field, key, value, REQUEST, render_prefix=None):
  return original_TextWidget_render(self, field, key, value, REQUEST)
TextWidget.render = TextWidget_render

from Products.Formulator.Widget import TextAreaWidget
# Use a standard span rendering
TextAreaWidget.render_view = TextWidget_patched_render_view

original_TextAreaWidget_render = TextAreaWidget.render
def TextAreaWidget_render(self, field, key, value, REQUEST, render_prefix=None):
  return original_TextAreaWidget_render(self, field, key, value, REQUEST)
TextAreaWidget.render = TextAreaWidget_render

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


from Products.Formulator.StandardFields import IntegerField
from Products.Formulator.Validator import IntegerValidator
IntegerFieldWidgetInstance = IntegerWidget()
IntegerField.widget = IntegerFieldWidgetInstance

import string

def IntegerValidator_validate(self, field, key, REQUEST):
    value = StringBaseValidator.validate(self, field, key, REQUEST)
    # we need to add this check again
    if value == "" and not field.get_value('required'):
        return value

    try:
        if value.find(' ')>0:
          value = value.replace(' ','')
        value = int(value)
    except ValueError:
        self.raise_error('not_integer', field)

    start = field.get_value('start')
    end = field.get_value('end')
    if start != "" and value < start:
        self.raise_error('integer_out_of_range', field)
    if end != "" and value >= end:
        self.raise_error('integer_out_of_range', field)
    return value

IntegerValidator.validate = IntegerValidator_validate

def StringBaseValidator_validate(self, field, key, REQUEST):
  # We had to add this patch for hidden fields of type "list"
  value = REQUEST.get(key, REQUEST.get('default_%s' % (key, )))
  if value is None:
    if field.get_value('required'):
      raise Exception, 'Required field %s has not been transmitted. Check that all required fields are in visible groups.' % (repr(field.id), )
    else:
      raise KeyError, 'Field %s is not present in request object.' % (repr(field.id), )
  if isinstance(value, str):
    value = string.strip(value)
  if field.get_value('required') and value == "":
      self.raise_error('required_not_found', field)
  #if field.get_value('uppercase'):
  #    value = value.upper()

  return value

StringBaseValidator.validate = StringBaseValidator_validate

def Widget_render_hidden(self, field, key, value, REQUEST, render_prefix=None):
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

def Widget_render_view(self, field, value, REQUEST=None, render_prefix=None):
    """Renders this widget for public viewing.
    """
    # default implementation
    if value is None:
        return ''
    return value

Widget.render_hidden = Widget_render_hidden
# default render_pdf for a Widget
Widget.render_pdf = Widget.render_view = Widget_render_view

def Widget_render_css(self, field, REQUEST):
  """
    Default render css for widget - to be overwritten in field classes.
    Should return valid css code as string.
    The value returned by this method will be used as inline style for a field.
  """
  pass
Widget.render_css = Widget_render_css

def Widget_get_css_list(self, field, REQUEST):
  """
    Return CSS needed by the widget - to be overwritten in field classes.
    Should return a list of CSS file names.
    These names will be appended to global css_list and included in a rendered page.
  """
  return []
Widget.get_css_list = Widget_get_css_list

def Widget_get_javascript_list(self, field, REQUEST):
  """
    Return JS needed by the widget - to be overwritten in field classes.
    Should return a list of javascript file names.
    These names will be appended to global js_list and included in a rendered page.
  """
  return []
Widget.get_javascript_list = Widget_get_javascript_list


from Products.Formulator import Widget as WidgetModule

for widget_name in ('MultiItemsWidget', 'LabelWidget',
                    'FileWidget', 'PasswordWidget',):
  widget = getattr(WidgetModule, widget_name)
  widget._old_render_view = widget.render_view
  widget.render_view = lambda self, field, value, REQUEST=None, render_prefix=None: \
    self._old_render_view(field, value)
  widget._old_render = widget.render
  widget.render = lambda self, field, key, value, REQUEST=None, render_prefix=None: \
    self._old_render(field, key, value, REQUEST)

from Products.Formulator.ListTextAreaField import ListTextAreaWidget
original_ListTextAreaWidget_render = ListTextAreaWidget.render
def ListTextAreaWidget_render(self, field, key, value, REQUEST, render_prefix=None):
  return original_ListTextAreaWidget_render(self, field, key, value, REQUEST)
ListTextAreaWidget.render = ListTextAreaWidget_render

from Products.Formulator.MethodField import MethodWidget
original_MethodWidget_render = MethodWidget.render
def MethodWidget_render(self, field, key, value, REQUEST, render_prefix=None):
  return original_MethodWidget_render(self, field, key, value, REQUEST)
MethodWidget.render = MethodWidget_render

from Products.Formulator.Validator import LinesValidator

def LinesValidator_validate(self, field, key, REQUEST):
    value = StringBaseValidator.validate(self, field, key, REQUEST)
    # Added as a patch for hidden values
    if isinstance(value, (list, tuple)):
      value = string.join(value, "\n")
    # we need to add this check again
    if value == "" and not field.get_value('required'):
        return []
    if field.get_value('unicode'):
        value = unicode(value, field.get_form_encoding())
    # check whether the entire input is too long
    max_length = field.get_value('max_length') or 0
    if max_length and len(value) > max_length:
        self.raise_error('too_long', field)
    # split input into separate lines
    lines = string.split(value, "\n")

    # check whether we have too many lines
    max_lines = field.get_value('max_lines') or 0
    if max_lines and len(lines) > max_lines:
        self.raise_error('too_many_lines', field)

    # strip extraneous data from lines and check whether each line is
    # short enough
    max_linelength = field.get_value('max_linelength') or 0
    result = []
    whitespace_preserve = field.get_value('whitespace_preserve')
    for line in lines:
        if not whitespace_preserve:
            line = string.strip(line)
        if max_linelength and len(line) > max_linelength:
            self.raise_error('line_too_long', field)
        result.append(line)

    return result

LinesValidator.validate = LinesValidator_validate

from Products.Formulator.Validator import FloatValidator
def FloatValidator_validate(self, field, key, REQUEST):
    value = StringBaseValidator.validate(self, field, key, REQUEST)
    if value == "" and not field.get_value('required'):
        return value
    value = value.replace(' ','')
    input_style = field.get_value('input_style')
    if value.find(',') >= 0:
        value = value.replace(',','.')
    if value.find('%')>=0:
        value = value.replace('%','')
    try:
        value = float(value)
        if input_style.find('%')>=0:
            value = value/100
    except ValueError:
        self.raise_error('not_float', field)
    return value

FloatValidator.validate = FloatValidator_validate

from Products.Formulator.Widget import SingleItemsWidget

def SingleItemsWidget_render_items(self, field, key, value, REQUEST, render_prefix=None):
  # get items
  cell = getattr(REQUEST, 'cell', None)
  items = field.get_value('items', REQUEST=REQUEST, cell=cell)
  if not items:
    # single item widget should have at least one child in order to produce
    # valid XHTML; disable it so user can not select it
    return [self.render_item('', '', '', '', 'disabled="disabled"')]

  # check if we want to select first item
  if not value and field.get_value('first_item',
                                   REQUEST=REQUEST,
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

SingleItemsWidget.render_items = SingleItemsWidget_render_items

def SingleItemsWidget_render_view(self, field, value, REQUEST=None, render_prefix=None):
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

def RadioWidget_render(self, field, key, value, REQUEST, render_prefix=None):
  input_hidden = render_element('input', type='hidden',
                                name="default_%s" % (key, ), value="")
  rendered_items = self.render_items(field, key, value, REQUEST)
  rendered_items.append(input_hidden)
  orientation = field.get_value('orientation')
  if orientation == 'horizontal':
      return string.join(rendered_items, "&nbsp;&nbsp;")
  else:
      return string.join(rendered_items, "<br />")

ListWidget.render_view = SingleItemsWidget_render_view
ListWidget.render_pdf = SingleItemsWidget_render_view
RadioWidget.render_view = SingleItemsWidget_render_view
RadioWidget.render = RadioWidget_render
RadioWidget.render_pdf = SingleItemsWidget_render_view

def MultiItemsWidget_render_items(self, field, key, value, REQUEST, render_prefix=None):
  # list is needed, not a tuple
  if isinstance(value, tuple):
      value = list(value)
  # need to deal with single item selects
  if not isinstance(value, list):
      value = [value]

  # XXX -yo
  selected_found = {}

  items = field.get_value('items',REQUEST=REQUEST, cell=getattr(REQUEST,'cell',None)) # Added request
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

MultiItemsWidget.render_items = MultiItemsWidget_render_items

from Products.Formulator.Widget import MultiListWidget

def MultiListWidget_render(self, field, key, value, REQUEST, render_prefix=None):
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

MultiListWidget.render = MultiListWidget_render

from Products.Formulator.Widget import MultiCheckBoxWidget

def MultiCheckBoxWidget_render(self, field, key, value, REQUEST, render_prefix=None):
  rendered_items = self.render_items(field, key, value, REQUEST)
  rendered_items.append(render_element('input', type='hidden', name="default_%s:int" % (key, ), value="0"))
  orientation = field.get_value('orientation')
  if orientation == 'horizontal':
    return string.join(rendered_items, "&nbsp;&nbsp;")
  else:
    return string.join(rendered_items, "<br />")

MultiCheckBoxWidget.render = MultiCheckBoxWidget_render

def ListWidget_render(self, field, key, value, REQUEST, render_prefix=None):
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
  
ListWidget.render = ListWidget_render

# JPS - Subfield handling with listbox requires extension
from Products.Formulator.StandardFields import DateTimeField
from Products.Formulator.Field import ZMIField

def DateTimeField_get_default(self, key, value, REQUEST):
    """
    Use the default method
    """
    return ZMIField._get_default(self, key, value, REQUEST)

def DateTimeField_get_user_input_value(self, key, REQUEST):
  """
  Try to get a value of the field from the REQUEST
  """
  if REQUEST.form['subfield_%s_%s' % (key, 'year')]:
    return None

DateTimeField._get_default = DateTimeField_get_default
DateTimeField._get_user_input_value = DateTimeField_get_user_input_value

from Products.Formulator.Widget import DateTimeWidget
old_date_time_widget_property_names = DateTimeWidget.property_names
from Products.Formulator.StandardFields import create_datetime_text_sub_form

class PatchedDateTimeWidget(DateTimeWidget):
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
    
    property_names = old_date_time_widget_property_names \
        + ['timezone_style', 'hide_day', 'hidden_day_is_last_day']

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

DateTimeField.widget = PatchedDateTimeWidget()

from Products.Formulator.Validator import DateTimeValidator, ValidationError, DateTime
from DateTime.DateTime import DateError, TimeError
from Products.Formulator.StandardFields import ListField, StringField, IntegerField, create_items
from Products.Formulator.Form import BasicForm
import Products.Formulator.StandardFields

gmt_timezones =  [('GMT%s' %zone, 'GMT%s' %zone,) for zone in range(-12, 0)]\
                  + [('GMT', 'GMT',),] \
                  + [('GMT+%s' %zone, 'GMT+%s' %zone,) for zone in range(1, 13)]
                  
def Patched_create_datetime_text_sub_form():
    """ Patch Products.Formulator.StandardFields so we can add timezone subfield """
    sub_form = BasicForm()
        
    year = IntegerField('year',
                        title="Year",
                        required=0,
                        display_width=4,
                        display_maxwidth=4,
                        max_length=4)
    
    month = IntegerField('month',
                         title="Month",
                         required=0,
                         display_width=2,
                         display_maxwidth=2,
                         max_length=2)
    
    day = IntegerField('day',
                       title="Day",
                       required=0,
                       display_width=2,
                       display_maxwidth=2,
                       max_length=2)
    sub_form.add_group("date")
    sub_form.add_fields([year, month, day], "date")
    
    hour = IntegerField('hour',
                        title="Hour",
                        required=0,
                        display_width=2,
                        display_maxwidth=2,
                        max_length=2)
    
    minute = IntegerField('minute',
                          title="Minute",
                          required=0,
                          display_width=2,
                          display_maxwidth=2,
                          max_length=2)

    ampm = StringField('ampm',
                       title="am/pm",
                       required=0,
                       display_width=2,
                       display_maxwidth=2,
                       max_length=2)
    timezone = ListField('timezone',
                          title = "Timezone",
                          required = 0,
                          default = 'GMT',
                          items = gmt_timezones,
                          size = 1)                       
    sub_form.add_fields([hour, minute, ampm, timezone], "time")
    return sub_form
    
def Patched_create_datetime_list_sub_form():
    """ Patch Products.Formulator.StandardFields so we can add timezone subfield """
    sub_form = BasicForm()

    year = ListField('year',
                     title="Year",
                     required=0,
                     default="",
                     items=create_items(2000, 2010, digits=4),
                     size=1)
    
    month = ListField('month',
                      title="Month",
                      required=0,
                      default="",
                      items=create_items(1, 13, digits=2),
                      size=1)
    
    day = ListField('day',
                    title="Day",
                    required=0,
                    default="",
                    items=create_items(1, 32, digits=2),
                    size=1)

    sub_form.add_group("date")
    sub_form.add_fields([year, month, day], "date")
    
    hour = IntegerField('hour',
                        title="Hour",
                        required=0,
                        display_width=2,
                        display_maxwidth=2,
                        max_length=2)
    
    minute = IntegerField('minute',
                          title="Minute",
                          required=0,
                          display_width=2,
                          display_maxwidth=2,
                          max_length=2)

    ampm = ListField('ampm',
                     title="am/pm",
                     required=0,
                     default="am",
                     items=[("am","am"),
                            ("pm","pm")],
                     size=1)
    timezone = ListField('timezone',
                          title = "Timezone",
                          required = 0,
                          default = 'GMT',
                          items = gmt_timezones,
                          size = 1)                                            
    sub_form.add_group("time")

    sub_form.add_fields([hour, minute, ampm, timezone], "time")
    return sub_form

Products.Formulator.StandardFields.create_datetime_text_sub_form = Patched_create_datetime_text_sub_form
Products.Formulator.StandardFields.create_datetime_list_sub_form = Patched_create_datetime_list_sub_form
    
class PatchedDateTimeValidator(DateTimeValidator):
    """
      Added support for key in every call to validate_sub_field
    """

    def validate(self, field, key, REQUEST):
        try:
            year = field.validate_sub_field('year', REQUEST, key=key)
            month = field.validate_sub_field('month', REQUEST, key=key)
            if field.get_value('hide_day'):
              day = 1
            else:
              day = field.validate_sub_field('day', REQUEST, key=key)

            if field.get_value('date_only'):
                hour = 0
                minute = 0
            elif field.get_value('allow_empty_time'):
                hour = field.validate_sub_field('hour', REQUEST, key=key)
                minute = field.validate_sub_field('minute', REQUEST, key=key)
                if hour == '' and minute == '':
                    hour = 0
                    minute = 0
                elif hour == '' or minute == '':
                    raise ValidationError('not_datetime', field)
            else:
                hour = field.validate_sub_field('hour', REQUEST, key=key)
                minute = field.validate_sub_field('minute', REQUEST, key=key)
        except ValidationError:
            self.raise_error('not_datetime', field)

        # handling of completely empty sub fields
        if ((year == '' and month == '') and
            (field.get_value('hide_day') or day == '') and
            (field.get_value('date_only') or (hour == '' and minute == '')
            or (hour == 0 and minute == 0))):
            if field.get_value('required'):
                self.raise_error('required_not_found', field)
            else:
                # field is not required, return None for no entry
                return None
        # handling of partially empty sub fields; invalid datetime
        if ((year == '' or month == '') or
            (not field.get_value('hide_day') and day == '') or
            (not field.get_value('date_only') and
             (hour == '' or minute == ''))):
            self.raise_error('not_datetime', field)

        if field.get_value('ampm_time_style'):
            ampm = field.validate_sub_field('ampm', REQUEST, key=key)
            if field.get_value('allow_empty_time'):
                if ampm == '':
                    ampm = 'am'
            hour = int(hour)
            # handling not am or pm
            # handling hour > 12
            if ((ampm != 'am') and (ampm != 'pm')) or (hour > 12):
                self.raise_error('not_datetime', field)
            if (ampm == 'pm') and (hour == 0):
                self.raise_error('not_datetime', field)
            elif ampm == 'pm' and hour < 12:
                hour += 12
                
        # handle possible timezone input
        timezone = ''
        if field.get_value('timezone_style'):
          timezone =  field.validate_sub_field('timezone', REQUEST, key=key)
          
        try:
            # handling of hidden day, which can be first or last day of the month:
            if field.get_value('hidden_day_is_last_day'):
              if int(month) == 12:
                tmp_year = int(year) + 1
                tmp_month = 1
              else:
                tmp_year = int(year)
                tmp_month = int(month) + 1
              tmp_day = DateTime(tmp_year, tmp_month, 1, hour, minute)
              result = tmp_day - 1
            else:
              result = DateTime(int(year),
                                int(month),
                                int(day),
                                hour,
                                minute)
              year = result.year()
              result = DateTime('%s/%s/%s %s:%s %s' % (year,
                                  int(month),
                                  int(day),
                                  hour,
                                  minute, timezone))
         # ugh, a host of string based exceptions (not since Zope 2.7)
        except ('DateTimeError', 'Invalid Date Components', 'TimeError',
                DateError, TimeError) :
            self.raise_error('not_datetime', field)

        # check if things are within range
        start_datetime = field.get_value('start_datetime')
        if (start_datetime not in (None, '') and
            result < start_datetime):
            self.raise_error('datetime_out_of_range', field)
        end_datetime = field.get_value('end_datetime')
        if (end_datetime not in (None, '') and
            result >= end_datetime):
            self.raise_error('datetime_out_of_range', field)

        return result

DateTimeField.validator = PatchedDateTimeValidator()

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
from Products.Formulator.StandardFields import FloatField
FloatField.widget = FloatWidgetInstance

###################################################################
# New formulator API
#
# render method on Field must change, and have a new parameter:
#   render_format
# which is used to call others methods ('html' call render_html)
###################################################################
# XXX Patching all Fields is not easy, as ERP5 defines his own fields.
# def Widget_render(self, field, key, value, REQUEST, render_format='html')
#   # Test if method defined on class
#   method_id = 'render_%' % render_format
#   if hasattr(aq_self(self), method_id):
#     # Try to return built-in renderer
#     return getattr(self, method_id )(self, field, key, value, REQUEST)
#   raise KeyError, "Rendering not defined"

# Monkey Patch
#
# Lookup all registered widgets and create render_html
# XXX This method is not a good way of patching,
# because it breaks inheritance
# XXX It's difficult to get all possible widgets, as ERP5 defines
# also his owns.
# for f in Formulator.widgets():
#   if not hasattr(f, '__erp5_patched'):
#     f.render_html = f.render
def Widget_render_html(self, *args, **kw):
  return self.render(*args, **kw)
Widget.render_html = Widget_render_html

def Field_render_html(self, *args, **kw):
  """
  render_html is used to as definition of render method in Formulator.
  """
  return self.render(*args, **kw)
Field.render_html = Field_render_html

def Field_render_htmlgrid(self, value=None, REQUEST=None, key=None, render_prefix=None):
  """
  render_htmlgrid returns a list of tuple (title, html render)
  """
  # What about CSS ? What about description ? What about error ?
  widget_key = self.generate_field_key(key=key)
  value = self._get_default(widget_key, value, REQUEST)
  __traceback_info__ = ('key=%s value=%r' % (key, value))
  # XXX: API transition try..except..log..raise. Remove after a while.
  try:
    return self.widget.render_htmlgrid(self, widget_key, value, REQUEST, render_prefix=render_prefix)
  except TypeError:
    LOG('FormulatorPatch', 0, 'To update: %r (%r)' % (self.widget.render_htmlgrid, getattr(self.widget.render_htmlgrid, 'func_code', None)))
    raise

Field.render_htmlgrid = Field_render_htmlgrid

def Widget_render_htmlgrid(self, field, key, value, REQUEST, render_prefix=None):
  """
  render_htmlgrid returns a list of tuple (title, html render)
  """
  # XXX Calling _render_helper on the field is not optimized
  # XXX: API transition try..except..log..raise. Remove after a while.
  try:
    return ((field.get_value('title'), 
             field._render_helper(key, value, REQUEST, render_prefix=render_prefix)),)
  except TypeError:
    LOG('FormulatorPatch', 0, 'To update: %r (%r)' % (field._render_helper, getattr(field._render_helper, 'func_code', None)))
    raise
Widget.render_htmlgrid = Widget_render_htmlgrid

# Generic possible renderers
#   def render_ext(self, field, key, value, REQUEST, render_prefix=None):
#     return getattr(self, '%s_render' % self.__class__.__name__)
#
#   def render_pt(self, field, key, value, REQUEST, render_prefix=None):
#     """
#     Call a page template which contains 1 macro per field
#     """
#     return self.field_master(self.__class__.__name__)
#
#   def render_grid(self, field, key, value, REQUEST, render_prefix=None):
#     return ((self.get_value('title'), self.get_value('value'),)
#    # What about CSS ? What about description ? What about error ?
#    # What about rendering a listbox ?
#    # Grid is only valid if stucture of grid has some meaning and is
#    # implemeted by listbox (ex. spreadsheet = grid)
#

def Field_render_pdf(self, value=None, REQUEST=None, key=None, **kw):
  """
  render_pdf renders the field for reportlab
  """
  return self.widget.render_pdf(self, value)
Field.render_pdf = Field_render_pdf

def Field_render_css(self, REQUEST=None):
  """
  Generate css content which will be added inline.

  XXX key parameter may be needed.
  """
  return self.widget.render_css(self, REQUEST)
Field.render_css = Field_render_css

def Field_get_css_list(self, REQUEST=None):
  """
    Returns list of css sheets needed by the field
    to be included in global css imports
  """
  return self.widget.get_css_list(self, REQUEST)
Field.get_css_list = Field_get_css_list


def Field_get_javascript_list(self, REQUEST=None):
  """
    Returns list of javascript needed by the field
    to be included in global js imports
  """
  return self.widget.get_javascript_list(self, REQUEST)
Field.get_javascript_list = Field_get_javascript_list


from Products.Formulator.TALESField import TALESWidget
def TALESWidget_render_view(self, field, value, REQUEST=None, render_prefix=None):
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

TALESWidget.render_view = TALESWidget_render_view

original_TALESWidget_render = TALESWidget.render
def TALESWidget_render(self, field, key, value, REQUEST, render_prefix=None):
  return original_TALESWidget_render(self, field, key, value, REQUEST)
TALESWidget.render = TALESWidget_render

def Widget_render_dict(self, field, value):
  """
  This is yet another field rendering. It is designed to allow code to
  understand field's value data by providing its type and format when
  applicable.
  """
  return None
Widget.render_dict = Widget_render_dict

def Field_render_dict(self, value=None, REQUEST=None, key=None, **kw):
  """
  This is yet another field rendering. It is designed to allow code to
  understand field's value data by providing its type and format when
  applicable.
  """
  return self.widget.render_dict(self, value)
Field.render_dict = Field_render_dict


# Find support in ZMI. This is useful for development.
def getSearchSource(obj):
  obj_type = type(obj)
  if obj_type is MethodField.Method:
    return obj.method_name
  elif obj_type is TALESField.TALESMethod:
    return obj._text
  return str(obj)
def Field_PrincipiaSearchSource(self):
  return ''.join(
    map(getSearchSource,
        (self.values.values()+self.tales.values()+self.overrides.values())))
Field.PrincipiaSearchSource = Field_PrincipiaSearchSource

# If type definition is missing for LinesField, the input text will be
# splitted into list like ['f', 'o', 'o'] with original Formulator's
# implementation. So explicit conversion to list is required before
# passing to LinesTextAreaWidget's render and render_view methods.
from Products.Formulator.Widget import LinesTextAreaWidget

original_LinesTextAreaWidget_render = LinesTextAreaWidget.render
def LinesTextAreaWidget_render(self, field, key, value, REQUEST, render_prefix=None):
  if isinstance(value, (str, unicode)):
    value = [value]
  return original_LinesTextAreaWidget_render(self, field, key, value, REQUEST)
LinesTextAreaWidget.render = LinesTextAreaWidget_render

original_LinesTextAreaWidget_render_view = LinesTextAreaWidget.render_view
def LinesTextAreaWidget_render_view(self, field, value, REQUEST=None, render_prefix=None):
  if isinstance(value, (str, unicode)):
    value = [value]
  return original_LinesTextAreaWidget_render_view(self, field, value)
LinesTextAreaWidget.render_view = LinesTextAreaWidget_render_view

from Products.Formulator.Validator import EmailValidator
import re
# This regexp is based on the default Formulator regexp, and add the
# possibility to allow ' in the email address
# see: http://www.regular-expressions.info/email.html
EmailValidator.pattern = \
  re.compile('^[0-9a-zA-Z_\'&.%+-]+@([0-9a-zA-Z]([0-9a-zA-Z-]*[0-9a-zA-Z])?\.)+[a-zA-Z]{2,6}$')

