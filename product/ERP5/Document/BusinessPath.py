# -*- coding: shift_jis -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Yusuke Muraoka <yusuke@nexedi.com>
#                    Łukasz Nowak <luke@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
from Products.ERP5.Document.Predicate import Predicate
from Products.ERP5.ExplanationCache import _getExplanationCache

import zope.interface

from zLOG import LOG

class BusinessPath(Path, Predicate):
  """
    The BusinessPath class embeds all information related to
    lead times and parties involved at a given phase of a business
    process. BusinessPath are also the most common way to trigger
    the build deliveries from buildable movements.

    The idea is to invoke isBuildable() on the collected simulation
    movements (which are orphan) during build "after select" process

    Here is the typical code of an alarm in charge of the building process::

      builder = portal_deliveries.a_delivery_builder
      for business_path in builder.getDeliveryBuilderRelatedValueList():
        builder.build(causality_uid=business_path.getUid(),) # Select movements

      Pros: global select is possible by not providing a causality_uid
      Cons: global select retrieves long lists of orphan movements which
            are not yet buildable the build process could be rather
            slow or require activities

    TODO:
    - IArrowBase implementation has too many comments which need to be
      fixed
  """
  meta_type = 'ERP5 Business Path'
  portal_type = 'Business Path'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Folder
                    , PropertySheet.Reference
                    , PropertySheet.Comment
                    , PropertySheet.Arrow
                    , PropertySheet.Amount
                    , PropertySheet.Chain # XXX-JPS Why N
                    , PropertySheet.SortIndex
                    , PropertySheet.BusinessPath
                    , PropertySheet.FlowCapacity
                    , PropertySheet.Reference
                    , PropertySheet.PaymentCondition # XXX-JPS must be renames some day
                    )

  # Declarative interfaces
  zope.interface.implements(interfaces.ICategoryAccessProvider,
                            interfaces.IArrowBase,
                            interfaces.IBusinessPath,
                            interfaces.IPredicate,
                            )

  # Helper Methods
  def _getExplanationRelatedSimulationMovementValueList(self, explanation):
    explanation_cache = _getExplanationCache(explanation)
    return explanation_cache.getBusinessPathRelatedSimulationMovementValueList(self)

  # IArrowBase implementation
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSourceArrowBaseCategoryList')
  def getSourceArrowBaseCategoryList(self):
    """
      Returns all categories which are used to define the source
      of this Arrow
    """
    # Naive implementation - we must use category groups instead - XXX
    return ('source',
            'source_account',
            'source_administration',
            #'source_advice',
            'source_carrier',
            #'source_decision',
            'source_function',
            'source_payment',
            'source_project',
            #'source_referral',
            'source_section',
            #'source_trade',
            #'source_transport'
            )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDestinationArrowBaseCategoryList')
  def getDestinationArrowBaseCategoryList(self):
    """
      Returns all categories which are used to define the destination
      of this Arrow
    """
    # Naive implementation - we must use category groups instead - XXX-JPS review this later
    return ('destination',
            'destination_account',
            'destination_administration',
            #'destination_advice',
            #'destination_carrier',
            #'destination_decision',
            'destination_function',
            'destination_payment',
            'destination_project',
            #'destination_referral',
            'destination_section',
            #'destination_trade',
            #'destination_transport'
            )

  # XXX-JPS UNkonwn ?
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getArrowCategoryDict')
  def getArrowCategoryDict(self, context=None, **kw): # XXX-JPS do we need it in API ?
    result = {}
    dynamic_category_list = self._getDynamicCategoryList(context)
    for base_category in self.getSourceArrowBaseCategoryList() +\
            self.getDestinationArrowBaseCategoryList():
      category_url_list = Path._getAcquiredCategoryMembershipList(
        self, base_category, **kw)
      if len(category_url_list) == 0 and context is not None:
        category_url_list = self._filterCategoryList(dynamic_category_list,
                                                     base_category, **kw)
      if len(category_url_list) > 0:
        result[base_category] = category_url_list
    return result

  # ICategoryAccessProvider overridden methods
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

  def _filterCategoryList(self, category_list, category, spec=(),
                          filter=None, portal_type=(), base=0,
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

  # IBusinessPath implementation
  security.declareProtected(Permissions.AccessContentsInformation,
                                            'getMovementCompletionDate')
  def getMovementCompletionDate(self, movement):
    """Returns the date of completion of the movemnet 
    based on paremeters of the business path. This complete date can be
    the start date, the stop date, the date of a given workflow transition
    on the explaining delivery, etc.

    movement -- a Simulation Movement
    """
    method_id = self.getCompletionDateMethodId()
    method = getattr(movement, method_id) # We wish to raise if it does not exist
    return method()

  def getCompletionDate(self, explanation):
    """Returns the date of completion of business path in the
    context of the explanation. The completion date of the Business 
    Path is the max date of all simulation movements which are
    related to the Business Path and which are part of the explanation.

    explanation -- the Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree and a union 
                   business process.

    NOTE:
    It seems that current implementation makes sense mostly in the
    context of a root explanation.
    """
    date_list = []
    for movement in self._getExplanationRelatedSimulationMovementValueList(explanation):
      date_list.append(self.getMovementCompletionDate(movement))

    return max(date_list)
  
  security.declareProtected(Permissions.AccessContentsInformation,
                                            'getExpectedQuantity')
  def getExpectedQuantity(self, amount):
    """Returns the new quantity for the provided amount taking
    into account the efficiency or the quantity defined on the business path.
    This is used to implement payment conditions or splitting production
    over multiple path. The total of getExpectedQuantity for all business
    path which are applicable should never exceed the original quantity.
    The implementation of this validation is left to rules.
    """
    if self.getQuantity():
      return self.getQuantity()
    elif self.getEfficiency():
      return amount.getQuantity() * self.getEfficiency()
    else:
      return amount.getQuantity()

  security.declareProtected(Permissions.AccessContentsInformation,
      'isCompleted')
  def isCompleted(self, explanation):
    """returns True if all related simulation movements for this explanation
    document are in a simulation state which is considered as completed
    according to the configuration of the current business path.
    Completed means that it is possible to move to next step
    of Business Process. This method does not check however whether previous
    trade states of a given business process are completed or not.
    Use instead IBusinessPathProcess.isBusinessPathCompleted for this purpose.

    explanation -- the Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree and a union 
                   business process.

    NOTE: simulation movements can be completed (ex. in 'started' state) but
    not yet frozen (ex. in 'delivered' state).
    """
    acceptable_state_list = self.getCompletedStateList()
    for movement in self._getExplanationRelatedSimulationMovementValueList(
                                                                explanation):
      if movement.getSimulationState() not in acceptable_state_list:
        return False
    return True

  security.declareProtected(Permissions.AccessContentsInformation,
      'isPartiallyCompleted')
  def isPartiallyCompleted(self, explanation):
    """returns True if some related simulation movements for this explanation
    document are in a simulation state which is considered as completed
    according to the configuration of the current business path.
    Completed means that it is possible to move to next step
    of Business Process. This method does not check however whether previous
    trade states of a given business process are completed or not.
    Use instead IBusinessPathProcess.isBusinessPathCompleted for this purpose.

    explanation -- the Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree and a union 
                   business process.
    """
    acceptable_state_list = self.getCompletedStateList()
    for movement in self._getExplanationRelatedSimulationMovementValueList(
                                                                explanation):
      if movement.getSimulationState() in acceptable_state_list:
        return True
    return False

  security.declareProtected(Permissions.AccessContentsInformation, 'isFrozen')
  def isFrozen(self, explanation):
    """returns True if all related simulation movements for this explanation
    document are in a simulation state which is considered as frozen
    according to the configuration of the current business path.
    Frozen means that simulation movement cannot be modified.
    This method does not check however whether previous
    trade states of a given business process are completed or not.
    Use instead IBusinessPathProcess.isBusinessPathCompleted for this purpose.

    explanation -- the Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree and a union 
                   business process.

    NOTE: simulation movements can be frozen (ex. in 'stopped' state) but
    not yet completed (ex. in 'delivered' state).
    """
    acceptable_state_list = self.getFrozenStateList()
    movement_list = self._getExplanationRelatedSimulationMovementValueList(
                                                                explanation)
    if not movement_list:
      return False # Frozen is True only if some delivered movements exist
    for movement in movement_list:
      if movement.getDelivery() and movement.getSimulationState() not in acceptable_state_list: # XXX-JPS is it acceptable optimizatoin ?
        return False
    return True

  def isDelivered(self, explanation):
    """Returns True is all simulation movements related to this
    Business Path in the context of given explanation are built
    and related to a delivery through the 'delivery' category.

    explanation -- the Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree and a union 
                   business process.
    """
    for simulation_movement in self._getExplanationRelatedSimulationMovementValueList(
        explanation):
      if not simulation_movement.getDelivery():
        return False
    return True

  def build(self, explanation):
    """Builds all related movements in the simulation using the builders
    defined on the Business Path.

    explanation -- the Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree and a union 
                   business process.
    """
    builder_list = self.getDeliveryBuilderValueList()
    explanation_cache = _getExplanationCache(explanation)
    for builder in builder_list:
      # Call build on each builder
      # Provide 2 parameters: self and and explanation_cache
      builder.build(select_method_dict={
        'business_path': self,
        'explanation_cache': explanation_cache,
      })

  # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX GARBAGE FROM HERE - all code will be removed
  # _LEGACY_ prefix is used to make sure nobody will call methods

  def _LEGACY_getExpectedStartDate(self, explanation, predecessor_date=None, *args, **kwargs):
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

  def _LEGACY__getRootExplanationExpectedStartDate(self, explanation, *args, **kwargs):
    if self.getParentValue().isStartDateReferential():
      return explanation.getStartDate()
    else:
      expected_date = self.getExpectedStopDate(explanation, *args, **kwargs)
      if expected_date is not None:
        return expected_date - self.getLeadTime()

  def _LEGACY__getPredecessorExpectedStartDate(self, explanation, predecessor_date=None, *args, **kwargs):
    if predecessor_date is None:
      node = self.getPredecessorValue()
      if node is not None:
        predecessor_date = self.getParentValue().getExpectedStateCompletionDate(
          explanation, node, *args, **kwargs)
    if predecessor_date is not None:
      return predecessor_date + self.getWaitTime()

  def _LEGACY__getSuccessorExpectedStartDate(self, explanation, *args, **kwargs):
    node = self.getSuccessorValue()
    if node is not None:
      expected_date =  self.getParentValue().getExpectedStateBeginningDate(
        explanation, node, *args, **kwargs)
      if expected_date is not None:
        return expected_date - self.getLeadTime()

  def _LEGACY_getExpectedStopDate(self, explanation, predecessor_date=None, *args, **kwargs):
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

  def _LEGACY__getRootExplanationExpectedStopDate(self, explanation, *args, **kwargs):
    if self.getParentValue().isStopDateReferential():
      return explanation.getStopDate()
    else:
      expected_date = self.getExpectedStartDate(explanation, *args, **kwargs)
      if expected_date is not None:
        return expected_date + self.getLeadTime()

  def _LEGACY__getPredecessorExpectedStopDate(self, explanation, *args, **kwargs):
    node = self.getPredecessorValue()
    if node is not None:
      expected_date = self.getParentValue().getExpectedStateCompletionDate(
         explanation, node, *args, **kwargs)
      if expected_date is not None:
        return expected_date + self.getWaitTime() + self.getLeadTime()

  def _LEGACY__getSuccessorExpectedStopDate(self, explanation, *args, **kwargs):
    node = self.getSuccessorValue()
    if node is not None:
      return self.getParentValue().getExpectedStateBeginningDate(
         explanation, node, *args, **kwargs)

  def _LEGACY__getExpectedDate(self, explanation, root_explanation_method,
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



  def _LEGACY__recurseGetValueList(self, document, portal_type):
    """Helper method to recurse documents as deep as possible and returns
       list of document values matching portal_type"""
    return_list = []
    for subdocument in document.contentValues():
      if subdocument.getPortalType() == portal_type:
        return_list.append(subdocument)
      return_list.extend(self._recurseGetValueList(subdocument, portal_type))
    return return_list

  def _LEGACY__isMovementRelatedWithMovement(self, movement_value_a, movement_value_b): # XXX-JPS not in API
    """Checks if self is parent or children to movement_value

    This logic is Business Process specific for Simulation Movements, as
    sequence of Business Process is not related appearance of Simulation Tree

    movement_value_a, movement_value_b - movements to check relation between
    """
    movement_a_path = '%s/' % movement_value_a.getRelativeUrl()
    movement_b_path = '%s/' % movement_value_b.getRelativeUrl()

    if movement_a_path == movement_b_path or \
       movement_a_path.startswith(movement_b_path) or \
       movement_b_path.startswith(movement_a_path):
      return True
    return False

  def _LEGACY__isDeliverySimulationMovementRelated(self, simulation_movement,
                                           delivery_simulation_movement_list):
    """Helper method, which checks if simulation_movement is BPM like related
       with delivery"""
    for delivery_simulation_movement in delivery_simulation_movement_list:
      if self.isMovementRelatedWithMovement(delivery_simulation_movement,
          simulation_movement):
        return True
    return False

  # IBusinessPath implementation
  def _LEGACY__getRelatedSimulationMovementValueList(self, explanation): # XXX-JPS purpose ? NOT IN API
    """
      Returns recursively all Simulation Movements indirectly related to explanation and self

      As business sequence is not related to simulation tree need to built
      full simulation trees per applied rule
    """
    portal_catalog = self.getPortalObject().portal_catalog
    root_applied_rule_list = []

     
    if getattr(self, 'getMovementList', None) is None: # XXX-JPS temp hack
      return []

    delivery_simulation_movement_list = portal_catalog(
      delivery_uid=[x.getUid() for x in explanation.getMovementList()]) # XXX-JPS it seems explanation is not understood as it should - only the root

    for simulation_movement in delivery_simulation_movement_list:
      applied_rule = simulation_movement.getRootAppliedRule().getPath()
      if applied_rule not in root_applied_rule_list:
        root_applied_rule_list.append(applied_rule)

    simulation_movement_list = portal_catalog(
      portal_type='Simulation Movement', causality_uid=self.getUid(),
      path=['%s/%%' % x for x in root_applied_rule_list])

    return [simulation_movement.getObject() for simulation_movement
          in simulation_movement_list
          # related with explanation
          if self._isDeliverySimulationMovementRelated(
              simulation_movement, delivery_simulation_movement_list)]
