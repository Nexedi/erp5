# -*- coding: utf-8 -*-
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
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5.Document.Amount import Amount
from Products.ERP5Type.Utils import cartesianProduct
from Products.ERP5.AggregatedAmountList import AggregatedAmountList
import zope.interface

class TradeModelLine(XMLMatrix, Amount):
    """Trade Model Line
    """
    meta_type = 'ERP5 Trade Model Line'
    portal_type = 'Trade Model Line'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative interfaces
    # interfaces.IVariated - as soon as interfaces.IVariated will be zope3
    zope.interface.implements(
        interfaces.ITransformation
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
        current_aggregated_amount_list = None, base_id='movement', **kw):
      from Products.ERP5Type.Document import newTempSimulationMovement

      # test with predicate if this model line could be applied
      if not self.test(context):
        # This model_line should not be applied
        return []

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

      tmp_movement_list = [q for q in current_aggregated_amount_list \
          if q.getProperty('resource') == self.getResource() ]
      if len(tmp_movement_list) > 0:
        tmp_movement_list = tmp_movement_list[:1]
        update = 1
      else:
        update = 0
        base_category_list = self.getVariationBaseCategoryList()
        category_list_list = []
        for base_cat in base_category_list:
          category_list = self.getVariationCategoryList(
                                          base_category_list=base_cat)
          category_list_list.append(category_list)
        cartesian_product = cartesianProduct(category_list_list)
        # if categories are used, we want to look for all cells
        if len(category_list_list) > 0:
          for cell_coordinates in cartesian_product:
            cell = self.getCell(base_id=base_id, *cell_coordinates)
            if cell is None:
              raise ValueError("Can't find the cell corresponding to those "+\
                  "cells coordinates : %s" % cell_coordinates)
            tmp_movement = newTempSimulationMovement(self.getPortalObject(),
                self_id )
            tmp_movement.edit(
                variation_base_category_list = cell.getVariationBaseCategoryList(),
                variation_category_list = cell.getVariationCategoryList(),
                causality = self.getRelativeUrl(),
                resource = self.getResource(),
                base_application_list = base_application_list,
                base_contribution_list = self.getBaseContributionList(),
                price = cell.getPrice(),
                quantity = cell.getQuantity(0.0),
                trade_phase_list = self.getTradePhaseList(),
                )
            tmp_movement_list.append(tmp_movement)
        else:
          tmp_movement = newTempSimulationMovement(self.getPortalObject(),
              self_id )
          tmp_movement.edit(
            causality = self.getRelativeUrl(),
            resource = self.getResource(),
            base_application_list = base_application_list,
            base_contribution_list = self.getBaseContributionList(),
            price = self.getPrice(),
            trade_phase_list = self.getTradePhaseList(),
          )
          tmp_movement_list.append(tmp_movement)

      modified = 0
      
      for tmp_movement in tmp_movement_list:
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
