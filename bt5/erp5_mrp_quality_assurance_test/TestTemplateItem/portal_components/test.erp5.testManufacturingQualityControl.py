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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from DateTime import DateTime

class TestQualityAssurance(ERP5TypeTestCase):

  def afterSetUp(self):
    quality_element_id_list = [x.getId() for x in self.portal.quality_assurance_module.searchFolder(id='test_%')]
    self.portal.quality_assurance_module.manage_delObjects(ids=quality_element_id_list)
    self.tic()
    po_list = self.portal.production_order_module.searchFolder(id='test_%')
    sm_id_list = []
    me_id_list = []
    ppl_id_list = []
    mo_id_list = []
    for po in po_list:
      for ppl in po.getCausalityRelatedValueList(portal_type='Production Packing List'):
        ppl_id_list.append(ppl.getId())
      sm = po.getCausalityRelatedValue(portal_type='Simulation Movement')
      if sm:
        sm_id_list.append(sm.getId())
      for me in po.getCausalityRelatedValueList(portal_type='Manufacturing Execution'):
        me_id_list.append(me.getId())
        for quality_element in me.getCausalityRelatedValueList(portal_type=('Quality Control', 'Traceability', 'Gate', 'Defect Declaration','Defect Correction', 'SMON', 'ACOM')):
          if quality_element.getId() not in quality_element_id_list:
            quality_element_id_list.append(quality_element.getId())

      for mo_line in po.getCausalityRelatedValueList(portal_type='Manufacturing Order Line'):
        mo_id_list.append(mo_line.getParentValue().getId())


    self.portal.quality_assurance_module.manage_delObjects(ids=quality_element_id_list)
    self.portal.production_order_module.manage_delObjects(ids=[x.getId() for x in po_list])
    self.portal.production_packing_list_module.manage_delObjects(ids=ppl_id_list)
    self.portal.manufacturing_order_module.manage_delObjects(ids=mo_id_list)
    self.portal.manufacturing_execution_module.manage_delObjects(ids=me_id_list)
    self.quality_element_type = getattr(self.portal.portal_types, 'Quality Assurance Module').getTypeAllowedContentTypeList()

    self.tic()


  def test_quality_element_workflow(self):
    def createTestElement(portal_type):
      return self.portal.quality_assurance_module.newContent(
        portal_type=portal_type,
        id='test_%s' % DateTime().second(),
        publication_section = 'quality_insurance'
      )

    for portal_type in self.quality_element_type:
      quality_element = createTestElement(portal_type)
      self.assertEquals(quality_element.getValidationState(), 'draft')
      quality_element.plan()
      self.assertEquals(quality_element.getValidationState(), 'queued')
      quality_element.confirm()
      self.assertEquals(quality_element.getValidationState(), 'expected')
      self.assertTrue(self.portal.portal_workflow.isTransitionPossible(quality_element, 'pending'))
      self.assertTrue(self.portal.portal_workflow.isTransitionPossible(quality_element, 'post'))
      quality_element.pending()
      self.assertEquals(quality_element.getValidationState(), 'pending_update')
      quality_element.post()
      self.assertEquals(quality_element.getValidationState(), 'posted')
      quality_element.archive()
      self.assertEquals(quality_element.getValidationState(), 'archived')

    quality_control = createTestElement(portal_type='Quality Control')
    quality_control.plan()
    quality_control.confirm()
    quality_control.post()
    quality_control2 = createTestElement(portal_type='Quality Control')
    quality_control2.setFollowUpValue(quality_control)
    quality_control2.plan()
    quality_control2.confirm()
    quality_control2.post()
    self.assertEquals(quality_control.getValidationState(), 'archived')
    element_list = []
    index = 0
    po = self.portal.production_order_module.newContent(
      portal_type='Production Order',
      id='test_%s' % DateTime().second())
    me  = self.portal.manufacturing_execution_module.newContent(
      portal_type='Manufacturing Execution',
      causality_value = po,
      id='test_%s' % DateTime().second(),
      ledger = 'manufacturing/quality_insurance')
    me_2 = self.portal.manufacturing_execution_module.newContent(
      portal_type='Manufacturing Execution',
      causality_value = po,
      id='test_%s' % DateTime().second(),
      ledger = 'manufacturing/execution')

    for portal_type in self.quality_element_type:
      quality_element = createTestElement(portal_type=portal_type)
      quality_element.edit(int_index = index, causality_value = me_2)
      quality_element.plan()
      me.newContent(portal_type='Manufacturing Execution Line',
                    int_index = index,
                    aggregate_value = quality_element)

      element_list.append(quality_element)
      index += 1

    self.tic()
    element_list[2].confirm()
    self.tic()
    element_list[2].post()
    self.tic()

    for index in [0, 1,3, 4]:
      self.assertEquals(element_list[index].getValidationState(), 'expected')
    for index in [5, 6]:
      self.assertEquals(element_list[index].getValidationState(), 'queued')

    element_list[4].post()
    self.tic()

    for index in [0, 1,3, 5, 6]:
      self.assertEquals(element_list[index].getValidationState(), 'expected')

  def test_quality_element_creation(self):
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
    self.tic()
    self.portal.portal_alarms.quality_assurance_builder_alarm.activeSense()
    self.tic()
    me = [x for x in po.getCausalityRelatedValueList(portal_type='Manufacturing Execution') if x.getLedger() == 'manufacturing/execution'][0]
    quality_element_list = me.getCausalityRelatedValueList(portal_type=self.quality_element_type)
    self.assertEquals(len(quality_element_list), 15, quality_element_list)



























































