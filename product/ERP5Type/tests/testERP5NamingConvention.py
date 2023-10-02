##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#                     Kazuhiko <kazuhiko@nexedi.com>
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

import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type import WITH_LEGACY_WORKFLOW
from Testing import ZopeTestCase

class TestNamingConvention(ERP5TypeTestCase):

  def getBusinessTemplateList(self):
    # include all standard Business Templates, i.e. erp5_*
    return (
      'erp5_core_proxy_field_legacy',
      'erp5_base', 'erp5_pdm',
      'erp5_simulation', 'erp5_trade', 'erp5_accounting',
      'erp5_apparel', 'erp5_mrp', 'erp5_project',
      'erp5_ingestion_mysql_innodb_catalog', 'erp5_ingestion',
      'erp5_jquery', 'erp5_web', 'erp5_dms', 'erp5_csv_style', 'erp5_crm',
      'erp5_budget', 'erp5_item', 'erp5_ui_test_core', 'erp5_ui_test',
      'erp5_accounting_l10n_fr', 'erp5_invoicing', 'erp5_accounting_ui_test',
      'erp5_commerce', 'erp5_consulting',
      'erp5_dummy_movement', 'erp5_forge', 'erp5_promise', 'erp5_mobile',
      'erp5_payroll', 'erp5_credential', 'erp5_jquery_ui', 'erp5_payroll_ui_test',
      'erp5_publication', 'erp5_dms_ui_test', 'erp5_administration',
      'erp5_advanced_invoicing', 'erp5_apparel', 'erp5_archive',
      'erp5_barcode', 'erp5_budget', 'erp5_calendar', 'erp5_knowledge_pad', 'erp5_km',
      'erp5_oauth', 'erp5_ods_style', 'erp5_odt_style', 'erp5_ooo_import',
      'erp5_open_trade', 'erp5_open_trade_periodicity_line', 'erp5_payment_mean',
      'erp5_secure_payment', 'erp5_paypal_secure_payment', 'erp5_payzen_secure_payment',
      'erp5_public_accounting_budget', 'erp5_publication', 'erp5_run_my_doc',
      'erp5_short_message', 'erp5_simplified_invoicing', 'erp5_trade_knowledge_pad',
      'erp5_trade_ui_test',
      'erp5_authentication_policy', 'erp5_bearer_token',
      'erp5_code_mirror', 'erp5_computer_immobilisation',
      'erp5_credential_oauth2', 'erp5_data_protection', 'erp5_data_set',
      'erp5_development_wizard', 'erp5_dhtml_style', 'erp5_direct_debit_payment',
      'erp5_rss_style', 'erp5_discussion', 'erp5_tax_resource', 'erp5_discount_resource',
      'erp5_email_reader', 'erp5_external_account', 'erp5_forum_tutorial',
      'erp5_immobilisation', 'erp5_ical_style', 'erp5_inotify', 'erp5_interfaces',
      'erp5_promise', 'erp5_software_pdm', 'erp5_sso_openam', 'erp5_jquery_plugin_hotkey',
      'erp5_jquery_plugin_jgraduate', 'erp5_jquery_plugin_svgicon', 'erp5_jquery_plugin_jquerybbq',
      'erp5_jquery_plugin_spinbtn', 'erp5_jquery_plugin_svg_editor', 'erp5_svg_editor', 'erp5_syncml',
      'erp5_system_event', 'erp5_tiosafe_core',
      'erp5_public_accounting_budget', 'erp5_publication',
      'erp5_social_contracts', 'test_core', 'test_accounting', 'test_web', 'test_html_style',
      'test_xhtml_style', 'cloudooo_data', 'cloudooo_web', 'erp5_configurator',
      'erp5_configurator_maxma_demo', 'erp5_configurator_run_my_doc', 'erp5_configurator_standard',
      'erp5_configurator_standard_solver',
      'erp5_web_service', 'erp5_certificate_authority',
      # skip l10n templates to save time.
      # 'erp5_l10n_fr', 'erp5_l10n_ja',
      # 'erp5_l10n_pl_PL', 'erp5_l10n_pt-BR',
      # 'erp5_accounting_l10n_fr_m14', 'erp5_accounting_l10n_fr_m9',
      # 'erp5_accounting_l10n_pl',
      # 'erp5_accounting_l10n_sn',
      # 'erp5_accounting_l10n_in',
      ) + (('erp5_workflow_test',) if WITH_LEGACY_WORKFLOW else ())

  def getTitle(self):
    return "Naming Convention"

  def testNamingConvention(self):
    result_list = self.portal.ERP5Site_checkNamingConventions(batch_mode=True)
    final_result_list = []
    ignored_result_list = []
    for result in result_list:
      # Thre is too much mess in Field Library, so enforce only some business
      # template until more cleanup is done
      if result.find("Field Library") >= 0:
        for skin_folder in ('erp5_simulation', 'erp5_accounting', 'erp5_apparel',
                            'erp5_mrp', 'erp5_project', 'erp5_ingestion', 'erp5_web',
                            'erp5_dms', 'erp5_crm', 'erp5_budget', 'erp5_item',
                            'erp5_ui_test', 'erp5_invoicing',
                            'erp5_consulting', 'erp5_forge',
                            'erp5_payroll', 'erp5_administration',
                            'erp5_advanced_invoicing', 'erp5_archive', 'erp5_barcode',
                            'erp5_calendar', 'erp5_knowledge_pad', 'erp5_km_theme',
                            'erp5_odt_style', 'erp5_run_my_doc', 'erp5_development',
                            'erp5_tax_resource', 'erp5_immobilisation', 'erp5_software_pdm',
                            'erp5_syncml', 'erp5_workflow', 'erp5_configurator',
                            'erp5_configurator_wizard', 'erp5_base', 'erp5_pdm',
                            'erp5_core_proxy_field_legacy'):
          if result.startswith(skin_folder):
            ignored_result_list.append(result)
            break
        else:
          final_result_list.append(result)
      else:
        final_result_list.append(result)
    ZopeTestCase._print("\n==============================")
    ZopeTestCase._print("\nResult we ignore until cleanup is done:\n")
    ZopeTestCase._print("\n".join(["(ignored): %s" % x for x in ignored_result_list]))
    ZopeTestCase._print("\n==============================\n")
    self.assertEqual(0, len(final_result_list), "\n".join(final_result_list))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestNamingConvention))
  return suite
