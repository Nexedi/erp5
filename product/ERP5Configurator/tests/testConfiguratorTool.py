##############################################################################
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                     Lucas Carvalho <lucas@nexedi.com>
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


from AccessControl import Unauthorized
from Products.ERP5Configurator.tests.ConfiguratorTestMixin import \
                                             TestLiveConfiguratorWorkflowMixin


class TestConfiguratorTool(TestLiveConfiguratorWorkflowMixin):
  """
    Test the Configurator Tool
  """

  def getBusinessTemplateList(self):
    return ('erp5_core_proxy_field_legacy',
            'erp5_full_text_mroonga_catalog',
            'erp5_base',
            'erp5_workflow',
            'erp5_configurator',
            'erp5_configurator_standard',)

  def test_anonymous_can_not_view_configurator_tool(self):
    """
      The Anonymous user can not have access to view the Configurator Tool.
    """
    checkPermission = self.portal.portal_membership.checkPermission
    configurator_tool = self.portal.portal_configurator
    self.logout()
    self.assertEqual(None, checkPermission('View', configurator_tool))
    self.assertRaises(Unauthorized, configurator_tool)
