# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re
import six
from . import PatternChecker
from .DummyField import fields
from DateTime import DateTime
from threading import Thread
from six.moves.urllib.request import urlopen
from six.moves.urllib.parse import urljoin
from .Errors import ValidationError
from DateTime.DateTime import DateError, TimeError
import unicodedata

class ValidatorBase:
    """Even more minimalistic base class for validators.
    """
    property_names = ['enabled','editable']

    message_names = []

    enabled = fields.CheckBoxField('enabled',
                                   title="Enabled",
                                   description=(
        "If a field is not enabled, it will considered to be not "
        "in the form during rendering or validation. Be careful "
        "when you change this state dynamically (in the TALES tab): "
        "a user could submit a field that since got disabled, or "
        "get a validation error as a field suddenly got enabled that "
        "wasn't there when the form was drawn."),
                                   css_class="form-check-input",
                                   default=1)

    editable = fields.CheckBoxField('editable',
                                   title="Editable",
                                   description=(
        "If a field is not editable, then the user can only see"
        "the value. This allows to drawn very different forms depending"
        "on use permissions."),
                                   css_class="form-check-input",
                                   default=1)

    def raise_error(self, error_key, field):
        raise ValidationError(error_key, field)

    def validate(self, field, key, REQUEST):
        pass # override in subclass

    def need_validate(self, field, key, REQUEST):
        """Default behavior is always validation.
        """
        return 1

class Validator(ValidatorBase):
    """Validates input and possibly transforms it to output.
    """
    property_names = ValidatorBase.property_names + ['external_validator']

    external_validator = fields.MethodField('external_validator',
                                            title="External Validator",
                                            description=(
        "When a method name is supplied, this method will be "
        "called each time this field is being validated. All other "
        "validation code is called first, however. The value (result of "
        "previous validation) and the REQUEST object will be passed as "
        "arguments to this method. Your method should return true if the "
        "validation succeeded. Anything else will cause "
        "'external_validator_failed' to be raised."),
                                            css_class="form-control",
                                            default="",
                                            required=0)

    message_names = ValidatorBase.message_names + ['external_validator_failed']

    external_validator_failed = "The input failed the external validator."

class StringBaseValidator(Validator):
    """Simple string validator.
    """
    property_names = Validator.property_names + ['required', 'whitespace_preserve']

    required = fields.CheckBoxField('required',
                                title='Required',
                                description=(
    "Checked if the field is required; the user has to fill in some "
    "data."),
                                default=0)

    whitespace_preserve = fields.CheckBoxField('whitespace_preserve',
                                               title="Preserve whitespace",
                                               description=(
        "Checked if the field preserves whitespace. This means even "
        "just whitespace input is considered to be data."),
                                               css_class="form-check-input",
                                               default=0)

    message_names = Validator.message_names + ['required_not_found']

    required_not_found = 'Input is required but no input given.'

    def validate(self, field, key, REQUEST):
      # We had to add this patch for hidden fields of type "list"
      value = REQUEST.get(key, REQUEST.get('default_%s' % (key, )))
      if value is None:
        if field.get_value('required'):
          raise Exception('Required field %r has not been transmitted. Check that all required fields are in visible groups.' % field.id)
        else:
          raise KeyError('Field %r is not present in request object.' % field.id)
      if isinstance(value, str):
        if field.has_value('whitespace_preserve'):
          if not field.get_value('whitespace_preserve'):
            value = value.strip()
        else:
          # XXX Compatibility: use to prevent KeyError exception from get_value
          value = value.strip()
      if field.get_value('required') and value == "":
        self.raise_error('required_not_found', field)

      return value

class StringValidator(StringBaseValidator):
    property_names = StringBaseValidator.property_names +\
                     ['unicode', 'max_length', 'truncate']

    unicode = fields.CheckBoxField('unicode',
                                   title='Unicode',
                                   description=(
        "Checked if the field delivers a unicode string instead of an "
        "8-bit string."),
                                   css_class="form-check-input",
                                   default=0)

    max_length = fields.IntegerField('max_length',
                                     title='Maximum length',
                                     description=(
        "The maximum amount of characters that can be entered in this "
        "field. If set to 0 or is left empty, there is no maximum. "
        "Note that this is server side validation."),
                                     css_class="form-control",
                                     default="",
                                     required=0)

    truncate = fields.CheckBoxField('truncate',
                                    title='Truncate',
                                    description=(
        "If checked, truncate the field if it receives more input than is "
        "allowed. The normal behavior in this case is to raise a validation "
        "error, but the text can be silently truncated instead."),
                                    css_class="form-check-input",
                                    default=0)

    message_names = StringBaseValidator.message_names +\
                    ['too_long']

    too_long = 'Too much input was given.'

    def validate(self, field, key, REQUEST):
        value = StringBaseValidator.validate(self, field, key, REQUEST)
        if field.get_value('unicode'):
            # use acquisition to get encoding of form
            value = six.text_type(value, field.get_form_encoding())

        max_length = field.get_value('max_length') or 0
        truncate = field.get_value('truncate')

        if max_length > 0 and len(value) > max_length:
            if truncate:
                value = value[:max_length]
            else:
                self.raise_error('too_long', field)
        return value

StringValidatorInstance = StringValidator()

class EmailValidator(StringValidator):
    message_names = StringValidator.message_names + ['not_email']

    not_email = 'You did not enter an email address.'

    # This regex allows for a simple username or a username in a
    # multi-dropbox (%). The host part has to be a normal fully
    # qualified domain name, allowing for 6 characters (.museum) as a
    # TLD.  No bang paths (uucp), no dotted-ip-addresses, no angle
    # brackets around the address (we assume these would be added by
    # some custom script if needed), and of course no characters that
    # don't belong in an e-mail address.
    pattern = re.compile('^[0-9a-zA-Z_\'&.%+-]+@([0-9a-zA-Z]([0-9a-zA-Z-]*[0-9a-zA-Z])?\.)+[a-zA-Z]{2,}$')

    def validate(self, field, key, REQUEST):
        value = StringValidator.validate(self, field, key, REQUEST)
        if value == "" and not field.get_value('required'):
            return value

        if self.pattern.search(value.lower()) == None:
            self.raise_error('not_email', field)
        return value

EmailValidatorInstance = EmailValidator()

class PatternValidator(StringValidator):
    # does the real work
    checker = PatternChecker.PatternChecker()

    property_names = StringValidator.property_names +\
                     ['pattern']

    pattern = fields.StringField('pattern',
                                 title="Pattern",
                                 required=1,
                                 default="",
                                 description=(
        "The pattern the value should conform to. Patterns are "
        "composed of digits ('d'), alphabetic characters ('e') and "
        "alphanumeric characters ('f'). Any other character in the pattern "
        "should appear literally in the value in that place. Internal "
        "whitespace is checked as well but may be included in any amount. "
        "Example: 'dddd ee' is a Dutch zipcode (postcode). "
        "NOTE: currently experimental and details may change!"),
                                 css_class="form-control",
                                 )

    message_names = StringValidator.message_names +\
                    ['pattern_not_matched']

    pattern_not_matched = "The entered value did not match the pattern."

    def validate(self, field, key, REQUEST):
        value = StringValidator.validate(self, field, key, REQUEST)
        if value == "" and not field.get_value('required'):
            return value
        value = self.checker.validate_value([field.get_value('pattern')],
                                            value)
        if value is None:
            self.raise_error('pattern_not_matched', field)
        return value

PatternValidatorInstance = PatternValidator()

class BooleanValidator(Validator):
    property_names = Validator.property_names + ['required']

    required = fields.CheckBoxField('required',
                                title='Required',
                                description=(
    "Checked if the field is required; the user has to check."),
                                css_class="form-check-input",
                                default=0)

    message_names = Validator.message_names + ['required_not_found']

    required_not_found = 'This field is mandatory.'

    def validate(self, field, key, REQUEST):
      result = REQUEST.get(key, REQUEST.get('default_%s' % key))
      if result is None:
        raise KeyError('Field %r is not present in request object.' % field.id)
      # XXX If the checkbox is hidden, Widget_render_hidden is used instead of
      #     CheckBoxWidget_render, and ':int' suffix is missing.
      value = result and result != '0' and 1 or 0
      if not value and field.get_value('required'):
        self.raise_error('required_not_found', field)
      return value


BooleanValidatorInstance = BooleanValidator()

class IntegerValidator(StringBaseValidator):
    property_names = StringBaseValidator.property_names +\
                     ['start', 'end']

    start = fields.IntegerField('start',
                                title='Start',
                                description=(
        "The integer entered by the user must be larger than or equal to "
        "this value. If left empty, there is no minimum."),
                                css_class="form-control",
                                default="",
                                required=0)

    end = fields.IntegerField('end',
                              title='End',
                              description=(
        "The integer entered by the user must be smaller than this "
        "value. If left empty, there is no maximum."),
                              css_class="form-control",
                              default="",
                              required=0)

    message_names = StringBaseValidator.message_names +\
                    ['not_integer', 'integer_out_of_range']

    not_integer = 'You did not enter an integer.'
    integer_out_of_range = 'The integer you entered was out of range.'

    def validate(self, field, key, REQUEST):
      value = StringBaseValidator.validate(self, field, key, REQUEST)
      # we need to add this check again
      if value == "" and not field.get_value('required'):
        return value

      value = normalizeFullWidthNumber(value)

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

IntegerValidatorInstance = IntegerValidator()

class FloatValidator(StringBaseValidator):
  message_names = StringBaseValidator.message_names + ['not_float',
                                                       'too_large_precision']

  not_float = "You did not enter a floating point number."
  too_large_precision = "The number you input has too large precision."

  def _validatePrecision(self, field, value, decimal_point, input_style):
    """ Validate the consistency among the precision and the user inputs """
    if not field.has_value('precision'):
      return value
    precision = field.get_value('precision')
    if precision == '' or precision is None:
      # need to validate when the precision is 0
      return value
    index = value.find(decimal_point)
    if index < 0:
      return value
    input_precision_length = len(value[index+1:])
    if input_precision_length > int(precision):
      self.raise_error('too_large_precision', field)
    return value

  def validate(self, field, key, REQUEST):
    value = StringBaseValidator.validate(self, field, key, REQUEST)
    if value == "" and not field.get_value('required'):
      return value

    value = normalizeFullWidthNumber(value)

    input_style = field.get_value('input_style')
    decimal_separator = ''
    decimal_point = '.'

    if input_style == "-1234.5":
      decimal_point = '.'
    elif input_style == '-1 234.5':
      decimal_separator = ' '
      decimal_point = '.'
    elif input_style == '-1 234,5':
      decimal_separator = ' '
      decimal_point = ','
    elif input_style == '-1.234,5':
      decimal_separator = '.'
      decimal_point = ','
    elif input_style == '-1,234.5':
      decimal_separator = ','
      decimal_point = '.'

    value = value.replace(decimal_separator,'')
    input_style = field.get_value('input_style')
    if value.find(decimal_point) >= 0:
      value = value.replace(decimal_point, '.')
    if value.find('%') >= 0:
      value = value.replace('%', '')
    value = self._validatePrecision(field, value, decimal_point, input_style)
    try:
      value = float(value)
      if input_style.find('%')>=0:
        value = value / 100
    except ValueError:
      self.raise_error('not_float', field)
    return value

FloatValidatorInstance = FloatValidator()

class LinesValidator(StringBaseValidator):
  property_names = StringBaseValidator.property_names +\
                    ['unicode', 'max_lines', 'max_linelength', 'max_length']

  unicode = fields.CheckBoxField('unicode',
                                  title='Unicode',
                                  description=(
      "Checked if the field delivers a unicode string instead of an "
      "8-bit string."),
                                  css_class="form-check-input",
                                  default=0)

  max_lines = fields.IntegerField('max_lines',
                                  title='Maximum lines',
                                  description=(
      "The maximum amount of lines a user can enter. If set to 0, "
      "or is left empty, there is no maximum."),
                                  css_class="form-control",
                                  default="",
                                  required=0)

  max_linelength = fields.IntegerField('max_linelength',
                                        title="Maximum length of line",
                                        description=(
      "The maximum length of a line. If set to 0 or is left empty, there "
      "is no maximum."),
                                        css_class="form-control",
                                        default="",
                                        required=0)

  max_length = fields.IntegerField('max_length',
                                    title="Maximum length (in characters)",
                                    description=(
      "The maximum total length in characters that the user may enter. "
      "If set to 0 or is left empty, there is no maximum."),
                                    css_class="form-control",
                                    default="",
                                    required=0)

  message_names = StringBaseValidator.message_names +\
                  ['too_many_lines', 'line_too_long', 'too_long']

  too_many_lines = 'You entered too many lines.'
  line_too_long = 'A line was too long.'
  too_long = 'You entered too many characters.'

  def validate(self, field, key, REQUEST):
    value = StringBaseValidator.validate(self, field, key, REQUEST)
    # Added as a patch for hidden values
    if isinstance(value, (list, tuple)):
      value = '\n'.join(value)
    # we need to add this check again
    if value == "" and not field.get_value('required'):
      return []
    if field.get_value('unicode'):
        value = six.text_type(value, field.get_form_encoding())
    # check whether the entire input is too long
    max_length = field.get_value('max_length') or 0
    if max_length and len(value) > max_length:
      self.raise_error('too_long', field)
    # split input into separate lines
    lines = value.replace('\r\n', '\n').split('\n')

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
        line = line.strip()
      if max_linelength and len(line) > max_linelength:
        self.raise_error('line_too_long', field)
      result.append(line)

    return result

LinesValidatorInstance = LinesValidator()

class TextValidator(LinesValidator):
    def validate(self, field, key, REQUEST):
        value = LinesValidator.validate(self, field, key, REQUEST)
        # we need to add this check again
        if value == [] and not field.get_value('required'):
            return ""

        # join everything into string again with \n and return
        return "\n".join(value)

TextValidatorInstance = TextValidator()

class SelectionValidator(StringBaseValidator):

    property_names = StringBaseValidator.property_names +\
                     ['unicode']

    unicode = fields.CheckBoxField('unicode',
                                   title='Unicode',
                                   description=(
        "Checked if the field delivers a unicode string instead of an "
        "8-bit string."),
                                   css_class="form-check-input",
                                   default=0)

    message_names = StringBaseValidator.message_names +\
                    ['unknown_selection']

    unknown_selection = 'You selected an item that was not in the list.'

    def validate(self, field, key, REQUEST):
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
        if six.PY2 and field.get_value('unicode') and isinstance(item_value, six.text_type):
          str_value = item_value.encode(field.get_form_encoding())
        else:
          str_value = str(item_value)

        if str_value == value:
          return item_value

      # if we didn't find the value, return error
      self.raise_error('unknown_selection', field)

SelectionValidatorInstance = SelectionValidator()

class MultiSelectionValidator(Validator):
    property_names = Validator.property_names + ['required', 'unicode']

    required = fields.CheckBoxField('required',
                                    title='Required',
                                    description=(
        "Checked if the field is required; the user has to fill in some "
        "data."),
                                    css_class="form-check-input",
                                    default=1)

    unicode = fields.CheckBoxField('unicode',
                                   title='Unicode',
                                   description=(
        "Checked if the field delivers a unicode string instead of an "
        "8-bit string."),
                                   css_class="form-check-input",
                                   default=0)

    message_names = Validator.message_names + ['required_not_found',
                                               'unknown_selection']

    required_not_found = 'Input is required but no input given.'
    unknown_selection = 'You selected an item that was not in the list.'

    def validate(self, field, key, REQUEST):
      if REQUEST.get('default_%s' % (key, )) is None:
        raise KeyError('Field %r is not present in request object (marker field default_%s not found).' % (field.id, key))
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
        values = [six.text_type(value, field.get_form_encoding())
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
        if int_value is not None and int_value in value_dict:
          result.append(int_value)
          continue
        if value in value_dict:
          result.append(value)
          continue
        self.raise_error('unknown_selection', field)
      # everything checks out
      return result

MultiSelectionValidatorInstance = MultiSelectionValidator()

class FileValidator(Validator):
    required = fields.CheckBoxField('required',
                                    title='Required',
                                    description=(
                                      "Checked if the field is required; the "
                                      "user has to fill in some data."),
                                    css_class="form-check-input",
                                    default=0)
    property_names = Validator.property_names + ['required']

    message_names = Validator.message_names + ['required_not_found']
    required_not_found = 'Input is required but no input given.'

    def validate(self, field, key, REQUEST):
        value = REQUEST.get(key, None)
        if field.get_value('required') and value in (None, ''):
                  self.raise_error('required_not_found', field)
        return value

FileValidatorInstance = FileValidator()

class LinkHelper:
    """A helper class to check if links are openable.
    """
    status = 0

    def __init__(self, link):
        self.link = link

    def open(self):
        try:
            urlopen(self.link)
        except:
            # all errors will definitely result in a failure
            pass
        else:
            # FIXME: would like to check for 404 errors and such?
            self.status = 1

class LinkValidator(StringValidator):
    property_names = StringValidator.property_names +\
                     ['check_link', 'check_timeout', 'link_type']

    check_link = fields.CheckBoxField('check_link',
                                      title='Check Link',
                                      description=(
        "Check whether the link is not broken."),
                                      css_class="form-check-input",
                                      default=0)

    check_timeout = fields.FloatField('check_timeout',
                                      title='Check Timeout',
                                      description=(
        "Maximum amount of seconds to check link. Required"),
                                      css_class="form-control",
                                      default=7.0,
                                      required=1)

    link_type = fields.ListField('link_type',
                                 title='Type of Link',
                                 css_class="form-control",
                                 default="external",
                                 size=1,
                                 items=[('External Link', 'external'),
                                        ('Internal Link', 'internal'),
                                        ('Relative Link', 'relative')],
                                 description=(
        "Define the type of the link. Required."),
                                 required=1)

    message_names = StringValidator.message_names + ['not_link']

    not_link = 'The specified link is broken.'

    def validate(self, field, key, REQUEST):
        value = StringValidator.validate(self, field, key, REQUEST)
        if value == "" and not field.get_value('required'):
            return value

        link_type = field.get_value('link_type')
        if link_type == 'internal':
            value = urljoin(REQUEST['BASE0'], value)
        elif link_type == 'relative':
            value = urljoin(REQUEST['URL1'], value)
        # otherwise must be external

        # FIXME: should try regular expression to do some more checking here?

        # if we don't need to check the link, we're done now
        if not field.get_value('check_link'):
            return value

        # resolve internal links using Zope's resolve_url
        if link_type in ['internal', 'relative']:
            try:
                REQUEST.resolve_url(value)
            except:
                self.raise_error('not_link', field)

        # check whether we can open the link
        link = LinkHelper(value)
        thread = Thread(target=link.open)
        thread.start()
        thread.join(field.get_value('check_timeout'))
        del thread
        if not link.status:
            self.raise_error('not_link', field)

        return value

LinkValidatorInstance = LinkValidator()

class DateTimeValidator(Validator):
  """
    Added support for key in every call to validate_sub_field
  """
  property_names = Validator.property_names + ['required',
                                                'start_datetime',
                                                'end_datetime',
                                                'allow_empty_time']

  required = fields.CheckBoxField('required',
                                  title='Required',
                                  description=(
      "Checked if the field is required; the user has to enter something "
      "in the field."),
                                  css_class="form-check-input",
                                  default=1)

  start_datetime = fields.DateTimeField('start_datetime',
                                        title="Start datetime",
                                        description=(
      "The date and time entered must be later than or equal to "
      "this date/time. If left empty, no check is performed."),
                                        css_class="form-control",
                                        default=None,
                                        input_style="text",
                                        required=0)

  end_datetime = fields.DateTimeField('end_datetime',
                                      title="End datetime",
                                      description=(
      "The date and time entered must be earlier than "
      "this date/time. If left empty, no check is performed."),
                                      css_class="form-control",
                                      default=None,
                                      input_style="text",
                                      required=0)

  allow_empty_time = fields.CheckBoxField('allow_empty_time',
                                          title="Allow empty time",
                                          description=(
      "Allow time to be left empty. Time will default to midnight "
      "on that date."),
                                          css_class="form-check-input",
                                          default=0)

  message_names = Validator.message_names + ['required_not_found',
                                              'not_datetime',
                                              'datetime_out_of_range']

  required_not_found = 'Input is required but no input given.'
  not_datetime = 'You did not enter a valid date and time.'
  datetime_out_of_range = 'The date and time you entered were out of range.'

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
    # pass value through request in order to be restored in case if validation fail
    if getattr(REQUEST, 'form', None):
      REQUEST.form[key] = result
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

DateTimeValidatorInstance = DateTimeValidator()

class SuppressValidator(ValidatorBase):
    """A validator that is actually not used.
    """
    def need_validate(self, field, key, REQUEST):
        """Don't ever validate; suppress result in output.
        """
        return 0

SuppressValidatorInstance = SuppressValidator()


fullwidth_minus_character_list = (
    u'\u2010',
    u'\u2011',
    u'\u2012',
    u'\u2013',
    u'\u2014',
    u'\u2015',
    u'\u2212',
    u'\u30fc',
    u'\uff0d',
    )
def normalizeFullWidthNumber(value):
  try:
    if six.PY2:
      value = unicodedata.normalize('NFKD', value.decode('UTF8'))
    else:
      value = unicodedata.normalize('NFKD', value)
    if value[0] in fullwidth_minus_character_list:
      value = u'-' + value[1:]
    value = value.encode('ASCII', 'ignore')
    if six.PY3:
      value = value.decode()
  except UnicodeDecodeError:
    pass
  return value
