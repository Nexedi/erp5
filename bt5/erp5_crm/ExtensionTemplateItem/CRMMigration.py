##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5Type.patches.WorkflowTool import WorkflowHistoryList

def migrateEventWorkflowHistory(self):
  portal_type = self.getPortalType()
  portal = self.getPortalObject()
  if portal_type not in portal.getPortalEventTypeList():
    return
  workflow_history = getattr(self, 'workflow_history', None)
  if workflow_history is None:
    return
  event_workflow = workflow_history.get('event_workflow', None)
  if event_workflow is None:
    return
  event_simulation_workflow = workflow_history.get('event_simulation_workflow', None)
  if event_simulation_workflow is not None:
    # already migrated.
    return
  self.workflow_history['event_simulation_workflow'] = \
      WorkflowHistoryList(event_workflow[:])
  migrate_state_dict = {
    'acknowledged':'delivered',
    'assigned':'stopped',
    'expired':'delivered',
    'new':'stopped',
    'ordered':'confirmed',
    'responded':'delivered',
  }
  current_state = event_workflow[-1]['simulation_state']
  new_state = migrate_state_dict.get(current_state, None)
  if new_state is None:
    # no need to change the state.
    return
  workflow_tool = portal.portal_workflow
  workflow_tool._jumpToStateFor(self, new_state)
  return 'Event workflow migration on %s : %s -> %s' % (
      self.getPath(), current_state, new_state)
