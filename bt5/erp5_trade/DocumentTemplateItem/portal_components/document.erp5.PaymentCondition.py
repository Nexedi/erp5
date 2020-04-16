##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.document.TradeModelLine import TradeModelLine

class PaymentCondition(TradeModelLine):
  """
    Payment Conditions are used to define all the parameters of a payment
  """

  meta_type = 'ERP5 Payment Condition'
  portal_type = 'Payment Condition'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.PaymentCondition
                    , PropertySheet.Chain
                    )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCalculationScript')
  def getCalculationScript(self, context):
    # In the case of Payment Condition, unlike Trade Model Line,
    # it is not realistic to share the same method, so do not acquire
    # a script from its parent.
    #
    # It is always complicated and different how to adopt the calculation of
    # payment dates for each user, and it is not practical to force the
    # user to set a script id in every Payment Condition, so it is better
    # to use a type-based method here, unless a script is explicitly set.
    script_id = self.getCalculationScriptId()
    if script_id is not None:
      method = getattr(context, script_id)
      return method
    method = self._getTypeBasedMethod('calculateMovement')
    return method
