##############################################################################
#
# Copyright (c) 2004, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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

import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from testOrder import TestOrderMixin

class TestPackingListMixin(TestOrderMixin):
  """
    Test business template erp5_trade 
  """
  packable_packing_list_portal_type_list = ['Sale Packing List']
  container_portal_type = 'Container'
  container_line_portal_type = 'Container Line'
  container_cell_portal_type = 'Container Cell'

  default_sequence = 'stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
                      stepCreateOrganisation3 \
                      stepCreateOrder \
                      stepSetOrderProfile \
                      stepCreateNotVariatedResource \
                      stepTic \
                      stepCreateOrderLine \
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultValues \
                      stepOrderOrder \
                      stepTic \
                      stepConfirmOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      stepCheckDeliveryBuilding \
                      stepCheckPackingListIsNotDivergent '

  default_sequence_with_two_lines = '\
                      stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
                      stepCreateOrganisation3 \
                      stepCreateOrder \
                      stepSetOrderProfile \
                      stepCreateNotVariatedResource \
                      stepTic \
                      stepCreateOrderLine \
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultValues \
                      stepCreateNotVariatedResource \
                      stepTic \
                      stepCreateOrderLine \
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultValues \
                      stepOrderOrder \
                      stepTic \
                      stepConfirmOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      stepCheckDeliveryBuilding \
                      stepCheckPackingListIsNotDivergent '

  variated_default_sequence = '\
                      stepCreateOrganisation1 \
                      stepCreateOrganisation2 \
                      stepCreateOrganisation3 \
                      stepCreateOrder \
                      stepSetOrderProfile \
                      stepCreateVariatedResource \
                      stepTic \
                      stepCreateOrderLine \
                      stepSetOrderLineResource \
                      stepSetOrderLineDefaultValues \
                      stepSetOrderLineFullVCL \
                      stepCompleteOrderLineMatrix \
                      stepOrderOrder \
                      stepTic \
                      stepConfirmOrder \
                      stepTic \
                      stepCheckOrderSimulation \
                      stepCheckDeliveryBuilding \
                      stepCheckPackingListIsNotDivergent '

  def getTitle(self):
    return "Packing List"

  def enableLightInstall(self):
    """
    You can override this. 
    Return if we should do a light install (1) or not (0)
    """
    return 1

  def enableActivityTool(self):
    """
    You can override this.
    Return if we should create (1) or not (0) an activity tool.
    """
    return 1

  def stepCheckPackingListIsDivergent(self, sequence=None, sequence_list=None, 
                                      packing_list=None,**kw):
    """
      Test if packing list is divergent
    """
    if packing_list is None:
      packing_list = sequence.get('packing_list')
    self.failIf('Site Error' in packing_list.view())
    self.assertTrue(packing_list.isDivergent())

  def stepCheckNewPackingListIsDivergent(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is divergent
    """
    packing_list = sequence.get('new_packing_list')
    self.failIf('Site Error' in packing_list.view())
    self.stepCheckPackingListIsDivergent(packing_list=packing_list,sequence=sequence)

  def stepCheckPackingListIsCalculating(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is calculating
    """
    packing_list = sequence.get('packing_list')
    self.assertEquals('calculating',packing_list.getCausalityState())

  def stepCheckPackingListIsSolved(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is solved
    """
    packing_list = sequence.get('packing_list')
    self.assertEquals('solved',packing_list.getCausalityState())

  def stepCheckPackingListIsDiverged(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is divergent
    """
    packing_list = sequence.get('packing_list')
    self.assertEquals('diverged', packing_list.getCausalityState())

  def stepCheckPackingListIsNotDivergent(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is not divergent
    """
    packing_list = sequence.get('packing_list')
    self.assertFalse(packing_list.isDivergent())

  def stepChangePackingListLineResource(self, sequence=None, 
                                        sequence_list=None, **kw):
    """
    Change the resource of the packing list.
    """
    packing_list = sequence.get('packing_list')
    resource = sequence.get('resource')
    for packing_list_line in packing_list.objectValues(
                             portal_type=self.packing_list_line_portal_type):
      packing_list_line.edit(resource_value=resource)

  def stepDecreasePackingListLineQuantity(self, sequence=None,
      sequence_list=None, **kw):
    """
    Set a decreased quantity on packing list lines
    """
    packing_list = sequence.get('packing_list')
    quantity = sequence.get('line_quantity',default=self.default_quantity)
    quantity = quantity - 1
    sequence.edit(line_quantity=quantity)
    for packing_list_line in packing_list.objectValues(
        portal_type=self.packing_list_line_portal_type):
      packing_list_line.edit(quantity=quantity)
    sequence.edit(last_delta = sequence.get('last_delta', 0.0) - 1.0)

  def stepIncreasePackingListLineQuantity(self, sequence=None,
      sequence_list=None, **kw):
    """
    Set a increased quantity on packing list lines
    """
    packing_list = sequence.get('packing_list')
    quantity = sequence.get('line_quantity',default=self.default_quantity)
    quantity = quantity + 1
    sequence.edit(line_quantity=quantity)
    for packing_list_line in packing_list.objectValues(
        portal_type=self.packing_list_line_portal_type):
      packing_list_line.edit(quantity=quantity)
    sequence.edit(last_delta = sequence.get('last_delta', 0.0) + 1.0)

  def stepSplitAndDeferPackingList(self, sequence=None, sequence_list=None, **kw):
    """
      Do the split and defer action
    """
    packing_list = sequence.get('packing_list')
    packing_list.portal_workflow.doActionFor(packing_list,'split_prevision_action',
                                             wf_id='packing_list_causality_workflow',
                                             start_date=self.datetime + 15,
                                             stop_date=self.datetime + 25)

  def stepCheckPackingListSplitted(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list was splitted
    """
    order = sequence.get('order')
    packing_list_list = order.getCausalityRelatedValueList(
                               portal_type=self.packing_list_portal_type)
    self.assertEquals(2,len(packing_list_list))
    packing_list1 = None
    packing_list2 = None
    for packing_list in packing_list_list:
      if packing_list.getUid() == sequence.get('packing_list').getUid():
        packing_list1 = packing_list
      else:
        packing_list2 = packing_list
    sequence.edit(new_packing_list=packing_list2)
    for line in packing_list1.objectValues(
          portal_type= self.packing_list_line_portal_type):
      self.assertEquals(self.default_quantity-1,line.getQuantity())
    for line in packing_list2.objectValues(
          portal_type= self.packing_list_line_portal_type):
      self.assertEquals(1,line.getQuantity())

  def stepCheckPackingListSplittedTwoTimes(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is divergent
    """
    order = sequence.get('order')
    packing_list_list = order.getCausalityRelatedValueList(
                               portal_type=self.packing_list_portal_type)
    self.assertEquals(2,len(packing_list_list))
    packing_list1 = None
    packing_list2 = None
    for packing_list in packing_list_list:
      if packing_list.getUid() == sequence.get('packing_list').getUid():
        packing_list1 = packing_list
      else:
        packing_list2 = packing_list
    for line in packing_list1.objectValues(
          portal_type= self.packing_list_line_portal_type):
      self.assertEquals(self.default_quantity-2,line.getQuantity())
    for line in packing_list2.objectValues(
          portal_type= self.packing_list_line_portal_type):
      self.assertEquals(2,line.getQuantity())

  def stepCheckPackingListNotSplitted(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is divergent
    """
    order = sequence.get('order')
    packing_list_list = order.getCausalityRelatedValueList(
                               portal_type=self.packing_list_portal_type)
    self.assertEquals(1,len(packing_list_list))
    packing_list1 = sequence.get('packing_list')
    last_delta = sequence.get('last_delta', 0.0)
    for line in packing_list1.objectValues(
          portal_type= self.packing_list_line_portal_type):
      self.assertEquals(self.default_quantity + last_delta,
          line.getQuantity())
      simulation_list = line.getDeliveryRelatedValueList(
                            portal_type='Simulation Movement')
      self.assertEquals(len(simulation_list),1)
      simulation_movement = simulation_list[0]
      self.assertEquals(self.default_quantity + last_delta,
          simulation_movement.getCorrectedQuantity())

  def stepCheckPackingListNotSolved(self, sequence=None, sequence_list=None, **kw):
    """
      This step is specific to test_10 : the incorrectly used solver didn't
      solve anything.
    """
    order = sequence.get('order')
    packing_list_list = order.getCausalityRelatedValueList(
                               portal_type=self.packing_list_portal_type)
    self.assertEquals(1,len(packing_list_list))
    packing_list1 = sequence.get('packing_list')
    last_delta = sequence.get('last_delta', 0.0)
    for line in packing_list1.objectValues(
          portal_type= self.packing_list_line_portal_type):
      self.assertEquals(self.default_quantity + last_delta,
          line.getQuantity())
      simulation_list = line.getDeliveryRelatedValueList(
                            portal_type='Simulation Movement')
      self.assertEquals(len(simulation_list),1)
      simulation_movement = simulation_list[0]

      # Here we don't add last_delta, as the solver didn't do its work.
      self.assertEquals(self.default_quantity,
          simulation_movement.getCorrectedQuantity())

  def stepChangePackingListDestination(self, sequence=None, 
                                       sequence_list=None, **kw):
    """
      Test if packing list is divergent
    """
    organisation3 = sequence.get('organisation3')
    packing_list = sequence.get('packing_list')
    packing_list.edit(destination_value=organisation3)

  def stepCreateOrganisation3(self,sequence=None, sequence_list=None, **kw):
    """
      Create a empty organisation
    """
    self.stepCreateOrganisation(sequence=sequence, sequence_list=sequence_list,
                                **kw)
    organisation = sequence.get('organisation')
    sequence.edit(organisation3=organisation)

  def stepCheckSimulationDestinationUpdated(self,sequence=None, sequence_list=None, **kw):
    """
      Test if the destination of the simulation movement was changed
    """
    applied_rule = sequence.get('applied_rule')
    simulation_line_list = applied_rule.objectValues()
    self.assertEquals(len(simulation_line_list),1)
    org3 = sequence.get('organisation3')
    for simulation_line in simulation_line_list:
      self.assertEquals(simulation_line.getDestinationValue(),org3)

  def stepChangePackingListStartDate(self, sequence=None, sequence_list=None, **kw):
    """
      Change the start_date of the packing_list.
    """
    packing_list = sequence.get('packing_list')
    packing_list.edit(start_date=self.datetime + 15)

  def stepCheckSimulationStartDateUpdated(self,sequence=None, sequence_list=None, **kw):
    """
      Test if the start_date of the simulation movement was changed
    """
    applied_rule = sequence.get('applied_rule')
    simulation_line_list = applied_rule.objectValues()
    self.assertEquals(len(simulation_line_list),1)
    for simulation_line in simulation_line_list:
      self.assertEquals(simulation_line.getStartDate(),self.datetime + 15)

  def stepEditPackingListLine(self,sequence=None, sequence_list=None, **kw):
    """
      Edits a Packing List Line
    """
    packing_list_line = sequence.get('packing_list_line')
    packing_list_line.edit(description='This line was edited!')

  def stepDeletePackingListLine(self,sequence=None, sequence_list=None, **kw):
    """
      Deletes a Packing List Line
    """
    packing_list = sequence.get('packing_list')
    packing_list_line_id = sequence.get('packing_list_line').getId()
    packing_list.manage_delObjects([packing_list_line_id])

  def stepAddPackingListLine(self,sequence=None, sequence_list=None, **kw):
    """
      Adds a Packing List Line
    """
    packing_list = sequence.get('packing_list')
    packing_list_line = packing_list.newContent(
        portal_type=self.packing_list_line_portal_type)
    self.stepCreateNotVariatedResource(sequence=sequence,
        sequence_list=sequence_list, **kw)
    resource = sequence.get('resource')
    packing_list_line.setResourceValue(resource)
    packing_list_line.edit(price=100, quantity=200)

  def stepCheckSimulationConnected(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    applied_rule = sequence.get('applied_rule')
    simulation_line_list = applied_rule.objectValues()
    self.assertEquals(len(simulation_line_list),1)
    packing_list = sequence.get('packing_list')
    packing_list_line = sequence.get('packing_list_line')
    for simulation_line in simulation_line_list:
      self.assertEquals(simulation_line.getDeliveryValue(),packing_list_line)

  def stepCheckSimulationDisconnected(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    applied_rule = sequence.get('applied_rule')
    simulation_line_list = applied_rule.objectValues()
    self.assertEquals(len(simulation_line_list),1)
    for simulation_line in simulation_line_list:
      self.assertEquals(simulation_line.getDeliveryValue(),None)

  def stepModifySimulationLineQuantity(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    applied_rule = sequence.get('applied_rule')
    simulation_line_list = applied_rule.objectValues()
    self.assertEquals(len(simulation_line_list),1)
    for simulation_line in simulation_line_list:
      simulation_line.edit(quantity=self.default_quantity-1)

  def stepModifySimulationLineStartDate(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    applied_rule = sequence.get('applied_rule')
    simulation_line_list = applied_rule.objectValues()
    resource_list = sequence.get('resource_list')
    self.assertEquals(len(simulation_line_list),len(resource_list))
    for simulation_line in simulation_line_list:
      simulation_line.edit(start_date=self.datetime+15)

  def stepAdoptPrevision(self,sequence=None, sequence_list=None, 
                         packing_list=None,**kw):
    """
      Check if simulation movement are disconnected
    """
    if packing_list is None:
      packing_list = sequence.get('packing_list')
    LOG('packing_list.getSimulationState()',0,packing_list.getSimulationState())
    LOG('packing_list.getCausalityState()',0,packing_list.getCausalityState())
    packing_list.portal_workflow.doActionFor(packing_list,'adopt_prevision_action')

  def stepNewPackingListAdoptPrevision(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    packing_list = sequence.get('new_packing_list')
    self.stepAdoptPrevision(sequence=sequence,packing_list=packing_list)

  def stepAcceptDecisionPackingList(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    packing_list = sequence.get('packing_list')
    packing_list.portal_workflow.doActionFor(packing_list,'accept_decision_action')

  def stepCheckPackingListLineWithNewQuantityPrevision(self,sequence=None, sequence_list=None, **kw):
    """
      Look if the packing list has new previsions
    """
    packing_list_line = sequence.get('packing_list_line')
    self.assertEquals(packing_list_line.getQuantity(),self.default_quantity-1)

  def stepCheckNewPackingListAfterStartDateAdopt(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    applied_rule = sequence.get('applied_rule')
    packing_list_line = sequence.get('packing_list_line')
    packing_list = sequence.get('packing_list')
    LOG('CheckNewPackingList, self.datetime+15',0,self.datetime+15)
    LOG('CheckNewPackingList, packing_list.getStartDate',0,packing_list.getStartDate())
    self.assertEquals(packing_list_line.getQuantity(),self.default_quantity)
    self.assertEquals(packing_list.getStartDate(),self.datetime+15)
    simulation_line_list = applied_rule.objectValues()
    resource_list = sequence.get('resource_list')
    self.assertEquals(len(simulation_line_list),len(resource_list))
    delivery_value_list = []
    for simulation_line in simulation_line_list:
#      self.assertNotEquals(simulation_line.getDeliveryValue(),None)
      delivery_value = simulation_line.getDeliveryValue()
      if delivery_value not in delivery_value_list:
        delivery_value_list.append(delivery_value_list)
#      new_packing_list = delivery_value.getParent()
#      self.assertNotEquals(new_packing_list.getUid(),packing_list.getUid())
    self.assertEquals(len(delivery_value_list),len(resource_list))

  def stepAddPackingListContainer(self,sequence=None, 
                                  packing_list=None,sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    if packing_list is None:
      packing_list = sequence.get('packing_list')
    container = packing_list.newContent(portal_type=self.container_portal_type)
    sequence.edit(container=container)

  def stepDefineNewPackingListContainer(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    packing_list = sequence.get('new_packing_list')
    self.stepAddPackingListContainer(sequence=sequence,packing_list=packing_list)
    self.stepAddPackingListContainerLine(sequence=sequence)
    self.stepSetContainerLineFullQuantity(quantity=1,sequence=sequence)

  def stepAddPackingListContainerLine(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    container = sequence.get('container')
    container_line = container.newContent(portal_type=self.container_line_portal_type)
    sequence.edit(container_line=container_line)
    resource = sequence.get('resource')
    container_line.edit(resource_value=resource)

  def stepSetContainerLineSmallQuantity(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    container_line = sequence.get('container_line')
    container_line.edit(quantity=self.default_quantity-1)

  def stepSetContainerLineFullQuantity(self,sequence=None, sequence_list=None, 
                                       quantity=None,**kw):
    """
      Check if simulation movement are disconnected
    """
    container_line = sequence.get('container_line')
    if quantity is None:
      quantity = sequence.get('line_quantity',self.default_quantity)
    container_line.edit(quantity=quantity)
    container_line.immediateReindexObject()

  def stepSetContainerFullQuantity(self,sequence=None, sequence_list=None, 
                                       quantity=None,**kw):
    """
      Really fills the container
    """
    packing_list = sequence.get('packing_list')
    container = sequence.get('container')
    #empty container
    container.deleteContent(container.contentIds())
    for line in packing_list.objectValues(
        portal_type=self.packing_list_line_portal_type):
      resource = line.getResourceValue()
      tmp_kw={'movement.resource_uid':resource.getUid()}
      container_line = \
          container.newContent(portal_type=self.container_line_portal_type)
      container_line.setResourceValue(resource)
      # without variation
      if not line.hasCellContent():
        quantity = line.getQuantity()
        container_line.edit(quantity=quantity)
        container_line.immediateReindexObject()
      # with variation
      elif line.hasCellContent():
        vcl = line.getVariationCategoryList()
        vcl.sort()
        base_id = 'movement'
        container_line.setVariationCategoryList(vcl)
        cell_key_list = list(line.getCellKeyList(base_id=base_id))
        cell_key_list.sort()
        for cell_key in cell_key_list:
          if line.hasCell(base_id=base_id, *cell_key):
            old_cell = line.getCell(base_id=base_id, *cell_key)
            cell = container_line.newCell(base_id=base_id,
                portal_type=self.container_cell_portal_type, *cell_key)
            cell.edit(mapped_value_property_list=['price', 'quantity'],
                price=old_cell.getPrice(),
                quantity=old_cell.getQuantity(),
                predicate_category_list=cell_key,
                variation_category_list=cell_key)
            cell.immediateReindexObject()

  def stepCheckPackingListIsNotPacked(self,sequence=None, sequence_list=None, **kw):
    """
      Check that the number of objects in containers are
      not equals to the quantity of the packing list
    """
    packing_list = sequence.get('packing_list')
    if packing_list.getPortalType() not in \
        self.packable_packing_list_portal_type_list: return
    self.assertEquals(0,packing_list.isPacked())
    self.assertEquals('missing',packing_list.getContainerState())

  def stepCheckPackingListIsPacked(self,sequence=None, sequence_list=None, 
                                   packing_list=None,**kw):
    """
      Check that the number of objects in containers are
      equals to the quantity of the packing list
    """
    if packing_list is None:
      packing_list = sequence.get('packing_list')
    if packing_list.getPortalType() not in \
        self.packable_packing_list_portal_type_list: return
    get_transaction().commit()
    self.assertEquals(1,packing_list.isPacked())
    self.assertEquals('packed',packing_list.getContainerState())

  def stepCheckNewPackingListIsPacked(self,sequence=None, sequence_list=None, **kw):
    """
      Check that the number of objects in containers are
      equals to the quantity of the packing list
    """
    packing_list = sequence.get('new_packing_list')
    if packing_list.getPortalType() not in \
        self.packable_packing_list_portal_type_list: return
    self.stepCheckPackingListIsPacked(sequence=sequence,
                                      packing_list=packing_list)


class TestPackingList(TestPackingListMixin, ERP5TypeTestCase) :

  run_all_test = 1
  quiet = 0

  def test_01_PackingListDecreaseQuantity(self, quiet=quiet, run=run_all_test):
    """
      Change the quantity on an delivery line, then
      see if the packing list is divergent and then
      split and defer the packing list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      stepDecreasePackingListLineQuantity \
                      stepCheckPackingListIsCalculating \
                      stepSplitAndDeferPackingList \
                      stepTic \
                      stepCheckPackingListIsSolved \
                      stepCheckPackingListSplitted \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_02_PackingListChangeDestination(self, quiet=quiet, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      stepChangePackingListDestination \
                      stepCheckPackingListIsCalculating \
                      stepAcceptDecisionPackingList \
                      stepTic \
                      stepCheckPackingListIsSolved \
                      stepCheckPackingListIsNotDivergent \
                      stepCheckSimulationDestinationUpdated \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_03_PackingListChangeStartDate(self, quiet=quiet, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      stepChangePackingListStartDate \
                      stepCheckPackingListIsCalculating \
                      stepAcceptDecisionPackingList \
                      stepTic \
                      stepCheckPackingListIsSolved \
                      stepCheckPackingListIsNotDivergent \
                      stepCheckSimulationStartDateUpdated \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_04_PackingListDeleteLine(self, quiet=quiet, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      stepCheckSimulationConnected \
                      stepDeletePackingListLine \
                      stepCheckPackingListIsNotDivergent \
                      stepTic \
                      stepCheckSimulationDisconnected \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_05_SimulationChangeQuantity(self, quiet=quiet, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      stepModifySimulationLineQuantity \
                      stepTic \
                      stepCheckPackingListIsDiverged \
                      stepAdoptPrevision \
                      stepTic \
                      stepCheckPackingListIsNotDivergent \
                      stepCheckPackingListIsSolved \
                      stepCheckPackingListLineWithNewQuantityPrevision \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_06_SimulationChangeStartDate(self, quiet=quiet, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      stepModifySimulationLineStartDate \
                      stepTic \
                      stepCheckPackingListIsDiverged \
                      stepAdoptPrevision \
                      stepTic \
                      stepCheckPackingListIsSolved \
                      stepCheckNewPackingListAfterStartDateAdopt \
                      '
    # XXX Check if there is a new packing list created
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_07_SimulationChangeStartDateWithTwoOrderLine(self, quiet=quiet, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence_with_two_lines + '\
                      stepModifySimulationLineStartDate \
                      stepTic \
                      stepCheckPackingListIsDiverged \
                      stepCheckPackingListIsDivergent \
                      stepAdoptPrevision \
                      stepTic \
                      stepCheckPackingListIsNotDivergent \
                      stepCheckPackingListIsSolved \
                      stepCheckNewPackingListAfterStartDateAdopt \
                      '
    # XXX Check if there is a new packing list created
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_08_AddContainers(self, quiet=quiet, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      stepAddPackingListContainer \
                      stepAddPackingListContainerLine \
                      stepSetContainerLineSmallQuantity \
                      stepCheckPackingListIsNotPacked \
                      stepSetContainerFullQuantity \
                      stepTic \
                      stepCheckPackingListIsPacked \
                      '
    # XXX Check if there is a new packing list created
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_09_AddContainersWithVariatedResources(self, quiet=quiet, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a order with cells
    sequence_string = self.variated_default_sequence + '\
                      stepAddPackingListContainer \
                      stepAddPackingListContainerLine \
                      stepSetContainerLineSmallQuantity \
                      stepCheckPackingListIsNotPacked \
                      stepSetContainerFullQuantity \
                      stepTic \
                      stepCheckPackingListIsPacked \
                      '
    # XXX Check if there is a new packing list created
    sequence_list.addSequenceString(sequence_string)
    
    sequence_list.play(self, quiet=quiet)

  def test_10_PackingListIncreaseQuantity(self, quiet=quiet, run=run_all_test):
    """
    - Increase the quantity on an delivery line
    - check if the packing list is divergent
    - Apply the "split and defer" solver to the packing list
    - check that nothing was splitted and the packing list is still divergent
      (reset the delta before, as we don't expect a modification)

    Basically, when we apply "split and defer" to a packing list, we don't
    want it to modify lines which have been increased.
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      stepIncreasePackingListLineQuantity \
                      stepCheckPackingListIsCalculating \
                      stepSplitAndDeferPackingList \
                      stepTic \
                      stepCheckPackingListIsDiverged \
                      stepCheckPackingListIsDivergent \
                      stepCheckPackingListNotSolved \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_11_PackingListDecreaseTwoTimesQuantityAndUpdateDelivery(self,
                                               quiet=quiet, run=run_all_test):
    """
      Change the quantity on an delivery line, then
      see if the packing list is divergent and then
      split and defer the packing list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      stepDecreasePackingListLineQuantity \
                      stepCheckPackingListIsCalculating \
                      stepSplitAndDeferPackingList \
                      stepTic \
                      stepCheckPackingListIsSolved \
                      stepCheckPackingListSplitted \
                      stepDecreasePackingListLineQuantity \
                      stepCheckPackingListIsCalculating \
                      stepSplitAndDeferPackingList \
                      stepTic \
                      stepCheckNewPackingListIsDivergent \
                      stepNewPackingListAdoptPrevision \
                      stepTic \
                      stepCheckPackingListIsSolved \
                      stepCheckPackingListSplittedTwoTimes \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_12_PackingListLineChangeResource(self, quiet=quiet, run=run_all_test):
    """
    Test if delivery diverged when we change the resource.
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      stepCreateNotVariatedResource \
                      stepChangePackingListLineResource \
                      stepCheckPackingListIsCalculating \
                      stepTic \
                      stepCheckPackingListIsDivergent \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_14_PackingListHavePriceCurrencyCategory(self, quiet=quiet,
                                                   run=run_all_test):
    """Deliveries must have a price currency category. #252
    """
    if not run:
      return
    pl = self.getPortal().getDefaultModule(self.packing_list_portal_type
               ).newContent(portal_type=self.packing_list_portal_type)
    self.failUnless(hasattr(pl, 'getPriceCurrency'))
    
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPackingList))
  return suite

