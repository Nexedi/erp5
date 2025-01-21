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
    # remove all test datas
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
    self.portal.portal_simulation.manage_delObjects(ids=sm_id_list)

    self.tic()
    self.quality_element_type = getattr(self.portal.portal_types, 'Quality Assurance Module').getTypeAllowedContentTypeList()
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

  def test_quality_control(self):
    me_execution = self.me_execution
    quality_element_list = me_execution.getCausalityRelatedValueList(portal_type=self.quality_element_type)
    self.assertEquals(len(quality_element_list), 15, quality_element_list)
    quality_element_list = me_execution.Delivery_getUpcomingQualityControlOperationList()
    self.assertEquals(len(quality_element_list), 3)
    for quality_element in quality_element_list:
      self.assertEquals(quality_element.getValidationState(), 'expected')
    self.assertEquals(quality_element_list[-1].getPortalType(), 'Gate')
    quality_control = quality_element_list[0].getObject()
    quality_control.QualityControl_postQualityAssuranceResult(result='ok', batch=True)
    self.tic()
    self.assertEquals(quality_control.getValidationState(), 'posted')
    self.assertEquals(quality_control.getQualityAssurance(), 'result/ok')
    cloned_one = quality_control.QualityControl_RequestNewQualityControl(batch=True)
    self.tic()
    self.assertTrue(cloned_one.getAggregateRelatedValue(portal_type='Manufacturing Execution Line') is not None)
    self.assertNotEquals(cloned_one.getAggregateRelatedValue(portal_type='Manufacturing Execution Line'), quality_control.getAggregateRelatedValue(portal_type='Manufacturing Execution Line'))
    self.tic()
    self.assertEquals(quality_control.getValidationState(), 'posted')
    self.assertEquals(cloned_one.getValidationState(), 'expected')
    cloned_one.QualityControl_postQualityAssuranceResult(result='nok', batch=True, redirect_to_defect_dialog=False)
    self.tic()
    self.assertEquals(quality_control.getValidationState(), 'archived')
    self.assertEquals(cloned_one.getValidationState(), 'posted')
    cloned_cloned_one = cloned_one.getFollowUpRelatedValue(portal_type='Quality Control')
    self.assertTrue(cloned_cloned_one.getAggregateRelatedValue(portal_type='Manufacturing Execution Line') is not None)
    self.assertNotEquals(cloned_cloned_one.getAggregateRelatedValue(portal_type='Manufacturing Execution Line'), cloned_one.getAggregateRelatedValue(portal_type='Manufacturing Execution Line'))
    self.assertEquals(cloned_cloned_one.getValidationState(), 'pending_update')
    cloned_cloned_one.QualityControl_postQualityAssuranceResult(result='ok', batch=True)
    self.tic()
    self.assertEquals(cloned_one.getValidationState(), 'archived')
    self.assertEquals(cloned_cloned_one.getValidationState(), 'posted')
    defect_one = cloned_cloned_one.QualityControl_RequestNewQualityControl(batch=True)

    self.assertEquals(defect_one.getValidationState(), 'expected')


  def test_gate(self):
    me_execution = self.me_execution
    previous_quality_element_list = []
    while True:
      quality_element_list = [x.getObject() for x in me_execution.Delivery_getUpcomingQualityControlOperationList()]

      for i in previous_quality_element_list:
        self.assertTrue(i in quality_element_list)

      for i in quality_element_list:
        self.assertEquals(i.getValidationState(), 'expected')

      if quality_element_list[-1].getPortalType() != 'Gate':
        break


      gate = quality_element_list[-1]
      gate.Gate_validate()
      self.tic()
      self.assertEquals(gate.getValidationState(), 'posted')
      previous_quality_element_list = quality_element_list[:-1]


  def test_SMON(self):
    me_execution = self.me_execution
    while True:
      quality_element_list = me_execution.Delivery_getUpcomingQualityControlOperationList()
      if quality_element_list[-1].getPortalType() != 'Gate':
        break
      gate = quality_element_list[-1]
      gate.Gate_validate()
      self.tic()

    # all gate are passed, SMON is the next last one
    SMON = quality_element_list[-1]
    incompleted_list = SMON.Base_getIncompletedOperationList()
    self.assertTrue(incompleted_list is not None)
    SMON.SMON_postSMONResult()
    self.tic()
    self.assertEquals(SMON.getValidationState(), 'posted')
    self.assertEquals(me_execution.getSimulationState(), 'stopped')

  def test_ACOM(self):
    me_execution = self.me_execution
    while True:
      quality_element_list = me_execution.Delivery_getUpcomingQualityControlOperationList()
      if quality_element_list[-1].getPortalType() != 'Gate':
        break
      gate = quality_element_list[-1]
      gate.Gate_validate()
      self.tic()

    SMON =  quality_element_list[-1]
    SMON.SMON_postSMONResult()
    self.tic()
    quality_element_list = me_execution.Delivery_getUpcomingQualityControlOperationList()
    ACOM = quality_element_list[-1]

    incompleted_list = ACOM.Base_getIncompletedOperationList()
    self.assertTrue(incompleted_list is not None)
    ACOM.ACOM_validate()
    self.tic()
    self.assertEquals(ACOM.getValidationState(), 'expected')


    for i in incompleted_list:
      self.assertEquals(i.getValidationState(), 'expected')
      i.post()

    self.tic()
    incompleted_list = ACOM.Base_getIncompletedOperationList()
    self.assertEquals(len(incompleted_list), 0)
    ACOM.ACOM_validate()
    self.tic()
    self.assertEquals(ACOM.getValidationState(), 'posted')
    self.assertEquals(me_execution.getSimulationState(), 'delivered')


  def _test_SMON_ACOM_operation_list(self, ACOM = False):
    me_execution = self.startManufacturingForTest()
    while True:
      quality_element_list = me_execution.Delivery_getUpcomingQualityControlOperationList()
      if quality_element_list[-1].getPortalType() != 'Gate':
        break
      gate = quality_element_list[-1]
      gate.Gate_validate()
      self.tic()

    target_element = quality_element_list[-1]
    self.assertEquals(target_element.getPortalType(), 'SMON')
    if ACOM:
      target_element.SMON_postSMONResult()
      self.tic()
      target_element = me_execution.Delivery_getUpcomingQualityControlOperationList()[-1]
      self.assertEquals(target_element.getPortalType(), 'ACOM')


    incompleted_list = target_element.Base_getIncompletedOperationList()
    for element in incompleted_list:
      self.assertTrue(element.getIntIndex() < target_element.getIntIndex())
      self.assertEquals(element.getValidationState(), 'expected')
    incompleted_list[0].getObject().QualityControl_postQualityAssuranceResult(result='nok', batch=True, redirect_to_defect_dialog=False)
    self.tic()
    new_incompleted_list = target_element.Base_getIncompletedOperationList()
    self.assertEquals([x.getObject() for x in incompleted_list], [x.getObject() for x in new_incompleted_list])
    self.assertEquals(new_incompleted_list[0].getValidationState(), 'posted')

  def _test_SMON_operation_list(self):
    self._test_SMON_ACOM_operation_list()

  def _test_ACOM_operation_list(self):
    self._test_SMON_ACOM_operation_list(True)




  def _test_traceability(self):
    me_execution = self.startManufacturingForTest()
    while True:
      quality_element_list = me_execution.Delivery_getUpcomingQualityControlOperationList()
      if quality_element_list[-1].getPortalType() != 'Gate':
        break
      gate = quality_element_list[-1]
      gate.Gate_validate()
      self.tic()


    traceability_list = me_execution.Base_getExpectedTraceabilityInputList()
    self.assertEquals(len(traceability_list), 3)
    me_execution.ManufacturingExecution_processTraceabilityData('''00463429720111111111111111
00517566260111111111111111
''')
    self.tic()
    traceability_list = me_execution.Base_getExpectedTraceabilityInputList()
    self.assertEquals(len(traceability_list), 1)
    self.assertEquals(traceability_list[0].getReference(), '00519267020')
    me_execution.ManufacturingExecution_processTraceabilityData('''00463429720111111111111111
''')
    self.tic()
    traceability_list = me_execution.Base_getExpectedTraceabilityInputList()
    self.assertEquals(len(traceability_list), 1)
    self.assertEquals(traceability_list[0].getReference(), '00519267020')
    update_traceability = traceability_list[0]
    me_execution.ManufacturingExecution_processTraceabilityData('''00519267020111111111111111
''')
    self.tic()
    traceability_list = me_execution.Base_getExpectedTraceabilityInputList()
    self.assertEquals(len(traceability_list), 0)
    update_traceability.Traceability_updateTraceabilityInput()
    self.tic()
    self.assertEquals(update_traceability.getValidationState(), 'archived')
    traceability_list = me_execution.Base_getExpectedTraceabilityInputList()
    self.assertEquals(len(traceability_list), 1)
    self.assertNotEquals(traceability_list[0], update_traceability)
    self.assertEquals(traceability_list[0].getObject(), update_traceability.getFollowUpRelatedValue(portal_type='Traceability'))
    # traceability_list[0] is the new one
    self.assertTrue(traceability_list[0].getAggregateRelatedValue(portal_type='Manufacturing Execution Line') is not None)
    self.assertNotEquals(traceability_list[0].getAggregateRelatedValue(portal_type='Manufacturing Execution Line'), update_traceability.getAggregateRelatedValue(portal_type='Manufacturing Execution Line'))
    # same traceability as before, can be reused
    me_execution.ManufacturingExecution_processTraceabilityData('''00519267020111111111111111
''')
    traceability_list = me_execution.Base_getExpectedTraceabilityInputList()
    self.assertEquals(len(traceability_list), 0)
    self.tic()
    serial_number = self.portal.quality_assurance_module['00463429720111111111111111']
    traceability = serial_number.getFollowUpValue(portal_type='Traceability')
    self.assertEquals(traceability.getAggregateValue(portal_type='Serial Number'), serial_number)
    traceability.Traceability_updateTraceabilityInput()
    self.tic()
    traceability_list = me_execution.Base_getExpectedTraceabilityInputList()
    self.assertEquals(len(traceability_list), 1)
    # 00519267020111111111111111 is used for one valide traceability
    me_execution.ManufacturingExecution_processTraceabilityData('''00519267020111111111111111
''')
    traceability_list = me_execution.Base_getExpectedTraceabilityInputList()
    self.assertEquals(len(traceability_list), 1)





























