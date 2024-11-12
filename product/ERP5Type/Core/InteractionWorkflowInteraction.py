# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Nexedi SARL and Contributors. All Rights Reserved.
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

from Products.ERP5Type import Permissions
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.mixin.guardable import GuardableMixin

class InteractionWorkflowInteraction(IdAsReferenceMixin('interaction_'),
                                     XMLObject,
                                     GuardableMixin):
  """
  An ERP5 Workflow Interaction (Interaction Workflow)
  """
  meta_type = 'ERP5 Interaction'
  portal_type = 'Interaction Workflow Interaction'
  add_permission = Permissions.AddPortalContent

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (
    'Base',
    'XMLObject',
    'CategoryCore',
    'DublinCore',
    'Reference',
    'InteractionWorkflowInteraction',
    'Guard',
  )

  # following getters are redefined for performance improvements
  # they use the categories paths directly and string operations
  # instead of traversing from the portal to get the objects
  # in order to have their id or value
  @security.protected(Permissions.AccessContentsInformation)
  def getBeforeCommitScriptIdList(self):
    """
    returns the list of before commit script ids
    """
    return [path.split('/')[-1] for path in self.getBeforeCommitScriptList()]

  @security.protected(Permissions.AccessContentsInformation)
  def getBeforeCommitScriptValueList(self):
    """
    returns the list of before commit script values
    """
    parent = self.getParentValue()
    return [parent._getOb(transition_id) for transition_id
            in self.getBeforeCommitScriptIdList()]

  @security.protected(Permissions.AccessContentsInformation)
  def getActivateScriptIdList(self):
    """
    returns the list of activate script ids
    """
    return [path.split('/')[-1] for path in self.getActivateScriptList()]

  @security.protected(Permissions.AccessContentsInformation)
  def getActivateScriptValueList(self):
    """
    returns the list of activate script values
    """
    parent = self.getParentValue()
    return [parent._getOb(transition_id) for transition_id
            in self.getActivateScriptIdList()]

  # XXX(PERF): hack to see Category Tool responsability in new workflow slowness
  @security.protected(Permissions.AccessContentsInformation)
  def getActivateScriptList(self):
    """
    returns the list of activate script
    """
    prefix_length = len('activate_script/')
    return [path[prefix_length:] for path in self.getCategoryList()
            if path.startswith('activate_script/')]

  # XXX(PERF): hack to see Category Tool responsability in new workflow slowness
  @security.protected(Permissions.AccessContentsInformation)
  def getBeforeCommitScriptList(self):
    """
    returns the list of before commit script
    """
    prefix_length = len('before_commit_script/')
    return [path[prefix_length:] for path in self.getCategoryList()
            if path.startswith('before_commit_script/')]
