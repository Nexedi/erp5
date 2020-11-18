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
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
from Products.ERP5Type.XMLObject import XMLObject
#from Products.ERP5Workflow.Document.Transition import TRIGGER_WORKFLOW_METHOD
TRIGGER_WORKFLOW_METHOD = 2
from Products.ERP5Workflow.mixin.guardable import GuardableMixin

class Interaction(IdAsReferenceMixin('interaction_', "prefix"), XMLObject,
                  GuardableMixin):

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
  state_permission_roles = {} # { permission: [role] or (role,) }
  manager_bypass = 0
  trigger_method_id = None
  trigger_type = TRIGGER_WORKFLOW_METHOD
  portal_type_filter = None
  portal_type_group_filter = None
  trigger_once_per_transaction = False
  temporary_document_disallowed = False
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
    PropertySheet.Interaction,
    PropertySheet.Guard,
  )

  # following getters are redefined for performance improvements
  # they use the categories paths directly and string operations
  # instead of traversing from the portal to get the objects
  # in order to have their id or value
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getBeforeCommitScriptIdList')
  def getBeforeCommitScriptIdList(self):
    """
    returns the list of before commit script ids
    """
    return [path.split('/')[-1] for path in self.getBeforeCommitScriptList()]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getBeforeCommitScriptValueList')
  def getBeforeCommitScriptValueList(self):
    """
    returns the list of before commit script values
    """
    parent = self.getParentValue()
    return [parent._getOb(transition_id) for transition_id
            in self.getBeforeCommitScriptIdList()]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getActivateScriptIdList')
  def getActivateScriptIdList(self):
    """
    returns the list of activate script ids
    """
    return [path.split('/')[-1] for path in self.getActivateScriptList()]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getActivateScriptValueList')
  def getActivateScriptValueList(self):
    """
    returns the list of activate script values
    """
    parent = self.getParentValue()
    return [parent._getOb(transition_id) for transition_id
            in self.getActivateScriptIdList()]

  # XXX(PERF): hack to see Category Tool responsability in new workflow slowness
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getActivateScriptList')
  def getActivateScriptList(self):
    """
    returns the list of activate script
    """
    prefix_length = len('activate_script/')
    return [path[prefix_length:] for path in self.getCategoryList()
            if path.startswith('activate_script/')]

  # XXX(PERF): hack to see Category Tool responsability in new workflow slowness
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getBeforeCommitScriptList')
  def getBeforeCommitScriptList(self):
    """
    returns the list of before commit script
    """
    prefix_length = len('before_commit_script/')
    return [path[prefix_length:] for path in self.getCategoryList()
            if path.startswith('before_commit_script/')]
