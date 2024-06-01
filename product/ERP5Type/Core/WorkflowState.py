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

from AccessControl import ClassSecurityInfo
from Persistence import PersistentMapping
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
from Products.ERP5Type.XMLObject import XMLObject

class WorkflowState(IdAsReferenceMixin("state_"),
                    XMLObject):
  """
  A ERP5 State.
  """
  meta_type = 'ERP5 Workflow State'
  portal_type = 'Workflow State'
  add_permission = Permissions.AddPortalContent

  state_permission_role_list_dict = None

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
    'WorkflowState',
  )

  # XXX(PERF): hack to see Category Tool responsability in new workflow slowness
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDestinationList')
  def getDestinationList(self):
    """
    this getter is redefined to improve performance:
    instead of getting all the transition objects from the destination list
    to then use their ids, extract the information from the string
    """
    prefix_length = len('destination/')
    return [path[prefix_length:] for path in self.getCategoryList()
            if path.startswith('destination/')]


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDestinationIdList')
  def getDestinationIdList(self):
    """
    this getter is redefined to improve performance:
    instead of getting all the transition objects from the destination list
    to then use their ids, extract the information from the string
    """
    return [path.split('/')[-1] for path in self.getCategoryList()
            if path.startswith('destination/')]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDestinationValueList')
  def getDestinationValueList(self):
    """
    this getter is redefined to improve performance:
    instead of getting all the transition objects from the destination list
    to then use their ids, extract the information from the string
    """
    parent = self.getParentValue()
    return [parent._getOb(destination_id) for destination_id in
            self.getDestinationIdList()]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAcquirePermissionList')
  def getAcquirePermissionList(self):
    """
    acquire all permissions if not yet configured, like DCWorkflow
    """
    if not self.state_permission_role_list_dict:
      return self.getWorkflowManagedPermissionList()
    else:
      return self._baseGetAcquirePermissionList()

  security.declareProtected(Permissions.ModifyPortalContent,
                            'setStatePermissionRoleListDict')
  def setStatePermissionRoleListDict(self, permission_roles):
    """
    create a dict containing the state's permission (as key) and its
    associated role list (value)
    use a PersistentMapping so that the ZODB is updated
    when this dict is changed
    """
    self.state_permission_role_list_dict = PersistentMapping(
        {k: tuple(v) for (k, v) in permission_roles.items()})

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getStatePermissionRoleListDict')
  def getStatePermissionRoleListDict(self):
    """
    return the permission/roles dict
    """
    state_permission_role_list_dict_get = (self.state_permission_role_list_dict or {}).get
    return {k: state_permission_role_list_dict_get(k, ())
            for k in self.getWorkflowManagedPermissionList()}

  security.declareProtected(Permissions.ModifyPortalContent,
                            'setPermission')
  def setPermission(self, permission, roles, REQUEST=None):
    """
    Set a permission for this State.
    """
    if self.state_permission_role_list_dict is None:
      self.state_permission_role_list_dict = PersistentMapping()
    self.state_permission_role_list_dict[permission] = tuple(sorted(roles))

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAvailableTypeList')
  def getAvailableTypeList(self):
    """
    This is a method specific to ERP5. This returns a list of state types,
    which are used for portal methods.
    """
    return ('draft_order',
            'planned_order',
            'future_inventory',
            'reserved_inventory',
            'transit_inventory',
            'current_inventory')

from Products.ERP5Type import WITH_LEGACY_WORKFLOW
if WITH_LEGACY_WORKFLOW:
  from Products.ERP5Type.Utils import deprecated

  WorkflowState.getTransitions = \
    deprecated('getTransitions() is deprecated; use getDestinationIdList()')\
              (lambda self: self.getDestinationIdList())
  WorkflowState.security.declareProtected(Permissions.AccessContentsInformation, 'getTransitions')

  from ComputedAttribute import ComputedAttribute
  WorkflowState.transitions = ComputedAttribute(
    deprecated('`transitions` is deprecated; use getDestinationValueList()')\
              (WorkflowState.getDestinationIdList),
    1) # must be Acquisition-wrapped
  WorkflowState.security.declareProtected(Permissions.AccessContentsInformation, 'transitions')

InitializeClass(WorkflowState)
