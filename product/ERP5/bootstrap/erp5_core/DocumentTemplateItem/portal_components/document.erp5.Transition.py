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
from Products.DCWorkflow.DCWorkflow import ObjectDeleted, ObjectMoved
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Accessor.Base import _evaluateTales
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
from Products.ERP5Type.patches.DCWorkflow import ValidationFailed
from Products.ERP5Type.patches.WorkflowTool import WorkflowHistoryList
from Products.ERP5Type.Utils import convertToUpperCase, convertToMixedCase
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Workflow.mixin.guardable import GuardableMixin
from zLOG import LOG, ERROR, DEBUG, WARNING

TRIGGER_AUTOMATIC = 0
TRIGGER_USER_ACTION = 1
TRIGGER_WORKFLOW_METHOD = 2

class Transition(IdAsReferenceMixin("transition_", "prefix"), XMLObject,
                 GuardableMixin):
  """
  A ERP5 Transition.
  """

  meta_type = 'ERP5 Transition'
  portal_type = 'Transition'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  trigger_type = TRIGGER_USER_ACTION #zwj: type is int 0, 1, 2
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
             PropertySheet.SortIndex,
             PropertySheet.Transition,
             PropertySheet.Guard,
             PropertySheet.ActionInformation,
  )

  # following getters are redefined for performance improvements
  # they use the categories paths directly and string operations
  # instead of traversing from the portal to get the objects
  # in order to have their id or value

  # XXX(PERF): hack to see Category Tool responsability in new workflow slowness
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getActionType')
  def getActionType(self):
    for path in self.getCategoryList():
      if path.startswith('action_type/'):
        return path[12:] # 12 is len('action_type/')
    return None

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getBeforeScriptList')
  def getBeforeScriptList(self):
    """
    returns the list of before script
    """
    prefix_length = len('before_script/')
    return [path[prefix_length:] for path in self.getCategoryList()
            if path.startswith('before_script/')]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAfterScriptList')
  def getAfterScriptList(self):
    """
    returns the list of after script
    """
    prefix_length = len('after_script/')
    return [path[prefix_length:] for path in self.getCategoryList()
            if path.startswith('after_script/')]


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getBeforeScriptIdList')
  def getBeforeScriptIdList(self):
    """
    returns the list of before script ids
    """
    return [path.split('/')[-1] for path in self.getBeforeScriptList()]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getBeforeScriptValueList')
  def getBeforeScriptValueList(self):
    """
    returns the list of before script values
    """
    parent = self.getParentValue()
    return [parent._getOb(transition_id) for transition_id
            in self.getBeforeScriptIdList()]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAfterScriptIdList')
  def getAfterScriptIdList(self):
    """
    returns the list of after script ids
    """
    return [path.split('/')[-1] for path in self.getAfterScriptList()]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAfterScriptValueList')
  def getAfterScriptValueList(self):
    """
    returns the list of after script values
    """
    parent = self.getParentValue()
    return [parent._getOb(transition_id) for transition_id
            in self.getAfterScriptIdList()]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDestinationValue')
  def getDestinationValue(self):
    """
    returns the destination object
    """

    destination_path_list = [path for path in self.getCategoryList()
                             if path.startswith('destination/')]
    if destination_path_list:
      destination_id = destination_path_list[0].split('/')[-1]
      parent = self.getParentValue()
      return parent._getOb(destination_id)
    return None
