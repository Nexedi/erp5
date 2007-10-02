##############################################################################
#
# Copyright (c) 2003-2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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

from Products.PythonScripts.PythonScript import PythonScript
try:
  import pychart
except ImportError:
  pychart = None

from zLOG import LOG

class ZPyChartWidget(Widget.Widget):
  """
    A widget to generate pychart charts in multiple formats
    
    Chart definition is defined in a script. Some parameters
    are defined through Web UI. Web UI parameters are intended
    to be specialised through Proxy fields.
  """
  property_names = Widget.Widget.property_names+\
                   [ 'selection_name',
                     'data_method',
                     'chart_title',
                     'x_title',
                     'y_title',]

  default = fields.StringField('default',
                                title='Default',
                                description=(
      "Default value of the text in the widget."),
                                default="",
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

  def render(self, field, key, value, REQUEST):
    """
      Here, we just generate tags which will later call download
    """
    # Get standard parameters
    selection_name = field.get_value('selection_name')
    chart_title = field.get_value('chart_title')
    data_method = field.get_value('data_method')
    x_title = field.get_value('x_title')
    y_title = field.get_value('y_title')

    # Retrieve the data and set the selection if data_method is not None
    if data_method:
      here = REQUEST.get('here', self)
      if getattr(here, data_method, None) is not None:
        data_method = getattr(here, data_method)
        # Retrieve selection
        selection = here.portal_selections.getSelectionFor(selection_name, REQUEST=REQUEST)
        # Define the new selection data_method
        selection.edit(method_id = data_method) # XXX This is probably wrong

    # Return an image field
    return """<img src="%s/download?selection_name=%s&chart_title=%s&data_method=%s&x_title=%s&y_title=%s"/>""" % (field.absolute_url(), selection_name, chart_title, data_method, x_title, y_title)

ZPyChartWidgetInstance = ZPyChartWidget()

class ZPyChartValidator(Validator.Validator):
  property_names = Validator.Validator.property_names

  def validate(self, field, key, REQUEST):
    result = {}
    return result

ZPyChartValidatorInstance = ZPyChartValidator()

class ZPyChart(ZMIField, PythonScript):
    """
      A hybrid between a field and a script

      TODO:
        - implement XML I/O of script
        - make tabs nicer
    """
    
    meta_type = "ZPyChart"

    manage_options = ZMIField.manage_options + PythonScript.manage_options

    widget = ZPyChartWidgetInstance
    validator = ZPyChartValidatorInstance

    def __init__(self, id, **kw):
        ZMIField.__init__(self, id, **kw)
        PythonScript.__init__(self, id)

    def download(self, selection_name=None, data_method=None, REQUEST=None, **kw):
        """
          This is where we actually render the chart. The main interest
          of doing like this is to accelerate initial rendering

          TODO:
            - add minimal security here
            - implement all pychart options (PNG, PS, SVG, etc.)
            - implement all standard parameters
        """
        # Get the applicable selection
        selection = self.portal_selections.getSelectionFor(selection_name, REQUEST=REQUEST)

        # If selection is None, create a new one
        if selection is None:
          selection = Selection()
        
        # Get the data method if defined
        if data_method is not None:
          here = REQUEST.get('here', self)
          data_method = getattr(here, data_method, None)
        
        # This is the default data, this is just in the case there is not method given
        if data_method is None:
          data = selection()
        else:
          data = selection(data_method=data_method)
    
        # Now call the script - XXX implement bindings properly here
        output = self._exec(here=self, pychart=pychart, data=data)
    
        # And return result
        return output
