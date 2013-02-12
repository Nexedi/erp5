##############################################################################
#
# Copyright (c) 2004-2008 Nexedi SA and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5.Document.BusinessTemplate import getChainByType
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5.tests.testOrder import TestOrderMixin
from DateTime import DateTime
from Products.ERP5Type.Globals import PersistentMapping

class TestPackingListMixin(TestOrderMixin):
  """
    Test business template erp5_trade
  """
  container_portal_type = 'Container'
  container_line_portal_type = 'Container Line'
  container_cell_portal_type = 'Container Cell'
  default_order_sequence = """
        CreateOrganisation1
        CreateOrganisation2
        CreateOrganisation3
        CreateProject1
        CreateProject2
        CreateOrder
        CreateCurrency
        SetOrderPriceCurrency
        SetOrderProfile
        """
  # Simple order without cell
  default_sequence = default_order_sequence + """
        CreateNotVariatedResource
        Tic
        CreateOrderLine
        SetOrderLineResource
        SetOrderLineDefaultValues
        OrderOrder
        Tic
        ConfirmOrder
        Tic
        PackingListBuilderAlarm
        Tic
        CheckOrderSimulation
        CheckDeliveryBuilding
        CheckPackingListIsNotDivergent
        CheckOrderPackingList
        """
  confirmed_order_without_packing_list = default_order_sequence + """
        CreateNotVariatedResource
        Tic
        CreateOrderLine
        SetOrderLineResource
        SetOrderLineDefaultValues
        OrderOrder
        Tic
        ConfirmOrder
        Tic
        PackingListBuilderAlarm
        Tic
        """
  default_sequence_with_duplicated_lines = default_order_sequence + """
        CreateNotVariatedResource
        Tic
        CreateOrderLine
        SetOrderLineResource
        SetOrderLineDefaultValues
        Tic
        CreateOrderLine
        SetOrderLineResource
        SetOrderLineDefaultValues
        OrderOrder
        Tic
        ConfirmOrder
        Tic
        PackingListBuilderAlarm
        Tic
        CheckOrderSimulation
        CheckDeliveryBuilding
        CheckPackingListIsNotDivergent
        CheckOrderPackingList
        """
  default_sequence_with_two_lines = default_order_sequence + """
        CreateNotVariatedResource
        Tic
        CreateOrderLine
        SetOrderLineResource
        SetOrderLineDefaultValues
        CreateNotVariatedResource
        Tic
        CreateOrderLine
        SetOrderLineResource
        SetOrderLineDefaultValues
        OrderOrder
        Tic
        ConfirmOrder
        Tic
        PackingListBuilderAlarm
        Tic
        CheckOrderSimulation
        CheckDeliveryBuilding
        CheckPackingListIsNotDivergent
        CheckOrderPackingList
        """
  variated_default_sequence = default_order_sequence + """
        CreateVariatedResource
        Tic
        CreateOrderLine
        SetOrderLineResource
        SetOrderLineDefaultValues
        SetOrderLineFullVCL
        CompleteOrderLineMatrix
        OrderOrder
        Tic
        ConfirmOrder
        Tic
        PackingListBuilderAlarm
        Tic
        CheckOrderSimulation
        CheckDeliveryBuilding
        CheckPackingListIsNotDivergent
        CheckOrderPackingList
        """

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

  def stepCheckOrderPackingList(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is matching order
    """
    packing_list = sequence.get('packing_list')
    order = sequence.get('order')
    self.assertEquals(packing_list.getCausalityValue(), order)
    self.assertEquals(packing_list.getSource(), order.getSource())
    self.assertEquals(packing_list.getDestination(), order.getDestination())
    self.assertEquals(packing_list.getDestinationSection(),
                                       order.getDestinationSection())
    self.assertEquals(packing_list.getSourceSection(),
                                       order.getSourceSection())
    self.assertEquals(packing_list.getSourceDecision(),
                                       order.getSourceDecision())
    self.assertEquals(packing_list.getDestinationAdministration(),
                                       order.getDestinationAdministration())
    self.assertEquals(packing_list.getSourceAdministration(),
                                       order.getSourceAdministration())
    self.assertEquals(packing_list.getPriceCurrency(),
                                       order.getPriceCurrency())
    self.assertEquals(packing_list.getDestinationProject(),
                                       order.getDestinationProject())
    self.assertEquals(packing_list.getSourceProject(),
                                       order.getSourceProject())

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

  def stepCheckNewPackingListIsSolved(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('new_packing_list')
    self.assertEquals('solved', packing_list.getCausalityState())

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

  def stepChangeOrderLineResource(self, sequence=None,
                                        sequence_list=None, **kw):
    """
    Change the resource of the order.
    """
    order = sequence.get('order')
    resource = sequence.get('resource')
    for order_line in order.objectValues(
                             portal_type=self.order_line_portal_type):
      order_line.edit(resource_value=resource)

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

  def stepDecreaseOrderLineQuantity(self, sequence=None, sequence_list=None,
                                    **kw):
    """
    Set a decreased quantity on order lines
    """
    order = sequence.get('order')
    quantity = sequence.get('line_quantity', default=self.default_quantity - 1)
    sequence.edit(line_quantity=quantity)
    for order_line in order.objectValues(
        portal_type=self.order_line_portal_type):
      order_line.edit(quantity=quantity)

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
    solver_process_tool = self.portal.portal_solver_processes
    solver_process = solver_process_tool.newSolverProcess(packing_list)
    quantity_solver_decision, = [x for x in solver_process.contentValues()
      if x.getCausalityValue().getTestedProperty() == 'quantity']
    # use Quantity Split Solver.
    quantity_solver_decision.setSolverValue(self.portal.portal_solvers['Quantity Split Solver'])
    # configure for Quantity Split Solver.
    kw = {'delivery_solver':'FIFO Delivery Solver',
          'start_date':self.datetime + 15,
          'stop_date':self.datetime + 25}
    quantity_solver_decision.updateConfiguration(**kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()
    # build split deliveries manually. XXX ad-hoc
    previous_tag = None
    for delivery_builder in packing_list.getBuilderList():
      after_tag = []
      if previous_tag:
        after_tag.append(previous_tag)
      delivery_builder.activate(
        after_method_id=('solve',
                         'immediateReindexObject',
                         'recursiveImmediateReindexObject',), # XXX too brutal.
        after_tag=after_tag,
        ).build(explanation_uid=packing_list.getCausalityValue().getUid())

  def stepSplitAndDeferDoNothingPackingList(self, sequence=None, sequence_list=None, **kw):
    """
      Do the split and defer action, but choose "do nothing" for divergences
    """
    packing_list = sequence.get('packing_list')
    kw = {'listbox':[
      {'listbox_key':line.getRelativeUrl(),
       'choice':'ignore'} for line in packing_list.getMovementList()
      if line.isDivergent()]}
    self.portal.portal_workflow.doActionFor(
      packing_list,
      'split_and_defer_action',
      start_date=self.datetime + 15,
      stop_date=self.datetime + 25,
      **kw)

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
    simulation_movement_list = applied_rule.objectValues()
    self.assertEquals(len(simulation_movement_list),1)
    org3 = sequence.get('organisation3')
    for simulation_movement in simulation_movement_list:
      simulation_movement = simulation_movement.objectValues()[0].objectValues()[0]
      self.assertEquals(simulation_movement.getDestinationValue(),org3)

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
    simulation_movement_list = applied_rule.objectValues()
    self.assertEquals(len(simulation_movement_list),1)
    delivery_applied_rule = simulation_movement_list[0].objectValues()[0]
    simulation_movement_list = delivery_applied_rule.objectValues()
    self.assertEquals(len(simulation_movement_list),1)
    for simulation_movement in simulation_movement_list:
      self.assertEquals(simulation_movement.getStartDate(),self.datetime + 15)

  def stepCheckSimulationQuantityUpdated(self,sequence=None, sequence_list=None, **kw):
    """
      Test if the quantity of the simulation movement was changed
    """
    applied_rule = sequence.get('applied_rule')
    simulation_movement_list = applied_rule.objectValues()
    self.assertEquals(len(simulation_movement_list),1)
    for simulation_movement in simulation_movement_list:
      simulation_movement = simulation_movement.objectValues()[0].objectValues()[0]
      self.assertEquals(simulation_movement.getQuantity() +
                        simulation_movement.getDeliveryError(),
                        self.default_quantity)

  def stepCheckSimulationQuantityUpdatedForMergedLine(self,sequence=None, sequence_list=None, **kw):
    """
      Test if the quantity of the simulation movement was changed
    """
    applied_rule = sequence.get('applied_rule')
    simulation_movement_list = applied_rule.objectValues()
    self.assertEquals(len(simulation_movement_list),2)
    for simulation_movement in simulation_movement_list:
      simulation_movement = simulation_movement.objectValues()[0].objectValues()[0]
      self.assertEquals(simulation_movement.getQuantity() +
                        simulation_movement.getDeliveryError(),
                        self.default_quantity)

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
      Check if simulation movement are connected
    """
    applied_rule = sequence.get('applied_rule')
    simulation_movement_list = applied_rule.objectValues()
    self.assertEquals(len(simulation_movement_list),1)
    order_line = sequence.get('order_line')
    packing_list = sequence.get('packing_list')
    packing_list_line = sequence.get('packing_list_line')
    for simulation_movement in simulation_movement_list:
      self.assertEquals(simulation_movement.getDeliveryValue(), order_line)
      self.assertEquals(packing_list_line.getCausalityValue(),
                        order_line)
      rule_list = simulation_movement.objectValues()
      self.failUnless(len(rule_list), 1)
      delivering_rule = rule_list[0]
      self.failUnless(delivering_rule.getSpecialiseValue().getPortalType(),
                      'Delivering Rule')
      child_simulation_movement_list = delivering_rule.objectValues()
      self.failUnless(len(child_simulation_movement_list), 1)
      child_simulation_movement = child_simulation_movement_list[0]
      self.assertEquals(child_simulation_movement.getDeliveryValue(),
                        packing_list_line)

  def stepCheckSimulationDisconnected(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    applied_rule = sequence.get('applied_rule')
    simulation_movement_list = applied_rule.objectValues()
    self.assertEquals(len(simulation_movement_list),1)
    for simulation_movement in simulation_movement_list:
      child_simulation_movement = simulation_movement.objectValues()[0].objectValues()[0]
      self.assertEquals(child_simulation_movement.getDeliveryValue(),None)

  def stepCheckTwoSimulationLines(self, sequence):
    """
    Check there are exactly two simulation lines related to the packing list
    line(s)
    """
    simulation_movement_list = self._getSPLSimulationMovementList(sequence)
    self.assertEquals(len(simulation_movement_list),2)

  def _getSPLSimulationMovementList(self, sequence):
    """ Get the simulation movement lines from sales packing list movements """
    packing_list = sequence['packing_list']
    movement_list = packing_list.getMovementList()
    simulation_movement_list = []
    for movement in movement_list:
      simulation_movement_list.extend(
        movement.getDeliveryRelatedValueList()
      )
    return simulation_movement_list

  def stepModifySimulationLineQuantity(self,sequence=None, sequence_list=None, **kw):
    """
      Modify quantity on simulation lines related to SPL lines
    """
    simulation_movement_list = self._getSPLSimulationMovementList(sequence)
    for simulation_movement in simulation_movement_list:
      # we record the property so it doesn't get changed by expand with
      # the value from a higher simulation level
      simulation_movement.recordProperty('quantity')
      simulation_movement.edit(quantity=self.default_quantity-1)
      #simulation_movement.getDeliveryValue().edit(quantity=self.default_quantity-1)
      simulation_movement.expand()

  def stepModifySimulationLineStartDate(self,sequence=None, sequence_list=None, **kw):
    """
    Modify start_date on simulation lines related to SPL lines
    """
    simulation_movement_list = self._getSPLSimulationMovementList(sequence)
    for simulation_movement in simulation_movement_list:
      # we record the property so it doesn't get changed by expand with
      # the value from a higher simulation level
      simulation_movement.recordProperty('start_date')
      simulation_movement.edit(start_date=self.datetime+15)
      simulation_movement.expand()

  def stepModifyOneSimulationLineStartDate(self,sequence=None, sequence_list=None, **kw):
    """
      Modify start_date on only one simulation line related to SPL lines
    """
    simulation_movement_list = self._getSPLSimulationMovementList(sequence)
    self.assertEquals(len(simulation_movement_list),
                      len(sequence['resource_list']))
    simulation_movement_list[-1].recordProperty('start_date')
    simulation_movement_list[-1].edit(start_date=self.datetime+15)
    simulation_movement_list[-1].expand()

  def stepModifySimulationLineResource(self,sequence=None, sequence_list=None, **kw):
    """
      Modify the resource on simulation lines related to SPL lines
    """
    simulation_movement_list = self._getSPLSimulationMovementList(sequence)
    resource_list = sequence.get('resource_list')
    for simulation_movement in simulation_movement_list:
      simulation_movement.recordProperty('resource')
      simulation_movement.edit(resource_value=resource_list[-1])
      simulation_movement.expand()

  def stepModifyOneSimulationLineResource(self,sequence=None, sequence_list=None, **kw):
    """
      Modify the resource on only one simulation line related to SPL lines
    """
    simulation_movement_list = self._getSPLSimulationMovementList(sequence)
    resource_list = sequence.get('resource_list')
    simulation_movement_list[-1].recordProperty('resource')
    simulation_movement_list[-1].edit(resource_value=resource_list[-1])
    simulation_movement_list[-1].expand()

  def stepNewPackingListAdoptPrevisionQuantity(self,sequence=None, sequence_list=None, **kw):
    """
      Solve quantity divergence on new_packing_list with 'Adopt Solver'
    """
    packing_list = sequence.get('new_packing_list')
    self._solveDivergence(packing_list, 'quantity', 'Adopt Solver')

  def stepAcceptDecisionDestination(self,sequence=None, sequence_list=None, **kw):
    """
      Solve destination divergence on packing_list with 'Adopt Solver'
    """
    packing_list = sequence.get('packing_list')
    self._solveDivergence(packing_list, 'destination', 'Accept Solver')

  def stepUnifyStartDateWithDecision(self,sequence=None, sequence_list=None, **kw):
    """
      Solve start_date divergence on packing_list with the 'Unify Solver',
      using the start_date of the packing_list.
    """
    packing_list = sequence.get('packing_list')
    self._solveDivergence(packing_list, 'start_date', 'Unify Solver',
                          value=packing_list.getStartDate())

  def stepUnifyStartDateWithPrevision(self,sequence=None, sequence_list=None, **kw):
    """
      Solve start_date divergence on packing_list with the 'Unify Solver',
      using the start_date of one of the simulation movements.
    """
    packing_list = sequence.get('packing_list')
    simulation_movement_list = self._getSPLSimulationMovementList(sequence)
    self._solveDivergence(packing_list, 'start_date',
      'Unify Solver', value=simulation_movement_list[-1].getStartDate())

  def stepAcceptDecisionResource(self,sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    self._solveDivergence(packing_list, 'resource', 'Accept Solver')

  def stepAcceptDecisionQuantity(self,sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    self._solveDivergence(packing_list, 'quantity', 'Accept Solver')

  def stepAdoptPrevisionResource(self,sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    self._solveDivergence(packing_list, 'resource', 'Adopt Solver')

  def stepAdoptPrevisionQuantity(self,sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    self._solveDivergence(packing_list, 'quantity', 'Adopt Solver')

  def _solveDivergence(self, document, property, solver, **kw):
    """Solve divergence by using solver tool"""
    solver_process_tool = self.portal.portal_solver_processes
    solver_process = solver_process_tool.newSolverProcess(document)
    solver_decision, = [x for x in solver_process.contentValues()
      if x.getCausalityValue().getTestedProperty() == property]
    # use Quantity Accept Solver.
    solver_decision.setSolverValue(self.portal.portal_solvers[solver])
    # configure for Accept Solver.
    solver_decision.updateConfiguration(tested_property_list=[property], **kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def stepCheckPackingListLineWithNewQuantityPrevision(self,sequence=None, sequence_list=None, **kw):
    """
      Look if the packing list has new previsions
    """
    packing_list_line = sequence.get('packing_list_line')
    self.assertEquals(packing_list_line.getQuantity(),self.default_quantity-1)

  def stepCheckPackingListLineWithNewQuantityPrevisionForMergedLine(self,sequence=None, sequence_list=None, **kw):
    """
      Look if the packing list has new previsions
    """
    packing_list_line = sequence.get('packing_list_line')
    self.assertEquals(packing_list_line.getQuantity(),(self.default_quantity-1)*2)

  def stepCheckPackingListLineWithNewResource(self,sequence=None, sequence_list=None, **kw):
    """
      Look if the packing list has new resource
    """
    packing_list_line = sequence.get('packing_list_line')
    new_resource = sequence.get('resource')
    self.assertEquals(packing_list_line.getQuantity(), self.default_quantity*2)
    self.assertEquals(packing_list_line.getResourceValue(), new_resource)
    simulation_line_list = packing_list_line.getDeliveryRelatedValueList()
    order_line_list = sum([x.getParentValue().getParentValue().getDeliveryList()
                           for x in simulation_line_list], [])
    self.assertEquals(sorted(packing_list_line.getCausalityList()),
                      sorted(order_line_list))

  def stepCheckPackingListLineWithPreviousResource(self, sequence=None):
    packing_list_line = sequence.get('packing_list_line')
    old_resource = sequence['resource_list'][-2]
    self.assertEquals(packing_list_line.getResourceValue(), old_resource)

  def stepCheckPackingListLineWithSameResource(self,sequence=None, sequence_list=None, **kw):
    """
      Look if the packing list has new previsions
    """
    old_packing_list_line = sequence.get('packing_list_line')
    packing_list_line = old_packing_list_line.aq_parent[str(int(old_packing_list_line.getId())-1)]
    resource = sequence.get('resource')
    for line in sequence.get('packing_list').getMovementList():
      self.assertEquals(line.getResourceValue(), resource)
      self.assertEquals(line.getQuantity(), self.default_quantity)
      self.assertEquals(line.getCausalityList(),
                        [x.getParentValue().getParentValue().getDelivery()
                         for x in line.getDeliveryRelatedValueList()])

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
    simulation_movement_list = applied_rule.objectValues()
    resource_list = sequence.get('resource_list')
    self.assertEquals(len(simulation_movement_list),len(resource_list))
    delivery_value_list = []
    for simulation_movement in simulation_movement_list:
#      self.assertNotEquals(simulation_movement.getDeliveryValue(),None)
      delivery_value = simulation_movement.getDeliveryValue()
      if delivery_value not in delivery_value_list:
        delivery_value_list.append(delivery_value_list)
#      new_packing_list = delivery_value.getParent()
#      self.assertNotEquals(new_packing_list.getUid(),packing_list.getUid())
    self.assertEquals(len(delivery_value_list),len(resource_list))

  def stepCheckNewSplitPackingListAfterStartDateAdopt(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    applied_rule = sequence.get('applied_rule')
    packing_list = sequence.get('packing_list')
    packing_list_line = [x for x in packing_list.getMovementList()
                         if x.getQuantity()][0]
    new_packing_list = self.portal.sale_packing_list_module[str(int(packing_list.getId())-1)]
    new_packing_list_line = [x for x in new_packing_list.getMovementList()
                             if x.getQuantity()][0]
    self.assertEquals(packing_list_line.getQuantity(),self.default_quantity)
    self.assertEquals(packing_list.getStartDate(),self.datetime+10)
    self.assertEquals(new_packing_list_line.getQuantity(),self.default_quantity)
    self.assertEquals(new_packing_list.getStartDate(),self.datetime+15)
    simulation_movement_list = applied_rule.objectValues()
    resource_list = sequence.get('resource_list')
    self.assertEquals(len(simulation_movement_list),len(resource_list))
    delivery_value_list = []
    for simulation_movement in simulation_movement_list:
#      self.assertNotEquals(simulation_movement.getDeliveryValue(),None)
      delivery_value = simulation_movement.getDeliveryValue()
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
      Add a container line in the packing list
    """
    container = sequence.get('container')
    container_line = container.newContent(portal_type=self.container_line_portal_type)
    sequence.edit(container_line=container_line)
    resource = sequence.get('resource')
    container_line.edit(resource_value=resource)

  def stepSetContainerLineSmallQuantity(self,sequence=None, sequence_list=None, **kw):
    """
      Set a small quantity on the container line, it should not be enough for
      the packing list to be packed.
    """
    container_line = sequence.get('container_line')
    container_line.edit(quantity=self.default_quantity-1)

  def stepCheckContainerLineSmallQuantity(self, sequence=None,
      sequence_list=None, **kw):
    """
      Checks that quantity is set correctly on the container_line.
    """
    container_line = sequence.get('container_line')
    self.assertEquals(self.default_quantity - 1, container_line.getQuantity())
    self.assertEquals(self.default_quantity - 1,
                      container_line.getTotalQuantity())

  def stepSetContainerLineFullQuantity(self,sequence=None, sequence_list=None,
                                       quantity=None,**kw):
    """
      Set the full quantity
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
      container_line = \
          container.newContent(portal_type=self.container_line_portal_type)
      container_line.setResourceValue(resource)
      # without variation
      if not line.hasCellContent():
        quantity = line.getQuantity()
        container_line.edit(quantity=quantity)
        container_line.immediateReindexObject()
        self.assertEquals(quantity, container_line.getQuantity())
        self.assertEquals(quantity, container_line.getTotalQuantity())
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
          self.assertEquals(old_cell.getQuantity(), cell.getQuantity())
          self.assertEquals(old_cell.getTotalQuantity(), cell.getTotalQuantity())

        self.assertEquals(line.getQuantity(), container_line.getQuantity())
        self.assertEquals(line.getTotalQuantity(), container_line.getTotalQuantity())

    # quantity is 1 on the container itself
    self.assertEquals(1, container.getQuantity())
    self.assertEquals(1, container.getTotalQuantity())

  def stepCheckPackingListIsNotPacked(self,sequence=None, sequence_list=None, **kw):
    """
      Check that the number of objects in containers are
      not equals to the quantity of the packing list
    """
    packing_list = sequence.get('packing_list')
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
    self.commit()
    self.assertEquals(1,packing_list.isPacked())
    self.assertEquals('packed',packing_list.getContainerState())

  def stepCheckNewPackingListIsPacked(self,sequence=None, sequence_list=None, **kw):
    """
      Check that the number of objects in containers are
      equals to the quantity of the packing list
    """
    packing_list = sequence.get('new_packing_list')
    self.stepCheckPackingListIsPacked(sequence=sequence,
                                      packing_list=packing_list)

  def stepCreateCurrency(self, sequence, **kw) :
    """Create a default currency. """
    currency_module = self.getCurrencyModule()
    if currency_module._getOb('EUR', None) is None:
      currency = self.getCurrencyModule().newContent(
          portal_type='Currency',
          id="EUR",
          base_unit_quantity=0.01,
          )
    else:
      currency = currency_module._getOb('EUR')
    sequence.edit(currency=currency)

  def stepSetOrderPriceCurrency(self, sequence, **kw) :
    """Set the price currency of the order.

    This step is not necessary.
    TODO : - include a test without this step.
           - include a test with this step late.
    """
    currency = sequence.get('currency')
    order = sequence.get('order')
    order.setPriceCurrency(currency.getRelativeUrl())

  def _checkRecordedProperty(self, movement_list, property_id, assertion):
    for movement in movement_list:
      for simulation_movement in movement.getDeliveryRelatedValueList():
        if assertion:
          self.assertTrue(simulation_movement.isPropertyRecorded(property_id))
        else:
          self.assertFalse(simulation_movement.isPropertyRecorded(property_id))

  def stepCheckSimulationMovementHasRecordedQuantity(self, sequence=None,
                                                     sequence_list=None):
    movement_list = sequence.get('packing_list').objectValues(
      portal_type=self.packing_list_line_portal_type)
    self._checkRecordedProperty(movement_list, 'quantity', True)

  def stepCheckSimulationMovementHasNoRecordedQuantity(self, sequence=None,
                                                       sequence_list=None):
    movement_list = sequence.get('packing_list').objectValues(
      portal_type=self.packing_list_line_portal_type)
    self._checkRecordedProperty(movement_list, 'quantity', False)

  def stepCheckSimulationMovementHasRecordedResource(self, sequence=None,
                                                     sequence_list=None):
    movement_list = sequence.get('packing_list').objectValues(
      portal_type=self.packing_list_line_portal_type)
    self._checkRecordedProperty(movement_list, 'resource', True)

  def stepCheckSimulationMovementHasNoRecordedResource(self, sequence=None,
                                                       sequence_list=None):
    movement_list = sequence.get('packing_list').objectValues(
      portal_type=self.packing_list_line_portal_type)
    self._checkRecordedProperty(movement_list, 'resource', False)

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

    sequence_string = self.default_sequence + """
        DecreasePackingListLineQuantity
        CheckPackingListIsCalculating
        Tic
        CheckPackingListIsDiverged
        SplitAndDeferPackingList
        Tic
        CheckPackingListIsSolved
        CheckPackingListSplitted
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_02_PackingListChangeDestination(self, quiet=quiet, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()

    sequence_string = self.default_sequence + """
        ChangePackingListDestination
        CheckPackingListIsCalculating
        Tic
        CheckPackingListIsDiverged
        AcceptDecisionDestination
        Tic
        CheckPackingListIsSolved
        CheckPackingListIsNotDivergent
        CheckSimulationDestinationUpdated
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_03_PackingListChangeStartDate(self, quiet=quiet, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()

    sequence_string = self.default_sequence + """
        ChangePackingListStartDate
        CheckPackingListIsCalculating
        Tic
        CheckPackingListIsDiverged
        UnifyStartDateWithDecision
        Tic
        CheckPackingListIsSolved
        CheckPackingListIsNotDivergent
        CheckSimulationStartDateUpdated
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_04_PackingListDeleteLine(self, quiet=quiet, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()

    sequence_string = self.default_sequence + """
        CheckSimulationConnected
        DeletePackingListLine
        CheckPackingListIsNotDivergent
        Tic
        CheckSimulationDisconnected
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_05_SimulationChangeQuantity(self, quiet=quiet, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()

    sequence_string = self.default_sequence + """
        ModifySimulationLineQuantity
        Tic
        CheckPackingListIsDiverged
        AdoptPrevisionQuantity
        Tic
        CheckPackingListIsNotDivergent
        CheckPackingListIsSolved
        CheckPackingListLineWithNewQuantityPrevision
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_05a_SimulationChangeQuantityAndAcceptDecision(self, quiet=quiet, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()

    sequence_string = self.default_sequence + """
        ModifySimulationLineQuantity
        Tic
        CheckPackingListIsDiverged
        AcceptDecisionQuantity
        Tic
        CheckPackingListIsNotDivergent
        CheckPackingListIsSolved
        CheckSimulationQuantityUpdated
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_05b_SimulationChangeQuantityForMergedLine(self, quiet=quiet, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()

    sequence_string = self.default_sequence_with_duplicated_lines + """
        CheckTwoSimulationLines
        ModifySimulationLineQuantity
        Tic
        CheckPackingListIsDiverged
        AdoptPrevisionQuantity
        Tic
        CheckPackingListIsNotDivergent
        CheckPackingListIsSolved
        CheckPackingListLineWithNewQuantityPrevisionForMergedLine
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_05c_SimulationChangeQuantityAndAcceptDecisionForMergedLine(self, quiet=quiet, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()

    sequence_string = self.default_sequence_with_duplicated_lines + """
        CheckTwoSimulationLines
        ModifySimulationLineQuantity
        Tic
        CheckPackingListIsDiverged
        AcceptDecisionQuantity
        Tic
        CheckPackingListIsNotDivergent
        CheckPackingListIsSolved
        CheckSimulationQuantityUpdatedForMergedLine
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_05d_SimulationChangeResourceOnOneSimulationMovementForMergedLine(self, quiet=quiet, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()

    sequence_string = self.default_sequence_with_duplicated_lines + """
        CreateNotVariatedResource
        ModifyOneSimulationLineResource
        Tic
        CheckPackingListIsDiverged
        AdoptPrevisionResource
        Tic
        # Trying to Solve the divergence above with one simulation
        # movement changes the resource
        CheckPackingListLineWithNewResource
        # but doesn't solve the divergence as it is now divergent with the
        # other simulation movement
        CheckPackingListIsDiverged
        # solving again reverts the value.
        AdoptPrevisionResource
        Tic
        CheckPackingListLineWithPreviousResource
        # but now the packing list is divergent with the previous
        # simulation movement
        CheckPackingListIsDiverged
        # We have to chose one of them and accept the decision
        AcceptDecisionResource
        Tic
        CheckPackingListIsNotDivergent
        CheckPackingListIsSolved
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_05e_SimulationUnifyResourceOnSimulationMovementsForNonMergedLines(self, quiet=quiet, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()

    sequence_string = self.default_sequence_with_two_lines + """
        ModifySimulationLineResource
        Tic
        CheckPackingListIsDiverged
        AdoptPrevisionResource
        Tic
        CheckPackingListIsNotDivergent
        CheckPackingListIsSolved
        CheckPackingListLineWithSameResource
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_05f_SimulationChangeAndPartialAcceptDecision(self, quiet=quiet, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()

    sequence_string = self.default_sequence_with_duplicated_lines + """
        CreateNotVariatedResource
        CheckTwoSimulationLines
        ModifySimulationLineQuantity
        ModifyOneSimulationLineResource
        ModifySimulationLineStartDate
        Tic
        CheckPackingListIsDiverged
        AcceptDecisionQuantity
        Tic
        CheckPackingListIsDiverged
        AcceptDecisionResource
        Tic
        CheckPackingListIsDiverged
        UnifyStartDateWithDecision
        Tic
        CheckPackingListIsNotDivergent
        CheckPackingListIsSolved
        CheckSimulationQuantityUpdatedForMergedLine
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  # The 3 following tests currently fail because they are making assertions on
  # an applied rule which with the new simulation structure is not the same as
  # in the original test packing list.

  def test_06_SimulationChangeStartDate(self, quiet=quiet, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()

    sequence_string = self.default_sequence + """
        ModifySimulationLineStartDate
        Tic
        CheckPackingListIsDiverged
        UnifyStartDateWithPrevision
        Tic
        CheckPackingListIsSolved
        CheckNewPackingListAfterStartDateAdopt
        """
    # XXX Check if there is a new packing list created
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_07_SimulationChangeStartDateWithTwoOrderLine(self, quiet=quiet, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()

    sequence_string = self.default_sequence_with_two_lines + """
        ModifySimulationLineStartDate
        Tic
        CheckPackingListIsDiverged
        CheckPackingListIsDivergent
        UnifyStartDateWithPrevision
        Tic
        CheckPackingListIsNotDivergent
        CheckPackingListIsSolved
        CheckNewPackingListAfterStartDateAdopt
        """
    # XXX Check if there is a new packing list created
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_07a_SimulationChangeStartDateWithTwoOrderLine(self, quiet=quiet, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()

    sequence_string = self.default_sequence_with_two_lines + """
        ModifyOneSimulationLineStartDate
        Tic
        CheckPackingListIsDiverged
        CheckPackingListIsDivergent
        UnifyStartDateWithPrevision
        Tic
        CheckPackingListIsNotDivergent
        CheckPackingListIsSolved
        CheckNewPackingListAfterStartDateAdopt
        """
    # XXX Check if there is a new packing list created
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_08_AddContainers(self, quiet=quiet, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()

    sequence_string = self.default_sequence + """
        AddPackingListContainer
        AddPackingListContainerLine
        SetContainerLineSmallQuantity
        CheckContainerLineSmallQuantity
        CheckPackingListIsNotPacked
        SetContainerFullQuantity
        Tic
        CheckPackingListIsPacked
        """
    # XXX Check if there is a new packing list created
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_09_AddContainersWithVariatedResources(self, quiet=quiet, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()

    # Test with a order with cells
    sequence_string = self.variated_default_sequence + """
        AddPackingListContainer
        AddPackingListContainerLine
        SetContainerLineSmallQuantity
        CheckContainerLineSmallQuantity
        CheckPackingListIsNotPacked
        SetContainerFullQuantity
        Tic
        CheckPackingListIsPacked
        ModifySimulationLineStartDate
        Tic
        CheckPackingListIsDiverged
        CheckPackingListIsDivergent
        UnifyStartDateWithPrevision
        Tic
        """
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

    sequence_string = self.default_sequence + """
        IncreasePackingListLineQuantity
        CheckPackingListIsCalculating
        Tic
        CheckPackingListIsDiverged
        SplitAndDeferPackingList
        Tic
        CheckPackingListIsDiverged
        CheckPackingListIsDivergent
        CheckPackingListNotSolved
        """
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

    sequence_string = self.default_sequence + """
        DecreasePackingListLineQuantity
        CheckPackingListIsCalculating
        Tic
        CheckPackingListIsDiverged
        SplitAndDeferPackingList
        Tic
        CheckPackingListIsSolved
        CheckPackingListSplitted
        DecreasePackingListLineQuantity
        CheckPackingListIsCalculating
        Tic
        CheckPackingListIsDiverged
        SplitAndDeferPackingList
        Tic
        CheckNewPackingListIsDivergent
        NewPackingListAdoptPrevisionQuantity
        Tic
        CheckPackingListIsSolved
        CheckNewPackingListIsSolved
        CheckPackingListSplittedTwoTimes
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_SplitAndDeferDoNothing(self, quiet=quiet, run=run_all_test):
    """
    Use split & defer to solve a divergence, but choose do nothing for all
    lines.
    """
    if not run: return
    sequence_list = SequenceList()

    sequence_string = self.default_sequence + """
        IncreasePackingListLineQuantity
        CheckPackingListIsCalculating
        Tic
        CheckPackingListIsDiverged
        SplitAndDeferDoNothingPackingList
        Tic
        CheckPackingListIsDiverged
        CheckPackingListIsDivergent
        CheckPackingListNotSolved
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)


  def test_12_PackingListLineChangeResource(self, quiet=quiet, run=run_all_test):
    """
    Test if delivery diverged when we change the resource.
    """
    if not run: return
    sequence_list = SequenceList()

    sequence_string = self.default_sequence + """
        CreateNotVariatedResource
        ChangePackingListLineResource
        CheckPackingListIsCalculating
        Tic
        CheckPackingListIsDivergent
        """
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

  def test_PackingList_viewAsODT(self):
    # tests packing list printout
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',)
    client = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Client')
    vendor = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Vendor')
    packing_list = self.portal.getDefaultModule(self.packing_list_portal_type).newContent(
                              portal_type=self.packing_list_portal_type,
                              title='Packing List',
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client)
    line = packing_list.newContent(
                            portal_type=self.packing_list_line_portal_type,
                            resource_value=resource,
                            quantity=10,
                            price=3)
    packing_list.confirm()
    self.tic()

    odt = packing_list.PackingList_viewAsODT()
    from Products.ERP5OOo.tests.utils import Validator
    odf_validator = Validator()
    err_list = odf_validator.validate(odt)
    if err_list:
      self.fail(''.join(err_list))

  def test_15_CheckBuilderCanBeCalledTwiceSafely(self):
    """
    Builder design should allows to call the build method as many times as we 
    want. Make sure that we will not have duplicated packing list if build is 
    called several times.
    """
    delivery_builder = getattr(self.getPortalObject().portal_deliveries,
                               self.delivery_builder_id)
 
    def doNothing(self, *args, **kw):
      pass
    original_delivery_builder_build =  delivery_builder.__class__.build

    try:
      # We patch the delivery builder to make sure that it will not be
      # called by activities
      delivery_builder.__class__.build = doNothing
      sequence_list = SequenceList()

      sequence_string = self.confirmed_order_without_packing_list
      sequence_list.addSequenceString(sequence_string)
      sequence_list.play(self)

      # Now restore the build method and make sure first call returns document
      delivery_builder.__class__.build = original_delivery_builder_build
      self.assertTrue(len(delivery_builder.build()) > 0)
      # The second call should returns empty result even if tic not called
      self.assertTrue(len(delivery_builder.build()) ==  0)
    finally:
      delivery_builder.build = original_delivery_builder_build

  def test_16_simulation_reindexation_on_cancel(self):
    self.organisation_portal_type = 'Organisation'
    self.resource_portal_type = 'Product'

    packing_list_module = self.portal.getDefaultModule(
        portal_type=self.packing_list_portal_type)
    organisation_module = self.portal.getDefaultModule(
        portal_type=self.organisation_portal_type)
    resource_module = self.portal.getDefaultModule(
        portal_type=self.resource_portal_type)
    source = organisation_module.newContent(
        portal_type=self.organisation_portal_type)
    destination = organisation_module.newContent(
        portal_type=self.organisation_portal_type)
    resource = resource_module.newContent(
        portal_type=self.resource_portal_type)

    packing_list = packing_list_module.newContent(
        portal_type=self.packing_list_portal_type,
        source_value=source,
        destination_value=destination,
        specialise=self.business_process,
        start_date=DateTime())
    packing_list_line = packing_list.newContent(
        portal_type=self.packing_list_line_portal_type,
        resource_value=resource,
        quantity=1)
    packing_list.confirm()
    self.tic()
    self.assertEqual('confirmed', packing_list.getSimulationState())
    simulation_movement = packing_list_line.getDeliveryRelatedValue(
        portal_type='Simulation Movement')
    self.assertEqual('confirmed', simulation_movement.getSimulationState())
    packing_list.cancel()
    self.tic()
    self.assertEqual('cancelled', packing_list.getSimulationState())
    self.assertEqual('cancelled', simulation_movement.getSimulationState())

  def stepCreateSourceAccount(self, sequence=None, **kw):
    organisation = self.stepCreateOrganisation(sequence, None, 'dummy_source')
    sequence.edit(source_account = sequence.get('dummy_source')['bank'])

  def stepCreateDestinationAccount(self, sequence=None, **kw):
    organisation = self.stepCreateOrganisation(sequence, None,
        'dummy_destination')
    sequence.edit(destination_account = sequence.get('dummy_destination')
        ['bank'])

  def stepSetOrderLineSourceAccount(self, sequence=None, **kw):
    order_line = sequence.get('order_line')
    account = sequence.get('source_account')
    self.assertNotEqual(None, account)
    order_line.setSourceAccountValue(account)

  def stepSetOrderLineDestinationAccount(self, sequence=None, **kw):
    order_line = sequence.get('order_line')
    account = sequence.get('destination_account')
    self.assertNotEqual(None, account)
    order_line.setDestinationAccountValue(account)

  def stepCheckPackingListLineSourceAccount(self, sequence=None, **kw):
    packing_list = sequence.get('packing_list')
    account = sequence.get('source_account')
    for line in packing_list.getMovementList():
      self.assertEqual(line.getSourceAccountValue(), account)

  def stepCheckPackingListLineDestinationAccount(self, sequence=None, **kw):
    packing_list = sequence.get('packing_list')
    account = sequence.get('destination_account')
    for line in packing_list.getMovementList():
      self.assertEqual(line.getDestinationAccountValue(), account)

  def test_17_PackingListOrderLineWithAccount(self, quiet=quiet):
    """
      Check how packing list behaves if comes from order line which has
      source/destination account set.
    """
    sequence_list = SequenceList()

    sequence_string = self.default_order_sequence + """
        CreateNotVariatedResource
        CreateSourceAccount
        CreateDestinationAccount
        Tic
        CreateOrderLine
        SetOrderLineResource
        SetOrderLineDefaultValues
        SetOrderLineSourceAccount
        SetOrderLineDestinationAccount
        OrderOrder
        Tic
        ConfirmOrder
        Tic
        PackingListBuilderAlarm
        Tic
        CheckOrderSimulation
        CheckDeliveryBuilding
        CheckPackingListIsSolved
        CheckOrderPackingList
        CheckPackingListLineSourceAccount
        CheckPackingListLineDestinationAccount
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_18_ChangeQuantityOnPackingListAndOrder(self, quiet=quiet):
    """
      Change the quantity on a packing list line, and accept the
      divergence, then change the quantity on an order line to the same
      value and check if it does not cause divergence on a packing list
      line and recorded properties are reset after re-expand.
    """
    sequence_list = SequenceList()

    sequence_string = self.default_sequence + """
        DecreasePackingListLineQuantity
        Tic
        CheckPackingListIsDiverged
        AcceptDecisionQuantity
        Tic
        CheckPackingListIsSolved
        CheckSimulationMovementHasRecordedQuantity
        DecreaseOrderLineQuantity
        Tic
        CheckPackingListIsSolved
        CheckSimulationMovementHasNoRecordedQuantity
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_19_ChangeResourceOnPackingListAndOrder(self, quiet=quiet):
    """
      Change the resource on a packing list line, and accept the
      divergence, then change the resource on an order line to the same
      value and check if it does not cause divergence on a packing list
      line and recorded properties are reset after re-expand.
    """
    sequence_list = SequenceList()

    sequence_string = self.default_sequence + """
        CreateNotVariatedResource
        ChangePackingListLineResource
        Tic
        CheckPackingListIsDiverged
        AcceptDecisionResource
        Tic
        CheckPackingListIsSolved
        CheckSimulationMovementHasRecordedResource
        ChangeOrderLineResource
        Tic
        CheckPackingListIsSolved
        CheckSimulationMovementHasNoRecordedResource
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_subcontent_reindexing_packing_list_line_cell(self):
    """Tests, that indexation of Packing List are propagated to subobjects
    during reindxation"""
    packing_list = self.portal.getDefaultModule(
        self.packing_list_portal_type).newContent(
            portal_type=self.packing_list_portal_type)
    packing_list_line = packing_list.newContent(
        portal_type=self.packing_list_line_portal_type)
    packing_list_cell = packing_list_line.newContent(
        portal_type=self.packing_list_cell_portal_type)
    self._testSubContentReindexing(packing_list, [packing_list_line,
      packing_list_cell])

  def test_subcontent_reindexing_packing_list_container_line_cell(self):
    """Tests, that indexation of Packing List are propagated to subobjects
    during reindxation, for Container, Container Line and Container Cell"""
    packing_list = self.portal.getDefaultModule(
        self.packing_list_portal_type).newContent(
            portal_type=self.packing_list_portal_type)
    container = packing_list.newContent(
        portal_type=self.container_portal_type)
    container_line = container.newContent(
        portal_type=self.container_line_portal_type)
    container_cell = container_line.newContent(
        portal_type=self.container_cell_portal_type)
    self._testSubContentReindexing(packing_list, [container, container_line,
      container_cell])

  def test_PackingList_getMovementListSorting(self):
    '''Test that is possible to sort getMovementList result passing it sort_on
    parameter
    '''
    packing_list = self.portal.getDefaultModule(self.packing_list_portal_type).newContent(
                              portal_type=self.packing_list_portal_type,
                              title='Packing List')
    # create some packing list lines
    line_bbb = packing_list.newContent(
                            portal_type=self.packing_list_line_portal_type,
                            reference='bbb',
                            int_index=1)
    line_bbb_cell_bbb = line_bbb.newContent(
                            portal_type=self.packing_list_cell_portal_type,
                            reference='bbb',
                            int_index=2)
    line_bbb_cell_aaa = line_bbb.newContent(
                            portal_type=self.packing_list_cell_portal_type,
                            reference='aaa',
                            int_index=1)
    line_aaa = packing_list.newContent(
                            portal_type=self.packing_list_line_portal_type,
                            reference='aaa',
                            int_index=2)
    line_ccc = packing_list.newContent(
                            portal_type=self.packing_list_line_portal_type,
                            reference='ccc',
                            int_index=4)
    line_ddd = packing_list.newContent(
                            portal_type=self.packing_list_line_portal_type,
                            reference='ddd',
                            int_index=3)
    self.tic()
    # check it's possible to sort by reference
    reference_result = packing_list.getMovementList(sort_on=
        [('reference', 'descending')])
    self.assertEquals(reference_result, [line_ddd, line_ccc,
      line_bbb_cell_bbb, line_bbb_cell_aaa, line_aaa])

    # check it's possible to sort by int_index
    int_index_result = packing_list.getMovementList(sort_on=
        [('int_index', 'ascending')])
    self.assertEquals(int_index_result, [line_bbb_cell_aaa, line_bbb_cell_bbb,
      line_aaa, line_ddd, line_ccc])

  def test_subcontent_reindexing_container_line_cell(self):
    """Tests, that indexation of Packing List are propagated to subobjects
    during reindxation, for Container, Container Line and Container Cell"""
    packing_list = self.portal.getDefaultModule(
        self.packing_list_portal_type).newContent(
            portal_type=self.packing_list_portal_type)
    container = packing_list.newContent(
        portal_type=self.container_portal_type)
    container_line = container.newContent(
        portal_type=self.container_line_portal_type)
    container_cell = container_line.newContent(
        portal_type=self.container_cell_portal_type)
    self._testSubContentReindexing(container, [container_line,
      container_cell])

  def stepSetAssignmentOrderProfile(self,sequence=None, sequence_list=None, **kw):
    """
      Configure an Assingnment Order.
      This order represents that it transfers an ownership to somebody.
      In this case, source and destination are not moving.
    """
    organisation1 = sequence.get('organisation1')
    organisation2 = sequence.get('organisation2')
    project1 = sequence.get('project1')
    project2 = sequence.get('project2')
    order = sequence.get('order')
    order.edit(source_value = organisation1,
               source_section_value = organisation1,
               source_payment_value = organisation1['bank'],
               destination_value = organisation1,  # set same organisation
               destination_section_value = organisation2,
               destination_payment_value = organisation2['bank'],
               source_project_value = project1,
               destination_project_value = project2 )
    order.setPaymentConditionEfficiency(1.0)
    self.failUnless('Site Error' not in order.view())


  def testTransferOfOwnership(self, quiet=quiet):
    """
     Test that Packing List has a capability to represent transfer of an
     ownership(rights).
    """
    sequence_list = SequenceList()
    assignment_order_sequence = """
        CreateOrganisation1
        CreateOrganisation2
        CreateOrganisation3
        CreateProject1
        CreateProject2
        CreateOrder
        CreateCurrency
        SetOrderPriceCurrency
        SetAssignmentOrderProfile
    """
    sequence_string = assignment_order_sequence + """
        CreateNotVariatedResource
        Tic
        CreateOrderLine
        SetOrderLineResource
        SetOrderLineDefaultValues
        OrderOrder
        Tic
        ConfirmOrder
        Tic
        PackingListBuilderAlarm
        Tic
        CheckOrderSimulation
        CheckDeliveryBuilding
        CheckPackingListIsNotDivergent
        CheckOrderPackingList
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

class TestSolvingPackingList(TestPackingListMixin, ERP5TypeTestCase):
  quiet = 0

  def afterSetUp(self, quiet=1, run=1):
    TestPackingListMixin.afterSetUp(self)
    solver_process_type_info = self.portal.portal_types['Solver Process']
    self.original_allowed_content_types = \
      solver_process_type_info.getTypeAllowedContentTypeList()
    self.added_target_solver_list = []

  def beforeTearDown(self, quiet=1, run=1):
    super(TestSolvingPackingList, self).beforeTearDown()
    self.portal.portal_rules.new_delivery_simulation_rule.quantity_tester.edit(
      solver=())
    self.portal.portal_types['Solver Process'].setTypeAllowedContentTypeList(
      self.original_allowed_content_types)
    self.portal.portal_solvers.manage_delObjects(self.added_target_solver_list)
    self.tic()

  @UnrestrictedMethod
  def _setUpTargetSolver(self, solver_id, solver_class, tested_property_list):
    solver_tool = self.portal.portal_solvers
    solver = solver_tool.newContent(
      portal_type='Solver Type',
      id=solver_id,
      tested_property_list=tested_property_list,
      automatic_solver=1,
      type_class=solver_class,
      type_group_list=('target_solver',),
    )
    solver.setCriterion(property='portal_type',
                        identity=['Simulation Movement',])
    solver.setCriterionProperty('portal_type')
    solver_process_type_info = self.portal.portal_types['Solver Process']
    solver_process_type_info.setTypeAllowedContentTypeList(
      solver_process_type_info.getTypeAllowedContentTypeList() +
      [solver_id]
    )
    (default_chain, chain_dict) = getChainByType(self.portal)
    chain_dict['chain_%s' % solver_id] = 'solver_workflow'
    self.portal.portal_workflow.manage_changeWorkflows(default_chain,
                                                       props=chain_dict)
    self.portal.portal_caches.clearAllCache()
    self.added_target_solver_list.append(solver_id)

  def stepSetUpAutomaticQuantityAcceptSolver(self, sequence=None, sequence_list=None):
    self._setUpTargetSolver('Automatic Quantity Accept Solver',
                            'AcceptSolver', ('quantity',))
    self.portal.portal_rules.new_delivery_simulation_rule.quantity_tester.edit(
      solver=('portal_solvers/Automatic Quantity Accept Solver',))

  def stepSetUpAutomaticQuantityAdoptSolver(self, sequence=None, sequence_list=None):
    self._setUpTargetSolver('Automatic Quantity Adopt Solver',
                            'AdoptSolver', ('quantity',))
    self.portal.portal_rules.new_delivery_simulation_rule.quantity_tester.edit(
      solver=('portal_solvers/Automatic Quantity Adopt Solver',))

  def stepSetUpMovementSplitSolver(self, sequence=None, sequence_list=None):
    self._setUpTargetSolver('Movement Split Solver',
                            'MovementSplitSolver', ())

  def stepSplitMovementWithVariatedResources(self, sequence=None,
                                             sequence_list=None):
    packing_list = sequence.get('packing_list')
    simulation_movement_list = sum(
      [x.getDeliveryRelatedValueList() for x in
       packing_list.getMovementList()[:10]], [])
    solver_process = self.portal.portal_solver_processes.newContent(
      portal_type='Solver Process')
    target_solver = solver_process.newContent(
      portal_type='Movement Split Solver',
      delivery_value_list=simulation_movement_list)
    target_solver.solve()

  def stepCheckSplitMovementWithVariatedResources(self, sequence=None,
                                                  sequence_list=None):
    packing_list = sequence.get('packing_list')
    order = packing_list.getCausalityValue()
    new_packing_list = filter(lambda x:x != packing_list,
                              order.getCausalityRelatedValueList(
      portal_type=packing_list.getPortalType()))[0]
    self.assertEquals(len(packing_list.getMovementList()),
                      len(order.getMovementList()) - 10)
    self.assertEquals(len(new_packing_list.getMovementList()), 10)

  def test_01_PackingListDecreaseQuantity(self, quiet=quiet):
    """
      Change the quantity on an delivery line, then
      see if the packing list is solved automatically
      with accept solver.
    """
    sequence_list = SequenceList()

    sequence_string = """
        SetUpAutomaticQuantityAcceptSolver
        """ + self.default_sequence + """
        DecreasePackingListLineQuantity
        CheckPackingListIsCalculating
        Tic
        CheckPackingListIsSolved
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_02_PackingListDecreaseQuantity(self, quiet=quiet):
    """
      Change the quantity on an delivery line, then
      see if the packing list is solved automatically
      with adopt solver.
    """
    sequence_list = SequenceList()

    sequence_string = """
        SetUpAutomaticQuantityAdoptSolver
        """ + self.default_sequence + """
        DecreasePackingListLineQuantity
        CheckPackingListIsCalculating
        Tic
        CheckPackingListIsSolved
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_09_AddContainersWithVariatedResources(self, quiet=quiet):
    sequence_list = SequenceList()

    # Test with a order with cells
    sequence_string = """
        SetUpMovementSplitSolver
        """ + self.variated_default_sequence + """
        AddPackingListContainer
        AddPackingListContainerLine
        SetContainerLineSmallQuantity
        CheckContainerLineSmallQuantity
        CheckPackingListIsNotPacked
        SetContainerFullQuantity
        Tic
        CheckPackingListIsPacked
        SplitMovementWithVariatedResources
        Tic
        CheckSplitMovementWithVariatedResources
        """
    # XXX Check if there is a new packing list created
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

class TestPurchasePackingListMixin(TestPackingListMixin):
  """Mixing class with steps to test purchase packing lists.
  """
  order_portal_type = 'Purchase Order'
  order_line_portal_type = 'Purchase Order Line'
  order_cell_portal_type = 'Purchase Order Cell'
  packing_list_portal_type = 'Purchase Packing List'
  packing_list_line_portal_type = 'Purchase Packing List Line'
  packing_list_cell_portal_type = 'Purchase Packing List Cell'
  delivery_builder_id = 'purchase_packing_list_builder'
  container_portal_type = None
  container_line_portal_type = None
  container_cell_portal_type = None

  # all steps related to packing and container does not apply on purchase
  def ignored_step(self, **kw):
    return
  stepAddPackingListContainer = ignored_step
  stepDefineNewPackingListContainer = ignored_step
  stepAddPackingListContainerLine = ignored_step
  stepSetContainerLineSmallQuantity = ignored_step
  stepCheckContainerLineSmallQuantity = ignored_step
  stepSetContainerLineFullQuantity = ignored_step
  stepSetContainerFullQuantity = ignored_step
  stepCheckPackingListIsNotPacked = ignored_step
  stepCheckPackingListIsPacked = ignored_step
  stepCheckNewPackingListIsPacked = ignored_step

  def test_subcontent_reindexing_packing_list_container_line_cell(self):
    """No need to check Containers in Purchase Packing List"""
    pass

  def test_subcontent_reindexing_container_line_cell(self):
    """No need to check Containers in Purchase Packing List"""
    pass

class TestPurchasePackingList(TestPurchasePackingListMixin, TestPackingList):
  """Tests for purchase packing list.
  """


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPackingList))
  suite.addTest(unittest.makeSuite(TestSolvingPackingList))
  suite.addTest(unittest.makeSuite(TestPurchasePackingList))
  return suite
