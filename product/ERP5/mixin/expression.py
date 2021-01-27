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
from Products.ERP5Type.Utils import convertToUpperCase

def ExpressionMixin(property_reference='expression'):
  """
  Mixin for a common pattern where ERP5 objects stores a TALES Expression as text.

  Usage examples:
    Python Script/SQL Method: expression_property (reference=expression)
    GuardableMixin: guard_expression_property (reference=guard_expression)

  CMFCore.Expression already stores the Expression text as 'text' property and
  create a volatile for the instance, so this may seem redundant and we may
  have stored an Expression instance directly on the object. However this
  would make exported objects depend on CMFCore.Expression and not storing
  "directly" user input.
  """
  property_reference_uppercase = convertToUpperCase(property_reference)

  volatile_attribute_name = '_v_' + property_reference + '_instance'
  def _setter(self, value):
    """
    _set<PropertyReference>()
    """
    try:
      delattr(self, volatile_attribute_name)
    except AttributeError:
      pass
    getattr(self, '_baseSet' + property_reference_uppercase)(value)

  def getter(self, default=None):
    """
    get<PropertyReference>Instance()
    """
    try:
      return getattr(self, volatile_attribute_name)
    except AttributeError:
      expression = getattr(self, 'get' + property_reference_uppercase)()
      # Check if the expression is not None, because Expression(<expression>)
      # raises an error in case `expression` is empty or None.
      if expression:
        result = Expression(expression)
      else:
        result = None
      setattr(self, volatile_attribute_name, result)
      return result

  class ExpressionMixin:
    security = ClassSecurityInfo()

  _setter.__name__ = '_set' + property_reference_uppercase
  setattr(ExpressionMixin, _setter.__name__, _setter)

  getter.__name__ = 'get' + property_reference_uppercase + 'Instance'
  setattr(ExpressionMixin, getter.__name__, getter)
  ExpressionMixin.security.declareProtected(Permissions.AccessContentsInformation,
                                            getter.__name__)

  InitializeClass(ExpressionMixin)
  return ExpressionMixin
