##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
#               2015 Wenjie Zheng <wenjie.zheng@tiolive.com>
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
from Acquisition import aq_base
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Accessor.Base import _evaluateTales
from Products.ERP5Type.Globals import PersistentMapping
from Products.DCWorkflow.Expression import StateChangeInfo
from zLOG import LOG, ERROR, DEBUG, WARNING
from Products.ERP5Type.Utils import convertToUpperCase, convertToMixedCase
from Products.DCWorkflow.DCWorkflow import ObjectDeleted, ObjectMoved
from Products.ERP5Type.patches.DCWorkflow import ValidationFailed
from copy import deepcopy
import sys
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.patches.WorkflowTool import WorkflowHistoryList
from Products.ERP5Type.patches.Expression import Expression_createExprContext
from Products.DCWorkflow.Guard import Guard
from Products.CMFCore.Expression import Expression
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin

TRIGGER_AUTOMATIC = 0
TRIGGER_USER_ACTION = 1
TRIGGER_WORKFLOW_METHOD = 2

class Transition(IdAsReferenceMixin("transition_", "prefix"), XMLObject):
  """
  A ERP5 Transition.
  """

  meta_type = 'ERP5 Transition'
  portal_type = 'Transition'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  trigger_type = TRIGGER_USER_ACTION #zwj: type is int 0, 1, 2
  guard = None
  actbox_name = ''
  actbox_url = ''
  actbox_icon = ''
  actbox_category = 'workflow'
  var_exprs = None  # A mapping.
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
             PropertySheet.Transition,
  )

  def getGuardSummary(self):
    res = None
    if self.guard is not None:
      res = self.guard.getSummary()
    return res

  def getGuard(self):
    if self.guard is None:
      self.generateGuard()
    return self.guard ### only generate gurad when self is a User Action
      #return Guard().__of__(self)  # Create a temporary guard.

  def getVarExprText(self, id):
    if not self.var_exprs:
      return ''
    else:
      expr = self.var_exprs.get(id, None)
      if expr is not None:
        return expr.text
      else:
        return ''

  def generateGuard(self):
    if self.trigger_type == TRIGGER_USER_ACTION:
      if self.guard == None:
        self.guard = Guard(permissions=self.getPermissionList(),
                      roles=self.getRoleList(),
                      groups=self.getGroupList(),
                      expr=self.getExpression())
      else:
        if self.guard.roles != self.getRoleList():
          self.guard.roles = self.getRoleList()
        if self.guard.permissions != self.getPermissionList():
          self.guard.permissions = self.getPermissionList()
        if self.guard.groups != self.getGroupList():
          self.guard.groups = self.getGroupList()
        if self.guard.expr != self.getExpression():
          self.guard.expr = self.getExpression()

  def execute(self, document, form_kw=None):
    """
    Execute transition.
    """
    sci = None
    econtext = None
    moved_exc = None
    validation_exc = None
    tool = getToolByName(self, 'portal_workflow')

    # Figure out the old and new states.
    if form_kw is None:
      form_kw = {}
    workflow = self.getParentValue()

    ### get related history
    state_var = workflow.getStateVariable()
    status_dict = workflow.getCurrentStatusDict(document)
    state_object = workflow._getWorkflowStateOf(document, id_only=0)

    if state_object == None:
      state_object = workflow.getSourceValue()

    old_state = state_object.getId()
    old_sdef = state_object

    new_state = self.getDestinationId()

    if new_state is None:
        #new_state = workflow.getSourceId()
        new_state = old_state
        if not new_state:
            # Do nothing if there is no initial state. We may want to create
            # workflows with no state at all, only for worklists.
            return
        former_status = {}
    else:
        former_status = state_object.getId()

    try:
        new_sdef = self.getDestinationValue()
    except KeyError:
        raise WorkflowException('Destination state undefined: ' + new_state)

    LOG(" 168 object '%s' will change from state '%s' to '%s'"%(document.getId(), old_state, new_state), WARNING, " in Transition.py")

    # Execute the "before" script.
    before_script_success = 1
    script_id = self.getBeforeScriptId()
    if script_id:
      script = self.getParent()._getOb(script_id)
      # Pass lots of info to the script in a single parameter.
      kwargs = form_kw
      sci = StateChangeInfo(
            document, workflow, former_status, self, old_sdef, new_sdef, kwargs)
      try:
        #LOG('_executeTransition', 0, "script = %s, sci = %s" % (repr(script), repr(sci)))
        script.execute(sci)  # May throw an exception.
      except ValidationFailed, validation_exc:
        before_script_success = 0
        before_script_error_message = deepcopy(validation_exc.msg)
        validation_exc_traceback = sys.exc_traceback
      except ObjectMoved, moved_exc:
        ob = moved_exc.getNewObject()
        # Re-raise after transition

    # Do not proceed in case of failure of before script
    if not before_script_success:
      former_status = old_state # Remain in state
      tool.setStatusOf(workflow.getReference(), document, status_dict)
      sci = StateChangeInfo(
        document, workflow, former_status, self, old_sdef, new_sdef, kwargs)
        # put the error message in the workflow history
      sci.setWorkflowVariable(error_message=before_script_error_message)
      if validation_exc :
        # reraise validation failed exception
        raise validation_exc, None, validation_exc_traceback
      return old_state

    # update state
    state = self.getDestination()
    if state is None:
      state = old_sdef
    state_var = workflow.getStateVariable()
    #document.setCategoryMembership(state_var, state)

    status_dict['undo'] = 0

    # Modify workflow history
    status_dict[state_var] = '_'.join(new_state.split('_')[1:])
    object = workflow.getStateChangeInformation(document, state_object, transition=self)

    # update variables =========================================================
    state_values = None

    if new_sdef is not None:
      state_values = new_sdef.objectValues(portal_type='Variable')
    if state_values is None:
      state_values = {}

    tdef_exprs = self.objectValues(portal_type='Variable')
    if tdef_exprs is None:
      tdef_exprs = {}

    for vdef in workflow.objectValues(portal_type='Variable'):
      id = vdef.getId()
      id_no_suffix = '_'.join(id.split('_')[1:])
      if vdef.for_status == 0:
        continue
      expr = None
      if id_no_suffix in state_values:
        value = state_values[id_no_suffix]
      elif id in tdef_exprs:
        expr = tdef_exprs[id]
      elif not vdef.update_always and id in former_status:
        # Preserve former value
        value = former_status[id]
      else:
        if vdef.default_expr is not None:
          expr = vdef.default_expr
        else:
          value = vdef.default_value
      if expr is not None:
        # Evaluate an expression.
        if econtext is None:
          # Lazily create the expression context.
          if sci is None:
            kwargs = form_kw
            sci = StateChangeInfo(
                document, workflow, former_status, self,
                old_sdef, new_sdef, kwargs)
          econtext = Expression_createExprContext(sci)
        expr = Expression(expr)
        value = expr(econtext)
      if id_no_suffix == "action":
        status_dict[id_no_suffix] = '_'.join(value.split('_')[1:])
      else:
        status_dict[id_no_suffix] = value

    # Update all transition variables
    if form_kw is not None:
      object.REQUEST.other.update(form_kw)

    for variable in self.objectValues(portal_type='Transition Variable'):
      status_dict[variable.getCausalityTitle()] = variable.getInitialValue(object=object)

    # Generate Workflow History List
    tool.setStatusOf(workflow.getReference(), document, status_dict)

    ### zwj: update Role mapping, also in Workflow, initialiseDocument()
    workflow.updateRoleMappingsFor(document)
    # Execute the "after" script.
    script_id = self.getAfterScriptId()
    if script_id is not None:
      kwargs = form_kw
      # Script can be either script or workflow method
      if script_id in old_sdef.getDestinationIdList():
        getattr(workflow, convertToMixedCase(script_id)).execute(document)
      else:
        script = self.getParent()._getOb(script_id)
        # Pass lots of info to the script in a single parameter.
        if script.getTypeInfo().getId() == 'Workflow Script':
          sci = StateChangeInfo(
              document, workflow, former_status, self, old_sdef, new_sdef, kwargs)
          script.execute(sci)  # May throw an exception.
        else:
          raise NotImplementedError ('Unsupported Script %s for state %s'%(script_id, old_sdef.getId())) ### getRef
    # Return the new state object.
    if moved_exc is not None:
        # Propagate the notification that the object has moved.
        raise moved_exc
    else:
        return new_sdef

  def _checkPermission(self, document):
    """
    Check if transition is allowed.
    """
    expr_value = self.getGuardExpression(evaluate=0)
    if expr_value is not None:
      # do not use 'getGuardExpression' to calculate tales because
      # it caches value which is bad. Instead do it manually
      value = _evaluateTales(document, expr_value)
    else:
      value = True
    #print "CALC", expr_value, '-->', value
    return value
