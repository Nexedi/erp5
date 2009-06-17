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

class MovementFactory:
  def getRequestList(self):
    """
    return the list of a request which to be used to apply movements
    """
    raise NotImplementedError, 'Must be implemented on each child'

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

  def makeMovements(self, applied_rule):
    """
    make movements under the applied_rule by requests
    """
    movement_dict = {}
    for movement in applied_rule.objectValues(
        portal_type="Simulation Movement"):
      key = tuple(sorted(movement.getCausalityList()))
      movement_dict[key] = movement

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


class TransformationModelMovementFactory(MovementFactory):
  def __init__(self):
    self.product = None # base information to use for making movements
    self.produced_list = list()
    self.consumed_list = list()

  def requestProduced(self, **produced):
    self.produced_list.append(produced)

  def requestConsumed(self, **consumed):
    self.consumed_list.append(consumed)

  def getRequestList(self):
    """
    return the list of a request which to be used to apply movements
    """
    _list = []
    """
    produced quantity should be represented by minus quantity on movement.
    because plus quantity is consumed.
    """ 
    for (request_list, sign) in ((self.produced_list, -1),
                                 (self.consumed_list, 1)):
      for request in request_list:
        d = self.product.copy()
        d.update(request)
        d['quantity'] *= sign
        _list.append(d)
    return _list


class TransformationModelRuleMixin(Base):
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
    # find the line of order recursively
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

  security.declareProtected(Permissions.View, 'getSpecialise')
  def getSpecialise(self, movement=None, applied_rule=None, portal_type_list=None):
    """
    Return a business process related to the root causality.
    """
    if portal_type_list is None:
      portal_type_list = self.getPortalBusinessProcessTypeList()

    explanation = self.getExplanation(movement=movement,
                                      applied_rule=applied_rule)
    if explanation is not None:
      specialise = explanation.getSpecialiseValue()
      business_process_type_list = self.getPortalBusinessProcessTypeList()
      # because trade condition can be specialised
      while specialise is not None and \
            hasattr(specialise, 'getSpecialiseValue') and \
            specialise.getPortalType() not in portal_type_list:
        specialise = specialise.getSpecialiseValue()
      return specialise

  security.declareProtected(Permissions.View, 'getExplanation')
  def getExplanation(self, movement=None, applied_rule=None):
    if applied_rule is not None:
      return applied_rule.getRootAppliedRule().getCausalityValue()
    else:
      return movement.getRootSimulationMovement()\
             .getOrderValue().getExplanationValue()

  def getHeadProductionPathValueList(self, transformation, business_process):
    """
    Return list of path which is head of transformation trade_phases
    """
    return business_process.getHeadPathValueList(
      set([amount.getTradePhase()
           for amount in transformation.getAggregatedAmountList()]))


class TransformationModelRule(TransformationModelRuleMixin, Rule):
  """
  """

  # CMF Type Definition
  meta_type = 'ERP5 Transformation Model Rule'
  portal_type = 'Transformation Model Rule'
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

  def getFactory(self):
    return TransformationModelMovementFactory()

  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, applied_rule, **kw):
    """
    """
    parent_movement = applied_rule.getParentValue()

    transformation = self.getTransformation(movement=parent_movement)
    business_process = self.getSpecialise(movement=parent_movement)
    explanation = self.getExplanation(movement=parent_movement)

    # get all trade_phase of the Business Process
    trade_phase_list = business_process.getTradePhaseList()

    # get head of production path from business process with trade_phase_list
    head_production_path_value_list = self.getHeadProductionPathValueList(transformation,
                                                                          business_process)
    # the factory which is to make simulation movements
    factory = self.getFactory()
    factory.product = dict(
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
              "the trade phase %r is not part of Business Process %r" % (phase, business_process)
      amount_dict.setdefault(phase, [])
      amount_dict[phase].append(amount)

    last_phase_path_list = list() # to keep phase_path_list
    last_prop_dict = dict()
    for (phase, amount_list) in amount_dict.items():
      phase_path_value_list = business_process.getPathValueList(phase)
      """
      XXX: In this context, we assume quantity as ratio,
           but this "quantity as ratio" is consistent with transformation.
      """
      if sum(map(lambda path: path.getQuantity(), phase_path_value_list)) != 1:
        raise TransformationRuleError,\
              "the sum ratio at the Trade Phase %r on the Business Process %r is not 1"\
              % (phase, business_process)

      for path in phase_path_value_list:
        path_common_dict = dict(causality_value=path,
                                start_date=path.getExpectedStartDate(explanation),
                                stop_date=path.getExpectedStopDate(explanation))

        # the quantity which is produced/consumed at the path.
        quantity = factory.product['quantity'] * path.getQuantity()

        # nodes at the path
        source_section = path.getSourceSection(explanation)
        destination_section = path.getDestinationSection(explanation)
        source = path.getSource(explanation)
        destination = path.getDestination(explanation)

        # the remaining at the start and the end on the path
        predecessor_remaining_phase_list = path.getPredecessorValue()\
          .getRemainingTradePhaseList(explanation,
                                      trade_phase_list=trade_phase_list)
        successor_remaining_phase_list = path.getSuccessorValue()\
          .getRemainingTradePhaseList(explanation,
                                      trade_phase_list=trade_phase_list)
 
        consumed_common_dict = dict(source_section=source_section,
                                    destination_section=destination_section,
                                    source=source,
                                    **path_common_dict)

        produced_common_dict = dict(source_section=source_section,
                                    destination_section=destination_section,
                                    destination=destination,
                                    trade_phase_value_list=successor_remaining_phase_list,
                                    **path_common_dict)

        # when the path is not a part in the last phase on the transformation.
        if len(successor_remaining_phase_list) != 0:
          # partial produced movement
          factory.requestProduced(
            quantity=quantity,
            **produced_common_dict)
        else:
          last_phase_path_list.append(path)

          # used for matching
          work_dict = dict(filter(lambda x: x[0] != 'causality_value',
                                  produced_common_dict.items()))

          # when empty
          if not last_prop_dict:
            last_prop_dict.update(work_dict)

          # must be same, because the path(s) are integrated in the last phase on the transformation.
          if last_prop_dict != work_dict:
            raise TransformationRuleError,\
                  """the Properties which is used to make a movement on the last path
are different with the Transformation %r and the Business Process %r"""\
              % (transformation, business_process)

        # when the path is part of production, but not first, consume previous partial product
        if path not in head_production_path_value_list:
          factory.requestConsumed(
            quantity=quantity,
            trade_phase_value_list=predecessor_remaining_phase_list,
            **consumed_common_dict)

        # consumed movement
        for amount in amount_list:
          factory.requestConsumed(
            resource=amount.getResource(),
            quantity=quantity * amount.getQuantity() / amount.getEfficiency(),
            quantity_unit=amount.getQuantityUnit(),
            trade_phase=path.getTradePhase(),
            **consumed_common_dict)

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
            """could not make the product with the Transformation %r on the Business Process %r,
because last_phase_path_list is empty.""" % (transformation, business_process)

    factory.requestProduced(
      causality_value_list=last_phase_path_list,
      # in the last phase of transformation, produced quantity must be planned as same as ordered.
      quantity=factory.product['quantity'],
      **last_prop_dict)

    # make actual simulation movements
    factory.makeMovements(applied_rule)

    Rule.expand(self, applied_rule, **kw)

  # Deliverability / orderability
  def isDeliverable(self, m):
    return 1
  def isOrderable(self, m):
    return 0
