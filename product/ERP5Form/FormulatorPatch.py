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
from AccessControl import ClassSecurityInfo
from zLOG import LOG

class PatchedField(Field):

    security = ClassSecurityInfo()
    security.declareProtected('Access contents information',
                              'generate_field_key')
    def generate_field_key(self, validation=0, key=None):
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

    security.declareProtected('View', 'render')
    def render(self, value=None, REQUEST=None, key=None):
        """Render the field widget.
        value -- the value the field should have (for instance
                 from validation).
        REQUEST -- REQUEST can contain raw (unvalidated) field
                 information. If value is None, REQUEST is searched
                 for this value.
        if value and REQUEST are both None, the 'default' property of
        the field will be used for the value.
        """
        return self._render_helper(self.generate_field_key(key=key), value, REQUEST)

    security.declareProtected('View', 'render_sub_field')
    def render_sub_field(self, id, value=None, REQUEST=None, key=None):
        """Render a sub field, as part of complete rendering of widget in
        a form. Works like render() but for sub field.
           Added key parameter for ERP5 in order to be compatible with listbox/matrixbox
        """
        return self.sub_form.get_field(id)._render_helper(
            self.generate_subfield_key(id, key=key), value, REQUEST)

    def generate_subfield_key(self, id, validation=0, key=None):
        """Generate the key Silva uses to render a sub field.
           Added key parameter for ERP5
           Added key parameter for ERP5 in order to be compatible with listbox/matrixbox
        """
        if key is None: key = self.id
        if self.field_record is None or validation:
            return 'subfield_%s_%s'%(key, id)
        return '%s.subfield_%s_%s:record' % (self.field_record, key, id)                        

    def validate_sub_field(self, id, REQUEST, key=None):
        """Validates a subfield (as part of field validation).
        """
        return self.sub_form.get_field(id)._validate_helper(
            self.generate_subfield_key(id, validation=1, key=key), REQUEST)

Field.generate_field_key = PatchedField.generate_field_key
Field.render = PatchedField.render
Field.render_sub_field = PatchedField.render_sub_field
Field.generate_subfield_key = PatchedField.generate_subfield_key

from Products.Formulator.Validator import SelectionValidator
from Products.Formulator.Validator import StringBaseValidator

def SelectionValidator_validate(self, field, key, REQUEST):
    value = StringBaseValidator.validate(self, field, key, REQUEST)

    if value == "" and not field.get_value('required'):
        return value

    # get the text and the value from the list of items
    # Patch by JPS for Listbox cell
    for item in field.get_value('items', cell=getattr(REQUEST,'cell',None)):
        try:
            item_text, item_value = item
        except ValueError:
            item_text = item
            item_value = item

        # check if the value is equal to the string/unicode version of
        # item_value; if that's the case, we can return the *original*
        # value in the list (not the submitted value). This way, integers
        # will remain integers.
        # XXX it is impossible with the UI currently to fill in unicode
        # items, but it's possible to do it with the TALES tab
        if field.get_value('unicode') and type(item_value) == type(u''):
            str_value = item_value.encode(field.get_form_encoding())
        else:
            str_value = str(item_value)

        if str_value == value:
            return item_value

    # if we didn't find the value, return error
    self.raise_error('unknown_selection', field)

SelectionValidator.validate = SelectionValidator_validate

# The required field should have a default value to 0
from Products.Formulator.DummyField import fields

StringBaseValidator_required = fields.CheckBoxField('required',
                                title='Required',
                                description=(
    "Checked if the field is required; the user has to fill in some "
    "data."),
                                default=0)
StringBaseValidator.required = StringBaseValidator_required


from Products.Formulator.Validator import SelectionValidator

def SelectionValidator_validate(self, field, key, REQUEST):
    value = StringBaseValidator.validate(self, field, key, REQUEST)

    if value == "" and not field.get_value('required'):
        return value

    # get the text and the value from the list of items
    for item in field.get_value('items', cell=getattr(REQUEST,'cell',None)) + [field.get_value('default', cell=getattr(REQUEST,'cell',None))]:
        try:
            item_text, item_value = item
        except ValueError:
            item_text = item
            item_value = item

        # check if the value is equal to the string/unicode version of
        # item_value; if that's the case, we can return the *original*
        # value in the list (not the submitted value). This way, integers
        # will remain integers.
        # XXX it is impossible with the UI currently to fill in unicode
        # items, but it's possible to do it with the TALES tab
        if field.get_value('unicode') and type(item_value) == type(u''):
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
    values = REQUEST.get(key, [])
    # NOTE: a hack to deal with single item selections
    if type(values) is not type([]):
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
    if type(default_value) in (type([]), type(())):
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
    result = not not REQUEST.get(key, 0)
    if result==True:
       return 1
    else:
       return 0

BooleanValidator.validate = BooleanValidator_validate

# Patch the render_view of a TextAreaWidget so that
# it is rendered as a nice box, it is using the tag
# readonly understood by most browsers for a text area

from Products.Formulator.Widget import TextAreaWidget
from Products.Formulator.Widget import render_element
from DocumentTemplate.DT_Util import html_quote

def TextAreaWidget_render_view(self, field, value):
    width = field.get_value('width')
    height = field.get_value('height')

    return render_element("textarea",
                          name='',
                          css_class=field.get_value('css_class'),
                          cols=width,
                          rows=height,
                          contents=html_quote(value),
                          extra='readonly')

TextAreaWidget.render_view = TextAreaWidget_render_view

# Patch the render_view of LinkField so that it is clickable in read-only mode.
from Products.Formulator.Widget import TextWidget
from Products.Formulator.StandardFields import LinkField
from Globals import get_request
from urlparse import urljoin

class PatchedLinkWidget(TextWidget) :
  def render_view(self, field, value) :
    """Render link.
    """
    REQUEST = get_request()
    link_type = field.get_value('link_type')

    if link_type == 'internal':
      value = urljoin(REQUEST['BASE0'], value)
    elif link_type == 'relative':
      value = urljoin(REQUEST['URL1'], value)

    return '<a href="%s">%s</a>' % (value, field.get_value('title', cell=REQUEST.get('cell')))

PatchedLinkWidgetInstance = PatchedLinkWidget()
LinkField.widget = PatchedLinkWidgetInstance

class IntegerWidget(TextWidget) :
  def render(self, field, key, value, REQUEST) :
    """Render link.
    """
    if type(value) is type(1.0):
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
  value = REQUEST.get(key, "")
  if type(value) is type('a'):
    value = string.strip(value)
  if field.get_value('required') and value == "":
      self.raise_error('required_not_found', field)
  return value

StringBaseValidator.validate = StringBaseValidator_validate

def render_hidden(self, field, key, value, REQUEST):
    """Renders this widget as a hidden field.
    """
    #LOG('render_hidden',0,str(value))
    try:
        extra = field.get_value('extra')
    except KeyError:
    # In case extra is not defined as in DateTimeWidget
        extra = ''
    result = ''
    # We must adapt the rendering to the type of the value
    # in order to get the correct type back
    if type(value) is type([]) or type(value) is type(()):
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

Widget.render_hidden = render_hidden

from Products.Formulator.Validator import LinesValidator

def LinesValidator_validate(self, field, key, REQUEST):
    value = StringBaseValidator.validate(self, field, key, REQUEST)
    # Added as a patch for hidden values
    if type(value) is type([]) or type(value) is type(()):
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

    try:
        if value.find(',') >= 0:
            value = value.replace(',','.')
        value = float(value)
    except ValueError:
        self.raise_error('not_float', field)
    return value

FloatValidator.validate = FloatValidator_validate

from Products.Formulator.Widget import SingleItemsWidget

def SingleItemsWidget_render_items(self, field, key, value, REQUEST):
  # get items
  items = field.get_value('items', REQUEST=REQUEST, cell=getattr(REQUEST,'cell',None))

  # check if we want to select first item
  if not value and field.get_value('first_item') and len(items) > 0:
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
          rendered_item = self.render_selected_item(item_text,
                                                    item_value,
                                                    key,
                                                    css_class,
                                                    extra_item)
          selected_found = 1
      else:
          rendered_item = self.render_item(item_text,
                                            item_value,
                                            key,
                                            css_class,
                                            extra_item)

      rendered_items.append(rendered_item)

  # XXX We want to make sure that we always have the current value in items. -yo
  if not selected_found and value:
      rendered_item = self.render_selected_item('??? (%s)' % value,
                                                value,
                                                key,
                                                css_class,
                                                extra_item)
      rendered_items.append(rendered_item)

  return rendered_items

SingleItemsWidget.render_items = SingleItemsWidget_render_items

from Products.Formulator.Widget import MultiItemsWidget

def MultiItemsWidget_render_items(self, field, key, value, REQUEST):
  # need to deal with single item selects
  if type(value) is not type([]):
      value = [value]

  # XXX -yo
  selected_found = {}

  items = field.get_value('items',REQUEST=REQUEST, cell=getattr(REQUEST,'cell',None)) # The only thing changes, added request
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
          rendered_item = self.render_selected_item(item_text,
                                                    item_value,
                                                    key,
                                                    css_class,
                                                    extra_item)
          # XXX -yo
          index = value.index(item_value)
          selected_found[index] = 1
      else:
          rendered_item = self.render_item(item_text,
                                           item_value,
                                           key,
                                           css_class,
                                           extra_item)

      rendered_items.append(rendered_item)

  # XXX We want to make sure that we always have the current value in items. -yo
  for index in range(len(value)):
    v = value[index]
    if index not in selected_found and v:
      rendered_item = self.render_selected_item('??? (%s)' % v,
                                                v,
                                                key,
                                                css_class,
                                                extra_item)
      rendered_items.append(rendered_item)

  return rendered_items

MultiItemsWidget.render_items = MultiItemsWidget_render_items

# JPS - Subfield handling with listbox requires extension
from Products.Formulator.StandardFields import DateTimeField

class PatchedDateTimeField(DateTimeField):
    """
      Make sur we test if this REQUEST parameter has a form
      attribute. In ERP5, we sometimes use the REQUEST to pass
      subobjects to forms.
    """
  
    def _get_default(self, key, value, REQUEST):
        if value is not None:
            return value
        # if there is something in the request then return None
        # sub fields should pick up defaults themselves
        if REQUEST is not None and hasattr(REQUEST, 'form') and \
          REQUEST.form.has_key('subfield_%s_%s' % (self.id, 'year')):
            return None
        else:
            return self.get_value('default')

DateTimeField._get_default = PatchedDateTimeField._get_default
    
from Products.Formulator.Widget import DateTimeWidget

class PatchedDateTimeWidget(DateTimeWidget):
    """
      Added support for key in every call to render_sub_field
    """
    
    def render(self, field, key, value, REQUEST):
        use_ampm = field.get_value('ampm_time_style')
        # FIXME: backwards compatibility hack:
        if not hasattr(field, 'sub_form'):
            from StandardFields import create_datetime_text_sub_form
            field.sub_form = create_datetime_text_sub_form()
            
        if value is None and field.get_value('default_now'):
            value = DateTime()
        if value is None:
            year = None
            month = None
            day = None
            hour = None
            minute = None
            ampm = None
        else:
            year = "%04d" % value.year()
            month = "%02d" % value.month()
            day = "%02d" % value.day()
            if use_ampm:
                hour = "%02d" % value.h_12()
            else:
                hour = "%02d" % value.hour()
            minute = "%02d" % value.minute()
            ampm = value.ampm()
        
        input_order = field.get_value('input_order')
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
                
            return date_result + '&nbsp;&nbsp;&nbsp;' + time_result
        else:
            return date_result
        
DateTimeField.widget = PatchedDateTimeWidget()

from Products.Formulator.Validator import DateTimeValidator

class PatchedDateTimeValidator(DateTimeValidator):
    """
      Added support for key in every call to validate_sub_field
    """

    def validate(self, field, key, REQUEST):    
        try:
            year = field.validate_sub_field('year', REQUEST, key=key)
            month = field.validate_sub_field('month', REQUEST, key=key)
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
        if ((year == '' and month == '' and day == '') and
            (field.get_value('date_only') or (hour == '' and minute == '')
            or (hour == 0 and minute == 0))): 
            if field.get_value('required'):
                self.raise_error('required_not_found', field)
            else:
                # field is not required, return None for no entry
                return None
        # handling of partially empty sub fields; invalid datetime
        if ((year == '' or month == '' or day == '') or
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

        try:
            result = DateTime(int(year), int(month), int(day), hour, minute)
        # ugh, a host of string based exceptions
        except ('DateTimeError', 'Invalid Date Components', 'TimeError'):
            self.raise_error('not_datetime', field)

        # check if things are within range
        start_datetime = field.get_value('start_datetime')
        if (start_datetime is not None and
            result < start_datetime):
            self.raise_error('datetime_out_of_range', field)
        end_datetime = field.get_value('end_datetime')
        if (end_datetime is not None and
            result >= end_datetime):
            self.raise_error('datetime_out_of_range', field)

        return result

DateTimeField.validator = PatchedDateTimeValidator()
