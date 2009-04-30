# -*- coding: utf8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Łukasz Nowak <luke@nexedi.com>
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

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface

from Products.ERP5.Document.Amount import Amount

from Products.ERP5.AggregatedAmountList import AggregatedAmountList

import zope.interface

class TradeModelLine(Amount):
    """Trade Model Line
    """
    meta_type = 'ERP5 Trade Model Line'
    portal_type = 'Trade Model Line'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative interfaces
    # Interface.IVariated - as soon as Interface.Variated will be zope3
    zope.interface.implements(
        Interface.ITransformation
    )

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.Amount
                    , PropertySheet.Price
                    , PropertySheet.TradeModelLine
                    )

    def getPrice(self):
      return self._baseGetPrice()

    def updateAggregatedAmountList(self, context, **kw):
      raise NotImplementedError('TODO')

    def getAggregatedAmountList(self, context, movement_list = None,
        current_aggregated_amount_list = None, **kw):
      from Products.ERP5Type.Document import newTempMovement

      normal_resource_use_category_list = self.\
          portal_preferences.getPreferredNormalResourceUseCategoryList()
      if normal_resource_use_category_list is None:
        raise ValueError('preferred_normal_resource_use_category is not ' + \
            'configured in System Preferences')
      if current_aggregated_amount_list is None:
        current_aggregated_amount_list = []

      if movement_list is None:
        movement_list = []

      if len(movement_list) == 0:
        if context.getPortalType() == 'Applied Rule':
          movement_list = [context.getParentValue()]
        else:
          if callable(context.isMovement):
            is_movement = context.isMovement()
          else:
            is_movement = context.isMovement
          if is_movement:
            # we need to create aggreageted amount on context itself
            movement_list = [context]
          else:
            # XXX: filtering shall be in getMovementList
            movement_list = []
            for movement in context.getMovementList():
              movement_resource = movement.getResourceValue()
              if movement_resource is not None:
                if movement_resource.getUse() in \
                    normal_resource_use_category_list:
                  movement_list.append(movement)
      aggregated_amount_list = AggregatedAmountList()
      base_application_list = self.getBaseApplicationList()

      self_id = self.getParentValue().getId() + '_' + self.getId()

      tmp_movement = [q for q in current_aggregated_amount_list \
          if q.getProperty('resource') == self.getResource() ]
      if len(tmp_movement) > 0:
        tmp_movement = tmp_movement[0]
        update = 1
      else:
        update = 0
        tmp_movement = newTempMovement(self.getPortalObject(), self_id )
        tmp_movement.edit(
          causality = self.getRelativeUrl(),
          resource = self.getResource(),
          base_application_list = base_application_list,
          base_contribution_list = self.getBaseContributionList(),
          price = self.getPrice(),
          trade_phase_list = self.getTradePhaseList(),
        )

      modified = 0
      for movement in movement_list:
        if set(base_application_list)\
            .intersection(set(movement.getBaseContributionList())):
          quantity = tmp_movement.getQuantity(0.0)
          modified = 1
          tmp_movement.edit(
            quantity = quantity + movement.getTotalPrice()
          )

      if not update:
        if modified:
          aggregated_amount_list.append(tmp_movement)

      return aggregated_amount_list

