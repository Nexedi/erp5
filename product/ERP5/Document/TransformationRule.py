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

from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5.Document.Rule import Rule
from Products.ERP5.Document.SimulationMovement import SimulationMovement
from Products.ERP5Type.Errors import TransformationRuleError

class TransformationMovementFactory:
  def __init__(self):
    self.default = None # base information to use for making movements
    self.produced_list = list()
    self.consumed_list = list()

  def requestProduced(self, **produced):
    self.produced_list.append(produced)

  def requestConsumed(self, **consumed):
    self.consumed_list.append(consumed)

  def _getCausalityList(self, causality=None, causality_value=None,
                        causality_list=None, causality_value_list=None,
                        **kw):
    if causality is not None:
      return [causality]
    elif causality_value is not None:
      return [causality_value.getRelativeUrl()]
    elif causality_list is not None:
      return causality_list
    elif causality_value_list is not None:
      return [causality_value.getRelativeUrl()
              for causality_value in causality_value_list]

  def getRequestList(self):
    _list = []
    for (request_list, sign) in ((self.produced_list, -1),
                            (self.consumed_list, 1)):
      for request in request_list:
        d = self.default.copy()
        d.update(request)
        d['quantity'] *= sign
        _list.append(d)
    return _list

  def makeMovements(self, applied_rule):
    """
    make movements under the applied_rule by requests
    """
    movement_dict = {}
    for movement in applied_rule.objectValues(
        portal_type="Simulation Movement"):
      key = tuple(sorted(movement.getCausalityList()))
      movement_dict[key] = movement

    """
    produced quantity should be represented by minus quantity on movement.
    because plus quantity is consumed.
    """ 
    for request in self.getRequestList():
      # get movement by causality
      key = tuple(sorted(self._getCausalityList(**request)))
      movement = movement_dict.get(key, None)
      # when no exist
      if movement is None:
        movement = applied_rule.newContent(portal_type="Simulation Movement")
      # update
      if movement.isFrozen():
        self.makeDifferentMovement(movement, **request)
      else:
        movement.edit(**request)

  def _requestNetQuantity(self, request):
    quantity = request.get('quantity', None)
    efficiency = request.get('efficiency', None)
    if efficiency in (0, 0.0, None, ''):
      efficiency = 1.0
    return float(quantity) / efficiency

  def makeDifferentMovement(self, movement, **request):
    """
    make different movement, which is based on original movement.
    this implementation just focus about quantity.
    """
    applied_rule = movement.getParentValue()
    request['quantity'] = self._requestNetQuantity(request)\
                          - movement.getNetQuantity()
    if request['quantity'] != 0:
      diff_movement = applied_rule.newContent(portal_type="Simulation Movement")
      diff_movement.edit(**request)


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

  __implements__ = ( interfaces.IPredicate,
                     interfaces.IRule )
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
                                      .getAggregatedAmountList()])
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

  def getFactory(self):
    return TransformationMovementFactory()

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
    factory = self.getFactory()
    factory.default = dict(
      resource=transformation.getResource(),
      quantity=parent_movement.getNetQuantity(),
      quantity_unit=parent_movement.getQuantityUnit(),
      variation_category_list=parent_movement.getVariationCategoryList(),
      variation_property_dict=parent_movement.getVariationPropertyDict(),)

    # consumed amounts are sorted by phase, but not ordered.
    amount_dict = {}
    for amount in transformation.getAggregatedAmountList():
      phase = amount.getTradePhase()

      if phase not in trade_phase_list:
        raise TransformationRuleError,\
              "Trade phase %r is not part of Business Process %r" % (phase, business_process)

      amount_dict.setdefault(phase, [])
      amount_dict[phase].append(amount)

    last_phase_path_list = list() # to keep phase_path_list
    last_prop_dict = dict()
    for (phase, amount_list) in amount_dict.items():
      phase_path_list = business_process.getPathValueList(phase)
      """
      XXX: In this context, we assume quantity as ratio,
      but this "quantity as ratio" is consistent with transformation.
      """
      if sum(map(lambda path: path.getQuantity(), phase_path_list)) != 1:
        raise TransformationRuleError,\
              "sum ratio of Trade Phase %r of Business Process %r is not one"\
              % (phase, business_process)

      for path in phase_path_list:
        start_date = path.getExpectedStartDate(explanation)
        stop_date = path.getExpectedStopDate(explanation)
        predecessor_remaining_phase_list = path.getPredecessorValue()\
          .getRemainingTradePhaseList(explanation,
                                      trade_phase_list=trade_phase_list)
        successor_remaining_phase_list = path.getSuccessorValue()\
          .getRemainingTradePhaseList(explanation,
                                      trade_phase_list=trade_phase_list)
        destination = path.getDestination()

        # checking which is not last path of transformation
        if len(successor_remaining_phase_list) != 0:
          # partial produced movement
          factory.requestProduced(
            causality_value=path,
            start_date=start_date,
            stop_date=stop_date,
            # when last path of transformation, path.getQuantity() will be return 1.
            quantity=factory.default['quantity'] * path.getQuantity(),
            destination=destination,
            #destination_section=???,
            trade_phase_value_list=successor_remaining_phase_list)
        else:
          # for making movement of last product of the transformation
          last_phase_path_list.append(path)

          # path params must be same
          if last_prop_dict.get('start_date', None) is None:
            last_prop_dict['start_date'] = start_date
          if last_prop_dict.get('stop_date', None) is None:
            last_prop_dict['stop_date'] = stop_date
          # trade phase of product is must be empty []
          if last_prop_dict.get('trade_phase_value_list', None) is None:
            last_prop_dict['trade_phase_value_list'] = successor_remaining_phase_list
          if last_prop_dict.get('destination', None) is None:
            last_prop_dict['destination'] = destination

          if last_prop_dict['start_date'] != start_date or\
             last_prop_dict['stop_date'] != stop_date or\
             last_prop_dict['trade_phase_value_list'] != successor_remaining_phase_list or\
             last_prop_dict['destination'] != destination:
            raise TransformationRuleError,\
              """Returned property is different on Transformation %r and Business Process %r"""\
              % (transformation, business_process)

        # when the path is part of production but not first, consume previous partial product
        if path not in head_production_path_list:
          factory.requestConsumed(
            causality_value=path,
            start_date=start_date,
            stop_date=stop_date,
            quantity=factory.default['quantity'] * path.getQuantity(),
            source=path.getSource(),
            #source_section=???,
            trade_phase_value_list=predecessor_remaining_phase_list)

        # consumed movement
        for amount in amount_list:
          factory.requestConsumed(
            causality_value=path,
            start_date=start_date,
            stop_date=stop_date,
            resource=amount.getResource(),
            quantity=factory.default['quantity'] * amount.getQuantity()\
              / amount.getEfficiency() * path.getQuantity(),
            quantity_unit=amount.getQuantityUnit(),
            source=path.getSource(),
            #source_section=???,
            trade_phase=path.getTradePhase())

    """
    valid graph for transformation
    a --- b --- c

    a --
        \
         X b
        /
    c --

    invalid graph
    a ------- b
    c ------- d

        -- b
       /
    a X
       \
        -- c
    """
    # when empty
    if last_phase_path_list is None or len(last_phase_path_list) == 0:
      raise TransformationRuleError,\
            """Could not make the product by Transformation %r and Business Process %r,
which last_phase_path_list is empty.""" % (transformation, business_process)

    factory.requestProduced(
      causality_value_list=last_phase_path_list,
      # when last path of transformation, path.getQuantity() will be return 1.
      quantity=factory.default['quantity'] * path.getQuantity(),
      #destination_section=???,
      **last_prop_dict)

    factory.makeMovements(applied_rule)
    Rule.expand(self, applied_rule, **kw)
