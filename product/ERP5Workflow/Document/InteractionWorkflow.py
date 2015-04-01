##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
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

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Workflow.Document.Workflow import Workflow
import transaction
from Products.ERP5Type import Globals
import App
from types import StringTypes
from AccessControl import getSecurityManager, ClassSecurityInfo
from AccessControl.SecurityManagement import setSecurityManager
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.ERP5Workflow.Document.Transition import TRIGGER_WORKFLOW_METHOD
from Products.DCWorkflow.Expression import StateChangeInfo
from Products.ERP5Type.Workflow import addWorkflowFactory
from Products.CMFActivity.ActiveObject import ActiveObject
from Products.ERP5Type.patches.Expression import Expression_createExprContext
from Products.ERP5Type.Globals import PersistentMapping
from zLOG import LOG, ERROR, WARNING


_MARKER = []

class InteractionWorkflow(XMLObject):
  """
  An ERP5 Interaction Workflow.
  """

  meta_type = 'ERP5 Workflow'
  portal_type = 'Interaction Workflow'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  ### zwj: for security issue
  managed_permission_list = ()
  managed_role = ()

  intaractions = None
  manager_bypass = 0

  

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.XMLObject,
    PropertySheet.CategoryCore,
    PropertySheet.DublinCore,
    PropertySheet.InteractionWorkflow,
  )


  def initializeDocument(self, document):
    pass

  security.declareProtected(Permissions.View, 'getChainedPortalTypeList')
  def getChainedPortalTypeList(self):
    """Returns the list of portal types that are chained to this
    interaction workflow."""
    chained_ptype_list = []
    wf_tool = getToolByName(self, 'portal_workflow')
    types_tool = getToolByName(self, 'portal_types')
    for ptype in types_tool.objectValues():
      if self.getId() in ptype.getTypeERP5WorkflowList(): ### getRef
        chained_ptype_list.append(ptype.getId())
    return chained_ptype_list

  security.declarePrivate('listObjectActions')
  def listObjectActions(self, info):
    return []

  security.declarePrivate('_changeStateOf')
  def _changeStateOf(self, ob, tdef=None, kwargs=None) :
    """
    InteractionWorkflow is stateless. Thus, this function should do nothing.
    """
    return

  security.declarePrivate('isInfoSupported')
  def isInfoSupported(self, ob, name):
    '''
    Returns a true value if the given info name is supported.
    '''
    vdef = self._getOb(name, None) ### getObjectByRef
    if vdef is not None:
      if vdef.getTypeInfo().getId() == 'Variable':
        return 1
      return 0
    return 0

  security.declarePrivate('getInfoFor')
  def getInfoFor(self, ob, name, default):
    '''
    Allows the user to request information provided by the
    workflow.  This method must perform its own security checks.
    '''
    vdef = self._getOb(name, _MARKER) ### getObjectByRef
    if vdef is _MARKER:
      return default
    if vdef.info_guard is not None and not vdef.info_guard.check(
      getSecurityManager(), self, ob):
      return default
    status = self.getCurrentStatusDict(ob)
    if status is not None and name in status:
      value = status[name]
    # Not set yet.  Use a default.
    elif vdef.default_expr is not None:
      ec = Expression_createExprContext(StateChangeInfo(ob, self, status))
      value = vdef.default_expr(ec)
    else:
      value = vdef.default_value

    return value

  def isERP5WorkflowMethodSupported(self, ob, tdef):
    '''
    Returns a true value if the given workflow method
    is supported in the current state.
    '''
    LOG(' Trigger %s passing guard'%(tdef.getId()), WARNING,'in InteractionWorkflow.py') ### getRef
    if tdef is not None and self._checkTransitionGuard(tdef, ob):
      return 1
    return 0

  def _checkTransitionGuard(self, tdef, document, **kw):
    guard = tdef.getGuard()
    if guard is None:
      return 1
    if guard.check(getSecurityManager(), self, document, **kw):
      return 1
    return 0

  def _getObjectByRef(self, ref):
    for ob in self:
      if wf.getRef() == ref:
        return ob
    return None

  def getValidRoleList(self):
    return sorted(self.getPortalObject().getDefaultModule('acl_users').valid_roles())

  def _updateWorkflowHistory(self, document, status_dict):
    """
    Change the state of the object.
    """
    # Create history attributes if needed
    if getattr(aq_base(document), 'workflow_history', None) is None:
      document.workflow_history = PersistentMapping()
      # XXX this _p_changed is apparently not necessary
      document._p_changed = 1

    # Add an entry for the workflow in the history
    workflow_key = self._generateHistoryKey()
    if not document.workflow_history.has_key(workflow_key):
      document.workflow_history[workflow_key] = ()

    # Update history
    document.workflow_history[workflow_key] += (status_dict,)

  def getStateChangeInformation(self, document, state, transition=None):
    """
    Return an object used for variable tales expression.
    """
    if transition is None:
      transition_url = None
    else:
      transition_url = transition.getRelativeUrl()
    return self.asContext(document=document,
                          transition=transition,
                          transition_url=transition_url,
                          state=state)

  def getCurrentStatusDict(self, document):
    """
    Get the current status dict.
    """
    workflow_key = self._generateHistoryKey()

    # Copy is requested
    result = document.workflow_history[workflow_key][-1].copy()
    return result

  def _generateHistoryKey(self):
    """
    Generate a key used in the workflow history.
    """
    history_key = self.unrestrictedTraverse(self.getRelativeUrl()).getId() ### getRef
    return history_key

  def getWorklistVariableMatchDict(self, info, check_guard=True):
    return None

  def _getWorkflowStateOf(self, ob, id_only=0):
    return None