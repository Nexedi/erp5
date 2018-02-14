##############################################################################
#
# Copyright (c) 2018 Nexedi SA and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
from Products.CMFCore.Expression import Expression
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import InitializeClass

class ExpressionMixin:
  security = ClassSecurityInfo()

  def _setExpression(self, value):
    try:
      del self._v_expression_instance
    except AttributeError:
      pass
    self._baseSetExpression(value)

  security.declareProtected(Permissions.AccessContentsInformation, 'getExpressionInstance')
  def getExpressionInstance(self, default=None):
    try:
      return self._v_expression_instance
    except AttributeError:
      result = Expression(self.getExpression())
      self._v_expression_instance = result
      return result

InitializeClass(ExpressionMixin)
