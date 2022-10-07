##############################################################################
#
# Copyright (c) 2020 Nexedi SA and Contributors.
# All Rights Reserved.
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import six.moves.urllib.parse


class TestBusinessTemplateScripts(ERP5TypeTestCase):
  """Test for erp5_toolbox helpers for business template creation
  """
  def afterSetUp(self):
    super(TestBusinessTemplateScripts, self).afterSetUp()
    self.business_template = self.portal.portal_templates.newContent(
        portal_type='Business Template')
    self.skin_folder = self.portal.portal_skins.custom

  def test_BusinessTemplate_createReport(self):
    resp = self.business_template.BusinessTemplate_createReport(
        portal_type='Foo Module',
        report_name='Dummy Report',
        skin_folder=self.skin_folder.getId(),
        use_from_date_at_date=None)

    resp_url = six.moves.urllib.parse.urlparse(resp)
    self.assertEqual(
        ['Report created.'],
        six.moves.urllib.parse.parse_qs(resp_url.query)['portal_status_message'])

    # report is usable (also in ERP5JS)
    action, = [
        a for a in self.portal.portal_actions.listFilteredActionsFor(
            self.portal.foo_module)['object_jio_report']
        if a['name'] == 'Dummy Report'
    ]
    self.assertEqual('dummy_report_report', action['id'])
    self.assertEqual(
        'FooModule_viewDummyReportReportDialog',
        six.moves.urllib.parse.urlparse(action['url']).path.split('/')[-1])

    self.assertIn(
        'FooModule_viewDummyReportReportDialog', self.skin_folder.objectIds())
    self.assertIn(
        'FooModule_viewDummyReportReport', self.skin_folder.objectIds())
    self.assertIn(
        'FooModule_getDummyReportReportSectionList',
        self.skin_folder.objectIds())
    self.assertIn(
        'FooModule_viewDummyReportReportSection', self.skin_folder.objectIds())
    self.assertIn(
        'FooModule_getDummyReportLineList', self.skin_folder.objectIds())

    # actions were added to business template
    self.assertEqual(
        [
            'Foo Module | dummy_export_export',
            'Foo Module | dummy_report_report',
        ],
        self.business_template.getTemplateActionPathList(),
    )

  def test_BusinessTemplate_createSkinFolder(self):
    self.business_template.setTemplateSkinIdList(['existing'])
    resp = self.business_template.BusinessTemplate_createSkinFolder(
        skin_folder_name='dummy_skin_folder',
        skin_layer_priority=None,
        skin_layer_list=self.portal.portal_skins.getSkinSelections(),
    )
    resp_url = six.moves.urllib.parse.urlparse(resp)
    self.assertEqual(
        ['Skin folder created.'],
        six.moves.urllib.parse.parse_qs(resp_url.query)['portal_status_message'])

    self.assertIn('dummy_skin_folder', self.portal.portal_skins.objectIds())
    # skin is added to business template
    self.assertEqual(
        ['dummy_skin_folder', 'existing'],
        self.business_template.getTemplateSkinIdList())

  def test_BusinessTemplate_createSkinFolder_priority(self):
    resp = self.business_template.BusinessTemplate_createSkinFolder(
        skin_folder_name='dummy_skin_folder',
        skin_layer_priority=99,
        skin_layer_list=self.portal.portal_skins.getSkinSelections(),
    )
    resp_url = six.moves.urllib.parse.urlparse(resp)
    self.assertEqual(
        ['Skin folder created.'],
        six.moves.urllib.parse.parse_qs(resp_url.query)['portal_status_message'])

    self.assertIn('dummy_skin_folder', self.portal.portal_skins.objectIds())
    self.assertEqual(
        99,
        self.portal.portal_skins.dummy_skin_folder.getProperty(
            'business_template_skin_layer_priority'))

  def test_BusinessTemplate_createSkinFolder_skin_selection(self):
    self.business_template.setTemplateRegisteredSkinSelectionList(
        ['existing | SelectedSkinSelection'])
    self.portal.portal_skins.addSkinSelection(
        'SelectedSkinSelection', 'erp5_core')
    self.portal.portal_skins.addSkinSelection(
        'NotSelectedSkinSelection', 'erp5_core')

    resp = self.business_template.BusinessTemplate_createSkinFolder(
        skin_folder_name='dummy_skin_folder',
        skin_layer_priority=99,
        skin_layer_list=['View', 'SelectedSkinSelection'])
    resp_url = six.moves.urllib.parse.urlparse(resp)
    self.assertEqual(
        ['Skin folder created.'],
        six.moves.urllib.parse.parse_qs(resp_url.query)['portal_status_message'])

    self.assertIn('dummy_skin_folder', self.portal.portal_skins.objectIds())
    skin_folders_by_skin_selection = {
        k: v.split(',') for (k, v) in self.portal.portal_skins.getSkinPaths()
    }

    self.assertIn('dummy_skin_folder', skin_folders_by_skin_selection['View'])
    self.assertIn(
        'dummy_skin_folder',
        skin_folders_by_skin_selection['SelectedSkinSelection'])
    self.assertNotIn(
        'dummy_skin_folder',
        skin_folders_by_skin_selection['NotSelectedSkinSelection'])
    self.assertEqual(
        ['SelectedSkinSelection', 'View'],
        sorted(
            self.portal.portal_skins.dummy_skin_folder.getProperty(
                'business_template_registered_skin_selections')))

    # skin is added to business template
    self.assertEqual(
        [
            'dummy_skin_folder | SelectedSkinSelection',
            'dummy_skin_folder | View',
            'existing | SelectedSkinSelection',
        ], self.business_template.getTemplateRegisteredSkinSelectionList())
