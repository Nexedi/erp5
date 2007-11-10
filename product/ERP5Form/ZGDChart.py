##############################################################################
#
# Copyright (c) 2003 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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

class ZGDChartWidget(Widget.Widget):
  """
  This is the class used in order to include inside
  ERP5 some very nice charts
  """
  property_names = Widget.Widget.property_names +\
                   ['selection_name','default_params','chart_title',
                   'data_method','chart_style','x_title','y_title',
                   'bg_transparent']

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

  def render(self, field, key, value, REQUEST):

    """
    This is where most things happens
    """
    main_content = ""
    here = REQUEST['here']
    selection_name = field.get_value('selection_name')
    default_params = field.get_value('default_params')
    chart_title = field.get_value('chart_title')
    data_method = field.get_value('data_method')
    chart_style = field.get_value('chart_style')
    x_title = field.get_value('x_title')
    y_title = field.get_value('y_title')
    bg_transparent = field.get_value('bg_transparent')

    selection = here.portal_selections.getSelectionFor(selection_name, REQUEST=REQUEST)
    LOG('ZGDChart.render',0,'selection: %s, selection_name: %s' % (str(selection),
                                                                   str(selection_name)))

    # This is the default data, this is just in the case there is not method given
    data = {'chart_data':[]}

    # Retrieve the data with the data_method
    if hasattr(here,data_method):
      LOG('ZGDChart.render',0,'found method')
      data_method = getattr(here,data_method)
      data['chart_data'] = data_method()

    data['chart_parameter'] = {'zgdchart_runtime_title':chart_title,
                               'zgdchart_runtime_xtitle':x_title,
                               'zgdchart_runtime_ytitle':y_title,
                               'zgdchart_runtime_type':'Line_3D',
                               'zgdchart_runtime_bg_transparent':bg_transparent}

    # Creation selection if needed
    if selection is None:
      selection = Selection(params=data)
    else:
      LOG('ZGDChart.render',0,'selection is not None')
      kw = {'params':data}
      selection.edit(**kw)

    here.portal_selections.setSelectionFor(selection_name, selection, REQUEST=REQUEST)

    if len(data['chart_data']) > 0:


      main_content = """\
<div class="ChartContent">
 <table border="0" cellpadding="0" cellspacing="0"">
  <tr>
   <td valign="middle" align="center" nowrap>
    <img src="%s" title="Chart" border="0" alt="img"/">
   </td>
  </tr>
 </table>
</div>""" % str(chart_style + '?selection_name=' + selection_name)

    return main_content

ZGDChartWidgetInstance = ZGDChartWidget()

class ZGDChartValidator(Validator.Validator):
  property_names = Validator.Validator.property_names

  def validate(self, field, key, REQUEST):
    result = {}
    return result

ZGDChartValidatorInstance = ZGDChartValidator()

class ZGDChart(ZMIField):
    meta_type = "ZGDChart"

    widget = ZGDChartWidgetInstance
    validator = ZGDChartValidatorInstance

