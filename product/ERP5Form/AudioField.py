from Products.Formulator.Field import ZMIField
from Products.Formulator import Widget, Validator
from Products.Formulator.DummyField import fields
from Products.Formulator import Validator

class AudioWidget(Widget.TextWidget):
    """
    A widget that displays a Audio HTML element.
    This widget is intended to be used in
    conjunction with WebSite.
    """
    property_names = Widget.TextWidget.property_names + \
            ['audio_controls', 'audio_error_message', 'audio_loop', \
                'audio_preload', 'audio_autoplay']

    audio_controls = fields.StringField('audio_controls',
                           title='Audio Controls',
                           description=("Controls to be used in Audio Player."),
                           default='controls',
                           required=0)

    audio_error_message = fields.StringField('audio_error_message',
                           title='Audio Error Message',
                           description=("Error message to be showed when \
            user's browser does not support the audio tag."),
                           default='Your browser does not support audio tag.',
                           required=0)

    audio_loop = fields.StringField('audio_loop',
                           title='Audio Loop',
                           description=("Specifies that the audio file \
            will start over again, every time it is finished."),
                           default='none',
                           required=0)

    audio_preload = fields.StringField('audio_preload',
                           title='Audio Preload',
                           description=("Configure that you would like to \
        start downloading the audio file as soon as possible."),
                           default='preload',
                           required=0)

    audio_autoplay = fields.StringField('audio_autoplay',
                           title='Audio Autoplay',
                           description=("Configure that you would like to \
        start downloading and playing the audio file as soon as possible."),
                           default='',
                           required=0)

    def render(self, field, key, value, REQUEST, render_prefix=None):
        return self.render_view(field, value, REQUEST, render_prefix)

    def render_view(self, field, value, REQUEST=None, render_prefix=None):
        if value is None:
            return ''
        return Widget.render_element("audio",
                              src=value,
                              controls=field.get_value('audio_controls'),
                              loop=field.get_value('audio_loop'),
                              preload=field.get_value('audio_preload'),
                              autoplay=field.get_value('audio_autoplay'),
                              contents=field.get_value('audio_error_message'))

AudioWidgetInstance = AudioWidget()

class AudioField(ZMIField):
    """ Audio field
    """
    meta_type = "AudioField"

    widget = AudioWidgetInstance
    validator = Validator.SuppressValidatorInstance

