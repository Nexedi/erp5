##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Globals import get_request
from AccessControl.ZopeGuards import guarded_getattr
from Products.Formulator import Widget, Validator
from Products.Formulator.Field import ZMIField
from Products.Formulator.DummyField import fields

class ReportBoxWidget(Widget.Widget):

  property_names = list(Widget.Widget.property_names)
  property_names.append('report_method')

  # XXX this is only needed on bootstrap
  default = fields.StringField('default',
                                title='Default',
                                description="",
                                default="",
                                required=0)

  report_method = fields.StringField('report_method',
                                     title='Report Method',
                                     description="",
                                     default="",
                                     required=0)

  def render_view(self, field, value, REQUEST=None, key='reportbox', render_prefix=None):
    """
    """
    if REQUEST is None:
      REQUEST = get_request()
    return self.render(field, key, value, REQUEST)

  def render(self, field, key, value, REQUEST, render_prefix=None):
    """
    """
    form = getattr(field, 'aq_parent', None)
    if form is not None:
      obj = getattr(form, 'aq_parent', None)
    else:
      obj = None
    if obj is not None:
      report_method = guarded_getattr(obj, field['report_method'])
      if callable(report_method):
        return report_method()


class ReportBoxValidator(Validator.Validator):

  def validate(self, field, key, REQUEST):
    return True


class ReportBox(ZMIField):
  meta_type = "ReportBox"

  widget = ReportBoxWidget()
  validator = ReportBoxValidator()
