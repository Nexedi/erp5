##############################################################################
#
# Copyright (c) 2025 Nexedi KK and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestERP5SiteMethod(ERP5TypeTestCase):

  def getTitle(self):
    return 'ERP5Site Method Test'

  def beforeTearDown(self):
    if getattr(self.portal.portal_workflow, 'nobody_use_this_workflow', None) is not None:
      self.portal.portal_workflow.manage_delObjects(ids=['nobody_use_this_workflow'])
    if getattr(self.portal.portal_types, 'Do Not Use Me', None) is not None:
      self.portal.portal_types.manage_delObjects(ids=['Do Not Use Me'])
    self.portal.portal_caches.erp5_content_medium.clearCache()

  def test_do_not_use_unused_workflow_to_classify_state_type(self):
    """
    Make sure unused workflow's states are not used to classify state type
    """
    workflow = self.portal.portal_workflow.newContent(
      portal_type='Workflow',
      id='nobody_use_this_workflow')
    workflow.newContent(
      portal_type='Workflow State',
      reference='nobody_use_this_state',
      state_type_list=['draft_order',
                       'planned_order',
                       'future_inventory',
                       'reserved_inventory',
                       'transit_inventory',
                       'current_inventory'])

    self.portal.portal_types.newContent(
        portal_type='Base Type',
        id='Do Not Use Me',
        type_workflow='nobody_use_this_workflow')
    self.portal.portal_caches.erp5_content_medium.clearCache()
    self.assertIn('nobody_use_this_state', self.portal.getPortalDraftOrderStateList())
    self.assertIn('nobody_use_this_state', self.portal.getPortalPlannedOrderStateList())
    self.assertIn('nobody_use_this_state', self.portal.getPortalFutureInventoryStateList())
    self.assertIn('nobody_use_this_state', self.portal.getPortalReservedInventoryStateList())
    self.assertIn('nobody_use_this_state', self.portal.getPortalTransitInventoryStateList())
    self.assertIn('nobody_use_this_state', self.portal.getPortalCurrentInventoryStateList())

    self.portal.portal_types['Do Not Use Me'].setTypeWorkflow(None)
    self.portal.portal_caches.erp5_content_medium.clearCache()
    self.assertNotIn('nobody_use_this_state', self.portal.getPortalDraftOrderStateList())
    self.assertNotIn('nobody_use_this_state', self.portal.getPortalPlannedOrderStateList())
    self.assertNotIn('nobody_use_this_state', self.portal.getPortalFutureInventoryStateList())
    self.assertNotIn('nobody_use_this_state', self.portal.getPortalReservedInventoryStateList())
    self.assertNotIn('nobody_use_this_state', self.portal.getPortalTransitInventoryStateList())
    self.assertNotIn('nobody_use_this_state', self.portal.getPortalCurrentInventoryStateList())
