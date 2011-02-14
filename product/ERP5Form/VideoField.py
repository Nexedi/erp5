from Products.Formulator.Field import ZMIField
from Products.Formulator import Widget, Validator
from Products.Formulator.DummyField import fields
from Products.Formulator import Validator

class VideoWidget(Widget.TextWidget):
    """
    A widget that displays a Video HTML element.
    This widget is intended to be used in
    conjunction with WebSite.
    """
    property_names = Widget.TextWidget.property_names + \
            ['video_controls', 'video_error_message', 'video_loop', \
                'video_width', 'video_height', 'video_preload', \
                'video_autoplay']

    video_controls = fields.StringField('video_controls',
                           title='Video Controls',
                           description=("Controls to be used in Video Player."),
                           default='controls',
                           required=0)

    video_error_message = fields.StringField('video_error_message',
                           title='Video Error Message',
                           description=("Error message to be showed when \
            user's browser does not support the video tag."),
                           default='Your browser does not support video tag.',
                           required=0)

    video_loop = fields.StringField('video_loop',
                           title='Video Loop',
                           description=("Specifies that the video file \
            will start over again, every time it is finished."),
                           default='none',
                           required=0)

    video_width = fields.IntegerField('video_width',
                               title='Video Width',
                               description=(
        "The width to be used when playing the video."),
                               default=160,
                               required=0)

    video_height = fields.IntegerField('video_height',
                               title='Video Height',
                               description=(
        "The height to be used when playing the video."),
                               default=85,
                               required=0)

    video_preload = fields.StringField('video_preload',
                           title='Video Preload',
                           description=("Configure that you would like to \
        start downloading the video file as soon as possible."),
                           default='preload',
                           required=0)

    video_autoplay = fields.StringField('video_autoplay',
                           title='Video Autoplay',
                           description=("Configure that you would like to \
        start downloading and playing the video file as soon as possible."),
                           default='',
                           required=0)

    def render(self, field, key, value, REQUEST, render_prefix=None):
        return self.render_view(field, value, REQUEST, render_prefix)

    def render_view(self, field, value, REQUEST=None, render_prefix=None):
        if value is None:
            return ''
        return Widget.render_element("video",
                              src=value,
                              extra=field.get_value('extra'),
                              controls=field.get_value('video_controls'),
                              loop=field.get_value('video_loop'),
                              width=field.get_value('video_width'),
                              height=field.get_value('video_height'),
                              preload=field.get_value('video_preload'),
                              autoplay=field.get_value('video_autoplay'),
                              contents=field.get_value('video_error_message'))

VideoWidgetInstance = VideoWidget()

class VideoField(ZMIField):
    """ Video field
    """
    meta_type = "VideoField"

    widget = VideoWidgetInstance
    validator = Validator.SuppressValidatorInstance

