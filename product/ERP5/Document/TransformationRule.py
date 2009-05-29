# -*- coding:utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SARL and Contributors. All Rights Reserved.
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

from ExtensionClass import Base
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Rule import Rule
from Products.ERP5.Document.SimulationMovement import SimulationMovement
from Products.ERP5Type.Errors import TransformationRuleError

class TransformationRuleMixin(Base):
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.View, 'getTransformation')
  def getTransformation(self, movement=None, applied_rule=None):
    """
    Return transformation related to used by the applied rule.
    """
    if movement is None and applied_rule is not None:
      movement = applied_rule.getParentValue()

    order_movement = movement.getRootSimulationMovement().getOrderValue()
    explanation = self.getExplanation(movement=movement,
                                      applied_rule=applied_rule)
    # find line recursively
    order_line = order_movement
    while order_line.getParentValue() != explanation:
      order_line = order_line.getParentValue()

    script = order_line._getTypeBasedMethod('_getTransformation')
    if script is not None:
      transformation = script()
    else:
      line_transformation = order_line.objectValues(
        portal_type=self.getPortalTransformationTypeList())
      if len(line_transformation) == 1:
        transformation = line_transformation[0]
      else:
        transformation = order_line.getSpecialiseValue(
          portal_type=self.getPortalTransformationTypeList())

    if transformation.getResource() == movement.getResource():
      return transformation

  security.declareProtected(Permissions.View, 'getBusinessProcess')
  def getBusinessProcess(self, **kwargs):
    """
    Return business process related to root causality.
    """
    explanation = self.getExplanation(**kwargs)
    if explanation is not None:
      specialise = explanation.getSpecialiseValue()
      business_process_type_list = self.getPortalBusinessProcessTypeList()
      # because trade condition can be specialised
      while specialise is not None and \
            specialise.getPortalType() not in business_process_type_list:
        specialise = specialise.getSpecialiseValue()
      return specialise

  security.declareProtected(Permissions.View, 'getRootExplanation')
  def getRootExplanation(self, business_process):
    """
    the method of ProductionOrderRule returns most tail path of business process
    """
    if business_process is not None:
      for business_path in business_process.contentValues(
        portal_type=self.getPortalBusinessPathTypeList()):
        if business_path.isDeliverable():
          return business_path

  security.declareProtected(Permissions.View, 'getExplanation')
  def getExplanation(self, movement=None, applied_rule=None):
    if applied_rule is not None:
      return applied_rule.getRootAppliedRule().getCausalityValue()
    else:
      return movement.getRootSimulationMovement()\
             .getOrderValue().getExplanationValue()


class TransformationRule(TransformationRuleMixin, Rule):
  """
  """

  # CMF Type Definition
  meta_type = 'ERP5 Transformation Rule'
  portal_type = 'Transformation Rule'
  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  __implements__ = ( Interface.Predicate,
                     Interface.Rule )
  # Default Properties
  property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Task
                      )

  def getHeadProductionPathList(self, transformation, business_process):
    """
    Return list of path which is head of transformation trade_phases

    this method assumes trade_phase of head paths is only one
    """
    production_trade_phase_set = set([amount.getTradePhase()
                                      for amount in transformation\
                                      .objectValues(portal_type='Transformation Transformed Resource')])
    head_path_list = []
    for state in business_process.objectValues(
      portal_type=self.getPortalBusinessStateTypeList()):
      if len(state.getSuccessorRelatedValueList()) == 0:
        head_path_list.extend(state.getPredecessorRelatedValueList())

    result_list = []
    for path in head_path_list:
      result_list += self._getHeadPathByTradePhaseList(path, production_trade_phase_set)

    return map(lambda t: t[0], filter(lambda t: t != (None, None), result_list))

  def _getHeadPathByTradePhaseList(self, path, trade_phase_set):
    _set = set(path.getTradePhaseList())
    if _set & trade_phase_set:
      return [(path, _set & trade_phase_set)]

    successor_node = path.getSuccessorValue()
    if successor_node is None:
      return [(None, None)]

    _list = []
    for next_path in successor_node.getPredecessorRelatedValueList():
      _list += self._getHeadPathByTradePhaseList(next_path, trade_phase_set)
    return _list

  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, applied_rule, **kw):
    """
    """

    parent_movement = applied_rule.getParentValue()

    transformation = self.getTransformation(movement=parent_movement)
    business_process = self.getBusinessProcess(movement=parent_movement)
    explanation = self.getExplanation(movement=parent_movement)

    # get all trade_phase of the Business Process
    trade_phase_list = business_process.getTradePhaseList()

    # get head of production path from business process with trade_phase_list
    head_production_path_list = self.getHeadProductionPathList(transformation,
                                                               business_process)

    product_resource = transformation.getResource()
    product_quantity = parent_movement.getNetQuantity()
    product_quantity_unit = parent_movement.getQuantityUnit()
    product_variation_category_list = parent_movement.getVariationCategoryList()
    product_variation_property_dict = parent_movement.getVariationPropertyDict()

    amount_dict = {}
    # XXX Transformation.getAggregatedAmountList is useless, it can not have trade_phase, because Amout.
    for amount in transformation.objectValues(portal_type='Transformation Transformed Resource'):
      phase = amount.getTradePhase()
      amount_dict.setdefault(phase, [])
      amount_dict[phase].append(amount)

    product_destination = None
    for (phase, amount_list) in amount_dict.items():
      if phase not in trade_phase_list:
        raise TransformationRuleError,\
              "Trade phase %r is not part of Business Process %r" % (phase, business_process)

      phase_path_list = business_process.getPathValueList(phase)
      """
      XXX: In this context, we assume quantity as ratio,
      but this notion is consistent with transformation.
      """
      if sum(map(lambda path: path.getQuantity(), phase_path_list)) != 1:
        raise TransformationRuleError,\
              "sum ratio of Trade Phase %r of Business Process %r is not one" % (phase, business_process)

      for path in phase_path_list:
        start_date = path.getExpectedStartDate(explanation)
        stop_date = path.getExpectedStopDate(explanation)
        predecessor_remaining_phase_list = path.getPredecessorValue()\
                                           .getRemainingTradePhaseList(explanation,
                                                                       trade_phase_list=trade_phase_list)
        successor_remaining_phase_list = path.getSuccessorValue()\
                                         .getRemainingTradePhaseList(explanation,
                                                                     trade_phase_list=trade_phase_list)
        if len(successor_remaining_trade_phase_list) == 0:
          """
            Destinations of last paths for transformation must be same,
            because paths for transformation must be integrated finally,

            valid graph
            a --
                \--
                   X- b
                /--
            c --

            invalid graph
            a ------- b

            c ------- d
          """
          if product_destination is None:
            product_destination = path.getDestination()
          if product_destination != path.getDestination():
            raise TransformationRuleError,\
                  "Transformation %r is not integrated on Business Process %r" % (transformation, business_process)
        else:
          # partial product movement
          movement = applied_rule.newContent(portal_type="Simulation Movement")
          movement.edit(causality_value=path,
                        start_date=path.getExpectedStartDate(explanation),
                        stop_date=path.getExpectedStopDate(explanation),
                        resource=product_resource,
                        quantity=-(product_quantity * path.getQuantity()),
                        quantity_unit=product_quantity_unit,
                        variation_category_list=product_variation_category_list,
                        variation_property_dict=product_variation_property_dict,
                        destination=path.getDestination(),
                        #destination_section=???,
                        trade_phase_value_list=successor_remaining_trade_phase_list)

        # when the path is part of production but not first, consume previous partial product
        if path not in head_production_path_list:
          # consumed partial product movement
          movement = applied_rule.newContent(portal_type="Simulation Movement")
          movement.edit(causality_value=path,
                        start_date=start_date,
                        stop_date=stop_date,
                        resource=product_resource,
                        quantity=product_quantity * path.getQuantity(),
                        quantity_unit=product_quantity_unit,
                        variation_category_list=product_variation_category_list,
                        variation_property_dict=product_variation_property_dict,
                        source=path.getSource(),
                        #source_section=???,
                        trade_phase_value_list=predecessor_remaining_trade_phase_list)

        # consumption movement
        for amount in amount_list:
          consumed_resource = amount.getResource()
          consumed_quantity = product_quantity * amount.getQuantity() / amount.getEfficiency()
          consumed_quantity_unit = amount.getQuantityUnit()

          # consume resource
          movement = applied_rule.newContent(portal_type="Simulation Movement")
          movement.edit(causality_value=path,
                        start_date=start_date,
                        stop_date=stop_date,
                        resource=consumed_resource,
                        quantity=consumed_quantity * path.getQuantity(),
                        quantity_unit=consumed_quantity_unit,
                        source=path.getSource(),
                        #source_section=???,
                        trade_phase=path.getTradePhase())

    # product movement
    movement = applied_rule.newContent(portal_type="Simulation Movement")
    movement.edit(start_date=path.getExpectedStartDate(explanation),
                  stop_date=path.getExpectedStopDate(explanation),
                  resource=product_resource,
                  quantity=-(product_quantity),
                  quantity_unit=product_quantity_unit,
                  variation_category_list=product_variation_category_list,
                  variation_property_dict=product_variation_property_dict,
                  destination=product_destination,
                  #destination_section=???,
                  )

    Rule.expand(self, applied_rule, **kw)
