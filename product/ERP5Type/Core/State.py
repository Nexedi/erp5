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
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5Type.XMLObject import XMLObject

class CustomStorageMatrixMixin(XMLMatrix):
  """
  Prototype of a mixin allowing to have custom storage for matrix
  """
  def newCellContent(self, cell_id, **kw):
    """
    Creates a new content as a matrix box cell.
    """
    cell = self.newContent(id=cell_id, temp_object=True, **kw)
    self.updateCellFromCustomStorage(cell)
    return cell

  def getCell(self, *kw , **kwd):
    return self.newCell(*kw , **kwd)

class State(IdAsReferenceMixin("state_"),
            XMLObject,
            CustomStorageMatrixMixin):
  """
  A ERP5 State.
  """
  meta_type = 'ERP5 State'
  portal_type = 'State'
  add_permission = Permissions.AddPortalContent

  # TODO-ERP5Workflow: Shouldn't it be in a Property Sheet?
  state_permission_roles_dict = {}

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = (
    'Base',
    'XMLObject',
    'CategoryCore',
    'DublinCore',
    'Reference',
    'SortIndex',
    'State',
  )

  def addPossibleTransition(self, tr_ref):
    possible_transition_list = self.getCategoryList()
    transition = self.getParentValue()._getOb('transition_'+tr_ref, None)
    if transition is not None:
      tr_path = 'destination/' + '/'.join(transition.getPath().split('/')[2:])
      possible_transition_list.append(tr_path)
      self.setCategoryList(possible_transition_list)


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
                            'setStatePermissionRolesDict')
  def setStatePermissionRolesDict(self, permission_roles):
    """
    create a dict containing the state's permission (as key) and its
    associated role list (value)
    use a PersistentMapping so that the ZODB is updated
    when this dict is changed
    """
    self.state_permission_roles_dict = PersistentMapping(permission_roles)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'getStatePermissionRolesDict')
  def getStatePermissionRolesDict(self):
    """
    return the permission/roles dict
    """
    if self.state_permission_roles_dict is None:
      return {}
    return self.state_permission_roles_dict

  security.declareProtected(Permissions.ModifyPortalContent,
                            'setPermission')
  def setPermission(self, permission, acquired, roles, REQUEST=None):
    """
    Set a permission for this State.
    """
    self.state_permission_roles_dict[permission] = list(roles)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAvailableTypeList')
  def getAvailableTypeList(self):
    """
    This is a method specific to ERP5. This returns a list of state types,
    which are used for portal methods.
    """
    return (
            'draft_order',
            'planned_order',
            'future_inventory',
            'reserved_inventory',
            'transit_inventory',
            'current_inventory',
            )

  security.declareProtected(Permissions.ModifyPortalContent,
                            'updateCellFromCustomStorage')
  def updateCellFromCustomStorage(self, cell, **kw):
    """
    Creates a new content as a matrix box cell.
    """
    cell_permission = cell._getPermission()
    cell_role = cell._getRole()
    cell.selected = cell_role in self.getStatePermissionRolesDict()[cell_permission]

from Products.ERP5Type import WITH_DC_WORKFLOW_BACKWARD_COMPATIBILITY
if WITH_DC_WORKFLOW_BACKWARD_COMPATIBILITY:
  from Products.ERP5Type.Utils import deprecated

  State.getTransitions = deprecated(
    'getTransitions() is deprecated; use getDestinationIdList()')\
    (State.getDestinationIdList)
  State.security.declareProtected(Permissions.AccessContentsInformation, 'getTransitions')

  State.transitions = deprecated(
    '`transitions` is deprecated; use getDestinationValueList()')\
    (State.getDestinationIdList)
  State.security.declareProtected(Permissions.AccessContentsInformation, 'transitions')

InitializeClass(State)
