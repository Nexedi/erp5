# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Yusuke Muraoka <yusuke@nexedi.com>
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
from Products.ERP5.Document.Path import Path

import zope.interface

class BusinessPath(Path):
  """
    The BusinessPath class embeds all information related to 
    lead times and parties involved at a given phase of a business
    process.

    BusinessPath are also used as helper to build deliveries from
    buildable movements. Here is the typical code of an alarm
    in charge of the building process.

    The idea is to invoke isBuildable() on the collected simulation
    movements (which are orphan) during build "after select" process

      builder = portal_deliveries.default_order_builder
      for path in builder.getSpecialiseRelatedValueList() # or wharever category
        builder.build(causality_uid=path.getUid(),) # Select movemenents

      Pros: global select is possible by not providing a causality_uid
      Cons: global select retrieves long lists of orphan movements which 
              are not yet buildable
            the build process could be rather slow or require activities

    TODO:
      - finish build process implementation
  """
  meta_type = 'ERP5 Business Path'
  portal_type = 'Business Path'
  isPredicate = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Folder
                    , PropertySheet.Comment
                    , PropertySheet.Arrow
                    , PropertySheet.Chain
                    , PropertySheet.SortIndex
                    , PropertySheet.BusinessPath
                    )

  # Declarative interfaces
  zope.interface.implements(interfaces.ICategoryAccessProvider,
                            interfaces.IArrowBase,
                            interfaces.IBusinessPath,
                            interfaces.IBusinessBuildable,
                            interfaces.IBusinessCompletable
                            )

  # IArrowBase implementation
  security.declareProtected(Permissions.AccessContentsInformation, 'getSourceBaseCategoryList')
  def getSourceBaseCategoryList(self):
    """
      Returns all categories which are used to define the source
      of this Arrow
    """
    # Naive implementation - we must use category groups instead - XXX
    return ('source', 'source_section', 'source_payment', 'source_project',
        'source_administration', 'source_project', 'source_function',
        'source_payment', 'source_account')

  security.declareProtected(Permissions.AccessContentsInformation, 'getDestinationBaseCategoryList')
  def getDestinationBaseCategoryList(self):
    """
      Returns all categories which are used to define the destination
      of this Arrow
    """
    # Naive implementation - we must use category groups instead - XXX
    return ('destination', 'destination_section', 'destination_payment', 'destination_project',
        'destination_administration', 'destination_project', 'destination_function',
        'destination_payment', 'destination_account')

  # ICategoryAccessProvider overriden methods
  def _getCategoryMembershipList(self, category, **kw):
    """
      Overridden in order to take into account dynamic arrow categories in case if no static
      categories are set on Business Path
    """
    context = kw.pop('context')
    result = Path._getCategoryMembershipList(self, category, **kw)
    if len(result) > 0:
      return result
    if context is not None:
      dynamic_category_list = self._getDynamicCategoryList(context)
      dynamic_category_list = self._filterCategoryList(dynamic_category_list, category, **kw)
      result = dynamic_category_list
    return result

  def _getAcquiredCategoryMembershipList(self, category, **kw):
    """
      Overridden in order to take into account dynamic arrow categories in case if no static
      categories are set on Business Path
    """
    context = kw.pop('context', None)
    result = Path._getAcquiredCategoryMembershipList(self, category, **kw)
    if len(result) > 0:
      return result
    if context is not None:
      dynamic_category_list = self._getDynamicCategoryList(context)
      dynamic_category_list = self._filterCategoryList(dynamic_category_list, category, **kw)
      result = dynamic_category_list
    return result

  def _filterCategoryList(self, category_list, category, spec=(), filter=None, portal_type=(), base=0, 
                         keep_default=1, checked_permission=None):
    """
      XXX - implementation missing
      TBD - look at CategoryTool._buildFilter for inspiration
    """
    # basic filtering:
    #  * remove categories which base name is not category
    #  * respect base parameter
    prefix = category + '/'
    start_index = not base and len(prefix) or 0
    return [category[start_index:]
            for category in category_list
            if category.startswith(prefix)]

  # Dynamic context based categories
  def _getDynamicCategoryList(self, context):
    return self._getDynamicSourceCategoryList(context) \
         + self._getDynamicDestinationCategoryList(context)

  def _getDynamicSourceCategoryList(self, context):
    method_id = self.getSourceMethodId()
    if method_id:
      method = getattr(self, method_id)
      return method(context)
    return []

  def _getDynamicDestinationCategoryList(self, context):
    method_id = self.getDestinationMethodId()
    if method_id:
      method = getattr(self, method_id)
      return method(context)
    return []

  # IBusinessBuildable implementation
  def isBuildable(self, explanation):
    """
    """
    # check if there is at least one simulation movement which is not
    # delivered
    result = False
    if self.isCompleted(explanation) or self.isFrozen(explanation):
      return False # No need to build what was already built or frozen
    for simulation_movement in self.getRelatedSimulationMovementValueList(
        explanation):
      if simulation_movement.getDeliveryValue() is None:
        result = True
    predecessor = self.getPredecessorValue()
    if predecessor is None:
      return result
    if predecessor.isPartiallyCompleted(explanation):
      return result
    return False

  def isPartiallyBuildable(self, explanation):
    """
      Not sure if this will exist some day XXX
    """

  def _getExplanationUidList(self, explanation):
    """Helper method to fetch really explanation related movements"""
    explanation_uid_list = [explanation.getUid()]
    for found_explanation in explanation.getCausalityRelatedValueList(
        portal_type=self.getPortalDeliveryTypeList()):
      explanation_uid_list.extend(self._getExplanationUidList(
        found_explanation))
    return explanation_uid_list

  def build(self, explanation):
    """
      Build
    """
    builder_list = self.getDeliveryBuilderValueList() # Missing method
    for builder in builder_list:
      # chosen a way that builder is good enough to decide to select movements
      # which shall be really build (movement selection for build is builder
      # job, not business path job)
      builder.build(select_method_dict={
        'causality_uid': self.getUid(),
        'explanation_uid': self._getExplanationUidList(explanation)
      })

  # IBusinessCompletable implementation
  security.declareProtected(Permissions.AccessContentsInformation,
      'isCompleted')
  def isCompleted(self, explanation):
    """
      Looks at all simulation related movements
      and checks the simulation_state of the delivery
    """
    acceptable_state_list = self.getCompletedStateList()
    for movement in self.getRelatedSimulationMovementValueList(explanation):
      if movement.getSimulationState() not in acceptable_state_list:
        return False
    return True

  security.declareProtected(Permissions.AccessContentsInformation,
      'isPartiallyCompleted')
  def isPartiallyCompleted(self, explanation):
    """
      Looks at all simulation related movements
      and checks the simulation_state of the delivery
    """
    acceptable_state_list = self.getCompletedStateList()
    for movement in self.getRelatedSimulationMovementValueList(explanation):
      if movement.getSimulationState() in acceptable_state_list:
        return True
    return False

  security.declareProtected(Permissions.AccessContentsInformation,
      'isFrozen')
  def isFrozen(self, explanation):
    """
      Looks at all simulation related movements
      and checks if frozen
    """
    movement_list = self.getRelatedSimulationMovementValueList(explanation)
    if len(movement_list) == 0:
      return False # Nothing to be considered as Frozen
    for movement in movement_list:
      if not movement.isFrozen():
        return False
    return True

  def _recurseGetValueList(self, document, portal_type):
    """Helper method to recurse documents as deep as possible and returns
       list of document values matching portal_type"""
    return_list = []
    for subdocument in document.contentValues():
      if subdocument.getPortalType() == portal_type:
        return_list.append(subdocument)
      return_list.extend(self._recurseGetValueList(subdocument, portal_type))
    return return_list

  def isMovementRelatedWithMovement(self, movement_value_a, movement_value_b):
    """Documentation in IBusinessPath"""
    movement_a_path_list = movement_value_a.getRelativeUrl().split('/')
    movement_b_path_list = movement_value_b.getRelativeUrl().split('/')

    if len(movement_a_path_list) == len(movement_b_path_list):
      if movement_value_a == movement_value_b:
        # same is related
        return True
      # same level, cannot be related
      return False

    index = 0
    for movement_a_part in movement_a_path_list:
      try:
        movement_b_part = movement_b_path_list[index]
      except IndexError:
        # so far was good, they are related
        return True
      if movement_a_part != movement_b_part:
        return False
      index += 1
    # movement_a_path_list was shorter than movement_b_path_list and matched
    # so they are related
    return True

  def _isDeliverySimulationMovementRelated(self, delivery, simulation_movement):
    """Helper method, which checks if simulation_movement is BPM like related
       with delivery"""
    for delivery_simulation_movement in self \
        ._getDeliverySimulationMovementList(delivery):
      if self.isMovementRelatedWithMovement(delivery_simulation_movement,
          simulation_movement):
        return True
    return False

  def _getDeliverySimulationMovementList(self, delivery):
    """Returns list of simulation movements related to delivery by applied rule
       or delivery's movements"""
    movement_list = []
    for applied_rule in delivery.getCausalityRelatedValueList(
        portal_type='Applied Rule'):
      movement_list.extend(applied_rule.contentValues(
        portal_type='Simulation Movement'))
    for movement in delivery.getMovementList():
      movement_list.extend(movement.getDeliveryRelatedValueList(
        portal_type='Simulation Movement'))
    return movement_list

  # IBusinessPath implementation
  security.declareProtected(Permissions.AccessContentsInformation,
      'getRelatedSimulationMovementValueList')
  def getRelatedSimulationMovementValueList(self, explanation):
    """
      Returns recursively all Simulation Movements indirectly related to explanation and self

      As business sequence is not related to simulation tree need to built
      full simulation trees per applied rule
    """
    # FIXME: Needed better implementation, maybe use catalog?
    simulation_movement_value_list = []
    # first tree from root Applied Rules related to delivery itself
    for applied_rule in explanation.getCausalityRelatedValueList(
        portal_type='Applied Rule'):
      simulation_movement_value_list.extend(self._recurseGetValueList(
        applied_rule, 'Simulation Movement'))
    # now tree from root Applied Rules related to movements used to build delivery
    root_applied_rule_list = []
    for movement in explanation.getMovementList():
      for simulation_movement in movement.getDeliveryRelatedValueList(
          portal_type='Simulation Movement'):
        applied_rule = simulation_movement.getRootAppliedRule()
        if applied_rule not in root_applied_rule_list:
          root_applied_rule_list.append(
              simulation_movement.getRootAppliedRule())

    for applied_rule in root_applied_rule_list:
      simulation_movement_value_list.extend(self._recurseGetValueList(
        applied_rule, 'Simulation Movement'))

    return [simulation_movement.getObject() for simulation_movement
          in simulation_movement_value_list
          # this business path
          if simulation_movement.getCausalityValue() == self
          # related with explanation
          and self._isDeliverySimulationMovementRelated(
            explanation, simulation_movement)]

  def getExpectedStartDate(self, explanation, predecessor_date=None, *args, **kwargs):
    """
      Returns the expected start date for this
      path based on the explanation.

      predecessor_date -- if provided, computes the date base on the
                          date value provided
    """
    return self._getExpectedDate(explanation,
                                 self._getRootExplanationExpectedStartDate,
                                 self._getPredecessorExpectedStartDate,
                                 self._getSuccessorExpectedStartDate,
                                 predecessor_date=predecessor_date,
                                 *args, **kwargs)

  def _getRootExplanationExpectedStartDate(self, explanation, *args, **kwargs):
    if self.getParentValue().isStartDateReferential():
      return explanation.getStartDate()
    else:
      expected_date = self.getExpectedStopDate(explanation, *args, **kwargs)
      if expected_date is not None:
        return expected_date - self.getLeadTime()

  def _getPredecessorExpectedStartDate(self, explanation, predecessor_date=None, *args, **kwargs):
    if predecessor_date is None:
      node = self.getPredecessorValue()
      if node is not None:
        predecessor_date = node.getExpectedCompletionDate(explanation, *args, **kwargs)
    if predecessor_date is not None:
      return predecessor_date + self.getWaitTime()

  def _getSuccessorExpectedStartDate(self, explanation, *args, **kwargs):
    node = self.getSuccessorValue()
    if node is not None:
      expected_date =  node.getExpectedBeginningDate(explanation, *args, **kwargs)
      if expected_date is not None:
        return expected_date - self.getLeadTime()

  def getExpectedStopDate(self, explanation, predecessor_date=None, *args, **kwargs):
    """
      Returns the expected stop date for this
      path based on the explanation.

      predecessor_date -- if provided, computes the date base on the
                          date value provided
    """
    return self._getExpectedDate(explanation,
                                 self._getRootExplanationExpectedStopDate,
                                 self._getPredecessorExpectedStopDate,
                                 self._getSuccessorExpectedStopDate,
                                 predecessor_date=predecessor_date,
                                 *args, **kwargs)

  def _getRootExplanationExpectedStopDate(self, explanation, *args, **kwargs):
    if self.getParentValue().isStopDateReferential():
      return explanation.getStopDate()
    else:
      expected_date = self.getExpectedStartDate(explanation, *args, **kwargs)
      if expected_date is not None:
        return expected_date + self.getLeadTime()

  def _getPredecessorExpectedStopDate(self, explanation, *args, **kwargs):
    node = self.getPredecessorValue()
    if node is not None:
      expected_date = node.getExpectedCompletionDate(explanation, *args, **kwargs)
      if expected_date is not None:
        return expected_date + self.getWaitTime() + self.getLeadTime()

  def _getSuccessorExpectedStopDate(self, explanation, *args, **kwargs):
    node = self.getSuccessorValue()
    if node is not None:
      return node.getExpectedBeginningDate(explanation, *args, **kwargs)

  def _getExpectedDate(self, explanation, root_explanation_method,
                       predecessor_method, successor_method,
                       visited=None, *args, **kwargs):
    """
      Returns the expected stop date for this
      path based on the explanation.

      root_explanation_method -- used when the path is root explanation
      predecessor_method --- used to get expected date of side of predecessor
      successor_method --- used to get expected date of side of successor
      visited -- only used to prevent infinite recursion internally
    """
    if visited is None:
      visited = []

    # mark the path as visited
    if self not in visited:
      visited.append(self)

    if self.isDeliverable():
      return root_explanation_method(
        explanation, visited=visited, *args, **kwargs)

    predecessor_expected_date = predecessor_method(
      explanation, visited=visited, *args, **kwargs)

    successor_expected_date = successor_method(
      explanation, visited=visited, *args, **kwargs)

    if successor_expected_date is not None or \
       predecessor_expected_date is not None:
      # return minimum expected date but it is not None
      if successor_expected_date is None:
        return predecessor_expected_date
      elif predecessor_expected_date is None:
        return successor_expected_date
      else:
        if predecessor_expected_date < successor_expected_date:
          return predecessor_expected_date
        else:
          return successor_expected_date
