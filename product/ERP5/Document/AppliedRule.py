# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from collections import deque
import zope.interface

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.Base import WorkflowMethod
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5.mixin.explainable import ExplainableMixin
from Products.ERP5.mixin.rule import RuleMixin

TREE_DELIVERED_CACHE_KEY = 'AppliedRule._isTreeDelivered_cache'
TREE_DELIVERED_CACHE_ENABLED = 'TREE_DELIVERED_CACHE_ENABLED'

class AppliedRule(XMLObject, ExplainableMixin):
  """
    An applied rule holds a list of simulation movements.

    An applied rule points to an instance of Rule (which defines the actual
    rule to apply with its parameters) through the specialise relation.

    An applied rule can expand itself (look at its direct parent and take
    conclusions on what should be inside).

    An applied rule can tell if it is stable (if its children are consistent
    with what would be expanded from its direct parent).

    An applied rule can tell if any of his direct children is divergent (not
    consistent with the delivery).

    All algorithms are implemented by the rule.
  """

  # CMF Type Definition
  meta_type = 'ERP5 Applied Rule'
  portal_type = 'Applied Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.SimpleItem
                    , PropertySheet.CategoryCore
                    , PropertySheet.AppliedRule
                    )

  # Declarative interfaces
  zope.interface.implements(interfaces.IMovementCollection,)

  def tpValues(self) :
    """ show the content in the left pane of the ZMI """
    return self.objectValues()

  security.declareProtected(Permissions.AccessContentsInformation,
      'isAccountable')
  def isAccountable(self, movement):
    """Tells whether generated movement needs to be accounted or not."""
    return self.getSpecialiseValue().isAccountable(movement)

  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  @UnrestrictedMethod
  def expand(self, **kw):
    """
      Expands the current movement downward.

      -> new status -> expanded

      An applied rule can be expanded only if its parent movement
      is expanded.
    """
    tv = getTransactionalVariable()
    cache = tv.setdefault(TREE_DELIVERED_CACHE_KEY, {})
    cache_enabled = cache.get(TREE_DELIVERED_CACHE_ENABLED, 0)

    # enable cache
    if not cache_enabled:
      cache[TREE_DELIVERED_CACHE_ENABLED] = 1

    rule = self.getSpecialiseValue()
    if rule is not None:
      rule.expand(self,**kw)

    # disable and clear cache
    if not cache_enabled:
      try:
        del tv[TREE_DELIVERED_CACHE_KEY]
      except KeyError:
        pass

  security.declareProtected(Permissions.ModifyPortalContent, 'solve')
  def solve(self, solution_list):
    """
      Solve inconsistency according to a certain number of solutions
      templates. This updates the

      -> new status -> solved

      This applies a solution to an applied rule. Once
      the solution is applied, the parent movement is checked.
      If it does not diverge, the rule is reexpanded. If not,
      diverge is called on the parent movement.
    """
    rule = self.getSpecialiseValue()
    if rule is not None:
      rule.solve(self)

  security.declareProtected(Permissions.ModifyPortalContent, 'diverge')
  def diverge(self):
    """
      -> new status -> diverged

      This basically sets the rule to "diverged"
      and blocks expansion process
    """
    rule = self.getSpecialiseValue()
    if rule is not None:
      rule.diverge(self)

  # Solvers
  security.declareProtected(Permissions.AccessContentsInformation,
      'isStable')
  def isStable(self):
    """
    Tells whether the rule is stable or not.
    """
    return self.getSpecialiseValue().isStable(self)

  security.declareProtected(Permissions.AccessContentsInformation,
      'isDivergent')
  def isDivergent(self, sim_mvt):
    """
    Tells whether generated sim_mvt is divergent or not.
    """
    return self.getSpecialiseValue().isDivergent(sim_mvt)

  security.declareProtected(Permissions.AccessContentsInformation,
      'getDivergenceList')
  def getDivergenceList(self, sim_mvt):
    """
    Returns a list Divergence descriptors
    """
    return self.getSpecialiseValue().getDivergenceList(sim_mvt)

  security.declareProtected(Permissions.AccessContentsInformation,
      'isRootAppliedRule')
  def isRootAppliedRule(self):
    """
      Returns 1 is this is a root applied rule
    """
    return self.getParentValue().getMetaType() == "ERP5 Simulation Tool"

  security.declareProtected(Permissions.AccessContentsInformation,
      'getRootAppliedRule')
  def getRootAppliedRule(self):
    """Return the root applied rule.
    useful if some reindexing is needed from inside
    """
    if self.getParentValue().getMetaType() == "ERP5 Simulation Tool":
      return self
    return self.getParentValue().getRootAppliedRule()

  def _isTreeDelivered(self):
    """
    Checks if submovements of this applied rule (going down the complete
    simulation tree) have a delivery relation.
    Returns True if at least one is delivered, False if none of them are.

    see SimulationMovement._isTreeDelivered
    """
    tv = getTransactionalVariable()
    cache = tv.setdefault(TREE_DELIVERED_CACHE_KEY, {})
    cache_enabled = cache.get(TREE_DELIVERED_CACHE_ENABLED, 0)

    def getTreeDelivered(applied_rule):
      for movement in applied_rule.objectValues():
        if movement._isTreeDelivered():
          return True
      return False

    rule_key = self.getRelativeUrl()
    if cache_enabled:
      try:
        return cache[rule_key]
      except:
        result = getTreeDelivered(self)
        cache[rule_key] = result
        return result
    else:
      return getTreeDelivered(self)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getMovementList')
  def getMovementList(self, portal_type=None, **kw):
    """
     Return a list of movements.
    """
    return self.objectValues(portal_type=RuleMixin.movement_type)

  security.declareProtected(Permissions.AccessContentsInformation,
          'getIndexableChildSimulationMovementValueList')
  def getIndexableChildSimulationMovementValueList(self):
    return [x for x in self.getIndexableChildValueList()
              if x.getPortalType() == 'Simulation Movement']

  security.declarePublic('recursiveImmediateReindexSimulationMovement')
  def recursiveImmediateReindexSimulationMovement(self, **kw):
    """
      Applies immediateReindexObject recursively to Simulation Movements
    """
    # Reindex direct children
    root_indexable = int(getattr(self.getPortalObject(), 'isIndexable', 1))
    for movement in self.objectValues():
      if movement.isIndexable and root_indexable:
        movement.immediateReindexObject(**kw)
    # Go recursively
    for movement in self.objectValues():
      for applied_rule in movement.objectValues():
        applied_rule.recursiveImmediateReindexSimulationMovement(**kw)

  security.declarePublic('recursiveReindexSimulationMovement')
  def recursiveReindexSimulationMovement(self, activate_kw=None, **kw):
    if self.isIndexable:
      if activate_kw is None:
        activate_kw = {}

    reindex_kw = self.getDefaultReindexParameterDict()
    if reindex_kw is not None:
      reindex_activate_kw = reindex_kw.pop('activate_kw', None)
      if reindex_activate_kw is not None:
        reindex_activate_kw = reindex_activate_kw.copy()
        if activate_kw is not None:
          # activate_kw parameter takes precedence
          reindex_activate_kw.update(activate_kw)
        activate_kw = reindex_activate_kw
      kw.update(reindex_kw)

    group_id_list  = []
    if kw.get("group_id", "") not in ('', None):
      group_id_list.append(kw.get("group_id", ""))
    if kw.get("sql_catalog_id", "") not in ('', None):
      group_id_list.append(kw.get("sql_catalog_id", ""))
    group_id = ' '.join(group_id_list)

    self.activate(
      group_method_id='portal_catalog/catalogObjectList',
      expand_method_id='getIndexableChildSimulationMovementValueList',
      alternate_method_id='alternateReindexObject',
      group_id=group_id,
      serialization_tag=self.getRootDocumentPath(),
      **activate_kw).recursiveImmediateReindexSimulationMovement(**kw)

  def _migrateSimulationTree(self, get_matching_key,
                             get_original_property_dict, root_rule=None):
    """Migrate an entire simulation tree in order to use new rules

    This must be called on a root applied rule, with interaction workflows
    disabled. It is required that:
    - All related simulation trees are properly indexed (due to use of
      isSimulated). Unfortunately, this method temporarily unindexes everything,
      so you have to be careful when migrating several trees at once.
    - All simulation trees it may depend on are already migrated. It is adviced
      to first migrate all root applied rule for the first phase (usually
      order) and to continue respecting the order of phases.

    def get_matching_key(simulation_movement):
      # Return arbitrary value to match old and new simulation movements,
      # or null if the old simulation movement is dropped.

    def get_original_property_dict(tester, old_sm, sm, movement):
      # Return values to override on the new simulation movement.
      # In most cases, it would return the result of:
      #   tester.getUpdatablePropertyDict(old_sm, movement)

    root_rule # If not null and tree is about to be regenerated, 'specialise'
              # is changed on self to this relative url.
    """
    assert WorkflowMethod.disabled(), \
      "Interaction workflows must be disabled using WorkflowMethod.disable"
    simulation_tool = self.getParentValue()
    assert simulation_tool.getPortalType() == 'Simulation Tool'
    portal = simulation_tool.getPortalObject()
    delivery = self.getCausalityValue()
    # Check the whole history to not drop simulation in case of redraft
    draft_state_list = portal.getPortalDraftOrderStateList()
    workflow, = [wf for wf in portal.portal_workflow.getWorkflowsFor(delivery)
                    if wf.isInfoSupported(delivery, 'simulation_state')]
    for history_item in workflow.getInfoFor(delivery, 'history', ()):
      if history_item['simulation_state'] in draft_state_list:
        continue
      # Delivery is/was not is draft state
      order_dict = {}
      old_dict = {}
      # Caller may want to drop duplicate SM, like a unbuilt SM if there's
      # already a built one, or one with no quantity. So first call
      # 'get_matching_key' on SM that would be kept. 'get_matching_key' would
      # remember them and returns None for duplicates.
      sort_sm = lambda x: (not x.getDelivery(), not x.getQuantity(), x.getId())
      for sm in sorted(self.objectValues(), key=sort_sm):
        sm_dict = old_dict.setdefault(sm.getOrder() or sm.getDelivery(), {})
        recurse_list = deque(({get_matching_key(sm): (sm,)},))
        while recurse_list:
          for k, x in recurse_list.popleft().iteritems():
            if not k:
              continue
            if len(x) > 1:
              x = [x for x in x if x.getDelivery() or x.getQuantity()]
              if len(x) > 1:
                x.sort(key=sort_sm)
            sm_dict.setdefault(k, []).extend(x)
            for x in x:
              r = {}
              for x in x.objectValues():
                sm_list = x.getMovementList()
                if sm_list:
                  r.setdefault(x.getSpecialise(), []).append(sm_list)
              for x in r.values():
                if len(x) > 1:
                  x = [y for y in x if any(z.getDelivery() for z in y)] or x[:1]
                x, = x
                r = {}
                for x in x:
                  r.setdefault(get_matching_key(x), []).append(x)
                recurse_list.append(r)
        self._delObject(sm.getId())
      # Here Delivery.isSimulated works because Movement.isSimulated
      # does not see the simulated movements we've just deleted.
      if delivery.isSimulated():
        break
      # Do not try to keep simulation tree for draft delivery
      # if it was already out of sync.
      if delivery.getSimulationState() in draft_state_list and \
         any(x.getRelativeUrl() not in old_dict
             for x in delivery.getMovementList()):
        break
      if root_rule:
        self.setSpecialise(root_rule)
      delivery_set = set((delivery,))
      def updateMovementCollection(rule, context, *args, **kw):
        orig_updateMovementCollection(rule, context, *args, **kw)
        new_parent = context.getParentValue()
        for sm in context.getMovementList():
          delivery = sm.getDelivery()
          if delivery:
            sm_dict = old_dict.pop(delivery)
          else:
            sm_dict = order_dict[new_parent]
          order_dict[sm] = sm_dict
          k = get_matching_key(sm)
          sm_list = sm_dict.pop(k, ())
          if len(sm_list) > 1:
            # Heuristic to find matching old simulation movements for the
            # currently expanded applied rule. We first try to preserve same
            # tree structure (new & old parent SM match), then we look for an
            # old possible parent that is in the same branch.
            try:
              old_parent = old_dict[new_parent]
            except KeyError:
              old_parent = simulation_tool
            best_dict = {}
            for old_sm in sm_list:
              parent = old_sm.getParentValue().getParentValue()
              if parent is old_parent:
                parent = None
              elif not (parent.aq_inContextOf(old_parent) or
                        old_parent.aq_inContextOf(parent)):
                continue
              best_dict.setdefault(parent, []).append(old_sm)
            try:
              best_sm_list = best_dict[None]
            except KeyError:
              best_sm_list, = best_dict.values()
            if len(best_sm_list) < len(sm_list):
              sm_dict[k] = list(set(sm_list).difference(best_sm_list))
            sm_list = best_sm_list
            if len(sm_list) > 1:
              kw = sm.__dict__.copy()
          # We may have several old matching SM, e.g. in case of split.
          for old_sm in sm_list:
            movement = old_sm.getDeliveryValue()
            if sm is None:
              sm = context.newContent(portal_type=rule.movement_type)
              sm.__dict__ = dict(kw, **sm.__dict__)
              order_dict[sm] = sm_dict
            if delivery:
              assert movement.getRelativeUrl() == delivery
            elif movement is not None:
              sm._setDeliveryValue(movement)
              delivery_set.add(sm.getExplanationValue())
            recorded_property_dict = {}
            edit_kw = {}
            kw['quantity'] = 0
            for tester in rule._getUpdatingTesterList():
              old = get_original_property_dict(tester, old_sm, sm, movement)
              if old is not None:
                new = tester.getUpdatablePropertyDict(sm, movement)
                if old != new:
                  edit_kw.update(old)
                  if 'quantity' in new and old_sm is not sm_list[-1]:
                    quantity = new.pop('quantity')
                    kw['quantity'] = quantity - old.pop('quantity')
                    if new != old or sm.quantity != quantity:
                      raise NotImplementedError # quantity_unit/efficiency ?
                  else:
                    recorded_property_dict.update(new)
            if recorded_property_dict:
              sm._recorded_property_dict = PersistentMapping(
                recorded_property_dict)
            sm._edit(**edit_kw)
            old_dict[sm] = old_sm
            sm = None
      deleted = old_dict.items()
      for delivery, sm_dict in deleted:
        if not sm_dict:
          del old_dict[delivery]
      from Products.ERP5.mixin.movement_collection_updater import \
          MovementCollectionUpdaterMixin as mixin
      # Patch is already protected by WorkflowMethod.disable lock.
      orig_updateMovementCollection = mixin.__dict__['updateMovementCollection']
      try:
        mixin.updateMovementCollection = updateMovementCollection
        self.expand()
      finally:
        mixin.updateMovementCollection = orig_updateMovementCollection
      assert str not in map(type, old_dict), old_dict
      return dict((k, sum(v.values(), [])) for k, v in deleted), delivery_set
    simulation_tool._delObject(self.getId())
