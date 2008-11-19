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
from Globals import get_request
from Products.ERP5OOo.Document.OOoDocument import STANDARD_IMAGE_FORMAT_LIST

from zLOG import LOG

class OOoChartWidget(Widget.Widget):
  """
  This class is capabale of producing ODF
  charts based on data obtained through a
  listbox.
  Some properties are useless
  http://books.evc-cit.info/odbook/ch08.html#chart-plot-area-example
    - mean-value
    - error-margin
    - error-upper-limit
    - error-lower-limit
    - error-category
    - error-percentage
    - chart-japanese-candle-stick and stock-with-volume,chart:stock-updown-bars. These attributs are used with a chart:stock
  """

  property_names = list(Widget.Widget.property_names)

  default = fields.StringField(
                              'default',
                              title='Default',
                              description=("A default value (not used)."),
                              default="",
                              required=0)

  listbox_form_id = fields.StringField(
                              'listbox_form_id',
                              title='ListBox Form ID',
                              description=("ID of the master form."),
                              default="",
                              required=0)
  property_names.append('listbox_form_id')

  listbox_id = fields.StringField(
                              'listbox_id',
                              title='ListBox ID',
                              description=("ID of the listbox in the master form."),
                              default="",
                              required=0)
  property_names.append('listbox_id')

  image_display = fields.ListField('image_display',
                              title='Image Display',
                              description=("Render size of this chart in HTML mode."),
                              default='medium',
                              items=[('thumbnail','thumbnail'),
                                    ('xsmall', 'xsmall'),
                                    ('small', 'small'),
                                    ('medium', 'medium'),
                                    ('large', 'large'),
                                    ('xlarge', 'xlarge'),
                                    ],
                              size=1)
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
                                            'to render the ListBox'),
                              default='ERP5Site_viewChart',
                              required=0)
  property_names.append('ooo_template')


  chart_type = fields.ListField('chart_type',
                              title='Chart Type',
                              description=('Type of the Chart'),
                              default='chart:bar',
                              items=[('bar', 'chart:bar'),
                                    ('circle', 'chart:circle'),
                                    ('line', 'chart:line'),
                                    ('scatter', 'chart:scatter'),
                                    ('area', 'chart:area'),
                                    ],
                              size=0)
  property_names.append('chart_type')


  colour_column_list = fields.ListTextAreaField('colour_column_list',
                              title="Data Color",
                              description=(
    "A list of colors for each data associated to a column."),
                              default=[],
                              required=0)
  property_names.append('colour_column_list')

  # vertical ="true"
  chart_position = fields.ListField('chart_position',
                              title='Bar Position',
                              description=(
                    'Render the bar in horizontal position or vertical position'),
                              default='false',
                              items=[('horizontal', 'true'),
                                    ('vertical', 'false'),
                                    ],
                              size=0)
  property_names.append('chart_position')

  #legend of the chart or not
  chart_legend = fields.CheckBoxField('chart_legend',
                              title='Chart Legend',
                              description=('Show Chart Legend or no'),
                              default=1,
                              required=0)
  property_names.append('chart_legend')


  position_legend = fields.ListField('position_legend',
                              title='Legend Position',
                              description=(
                              'Legend Position according to the graph'),
                              default='end',
                              items=[('bottom', 'bottom'),
                                    ('end', 'end'),
                                    ('start', 'start'),
                                    ('top', 'top'),
                                    ],
                              size=1)
  property_names.append('position_legend')

  #legend of the chart or not
  chart_title_or_no = fields.CheckBoxField('chart_title_or_no',
                              title='Chart Title ',
                              description=('Show Title on Graph or no '),
                              default=1,
                              required=0)
  property_names.append('chart_title_or_no')

  #grid or not
  grid_graph = fields.CheckBoxField('grid_graph',
                              title='Chart Grid ',
                              description=('Show Grid or no'),
                              default=1,
                              required=0)
  property_names.append('grid_graph')


  grid_size = fields.ListField('grid_size',
                              title='Grid Size',
                              description=(
                              'Render a big grid size or a small grid size'),
                              default='major',
                              items=[('major', 'major'),
                                    ('minor', 'minor'),
                                    ],
                              size=0)
  property_names.append('grid_size')

  user_data_title = fields.StringField('user_data_title',
                              title="Overide Labelled Column ID",
                              description=(
    "Column Id choose by user to define the label."),
                              required=0)
  property_names.append('user_data_title')

  user_column_id_list = fields.ListTextAreaField('user_column_id_list',
                              title="Overide Column Ids",
                              description=(
    "A list of column Ids choose by user to draw the graph."),
                              default=[],
                              required=0)
  property_names.append('user_column_id_list')


  chart_stacked = fields.CheckBoxField('chart_stacked',
                              title='Stacked Data',
                              description=('stacked data or not'),
                              default=0,
                              required=0)
  property_names.append('chart_stacked')

  #connect-bars="false"
  connect_bars = fields.CheckBoxField('connect_bars',
                              title='Connect Bars',
                              description=(''),
                              default=0,
                              required=0)
  property_names.append('connect_bars')


  chart_three_dimensional = fields.CheckBoxField('chart_three_dimensional',
                              title='3D',
                              description=(
                      'Render the chart in three dimensions rather in flat mode'),
                              default=0,
                              required=0)
  property_names.append('chart_three_dimensional')

  #deep="false"
  deep = fields.CheckBoxField('deep',
                              title='Deep',
                              description=('Deep'),
                              default=0,
                              required=0)
  property_names.append('deep')

  # sector_pie_offset Default:0
  sector_pie_offset = fields.IntegerField('sector_pie_offset',
                              title='Sector Pie Offset',
                              description=(''),
                              default=0,
                              required=0)
  property_names.append('sector_pie_offset')
  


  #interpolation="none", cubic-spline, b-spline
  interpolation = fields.ListField('interpolation',
                              title='Interpolation',
                              description=(''),
                              default='none',
                              items=[('none', 'none'),
                                    ('cubic-spline', 'cubic-spline'),
                                    ('b-spline', 'b-spline')],
                              size=1)
  property_names.append('interpolation')

  #symbol-type="none", automatic
  symbol_type = fields.ListField('symbol_type',
                              title='Symbol Type',
                              description=(''),
                              default='none',
                              items=[('none', 'none'),
                                    ('automatic', 'automatic'),],
                              size=1)
  property_names.append('symbol_type')

  #lines-used="0" 
  lines_used = fields.ListField('lines_used',
                              title='Lines Used',
                              description=(''),
                              default='0',
                              items=[('0', '0'),
                                      ('1', '1')],
                              size=1)
  property_names.append('lines_used')


  #series-source=columns or rows
  series_source = fields.ListField('series_source',
                              title='Series Source',
                              description=(''),
                              default='columns',
                              items=[('columns', 'columns'),
                                    ('rows', 'rows'),],
                              size=1)
  property_names.append('series_source')

  #regression-type="none" linear logarithmic exponential power
  regression_type = fields.ListField('regression_type',
                              title='Regression Type',
                              description=(''),
                              default='none',
                              items=[('none', 'none'),
                                    ('linear', 'linear'),
                                    ('logarithmic', 'logarithmic'),
                                    ('exponential', 'exponential'),
                                    ('power', 'power')],
                              size=1)
  property_names.append('regression_type')

  #data-label-number="none" value percentage
  data_label_number = fields.ListField('data_label_number',
                              title='Data Label Number',
                              description=(''),
                              default='none',
                              items=[('none', 'none'),
                                    ('value', 'value'),
                                    ('percentage', 'percentage')],
                              size=1)
  property_names.append('data_label_number')

  #data-label-text="false"
  data_label_text = fields.CheckBoxField('data_label_text',
                              title='Data Label Text',
                              description=(''),
                              default=0,
                              required=0)
  property_names.append('data_label_text')

  #data-label-symbol="false"
  data_label_symbol = fields.CheckBoxField('data_label_symbol',
                              title='Data Label Symbol',
                              description=(''),
                              default=0,
                              required=0)
  property_names.append('data_label_symbol')


  def getArgumentDict(self, field, REQUEST):
    """ Build argument Dict """
    def stringBoolean(value):
      return str(bool(value)).lower()
    form = field.aq_parent
    listbox_form_id = field.get_value('listbox_form_id')
    if listbox_form_id in ('', None):
      listbox_form_id = form.getId()
    listbox_id = field.get_value('listbox_id')
    if listbox_id in ('', None):
      listbox_id = 'listbox'
    render_prefix = REQUEST.get('render_prefix')
    extra_argument_dict = dict(
      render_prefix = render_prefix,
      chart_form_id = listbox_form_id,
      chart_field_id = listbox_id,
      chart_title = field.get_value('title'),
      chart_type = field.get_value('chart_type'),
      colour_column_list = field.get_value('colour_column_list'),
      user_column_id_list = field.get_value('user_column_id_list'),
      user_data_title= field.get_value('user_data_title'),
      chart_position = field.get_value('chart_position'),
      chart_legend = stringBoolean(field.get_value('chart_legend')),
      chart_title_or_no = stringBoolean(field.get_value('chart_title_or_no')),
      grid_graph = stringBoolean(field.get_value('grid_graph')),
      grid_size=field.get_value('grid_size'),
      chart_three_dimensional = stringBoolean(field.get_value('chart_three_dimensional')),
      deep = stringBoolean(field.get_value('deep')),
      chart_stacked = stringBoolean(field.get_value('chart_stacked')),
      sector_pie_offset = field.get_value('sector_pie_offset'),
      interpolation = field.get_value('interpolation'),
      symbol_type = field.get_value('symbol_type'),
      lines_used = field.get_value('lines_used'),
      connect_bars = stringBoolean(field.get_value('connect_bars')),
      series_source = field.get_value('series_source'),
      regression_type = field.get_value('regression_type'),
      data_label_number = field.get_value('data_label_number'),
      data_label_text = stringBoolean(field.get_value('data_label_text')),
      data_label_symbol = stringBoolean(field.get_value('data_label_symbol')),
      position_legend=field.get_value('position_legend'),
    )

    for k, v in extra_argument_dict.items():
      if REQUEST.get(k) is None:
        REQUEST.form[k] = v
    return extra_argument_dict


  def render_view(self, field, value, REQUEST=None, key=None, render_format='html', render_prefix=None):
    """
      Render a Chart in read-only.
    """
    if REQUEST is None: REQUEST=get_request()
    return self.render(field, key, value, REQUEST, render_format=render_format,
                       render_prefix=render_prefix)


  def render_odf(self, field, key, value, REQUEST, render_format='ooo', render_prefix=None):
    """
      Render a Chart for ODT Style.
    """
    form = field.aq_parent
    here = getattr(form, 'aq_parent', REQUEST)
    content = '''
                  <office:include path="%s/ERP5Site_buildChart" xlink:type="simple" xlink:actuate="onLoad" xlink:show="embed"/>
                  ''' % here.getPath()
    return content


  def render(self, field, key, value, REQUEST, render_format='html', render_prefix=None):

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
    alt = field.get_value('description') or title
    form = field.aq_parent

    # Find the applicable context
    here = getattr(form, 'aq_parent', REQUEST)
    # Update the render format based on REQUEST parameters
    render_format = getattr(REQUEST, 'render_format', render_format)
    if render_format == 'html':
      field_absolute_url = '%s/%s/%s' % (here.absolute_url(),
                                         form.getId(),
                                         field.getId())
      css_class = field.get_value('css_class')
      format = field.get_value('image_format') or 'png'
      display = field.get_value('image_display')
      if format in STANDARD_IMAGE_FORMAT_LIST:
        main_content = '''<div class="OOoChartContent">
          <img class="%s" src="%s?render_format=%s&display=%s&render_prefix=%s" title="%s" alt="%s"/">
          </div>''' % (css_class,
                       field_absolute_url,
                       format,
                       display,
                       render_prefix,
                       title,
                       alt)
        return main_content
      elif format == 'raw':
        UrlIconOOo = '%s/misc_/ERP5OOo/OOo.png' % REQUEST['BASEPATH1']
        main_content = '''<div class="OOoChartContent">
          <a href="%s?render_format=&display=%s&render_prefix=%s"><img src="%s" alt="OOo"/></a></div>
          ''' % (field_absolute_url,
                 display,
                 render_prefix,
                 UrlIconOOo)
        return main_content
      elif format == 'pdf':
        UrlIconPdf = '%s/misc_/ERP5Form/PDF.png' % REQUEST['BASEPATH1']
        main_content = '''<div class="OOoChartContent">
          <a href="%s?render_format=pdf&display=%s"><img src="%s" alt="PDF" /></a>
          </div>''' % (field_absolute_url,
                       display,
                       render_prefix,
                       UrlIconPdf)
        return main_content
      else:
        raise NotImplementedError, 'Format: %s not handled' % format

    extra_context = self.getArgumentDict(field, REQUEST)

    method_id = field.get_value('ooo_template')

    # Find the page template
    ooo_template = getattr(here, method_id)

    # Render the chart
    return ooo_template(format=render_format, **extra_context)

class OOoChartValidator(Validator.Validator):
  """
  """
  property_names = Validator.Validator.property_names

  def validate(self, key,field,  REQUEST):

    return {}

OOoChartWidgetInstance = OOoChartWidget()
OOoChartValidatorInstance = OOoChartValidator()

class OOoChart(ZMIField):
    meta_type = "OOoChart"
    widget = OOoChartWidgetInstance
    validator = OOoChartValidatorInstance
