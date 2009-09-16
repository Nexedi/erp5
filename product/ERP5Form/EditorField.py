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

class EditorWidget(Widget.TextAreaWidget):
  """
    A widget that displays a GUI HTML editor widget (based
    on FCK editor). This widget is intended to be used in
    conjunction with WebSite.

    TODO:
        - implement validation
        - extend to other widgets (kupu) ?
  """

  property_names = Widget.TextAreaWidget.property_names + [
   'text_editor'
  ]

  text_editor = fields.ListField('text_editor',
                                   title='Text Editor',
                                   description=(
        "The text editor widget to use."
        ""),
                                   default="text_area",
                                   required=1,
                                   size=1,
                                   items=[('Standard Text Area', 'text_area'),
                                          ('FCK Editor', 'fck_editor')])

  def render(self, field, key, value, REQUEST, render_prefix=None):
    """
      Render editor
    """
    here = REQUEST['here']
    text_editor = field.get_value('text_editor')
    if text_editor == 'text_area':
      return Widget.TextAreaWidget.render(self, field, key, value, REQUEST)
    else:
      return here.fckeditor_wysiwyg_support.pt_render(
           extra_context= {
                          'inputvalue' : value,
                          'inputname'  : key
                        })

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    """ 
      Render form in view only mode.
    """
    if value is None:
      value = ''
    return value

EditorWidgetInstance = EditorWidget()

class EditorField(ZMIField):
  meta_type = "EditorField"

  widget = EditorWidgetInstance
  validator = Validator.TextValidatorInstance
