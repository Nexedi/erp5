from Form import BasicForm
from Field import ZMIField
from DummyField import fields
from MethodField import BoundMethod
from DateTime import DateTime
import Validator, Widget
import OFS

class StringField(ZMIField):
  meta_type = "StringField"

  widget = Widget.TextWidgetInstance
  validator = Validator.StringValidatorInstance

class PasswordField(ZMIField):
  meta_type = "PasswordField"

  widget = Widget.PasswordWidgetInstance
  validator = Validator.StringValidatorInstance

class EmailField(ZMIField):
  meta_type = "EmailField"

  widget = Widget.TextWidgetInstance
  validator = Validator.EmailValidatorInstance

class PatternField(ZMIField):
  meta_type = "PatternField"

  widget = Widget.TextWidgetInstance
  validator = Validator.PatternValidatorInstance

class CheckBoxField(ZMIField):
  meta_type = "CheckBoxField"

  widget = Widget.CheckBoxWidgetInstance
  validator = Validator.BooleanValidatorInstance

class IntegerField(ZMIField):
  meta_type = "IntegerField"

  widget = Widget.IntegerWidgetInstance
  validator = Validator.IntegerValidatorInstance

class RangedIntegerField(ZMIField):
  meta_type = "RangedIntegerField"

  # this field is not addable anymore and deprecated. For
  # backwards compatibility it's a clone of IntegerField,
  # though it may go away in the future.
  internal_field = 1

  widget = Widget.TextWidgetInstance
  validator = Validator.IntegerValidatorInstance

class FloatField(ZMIField):
  meta_type = "FloatField"

  widget = Widget.FloatWidgetInstance
  validator = Validator.FloatValidatorInstance

class TextAreaField(ZMIField):
  meta_type = "TextAreaField"

  widget = Widget.TextAreaWidgetInstance
  validator = Validator.TextValidatorInstance

class RawTextAreaField(ZMIField):
  meta_type = "RawTextAreaField"

  widget = Widget.TextAreaWidgetInstance
  validator = Validator.StringValidatorInstance

class ListField(ZMIField):
  meta_type = "ListField"

  widget = Widget.ListWidgetInstance
  validator = Validator.SelectionValidatorInstance

class MultiListField(ZMIField):
  meta_type = "MultiListField"

  widget = Widget.MultiListWidgetInstance
  validator = Validator.MultiSelectionValidatorInstance

class LinesField(ZMIField):
  meta_type = "LinesField"

  widget = Widget.LinesTextAreaWidgetInstance
  validator = Validator.LinesValidatorInstance

class RadioField(ZMIField):
  meta_type = "RadioField"

  widget = Widget.RadioWidgetInstance
  validator = Validator.SelectionValidatorInstance

class MultiCheckBoxField(ZMIField):
  meta_type = "MultiCheckBoxField"

  widget = Widget.MultiCheckBoxWidgetInstance
  validator = Validator.MultiSelectionValidatorInstance

class FileField(ZMIField):
  meta_type = "FileField"

  widget = Widget.FileWidgetInstance
  validator = Validator.FileValidatorInstance

class LinkField(ZMIField):
  meta_type = "LinkField"

  widget = Widget.LinkWidgetInstance
  validator = Validator.LinkValidatorInstance

class LabelField(ZMIField):
  """Just a label, doesn't really validate.
  """
  meta_type = "LabelField"

  widget = Widget.LabelWidgetInstance
  validator = Validator.SuppressValidatorInstance

class DateTimeField(ZMIField):
  meta_type = "DateTimeField"

  widget = Widget.DateTimeWidgetInstance
  validator = Validator.DateTimeValidatorInstance

  def _get_user_input_value(self, key, REQUEST):
    """
    Try to get a value of the field from the REQUEST
    """
    if REQUEST.form['subfield_%s_%s' % (key, 'year')]:
      return None