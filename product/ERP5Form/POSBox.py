##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Mikael Barbero <mikael@nexedi.com>
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

from Products.Formulator import Widget, Validator
from Products.Formulator.Field import ZMIField
from Products.Formulator.DummyField import fields
from Products.ERP5Type.Utils import convertToUpperCase
from Products.CMFCore.utils import getToolByName

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.ERP5Type.Globals import get_request
from Products.PythonScripts.Utility import allow_class

from Products.PythonScripts.standard import url_quote_plus

import string

from zLOG import LOG

class POSBoxWidget(Widget.Widget):
  """
  A widget that display a point of sales UI.
  """
  
  property_names = Widget.Widget.property_names + [
    'html_ZPT', \
    'javascript_ZPT', \
    'css_ZPT', \
    'getResourceByReference_ZPT', \
    'createOrder_script', \
    'portal_types', \
    'display_fastResourceEntry', \
    'portal_type_fastResourceEntry', \
    'resource_category_fastResourceEntry', \
    'barcodeStartString', \
    'pos_layout', \
    'barcodeStopString', \
    'display_bgcolor', \
    'display_txtcolor', \
    'order_summary_aLine', \
    'order_summary_anotherLine'
  ]

  default = fields.StringField(
                                'default',
                                title='Default',
                                description=(
    "Default value of the text in the widget."),
                                default="",
                                required=0)

  html_ZPT = fields.StringField(
                                'html_ZPT',
                                title='Page Template for HTML',
                                description=(
    "Page Template for generating POSBox UI HTML"),
                                default="POSBox",
                                required=1)

  javascript_ZPT = fields.StringField(
                                'javascript_ZPT',
                                title='Page Template for JavaScript',
                                description=(
    "Page Template for generating JavaScript's options"),
                                default="POSBox_js",
                                required=1)

  css_ZPT = fields.StringField(
                                'css_ZPT',
                                title="Page Template for CSS",
                                description=(
      "Page Template for generating dynamic CSS"),
                                default="POSBox_css",
                                required=1)

  getResourceByReference_ZPT = fields.StringField(
                                'getResourceByReference_ZPT',
                                title="Page Template for generating resource's XML",
                                description=(
    "Page template which generates the XML of the resource when asking for a referencce"),
                                default="getResourceByReference",
                                required=1)

  createOrder_script = fields.StringField(
                                'createOrder_script',
                                title="Python script for creating the order",
                                description=(
    "Python script which create the order from the XML sended by POS"),
                                default="createOrder",
                                required=1)
  
  display_fastResourceEntry = fields.ListField(
                                'display_fastResourceEntry',
                                title='Display Fast Resource Entry Block',
                                description=(
    "Is the fast resource entry block displayed ?"),
                                default='False',
                                items=['True', 'False'],
                                size=1,
                                required=1,
                                group="Fast Product Entry")
  
  portal_type_fastResourceEntry = fields.StringField(
                                'portal_type_fastResourceEntry',
                                title='Portal Type of resources',
                                description=(
    "What is the portal type of resources in fast resource entry block"),
                                default='',
                                required=0,
                                group="Fast Product Entry")
                                
  
  portal_types = fields.ListTextAreaField(
                                'portal_types',
                                title='Portal Types',
                                description=(
    "The allowed resource to be requested by reference. Required."),
                                default=[],
                                required=1)

  resource_category_fastResourceEntry = fields.StringField(
                                'resource_category_fastResourceEntry',
                                title='Top level Resource Category',
                                description=(
    "The ProductLine that is a the top level of fast resource entry"),
                                default='',
                                required=0,
                                group="Fast Product Entry")
  
  pos_layout = fields.ListField(
                                'pos_layout',
                                title='Layout',
                                description=(
    "How is the layout organised"),
                                default='',
                                items=[
                                    'Summary of the order on the left' 
                                    , 'Summary of the order on the right'
                                  , ],
                                size=1,
                                required=1)
    
  barcodeStartString = fields.StringField(
                                'barcodeStartString',
                                title='Barcode Prefix String',
                                description=(
    "The string which is prefixed by the barcode while reading"),
                                default="#",
                                required=1,
                                group="barcode")

  barcodeStopString = fields.StringField(
                                'barcodeStopString',
                                title='Barcode Suffix String',
                                description=(
    "The string which is prefixed by the barcode while reading"),
                                default="#",
                                required=1,
                                group="barcode")

  display_bgcolor = fields.StringField(
                                'display_bgcolor',
                                title='Background color',
                                description=(
    "Color in html hex format (#000000 by ex.)"),
                                default="#ffffcc",
                                required=0,
                                group="display area")

  display_txtcolor = fields.StringField(
                                'display_txtcolor',
                                title='Text color',
                                description=(
    "Color in html hex format (#000000 by ex.)"),
                                default="#000000",
                                required=0,
                                group="display area")

  order_summary_aLine = fields.StringField(
                                'order_summary_aLine',
                                title="Order line background color 1",
                                description=(
    "Background color of a order line in order summary view"),
                                default="#e3e3e3",
                                required=0,
                                group="order summary")
    
  order_summary_anotherLine = fields.StringField(
                                'order_summary_anotherLine',
                                title="Order line background color 2",
                                description=(        
    "Background color of another order line in order summary view"),
                                default="#ffffff",
                                required=0,
                                group="order summary")
 
  def render(self, field, key, value, REQUEST, render_prefix=None):
    """
      Render point of sales widget.
    """
    here = REQUEST['here']
    page_template = getattr(here,field.get_value("html_ZPT"))

    return "<!-- Generated by render -->\n%s" % page_template()

  def render_css(self, field, key, value, REQUEST):
    here = REQUEST['here']
    page_template = getattr(here,field.get_value("css_ZPT"))
    
    return "<!-- Generated by render_css  -->\n%s" % page_template(
        display_txtcolor = field.get_value("display_txtcolor"),
        display_bgcolor = field.get_value("display_bgcolor"),
        pos_layout_left = (field.get_value("pos_layout") == 'Summary of the order on the left'),
        order_summary_aLine = field.get_value("order_summary_aLine"),
        order_summary_anotherLine = field.get_value("order_summary_anotherLine"),
        fastResourceEntry_display = field.get_value("display_fastResourceEntry"),
        )

  def render_javascript(self, field, key, value, REQUEST, render_prefix=None):
    here = REQUEST['here']
    page_template = getattr(here,field.get_value("javascript_ZPT"))

    

    return "<!-- Generated by render_javascript -->\n%s" % page_template(
        getResourceByReference_ZPT = field.get_value('getResourceByReference_ZPT'),
        createOrder_script = field.get_value('createOrder_script'),
        portal_types = "portal_type:list=" + "&portal_type:list=".join([url_quote_plus(x[0]) for x in field.get_value('portal_types')]),
        barcodeStartString = field.get_value('barcodeStartString'),
        barcodeStopString = field.get_value('barcodeStopString'),
        fastResourceEntry_display = field.get_value("display_fastResourceEntry"),
        portal_type_fastResourceEntry = field.get_value('portal_type_fastResourceEntry'),
        resource_category_fastResourceEntry = field.get_value('resource_category_fastResourceEntry')
        ) 

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    """ 
      Render point of sales widget
    """
    return "<p>Generated by render_view</p>"

class POSBoxValidator(Validator.Validator):
  """
    No need to validate POSBox as input is controlled by client side's javascript
  """
  property_names = Validator.Validator.property_names

  def validate(self, field, key, REQUEST):
    return None

POSBoxWidgetInstance = POSBoxWidget()
POSBoxValidatorInstance = POSBoxValidator()

class POSBox(ZMIField):
  meta_type = "POSBox"

  widget = POSBoxWidgetInstance
  validator = POSBoxValidatorInstance

  def render_css(self, value=None, REQUEST=None):
    return self.widget.render_css(self,'',value,REQUEST)

  def render_javascript(self, value=None, REQUEST=None, render_prefix=None):
    return self.widget.render_javascript(self,'',value,REQUEST)

