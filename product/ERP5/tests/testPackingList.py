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

#
# Skeleton ZopeTestCase
#

from random import randint

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, \
                                             noSecurityManager
from DateTime import DateTime
from Acquisition import aq_base, aq_inner
from zLOG import LOG
from Products.ERP5Type.DateUtils import addToDate
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
import time
import os
from Products.ERP5Type import product_path
from Products.CMFCore.utils import getToolByName
from testOrder import TestOrderMixin

class TestPackingListMixin(TestOrderMixin):
  """
    Test business template erp5_trade 
  """
  container_type = 'Container'
  container_line_type = 'Container Line'

  default_sequence = 'CreateOrganisation1 \
                      CreateOrganisation2 \
                      CreateOrganisation3 \
                      CreateOrder \
                      SetOrderProfile \
                      CreateNotVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      OrderOrder \
                      Tic \
                      ConfirmOrder \
                      Tic \
                      CheckOrderSimulation \
                      CheckDeliveryBuilding \
                      CheckPackingListIsNotDivergent '

  default_sequence_with_two_lines = 'CreateOrganisation1 \
                      CreateOrganisation2 \
                      CreateOrganisation3 \
                      CreateOrder \
                      SetOrderProfile \
                      CreateNotVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      CreateNotVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      OrderOrder \
                      Tic \
                      ConfirmOrder \
                      Tic \
                      CheckOrderSimulation \
                      CheckDeliveryBuilding \
                      CheckPackingListIsNotDivergent '

  variated_default_sequence = 'CreateOrganisation1 \
                      CreateOrganisation2 \
                      CreateOrganisation3 \
                      CreateOrder \
                      SetOrderProfile \
                      CreateVariatedResource \
                      Tic \
                      CreateOrderLine \
                      SetOrderLineResource \
                      SetOrderLineDefaultValues \
                      SetOrderLineFullVCL \
                      CompleteOrderLineMatrix \
                      OrderOrder \
                      Tic \
                      ConfirmOrder \
                      Tic \
                      CheckOrderSimulation \
                      CheckDeliveryBuilding \
                      CheckPackingListIsNotDivergent '

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

  def stepCheckPackingListIsDivergent(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is divergent
    """
    packing_list = sequence.get('packing_list')
    self.assertEquals(True,packing_list.isDivergent())

  def stepCheckPackingListIsCalculating(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is divergent
    """
    packing_list = sequence.get('packing_list')
    self.assertEquals('calculating',packing_list.getCausalityState())

  def stepCheckPackingListIsSolved(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is divergent
    """
    packing_list = sequence.get('packing_list')
    self.assertEquals('solved',packing_list.getCausalityState())

  def stepCheckPackingListIsDiverged(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is divergent
    """
    packing_list = sequence.get('packing_list')
    self.assertEquals('diverged',packing_list.getCausalityState())

  def stepCheckPackingListIsNotDivergent(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is not divergent
    """
    packing_list = sequence.get('packing_list')
    self.assertEquals(False,packing_list.isDivergent())

  def stepDecreasePackingListLineQuantity(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is divergent
    """
    packing_list = sequence.get('packing_list')
    for packing_list_line in packing_list.objectValues(
                             portal_type=self.packing_list_line_portal_type):
      packing_list_line.edit(quantity=self.default_quantity-1)

  def stepIncreasePackingListLineQuantity(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is divergent
    """
    packing_list = sequence.get('packing_list')
    for packing_list_line in packing_list.objectValues(
                             portal_type=self.packing_list_line_portal_type):
      packing_list_line.edit(quantity=self.default_quantity+1)

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
      self.assertEquals(self.default_quantity-1,line.getQuantity())
    for line in packing_list2.objectValues(
          portal_type= self.packing_list_line_portal_type):
      self.assertEquals(1,line.getQuantity())

  def stepCheckPackingListNotSplitted(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is divergent
    """
    order = sequence.get('order')
    packing_list_list = order.getCausalityRelatedValueList(
                               portal_type=self.packing_list_portal_type)
    self.assertEquals(1,len(packing_list_list))
    packing_list1 = sequence.get('packing_list')
    for line in packing_list1.objectValues(
          portal_type= self.packing_list_line_portal_type):
      self.assertEquals(self.default_quantity+1,line.getQuantity())
      simulation_list = line.getDeliveryRelatedValueList(
                            portal_type='Simulation Movement')
      self.assertEquals(len(simulation_list),1)
      simulation_movement = simulation_list[0]
      self.assertEquals(simulation_movement.getQuantity(),self.default_quantity+1)

  def stepChangePackingListDestination(self, sequence=None, sequence_list=None, **kw):
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
      Create a empty organisation
    """
    applied_rule = sequence.get('applied_rule')
    simulation_line_list = applied_rule.objectValues()
    self.assertEquals(len(simulation_line_list),1)
    org3 = sequence.get('organisation3')
    for simulation_line in simulation_line_list:
      self.assertEquals(simulation_line.getDestinationValue(),org3)

  def stepChangePackingListStartDate(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is divergent
    """
    packing_list = sequence.get('packing_list')
    packing_list.edit(start_date=self.datetime + 15)

  def stepCheckSimulationStartDateUpdated(self,sequence=None, sequence_list=None, **kw):
    """
      Create a empty organisation
    """
    applied_rule = sequence.get('applied_rule')
    simulation_line_list = applied_rule.objectValues()
    self.assertEquals(len(simulation_line_list),1)
    for simulation_line in simulation_line_list:
      self.assertEquals(simulation_line.getStartDate(),self.datetime + 15)

  def stepDeletePackingListLine(self,sequence=None, sequence_list=None, **kw):
    """
      Create a empty organisation
    """
    packing_list = sequence.get('packing_list')
    packing_list_line_id = sequence.get('packing_list_line').getId()
    packing_list.manage_delObjects([packing_list_line_id])

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

  def stepAdoptPrevision(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    packing_list = sequence.get('packing_list')
    LOG('packing_list.getSimulationState()',0,packing_list.getSimulationState())
    LOG('packing_list.getCausalityState()',0,packing_list.getCausalityState())
    packing_list.portal_workflow.doActionFor(packing_list,'adopt_prevision_action')

  def stepAcceptDecision(self,sequence=None, sequence_list=None, **kw):
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

  def stepAddPackingListContainer(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    packing_list = sequence.get('packing_list')
    container = packing_list.newContent(portal_type=self.container_type)
    sequence.edit(container=container)

  def stepAddPackingListContainerLine(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    container = sequence.get('container')
    container_line = container.newContent(portal_type=self.container_line_type)
    sequence.edit(container_line=container_line)
    resource = sequence.get('resource')
    container_line.edit(resource_value=resource)

  def stepSetContainerLineSmallQuantity(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    container_line = sequence.get('container_line')
    container_line.edit(quantity=self.default_quantity-1)

  def stepSetContainerLineFullQuantity(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    container_line = sequence.get('container_line')
    container_line.edit(quantity=self.default_quantity)
    container_line.immediateReindexObject()

  def stepCheckPackingListIsNotPacked(self,sequence=None, sequence_list=None, **kw):
    """
      Check that the number of objects in containers are
      not equals to the quantity of the packing list
    """
    packing_list = sequence.get('packing_list')
    self.assertEquals(0,packing_list.isPacked())
    self.assertEquals('missing',packing_list.getContainerState())

  def stepCheckPackingListIsPacked(self,sequence=None, sequence_list=None, **kw):
    """
      Check that the number of objects in containers are
      equals to the quantity of the packing list
    """
    packing_list = sequence.get('packing_list')
    get_transaction().commit()
    self.assertEquals(1,packing_list.isPacked())
    self.assertEquals('packed',packing_list.getContainerState())

  def stepCommit(self, sequence=None, sequence_list=None, **kw):
    """
    Commit transaction
    """
    get_transaction().commit()


class TestPackingList(TestPackingListMixin, ERP5TypeTestCase) :

  run_all_test = 1
  def test_01_PackingListDecreaseQuantity(self, quiet=0, run=run_all_test):
    """
      Change the quantity on an delivery line, then
      see if the packing list is divergent and then
      split and defer the packing list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      DecreasePackingListLineQuantity \
                      CheckPackingListIsCalculating \
                      SplitAndDeferPackingList \
                      Tic \
                      CheckPackingListIsSolved \
                      CheckPackingListSplitted \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_02_PackingListChangeDestination(self, quiet=0, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      ChangePackingListDestination \
                      CheckPackingListIsNotDivergent \
                      Tic \
                      CheckSimulationDestinationUpdated \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_03_PackingListChangeStartDate(self, quiet=0, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      ChangePackingListStartDate \
                      CheckPackingListIsCalculating \
                      AcceptDecision \
                      Tic \
                      CheckPackingListIsSolved \
                      CheckPackingListIsNotDivergent \
                      CheckSimulationStartDateUpdated \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_04_PackingListDeleteLine(self, quiet=0, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      CheckSimulationConnected \
                      DeletePackingListLine \
                      CheckPackingListIsNotDivergent \
                      Tic \
                      CheckSimulationDisconnected \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_05_SimulationChangeQuantity(self, quiet=0, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      ModifySimulationLineQuantity \
                      Tic \
                      CheckPackingListIsDiverged \
                      AdoptPrevision \
                      Tic \
                      CheckPackingListIsNotDivergent \
                      CheckPackingListIsSolved \
                      CheckPackingListLineWithNewQuantityPrevision \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_06_SimulationChangeStartDate(self, quiet=0, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      ModifySimulationLineStartDate \
                      Tic \
                      CheckPackingListIsDiverged \
                      AdoptPrevision \
                      Tic \
                      CheckPackingListIsSolved \
                      CheckNewPackingListAfterStartDateAdopt \
                      '
    # XXX Check if there is a new packing list created
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_07_SimulationChangeStartDateWithTwoOrderLine(self, quiet=0, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence_with_two_lines + '\
                      ModifySimulationLineStartDate \
                      Tic \
                      CheckPackingListIsDiverged \
                      CheckPackingListIsDivergent \
                      AdoptPrevision \
                      Tic \
                      CheckPackingListIsNotDivergent \
                      CheckPackingListIsSolved \
                      CheckNewPackingListAfterStartDateAdopt \
                      '
    # XXX Check if there is a new packing list created
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_08_AddContainers(self, quiet=0, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      AddPackingListContainer \
                      AddPackingListContainerLine \
                      SetContainerLineSmallQuantity \
                      CheckPackingListIsNotPacked \
                      SetContainerLineFullQuantity \
                      Tic \
                      CheckPackingListIsPacked \
                      '
    # XXX Check if there is a new packing list created
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_09_AddContainersWithVariatedResources(self, quiet=0, run=run_all_test):
    """
      Test generation of delivery list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      AddPackingListContainer \
                      AddPackingListContainerLine \
                      SetContainerLineSmallQuantity \
                      CheckPackingListIsNotPacked \
                      SetContainerLineFullQuantity \
                      Tic \
                      CheckPackingListIsPacked \
                      '
    # XXX Check if there is a new packing list created
    sequence_list.addSequenceString(sequence_string)
    
    sequence_list.play(self)

  def test_10_PackingListIncreaseQuantity(self, quiet=0, run=run_all_test):
    """
      Change the quantity on an delivery line, then
      see if the packing list is divergent and then
      split and defer the packing list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      IncreasePackingListLineQuantity \
                      CheckPackingListIsCalculating \
                      SplitAndDeferPackingList \
                      Tic \
                      CheckPackingListIsSolved \
                      CheckPackingListNotSplitted \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(Test))
        return suite

