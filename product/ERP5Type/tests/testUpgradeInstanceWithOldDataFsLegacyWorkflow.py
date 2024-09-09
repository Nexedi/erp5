##############################################################################
#
# Copyright (c) 2020 Nexedi SA and Contributors. All Rights Reserved.
#          Arnaud Fontaine <arnaud.fontaine@nexedi.com>
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
from Products.ERP5Type import WITH_LEGACY_WORKFLOW
import StringIO
import unittest
import urllib
import httplib


class TestUpgradeInstanceWithOldDataFsWithLegacyWorkflow(ERP5TypeTestCase):

  def getBusinessTemplateList(self):
    return ('erp5_core_proxy_field_legacy',
            'erp5_full_text_mroonga_catalog',
            'erp5_base',
            'erp5_simulation',
            'erp5_accounting',
            'erp5_configurator',
            'erp5_pdm',
            'erp5_trade',
            'erp5_ingestion_mysql_innodb_catalog',
            'erp5_ingestion',
            'erp5_crm',
            'erp5_jquery_ui',
            'erp5_knowledge_pad',
            'erp5_project',
            'erp5_forge',
            'erp5_web',
            'erp5_jquery_plugin_mbmenu',
            'erp5_jquery_plugin_sheet',
            'erp5_jquery_plugin_jqchart',
            'erp5_jquery_plugin_colorpicker',
            'erp5_jquery_plugin_elastic',
            'erp5_jquery_sheet_editor',
            'erp5_svg_editor',
            'erp5_dms',
            'erp5_mrp',
            'erp5_hal_json_style',
            'erp5_font',
            'erp5_web_renderjs_ui',
            'erp5_code_mirror',
            'erp5_multimedia',
            'erp5_smart_assistant',
            'erp5_officejs',
            'erp5_configurator_standard_trade_template',
            'erp5_upgrader')

  def testUpgrade(self):
    if not self.portal.portal_templates.getRepositoryList():
      self.setupAutomaticBusinessTemplateRepository(
        searchable_business_template_list=["erp5_core", "erp5_base", "erp5_notebook"])

    from Products.ERP5Type.tests.utils import createZODBPythonScript
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'Base_getUpgradeBusinessTemplateList',
      '',
      """return (('erp5_base',
         'erp5_configurator_standard_trade_template',
         'erp5_configurator_standard',
         'erp5_jquery',
         'erp5_xhtml_style',
         'erp5_upgrader',
         'erp5_accounting',
         'erp5_trade',
         'erp5_pdm',
         'erp5_crm',
         'erp5_project',
         'erp5_forge',
         'erp5_dms',
         'erp5_mrp',
         'erp5_officejs',
         'erp5_web_renderjs_ui'),
         ())""")
    self.tic()

    alarm = self.portal.portal_alarms.promise_check_upgrade

    # Ensure it is viewable
    alarm.view()
    # Call active sense
    alarm.activeSense()
    self.tic()
    # XXX No idea why active sense must be called twice...
    alarm.activeSense()
    self.tic()

    self.assertNotEqual([x.detail for x in alarm.getLastActiveProcess().getResultList()], [])

    # Solve divergencies, like called from the form_dialog
    # XXX We only check that Base_callDialogMethod can be correctly executed
    # and we do not check the result (the redirect can be an Unauthorized error)
    # A better version would be to use the Location header result to trigger Alarm_solve
    ret = self.publish(
      '%s/portal_alarms/promise_check_upgrade' % self.portal.getPath(),
      basic='%s:current' % self.id(),
      stdin=StringIO.StringIO(urllib.urlencode({
        'Base_callDialogMethod:method': '',
        'dialog_id': 'Alarm_viewSolveDialog',
        'dialog_method': 'Alarm_solve',
        'form_id': 'Alarm_view',
        'selection_name': 'foo_selection',
      })),
      request_method="POST",
      handle_errors=False
    )
    self.assertEqual(httplib.FOUND, ret.getStatus())

    alarm.Alarm_solve()

    self.tic(delay=2400)

    self.assertEqual([x.detail for x in alarm.getLastActiveProcess().getResultList()], [])

    # Make sure that *all* Portal Type can be loaded after upgrade
    import erp5.portal_type
    from Products.ERP5Type.dynamic.lazy_class import ERP5BaseBroken
    error_list = []
    for portal_type_obj in self.portal.portal_types.listTypeInfo():
      portal_type_id = portal_type_obj.getId()
      portal_type_class = getattr(erp5.portal_type, portal_type_id)
      portal_type_class.loadClass()
      if issubclass(portal_type_class, ERP5BaseBroken):
        error_list.append(portal_type_id)
    self.assertEqual(
      error_list, [],
      msg="The following Portal Type classes could not be loaded (see zLOG.log): %r" % error_list)

def test_suite():
  suite = unittest.TestSuite()
  if WITH_LEGACY_WORKFLOW:
    suite.addTest(unittest.makeSuite(TestUpgradeInstanceWithOldDataFsWithLegacyWorkflow))
  return suite
