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
from Products.ERP5.AggregatedAmountList import AggregatedAmountList
import zope.interface

def isMovement(document):
  """Hides isMovement method or variable complexity"""
  if callable(document.isMovement):
    is_movement = document.isMovement()
  else:
    is_movement = document.isMovement
  return is_movement

class TradeModelLine(Predicate, XMLMatrix, Amount):
  """Trade Model Line is a way to represent trade transformation for movements"""
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
      model = context.getSpecialiseValue().getEffectiveModel()
      script_name = model.getCalculationScriptId()
    if script_name is None:
      return None
    script = getattr(context, script_name, None)
    if script is None:
      raise ValueError, "Unable to find `%s` calculation script" % \
                                                       script_name
    return script

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAggregatedAmountList')
  def getAggregatedAmountList(self, context, movement_list = None,
      current_aggregated_amount_list = None, base_id='movement', **kw):
    from Products.ERP5Type.Document import newTempSimulationMovement

    # test with predicate if this model line could be applied
    if not self.test(context):
      # This model_line should not be applied
      return []
    if movement_list is None:
      movement_list = []
    if current_aggregated_amount_list is None:
      current_aggregated_amount_list = []

    normal_resource_use_category_list = self.\
        portal_preferences.getPreferredNormalResourceUseCategoryList()
    if normal_resource_use_category_list is None:
      raise ValueError('preferred_normal_resource_use_category is not ' + \
          'configured in System Preferences')

    # if movement_list is passed as parameter, it shall be used,
    # otherwise it is needed to look up for movements
    if len(movement_list) == 0:
      # no movements passed, need to find some
      if isMovement(context):
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
          movement_resource = movement.getResourceValue()
          if movement_resource is not None:
            if movement_resource.getUse() in \
                normal_resource_use_category_list:
              movement_list.append(movement)

    aggregated_amount_list = AggregatedAmountList()
    base_application_list = self.getBaseApplicationList()

    self_id = self.getParentValue().getId() + '_' + self.getId()

    tmp_movement_list = [q for q in current_aggregated_amount_list \
        if q.getReference() == self.getReference()]
    if len(tmp_movement_list) > 0:
      update = 1
    else:
      # get source and destination using Business Process
      document = self.getParentValue()
      if getattr(document, 'findSpecialiseValueList', None) is None:
        # if parent don't have findSpecialiseValueList, this mean it's on the
        # specialise_value
        document = self.getParentValue().getSpecialiseValue()
      business_process_list = document.findSpecialiseValueList(\
          context=self, portal_type_list=['Business Process'])
      business_process = None
      property_dict = {}
      if len(business_process_list):
        # XXX currently, is too complicated to use more than
        # one Business Process, so the first (which is the nearest from the
        # delivery) is took
        business_process = business_process_list[0]
        business_path_list = business_process.getPathValueList(trade_phase=\
            self.getTradePhase())
        if len(business_path_list) > 1:
          raise NotImplementedError, 'For now, it can not support more '\
              'than one business_path with same trade_phase. '\
              '%s have same trade_phase' % repr(business_path_list)
        if len(business_path_list) == 1:
          business_path = business_path_list[0]
          property_dict={
            'source_value_list': business_path.getSourceValueList(context=context),
            'destination_value_list':
            business_path.getDestinationValueList(context=context),
            'source_section_value_list':
            business_path.getSourceSectionValueList(context=context),
            'destination_section_value_list':
            business_path.getDestinationSectionValueList(context=context),
            'source_decision_value_list':
            business_path.getSourceDecisionValueList(context=context),
            'source_administration_value_list':
            business_path.getSourceAdministrationValueList(context=context),
            'source_payment_value_list':
            business_path.getSourcePaymentValueList(context=context),
            'destination_decision_value_list':
            business_path.getDestinationDecisionValueList(context=context),
            'destination_administration_value_list':
            business_path.getDestinationAdministrationValueList(context=context),
            'destination_payment_value_list':
            business_path.getDestinationPaymentValueList(context=context)
          }

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
            raise ValueError("Line '%s' (%s) can't find the cell corresponding"+\
                " to those cells coordinates : %s" % (self.getTitle(),
                                                      self.getRelativeUrl(),
                                                      cell_coordinates))
          tmp_movement = newTempSimulationMovement(self.getPortalObject(),
              self_id)
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
        tmp_movement_list.append(tmp_movement)
    modified = 0
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
          if set(base_application_list)\
              .intersection(set(movement.getBaseContributionList())) and \
              (len(movement.getVariationCategoryList()) == 0 or \
               len(tmp_movement.getVariationCategoryList()) == 0 or \
              set(movement.getVariationCategoryList()).intersection( \
              set(tmp_movement.getVariationCategoryList()))):
            # at least one base application is in base contributions and
            # if the movement have no variation category, it's the same as
            # if he have all variation categories
            quantity = tmp_movement.getQuantity(0.0)
            modified = 1
            tmp_movement.setQuantity(quantity + movement.getTotalPrice())

      # if a calculation script is defined, use it
      calculation_script = self.getCalculationScript(context)
      if calculation_script is not None:
        tmp_movement = calculation_script(\
            current_aggregated_amount_list=movement_list,
            current_movement=tmp_movement)

      else:
        # if the quantity is defined, use it
        modified = 1
        if tmp_movement.getPrice() is None:
          # if price is not defined, it the same as 100 %
          tmp_movement.setPrice(1)

      # check if slices are used
      salary_range_list = tmp_movement.getVariationCategoryList(\
          base_category_list='salary_range') #XXX hardcoded values
      salary_range = len(salary_range_list) and salary_range_list[0] or None
      if salary_range is not None and calculation_script is None:
        # slice are used only if there is no script found, in case where a
        # script exist, slice should be handle in it
        model = self.getParentValue()
        cell = model.getCell(salary_range)
        if cell is None:
          raise ValueError("Line '%s' (%s) can't find the cell corresponding"+\
              " to those cells coordinates : %s" % (self.getTitle(),
                                                    self.getRelativeUlr(),
                                                    salary_range))
        model_slice_min = cell.getQuantityRangeMin()
        model_slice_max = cell.getQuantityRangeMax()
        base_application = tmp_movement.getQuantity(0.0)
        if base_application < model_slice_min:
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
