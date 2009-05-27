##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Yusuke Muraoka <yusuke@nexedi.com>
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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo

from Products.CMFCore.PortalFolder import ContentFilter
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Path import Path

import zope.interface

class BusinessPath(Path):
  """
    The BusinessPath class embeds all information related to 
    lead times and parties involved at a give phase of a business
    process.

    BusinessPath are also used as helper to build buildable movements.
    Here is the typical code of an alarm:
   
    Approach 1: explanation per explanation
      builder = portal_deliveries.default_order_builder
      for path in builder.getSpecialiseRelatedValueList() # or wharever category
        for explanation in portal_catalog(buildable=1, portal_type='Order'):
          path.build(explanation)

      Pros: easy explanation based approach
      Cons: buildable column added in delivery table
            reexpand of a finished order might generate remaining buildable

    Approach 2: isBuildable is indexed for SimulationMovements
      isBuildable() method is added to SimulationMovement

      Pros: global select is possible
      Cons: reindex of simulation is required
            slow indexing

    Approach 3: isBuildable is invoked during build "after select" process
      builder = portal_deliveries.default_order_builder
      for path in builder.getSpecialiseRelatedValueList() # or wharever category
        builder.build(causality_uid=path.getUid(),) # Select movemenents

      Pros: global select is possible
      Cons: global select retrieves long lists
            slow build

     Method 3 is best
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
                    , PropertySheet.BusinessPath
                    )

  # Declarative interfaces
  zope.interface.implements(Interface.ICategoryAccessProvider,
                            Interface.IArrow)

  # IBusinessPath Interface
  security.declareProtected(Permissions.AccessContentsInformation, 'getSourceBaseCategoryList')
  def getSourceBaseCategoryList(self):
    """
      Returns all categories which are used to define the source
      of this Arrow
    """
    # Naive implementation - we must use category groups instead
    return ('source', 'source_section', 'source_payment', 'source_project', )

  security.declareProtected(Permissions.AccessContentsInformation, 'getDestinationBaseCategoryList')
  def getDestinationBaseCategoryList(self):
    """
      Returns all categories which are used to define the destination
      of this Arrow
    """
    # Naive implementation - we must use category groups instead
    return ('destination', 'destination_section', 'destination_payment', 'destination_project', )

  # ICategoryAccessProvider overriden methods
  def _getCategoryMembershipList(self, category, **kw):
    """
      Overriden in order to take into account dynamic arrow
      categories
    """
    context = kw.get('context')
    result = Path._getCategoryMembershipList(self, category, **kw)
    if context is not None:
      dynamic_category_list = self._getDynamicCategoryList(context)
      dynamic_category_list= self._filterCategoryList(dynamic_category_list, category, **kw)
      # TODO: static categories should have priority over dynamic categories
      result = dynamic_category_list + result
    return result

  def _getAcquiredCategoryMembershipList(self, category, **kw):
    """
      Overriden in order to take into account dynamic arrow
      categories
    """
    context = kw.pop('context', None)
    result = Path._getAcquiredCategoryMembershipList(self, category, **kw)
    if context is not None:
      dynamic_category_list = self._getDynamicCategoryList(context)
      dynamic_category_list= self._filterCategoryList(dynamic_category_list, category, **kw)
      # TODO: static categories should have priority over dynamic categories
      result = dynamic_category_list + result
    return result

  def _filterCategoryList(self, category_list, category, spec=(), filter=None, portal_type=(), base=0, 
                         keep_default=1, checked_permission=None):
    """
      XXX - implementation missing
      TBD - look at CategoryTool._buildFilter for inspiration
    """
    return category_list

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

  # Core API
  def isBuildable(self, explanation):
    """
    """
    if self.isCompleted(explanation):
      return False # No need to build what was already built
    if self.isFrozen(explanation):
      return False # No need to build what is frozen
    predecessor = self.getPredecessorValue()
    if predecessor is None:
      return True # No predecessor, let's build
    if predecessor.isCompleted(explanation):
      return True
    return False

  def isPartiallyBuildable(self, explanation):
    """
      Not sure if this will exist some day XXX
    """

  def _getRelatedSimulationMovementList(self, explanation):
    """
      
    """
    return self.getCausalityRelatedValueList(portal_type='Simulation Movement',
                                             explanation_uid=explanation.getUid())

  def isCompleted(self, explanation):
    """
      Looks at all simulation related movements
      and checks the simulation_state of the delivery
    """
    acceptable_state_list = self.getCompletedStateList()
    for movement in self._getRelatedSimulationMovementList(explanation):
      if movement.getSimulationState() not in acceptable_state_list:
        return False
    return True

  def isPartiallyCompleted(self, explanation):
    """
      Looks at all simulation related movements
      and checks the simulation_state of the delivery
    """
    acceptable_state_list = self.getCompletedStateList()
    for movement in self._getRelatedSimulationMovementList(explanation):
      if movement.getSimulationState() in acceptable_state_list:
        return True
    return False

  def isFrozen(self, explanation):
    """
      Looks at all simulation related movements
      and checks if frozen
    """
    movement_list = self._getRelatedSimulationMovementList(explanation)
    if len(movement_list) == 0:
      return False # Nothing to be considered as Frozen
    for movement in movement_list:
      if not movement.isFrozen():
        return False
    return True

  def build(self, explanation):
    """
      Build
    """
    builder_list = self.getBuilderList() # Missing method
    for builder in builder_list:
      builder.build(causality_uid=self.getUid()) # This is one way of doing
      builder.build(movement_relative_url_list=
        self._getRelatedSimulationMovementList(explanation)) # Another way

  # Date calculation
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
