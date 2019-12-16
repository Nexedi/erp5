# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import transaction
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Base import Base
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.Errors import SimulationError

class SimulableMixin(Base):
  security = ClassSecurityInfo()

  def updateSimulation(self, **kw):
    """Create/update related simulation trees by activity

    This method is used to maintain related objects in simulation trees:
    - hiding complexity of activity dependencies
    - avoiding duplicate work

    Repeated calls of this method for the same delivery will result in a single
    call to _updateSimulation. Grouping may happen at the end of the transaction
    or by the grouping method.

    See _updateSimulation for accepted parameters.
    """
    tv = getTransactionalVariable()
    key = 'SimulableMixin.updateSimulation', self.getUid()
    item_list = kw.items()
    try:
      kw, ignore = tv[key]
      kw.update(item_list)
    except KeyError:
      ignore_key = key + ('ignore',)
      ignore = tv.pop(ignore_key, set())
      tv[key] = kw, ignore
      def before_commit():
        if kw:
          path = self.getPath()
          if aq_base(self.unrestrictedTraverse(path, None)) is aq_base(self):
            self.activate(
              activity='SQLQueue',
              group_method_id='portal_rules/updateSimulation',
              tag='build:' + path,
              priority=3,
              )._updateSimulation(**kw)
        del tv[key]
        ignore.update(kw)
        tv[ignore_key] = ignore
      transaction.get().addBeforeCommitHook(before_commit)
    for k, v in item_list:
      if not v:
        ignore.add(k)
      elif k not in ignore:
        continue
      del kw[k]

  def _updateSimulation(self, create_root=0, expand_root=0,
                              expand_related=0, index_related=0):
    """
    Depending on set parameters, this method will:
      create_root    -- if a root applied rule is missing, create and expand it
      expand_root    -- expand related root applied rule,
                        create it before if missing
      expand_related -- expand related simulation movements
      index_related  -- reindex related simulation movements (recursively)
    """
    if create_root or expand_root:
      applied_rule = self._getRootAppliedRule()
      if applied_rule is None:
        applied_rule = self._createRootAppliedRule()
        expand_root = applied_rule is not None
    activate_kw = {'tag': 'build:'+self.getPath()}
    if expand_root:
      applied_rule.expand(activate_kw=activate_kw)
    else:
      applied_rule = None
    if expand_related:
      for movement in self._getAllRelatedSimulationMovementList():
        movement = movement.getObject()
        if not movement.aq_inContextOf(applied_rule):
          # XXX: make sure this will also reindex of all sub-objects recursively
          movement.expand(activate_kw=activate_kw)
    elif index_related:
      for movement in self._getAllRelatedSimulationMovementList():
        movement = movement.getObject()
        if not movement.aq_inContextOf(applied_rule):
          movement.recursiveReindexObject(activate_kw=activate_kw)

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getRuleReference')
  def getRuleReference(self):
    """Returns an appropriate rule reference

    XXX: Using reference to select a rule (for a root applied rule) is wrong
         and should be replaced by predicate and workflow state.
    """
    method = self._getTypeBasedMethod('getRuleReference')
    if method is None:
      raise SimulationError("Missing type-based 'getRuleReference' script for "
                            + repr(self))
    return method()

  def _getRootAppliedRule(self):
    """Get related root applied rule if it exists"""
    applied_rule_list = self.getCausalityRelatedValueList(
        portal_type='Applied Rule')
    if len(applied_rule_list) == 1:
      return applied_rule_list[0]
    elif applied_rule_list:
      raise SimulationError('%r has more than one applied rule.' % self)

  def _createRootAppliedRule(self):
    """Create a root applied rule"""
    # XXX: Consider moving this first test to Delivery
    if self.isSimulated():
      # No need to have a root applied rule
      # if we are already in the simulation process
      return
    rule_reference = self.getRuleReference()
    if rule_reference:
      portal = self.getPortalObject()
      rule_list = portal.portal_catalog.unrestrictedSearchResults(
        portal_type=portal.getPortalRuleTypeList(),
        validation_state="validated", reference=rule_reference,
        sort_on='version', sort_order='descending')
      if rule_list:
        applied_rule = rule_list[0].constructNewAppliedRule(
          portal.portal_simulation, is_indexable=False)
        applied_rule._setCausalityValue(self)
        del applied_rule.isIndexable
        # To prevent duplicate root Applied Rule, we reindex immediately and
        # lock ZODB, and we rely on the fact that ZODB is committed after
        # catalog. This way, we guarantee the catalog is up-to-date as soon as
        # ZODB is unlocked.
        applied_rule.immediateReindexObject()
        self.serialize() # prevent duplicate root Applied Rule
        return applied_rule
      raise SimulationError("No such rule as %r is found" % rule_reference)

  security.declarePrivate('manage_beforeDelete')
  def manage_beforeDelete(self, item, container):
    """Delete related Applied Rule"""
    for o in self.getCausalityRelatedValueList(portal_type='Applied Rule'):
      o.getParentValue().deleteContent(o.getId())
    super(SimulableMixin, self).manage_beforeDelete(item, container)

InitializeClass(SimulableMixin)
