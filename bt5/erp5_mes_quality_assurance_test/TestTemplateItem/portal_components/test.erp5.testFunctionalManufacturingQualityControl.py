##############################################################################
#
# Copyright (c) 2002-2025 Nexedi SA and Contributors. All Rights Reserved.
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
import unittest
from Products.ERP5Type.tests.ERP5TypeFunctionalTestCase import ERP5TypeFunctionalTestCase
from DateTime import DateTime

class TestFunctionalManufacturingQualityControl(ERP5TypeFunctionalTestCase):
  foreground = 0
  run_only = "manufacturing_quality_control_zuite"

  def getBusinessTemplateList(self):
    return (
      'erp5_mes_quality_assurance',
      'erp5_web_renderjs_ui_test_core',
      'erp5_ui_test_core'
    )

  def afterSetUp(self):
    super(TestFunctionalManufacturingQualityControl, self).afterSetUp()
    self.tic()
    self.quality_element_type = ['Quality Control', 'Traceability', 'Gate', 'Defect Declaration','Defect Correction', 'SMON', 'ACOM']
    # create needed test production datas
    now = DateTime()
    po = self.portal.production_order_module.newContent(
      portal_type='Production Order',
      id='test_%s' % now.second(),
      specialise = 'business_process_module/production_business_process',
      start_date = now,
      stop_date = now,
      destination_section = 'organisation_module/starlink',
      destination = 'organisation_module/warehouse'
    )
    po.newContent(
      portal_type='Production Order Line',
      resource = 'product_module/test_product',
      specialise = 'transformation_module/test_product_transformation',
      quantity = 1)
    po.newContent(
      portal_type='Production Order Line',
      resource = 'service_module/test_quality_insurance',
      specialise = 'transformation_module/test_quality_insurance_transformation',
      quantity = 1)
    po.plan()
    po.confirm()
    self.po = po
    self.tic()
    self.portal.portal_alarms.quality_assurance_builder_alarm.activeSense()
    self.tic()
    me_execution = [x for x in po.getCausalityRelatedValueList(portal_type='Manufacturing Execution') if x.getLedger() == 'manufacturing/execution'][0]
    me_execution.start()
    me_execution.Base_showNextStepQualityOperation(me=me_execution)
    self.me_execution = me_execution
    quality_execution = [x for x in po.getCausalityRelatedValueList(portal_type='Manufacturing Execution') if x.getLedger() == 'manufacturing/quality_insurance'][0]
    quality_execution.start()
    self.tic()




def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestFunctionalManufacturingQualityControl))
  return suite


