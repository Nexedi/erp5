# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Łukasz Nowak <luke@nexedi.com>
#                    Fabien Morin <fabien@nexedi.com>
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
from Products.ERP5.Document.Predicate import Predicate
from Products.ERP5Type.Utils import cartesianProduct
from Products.ERP5.AggregatedAmountList import AggregatedAmountList
import zope.interface

class TradeModelLine(Predicate, XMLMatrix, Amount):
    """Trade Model Line is a way to represent trade transformation for movements

    TODO:
      - make this code readable
      - use comments
      - use docstrings
    """
    meta_type = 'ERP5 Trade Model Line'
    portal_type = 'Trade Model Line'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative interfaces
    zope.interface.implements(
        interfaces.ITransformation,
        interfaces.IVariated
    )

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.CategoryCore
                    , PropertySheet.Amount
                    , PropertySheet.Price
                    , PropertySheet.TradeModelLine
                    , PropertySheet.Reference
                    , PropertySheet.Predicate
                    )

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getPrice')
    def getPrice(self):
      return self._baseGetPrice()

    def updateAggregatedAmountList(self, context, **kw):
      raise NotImplementedError('TODO')

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAggregatedAmountList')
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

      # XXX - really unreadable - more comments please
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
          if q.getReference() == self.getReference() ]
      if len(tmp_movement_list) > 0:
        tmp_movement_list = tmp_movement_list[:1]
        update = 1
      else:
        common_params = {
                'causality':self.getRelativeUrl(),
                'resource':self.getResource(),
                'reference':self.getReference(),
                'base_application_list':base_application_list,
                'base_contribution_list':self.getBaseContributionList(),
                'start_date':context.getStartDate(),
                'stop_date':context.getStopDate(),
                'create_line':self.isCreateLine(),
                'trade_phase_list':self.getTradePhaseList(),
            }
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
                price = cell.getPrice(),
                quantity = cell.getQuantity(0.0),
                **common_params
                )
            tmp_movement_list.append(tmp_movement)
        else:
          tmp_movement = newTempSimulationMovement(self.getPortalObject(),
              self_id )
          tmp_movement.edit(
            quantity = self.getQuantity(0.0),
            price = self.getPrice(),
            **common_params
          )
          tmp_movement_list.append(tmp_movement)
      modified = 0
      for tmp_movement in tmp_movement_list:
        if len(self.getVariationCategoryList()) == 0 and \
            self.getQuantity(None) is None or \
            len(self.getVariationCategoryList()) and \
            tmp_movement.getQuantity(None) is None:
          # if the quantity is not defined, that mean we should search on
          # all movements with correponding base_amount (if we use cells, we
          # have to look on cells, if we don't, look on self)
          for movement in movement_list:
            if set(base_application_list)\
                .intersection(set(movement.getBaseContributionList())):
              # if the movement have no variation category, it's the same as
              # if he have all variation categories
              if len(movement.getVariationCategoryList()) == 0 or \
                  set(movement.getVariationCategoryList()).intersection(\
                  set(tmp_movement.getVariationCategoryList())):
                  quantity = tmp_movement.getQuantity(0.0)
                  modified = 1
                  tmp_movement.edit(
                    quantity = quantity + movement.getTotalPrice()
                  )
        else:
          # if the quantity is defined, we use it
          modified = 1
          if tmp_movement.getPrice() in (0, None):
            # if price is not defined, it the same as 100 %
            tmp_movement.edit(
              price = 1
            )

        # check if slices are used
        salary_range_list = tmp_movement.getVariationCategoryList(\
            base_category_list='salary_range') #XXX hardcoded values
        salary_range = len(salary_range_list) and salary_range_list[0] or None
        if salary_range is not None:
          # we use slice
          model = self.getParentValue()
          cell = model.getCell(salary_range)
          if cell is None:
            raise ValueError("Can't find the cell corresponding to those "+\
                "cells coordinates : %s" % salary_range)
          model_slice_min = cell.getQuantityRangeMin()
          model_slice_max = cell.getQuantityRangeMax()
          base_application = tmp_movement.getQuantity(0.0)
          if base_application-model_slice_min>0:
            if base_application <= model_slice_max:
              tmp_movement.edit(
                quantity = base_application-model_slice_min
              )
            elif model_slice_max:
              tmp_movement.edit(
                quantity = model_slice_max-model_slice_min
              )

        if not update:
          if modified:
            aggregated_amount_list.append(tmp_movement)

      return aggregated_amount_list
