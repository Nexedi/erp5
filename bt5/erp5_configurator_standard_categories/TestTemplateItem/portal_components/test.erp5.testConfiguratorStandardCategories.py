##############################################################################
# Copyright (c) 2020 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests import ERP5TypeTestCase


class TestConfiguratorStandardCategoriesScripts(ERP5TypeTestCase.ERP5TypeTestCase):
  """Check that the scripts from erp5_configurator_standard are in sync.

  During configuration, we ask user to select categories, before the default category
  business template is actually installed. This test checks that the scripts are in
  sync with the actual categories.
  """
  maxDiff = None

  def afterSetUp(self):
    super(TestConfiguratorStandardCategoriesScripts, self).afterSetUp()
    self.business_configuration = self.portal.business_configuration_module.newContent(
        portal_type='Business Configuration'
    )

  def test_BusinessConfiguration_getFunctionTitleItemList(self):
    self.assertEqual(
        self.business_configuration.BusinessConfiguration_getFunctionTitleItemList(),
        self.portal.portal_categories.function.getCategoryChildTranslatedIndentedTitleItemList(
            disable_node=True,
            local_sort_id=('int_index', 'translated_title',)
        ))

  def test_BusinessConfiguration_getRegionTitleItemList(self):
    self.assertEqual(
        self.business_configuration.BusinessConfiguration_getRegionTitleItemList(),
        self.portal.portal_categories.region.getCategoryChildTranslatedTitleItemList(
            filter_node=True,
            sort_id='title'
        ))

