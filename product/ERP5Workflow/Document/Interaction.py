##############################################################################
#
# Copyright (c) 2015 Nexedi SARL and Contributors. All Rights Reserved.
#                    Wenjie Zheng <wenjie.zheng@tiolive.com>
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

import transaction

from AccessControl import getSecurityManager, ClassSecurityInfo
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.Expression import Expression
from Products.DCWorkflow.Guard import Guard
from Products.ERP5Type import Globals, Permissions, PropertySheet
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
from Products.ERP5Type.Permissions import ManagePortal
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Workflow.Document.Transition import TRIGGER_WORKFLOW_METHOD,\
                                                      TRIGGER_USER_ACTION
from zLOG import LOG, INFO, ERROR, WARNING

class Interaction(IdAsReferenceMixin('interaction_', "prefix"), XMLObject):

  """
  An ERP5 Interaction.
  """

  meta_type = 'ERP5 Interaction'
  portal_type = 'Interaction'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  managed_permission_list = ()
  managed_role = ()
  erp5_permission_roles = {} # { permission: [role] or (role,) }
  manager_bypass = 0
  method_id = None
  trigger_type = TRIGGER_WORKFLOW_METHOD
  script_name = ()  # Executed before transition
  after_script_name = ()  # Executed after transition
  before_commit_script_name = () #Executed Before Commit Transaction
  activate_script_name = ()  # Executed as activity
  portal_type_filter = None
  portal_type_group_filter = None
  once_per_transaction = False
  temporary_document_disallowed = False
  var_exprs = None  # A mapping.
  guard = None
  default_reference = ''

  # these attributes are definded in old interaction but no evidence that
  # they are in use
  actbox_name = ''
  actbox_url = ''
  actbox_category = 'workflow'

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
    PropertySheet.Interaction,
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

  def getMethodId(self):
    if type(self.method_id) is type(''):
      self.method_id = self.method_id.split()
    return self.method_id
