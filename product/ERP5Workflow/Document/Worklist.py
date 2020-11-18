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
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Workflow.mixin.guardable import GuardableMixin
from zLOG import LOG, WARNING

tales_re = re.compile(r'(\w+:)?(.*)')

class Worklist(IdAsReferenceMixin("worklist_", "prefix"), XMLObject,
               GuardableMixin):
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
               PropertySheet.Guard,
               PropertySheet.ActionInformation,
    )

    security.declareProtected(Permissions.AccessContentsInformation,
      'getAvailableCatalogVars')
    def getAvailableCatalogVars(self):
      parent = self.getParentValue()
      res = [parent.getStateVariable()]
      res += [variable.getId() for variable in self.objectValues()]
      res += [variable for variable in
              parent.contentValues(portal_type="Workflow Variable")
              if variable.getForCatalog()]
      res.sort()
      return res

    security.declareProtected(Permissions.ModifyPortalContent,
      'updateDynamicVariable')
    def updateDynamicVariable(self):
      # Keep worklist variables updating, correspond to workflow variables.
      # In the new workflow, we may not need this function for the moment.
      res = []
      # XXX(WORKFLOW): is there a reason not to return self.objectValues() here?
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

      # Check workflow variables:
      for variable_value in self.getParentValue().objectValues(portal_type="Workflow Variable"):
        variable_id = variable_value.getId()
        workflow_variable_id_list.append(variable_id)
        worklist_variable_value = self._getOb(variable_id, None)
        if (worklist_variable_value is None
            and variable_value.getForCatalog() == 1
            and variable_id not in default_variable_id_list):
          variable_value_ref = variable_value.getReference()
          worklist_variable_value = self.newContent(portal_type='Worklist Variable')
          worklist_variable_value.setReference(variable_value_ref)
          worklist_variable_value.setVariableExpression(variable_value.getVariableExpression())
          worklist_variable_value.setVariableValue(variable_value.getVariableValue())
          res.append(worklist_variable_value)
        if (worklist_variable_value and worklist_variable_value not in res
            and variable_value.getForCatalog() == 1):
          res.append(worklist_variable_value)
        if (worklist_variable_value in res
            and variable_value.getForCatalog() == 0):
          self._delObject(variable_id)
          res.remove(worklist_variable_value)

      # Append user created worklist variables.
      for worklist_variable_value in self.objectValues():
        if worklist_variable_value.getId() not in workflow_variable_id_list:
          res.append(worklist_variable_value)
          workflow_variable_id_list.append(worklist_variable_value.getId())
      return res

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getVarMatchKeys')
    def getVarMatchKeys(self):
        key_list = []
        if self.getMatchedPortalTypeList():
          key_list.append('portal_type')
        if self.getMatchedSimulationStateList():
          key_list.append('simulation_state')
        if self.getMatchedValidationStateList():
          key_list.append('validation_state')
        if self.getMatchedCausalityState():
          key_list.append('causality_state')
        
        key_list += [dynamic_variable.getReference() for dynamic_variable in self.objectValues()
         if dynamic_variable.getVariableValue() or dynamic_variable.getVariableExpression()]

        return key_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getVarMatch')
    def getVarMatch(self, id):
        """ return value of matched keys"""
        matches = None
        if id == 'portal_type':
          v = self.getMatchedPortalTypeList()
          if v: matches = tuple(v)
        elif id in ['validation_state', 'simulation_state', 'causality_state']:
          if id == 'validation_state':
            match_reference_list = self.getMatchedValidationStateList()
          elif id == 'simulation_state':
            match_reference_list = self.getMatchedSimulationStateList()
          elif id == 'causality_state':
            match_reference_list = self.getMatchedCausalityStateList()
          matches = tuple(match_reference_list)
        elif id:
          # Local dynamic variable:
          dynamic_variable = self._getOb('variable_'+id)
          dynamic_variable_value = dynamic_variable.getVariableValue()
          if dynamic_variable_value:
            matches = [dynamic_variable_value]
          # Override initial value if expression set:
          dynamic_variable_expression_text = dynamic_variable\
              .getVariableExpression()
          if dynamic_variable_expression_text:
            matches = dynamic_variable_expression_text

        if matches not in ([], None):
          if not isinstance(matches, (tuple, Expression)):
            # Old version, convert it.
            matches = tuple(matches)
          return matches
        else:
          return ()

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getVarMatchText')
    def getVarMatchText(self, id):
        values = self.getVarMatch(id)
        if isinstance(values, Expression):
            return values.text
        return '; '.join(values)

    # XXX(PERF): hack to see Category Tool responsability in new workflow slowness

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getActionType')
    def getActionType(self):
      prefix_length = len('action_type/')
      action_type_list = [path[prefix_length:] for path in self.getCategoryList()
                          if path.startswith('action_type/')]
      try:
        return action_type_list[0]
      except IndexError:
        return None
