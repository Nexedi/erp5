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


import string

from zLOG import LOG

class RawHTMLWidget(Widget.Widget):
  """
  a widget displaying raw html as supplied to it
  (useful mostly for listboxes)
  it is uneditable, so the validator section in ZMI is actually meaningless
  but I don't know how to get rid of it
  """

  default = fields.StringField('default',
                                 title='Default',
                                 description=("this is important"),
                                 default="",
                                 required=0)

  property_names = Widget.Widget.property_names + ['extra']

  def render(self, field, key, value, REQUEST):
    """Render text input field.
    """
    tpl='<div class="%(css_class)s" name="%(name)s" %(extra)s">%(value)s</div>'
    di={'css_class':field.get_value('css_class'),'name':key,'extra':field.get_value('extra'),'value':value}
    return tpl % di

RawHTMLWidgetInstance = RawHTMLWidget()

class RawHTMLField(ZMIField):
  meta_type = "RawHTMLField"

  widget = RawHTMLWidgetInstance
  validator = Validator.TextValidatorInstance


# vim: filetype=python syntax=python shiftwidth=2 
