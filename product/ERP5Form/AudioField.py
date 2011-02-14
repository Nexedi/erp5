from Products.Formulator.Field import ZMIField
from Products.Formulator import Widget
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
              'audio_preload', 'audio_autoplay', 'js_enabled', 'audio_player']

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

  js_enabled = fields.CheckBoxField('js_enabled',
      title='Enable on the fly video player change (based on java script)',
      description='Define if javascript is enabled or not on the current Video',
      default=1,
      required=1)

  audio_player = fields.ListField('audio_player',
                                 title='Audio Player',
                                 description=(
      "The video player to be used to show video."),
                                 default="html5_audio",
                                 required=1,
                                 size=1,
                                 items=[('HTML5 Audio', 'html5_audio'),
                                        ('Flowplayer', 'flowplayer'),])

  def render(self, field, key, value, REQUEST, render_prefix=None):
    return self.render_view(field, value, REQUEST, render_prefix)

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    if value is None:
      return ''
    audio_player = field.get_value('audio_player')
    if audio_player == 'html5_audio':
      return Widget.render_element("audio",
                              src=value,
                              extra=field.get_value('extra'),
                              controls=field.get_value('audio_controls'),
                              loop=field.get_value('audio_loop'),
                              preload=field.get_value('audio_preload'),
                              autoplay=field.get_value('audio_autoplay'),
                              contents=field.get_value('audio_error_message'))
    elif audio_player == 'flowplayer':
      a_element = Widget.render_element("a",
                        href="%s" % value,
                        style="display:block;width:%spx;height:%spx;" % \
                                        (field.get_value('video_width'),
                                         field.get_value('video_height'),),
                        id="player")

      script_element = """<script language="JavaScript">
                             flowplayer("player", "%s/flowplayer.swf");
                         </script>""" % self.getContext(field, REQUEST).getPortalObject().portal_url()
      return ' '.join([a_element,script_element])


  def get_javascript_list(self, field, REQUEST=None):
    """
    Returns list of javascript needed by the widget
    """
    if field.get_value('js_enabled'):
      audio_player = field.get_value('audio_player')
      context = self.getContext(field, REQUEST)
      if audio_player == 'html5_audio':
        # XXX Instead of harcoding library name
        # it should be better to call a python script, as
        # it is done on type base method.
        return ['%s/html5media.min.js' % context.portal_url()]
      elif audio_player == 'flowplayer':
        return ['%s/flowplayer.min.js' % context.portal_url()]
    else:
      return []

  def getContext(self, field, REQUEST):
    """Return the context of rendering this Field.
    """
    value = REQUEST.get('here')
    if value is None:
      value = self.getForm(field).aq_parent
    return value


  def getForm(self, field):
    """Return the form which contains the Field.
    """
    return field.aq_parent

AudioWidgetInstance = AudioWidget()

class AudioField(ZMIField):
  """ Audio field
  """
  meta_type = "AudioField"

  widget = AudioWidgetInstance
  validator = Validator.SuppressValidatorInstance
