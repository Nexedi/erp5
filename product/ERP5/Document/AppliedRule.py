##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
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
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject

from zLOG import LOG
import psyco

class AppliedRule(XMLObject):
    """
      An applied rule holds a list of simulation movements

      An applied rule points to an instance of Rule
      (which defines the actual rule to apply with its parameters)

      An applied rule can expand itself (look at its direct parent
      and take conclusions on what should be inside). This is similar
      to the base_fix_consistency mechanism

      An applied rule can "solve" or "backtrack". In this case
      it looks at its children, looks at the difference between
      target and actual, and takes conclusions on its parent

      All algorithms are implemented by the rule
    """

    # CMF Type Definition
    meta_type = 'ERP5 Applied Rule'
    portal_type = 'Applied Rule'
    add_permission = Permissions.AddERP5Content
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.SimpleItem
                      , PropertySheet.CategoryCore
                      , PropertySheet.AppliedRule
                      )

    # CMF Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
An ERP5 Rule..."""
         , 'icon'           : 'applied_rule_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addAppliedRule'
         , 'immediate_view' : 'applied_rule_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('Simulation Movement',)
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'applied_rule_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'list'
          , 'name'          : 'Object Contents'
          , 'category'      : 'object_action'
          , 'action'        : 'folder_contents'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'applied_rule_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'category'      : 'object_action'
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      }

    security.declareProtected(Permissions.AccessContentsInformation, 'getCausalityState')
    def getCausalityState(self, id_only=1):
      """
        Returns the current state in causality
      """
      portal_workflow = getToolByName(self, 'portal_workflow')
      wf = portal_workflow.getWorkflowById('causality_workflow')
      return wf._getWorkflowStateOf(self, id_only=id_only)


    security.declareProtected(Permissions.AccessContentsInformation, 'test')
    def test(self):
      """
        Tests if the rule (still) applies
      """
      my_parent = self.aq_parent
      if my_parent is None: # Should be is portal_simulation
        return 1
      else:
        rule = self.getSpecialiseValue()
        return rule.test(my_parent)

    # Simulation workflow
    def reset(self):
      """
        DO WE NEED IT ?

        -> this does either a diverge or a reset depending
        on the position in the tree

        if it is in root position, it is a solve
        if it is in non root position, it is a diverse
      """
      rule = self.getSpecialiseValue()
      if rule is not None:
        rule.reset(self)

    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self):
      """
        Expands the current movement downward.

        -> new status -> expanded

        An applied rule can be expanded only if its parent movement
        is expanded.
      """
      rule = self.getSpecialiseValue()
      if rule is not None:
        rule.expand(self)

    #expand = WorkflowMethod(expand)

    security.declareProtected(Permissions.ModifyPortalContent, 'solve')
    def solve(self, solution_list):
      """
        Solve inconsitency according to a certain number of solutions
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

    #solve = WorkflowMethod(solve)

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

    #diverge = WorkflowMethod(diverge)

    # Solvers
    security.declareProtected(Permissions.View, 'isDivergent')
    def isDivergent(self):
      """
        Returns 1 if divergent rule
      """
      rule = self.getSpecialiseValue()
      if rule is not None:
        return rule.isDivergent(self)
      return 0

    security.declareProtected(Permissions.View, 'getDivergenceList')
    def getDivergenceList(self):
      """
        Returns a list Divergence descriptors
      """
      rule = self.getSpecialiseValue()
      if rule is not None:
        return rule.getDivergenceList(self)
      return ()

    security.declareProtected(Permissions.View, 'getSolverList')
    def getSolverList(self):
      """
        Returns a list Divergence solvers
      """
      rule = self.getSpecialiseValue()
      if rule is not None:
        return rule.getSolverList(self)
      return ()

    # Optimized Reindexing
    security.declareProtected(Permissions.View, 'getMovementIndex')
    def getMovementIndex(self):
      """
        Returns a list of indexable movements
      """
      result = [ { 'uid'                        : self.getUid(),
                   'id'                         : self.getId(),
                   'portal_type'                : self.getPortalType(),
                   'url'                        : self.getUrl(),
                   'relative_url'               : self.getRelativeUrl(),
                   'parent_uid'                 : self.getParentUid(),
                   'simulation_state'           : None,
                   'causality_uid'              : self.getCausalityUid(),
                   'specialise_uid'             : self.getSpecialiseUid(),
                  } ]
      for m in self.objectValues():
        result.extend(m.getMovementIndex())
      return result

    security.declareProtected(Permissions.View, 'reindexObject')
    def reindexObject(self, **kw):
      """
        Only reindex root applied rule
      """
      if self.isRootAppliedRule():
        XMLObject.reindexObject(self, **kw)
      else:
        self.getRootAppliedRule().reindexObject() # Reindex the whole applied rule

    security.declareProtected(Permissions.View, 'hasActivity')
    def hasActivity(self, **kw):
      """
        We reindex the whole applied rule
      """
      if self.isRootAppliedRule():
        XMLObject.hasActivity(self, **kw)
      else:
        self.getRootAppliedRule().hasActivity(**kw) # Reindex the whole applied rule

    security.declareProtected(Permissions.View, 'isRootAppliedRule')
    def isRootAppliedRule(self):
      """
        Returns 1 is this is a root applied rule
      """
      if self.getParent().getMetaType() == "ERP5 Simulation Tool":
        return 1
      else:
        return 0

    def getRootAppliedRule(self):
      # Return the root applied rule -- useful if some reindexing is needed from inside
      if self.getParent().getMetaType() == "ERP5 Simulation Tool":
        return self
      else:
        return self.getParent().getRootAppliedRule()

    # Psyco optimizations
    psyco.bind(getMovementIndex)
