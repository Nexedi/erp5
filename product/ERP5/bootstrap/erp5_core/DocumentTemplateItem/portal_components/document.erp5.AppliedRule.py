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
from difflib import unified_diff
from pprint import pformat
import sys
import transaction
import zope.interface
from zExceptions import ExceptionFormatter
from ZODB.POSException import ConflictError
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type.Base import WorkflowMethod
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from erp5.component.module.ExpandPolicy import TREE_DELIVERED_CACHE_KEY
from erp5.component.mixin.ExplainableMixin import ExplainableMixin
from erp5.component.mixin.RuleMixin import RuleMixin
from erp5.component.interface.IExpandable import IExpandable
from erp5.component.interface.IMovementCollection import IMovementCollection
import six

@zope.interface.implementer(IExpandable,
                            IMovementCollection)
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

  def tpValues(self) :
    """ show the content in the left pane of the ZMI """
    return self.objectValues()

  security.declareProtected(Permissions.AccessContentsInformation,
      'isAccountable')
  def isAccountable(self, movement):
    """Tells whether generated movement needs to be accounted or not."""
    return self.getSpecialiseValue().isAccountable(movement)

  security.declarePrivate("getSimulationState")
  def getSimulationState(self):
    return

  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, *args, **kw):
    """Expand this applied rule to create new documents inside the applied rule
    """
    self.getSpecialiseValue().expand(self, *args, **kw)

  # Solvers
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
    def getTreeDelivered():
      for movement in self.objectValues():
        if movement._isTreeDelivered():
          return True
      return False
    try:
      cache = getTransactionalVariable()[TREE_DELIVERED_CACHE_KEY]
    except KeyError:
      return getTreeDelivered()
    rule_key = self.getRelativeUrl()
    try:
      return cache[rule_key]
    except KeyError:
      cache[rule_key] = result = getTreeDelivered()
      return result

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getMovementList')
  def getMovementList(self, portal_type=None, **kw):
    """
     Return a list of movements.
    """
    return self.objectValues(portal_type=RuleMixin.movement_type)

  # pylint: disable=cell-var-from-loop
  def _migrateSimulationTree(self,
                             get_matching_key,
                             get_original_property_dict,
                             root_rule=None,
                             hook_before_edit=None,
                             hook_after_edit=None):
    """Migrate an entire simulation tree in order to use new rules

    This must be called on a root applied rule, with interaction workflows
    disabled. It is required that:
    - All related simulation trees are properly indexed (due to use of
      isSimulated). Unfortunately, this method temporarily unindexes everything,
      so you have to be careful when migrating several trees at once.
    - All simulation trees it may depend on are already migrated. It is advised
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
    workflow, = [wf for wf in portal.portal_workflow.getWorkflowValueListFor(delivery)
                    if wf.isInfoSupported(delivery, 'simulation_state')]
    for history_item in workflow.getInfoFor(delivery, 'history', ()):
      if history_item['simulation_state'] in draft_state_list:
        continue
      # Delivery is/was not in draft state
      resolveCategory = portal.portal_categories.resolveCategory
      order_dict = {} # {new_sm: {key: [old_sm]}}
      old_dict = {} # {root_delivery_line_relative_url: {key: [old_sm]},
                    #  new_sm: old_sm}
      # Caller may want to drop duplicate SM, like a unbuilt SM if there's
      # already a built one, or one with no quantity. So first call
      # 'get_matching_key' on SM that would be kept. 'get_matching_key' would
      # remember them and returns None for duplicates.
      sort_sm = lambda x: (not x.getDelivery(), not x.getQuantity(), x.getId())
      for sm in sorted(self.objectValues(), key=sort_sm):
        line = sm.getOrder() or sm.getDelivery()
        # Check SM is not orphan, which happened with old buggy trees.
        if resolveCategory(line) is not None:
          sm_dict = old_dict.setdefault(line, {})
          recurse_list = deque(({get_matching_key(sm): (sm,)},))
          while recurse_list:
            for k, x in six.iteritems(recurse_list.popleft()):
              if not k:
                continue
              if len(x) > 1:
                x = [x for x in x if x.getDelivery() or x.getQuantity()]
                if len(x) > 1:
                  x.sort(key=sort_sm)
              sm_dict.setdefault(k, []).extend(x)
              for x in x:
                # Group AR by rule.
                r = {} # {rule: [[sm]]}
                for x in x.objectValues():
                  sm_list = x.getMovementList()
                  if sm_list:
                    r.setdefault(x.getSpecialise(), []).append(sm_list)
                # For each rule...
                for x in r.values():
                  if len(x) > 1:
                    # There were several AR applying the same rule.
                    # Choose the one with a built SM (it will fail if
                    # there are several such AR), fallback on the first.
                    x = [y for y in x if any(z.getDelivery()
                           for z in y)] or x[:1]
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
      # XXX: delivery.isSimulated may wrongly return False when a duplicate RAR
      #      was migrated but has not been reindexed yet. Delay migration of
      #      this one.
      rar_list = delivery.getCausalityRelatedValueList(
        portal_type='Applied Rule')
      rar_list.remove(self)
      if rar_list and portal.portal_activities.countMessage(
        path=[x.getPath() for x in rar_list],
        method_id=('immediateReindexObject',
                   'recursiveImmediateReindexSimulationMovement')):
        raise ConflictError
      # Do not try to keep simulation tree for a draft delivery
      # if it was already out of sync.
      if delivery.getSimulationState() in draft_state_list and \
         any(x.getRelativeUrl() not in old_dict
             for x in delivery.getMovementList()):
        break
      if root_rule:
        self._setSpecialise(root_rule)
      delivery_set = {delivery}
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
            try:
              sm.delivery_ratio = old_sm.aq_base.delivery_ratio
            except AttributeError:
              pass
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
                  recorded_property_dict.update(new)

            if hook_before_edit is not None:
              hook_before_edit(rule, old_sm, sm, edit_kw, recorded_property_dict)

            if recorded_property_dict:
              sm._recorded_property_dict = PersistentMapping(
                recorded_property_dict)
            sm._edit(**edit_kw)

            if hook_after_edit is not None:
              hook_after_edit(rule, old_sm, sm)

            old_dict[sm] = old_sm
            sm = None
      deleted = old_dict.items()
      for delivery, sm_dict in deleted:
        if not sm_dict:
          del old_dict[delivery]
      from erp5.component.document.SimulationMovement import SimulationMovement
      from erp5.component.mixin.MovementCollectionUpdaterMixin import \
          MovementCollectionUpdaterMixin as mixin
      # Patch is already protected by WorkflowMethod.disable lock.
      orig_updateMovementCollection = mixin.__dict__['updateMovementCollection']
      try:
        AppliedRule.isIndexable = SimulationMovement.isIndexable = \
          ConstantGetter('isIndexable', value=False)
        mixin.updateMovementCollection = updateMovementCollection
        self.expand("immediate")
      finally:
        mixin.updateMovementCollection = orig_updateMovementCollection
        del AppliedRule.isIndexable, SimulationMovement.isIndexable
      self.recursiveReindexObject()
      assert str not in map(type, old_dict), old_dict
      return {k: sum(v.values(), []) for k, v in deleted}, delivery_set
    simulation_tool._delObject(self.getId())

  def _checkExpand(self, ignore_nul_movements=False, filter=None):  # pylint:disable=redefined-builtin
    """Check that expand() would not fail nor do major changes to the subobjects

    Transaction is aborted after 'expand' is called.

    See also SimulationTool._checkExpandAll
    """
    property_dict = {'Applied Rule': ('specialise',),
                     'Simulation Movement': ('delivery', 'quantity')}
    def fillRuleDict():
      rule_dict = {}
      object_list = deque((self,))
      while object_list:
        document = object_list.popleft()
        portal_type = document.getPortalType()
        document_dict = {property: document.getProperty(property)
                         for property in property_dict[portal_type]}
        if ignore_nul_movements and portal_type == 'Simulation Movement' and \
           not (document_dict['quantity'] and document.getPrice()):
          if document.isDeletable():
            continue
          del document_dict['quantity']
        document_dict['portal_type'] = portal_type
        if filter is None or filter(initial_rule_dict, document, document_dict):
          rule_dict[document.getRelativeUrl()] = document_dict
          object_list += document.objectValues()
      return rule_dict
    initial_rule_dict = None
    initial_rule_dict = fillRuleDict()
    try:
      self.expand("immediate")
    except ConflictError:
      raise
    except Exception:
      msg = ''.join(ExceptionFormatter.format_exception(*sys.exc_info())[1:])
    else:
      final_rule_dict = fillRuleDict()
      if initial_rule_dict == final_rule_dict:
        msg = None
      else:
        diff = unified_diff(
          pformat(initial_rule_dict, width=1000).splitlines(),
          pformat(final_rule_dict, width=1000).splitlines(),
          lineterm='')
        next(diff)
        next(diff)
        msg = '\n'.join(diff)
    transaction.abort()
    return msg
