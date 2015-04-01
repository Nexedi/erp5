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

import sys

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from copy import deepcopy
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import ObjectDeleted, ObjectMoved
from Products.DCWorkflow.Guard import Guard
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Accessor.Base import _evaluateTales
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
from Products.ERP5Type.patches.DCWorkflow import ValidationFailed
from Products.ERP5Type.patches.WorkflowTool import WorkflowHistoryList
from Products.ERP5Type.Utils import convertToUpperCase, convertToMixedCase
from Products.ERP5Type.XMLObject import XMLObject
from zLOG import LOG, ERROR, DEBUG, WARNING

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

