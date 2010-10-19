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
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5.Document.Amount import Amount
from Products.ERP5Type.Core.Predicate import Predicate
from Products.ERP5.AggregatedAmountList import AggregatedAmountList
from Products.ERP5.Document.TradeCondition import TradeCondition
from Products.ERP5.PropertySheet.TradeModelLine import (TARGET_LEVEL_MOVEMENT,
                                                        TARGET_LEVEL_DELIVERY)
import zope.interface

class TradeModelLine(Predicate, XMLMatrix, Amount):
  """Trade Model Line is a way to represent trade transformation for movements"""
  meta_type = 'ERP5 Trade Model Line'
  portal_type = 'Trade Model Line'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(
      interfaces.IAmountGenerator,
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
                            'getCalculationScript')
  def getCalculationScript(self, context):
    '''get script in this order :
          1 - model_line script
          2 - model script
    '''
    # get the model line script
    script_name = self.getCalculationScriptId()
    if script_name is None:
      # if model line script is None, get the default model script
      if isinstance(self.getParentValue(), TradeCondition):
        # if parent is a TradeCondition
        script_name = self.getParentValue().getCalculationScriptId()
    if script_name is None:
      return None
    script = getattr(context, script_name, None)
    if script is None:
      raise ValueError, "Unable to find `%s` calculation script" % \
                                                       script_name
    return script

  security.declareProtected(Permissions.AccessContentsInformation, 'test')
  def test(self, context, tested_base_category_list=None, strict_membership=0,
           **kw):
    result = TradeModelLine.inheritedAttribute('test')(
      self, context, tested_base_category_list, strict_membership, **kw)

    if result and self.getTargetLevel():
      # If Trade Model Line is set to delivery level, then do nothing
      # at movement level.
      if self.getTargetLevel()==TARGET_LEVEL_DELIVERY and not context.isDelivery():
        return False
    return result

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAggregatedAmountList')
  def getAggregatedAmountList(self, context, movement_list=None,
      current_aggregated_amount_list=None, base_id='movement',
      rounding=False, **kw):

    # test with predicate if this model line could be applied
    if not self.test(context):
      # This model_line should not be applied
      return []
    if movement_list is None:
      movement_list = []
    if current_aggregated_amount_list is None:
      current_aggregated_amount_list = []

    # if movement_list is passed as parameter, it shall be used,
    # otherwise it is needed to look up for movements
    if len(movement_list) == 0:
      # no movements passed, need to find some
      if context.isMovement():
        # create movement lists from context
        movement_list = [context]
      else:
        # create movement list for delivery's movements
        movement_list = []
        for movement in context.getMovementList():
          # XXX: filtering shall be in getMovementList
          # add only movement which are input (i.e. resource use category
          # is in the normal resource use preference list). Output will
          # be recalculated
          if not movement.getBaseApplication():
            movement_list.append(movement)

    if self.getTargetLevel()==TARGET_LEVEL_MOVEMENT:
      # movement level trade model is applied to each movement and
      # generate result par movement.
      result = []
      # If there is an amount which target level is delivery level and
      # create line is true, then treat it as a movement.
      movement_like_amount_list = []
      temporary_aggregated_amount_list = []
      for amount in current_aggregated_amount_list:
        if (amount.getProperty('target_level')==TARGET_LEVEL_DELIVERY and
            amount.getProperty('create_line')):
          movement_like_amount_list.append(amount)
        else:
          temporary_aggregated_amount_list.append(amount)
      for movement in (movement_list + movement_like_amount_list):
        result.extend(self._getAggregatedAmountList(
          context, [movement], temporary_aggregated_amount_list,
          base_id, rounding, **kw))
      return result
    else:
      return self._getAggregatedAmountList(
        context, movement_list, current_aggregated_amount_list,
        base_id, rounding, **kw)

  def _getAggregatedAmountList(self, context, movement_list=None,
                               current_aggregated_amount_list=None,
                               base_id='movement', rounding=False, **kw):
    from Products.ERP5Type.Document import newTempSimulationMovement

    # ROUNDING
    if rounding:
      rounding_proxy = getToolByName(self.getPortalObject(),
                                     'portal_roundings').getRoundingProxy
      movement_list = [rounding_proxy(movement, context=self)
                       for movement in movement_list]

    aggregated_amount_list = AggregatedAmountList()
    base_application_list = self.getBaseApplicationList()

    document = self.getParentValue()
    self_id = '_'.join((document.getId(), self.getId(), context.getId()))

    # Make tmp movement list only when trade model line is not set to movement level.
    tmp_movement_list = []
    if self.getTargetLevel()!=TARGET_LEVEL_MOVEMENT:
      tmp_movement_list = [processed_movement
                           for processed_movement in current_aggregated_amount_list
                           if processed_movement.getReference() == self.getReference()]

    if len(tmp_movement_list) > 0:
      update = 1
    else:
      # get source and destination using Business Process
      if getattr(document, 'findEffectiveSpecialiseValueList', None) is None:
        # if parent don't have findSpecialiseValueList, this mean it's on the
        # specialise_value
        document = self.getParentValue().getSpecialiseValue()
      try:
        business_process_list = document.findEffectiveSpecialiseValueList(
            context=context, portal_type_list=['Business Process'])
      except AttributeError:
        business_process_list = []
      business_process = None
      property_dict = {}
      if len(business_process_list):
        # XXX currently, is too complicated to use more than
        # one Business Process, so the first (which is the nearest from the
        # delivery) is took
        business_process = business_process_list[0]
        business_path_list = business_process.getPathValueList(trade_phase=
            self.getTradePhase(), context=context)
        if len(business_path_list) > 1:
          raise NotImplementedError, 'For now, it can not support more '\
              'than one business_path with same trade_phase. '\
              '%s have same trade_phase' % repr(business_path_list)
        if len(business_path_list) == 1:
          business_path = business_path_list[0]
          property_dict={
            'source':context.getSourceList(),
            'destination':context.getDestinationList(),
            'source_section':context.getSourceSectionList(),
            'destination_section':context.getDestinationSectionList(),
            'source_decision':context.getSourceDecisionList(),
            'source_administration':context.getSourceAdministrationList(),
            'source_payment':context.getSourcePaymentList(),
            'destination_decision':context.getDestinationDecisionList(),
            'destination_administration':
            context.getDestinationAdministrationList(),
            'destination_payment':context.getDestinationPaymentList()
          }
          property_dict.update(
            business_path.getArrowCategoryDict(context=context))

      common_params = {
        'title':self.getTitle(),
        'description':self.getDescription(),
        'resource': self.getResource(),
        'reference': self.getReference(),
        'int_index': self.getIntIndex(),
        'base_application_list': base_application_list,
        'base_contribution_list': self.getBaseContributionList(),
        'start_date': context.getStartDate(),
        'stop_date': context.getStopDate(),
        'create_line': self.isCreateLine(),
        'trade_phase_list': self.getTradePhaseList(),
        'target_level': self.getTargetLevel(),
        'use': self.getUse(),
      }
      common_params.update(property_dict)

      update = 0
      base_category_list = self.getVariationBaseCategoryList()
      
      # get cells categories cartesian product
      cell_key_list = self.getCellKeyList(base_id='movement')
      if len(cell_key_list) > 0:
        # look for cells
        for cell_coordinates in cell_key_list:
          cell = self.getCell(base_id=base_id, *cell_coordinates)
          if cell is None:
            raise ValueError("Line '%s' (%s) can't find the cell corresponding"
                " to those cells coordinates : %s" % (self.getTitle(),
                                                      self.getRelativeUrl(),
                                                      cell_coordinates))
          tmp_movement = newTempSimulationMovement(self.getPortalObject(),
              self_id)

          # ROUNDING
          if rounding:
            # Once tmp_movement is replaced with the proxy, then the proxy
            # object returns rounded value.
            # For example, if rounding model is defined as
            # rounded_property_id='total_price', then proxied
            # tmp_movement.getTotalPrice() returns rounded result.
            # If rounded_property_id='quantity', then
            # tmp_movement.getQuantity() will be rounded.
            tmp_movement = rounding_proxy(tmp_movement, context=self)
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
          self_id,
          quantity = self.getQuantity(0.0),
          price = self.getPrice(),
          **common_params
        )

        # ROUNDING
        if rounding:
          # Replace temporary movement with rounding proxy so that target
          # property value will be rounded.
          tmp_movement = rounding_proxy(tmp_movement, context=self)
        tmp_movement_list.append(tmp_movement)
    modified = 0
    aggregated_movement_list = []
    for tmp_movement in tmp_movement_list:
      if len(self.getVariationCategoryList()) == 0 and \
          self.getQuantity(None) is None or \
          len(self.getVariationCategoryList()) and \
          tmp_movement.getQuantity(None) is None:
        for movement in movement_list + current_aggregated_amount_list:
          # here we need to look on movement_list and also on already processed
          # movements (current_aggregated_amount_list).
          # if the quantity is not defined, take it by searching all movements
          # that used this base_amount
          if self._isMatchedMovement(movement, base_application_list, tmp_movement):
            # at least one base application is in base contributions and
            # if the movement have no variation category, it's the same as
            # if he have all variation categories
            quantity = tmp_movement.getQuantity(0.0)
            modified = 1
            tmp_movement.setQuantity(quantity + movement.getTotalPrice())
            aggregated_movement_list.append(movement)
        if aggregated_movement_list:
          tmp_movement.setCausalityValueList(aggregated_movement_list)

      else:
        # if the quantity is defined, use it
        #
        # Is this really good? This looks too implicit.
        # Using something like "apply this trade model line by force"
        # option would be better...(yusei)
        modified = 1
        if tmp_movement.getPrice() is None:
          # if price is not defined, it the same as 100 %
          tmp_movement.setPrice(1)

      # if a calculation script is defined, use it
      calculation_script = self.getCalculationScript(context)
      if calculation_script is not None:
        if (calculation_script.func_code.co_argcount==2 and
            calculation_script.func_code.co_varnames[:2]==('current_aggregated_amount_list',
                                                           'current_movement')):
          # backward compatibility
          tmp_movement = calculation_script(
              current_aggregated_amount_list=movement_list,
              current_movement=tmp_movement)
        elif calculation_script.func_code.co_argcount==3:
          # backward compatibility
          tmp_movement = calculation_script(
              current_aggregated_amount_list=movement_list,
              current_movement=tmp_movement,
              aggregated_movement_list=aggregated_movement_list)
        else:
          tmp_movement = calculation_script(
              current_aggregated_amount_list=movement_list,
              current_movement=tmp_movement,
              aggregated_movement_list=aggregated_movement_list,
              trade_model_line=self,
              **kw)
        if tmp_movement is None:
          # Do nothing
          return aggregated_amount_list
        if rounding:
          tmp_movement = rounding_proxy(
            tmp_movement, context=self)

      # check if slices are used
      salary_range_list = tmp_movement.getVariationCategoryList(
          base_category_list='salary_range') #XXX hardcoded values
      salary_range = len(salary_range_list) and salary_range_list[0] or None
      if salary_range is not None and calculation_script is None:
        # slice are used only if there is no script found, in case where a
        # script exist, slice should be handle in it
        model = context.getSpecialiseValue() # get the closest model from
                                             # the paysheet
        cell = model.getCell(salary_range)
        if cell is None:
          raise ValueError("Line '%s' (%s) can't find the cell corresponding"
              " to those cells coordinates : %s" % (self.getTitle(),
                                                    self.getRelativeUrl(),
                                                    salary_range))
        model_slice_min = cell.getQuantityRangeMin()
        model_slice_max = cell.getQuantityRangeMax()
        base_application = tmp_movement.getQuantity(0.0)
        if base_application <= model_slice_min:
          # if base_application is not in the slice range, quantity is 0
          tmp_movement.setQuantity(0)
        elif base_application-model_slice_min > 0:
          if base_application <= model_slice_max:
            tmp_movement.setQuantity(base_application-model_slice_min)
          elif model_slice_max:
            tmp_movement.setQuantity(model_slice_max-model_slice_min)

      if not update and modified:
        # no movements were updated, but something was modified, so new
        # movement appeared
        aggregated_amount_list.append(tmp_movement)

    return aggregated_amount_list

  def _isMatchedMovement(self, movement, base_application_list, tmp_movement):
    return (
      set(base_application_list).intersection(
      set(movement.getBaseContributionList())) and
      (len(movement.getVariationCategoryList()) == 0 or
       len(tmp_movement.getVariationCategoryList()) == 0 or
       set(movement.getVariationCategoryList()).intersection(
      set(tmp_movement.getVariationCategoryList()))
       )
      )
