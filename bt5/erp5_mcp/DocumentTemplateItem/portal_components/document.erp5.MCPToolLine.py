##############################################################################
# coding:utf-8
# Copyright (c) 2026 Nexedi SA and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Utils import createExpressionContext, evaluateExpressionFromString


class MCPToolLine(XMLObject):
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.XMLObject,
    PropertySheet.CategoryCore,
    PropertySheet.DublinCore,
    PropertySheet.Reference,
    PropertySheet.Version,
    PropertySheet.SortIndex,
    PropertySheet.MCPToolLine,
  )

  def getParameterDefaultValue(self):
    """
    Convert parameter_default string property to evaluated TALES expression
    """
    tales_string = self.getParameterDefault()
    if tales_string in (None, ""):
      raise ValueError("%s: no default parameter defined" % self.getRelativeUrl())
    expression_context = createExpressionContext(self)
    if tales_string.startswith('python:'):
      return evaluateExpressionFromString(expression_context, tales_string)
    return tales_string

  def getPythonArgumentString(self):
    arg = "%s" % self.getReference()
    try:
      default_value = self.getParameterDefaultValue()
    except ValueError:
      pass
    else:
      arg = "%s=%s" % (arg, repr(default_value))  # XXX is repr enough ?
    return arg

