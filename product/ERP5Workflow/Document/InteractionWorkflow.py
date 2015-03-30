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

  security.declareProtected(Permissions.View, 'getChainedPortalTypeList')
  def getChainedPortalTypeList(self):
    """Returns the list of portal types that are chained to this
    interaction workflow."""
    chained_ptype_list = []
    wf_tool = getToolByName(self, 'portal_workflow')
    types_tool = getToolByName(self, 'portal_types')
    for ptype in types_tool.objectValues():
      if self.getId() in ptype.getTypeERP5WorkflowList():
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
    vdef = self._getOb(name, None)
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
    vdef = self._getOb(name, _MARKER)
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

  def isERP5WorkflowMethodSupported(self, ob, method_id):
    '''
    Returns a true value if the given workflow method
    is supported in the current state.
    '''
    tdef = self._getOb(method_id, None)
    return tdef is not None and self._checkTransitionGuard(tdef, ob)

  def execute(self): ### zwj: execute interaction, check Transition.py/execute
    pass

  def _before_commit(self, sci, script_name, security_manager):
    # check the object still exists before calling the script
    ob = sci.object
    while ob.isTempObject():
      ob = ob.getParentValue()
    if aq_base(self.unrestrictedTraverse(ob.getPhysicalPath(), None)) is \
       aq_base(ob):
      current_security_manager = getSecurityManager()
      try:
        # Who knows what happened to the authentication context
        # between here and when the interaction was executed... So we
        # need to switch to the security manager as it was back then
        setSecurityManager(security_manager)
        self._getOb(script_name)(sci)
      finally:
        setSecurityManager(current_security_manager)

  security.declarePrivate('activeScript')
  def activeScript(self, script_name, ob_url, status, tdef_id):
    script =self._getOb(script_name)
    ob = self.unrestrictedTraverse(ob_url)
    tdef = self._getOb(tdef_id)
    sci = StateChangeInfo(
                  ob, self, status, tdef, None, None, None)
    script(sci)

  def _checkTransitionGuard(self, t, ob, **kw):
    # This check can be implemented with a guard expression, but
    # it has a lot of overhead to use a TALES, so we make a special
    # treatment for the frequent case, that is, disallow the trigger
    # on a temporary document.
    if t.temporary_document_disallowed:
      isTempDocument = getattr(ob, 'isTempDocument', None)
      if isTempDocument is not None:
        if isTempDocument():
          return 0

    return Workflow._checkTransitionGuard(self, t, ob, **kw)

  def getValidRoleList(self):
    return sorted(self.getPortalObject().getDefaultModule('acl_users').valid_roles())
