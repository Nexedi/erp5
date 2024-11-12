# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
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

from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.mixin.guardable import GuardableMixin
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import InitializeClass

TRIGGER_AUTOMATIC = 0
TRIGGER_USER_ACTION = 1
TRIGGER_WORKFLOW_METHOD = 2

class WorkflowTransition(IdAsReferenceMixin("transition_"),
                         XMLObject,
                         GuardableMixin):
  """
  A ERP5 Transition.
  """
  meta_type = 'ERP5 Workflow Transition'
  portal_type = 'Workflow Transition'
  add_permission = Permissions.AddPortalContent

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = (
    'Base',
    'XMLObject',
    'CategoryCore',
    'DublinCore',
    'Reference',
    'Comment',
    'SortIndex',
    'WorkflowTransition',
    'Guard',
    'ActionInformation',
  )

  # following getters are redefined for performance improvements
  # they use the categories paths directly and string operations
  # instead of traversing from the portal to get the objects
  # in order to have their id or value

  # XXX(PERF): hack to see Category Tool responsability in new workflow slowness
  @security.protected(Permissions.AccessContentsInformation)
  def getActionType(self):
    for path in self.getCategoryList():
      if path.startswith('action_type/'):
        return path[12:] # 12 is len('action_type/')
    return None

  @security.protected(Permissions.AccessContentsInformation)
  def getBeforeScriptList(self):
    """
    returns the list of before script
    """
    prefix_length = len('before_script/')
    return [path[prefix_length:] for path in self.getCategoryList()
            if path.startswith('before_script/')]

  @security.protected(Permissions.AccessContentsInformation)
  def getAfterScriptList(self):
    """
    returns the list of after script
    """
    prefix_length = len('after_script/')
    return [path[prefix_length:] for path in self.getCategoryList()
            if path.startswith('after_script/')]


  @security.protected(Permissions.AccessContentsInformation)
  def getBeforeScriptIdList(self):
    """
    returns the list of before script ids
    """
    return [path.split('/')[-1] for path in self.getBeforeScriptList()]

  @security.protected(Permissions.AccessContentsInformation)
  def getBeforeScriptValueList(self):
    """
    returns the list of before script values
    """
    parent = self.getParentValue()
    return [parent._getOb(transition_id) for transition_id
            in self.getBeforeScriptIdList()]

  @security.protected(Permissions.AccessContentsInformation)
  def getAfterScriptIdList(self):
    """
    returns the list of after script ids
    """
    return [path.split('/')[-1] for path in self.getAfterScriptList()]

  @security.protected(Permissions.AccessContentsInformation)
  def getAfterScriptValueList(self):
    """
    returns the list of after script values
    """
    parent = self.getParentValue()
    return [parent._getOb(transition_id) for transition_id
            in self.getAfterScriptIdList()]

  @security.protected(Permissions.AccessContentsInformation)
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

  @security.protected(Permissions.AccessContentsInformation)
  def getTransitionVariableValueList(self):
    """
    Return Transition Variables
    """
    return self.objectValues(portal_type='Workflow Transition Variable')

from Products.ERP5Type import WITH_LEGACY_WORKFLOW
if WITH_LEGACY_WORKFLOW:
  from Products.ERP5Type.Utils import deprecated
  from ComputedAttribute import ComputedAttribute

  WorkflowTransition.actbox_url = ComputedAttribute(
    deprecated('`actbox_url` is deprecated; use getAction()')\
              (lambda self: self.getAction()))
  WorkflowTransition.security.declareProtected(Permissions.AccessContentsInformation,
                                       'actbox_url')

  WorkflowTransition.actbox_name = ComputedAttribute(
    deprecated('`actbox_name` is deprecated; use getActionName()')\
              (lambda self: self.getActionName()))
  WorkflowTransition.security.declareProtected(Permissions.AccessContentsInformation,
                                       'actbox_name')

InitializeClass(WorkflowTransition)
