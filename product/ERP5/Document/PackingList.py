##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
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
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces

from Products.ERP5.Document.Delivery import Delivery
from zLOG import LOG
from warnings import warn

class PackingList(Delivery):
    """
      Delivery/PackingList is the main document
      which allows to control causality in the simulation

      PackingList have 2 different states:

      - solved: this happens when quantities and target
        quantities are the same

      - diverged: this happens when quantities and target
        quantities are different

      Resolution of diverged PackingList is achieved by workflow
      methods. Such workflow methods eventually change
      movements in the simulation. Typical solution include:

      - reduce quantity

      - split delivery

      - postpone delivery

      solutions are implemented as solvers
    """
    # CMF Type Definition
    meta_type = 'ERP5 Packing List'
    portal_type = 'Packing List'
    add_permission = Permissions.AddPortalContent
    isDelivery = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Comment
                      , PropertySheet.Movement
                      , PropertySheet.TradeCondition
                      , PropertySheet.PackingList
                      )

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'isDivergent')
    def isDivergent(self,**kw):
      """
        Returns 1 if not simulated or inconsistent target and values
      """
      if self.getSimulationState() not in self.getPortalDraftOrderStateList():
        if not self.isSimulated():
          return 1
      return Delivery.isDivergent(self, **kw)

    #######################################################
    # Container computation
    security.declareProtected(Permissions.AccessContentsInformation, 
                              'isPacked')
    def isPacked(self):
      """
        Returns 0 if all quantity resource on packing list line
        are not in container.
        It works only if a Resource is not on 2 PackingListLine.
      """
      for movement in self.getMovementList():

        quantity = movement.getQuantity()
        query_kw = {
          'portal_type': self.getPortalContainerLineTypeList(),
          'movement.explanation_uid': self.getUid(),
          'movement.resource_uid': movement.getResourceUid(),
          'movement.variation_text': movement.getVariationText(),
          'has_cell_content': 0,
        }
        container_mvt_list = self.portal_catalog(**query_kw)
        packed_quantity = sum([x.getQuantity() for x in container_mvt_list \
                               if x.getQuantity() is not None])

        if quantity != packed_quantity:
          return 0

      return 1

    ##########################################################################
    # Applied Rule stuff
    def updateAppliedRule(self, rule_id=None, rule_reference=None, **kw):
      """XXX FIXME: Kept for compatibility.
      updateAppliedRule must be called with a rule_reference in a workflow
      script.
      """
      if rule_id is None and rule_reference is None:
        warn('Relying on a default delivery rule is deprecated; ' \
             'rule_reference must be specified explicitly.',
             DeprecationWarning)
        rule_reference = 'default_delivery_rule'
      Delivery.updateAppliedRule(self, rule_id=rule_id, 
                                 rule_reference=rule_reference, **kw)
