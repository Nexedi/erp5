# -*- coding: utf-8 -*-
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

import zope.interface

class BusinessPath(Path, Predicate):
  """
    The BusinessPath class embeds all information related to
    lead times and parties involved at a given phase of a business
    process.

    BusinessPath are also used as helper to build deliveries from
    buildable movements.

    The idea is to invoke isBuildable() on the collected simulation
    movements (which are orphan) during build "after select" process

    Here is the typical code of an alarm in charge of the building process::

      builder = portal_deliveries.a_delivery_builder
      for business_path in builder.getDeliveryBuilderRelatedValueList():
        builder.build(causality_uid=business_path.getUid(),) # Select movements

      Pros: global select is possible by not providing a causality_uid
      Cons: global select retrieves long lists of orphan movements which
              are not yet buildable
            the build process could be rather slow or require activities

    TODO:
      - merge build implementation from erp5_bpm business template to ERP5
        product code with backward compatibility
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
                    , PropertySheet.Comment
                    , PropertySheet.Arrow
                    , PropertySheet.Chain
                    , PropertySheet.SortIndex
                    , PropertySheet.BusinessPath
                    , PropertySheet.Reference
                    )

  # Declarative interfaces
  zope.interface.implements(interfaces.ICategoryAccessProvider,
                            interfaces.IArrowBase,
                            interfaces.IBusinessPath,
                            interfaces.IBusinessBuildable,
                            interfaces.IBusinessCompletable,
                            interfaces.IPredicate,
                            )

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
            #'source_carrier',
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
    # Naive implementation - we must use category groups instead - XXX
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

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getArrowCategoryDict')
  def getArrowCategoryDict(self, context=None, **kw):
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

  # IBusinessBuildable implementation
  def isBuildable(self, explanation):
    """
    """
    if self.isCompleted(explanation) or self.isFrozen(explanation):
      return False # No need to build what was already built or frozen

    # check if there is at least one simulation movement which is not
    # delivered
    for simulation_movement in self.getRelatedSimulationMovementValueList(
        explanation):
      if simulation_movement.getDeliveryValue() is None:
        break
    else:
      # if all simulation movements are delivered, we can bail out
      return False

    predecessor = self.getPredecessorValue()
    if predecessor is None:
      return True
    # XXX FIXME TODO
    # For now isPartiallyCompleted is used, as it was
    # assumed to not implement isPartiallyBuildable, so in reality
    # isBuildable is implemented like isPartiallyBuildable
    #
    # But in some cases it might be needed to implement
    # isPartiallyBuildable, than isCompleted have to be used here
    #
    # Such cases are Business Processes using sequence not related
    # to simulation tree with much of compensations
    return predecessor.isPartiallyCompleted(explanation)

  def isPartiallyBuildable(self, explanation):
    """
      Not sure if this will exist some day XXX
    """

  def _getExplanationUidList(self, explanation):
    """Helper method to fetch really explanation related movements"""
    explanation_uid_list = [explanation.getUid()]
    # XXX: getCausalityRelatedValueList is oversimplification, assumes
    #      that documents are sequenced like simulation movements, which
    #      is wrong
    for found_explanation in explanation.getCausalityRelatedValueList(
        portal_type=self.getPortalDeliveryTypeList()) + \
        explanation.getCausalityValueList():
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

  def _isDeliverySimulationMovementRelated(self, simulation_movement,
                                           delivery_simulation_movement_list):
    """Helper method, which checks if simulation_movement is BPM like related
       with delivery"""
    for delivery_simulation_movement in delivery_simulation_movement_list:
      if self.isMovementRelatedWithMovement(delivery_simulation_movement,
          simulation_movement):
        return True
    return False

  # IBusinessPath implementation
  security.declareProtected(Permissions.AccessContentsInformation,
      'getRelatedSimulationMovementValueList')
  def getRelatedSimulationMovementValueList(self, explanation):
    """
      Returns recursively all Simulation Movements indirectly related to explanation and self

      As business sequence is not related to simulation tree need to built
      full simulation trees per applied rule
    """
    portal_catalog = self.getPortalObject().portal_catalog

    delivery_simulation_movement_list = portal_catalog(
      delivery_uid=[x.getUid() for x in explanation.getMovementList()])

    related_list = self.getBusinessPathClosure(delivery_simulation_movement_list)

    self_url = self.getRelativeUrl()
    return [m for m in related_list if m.getCausality() == self_url]

  def getBusinessPathClosure(self, movement_list):
    """
    Returns a list of Simulation Movement that are related to
    movement_list.
    "related" means that each of the returned Movement
    will be an ancestor or a descendant of a movement in movement_list

    Formally, this method returns all Simulation Movements in:
       ancestors(movement_list) U descendants(movement_list)
    """
    # We need to find all ancestors of movement_list, as well as all
    # of its descendants.
    # When A is an ancestor of B we have:
    #   ancestors(B) > ancestors(A) and
    # and
    #   descendants(A) > descendants(B)
    # In this sense it only makes sense to compute descendants of A
    # and ancestors of B.
    #
    # To do this we construct a tree of all (physical) paths leading
    # to each movement in movement_list. This tree can be seen
    # as a subtree of the whole Simulation Tree, or as a coloration
    # of the Simulation Tree.
    # Then, for each tree leaf, if that leaf has an non-root ancestor,
    # we remove the leaf and only keep the ancestor:
    # Because of the above properties,
    #   closure({leaf, ancestor}) == closure({ancestor})
    # which ensures that at the end of the coloration,
    #   closure(colored_tree) == closure(movement_list)
    colored_tree_dict = dict()

    leaf_marker = object()
    for simulation_movement in movement_list:
      # remove portal_simulation from the path
      component_list = simulation_movement.getRelativeUrl().split("/")[1:]

      cur = colored_tree_dict
      for component in component_list[:-1]:
        cur = cur.setdefault(component, {})
        if cur == leaf_marker:
          # an ancestor of simulation_movement was colored before
          break
      else:
        # note that we remove possibly-colored-before descendants
        cur[component_list[-1]] = leaf_marker

    related_list = []
    def closure(root, path_item_tree):
      """
      recursive helper filling related_list with:
        nodes(tree) U descendants(leafs(tree))

      root is a zodb object where the path_item_tree should be rooted.
      """
      for k, v in path_item_tree.iteritems():
        cur = root[k]
        # XXX maybe using parity Applied Rule / Simulation Movement is enough?
        if cur.getPortalType() == 'Simulation Movement':
          related_list.append(cur)
        if v == leaf_marker:
          related_list.extend(self._recurseGetValueList(cur, 'Simulation Movement'))
        else:
          closure(cur, v)
    closure(self.getPortalObject().portal_simulation, colored_tree_dict)
    return related_list

  def getExpectedQuantity(self, explanation, *args, **kwargs):
    """
      Returns the expected stop date for this
      path based on the explanation.

      XXX predecessor_quantity argument is required?
    """
    if self.getQuantity():
      return self.getQuantity()
    elif self.getEfficiency():
      return explanation.getQuantity() * self.getEfficiency()
    else:
      return explanation.getQuantity()

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

  security.declareProtected(Permissions.AccessContentsInformation,
      'getBuildableMovementList')
  def getBuildableMovementList(self, **sql_kw):
    """
    Query catalog to find a list of movements related to this Business Path.

    Filter the results to return only Buildable Movements

    To specialize your builder, you can pass along SQL keywords
    in sql_kw, for instance:
      search_kw = {}
      search_kw['movement.quantity'] = {'query':0, 'range':'neq'}
      search_kw['movement.price'] = {'query':0, 'range':'neq'}
      sql_kw = portal_catalog.buildSQLQuery(**search_kw)
    """
    all_movement_list = self.BusinessPath_zSelectMovement(
                          business_path_uid=self.getUid(),
                          **sql_kw)

    # select method should return only non-delivered movements, but
    # maybe movements have been built in the meantime & catalog wasnt updated?
    non_delivered_movement_list = filter(lambda x:x.getDeliveryValue() is None,
                                         all_movement_list)

    return self.filterBuildableMovementList(non_delivered_movement_list)

  security.declareProtected(Permissions.AccessContentsInformation,
      'filterBuildableMovementList')
  def filterBuildableMovementList(self, non_delivered_movement_list):
    """
    Given a list of non delivered movements that all have "self" as
    a causality value, return the ones that are buildables

    This is computed efficiently: movements are first separated into
    distinct closures, and then filtering is made on each closure.
    """
    predecessor_state = self.getPredecessorValue()
    if predecessor_state is None:
      # first Path in Process, all movements can be built
      return non_delivered_movement_list

    predecessor_to_state_dict = {}
    for pred in predecessor_state.getSuccessorRelatedValueList():
      predecessor_to_state_dict[pred] = frozenset(pred.getCompletedStateList())

    root_dict = {}
    # classify movements according to Root Applied Rules so we can look at
    # them closure per closure
    for movement in non_delivered_movement_list:
      root_dict.setdefault(movement.getRootAppliedRule(), []).append(movement)

    result = []
    # for each root applied rule, get buildable Movements
    for root_rule, movement_list in root_dict.iteritems():
      result.extend(self._filterBuildableInSameClosure(movement_list,
                                          predecessor_to_state_dict))
    return result



  def _filterBuildableInSameClosure(self, movement_list, predecessor_to_state_dict):
    """
    Return the buildable movements in movement_list.

    It is about finding in the tree the movements that have causalities in
    predecessor_to_state_dict keys.

    Three main steps to find those movements, executed in least expensive
    to most expensive order, hoping that step n allows us to return early
    without having to execute n+1:
      - look at ancestors of movement_list
      - query catalog for descendants of movement_list, hoping that
        it would be recent enough to list them all
      - manually walk descendants of movement_list in ZODB
    """
    buildable_list = []

    # track relations within movement_list if any
    # movement->(set of descendants in movement_list)
    descendant_dict = {}

    # contains a movement -> (dict of predecessors that we still havent met)
    # only contains the movements that have not proved to be unbuildable until
    # now.
    movement_looking_for_dict = {}

    def isBuiltAndCompleted(simulation, path):
      return simulation.getCausalityValue() is not None and \
          simulation.getSimulationState() in predecessor_to_state_dict[path]

    ### Step 1:
    ## Explore ancestors
    #

    for movement in movement_list:
      # set of predecessors
      looking_for = set(predecessor_to_state_dict)
      current = movement.getParentValue()

      maybeBuildable = True

      # visit all parents until Root Applied Rule
      while looking_for and maybeBuildable:
        portal_type = current.getPortalType()
        if portal_type == "Simulation Movement":
          # exploring ancestors is a great way to initialize
          # descendant_dict, while we're at it.
          if current in movement_looking_for_dict:
            descendant_dict.setdefault(current, set()).add(movement)

          path = current.getCausalityValue()
          if path in looking_for:
            looking_for.remove(path)
            if not isBuiltAndCompleted(current, path):
              maybeBuildable = False

        elif portal_type != "Applied Rule":
          break
        # XXX or maybe directly go up by two levels?
        current = current.getParentValue()

      if maybeBuildable:
        if not looking_for:
          buildable_list.append(movement)
        else:
          movement_looking_for_dict[movement] = looking_for

    # Maybe we're lucky, and we've found all predecessors of all
    # movements.
    # We can thus return the buildable ones and we're done.
    if not movement_looking_for_dict:
      return buildable_list

    def updateDescendantDictAndReturnSmallestAncestorSet():
      """
      Remove from descendant_dict the movements that are not
      buildable.

      Returns the smallest set of ancestors A that satisfies:
        - A <= movement_looking_for_dict.keys()
        - descendants(A) = descendants(movement_looking_for_dict.keys())
      (a.k.a. for any ai, aj in A, ai is not a descendant or an ancestor
       of aj)
      """
      movement_to_query = set(movement_looking_for_dict)

      if descendant_dict:
        # remove movements that have been eliminated
        for k, v in descendant_dict.items():
          if k not in movement_looking_for_dict:
            del descendant_dict[k]
          else:
            v.intersection_update(movement_looking_for_dict)

            movement_to_query.difference_update(v)
      return movement_to_query

    movement_to_query = updateDescendantDictAndReturnSmallestAncestorSet()

    ### Step 2:
    ## Try catalog to find descendant movements, knowing
    # that it can be incomplete

    class treeNode(dict):
      """
      Used to cache accesses to ZODB objects.
      The idea is to put in visited_movement_dict the objects we've already
      loaded from ZODB to avoid loading them again.

      - self represents a single ZODB container c
      - self.visited_movement_dict contains an id->(ZODB obj) cache for
        subobjects of c
      - self[id] contains the treeNode representing c[id]
      """
      def __init__(self):
        dict.__init__(self)
        self.visited_movement_dict = dict()

    path_tree = treeNode()

    def updateTree(simulation_movement, path):
      """
      Mark simulation_movement as visited in the Tree

      Returns the list of movements in movement_looking_for_dict that
      are ancestors of simulation_movement
      """
      traversed = []

      tree_node = path_tree
      movement_path = simulation_movement.getPhysicalPath()
      simulation_movement_id = movement_path[-1]
      # find container
      for path_id in movement_path[:-1]:
        # mark traversed movements that are in movement_looking_for_dict
        mvmt, ignored = tree_node.visited_movement_dict.get(path_id, (None, None))
        if mvmt is not None and mvmt in movement_looking_for_dict:
          traversed.append(mvmt)

        tree_node = tree_node.setdefault(path_id, treeNode())

      # and mark the object as visited
      tree_node.visited_movement_dict[simulation_movement_id] = (simulation_movement, path)
      return traversed

    # initialization
    for movement in movement_looking_for_dict:
      updateTree(movement, None)

    portal_catalog = self.getPortalObject().portal_catalog
    catalog_simulation_movement_list = portal_catalog(
      portal_type='Simulation Movement',
      causality_uid=[p.getUid() for p in predecessor_to_state_dict],
      path=['%s/%%' % m.getPath() for m in movement_to_query])

    unbuildable = set()
    for movement in catalog_simulation_movement_list:
      path = movement.getCausalityValue()
      traversed = updateTree(movement, path)
      if not isBuiltAndCompleted(movement, path):
        unbuildable.update(traversed)

    if len(unbuildable) == len(movement_looking_for_dict):
      # the sets are equals
      return buildable_list

    for m in unbuildable:
      del movement_looking_for_dict[m]

    ### Step 3:
    ## We had no luck, we have to explore descendant movements in ZODB
    #

    def findInTree(movement):
      # descend in the tree to find self:
      tree_node = path_tree
      for path_id in movement.getPhysicalPath():
        tree_node = tree_node.get(path_id, treeNode())
      return tree_node

    def descendantGenerator(document, tree_node, path_set_to_check):
      """
      generator yielding Simulation Movement descendants of document.
      It does _not_ explore the whole subtree if iteration is stopped.

      It uses the tree we built previously to avoid loading again ZODB
      objects that we already loaded during catalog querying

      path_set_to_check contains a set of Business Paths that we are
      interested in. A branch is only explored if this set is not
      empty; a movement is only yielded if its causality value is in this set
      """
      object_id_list = document.objectIds()
      for id in object_id_list:
        if id not in tree_node.visited_movement_dict:
          # we had not visited it in step #2
          subdocument = document._getOb(id)
          if subdocument.getPortalType() == "Simulation Movement":
            path = subdocument.getCausalityValue()
            t = (subdocument, path)
            tree_node.visited_movement_dict[id] = t
            if path in path_set_to_check:
              yield t
          else:
            # it must be an Applied Rule
            subtree = tree_node.get(id, treeNode())
            for d in descendantGenerator(subdocument,
                                         subtree,
                                         path_set_to_check):
              yield d

      for id, t in tree_node.visited_movement_dict.iteritems():
        subdocument, path = t
        if path is None:
          # happens for movement in movement_list
          continue
        to_check = path_set_to_check
        # do we need to change/copy the set?
        if path in to_check:
          if len(to_check) == 1:
            # no more paths to check in this branch
            continue
          to_check = to_check.copy()
          to_check.remove(path)
        subtree = tree_node.get(id, treeNode())
        for d in descendantGenerator(subdocument, subtree, to_check):
          yield d


    for movement in updateDescendantDictAndReturnSmallestAncestorSet():
      tree_node = findInTree(movement)
      remaining_path_set = movement_looking_for_dict[movement]
      # find descendants
      for descendant, path in descendantGenerator(self,
                                                  tree_node,
                                                  remaining_path_set):
        if not isBuiltAndCompleted(descendant, path):
          break
      else:
        buildable_list.append(movement)
        buildable_list.extend(descendant_dict.get(movement, []))

    return buildable_list
