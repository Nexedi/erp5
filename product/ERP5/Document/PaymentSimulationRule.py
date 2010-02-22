##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5.Document.Rule import Rule
from Products.ERP5.Document.PredicateMatrix import PredicateMatrix

class PaymentSimulationRule(Rule, PredicateMatrix):
  """
  Payment Simulation Rule generates payment simulation movements from
  accounting / invoice transaction simulation movements.
  """

  # CMF Type Definition
  meta_type = 'ERP5 Payment Simulation Rule'
  portal_type = 'Payment Simulation Rule'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _generatePrevisionList(self, applied_rule, **kw):
    """
    Generate a list of dictionaries, that contain calculated content of
    current Simulation Movements in applied rule.
    based on its context (parent movement, delivery, configuration ...)

    These previsions are returned as dictionaries.
    """
    input_movement, business_path = self._getInputMovementAndPathTupleList(
        applied_rule)[0]
    kw = self._getExpandablePropertyDict(applied_rule, input_movement, None)
    prevision_list = []

    # Find a matching cell
    cell = self._getMatchingCell(input_movement)

    if cell is not None : # else, we do nothing
      for payment_rule_cell_line in cell.objectValues():
        prevision_line = kw.copy()
        prevision_line.update(
          source=payment_rule_cell_line.getSource() or \
                 input_movement.getSource(),
          destination=payment_rule_cell_line.getDestination() or \
                 input_movement.getDestination(),
          quantity=input_movement.getQuantity() * \
                   payment_rule_cell_line.getQuantity()
          )
        # Generate Prevision Script is required for Payment Simulation Rule?
        if payment_rule_cell_line.hasProperty(
            'generate_prevision_script_id'):
          generate_prevision_script_id = \
                payment_rule_cell_line.getGeneratePrevisionScriptId()
          prevision_line.update(getattr(input_movement,
                              generate_prevision_script_id)(prevision_line))
        prevision_list.append(prevision_line)
    return prevision_list

  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, applied_rule, **kw):
    """Expands the current movement downward.
    """
    return Rule._expand(self, applied_rule, **kw)

  # Matrix related
  security.declareProtected( Permissions.ModifyPortalContent,
                              'newCellContent' )
  def newCellContent(self, id, portal_type='Accounting Rule Cell', **kw):
    """Overriden to specify default portal type
    """
    return self.newContent(id=id, portal_type=portal_type, **kw)
