from Products.Formulator.Field import ZMIField
from Products.Formulator import Widget
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
              'video_autoplay', 'js_enabled', 'video_player']

  video_controls = fields.CheckBoxField('video_controls',
                         title='Video Controls',
                         description=("Controls to be used in Video Player."),
                         default=1,
                         required=0)

  video_error_message = fields.StringField('video_error_message',
                         title='Video Error Message',
                         description=("Error message to be showed when \
          user's browser does not support the video tag."),
                         default='Your browser does not support video tag.',
                         required=0)

  video_loop = fields.CheckBoxField('video_loop',
                         title='Video Loop',
                         description=("Specifies that the video file \
          will start over again, every time it is finished."),
                         default=0,
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

  video_preload = fields.CheckBoxField('video_preload',
                         title='Video Preload',
                         description=("Configure that you would like to \
      start downloading the video file as soon as possible."),
                         default=1,
                         required=0)

  video_autoplay = fields.CheckBoxField('video_autoplay',
                         title='Video Autoplay',
                         description=("Configure that you would like to \
      start downloading and playing the video file as soon as possible."),
                         default=0,
                         required=0)

  js_enabled = fields.CheckBoxField('js_enabled',
      title='Enable on the fly video player change (based on java script)',
      description='Define if javascript is enabled or not on the current Video',
      default=1,
      required=0)

  video_player = fields.ListField('video_player',
                                 title='Video Player',
                                 description=(
      "The video player to be used to show video."),
                                 default="html5_video",
                                 required=1,
                                 size=1,
                                 items=[('HTML5 Video', 'html5_video'),
                                        ('Flowplayer', 'flowplayer'),])

  def render(self, field, key, value, REQUEST, render_prefix=None):
      return self.render_view(field, value, REQUEST, render_prefix)

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    if value is None:
      return ''
    video_player = field.get_value('video_player')
    if video_player == 'html5_video':
      extra_kw = {}
      if field.get_value('video_autoplay'):
        extra_kw['autoplay']='autoplay'
      if field.get_value('video_controls'):
        extra_kw['controls']='controls'
      if field.get_value('video_loop'):
        extra_kw['loop']='loop'
      if field.get_value('video_preload'):
        extra_kw['preload']='auto'
      return Widget.render_element("video",
                        src=value,
                        extra=field.get_value('extra'),
                        width=field.get_value('video_width'),
                        height=field.get_value('video_height'),
                        contents=field.get_value('video_error_message'),
                        **extra_kw)
    elif video_player == 'flowplayer':
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
      video_player = field.get_value('video_player')
      context = self.getContext(field, REQUEST)
      if video_player == 'html5_video':
        # XXX Instead of harcoding library name
        # it should be better to call a python script, as
        # it is done on type base method.
        return ['%s/html5media.min.js' % context.portal_url()]
      elif video_player == 'flowplayer':
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


VideoWidgetInstance = VideoWidget()

class VideoField(ZMIField):
    """ Video field
    """
    meta_type = "VideoField"

    widget = VideoWidgetInstance
    validator = Validator.SuppressValidatorInstance

