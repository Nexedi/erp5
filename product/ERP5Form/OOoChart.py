##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets <jp@nexedi.com>
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

from Products.Formulator import Widget
from Products.Formulator import Widget, Validator
from Products.Formulator.DummyField import fields
from Products.Formulator.Field import ZMIField
from Selection import Selection

from zLOG import LOG

# XXX This should be move to preferences - just as for image
defaultdisplays = {'thumbnail' : (128,128),
                   'xsmall'    : (200,200),
                   'small'     : (320,320),
                   'medium'    : (480,480),
                   'large'     : (768,768),
                   'xlarge'    : (1024,1024)
                  }

class OOoChartWidget(Widget.Widget):
  """
  This class is capabale of producing ODF
  charts based on data obtained through a
  listbox.
  """
  property_names = list(Widget.Widget.property_names)

  # Default has no meaning in OOoChart.
  property_names.remove('default')

  form_id = fields.StringField(
                                'form_id',
                                title='Form ID',
                                description= \
                                  "ID of the master form.",
                                default="",
                                required=1)
  property_names.append('form_id')

  field_id = fields.StringField(
                                'field_id',
                                title='Field ID',
                                description= \
                                  "ID of the listbox in the master form.",
                                default="",
                                required=1)
  property_names.append('field_id')

  image_display = fields.StringField('image_display',
                              title='Image Display',
                              description=(
           "Render size of this chart in HTML mode."),
                              default='large',
                              required=1)
  property_names.append('image_display')

  image_format = fields.StringField('image_format',
                              title='Image Format',
                              description=(
      "The format in which the chart should be converted to."),
                              default='png',
                              required=0)
  property_names.append('image_format')

  ooo_template = fields.StringField('ooo_template',
                                title='OOo Template',
                                description=('The ID of a OOo Page Template'
                                            ' to render the ListBox'),
                                default='',
                                required=0)
  property_names.append('ooo_template')

  colour_column_list = fields.ListTextAreaField('colour_column_list',
                                title="Data Colour",
                                description=(
      "A list of colours for each data associated to a column."),
                                default=[],
                                required=1)
  property_names.append('colour_column_list')

  chart_japanese_candle_stick = fields.CheckBoxField('chart_japanese_candle_stick',
                              title='Japanese Candle Stick',
                              description=('XXX Unknown'),
                              default=0,
                              required=0)
  property_names.append('chart_japanese_candle_stick')


  chart_three_dimensional = fields.CheckBoxField('chart_three_dimensional',
                              title='3D',
                              description=('Render the chart in three dimensions rather in flat mode'),
                              default=0,
                              required=0)
  property_names.append('chart_three_dimensional')


#"""
#chart:japanese-candle-stick="false" chart:stock-with-volume="false" chart:three-dimensional="false" chart:deep="false" chart:lines="false" chart:interpolation="none" chart:symbol-type="none" chart:vertical="true" chart:lines-used="0" chart:connect-bars="false" chart:series-source="columns" chart:mean-value="false" chart:error-margin="0" chart:error-lower-limit="0" chart:error-upper-limit="0" chart:error-category="none" chart:error-percentage="0" chart:regression-type="none" chart:data-label-number="none" chart:data-label-text="false" chart:data-label-symbol="false"/>
#"""

  default = fields.TextAreaField('default',
                                title='Default',
                                description=(
      "Default value of the text in the widget."),
                                default="",
                                width=20, height=3,
                                required=0)

  selection_name = fields.StringField('selection_name',
                              title='Selection Name',
                              description=('The name of the selection to store'
                                            'params of selection'),
                              default='',
                              required=0)

  data_method = fields.StringField('data_method',
                              title='Data Method',
                              description=('The method wich returns data'),
                              default='',
                              required=0)

  chart_style = fields.StringField('chart_style',
                              title='Chart Style',
                              description=('The kind of Chart we want'),
                              default='bar_3d',
                              required=0)

  chart_title = fields.StringField('chart_title',
                              title='Chart Title',
                              description=('The Title on the top of the chart'),
                              default='',
                              required=0)

  x_title = fields.StringField('x_title',
                              title='X Title',
                              description=('The Title for the X axis'),
                              default='',
                              required=0)

  y_title = fields.StringField('y_title',
                              title='Y Title',
                              description=('The Title for the Y axis'),
                              default='',
                              required=0)

  default_params = fields.ListTextAreaField('default_params',
                              title="Default Parameters",
                              description=(
      "Default Parameters for the List Method."),
                              default=[],
                              required=0)

  bg_transparent = fields.CheckBoxField('bg_transparent',
                              title='Transparent Background',
                              description=('Allows to set the background transparent'),
                              default='',
                              required=0)

  def render_view(self, field, value, REQUEST=None, render_format='html'):
    """
      Render a Chart in read-only.
    """
    if REQUEST is None: REQUEST=get_request()
    return self.render(field, key, value, REQUEST, render_format=render_format)

  def render(self, field, key, value, REQUEST, render_format='html'):

    """
      Render a chart.

      render_format   -- If the format is set to html, render the chart
                         as a URL to ourselves with a png render_format

                         If the format is set to 'raw', render the chart
                         as raw XML.

                         If the format is set to an image type (ex. png)
                         render the chart using that format.
    """
    title = field.get_value('title')

    # Update the render format based on REQUEST parameters
    render_format = getattr(REQUEST, 'render_format', render_format)
    if render_format == 'html':
      css_class = field.get_value('css_class')
      format = field.get_value('image_format')
      display = field.get_value('image_display')
      alternate_name = field.get_value('alternate_name')
      main_content = """\
<div class="OOoChartContent">
  <img class="%s" src="%s?render_format=%s&display=%s" title="%s" alt="%s"/">
</div>""" % (css_class, field.absolute_url(), format, display, title, alternate_name)
      return main_content

    # Find the applicable context
    form = field.aq_parent
    here = getattr(form, 'aq_parent', REQUEST)

    def stringBoolean(value):
      return str(bool(value)).lower()

    # Build the parameters
    extra_argument_dict = dict(
      chart_title = field.get_value('title'),
      colour_column_dict = dict(field.get_value('colour_column_list')),
      chart_three_dimensional = stringBoolean(field.get_value('chart_three_dimensional')),
      chart_japanese_candle_stick = stringBoolean(field.get_value('chart_japanese_candle_stick')),
    )
    LOG('extra_argument_dict', 0, repr(extra_argument_dict))
    for k, v in extra_argument_dict.items():
      if REQUEST.get(k) is None:
        REQUEST.form[k] = v

    # Find the page template
    method_id = field.get_value('ooo_template')
    ooo_template = getattr(here, method_id)

    # Render the chart
    if render_format == 'raw':
      return ooo_template()
    return ooo_template(format=render_format)

OOoChartWidgetInstance = OOoChartWidget()

class OOoChartValidator(Validator.Validator):
  property_names = Validator.Validator.property_names

  def validate(self, field, key, REQUEST):
    result = {}
    return result

OOoChartValidatorInstance = OOoChartValidator()

class OOoChart(ZMIField):
    meta_type = "OOoChart"

    widget = OOoChartWidgetInstance
    validator = OOoChartValidatorInstance

