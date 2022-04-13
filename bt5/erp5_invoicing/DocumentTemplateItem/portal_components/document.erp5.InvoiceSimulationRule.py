# -*- coding: utf-8 -*-
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.mixin.RuleMixin import RuleMixin
from erp5.component.mixin.MovementGeneratorMixin import MovementGeneratorMixin
from erp5.component.mixin.MovementCollectionUpdaterMixin import \
     MovementCollectionUpdaterMixin
from erp5.component.interface.IRule import IRule
from erp5.component.interface.IDivergenceController import IDivergenceController
from erp5.component.interface.IMovementCollectionUpdater import IMovementCollectionUpdater

@zope.interface.implementer(IRule,
                            IDivergenceController,
                            IMovementCollectionUpdater,)
class InvoiceSimulationRule(RuleMixin, MovementCollectionUpdaterMixin):
  """
  Invoicing Rule expand simulation created by a order or delivery rule.
  """
  # CMF Type Definition
  meta_type = 'ERP5 Invoice Simulation Rule'
  portal_type = 'Invoice Simulation Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.XMLObject,
    PropertySheet.CategoryCore,
    PropertySheet.DublinCore,
    PropertySheet.Task,
    PropertySheet.Predicate,
    PropertySheet.Reference,
    PropertySheet.Version,
    PropertySheet.Rule
    )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isAccountable')
  def isAccountable(self, movement):
    """
    Tells whether generated movement needs to be accounted or not.

    Invoice movement are never accountable, so simulation movement for
    invoice movements should not be accountable either.
    """
    return False

  def _getMovementGenerator(self, context):
    """
    Return the movement generator to use in the expand process
    """
    return InvoicingRuleMovementGenerator(applied_rule=context, rule=self)

  def _isProfitAndLossMovement(self, movement):
    # For a kind of trade rule, a profit and loss movement lacks source
    # or destination.
    return (movement.getSource() is None or movement.getDestination() is None)

class InvoicingRuleMovementGenerator(MovementGeneratorMixin):

  def _getUpdatePropertyDict(self, input_movement):
    # Filter out specialise values we don't want, like transformations
    # XXX Should there be a configurable property on the rule ?
    specialise_list = [x.getRelativeUrl()
      for x in input_movement.getSpecialiseValueList()
      if x.providesIBusinessProcess() or
         x.isInternalType() or x.isPurchaseType() or x.isSaleType()]
    return {'delivery': None, 'specialise': specialise_list}

  def _getInputMovementList(self, movement_list=None, rounding=None):
    return [self._applied_rule.getParentValue(),]
