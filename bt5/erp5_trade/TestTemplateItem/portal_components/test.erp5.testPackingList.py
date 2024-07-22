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

from collections import deque
import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList, Sequence
from erp5.component.test.testOrder import TestOrderMixin
from DateTime import DateTime

def getTree(self):
  tree = []
  object_list = deque((self,))
  while object_list:
    self = object_list.popleft()
    tree.append(self)
    object_list += self.objectValues()
  return tree

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
    self.assertEqual(packing_list.getCausalityValue(), order)
    self.assertEqual(packing_list.getSource(), order.getSource())
    self.assertEqual(packing_list.getDestination(), order.getDestination())
    self.assertEqual(packing_list.getDestinationSection(),
                                       order.getDestinationSection())
    self.assertEqual(packing_list.getSourceSection(),
                                       order.getSourceSection())
    self.assertEqual(packing_list.getSourceDecision(),
                                       order.getSourceDecision())
    self.assertEqual(packing_list.getDestinationAdministration(),
                                       order.getDestinationAdministration())
    self.assertEqual(packing_list.getSourceAdministration(),
                                       order.getSourceAdministration())
    self.assertEqual(packing_list.getPriceCurrency(),
                                       order.getPriceCurrency())
    self.assertEqual(packing_list.getDestinationProject(),
                                       order.getDestinationProject())
    self.assertEqual(packing_list.getSourceProject(),
                                       order.getSourceProject())

  def stepCheckPackingListIsDivergent(self, sequence=None, sequence_list=None,
                                      packing_list=None,**kw):
    """
      Test if packing list is divergent
    """
    if packing_list is None:
      packing_list = sequence.get('packing_list')
    self.assertNotIn('Site Error', packing_list.view())
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
    self.assertEqual('calculating',packing_list.getCausalityState())

  def stepCheckPackingListIsSolved(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is solved
    """
    packing_list = sequence.get('packing_list')
    self.assertEqual('solved',packing_list.getCausalityState())

  def stepCheckNewPackingListIsSolved(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('new_packing_list')
    self.assertEqual('solved', packing_list.getCausalityState())

  def stepCheckPackingListIsDiverged(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is divergent
    """
    packing_list = sequence.get('packing_list')
    self.assertEqual('diverged', packing_list.getCausalityState())

  def stepCheckPackingListIsNotDivergent(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is not divergent
    """
    packing_list = sequence.get('packing_list')
    self.assertFalse(packing_list.isDivergent())

  @UnrestrictedMethod
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

  @UnrestrictedMethod
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
    solver_process = packing_list.Delivery_getSolverProcess()
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
    self.callPackingListBuilderList(packing_list)

  def stepSplitAndDeferDoNothingPackingList(self, sequence=None, sequence_list=None, **kw):
    """
      Do the solve divrgence action, but choose "do nothing" for divergences
    """
    packing_list = sequence.get('packing_list')
    solver_process = self.portal.portal_solver_processes.newSolverProcess(packing_list)
    quantity_solver_decision, = [x for x in solver_process.contentValues()
      if x.getCausalityValue().getTestedProperty() == 'quantity']
    # use no solver
    quantity_solver_decision.setSolverValue(None)
    # and no configure
    quantity_solver_decision.updateConfiguration()
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def stepCheckPackingListSplitted(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list was splitted
    """
    packing_list1, packing_list2 = self.getTwoRelatedPackingList(sequence)
    packing_list1_line, = packing_list1.objectValues(portal_type=self.packing_list_line_portal_type)
    self.assertEqual(self.default_quantity-1,packing_list1_line.getQuantity())
    packing_list2_line, = packing_list2.objectValues(portal_type=self.packing_list_line_portal_type)
    self.assertEqual(1,packing_list2_line.getQuantity())

  def stepCheckPackingListSplittedTwoTimes(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is divergent
    """
    packing_list1, packing_list2 = self.getTwoRelatedPackingList(sequence)
    packing_list1_line, = packing_list1.objectValues(portal_type=self.packing_list_line_portal_type)
    self.assertEqual(self.default_quantity-2,packing_list1_line.getQuantity())
    packing_list2_line, = packing_list2.objectValues(portal_type=self.packing_list_line_portal_type)
    self.assertEqual(2,packing_list2_line.getQuantity())

  def stepCheckPackingListNotSplitted(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is divergent
    """
    order = sequence.get('order')
    packing_list_list = order.getCausalityRelatedValueList(
                               portal_type=self.packing_list_portal_type)
    self.assertEqual(1,len(packing_list_list))
    packing_list1 = sequence.get('packing_list')
    last_delta = sequence.get('last_delta', 0.0)
    for line in packing_list1.objectValues(
          portal_type= self.packing_list_line_portal_type):
      self.assertEqual(self.default_quantity + last_delta,
          line.getQuantity())
      simulation_list = line.getDeliveryRelatedValueList(
                            portal_type='Simulation Movement')
      self.assertEqual(len(simulation_list),1)
      simulation_movement = simulation_list[0]
      self.assertEqual(self.default_quantity + last_delta,
          simulation_movement.getCorrectedQuantity())

  def stepCheckPackingListNotSolved(self, sequence=None, sequence_list=None, **kw):
    """
      This step is specific to test_10 : the incorrectly used solver didn't
      solve anything.
    """
    order = sequence.get('order')
    packing_list_list = order.getCausalityRelatedValueList(
                               portal_type=self.packing_list_portal_type)
    self.assertEqual(1,len(packing_list_list))
    packing_list1 = sequence.get('packing_list')
    last_delta = sequence.get('last_delta', 0.0)
    for line in packing_list1.objectValues(
          portal_type= self.packing_list_line_portal_type):
      self.assertEqual(self.default_quantity + last_delta,
          line.getQuantity())
      simulation_list = line.getDeliveryRelatedValueList(
                            portal_type='Simulation Movement')
      self.assertEqual(len(simulation_list),1)
      simulation_movement = simulation_list[0]

      # Here we don't add last_delta, as the solver didn't do its work.
      self.assertEqual(self.default_quantity,
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
    self.assertEqual(len(simulation_movement_list),1)
    org3 = sequence.get('organisation3')
    for simulation_movement in simulation_movement_list:
      simulation_movement = simulation_movement.objectValues()[0].objectValues()[0]
      self.assertEqual(simulation_movement.getDestinationValue(),org3)

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
    self.assertEqual(len(simulation_movement_list),1)
    delivery_applied_rule = simulation_movement_list[0].objectValues()[0]
    simulation_movement_list = delivery_applied_rule.objectValues()
    self.assertEqual(len(simulation_movement_list),1)
    for simulation_movement in simulation_movement_list:
      self.assertEqual(simulation_movement.getStartDate(),self.datetime + 15)

  def stepCheckSimulationQuantityUpdated(self,sequence=None, sequence_list=None, **kw):
    """
      Test if the quantity of the simulation movement was changed
    """
    applied_rule = sequence.get('applied_rule')
    simulation_movement_list = applied_rule.objectValues()
    self.assertEqual(len(simulation_movement_list),1)
    for simulation_movement in simulation_movement_list:
      simulation_movement = simulation_movement.objectValues()[0].objectValues()[0]
      self.assertEqual(simulation_movement.getQuantity() +
                        simulation_movement.getDeliveryError(),
                        self.default_quantity)

  def stepCheckSimulationQuantityUpdatedForMergedLine(self,sequence=None, sequence_list=None, **kw):
    """
      Test if the quantity of the simulation movement was changed
    """
    applied_rule = sequence.get('applied_rule')
    simulation_movement_list = applied_rule.objectValues()
    self.assertEqual(len(simulation_movement_list),2)
    for simulation_movement in simulation_movement_list:
      simulation_movement = simulation_movement.objectValues()[0].objectValues()[0]
      self.assertEqual(simulation_movement.getQuantity() +
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
    self.assertEqual(len(simulation_movement_list),1)
    order_line = sequence.get('order_line')
    packing_list_line = sequence.get('packing_list_line')
    for simulation_movement in simulation_movement_list:
      self.assertEqual(simulation_movement.getDeliveryValue(), order_line)
      self.assertEqual(packing_list_line.getCausalityValue(),
                        order_line)
      rule_list = simulation_movement.objectValues()
      self.assertTrue(len(rule_list), 1)
      delivering_rule = rule_list[0]
      self.assertTrue(delivering_rule.getSpecialiseValue().getPortalType(),
                      'Delivering Rule')
      child_simulation_movement_list = delivering_rule.objectValues()
      self.assertTrue(len(child_simulation_movement_list), 1)
      child_simulation_movement = child_simulation_movement_list[0]
      self.assertEqual(child_simulation_movement.getDeliveryValue(),
                        packing_list_line)

  def stepCheckSimulationDisconnected(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    applied_rule = sequence.get('applied_rule')
    simulation_movement_list = applied_rule.objectValues()
    self.assertEqual(len(simulation_movement_list),1)
    for simulation_movement in simulation_movement_list:
      child_simulation_movement = simulation_movement.objectValues()[0].objectValues()[0]
      self.assertEqual(child_simulation_movement.getDeliveryValue(),None)

  def stepCheckTwoSimulationLines(self, sequence):
    """
    Check there are exactly two simulation lines related to the packing list
    line(s)
    """
    simulation_movement_list = self._getSPLSimulationMovementList(sequence)
    self.assertEqual(len(simulation_movement_list),2)

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
    self.assertEqual(len(simulation_movement_list),
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

  def _solveDivergence(self, document, property_, solver, **kw):
    """Solve divergence by using solver tool"""
    solver_process_tool = self.portal.portal_solver_processes
    solver_process = solver_process_tool.newSolverProcess(document)
    solver_decision, = [x for x in solver_process.contentValues()
      if x.getCausalityValue().getTestedProperty() == property_]
    # use Quantity Accept Solver.
    solver_decision.setSolverValue(self.portal.portal_solvers[solver])
    # configure for Accept Solver.
    solver_decision.updateConfiguration(tested_property_list=[property_], **kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def stepCheckPackingListLineWithNewQuantityPrevision(self,sequence=None, sequence_list=None, **kw):
    """
      Look if the packing list has new previsions
    """
    packing_list_line = sequence.get('packing_list_line')
    self.assertEqual(packing_list_line.getQuantity(),self.default_quantity-1)

  def stepCheckPackingListLineWithNewQuantityPrevisionForMergedLine(self,sequence=None, sequence_list=None, **kw):
    """
      Look if the packing list has new previsions
    """
    packing_list_line = sequence.get('packing_list_line')
    self.assertEqual(packing_list_line.getQuantity(),(self.default_quantity-1)*2)

  def stepCheckPackingListLineWithNewResource(self,sequence=None, sequence_list=None, **kw):
    """
      Look if the packing list has new resource
    """
    packing_list_line = sequence.get('packing_list_line')
    new_resource = sequence.get('resource')
    self.assertEqual(packing_list_line.getQuantity(), self.default_quantity*2)
    self.assertEqual(packing_list_line.getResourceValue(), new_resource)
    simulation_line_list = packing_list_line.getDeliveryRelatedValueList()
    order_line_list = sum([x.getParentValue().getParentValue().getDeliveryList()
                           for x in simulation_line_list], [])
    self.assertEqual(sorted(packing_list_line.getCausalityList()),
                      sorted(order_line_list))

  def stepCheckPackingListLineWithPreviousResource(self, sequence=None):
    packing_list_line = sequence.get('packing_list_line')
    old_resource = sequence['resource_list'][-2]
    self.assertEqual(packing_list_line.getResourceValue(), old_resource)

  def stepCheckPackingListLineWithSameResource(self,sequence=None, sequence_list=None, **kw):
    """
      Look if the packing list has new previsions
    """
    resource = sequence.get('resource')
    for line in sequence.get('packing_list').getMovementList():
      self.assertEqual(line.getResourceValue(), resource)
      self.assertEqual(line.getQuantity(), self.default_quantity)
      self.assertEqual(line.getCausalityList(),
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
    self.assertEqual(packing_list_line.getQuantity(),self.default_quantity)
    self.assertEqual(packing_list.getStartDate(),self.datetime+15)
    simulation_movement_list = applied_rule.objectValues()
    resource_list = sequence.get('resource_list')
    self.assertEqual(len(simulation_movement_list),len(resource_list))
    delivery_value_list = []
    for simulation_movement in simulation_movement_list:
#      self.assertNotEquals(simulation_movement.getDeliveryValue(),None)
      delivery_value = simulation_movement.getDeliveryValue()
      if delivery_value not in delivery_value_list:
        delivery_value_list.append(delivery_value_list)
#      new_packing_list = delivery_value.getParentValue()
#      self.assertNotEquals(new_packing_list.getUid(),packing_list.getUid())
    self.assertEqual(len(delivery_value_list),len(resource_list))

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
    self.assertEqual(packing_list_line.getQuantity(),self.default_quantity)
    self.assertEqual(packing_list.getStartDate(),self.datetime+10)
    self.assertEqual(new_packing_list_line.getQuantity(),self.default_quantity)
    self.assertEqual(new_packing_list.getStartDate(),self.datetime+15)
    simulation_movement_list = applied_rule.objectValues()
    resource_list = sequence.get('resource_list')
    self.assertEqual(len(simulation_movement_list),len(resource_list))
    delivery_value_list = []
    for simulation_movement in simulation_movement_list:
#      self.assertNotEquals(simulation_movement.getDeliveryValue(),None)
      delivery_value = simulation_movement.getDeliveryValue()
      if delivery_value not in delivery_value_list:
        delivery_value_list.append(delivery_value_list)
#      new_packing_list = delivery_value.getParentValue()
#      self.assertNotEquals(new_packing_list.getUid(),packing_list.getUid())
    self.assertEqual(len(delivery_value_list),len(resource_list))

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
    self.assertEqual(self.default_quantity - 1, container_line.getQuantity())
    self.assertEqual(self.default_quantity - 1,
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
        self.assertEqual(quantity, container_line.getQuantity())
        self.assertEqual(quantity, container_line.getTotalQuantity())
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
          self.assertEqual(old_cell.getQuantity(), cell.getQuantity())
          self.assertEqual(old_cell.getTotalQuantity(), cell.getTotalQuantity())

        self.assertEqual(line.getQuantity(), container_line.getQuantity())
        self.assertEqual(line.getTotalQuantity(), container_line.getTotalQuantity())

    # quantity is 1 on the container itself
    self.assertEqual(1, container.getQuantity())
    self.assertEqual(1, container.getTotalQuantity())

  def stepCheckPackingListIsNotPacked(self,sequence=None, sequence_list=None, **kw):
    """
      Check that the number of objects in containers are
      not equals to the quantity of the packing list
    """
    packing_list = sequence.get('packing_list')
    self.assertFalse(packing_list.isPacked())
    self.assertEqual('missing', packing_list.getContainerState())

  def stepCheckPackingListIsPacked(self,sequence=None, sequence_list=None,
                                   packing_list=None,**kw):
    """
      Check that the number of objects in containers are
      equals to the quantity of the packing list
    """
    if packing_list is None:
      packing_list = sequence.get('packing_list')
    self.commit()
    self.assertTrue(packing_list.isPacked())
    self.assertEqual('packed', packing_list.getContainerState())

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

  def callPackingListBuilderList(self, packing_list):
    # build split deliveries manually. XXX ad-hoc
    previous_tag = None
    for delivery_builder in packing_list.getBuilderList():
      after_tag = []
      if previous_tag:
        after_tag.append(previous_tag)
      delivery_builder.activate(
        after_method_id=('solve',
                         'immediateReindexObject'), # XXX too brutal.
        after_tag=after_tag,
        ).build(explanation_uid=packing_list.getCausalityValue().getUid())

  def stepMergeSplittedPackingList(self, sequence=None):
    """
    Invoke the merge of the two sales packing list and check the merged packing list

    Then also try to create a packing list not coming from order, and then
    tro to merge it with the merged packing list
    """
    # Merge the two existing packing list
    packing_list1 = sequence.get('packing_list')
    packing_list2 = sequence.get('new_packing_list')
    self.portal.portal_simulation.mergeDeliveryList([packing_list1, packing_list2])
    self.tic()
    self.assertEqual('confirmed', packing_list1.getSimulationState())
    self.assertEqual('cancelled', packing_list2.getSimulationState())
    line, = packing_list1.objectValues(
          portal_type= self.packing_list_line_portal_type)
    self.assertEqual(self.default_quantity,line.getQuantity())
    self.assertTrue(packing_list1.getStartDate() is not None)
    self.assertTrue(packing_list1.getStopDate() is not None)
    # Now clone the merged packing list, so that we will have :
    # - one packing list coming from order (merged_packing_list)
    # - one not coming from order (the cloned one)
    cloned_packing_list = packing_list1.Base_createCloneDocument(batch_mode=True)
    cloned_packing_list.setStartDate(cloned_packing_list.getStartDate() + 1)
    cloned_packing_list.setStopDate(cloned_packing_list.getStopDate() + 1)
    cloned_line, = cloned_packing_list.objectValues()
    cloned_line.setQuantity(self.default_quantity+1)
    self.portal.portal_workflow.doActionFor(cloned_packing_list, "confirm_action")
    self.tic()
    self.portal.portal_simulation.mergeDeliveryList([packing_list1, cloned_packing_list])
    self.tic()
    self.assertEqual('confirmed', packing_list1.getSimulationState())
    self.assertEqual('cancelled', cloned_packing_list.getSimulationState())
    resource = sequence.get('resource').getRelativeUrl()
    def checkLineSet(delivery, expected_set):
      line_list = delivery.getMovementList()
      self.assertEqual(len(line_list), len(expected_set))
    expected_set = set([(resource, self.default_quantity, 555),
                        (resource, self.default_quantity+1, 555)])
    checkLineSet(packing_list1, expected_set)

class TestPackingList(TestPackingListMixin, ERP5TypeTestCase) :

  run_all_test = 1
  quiet = 0

  def test_01_PackingListDecreaseQuantity(self, quiet=quiet, run=run_all_test):
    """
      Change the quantity on an delivery line, then
      see if the packing list is divergent and then
      split and defer the packing list

      Finally, check we can merge if needed
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
        MergeSplittedPackingList
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

  def test_05g_SimulationAfterCloningLine(self):
    sequence_list = SequenceList()

    sequence_string = self.default_sequence
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)
    sequence = sequence_list.getSequenceList()[0]
    packing_list = sequence.get('packing_list')
    self.assertEqual(None, packing_list.getCausalityRelatedValue(
         portal_type="Applied Rule"))
    line, = packing_list.getMovementList()
    line.Base_createCloneDocument(batch_mode=True)
    self.assertEqual('calculating', packing_list.getCausalityState())
    self.tic()
    self.assertEqual('solved', packing_list.getCausalityState())
    applied_rule = packing_list.getCausalityRelatedValue(
         portal_type="Applied Rule")
    self.assertNotEqual(None, applied_rule)
    self.assertEqual(1, len(applied_rule.objectValues()))
    # create new line and check simulation has it
    line.Base_createCloneDocument(batch_mode=True)
    self.assertEqual('calculating', packing_list.getCausalityState())
    self.tic()
    self.assertEqual('solved', packing_list.getCausalityState())
    self.assertEqual(2, len(applied_rule.objectValues()))

  def stepModifySimulationMovementWithOppositeQuantities(self,sequence=None, sequence_list=None, **kw):
    """
      Make simulation movement having opposite quantities
    """
    simulation_movement_list = self._getSPLSimulationMovementList(sequence)
    new_quantity_list = [self.default_quantity, -self.default_quantity]
    for index, simulation_movement in enumerate(simulation_movement_list):
      # we record the property so it doesn't get changed by expand with
      # the value from a higher simulation level
      simulation_movement.recordProperty('quantity')
      simulation_movement.edit(quantity=new_quantity_list[index])
      simulation_movement.expand()

  def stepCheckPackingListLineHavingQuantityZero(self,sequence=None, sequence_list=None, **kw):
    """
      Look if the packing list has new previsions
    """
    packing_list_line = sequence.get('packing_list_line')
    self.assertEqual(packing_list_line.getQuantity(), 0)

  def test_05h_SimulationAdoptPrevisionOnAMergeLineHavingQuantityZero(self):
    """
    In some cases, we might have several simulation movements that makes a total
    quantity of zero. Make sure Adopt Solver works fine in such case
    """
    sequence_list = SequenceList()

    sequence_string = self.default_sequence_with_duplicated_lines + """
        CheckTwoSimulationLines
        ModifySimulationMovementWithOppositeQuantities
        Tic
        CheckPackingListIsDiverged
        AdoptPrevisionQuantity
        Tic
        CheckPackingListIsNotDivergent
        CheckPackingListIsSolved
        CheckPackingListLineHavingQuantityZero
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

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


  def stepDeliverPackingList(self, sequence=None, sequence_list=None, **kw):
    """
      Deliver Packing List
    """
    packing_list = sequence.get('packing_list')
    packing_list.stop()
    packing_list.deliver()

  def stepDeliverNewPackingList(self, sequence=None, sequence_list=None, **kw):
    """
      Deliver New Packing List
    """
    packing_list = sequence.get('new_packing_list')
    packing_list.stop()
    packing_list.deliver()

  def stepCheckExpandOrderRootAppliedRuleIsStable(self, sequence=None, sequence_list=None, **kw):
    """
      Check Order Applied Rule can be expanded without error
    """
    order = sequence.get('order')
    related_applied_rule_list = order.getCausalityRelatedValueList( \
                                  portal_type=self.applied_rule_portal_type)
    applied_rule = related_applied_rule_list[0].getObject()
    before = set(getTree(applied_rule))
    applied_rule.expand("immediate")
    after = getTree(applied_rule)
    self.assertTrue(before.issubset(after))
    for element in after:
      if element in before:
        if (element.getPortalType() == 'Simulation Movement' and
            element.getDelivery() and
            element.getParentValue().getSpecialiseValue().getPortalType()
            != 'Order Root Simulation Rule'):
          self.assertFalse(element.getDivergenceList())
      else:
        if element.getPortalType() == 'Simulation Movement':
          element = element.getParentValue()
          self.assertNotIn(element, before)

  def test_11_02_PackingListDecreaseTwoTimesQuantityAndUpdateDeliveryAndDeliver(self,
                                               quiet=quiet, run=run_all_test):
    """
      Change the quantity on an delivery line, then
      see if the packing list is divergent and then
      split and defer the packing list.
      Deliver Packing Lists and make sure the root can be expanded
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
        DeliverPackingList
        DeliverNewPackingList
        Tic
        CheckExpandOrderRootAppliedRuleIsStable
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)


  def stepSplitAndMovePackingList(self, sequence=None, sequence_list=None, **kw):
    """
      Do the split and move to another delivery action
    """
    packing_list = sequence.get('packing_list')
    new_packing_list = sequence.get('new_packing_list')
    solver_process_tool = self.portal.portal_solver_processes
    solver_process = solver_process_tool.newSolverProcess(packing_list)
    quantity_solver_decision, = [x for x in solver_process.contentValues()
      if 'quantity' in x.getCausalityValue().getTestedPropertyList()]
    # use Quantity Split Solver.
    quantity_solver_decision.setSolverValue(self.portal.portal_solvers['Quantity Split Move Solver'])
    # configure for Quantity Split Solver.
    kw = {'delivery_solver':'FIFO Delivery Solver',
          'delivery_url': new_packing_list.getRelativeUrl()}
    quantity_solver_decision.updateConfiguration(**kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def stepCheckSeveralDivergenceAction(self, sequence=None, sequence_list=None, **kw):
    """
      Do the split and move to another delivery action
    """
    packing_list1 = sequence.get('packing_list')
    line1, = packing_list1.objectValues(portal_type=self.packing_list_line_portal_type)
    packing_list2 = sequence.get('new_packing_list')
    # Make sure we can split and defer the new packing list, this would make
    # use of FIFO delivery solver in the case we have several lines
    line2, = packing_list2.objectValues(portal_type=self.packing_list_line_portal_type)
    line2.setQuantity(1.5)
    self.tic()
    self.assertEqual('diverged', packing_list2.getCausalityState())
    solver_process, = [x for x in packing_list2.getSolverValueList() if \
                       x.getValidationState() == "draft"]
    quantity_solver_decision, = [x for x in solver_process.contentValues()
      if 'quantity' in x.getCausalityValue().getTestedPropertyList()]
    # use Quantity Split Solver.
    quantity_solver_decision.setSolverValue(self.portal.portal_solvers['Quantity Split Solver'])
    # configure for Quantity Split Solver.
    kw = {'delivery_solver':'FIFO Delivery Solver',
          'start_date':self.datetime + 35,
          'stop_date':self.datetime + 45}
    quantity_solver_decision.updateConfiguration(**kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()
    self.callPackingListBuilderList(packing_list2)
    self.tic()
    packing_list1, packing_list2, packing_list3 = self.getCreatedTypeList(
      self.packing_list_portal_type)
    line3, = packing_list3.objectValues(portal_type=self.packing_list_line_portal_type)
    self.assertEqual(0.5, line3.getQuantity())
    self.assertEqual('solved', packing_list1.getCausalityState())
    self.assertEqual('solved', packing_list2.getCausalityState())
    self.assertEqual('solved', packing_list3.getCausalityState())
    # And now make sure we could accept a new quantity in case we have several
    # simulation movements
    line2.setQuantity(1.2)
    self.tic()
    self.assertEqual('diverged', packing_list2.getCausalityState())
    solver_process, = [x for x in packing_list2.getSolverValueList() if \
                       x.getValidationState() == "draft"]
    quantity_solver_decision, = [x for x in solver_process.contentValues()
      if 'quantity' in x.getCausalityValue().getTestedPropertyList()]
    # use Quantity Split Solver.
    quantity_solver_decision.setSolverValue(self.portal.portal_solvers['Accept Solver'])
    kw = {'tested_property_list':['quantity']}
    quantity_solver_decision.updateConfiguration(**kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()
    self.callPackingListBuilderList(packing_list2)
    self.tic()
    packing_list1, packing_list2, packing_list3 = self.getCreatedTypeList(
      self.packing_list_portal_type)
    self.assertEqual('solved', packing_list1.getCausalityState())
    self.assertEqual('solved', packing_list2.getCausalityState())
    self.assertEqual('solved', packing_list3.getCausalityState())
    self.assertEqual(self.default_quantity-2, line1.getQuantity())
    self.assertEqual(1.2, line2.getQuantity())
    self.assertEqual(0.5, line3.getQuantity())

  def test_11b_PackingListDecreaseTwoTimesQuantityAndMoveToDelivery(self,
                                               quiet=quiet, run=run_all_test):
    """
      Change the quantity on an delivery line, then
      split and defer the packing list. Then decrease again the quantity,
      and use solver "split and move" to move the quantity to the second packing
      list. The second packing list would be solved by the "split and move"
      solver
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
        SplitAndMovePackingList
        Tic
        CheckNewPackingListIsSolved
        CheckPackingListSplittedTwoTimes
        CheckSeveralDivergenceAction
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_11c_MoveSeveralLinesToDelivery(self,
                                               quiet=quiet, run=run_all_test):
    """
      Move partially two lines in a new packing list.
      Then move again partially theses 2 same lines in the same new packing list.
    """
    if not run: return
    from Products.CMFActivity.ActivityRuntimeEnvironment import BaseMessage
    BaseMessage.max_retry = property(lambda self:
      self.activity_kw.get('max_retry', 0))
    sequence = Sequence(context=self)
    sequence_string = self.default_sequence_with_two_lines
    sequence(sequence_string)
    sale_packing_list1, = self.getCreatedTypeList(
      self.packing_list_portal_type)
    movement_list = sale_packing_list1.getMovementList()
    self.assertEqual(2, len(movement_list))
    movement_list[0].setQuantity(self.default_quantity-1)
    self.tic()
    sequence("""SplitAndDeferPackingList
                Tic""")
    sale_packing_list2, = [x for x in self.getCreatedTypeList(
      self.packing_list_portal_type) if x.getUid() != sale_packing_list1.getUid()]
    # now decide to move the two lines
    def moveTwoLines(from_delivery, to_delivery):
      movement_list = from_delivery.getMovementList()
      self.assertEqual(2, len(movement_list))
      for movement in movement_list:
        movement.setQuantity(movement.getQuantity()-1)
      self.tic()
      self.assertEqual("draft", from_delivery.getSolverValueList()[-1].getValidationState())
      quantity_solver_decision_list = [x for x in from_delivery.Delivery_getSolverDecisionList()
        if 'quantity' in x.getCausalityValue().getTestedPropertyList()]
      # use Quantity Split Solver.
      for quantity_solver_decision in quantity_solver_decision_list:
        quantity_solver_decision.setSolverValue(self.portal.portal_solvers['Quantity Split Move Solver'])
        # configure for Quantity Split Solver.
        kw = {'delivery_solver':'FIFO Delivery Solver',
              'delivery_url': to_delivery.getRelativeUrl()}
        quantity_solver_decision.updateConfiguration(**kw)
      solver_process = quantity_solver_decision.getParentValue()
      solver_process.buildTargetSolverList()
      solver_process.solve()
      self.tic()
    # first move of two lines. Here sale packing list 2 has only one line, then
    # will have two lines after the move
    self.assertEqual("solved", sale_packing_list1.getCausalityState())
    self.assertEqual("solved", sale_packing_list2.getCausalityState())
    self.assertEqual({self.default_quantity-1, self.default_quantity},
                     set([x.getQuantity() for x in sale_packing_list1.getMovementList()]))
    self.assertEqual({1}, set([x.getQuantity() for x in sale_packing_list2.getMovementList()]))
    moveTwoLines(sale_packing_list1, sale_packing_list2)
    self.assertEqual("solved", sale_packing_list1.getCausalityState())
    self.assertEqual("solved", sale_packing_list2.getCausalityState())
    self.assertEqual({self.default_quantity-2, self.default_quantity-1},
                     set([x.getQuantity() for x in sale_packing_list1.getMovementList()]))
    self.assertEqual({1, 2}, set([x.getQuantity() for x in sale_packing_list2.getMovementList()]))
    # move two lines again. This time, the sale packing list already have 2 lines,
    # thus they will be just completed
    moveTwoLines(sale_packing_list1, sale_packing_list2)
    self.assertEqual("solved", sale_packing_list1.getCausalityState())
    self.assertEqual("solved", sale_packing_list2.getCausalityState())
    self.assertEqual({self.default_quantity-3, self.default_quantity-2},
                     set([x.getQuantity() for x in sale_packing_list1.getMovementList()]))
    self.assertEqual({2, 3}, set([x.getQuantity() for x in sale_packing_list2.getMovementList()]))
    # Now Split again first SPL to create a 3rd SPL
    def splitSalePackingList():
      movement_list = sale_packing_list1.getMovementList()
      self.assertEqual(2, len(movement_list))
      for movement in movement_list:
        movement.setQuantity(movement.getQuantity()-1)
      self.tic()
      self.assertEqual("draft", sale_packing_list1.getSolverValueList()[-1].getValidationState())
      quantity_solver_decision_list = [x for x in sale_packing_list1.Delivery_getSolverDecisionList()
        if 'quantity' in x.getCausalityValue().getTestedPropertyList()]
      # use Quantity Split Solver.
      for quantity_solver_decision in quantity_solver_decision_list:
        quantity_solver_decision.setSolverValue(self.portal.portal_solvers['Quantity Split Solver'])
        # configure for Quantity Split Solver.
        kw = {'delivery_solver':'FIFO Delivery Solver',
              'start_date':self.datetime + 36,
              'stop_date':self.datetime + 46}
        quantity_solver_decision.updateConfiguration(**kw)
      solver_process = quantity_solver_decision.getParentValue()
      solver_process.buildTargetSolverList()
      solver_process.solve()
      self.tic()
      self.callPackingListBuilderList(sale_packing_list1)
      self.tic()
    splitSalePackingList()
    sale_packing_list3, = [x for x in self.getCreatedTypeList(
      self.packing_list_portal_type) if not(x.getUid() in (sale_packing_list1.getUid(),
                                                           sale_packing_list2.getUid()))]
    self.assertEqual({self.default_quantity-4, self.default_quantity-3},
                     set([x.getQuantity() for x in sale_packing_list1.getMovementList()]))
    self.assertEqual({1}, set([x.getQuantity() for x in sale_packing_list3.getMovementList()]))
    self.assertEqual("solved", sale_packing_list3.getCausalityState())
    self.assertEqual("solved", sale_packing_list1.getCausalityState())
    def getSolverProcessStateList(delivery):
      return [x.getValidationState() for x in delivery.getSolverValueList()]
    # we should have as many solver process as we had split
    self.assertEqual(["solved"]*4, getSolverProcessStateList(sale_packing_list1))
    # Now try to move quantities several times and make sure all quantities are correct
    moveTwoLines(sale_packing_list2, sale_packing_list3)
    self.assertEqual({self.default_quantity-4, self.default_quantity-3},
                     set([x.getQuantity() for x in sale_packing_list1.getMovementList()]))
    self.assertEqual({1, 2}, set([x.getQuantity() for x in sale_packing_list2.getMovementList()]))
    self.assertEqual({2}, set([x.getQuantity() for x in sale_packing_list3.getMovementList()]))
    self.assertEqual("solved", sale_packing_list1.getCausalityState())
    self.assertEqual("solved", sale_packing_list2.getCausalityState())
    self.assertEqual("solved", sale_packing_list3.getCausalityState())
    moveTwoLines(sale_packing_list1, sale_packing_list2)
    sale_packing_list2.start()
    self.tic()
    sale_packing_list2.deliver()
    self.assertEqual({self.default_quantity-5, self.default_quantity-4},
                     set([x.getQuantity() for x in sale_packing_list1.getMovementList()]))
    self.assertEqual({2, 3}, set([x.getQuantity() for x in sale_packing_list2.getMovementList()]))
    self.assertEqual({2}, set([x.getQuantity() for x in sale_packing_list3.getMovementList()]))
    self.assertEqual("solved", sale_packing_list1.getCausalityState())
    self.assertEqual("solved", sale_packing_list2.getCausalityState())
    self.assertEqual("solved", sale_packing_list3.getCausalityState())
    moveTwoLines(sale_packing_list1, sale_packing_list3)
    # There was 6 split of sale packing list #
    self.assertEqual(["solved"]*6, getSolverProcessStateList(sale_packing_list1))
    # 4 solver process (2 adopt since we were destination of split move, 1 split and move,
    # and 1 adopt again since we were again destination of split move
    self.assertEqual(["solved"]*4, getSolverProcessStateList(sale_packing_list2))
    # 2 times adopt since we were destination of split move 2 times
    self.assertEqual(["solved"]*2, getSolverProcessStateList(sale_packing_list3))
    self.assertEqual({self.default_quantity-6, self.default_quantity-5},
                     set([x.getQuantity() for x in sale_packing_list1.getMovementList()]))
    self.assertEqual({2, 3}, set([x.getQuantity() for x in sale_packing_list2.getMovementList()]))
    self.assertEqual({3}, set([x.getQuantity() for x in sale_packing_list3.getMovementList()]))
    self.assertEqual("solved", sale_packing_list1.getCausalityState())
    self.assertEqual("solved", sale_packing_list2.getCausalityState())
    self.assertEqual("solved", sale_packing_list3.getCausalityState())

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
    self.assertTrue(hasattr(pl, 'getPriceCurrency'))

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
    packing_list.newContent(
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
    self.stepCreateOrganisation(sequence, None, 'dummy_source')
    sequence.edit(source_account = sequence.get('dummy_source')['bank'])

  def stepCreateDestinationAccount(self, sequence=None, **kw):
    self.stepCreateOrganisation(sequence, None,
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
    self.assertEqual(reference_result, [line_ddd, line_ccc,
      line_bbb_cell_bbb, line_bbb_cell_aaa, line_aaa])

    # check it's possible to sort by int_index
    int_index_result = packing_list.getMovementList(sort_on=
        [('int_index', 'ascending')])
    self.assertEqual(int_index_result, [line_bbb_cell_aaa, line_bbb_cell_bbb,
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
    self.assertNotIn('Site Error', order.view())


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

  def stepAssertCausalityStateIsNotSolvedInConsistencyMessage(self,
                    sequence=None, sequence_list=None, **kw):
    """
      Test that Causality State not solved appears in check consistency
    """
    packing_list = sequence.get('packing_list')
    self.assertEqual(
      ['Causality State is not "Solved". Please wait or take action'
        + ' for causality state to reach "Solved".'],
      [str(message.message) for message in packing_list.checkConsistency()])

  def test_20_PackingListCausalityStateConstraint(self,
      quiet=quiet, run=run_all_test):
    """
      Check that consistency takes into account the Causality State
    """
    if not run: return
    sequence_list = SequenceList()

    sequence_string = self.default_sequence + """
        DecreasePackingListLineQuantity
        CheckPackingListIsCalculating
        AssertCausalityStateIsNotSolvedInConsistencyMessage
        Tic
        CheckPackingListIsDiverged
        AssertCausalityStateIsNotSolvedInConsistencyMessage
        """
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def stepIncreasePackingListLineNegativeQuantity(self, sequence=None,
      sequence_list=None, **kw):
    """
    Set a decreased quantity on packing list lines
    """
    packing_list = sequence.get('packing_list')
    quantity = sequence.get('line_quantity',default=self.default_quantity)
    quantity = quantity + 1
    sequence.edit(line_quantity=quantity)
    packing_list_line, = packing_list.getMovementList(portal_type=self.packing_list_line_portal_type)
    packing_list_line.edit(quantity=quantity)
    for packing_list_line in packing_list.objectValues(
        portal_type=self.packing_list_line_portal_type):
      packing_list_line.edit(quantity=quantity)

  def stepCheckPackingListSplittedWithNegativeQuantity(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list was splitted
    """
    packing_list1, packing_list2 = self.getTwoRelatedPackingList(sequence)
    packing_list1_line, = packing_list1.objectValues(portal_type=self.packing_list_line_portal_type)
    self.assertEqual(self.default_quantity+1,packing_list1_line.getQuantity())
    packing_list2_line, = packing_list2.objectValues(portal_type=self.packing_list_line_portal_type)
    self.assertEqual(-1,packing_list2_line.getQuantity())

  def stepCheckPackingListSplittedTwoTimesWithNegativeQuantity(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list is splitted two times
    """
    packing_list1, packing_list2 = self.getTwoRelatedPackingList(sequence)
    packing_list1_line, = packing_list1.objectValues(portal_type=self.packing_list_line_portal_type)
    self.assertEqual(self.default_quantity+2,packing_list1_line.getQuantity())
    packing_list2_line, = packing_list2.objectValues(portal_type=self.packing_list_line_portal_type)
    self.assertEqual(-2,packing_list2_line.getQuantity())

  def test_21_PackingListQuantitySplitNegativeQuantity(self):
    """
      Make sur quantity split solver works fine in the case we have
      negative quantities. Probably rarely useful in the case of sale packing
      list, but could be useful in other kinds of delivery (like in MRP).
    """
    try:
      self.default_quantity = -99

      sequence_list = SequenceList()

      sequence_string = self.default_sequence + """
          IncreasePackingListLineNegativeQuantity
          CheckPackingListIsCalculating
          Tic
          CheckPackingListIsDiverged
          SplitAndDeferPackingList
          Tic
          CheckPackingListIsSolved
          CheckPackingListSplittedWithNegativeQuantity
          IncreasePackingListLineNegativeQuantity
          CheckPackingListIsCalculating
          Tic
          CheckPackingListIsDiverged
          SplitAndMovePackingList
          Tic
          CheckNewPackingListIsSolved
          stepCheckPackingListSplittedTwoTimesWithNegativeQuantity
          """
      sequence_list.addSequenceString(sequence_string)

      sequence_list.play(self)

    finally:
      delattr(self, "default_quantity")

class TestSolvingPackingList(TestPackingListMixin, ERP5TypeTestCase):
  quiet = 0

  def afterSetUp(self):
    TestPackingListMixin.afterSetUp(self)
    solver_process_type_info = self.portal.portal_types['Solver Process']
    self.original_allowed_content_types = \
      solver_process_type_info.getTypeAllowedContentTypeList()
    self.added_target_solver_list = []

  @UnrestrictedMethod
  def beforeTearDown(self):
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
    type_object = self.portal.portal_types.getTypeInfo(solver_id)
    type_object.setTypeWorkflowList(['solver_workflow'])
    self.portal.portal_caches.clearAllCache()
    self.added_target_solver_list.append(solver_id)

  @UnrestrictedMethod
  def stepSetUpAutomaticQuantityAcceptSolver(self, sequence=None, sequence_list=None):
    self._setUpTargetSolver('Automatic Quantity Accept Solver',
                            'AcceptSolver', ('quantity',))
    self.portal.portal_rules.new_delivery_simulation_rule.quantity_tester.edit(
      solver=('portal_solvers/Automatic Quantity Accept Solver',))

  @UnrestrictedMethod
  def stepSetUpAutomaticQuantityAdoptSolver(self, sequence=None, sequence_list=None):
    self._setUpTargetSolver('Automatic Quantity Adopt Solver',
                            'AdoptSolver', ('quantity',))
    self.portal.portal_rules.new_delivery_simulation_rule.quantity_tester.edit(
      solver=('portal_solvers/Automatic Quantity Adopt Solver',))

  @UnrestrictedMethod
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
    new_packing_list = [
      x for x in order.getCausalityRelatedValueList(
        portal_type=packing_list.getPortalType())
      if x != packing_list][0]
    self.assertEqual(len(packing_list.getMovementList()),
                      len(order.getMovementList()) - 10)
    self.assertEqual(len(new_packing_list.getMovementList()), 10)

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

  def test_subcontent_reindexing_container_line_cell(self):
    """No need to check Containers in Purchase Packing List"""

class TestPurchasePackingList(TestPurchasePackingListMixin, TestPackingList):
  """Tests for purchase packing list.
  """


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPackingList))
  suite.addTest(unittest.makeSuite(TestSolvingPackingList))
  suite.addTest(unittest.makeSuite(TestPurchasePackingList))
  return suite