##############################################################################
#
# Copyright (c) 2005-2007 Nexedi SARL and Contributors. All Rights Reserved.
#                    Aurelien Calonne <aurel@nexedi.com>
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


# import requested python module
import os
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.DCWorkflow.DCWorkflow import Unauthorized, ValidationFailed
from Testing.ZopeTestCase.PortalTestCase import PortalTestCase
from Products.ERP5Banking.tests.TestERP5BankingMixin import TestERP5BankingMixin

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

# Define how to launch the script if we don't use runUnitTest script
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))
  

class TestERP5BankingCashSortingIncident(TestERP5BankingMixin, ERP5TypeTestCase):
  """
    This class is a unit test to check the module of Incident
  """

  login = PortalTestCase.login

  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet

  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingCashSortingIncident"

  def getCashSortingIncidentModule(self):
    """
    Return the Cash Transer Module
    """
    return getattr(self.getPortal(), 'incident_module', None)


  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    self.initDefaultVariable()
    self.cash_sorting_incident_module = self.getCashSortingIncidentModule()
    self.createManagerAndLogin()
    self.createFunctionGroupSiteCategory(site_list=['paris'])
    # create resources
    self.createBanknotesAndCoins()
    self.vault = self.paris.surface.banque_interne
    self.incoming_vault = self.paris.surface.banque_interne.guichet_1.encaisse_des_billets_et_monnaies.entrante
    self.outgoing_vault = self.paris.surface.banque_interne.guichet_1.encaisse_des_billets_et_monnaies.sortante
    self.checkUserFolderType()
    self.organisation = self.organisation_module.newContent(id='baobab_org', portal_type='Organisation',
                          function='banking', group='baobab',  site='testsite/paris')
    # define the user
    user_dict = {
        'super_user' : [['Manager'], self.organisation, 'banking/comptable', 'baobab', 'testsite/paris/surface/banque_interne/guichet_1']
      }
    self.createERP5Users(user_dict)
    self.logout()
    self.login('super_user')
    # open counter date
    self.openCounterDate(site=self.paris)
    self.openCounter(site=self.vault)

  def stepDeleteCashSortingIncident(self, sequence=None, sequence_list=None, **kwd):
    """
    Set the debit required
    """
    self.cash_sorting_incident_module.manage_delObjects(['cash_sorting_incident_1',])

  def stepDelOutgoingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Delete the invalid cash transfer line previously create
    """
    self.cash_sorting_incident.deleteContent('valid_line_2')

  def stepDelIncomingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Delete the invalid cash transfer line previously create
    """
    self.cash_sorting_incident.deleteContent('valid_line_1')

  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    self.assertEqual(self.cash_sorting_incident_module.getPortalType(), 'Incident Module')
    self.assertEqual(len(self.cash_sorting_incident_module.objectValues()), 0)

  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.incoming_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.incoming_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.incoming_vault.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.incoming_vault.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.outgoing_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.outgoing_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.outgoing_vault.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.outgoing_vault.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)


  def stepCreateCashSortingIncident(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a cash transfer document and check it
    """
    self.cash_sorting_incident = self.cash_sorting_incident_module.newContent(
                                        id='cash_sorting_incident_1', 
                                        portal_type='Incident', 
                                        description='test',
                                        incident_type = "cash_sorting_incident",
                                        resource_value=self.currency_1,
                                        source_total_asset_price=52400.0,)
    self.stepTic()
    # Check it
    self.assertEqual(len(self.cash_sorting_incident_module.objectValues()), 1)
    self.setDocumentSourceReference(self.cash_sorting_incident)
    self.assertNotEqual(self.cash_sorting_incident.getSourceReference(), '')
    self.assertNotEqual(self.cash_sorting_incident.getSourceReference(), None)
    self.cash_sorting_incident = getattr(self.cash_sorting_incident_module, 'cash_sorting_incident_1')
    self.assertEqual(self.cash_sorting_incident.getPortalType(), 'Incident')
    self.assertEqual(self.cash_sorting_incident.getSource(), None)
    self.assertEqual(self.cash_sorting_incident.getDestination(), None)

  def stepCreateIncomingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash transfer line 1 with banknotes of 10000 and check it has been well created
    """
    self.addCashLineToDelivery(self.cash_sorting_incident, 'valid_line_1', 'Incoming Incident Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/valid') + self.variation_list,
            self.quantity_10000)
    self.stepTic()

    self.assertEqual(len(self.cash_sorting_incident.objectValues()), 1)
    self.valid_line_1 = getattr(self.cash_sorting_incident, 'valid_line_1')
    self.assertEqual(self.valid_line_1.getPortalType(), 'Incoming Incident Line')
    self.assertEqual(self.valid_line_1.getResourceValue(), self.billet_10000)
    self.assertEqual(self.valid_line_1.getPrice(), 10000.0)
    self.assertEqual(self.valid_line_1.getQuantityUnit(), 'unit')
    self.assertEqual(len(self.valid_line_1.objectValues()), 2)
    for variation in self.variation_list:
      cell = self.valid_line_1.getCell('emission_letter/p', variation, 'cash_status/valid')
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getBaobabSourceValue(), None)
      self.assertEqual(cell.getBaobabDestination(), None)
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      if cell.getId() == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCheckSubTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the amount after the creation of cash transfer line 1
    """
    self.assertEqual(len(self.cash_sorting_incident.objectValues()), 1)
    self.assertEqual(self.cash_sorting_incident.getTotalQuantity(), 5.0)
    self.assertEqual(self.cash_sorting_incident.getTotalPrice(), 10000 * 5.0)


  def stepCreateOutgoingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash transfer line 2 wiht coins of 200 and check it has been well created
    """
    self.addCashLineToDelivery(self.cash_sorting_incident, 'valid_line_2', 'Outgoing Incident Line', self.piece_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/valid') + self.variation_list,
            self.quantity_200)
    self.stepTic()

    self.assertEqual(len(self.cash_sorting_incident.objectValues()), 2)
    self.valid_line_2 = getattr(self.cash_sorting_incident, 'valid_line_2')
    self.assertEqual(self.valid_line_2.getPortalType(), 'Outgoing Incident Line')
    self.assertEqual(self.valid_line_2.getResourceValue(), self.piece_200)
    self.assertEqual(self.valid_line_2.getPrice(), 200.0)
    self.assertEqual(self.valid_line_2.getQuantityUnit(), 'unit')
    self.assertEqual(len(self.valid_line_2.objectValues()), 2)
    for variation in self.variation_list:
      cell = self.valid_line_2.getCell('emission_letter/p', variation, 'cash_status/valid')
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getBaobabSource(), None)
      self.assertEqual(cell.getBaobabDestinationValue(), None)
      if cell.getId() == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 5.0)
      elif cell.getId() == 'movement_0_1_0':
        self.assertEqual(cell.getQuantity(), 7.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepTryDeliverCashSortingIncidentWithTwoDifferentLines(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    self.cash_sorting_incident.setSourceTotalAssetPrice('172400.0')
    self.assertWorkflowTransitionFails(object=self.cash_sorting_incident, transition_id='deliver_action',
                                       workflow_id='incident_workflow', error_message="You can't have excess and deficit on the same document.")
    self.stepTic()
    self.assertEqual(self.cash_sorting_incident.getSimulationState(), 'ordered')

  def stepTryDeliverCashSortingIncidentWithBadPrice(self, sequence=None, sequence_list=None, **kwd):
    """
    Try to confirm the cash transfer with a bad cash transfer line and
    check the try of confirm the cash transfer with the invalid line has failed
    """
    self.assertWorkflowTransitionFails(object=self.cash_sorting_incident, transition_id='deliver_action',
                                        workflow_id='incident_workflow',
                                        error_message="Price differs between document and cash detail.")
    self.stepTic()
    self.assertEqual(self.cash_sorting_incident.getSimulationState(), 'ordered')


  def stepCheckTotalIncoming(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the total after the creation of the two cash transfer lines
    """
    self.assertEqual(len(self.cash_sorting_incident.objectValues()), 1)
    self.assertEqual(self.cash_sorting_incident.getTotalQuantity(), 5.0)
    self.assertEqual(self.cash_sorting_incident.getTotalPrice(), 10000 * 5.0)

  def stepCheckTotalOutgoing(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the total after the creation of the two cash transfer lines
    """
    self.assertEqual(len(self.cash_sorting_incident.objectValues()), 1)
    self.assertEqual(self.cash_sorting_incident.getTotalQuantity(), 12.0)
    self.assertEqual(self.cash_sorting_incident.getTotalPrice(), 200 * 12.0)

  def stepSetIncomingTotalAssetPrice(self, sequence=None, sequence_list=None, **kwd):
    self.cash_sorting_incident.setSourceTotalAssetPrice('50000.0')

  def stepSetOutgoingTotalAssetPrice(self, sequence=None, sequence_list=None, **kwd):
    self.cash_sorting_incident.setSourceTotalAssetPrice('2400.0')

  def stepPlanCashSortingIncident(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the cash transfer and check it
    """
    self.workflow_tool.doActionFor(self.cash_sorting_incident, 'plan_action', wf_id='incident_workflow')
    self.stepTic()

    state = self.cash_sorting_incident.getSimulationState()
    self.assertEqual(state, 'planned')

  def stepOrderCashSortingIncident(self, sequence=None, sequence_list=None, **kwd):
    """
    Order the cash transfer and check it
    """
    self.cash_sorting_incident.setSource(self.vault.getRelativeUrl())
    self.workflow_tool.doActionFor(self.cash_sorting_incident, 'order_action', wf_id='incident_workflow')
    self.assertEqual(self.cash_sorting_incident.getSimulationState(), 'ordered')

  def stepConfirmCashSortingIncident(self, sequence=None, sequence_list=None, **kwd):
    """
    Archive the cash transfer with a good user
    and check that the archive of a cash tranfer have achieved
    """
    self.workflow_tool.doActionFor(self.cash_sorting_incident, 'confirm_action', wf_id='incident_workflow')
    self.stepTic()

    state = self.cash_sorting_incident.getSimulationState()
    self.assertEqual(state, 'confirmed')

  def stepDeliverCashSortingIncident(self, sequence=None, sequence_list=None, **kwd):
    """
    Archive the cash transfer with a good user
    and check that the archive of a cash tranfer have achieved
    """
    self.cash_sorting_incident.deliver()
    self.stepTic()

    state = self.cash_sorting_incident.getSimulationState()
    self.assertEqual(state, 'delivered')
    # Check we don't have more line than required
    self.assertEqual(len(self.cash_sorting_incident.objectIds()), 1)
    
  def stepCheckFinalIncomingInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the final, nothing should have changed
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.incoming_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.incoming_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.incoming_vault.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.incoming_vault.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.outgoing_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.outgoing_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.outgoing_vault.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.outgoing_vault.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)

  def stepCheckFinalOutgoingInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the final, nothing should have changed
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.incoming_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.incoming_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.incoming_vault.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.incoming_vault.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.outgoing_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.outgoing_vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.outgoing_vault.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.outgoing_vault.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 0.0)

  def stepCreateOutgoingInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Create an inventory for outgoing lines
    """
    inventory_dict_line = {'id' : 'inventory_line',
                           'resource': self.piece_200,
                           'variation_id': ('emission_letter', 'cash_status', 'variation'),
                           'variation_value': ('emission_letter/p', 'cash_status/valid') + self.variation_list,
                           'quantity': self.quantity_200}
    self.createCashInventory(source=None, destination=self.outgoing_vault, currency=self.currency_1,
                             line_list=[inventory_dict_line,])

  def stepCheckOutgoingInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.incoming_vault.getRelativeUrl(),
                                                              resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.incoming_vault.getRelativeUrl(),
                                                             resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.incoming_vault.getRelativeUrl(),
                                                              resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.incoming_vault.getRelativeUrl(),
                                                             resource = self.piece_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.outgoing_vault.getRelativeUrl(),
                                                              resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.outgoing_vault.getRelativeUrl(),
                                                             resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.outgoing_vault.getRelativeUrl(),
                                                              resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getAvailableInventory(node=self.outgoing_vault.getRelativeUrl(),
                                                             resource = self.piece_200.getRelativeUrl()), 12.0)        
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.outgoing_vault.getRelativeUrl(),
                                                             resource = self.piece_200.getRelativeUrl()), 0.0)


  def stepDeliverCashSortingIncidentFails(self, sequence=None, sequence_list=None, **kwd):
    """
    Try if we get Insufficient balance
    """
    message = self.assertWorkflowTransitionFails(self.cash_sorting_incident,
                                                 'incident_workflow','deliver_action')
    self.failUnless(message.find('Insufficient balance')>=0)

  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingCashSortingIncident(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run: return
    sequence_list = SequenceList()
    # define the sequence with incoming line
    sequence_string_1 = 'Tic CheckObjects Tic CheckInitialInventory ' \
                        + 'CreateCashSortingIncident ' \
                        + 'PlanCashSortingIncident Tic ' \
                        + 'OrderCashSortingIncident Tic ' \
                        + 'CreateIncomingLine CheckSubTotal ' \
                        + 'CreateOutgoingLine ' \
                        + 'TryDeliverCashSortingIncidentWithTwoDifferentLines DelOutgoingLine Tic ' \
                        + 'TryDeliverCashSortingIncidentWithBadPrice ' \
                        + 'Tic CheckTotalIncoming ' \
                        + 'SetIncomingTotalAssetPrice ' \
                        + 'DeliverCashSortingIncident ' \
                        + 'Tic ' \
                        + 'CheckFinalIncomingInventory '
    sequence_list.addSequenceString(sequence_string_1)
    # define the sequence with outgoing line
    sequence_string_2 = 'Tic DeleteCashSortingIncident Tic CheckInitialInventory ' \
                        + 'CreateCashSortingIncident ' \
                        + 'PlanCashSortingIncident Tic ' \
                        + 'OrderCashSortingIncident Tic ' \
                        + 'CreateIncomingLine CheckSubTotal ' \
                        + 'CreateOutgoingLine ' \
                        + 'TryDeliverCashSortingIncidentWithTwoDifferentLines DelIncomingLine Tic ' \
                        + 'TryDeliverCashSortingIncidentWithBadPrice ' \
                        + 'Tic CheckTotalOutgoing ' \
                        + 'SetOutgoingTotalAssetPrice ' \
                        + 'DeliverCashSortingIncidentFails Tic ' \
                        + 'CreateOutgoingInventory Tic CheckOutgoingInventory ' \
                        + 'DeliverCashSortingIncident ' \
                        + 'Tic ' \
                        + 'CheckFinalOutgoingInventory '
    sequence_list.addSequenceString(sequence_string_2)
    # play the sequence
    sequence_list.play(self)

# define how we launch the unit test
if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestERP5BankingCashSortingIncident))
    return suite
