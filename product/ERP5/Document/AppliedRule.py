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

from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.PsycoWrapper import psyco

from zLOG import LOG

class AppliedRule(XMLObject):
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

    security.declareProtected(Permissions.AccessContentsInformation, 'test')
    def test(self):
      """
      Tests if the rule (still) applies
      """
      if self.isRootAppliedRule():
        return 1
      else:
        parent_value = self.getParentValue()
        rule = self.getSpecialiseValue()
        return rule.test(parent_value)

    security.declareProtected(Permissions.AccessContentsInformation,
        'isAccountable')
    def isAccountable(self, movement):
      """Tells whether generated movement needs to be accounted or not."""
      return self.getSpecialiseValue().isAccountable(movement)

    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, **kw):
      """
        Expands the current movement downward.

        -> new status -> expanded

        An applied rule can be expanded only if its parent movement
        is expanded.
      """
      rule = self.getSpecialiseValue()
      if rule is not None:
        if self.isRootAppliedRule():
          # We should capture here a list of url/uids of deliveires to update
          rule._v_notify_dict = {}
        rule.expand(self,**kw)
        # XXX This part must be done with a interaction workflow is needed.
#       if self.isRootAppliedRule():
#         self.activate(
#                after_method_id=["immediateReindexObject",
#                                 "recursiveImmediateReindexObject"]).\
#                                   notifySimulationChange(rule._v_notify_dict)

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
        'getSolverList')
    def getSolverList(self, movement):
      """
      Returns a list Divergence solvers
      """
      return self.getSpecialiseValue().getSolverList(movement)

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

    security.declareProtected(Permissions.ModifyPortalContent,
                              'notifySimulationChange')
    def notifySimulationChange(self, notify_dict):
      for delivery_url in notify_dict.keys():
        delivery_value = self.getPortalObject().restrictedTraverse(delivery_url)
        if delivery_value is None:
          LOG("ERP5 WARNING", 0,
              'Unable to access object %s to notify simulation change' %
               delivery_url)
        else:
          delivery_value.notifySimulationChange()
