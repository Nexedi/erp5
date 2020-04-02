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

class TestUpgradeInstanceWithOldDataFs(ERP5TypeTestCase):
  def getBusinessTemplateList(self):
    return ('erp5_core_proxy_field_legacy',
            'erp5_full_text_mroonga_catalog',
            'erp5_base',
            'erp5_workflow',
            'erp5_accounting',
            'erp5_configurator',
            'erp5_simulation',
            'erp5_pdm',
            'erp5_trade',
            'erp5_accounting',
            'erp5_configurator_standard_trade_template',
            'erp5_upgrader')

  def testUpgrade(self):
    if not self.portal.portal_templates.getRepositoryList():
      self.setupAutomaticBusinessTemplateRepository(
        searchable_business_template_list=["erp5_core", "erp5_base"])

    from Products.ERP5Type.tests.utils import createZODBPythonScript
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'Base_getUpgradeBusinessTemplateList',
      '',
      """return (('erp5_base',
         'erp5_configurator_standard_trade_template',
         'erp5_configurator_standard',
         'erp5_jquery',
         'erp5_xhtml_style'),
        ['erp5_upgrader'])""")
    self.tic()

    alarm = self.portal.portal_alarms.promise_check_upgrade
    alarm.solve()
    self.tic()
    self.assertEquals(alarm.getLastActiveProcess().getResultList(), [])

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
    self.assertEquals(
      error_list, [],
      msg="The following Portal Type classes could not be loaded (see zLOG.log): %r" % error_list)
