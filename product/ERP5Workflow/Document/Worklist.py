##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
#               2015 Wenjie Zheng <wenjie.zheng@tiolive.com>
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

import re

from AccessControl import ClassSecurityInfo
from Persistence import PersistentMapping
from Products.CMFCore.Expression import Expression
from Products.DCWorkflow.Guard import Guard
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
from Products.ERP5Type.XMLObject import XMLObject

from zLOG import LOG, WARNING

tales_re = re.compile(r'(\w+:)?(.*)')

class Worklist(IdAsReferenceMixin("worklist_", "prefix"), XMLObject):
    """
    A ERP5 Worklist.
    Four Variable: portal_type; simulation_state; validation_state; causality_state
    can be accessed directly; other dynamic variables will be accessable through
    content type "Worklist Variable".
    """

    meta_type = 'ERP5 Worklist'
    portal_type = 'Worklist'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1
    description = ''
    var_matches = []  # Compared with catalog when set.
    matched_portal_type = ''
    actbox_name = ''
    actbox_url = ''
    actbox_icon = ''
    actbox_category = 'global'
    guard = None
    default_reference = ''
    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = (
               PropertySheet.Base,
               PropertySheet.XMLObject,
               PropertySheet.CategoryCore,
               PropertySheet.DublinCore,
               PropertySheet.Reference,
               PropertySheet.Worklist,
    )

    def getGuardSummary(self):
      res = None
      if self.getGuard() is not None:
        res = self.guard.getSummary()
      return res

    def getGuard(self):
      if self.getRoleList() is None and\
          self.getPermissionList() is None and\
          self.getGroupList() is None and\
          self.getExpression() is None and\
          self.guard is None:
        return None
      else:
        self.generateGuard()
      return self.guard

    def generateGuard(self):
      if self.guard is None:
        self.guard = Guard().__of__(self)
      if self.getRoleList() is not None:
        self.guard.roles = self.getRoleList()
      if self.getPermissionList() is not None:
        self.guard.permissions = self.getPermissionList()
      if self.getGroupList() is not None:
        self.guard.groups = self.getGroupList()
      if self.getExpression() is not None:
        self.guard.expr = Expression(self.getExpression())

    def getAvailableCatalogVars(self):
        res = []
        res.append(self.getParentValue().getStateVariable())
        for vdef in self.getParentValue().contentValues(portal_type="Variable"):
            if vdef.for_catalog:
                res.append(vdef.getId())
        for vdef in self.objectValues():
          res.append(vdef.getId())
        res.sort()
        return res

    def updateDynamicVariable(self):
      # Keep worklist variables updating, correspond to workflow variables.
      # In the new workflow, we may not need this function for the moment.
      res = []

      for worklist_variable_value in self.objectValues():
        res.append(worklist_variable_value)
      return res

    def _updateDynamicVariable(self):
      # Keep worklist variables updating, correspond to workflow variables.
      res = []
      workflow_variable_id_list = []
      default_variable_id_list = ['variable_action', 'variable_actor',\
        'variable_comment', 'variable_error_message', 'variable_history',\
        'variable_portal_type', 'variable_time']

      """
      Check workflow variables:
      """
      for variable_value in self.getParentValue().objectValues(portal_type="Variable"):
        variable_id = variable_value.getId()
        workflow_variable_id_list.append(variable_id)
        worklist_variable_value = self._getOb(variable_id, None)
        if worklist_variable_value is None and variable_value.for_catalog == 1 and variable_id not in default_variable_id_list:
          variable_value_ref = variable_value.getReference()
          worklist_variable_value = self.newContent(portal_type='Worklist Variable')
          worklist_variable_value.setReference(variable_value_ref)
          worklist_variable_value.setDefaultExpr(variable_value.getDefaultExpr())
          worklist_variable_value.setInitialValue(variable_value.getInitialValue())
          res.append(worklist_variable_value)
        if worklist_variable_value and worklist_variable_value not in res and variable_value.for_catalog == 1:
          res.append(worklist_variable_value)
        if worklist_variable_value in res and variable_value.for_catalog == 0:
          self._delObject(variable_id)
          res.remove(worklist_variable_value)

      """
      Append user created worklist variables.
      """
      for worklist_variable_value in self.objectValues():
        if worklist_variable_value.getId() not in workflow_variable_id_list:
          res.append(worklist_variable_value)
          workflow_variable_id_list.append(worklist_variable_value.getId())
      LOG(" worklist '%s' has variable '%s'"%(self.getId(),workflow_variable_id_list ),0, " in Worklist.py 159")
      return res

    def getVarMatchKeys(self):
        key_list = []
        if self.getMatchedPortalType() is not None:
          key_list.append('portal_type')
        if self.getMatchedSimulationState() is not None:
          key_list.append('simulation_state')
        if self.getMatchedValidationState() is not None:
          key_list.append('validation_state')
        if self.getMatchedCausalityState() is not None:
          key_list.append('causality_state')
        for dynamic_variable in self.objectValues():
          if dynamic_variable.getInitialValue() or dynamic_variable.getDefaultExpr():
            key_list.append(dynamic_variable.getReference())
        return key_list

    def getVarMatch(self, id):
        """ return value of matched keys"""
        matches = None
        matches_ref_list = []
        if id == 'portal_type':
          v = self.getMatchedPortalTypeList()
          if v: matches = tuple(v)
        elif id in ['validation_state', 'simulation_state']:
          if id == 'validation_state':
            matches_id_list = self.getMatchedValidationStateList()
          elif id == 'simulation_state':
            matches_id_list = self.getMatchedSimulationStateList()
          # Get workflow state's reference:
          for state_id in matches_id_list:
            if hasattr(self.getParent(), state_id):
              matches_ref_list.append(self.getParent()._getOb(state_id).getReference())
            else: matches_ref_list = matches_id_list
          matches = tuple(matches_ref_list)
        elif id == 'causality_state':
          matches_id = self.getMatchedCausalityState()
          matches_ref_list.append(matches_id)
          matches = tuple(matches_ref_list)
        else:
          # Local dynamic variable:
          dynamic_varible = self._getOb('variable_'+id)
          if dynamic_varible.getInitialValue():
            matches = [dynamic_varible.getInitialValue()]
          # Override initial value if expression set:
          if dynamic_varible.getDefaultExpr():
            matches = Expression(dynamic_varible.getDefaultExpr())

        if matches is not [] and matches is not None:
          if not isinstance(matches, (tuple, Expression)):
            # Old version, convert it.
            matches = tuple(matches)
          return matches
        else:
          return ()

    def getVarMatchText(self, id):
        values = self.getVarMatch(id)
        if isinstance(values, Expression):
            return values.text
        return '; '.join(values)
