# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Danièle Vanbaelinghem <daniele@gmail.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from erp5.component.module.ERP5Conduit import ERP5Conduit
from Products.ERP5Type import Permissions
from AccessControl import ClassSecurityInfo

# Declarative security
security = ClassSecurityInfo()

WORKFLOW_ACTION_NOT_ADDABLE = 0
WORKFLOW_ACTION_ADDABLE = 1
WORKFLOW_ACTION_INSERTABLE = 2

class ERP5DocumentConduit(ERP5Conduit):
  """
  ERP5DocumentConduit specialise generic Conduit
  to produce adhoc GID.
  The GID is composed by the concatenation of "reference-version-language"
  """

  # Declarative security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation, 'getGidFromObject')
  def getGidFromObject(self, object): # pylint: disable=redefined-builtin
    """
    return the Gid generate with the reference, object, language of the object
    """
    return "%s-%s-%s" %\
             (object.getReference(), object.getVersion(), object.getLanguage())


  def isWorkflowActionAddable(self, document, status, wf_id):
    """
    Some checking in order to check if we should add the workfow or not
    We should not returns a conflict list as we wanted before, we should
    instead go to a conflict state.
    """
    # We first test if the status in not already inside the workflow_history
    wf_history = document.workflow_history
    if wf_id in wf_history:
      action_list = wf_history[wf_id]
    else:
      return WORKFLOW_ACTION_ADDABLE
    addable = WORKFLOW_ACTION_ADDABLE
    for action in action_list:
      this_one = WORKFLOW_ACTION_ADDABLE
      # if time <= action.get('time'):
      #   # action in the past are not appended
      #   addable = WORKFLOW_ACTION_INSERTABLE
      key_list = list(action.keys())
      # key_list.remove("time")
      # XXX-AUREL For document it seems that checking time != is required
      # I don't know why ?
      for key in key_list:
        if status[key] != action[key]:
          this_one = WORKFLOW_ACTION_NOT_ADDABLE
          break
      if this_one:
        addable = WORKFLOW_ACTION_NOT_ADDABLE
        break
    return addable

