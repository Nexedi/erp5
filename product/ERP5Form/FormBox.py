##############################################################################
#
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
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

from Products.Formulator import Widget, Validator
from Products.Formulator.Field import ZMIField
from Products.Formulator.DummyField import fields
from Products.ERP5Type.Utils import convertToUpperCase
from Products.CMFCore.utils import getToolByName

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Globals import get_request
from Products.PythonScripts.Utility import allow_class

from Products.PythonScripts.standard import url_quote_plus

import string

from zLOG import LOG

class FormBoxWidget(Widget.Widget):
  """
      A widget that display a form within a form.

      A first purpose of this widget is to display addresses in
      a different order for every localisation.

      A second purpose of this widget is to represent a single value
      (ex. a number, a date) into multiple forms. We need for that
      purpose a script to assemble a value out of

      A third purpose is to display values on subobjects and,
      if necessary, create such objects ?

      WARNING: this is still pre-alpha code for experimentation. Do not
      use in production.
  
      TODO:
          - implement validation
  """

  property_names = Widget.Widget.property_names + [
    'form_id', \
  ]

  form_id = fields.StringField(
                                'form_id',
                                title='Form ID',
                                description=(
    "ID of the form which must be rendered in this box."),
                                default="",
                                required=1)

  default = fields.StringField(
                                'default',
                                title='Default',
                                description=(
    "A default value (not used)."),
                                default="",
                                required=0)

 
  def render(self, field, key, value, REQUEST):
    """
        Render a form in a field
    """
    here = REQUEST['here']
    form = getattr(here, field.get_value('form_id'))
    return form()

  def render_view(self, field, value):
    """ 
        Display a form in a field
    """
    return self.render()

class FormBoxValidator(Validator.Validator):
  """
    Validate all fields of the form and return
    the result as a single variable.
  """
  property_names = Validator.Validator.property_names

  def validate(self, field, key, REQUEST):
    form = field.aq_parent
    form = getattr(form, field.get_value('form_id'))
    return form.validate(REQUEST)

FormBoxWidgetInstance = FormBoxWidget()
FormBoxValidatorInstance = FormBoxValidator()

class FormBox(ZMIField):
  meta_type = "FormBox"

  widget = FormBoxWidgetInstance
  validator = FormBoxValidatorInstance
