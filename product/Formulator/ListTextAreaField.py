import string
from DummyField import fields
import Widget, Validator
from Field import ZMIField

class ListTextAreaWidget(Widget.TextAreaWidget):
    default = fields.ListTextAreaField('default',
                                       title='Default',
                                       default=[],
                                       required=0)

    def render(self, field, key, value, REQUEST, render_prefix=None):
        if value is None:
            value = field.get_value('default')
        lines = []
        for element_text, element_value in value:
            lines.append("%s | %s" % (element_text, element_value))
        return Widget.TextAreaWidget.render(self, field, key,
                                            string.join(lines, '\n'),
                                            REQUEST)

ListTextAreaWidgetInstance = ListTextAreaWidget()

class ListLinesValidator(Validator.LinesValidator):
    """A validator that can deal with lines that have a | separator
    in them to split between text and value of list items.
    """
    def validate(self, field, key, REQUEST):
        value = Validator.LinesValidator.validate(self, field, key, REQUEST)
        result = []
        for line in value:
            elements = string.split(line, "|")
            if len(elements) >= 2:
                text, value = elements[:2]
            else:
                text = line
                value = line
            text = string.strip(text)
            value = string.strip(value)
            result.append((text, value))
        return result

ListLinesValidatorInstance = ListLinesValidator()

class ListTextAreaField(ZMIField):
    meta_type = "ListTextAreaField"

    # field only has internal use
    internal_field = 1

    widget = ListTextAreaWidgetInstance
    validator = ListLinesValidatorInstance
    



