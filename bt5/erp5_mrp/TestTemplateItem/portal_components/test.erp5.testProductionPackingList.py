# -*- coding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#          Łukasz Nowak <lukasz.nowak@ventis.com.pl>
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
from Products.ERP5Type.tests.Sequence import SequenceList
from erp5.component.test.testProductionOrder import TestProductionOrderMixin
from erp5.component.test.testPackingList import TestPackingListMixin
from Products.ERP5.tests.utils import newSimulationExpectedFailure

class TestProductionPackingReportListMixin(TestProductionOrderMixin, TestPackingListMixin, \
                          ERP5TypeTestCase):
  """Mixin for testing Production Packing Lists and Manufacturing Executions"""

  def modifyPackingListState(self, transition_name,
                             sequence,packing_list=None):
    """ calls the workflow for the packing list """
    if packing_list is None:
      packing_list = sequence.get('packing_list')
    packing_list.portal_workflow.doActionFor(packing_list, transition_name)

  def stepAcceptDecisionSupplyDeliveryPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('supply_delivery_packing_list')
    self._solveDivergence(packing_list, 'quantity', 'accept')

  def stepAcceptDecisionProducedDeliveryPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('produced_delivery_packing_list')
    self._solveDivergence(packing_list, 'quantity', 'accept')

  def stepAdoptPrevisionSupplyDeliveryPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('supply_delivery_packing_list')
    self._solveDivergence(packing_list, 'quantity', 'adopt')

  def stepAdoptPrevisionProducedDeliveryPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('produced_delivery_packing_list')
    self._solveDivergence(packing_list, 'quantity', 'adopt')

  def stepAdoptPrevisionProducedReport(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('produced_report')
    self._solveDivergence(packing_list, 'quantity', 'adopt')

  def stepAdoptPrevisionConsumedReport(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('consumed_report')
    self._solveDivergence(packing_list, 'quantity', 'adopt')

  def stepSetReadyProducedDeliveryPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('produced_delivery_packing_list')
    self.modifyPackingListState('set_ready_action', sequence=sequence, packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'ready')

  def stepStartProducedDeliveryPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('produced_delivery_packing_list')
    self.modifyPackingListState('start_action', sequence=sequence, packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'started')

  def stepStopProducedDeliveryPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('produced_delivery_packing_list')
    self.modifyPackingListState('stop_action', sequence=sequence, packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'stopped')

  def stepDeliverProducedDeliveryPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('produced_delivery_packing_list')
    self.modifyPackingListState('deliver_action', sequence=sequence, packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'delivered')

  def stepSetReadySupplyDeliveryPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('supply_delivery_packing_list')
    self.modifyPackingListState('set_ready_action', sequence=sequence, packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'ready')

  def stepStartSupplyDeliveryPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('supply_delivery_packing_list')
    self.modifyPackingListState('start_action', sequence=sequence, packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'started')

  def stepStopSupplyDeliveryPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('supply_delivery_packing_list')
    self.modifyPackingListState('stop_action', sequence=sequence, packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'stopped')

  def stepDeliverSupplyDeliveryPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('supply_delivery_packing_list')
    self.modifyPackingListState('deliver_action', sequence=sequence, packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'delivered')

  def stepSetReadyProducedReport(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('produced_report')
    self.modifyPackingListState('set_ready_action', sequence=sequence, packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'ready')

  def stepStartProducedReport(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('produced_report')
    self.modifyPackingListState('start_action', sequence=sequence, packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'started')

  def stepStopProducedReport(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('produced_report')
    self.modifyPackingListState('stop_action', sequence=sequence, packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'stopped')

  def stepDeliverProducedReport(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('produced_report')
    self.modifyPackingListState('deliver_action', sequence=sequence, packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'delivered')

  def stepSetReadyConsumedReport(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('consumed_report')
    self.modifyPackingListState('set_ready_action', sequence=sequence, packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'ready')

  def stepStartConsumedReport(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('consumed_report')
    self.modifyPackingListState('start_action', sequence=sequence, packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'started')

  def stepStopConsumedReport(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('consumed_report')
    self.modifyPackingListState('stop_action', sequence=sequence, packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'stopped')

  def stepDeliverConsumedReport(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('consumed_report')
    self.modifyPackingListState('deliver_action', sequence=sequence, packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'delivered')

  def stepDecreaseProducedDeliveryPackingListQuantity(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('produced_delivery_packing_list')

    for line in packing_list.getMovementList():
      line.edit(
        quantity = line.getQuantity() - 1.0
      )

  def stepDecreaseSupplyDeliveryPackingListQuantity(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('supply_delivery_packing_list')

    for line in packing_list.getMovementList():
      line.edit(
        quantity = line.getQuantity() - 1.0
      )

  def stepCheckSourcingDeliverySimulationDecreasedQuantity(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
    TODO
    """
    self.logMessage('TODO')

  def stepCheckSourcingDeliverySimulation(self, sequence=None, \
                                    sequence_list=None, **kw):
    """
      Hardcoded delivery checks
    """
    self.stepCheckSourcingSimulation(sequence,sequence_list,**kw)

    produced_movement = sequence.get('produced_movement')
    operation_movement = sequence.get('operation_movement')
    component_movement = sequence.get('component_movement')
    supply_movement = sequence.get('supply_movement')
    produced_delivery_movement = sequence.get('produced_delivery_movement')

    produced_delivery_packing_list = produced_delivery_movement.getDeliveryValue().getParentValue()
    supply_delivery_packing_list = supply_movement.getDeliveryValue().getParentValue()

    produced_report = produced_movement.getDeliveryValue().getParentValue()

    operation_report = operation_movement.getDeliveryValue().getParentValue()
    component_report = component_movement.getDeliveryValue().getParentValue()
    self.assertEqual(operation_report, component_report)
    consumed_report = operation_report

    # checks that simulations are same
    # TODO: resources, quantities, dates, ...
    self.assertEqual(
      produced_delivery_movement.getSimulationState(),
      produced_delivery_packing_list.getSimulationState()
    )

    self.assertEqual(
      supply_movement.getSimulationState(),
      supply_delivery_packing_list.getSimulationState()
    )

    self.assertEqual(
      produced_movement.getSimulationState(),
      produced_report.getSimulationState()
    )

    self.assertEqual(
      component_movement.getSimulationState(),
      consumed_report.getSimulationState()
    )

    self.assertEqual(
      operation_movement.getSimulationState(),
      consumed_report.getSimulationState()
    )

    sequence.edit(
      produced_delivery_packing_list = produced_delivery_packing_list,
      supply_delivery_packing_list = supply_delivery_packing_list,
      produced_report = produced_report,
      consumed_report = consumed_report,
    )

  def stepCheckProducedDeliveryPackingListIsConfirmed(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('produced_delivery_packing_list')

    self.assertEqual(
      'confirmed',
      packing_list.getSimulationState()
    )

  def stepCheckProducedDeliveryPackingListIsDelivered(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('produced_delivery_packing_list')

    self.assertEqual(
      'delivered',
      packing_list.getSimulationState()
    )

  def stepCheckSupplyDeliveryPackingListIsDelivered(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('supply_delivery_packing_list')

    self.assertEqual(
      'delivered',
      packing_list.getSimulationState()
    )

  def stepCheckProducedReportIsDelivered(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('produced_report')

    self.assertEqual(
      'delivered',
      packing_list.getSimulationState()
    )

  def stepCheckConsumedReportIsDelivered(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('consumed_report')

    self.assertEqual(
      'delivered',
      packing_list.getSimulationState()
    )

  def stepCheckProducedDeliveryPackingListIsSolved(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('produced_delivery_packing_list')

    self.assertEqual(
      'solved',
      packing_list.getCausalityState()
    )

  def stepCheckProducedDeliveryPackingListIsDiverged(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('produced_delivery_packing_list')

    self.assertEqual(
      'diverged',
      packing_list.getCausalityState()
    )

  def stepCheckProducedDeliveryPackingListIsCalculating(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('produced_delivery_packing_list')

    self.assertEqual(
      'calculating',
      packing_list.getCausalityState()
    )

  def stepCheckSupplyDeliveryPackingListIsCalculating(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('supply_delivery_packing_list')

    self.assertEqual(
      'calculating',
      packing_list.getCausalityState()
    )

  def stepCheckSupplyDeliveryPackingListIsConfirmed(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('supply_delivery_packing_list')

    self.assertEqual(
      'confirmed',
      packing_list.getSimulationState()
    )

  def stepCheckSupplyDeliveryPackingListIsSolved(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('supply_delivery_packing_list')

    self.assertEqual(
      'solved',
      packing_list.getCausalityState()
    )

  def stepCheckSupplyDeliveryPackingListIsDiverged(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('supply_delivery_packing_list')

    self.assertEqual(
      'diverged',
      packing_list.getCausalityState()
    )

  def stepCheckProducedReportIsConfirmed(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('produced_report')

    self.assertEqual(
      'confirmed',
      packing_list.getSimulationState()
    )

  def stepCheckProducedReportIsSolved(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('produced_report')

    self.assertEqual(
      'solved',
      packing_list.getCausalityState()
    )

  def stepCheckProducedReportIsDiverged(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('produced_report')

    self.assertEqual(
      'diverged',
      packing_list.getCausalityState()
    )

  def stepCheckConsumedReportIsConfirmed(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('consumed_report')

    self.assertEqual(
      'confirmed',
      packing_list.getSimulationState()
    )

  def stepCheckConsumedReportIsSolved(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('consumed_report')

    self.assertEqual(
      'solved',
      packing_list.getCausalityState()
    )

  def stepCheckConsumedReportIsDiverged(self, sequence=None, \
                                    sequence_list=None, **kw):
    packing_list = sequence.get('consumed_report')

    self.assertEqual(
      'diverged',
      packing_list.getCausalityState()
    )

class TestProductionDelivery(TestProductionPackingReportListMixin):
  """Test Production Packing Lists and Reports, mostly based on Production Orders"""

  run_all_test = 1

  def getTitle(self):
    return "Production Delivery: transformation type %s, resource type %s"%(
        self.transformation_portal_type,
        self.resource_portal_type,)

  @newSimulationExpectedFailure
  def test_01_sourcingDelivery(self, quiet=0,
                                          run=run_all_test):
    """
    Test for sourcing type of delivery (Manufacturing Execution and Production Packing Lists).
    """
    # XXX: Need to split to separate test (Luke)
    if not run: return

    delivery_check_sequence_string = self.SOURCING_ORDER_SEQUENCE + '\
                      CheckSourcingDeliverySimulation \
                      \
                      CheckProducedDeliveryPackingListIsConfirmed \
                      CheckProducedDeliveryPackingListIsSolved\
                      \
                      CheckSupplyDeliveryPackingListIsConfirmed \
                      CheckSupplyDeliveryPackingListIsSolved\
                      \
                      CheckProducedReportIsConfirmed \
                      CheckProducedReportIsSolved\
                      \
                      CheckConsumedReportIsConfirmed \
                      CheckConsumedReportIsSolved\
                      \
                      '

    sequence_list = SequenceList()
    # Check states of deliveries, just after order confirmation
    sequence_string = delivery_check_sequence_string
    sequence_list.addSequenceString(sequence_string)

    # Test when packing list are delivered one by one
    # Note: I (Luke) know, that below sequence is long
    #       but I wanted to be sure, that full production
    #       process is doable.
    sequence_string = delivery_check_sequence_string + '\
                      SetReadyProducedDeliveryPackingList \
                      StartProducedDeliveryPackingList \
                      StopProducedDeliveryPackingList \
                      DeliverProducedDeliveryPackingList \
                      Tic \
                      \
                      CheckSourcingDeliverySimulation \
                      \
                      CheckProducedDeliveryPackingListIsDelivered \
                      CheckProducedDeliveryPackingListIsSolved\
                      \
                      CheckSupplyDeliveryPackingListIsConfirmed \
                      CheckSupplyDeliveryPackingListIsSolved\
                      \
                      CheckProducedReportIsConfirmed \
                      CheckProducedReportIsSolved\
                      \
                      CheckConsumedReportIsConfirmed \
                      CheckConsumedReportIsSolved\
                      \
                      SetReadySupplyDeliveryPackingList \
                      StartSupplyDeliveryPackingList \
                      StopSupplyDeliveryPackingList \
                      DeliverSupplyDeliveryPackingList \
                      Tic \
                      \
                      CheckSourcingDeliverySimulation \
                      \
                      CheckProducedDeliveryPackingListIsDelivered \
                      CheckProducedDeliveryPackingListIsSolved\
                      \
                      CheckSupplyDeliveryPackingListIsDelivered \
                      CheckSupplyDeliveryPackingListIsSolved\
                      \
                      CheckProducedReportIsConfirmed \
                      CheckProducedReportIsSolved\
                      \
                      CheckConsumedReportIsConfirmed \
                      CheckConsumedReportIsSolved\
                      \
                      SetReadyProducedReport \
                      StartProducedReport \
                      StopProducedReport \
                      DeliverProducedReport \
                      Tic \
                      \
                      CheckSourcingDeliverySimulation \
                      \
                      CheckProducedDeliveryPackingListIsDelivered \
                      CheckProducedDeliveryPackingListIsSolved\
                      \
                      CheckSupplyDeliveryPackingListIsDelivered \
                      CheckSupplyDeliveryPackingListIsSolved\
                      \
                      CheckProducedReportIsDelivered \
                      CheckProducedReportIsSolved\
                      \
                      CheckConsumedReportIsConfirmed \
                      CheckConsumedReportIsSolved\
                      \
                      SetReadyConsumedReport \
                      StartConsumedReport \
                      StopConsumedReport \
                      DeliverConsumedReport \
                      Tic \
                      \
                      CheckSourcingDeliverySimulation \
                      \
                      CheckProducedDeliveryPackingListIsDelivered \
                      CheckProducedDeliveryPackingListIsSolved\
                      \
                      CheckSupplyDeliveryPackingListIsDelivered \
                      CheckSupplyDeliveryPackingListIsSolved\
                      \
                      CheckProducedReportIsDelivered \
                      CheckProducedReportIsSolved\
                      \
                      CheckConsumedReportIsDelivered \
                      CheckConsumedReportIsSolved\
                      \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Check a case, when Produced Delivery Packing List is diverged
    # then accept this decision, next deliver it, then adopt prevision
    # on rest of documents and deliver them - do it one by one
    sequence_string = delivery_check_sequence_string + '\
                      DecreaseProducedDeliveryPackingListQuantity \
                      \
                      CheckProducedDeliveryPackingListIsCalculating \
                      Tic \
                      CheckProducedDeliveryPackingListIsDiverged \
                      AcceptDecisionProducedDeliveryPackingList \
                      Tic \
                      CheckProducedDeliveryPackingListIsSolved \
                      CheckSourcingDeliverySimulationDecreasedQuantity \
                      \
                      CheckSupplyDeliveryPackingListIsConfirmed \
                      CheckSupplyDeliveryPackingListIsDiverged\
                      \
                      CheckProducedReportIsConfirmed \
                      CheckProducedReportIsDiverged\
                      \
                      CheckConsumedReportIsConfirmed \
                      CheckConsumedReportIsDiverged\
                      \
                      SetReadyProducedDeliveryPackingList \
                      StartProducedDeliveryPackingList \
                      StopProducedDeliveryPackingList \
                      DeliverProducedDeliveryPackingList \
                      Tic \
                      \
                      CheckSourcingDeliverySimulationDecreasedQuantity \
                      \
                      CheckProducedDeliveryPackingListIsDelivered \
                      CheckProducedDeliveryPackingListIsSolved\
                      \
                      CheckSupplyDeliveryPackingListIsConfirmed \
                      CheckSupplyDeliveryPackingListIsDiverged\
                      \
                      CheckProducedReportIsConfirmed \
                      CheckProducedReportIsDiverged\
                      \
                      CheckConsumedReportIsConfirmed \
                      CheckConsumedReportIsDiverged\
                      \
                      AdoptPrevisionSupplyDeliveryPackingList \
                      Tic \
                      CheckSupplyDeliveryPackingListIsSolved \
                      \
                      CheckProducedReportIsConfirmed \
                      CheckProducedReportIsDiverged\
                      \
                      CheckConsumedReportIsConfirmed \
                      CheckConsumedReportIsDiverged\
                      \
                      SetReadySupplyDeliveryPackingList \
                      StartSupplyDeliveryPackingList \
                      StopSupplyDeliveryPackingList \
                      DeliverSupplyDeliveryPackingList \
                      Tic \
                      \
                      CheckSourcingDeliverySimulationDecreasedQuantity \
                      \
                      CheckProducedDeliveryPackingListIsDelivered \
                      CheckProducedDeliveryPackingListIsSolved\
                      \
                      CheckSupplyDeliveryPackingListIsDelivered \
                      CheckSupplyDeliveryPackingListIsSolved\
                      \
                      CheckProducedReportIsConfirmed \
                      CheckProducedReportIsDiverged\
                      \
                      CheckConsumedReportIsConfirmed \
                      CheckConsumedReportIsDiverged\
                      \
                      AdoptPrevisionProducedReport \
                      Tic \
                      CheckProducedReportIsSolved \
                      \
                      CheckConsumedReportIsConfirmed \
                      CheckConsumedReportIsDiverged\
                      \
                      SetReadyProducedReport \
                      StartProducedReport \
                      StopProducedReport \
                      DeliverProducedReport \
                      Tic \
                      \
                      CheckSourcingDeliverySimulationDecreasedQuantity \
                      \
                      CheckProducedDeliveryPackingListIsDelivered \
                      CheckProducedDeliveryPackingListIsSolved\
                      \
                      CheckSupplyDeliveryPackingListIsDelivered \
                      CheckSupplyDeliveryPackingListIsSolved \
                      \
                      CheckProducedReportIsDelivered \
                      CheckProducedReportIsSolved\
                      \
                      CheckConsumedReportIsConfirmed \
                      CheckConsumedReportIsDiverged\
                      \
                      AdoptPrevisionConsumedReport \
                      Tic \
                      CheckProducedReportIsSolved \
                      \
                      SetReadyConsumedReport \
                      StartConsumedReport \
                      StopConsumedReport \
                      DeliverConsumedReport \
                      Tic \
                      \
                      CheckSourcingDeliverySimulationDecreasedQuantity \
                      \
                      CheckProducedDeliveryPackingListIsDelivered \
                      CheckProducedDeliveryPackingListIsSolved\
                      \
                      CheckSupplyDeliveryPackingListIsDelivered \
                      CheckSupplyDeliveryPackingListIsSolved\
                      \
                      CheckProducedReportIsDelivered \
                      CheckProducedReportIsSolved\
                      \
                      CheckConsumedReportIsDelivered \
                      CheckConsumedReportIsSolved\
                      \
                      '
    sequence_list.addSequenceString(sequence_string)

    # Check a case, when Consumed Delivery Packing List is diverged
    # then accept this decision, next deliver it, then adopt prevision
    # on rest of documents and deliver them - do it one by one
    sequence_string = delivery_check_sequence_string + '\
                      DecreaseSupplyDeliveryPackingListQuantity \
                      \
                      CheckSupplyDeliveryPackingListIsCalculating \
                      Tic \
                      CheckSupplyDeliveryPackingListIsDiverged \
                      AcceptDecisionSupplyDeliveryPackingList \
                      Tic \
                      CheckSupplyDeliveryPackingListIsSolved \
                      CheckSourcingDeliverySimulationDecreasedQuantity \
                      \
                      CheckProducedDeliveryPackingListIsConfirmed \
                      CheckProducedDeliveryPackingListIsDiverged\
                      \
                      CheckProducedReportIsConfirmed \
                      CheckProducedReportIsSolved \
                      \
                      CheckConsumedReportIsConfirmed \
                      CheckConsumedReportIsDiverged\
                      \
                      SetReadySupplyDeliveryPackingList \
                      StartSupplyDeliveryPackingList \
                      StopSupplyDeliveryPackingList \
                      DeliverSupplyDeliveryPackingList \
                      Tic \
                      \
                      CheckSourcingDeliverySimulationDecreasedQuantity \
                      \
                      CheckSupplyDeliveryPackingListIsDelivered \
                      CheckSupplyDeliveryPackingListIsSolved\
                      \
                      CheckProducedDeliveryPackingListIsConfirmed \
                      CheckProducedDeliveryPackingListIsDiverged\
                      \
                      CheckProducedReportIsConfirmed \
                      CheckProducedReportIsSolved\
                      \
                      CheckConsumedReportIsConfirmed \
                      CheckConsumedReportIsDiverged\
                      \
                      AdoptPrevisionProducedDeliveryPackingList \
                      Tic \
                      CheckProducedDeliveryPackingListIsSolved \
                      \
                      CheckProducedReportIsConfirmed \
                      CheckProducedReportIsDiverged\
                      \
                      CheckConsumedReportIsConfirmed \
                      CheckConsumedReportIsDiverged\
                      \
                      SetReadyProducedDeliveryPackingList \
                      StartProducedDeliveryPackingList \
                      StopProducedDeliveryPackingList \
                      DeliverProducedDeliveryPackingList \
                      Tic \
                      \
                      CheckSourcingDeliverySimulationDecreasedQuantity \
                      \
                      CheckProducedDeliveryPackingListIsDelivered \
                      CheckProducedDeliveryPackingListIsSolved\
                      \
                      CheckSupplyDeliveryPackingListIsDelivered \
                      CheckSupplyDeliveryPackingListIsSolved\
                      \
                      CheckProducedReportIsConfirmed \
                      CheckProducedReportIsDiverged\
                      \
                      CheckConsumedReportIsConfirmed \
                      CheckConsumedReportIsDiverged\
                      \
                      AdoptPrevisionProducedReport \
                      Tic \
                      CheckProducedReportIsSolved \
                      \
                      CheckConsumedReportIsConfirmed \
                      CheckConsumedReportIsDiverged\
                      \
                      SetReadyProducedReport \
                      StartProducedReport \
                      StopProducedReport \
                      DeliverProducedReport \
                      Tic \
                      \
                      CheckSourcingDeliverySimulationDecreasedQuantity \
                      \
                      CheckProducedDeliveryPackingListIsDelivered \
                      CheckProducedDeliveryPackingListIsSolved\
                      \
                      CheckSupplyDeliveryPackingListIsDelivered \
                      CheckSupplyDeliveryPackingListIsSolved \
                      \
                      CheckProducedReportIsDelivered \
                      CheckProducedReportIsSolved\
                      \
                      CheckConsumedReportIsConfirmed \
                      CheckConsumedReportIsDiverged\
                      \
                      AdoptPrevisionConsumedReport \
                      Tic \
                      CheckProducedReportIsSolved \
                      \
                      SetReadyConsumedReport \
                      StartConsumedReport \
                      StopConsumedReport \
                      DeliverConsumedReport \
                      Tic \
                      \
                      CheckSourcingDeliverySimulationDecreasedQuantity \
                      \
                      CheckProducedDeliveryPackingListIsDelivered \
                      CheckProducedDeliveryPackingListIsSolved\
                      \
                      CheckSupplyDeliveryPackingListIsDelivered \
                      CheckSupplyDeliveryPackingListIsSolved\
                      \
                      CheckProducedReportIsDelivered \
                      CheckProducedReportIsSolved\
                      \
                      CheckConsumedReportIsDelivered \
                      CheckConsumedReportIsSolved\
                      \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestProductionDelivery))
  return suite
