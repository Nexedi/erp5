##############################################################################
#
# Copyright (c) 2005-2006 Nexedi SARL and Contributors. All Rights Reserved.
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
  

class TestERP5BankingAccountIncident(TestERP5BankingMixin, ERP5TypeTestCase):
  """
    This class is a unit test to check the module of Account Incident

    Here are the following step that will be done in the test :
  
    - before the test, we need to create some movements that will put resources in the source

    - create a cash transfer
    - check it has been created correctly
    - check source and destination (current == future)

    - create a "Note Line" (billetage)
    - check it has been created correctly
    - check the total amount

    - create a second Line
    - check it has been created correctly
    - check the total amount

    - create an invalid Line (quantity > available at source)
    - check that the system behaves correctly

    - pass "confirm_action" transition
    - check that the new state is confirmed
    - check that the source has been debited correctly (current < future)
    - check amount, lines, ...

    - pass "deliver_action" transition
    - check that the new state is delivered
    - check that the destination has been credited correctly (current == future)
  """

  login = PortalTestCase.login

  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet

  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingAccountIncident"


  def getBusinessTemplateList(self):
    """
      Return the list of business templates we need to run the test.
      This method is called during the initialization of the unit test by
      the unit test framework in order to know which business templates
      need to be installed to run the test on.
    """
    return ('erp5_base'
            , 'erp5_trade'
            , 'erp5_accounting'
            , 'erp5_banking_core' # erp5_banking_core contains all generic methods for banking
            , 'erp5_banking_inventory'
            , 'erp5_banking_cash' # erp5_banking_cash contains all method for cash transfer
            )

  def getAccountIncidentModule(self):
    """
    Return the Cash Transer Module
    """
    return getattr(self.getPortal(), 'account_incident_module', None)


  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    # Set some variables : 
    self.initDefaultVariable()
    # the cahs transfer module
    self.account_incident_module = self.getAccountIncidentModule()
    
    self.createManagerAndLogin()

    # create categories
    self.createFunctionGroupSiteCategory()

    # create resources
    self.createBanknotesAndCoins()

    # Before the test, we need to input the inventory
    
    inventory_dict_line_1 = {'id' : 'inventory_line_1',
                             'resource': self.billet_10000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/p', 'cash_status/valid') + self.variation_list,
                             'quantity': self.quantity_10000}
    
    inventory_dict_line_2 = {'id' : 'inventory_line_2',
                             'resource': self.piece_200,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/p', 'cash_status/valid') + self.variation_list,
                             'quantity': self.quantity_200}
    
    line_list = [inventory_dict_line_1, inventory_dict_line_2]
    self.vault = self.paris.surface.caisse_courante.encaisse_des_billets_et_monnaies
    self.createCashInventory(source=None, destination=self.vault, currency=self.currency_1,
                             line_list=line_list)

    # create a person and a bank account
    self.person_1 = self.createPerson(id='person_1',
                                      first_name='toto',
                                      last_name='titi')
    self.bank_account_1 = self.createBankAccount(person=self.person_1,
                                                 account_id='bank_account_1',
                                                 title = 'Bank Account 1',
                                                 currency=self.currency_1,                                                 
                                                 amount=100000)

    # now we need to create a user as Manager to do the test
    # in order to have an assigment defined which is used to do transition
    # Create an Organisation that will be used for users assignment
    self.checkUserFolderType()
    self.organisation = self.organisation_module.newContent(id='baobab_org', portal_type='Organisation',
                          function='banking', group='baobab',  site='testsite/paris')
    # define the user
    user_dict = {
        'super_user' : [['Manager'], self.organisation, 'banking/comptable', 'baobab', 'testsite/paris/surface/banque_interne/guichet_1']
      }
    # call method to create this user
    self.createERP5Users(user_dict)
    self.logout()
    self.login('super_user')

    # open counter date
    self.openCounterDate(site=self.paris)

  def stepCleanupObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Cleanup account_incident_module after a sequence execution so that
    stepCheckObjects can succeed.
    """
    self.account_incident_module.manage_delObjects(ids=[x for x in self.account_incident_module.objectIds()])

  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that AccountIncident Module was created
    self.assertEqual(self.account_incident_module.getPortalType(), 'Account Incident Module')
    # check cash transfer module is empty
    self.assertEqual(len(self.account_incident_module.objectValues()), 0)


  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in usual_cash
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200 in usual_cash
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 100000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 100000)


  def stepCreateAccountIncident(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a cash transfer document and check it
    """
    # Cash transfer has usual_cash for source, counter for destination, and a price cooreponding to the sum of banknote of 10000 abd coin of 200 ( (2+3) * 1000 + (5+7) * 200 )
    self.account_incident = self.account_incident_module.newContent(
                                          id='account_incident_1', 
                                          portal_type='Account Incident', 
                                          source_total_asset_price=52400.0,
                                          description='test',
                                          destination_payment_value=self.bank_account_1,
                                          resource_value=self.currency_1)
    # execute tic
    self.stepTic()
    # set source reference
    self.setDocumentSourceReference(self.account_incident)
    # check we have only one cash transfer
    self.assertEqual(len(self.account_incident_module.objectValues()), 1)
    # get the cash transfer document
    self.account_incident = getattr(self.account_incident_module, 'account_incident_1')
    # check its portal type
    self.assertEqual(self.account_incident.getPortalType(), 'Account Incident')
    self.assertEqual(self.account_incident.getDestinationPaymentTitle(), 'Bank Account 1')
    # check that its destination is counter
    self.assertEqual(self.account_incident.getSource(), 'site/testsite/paris')
    self.assertEqual(self.account_incident.getDestination(), None)
    # check source reference
    self.assertNotEqual(self.account_incident.getSourceReference(), '')
    self.assertNotEqual(self.account_incident.getSourceReference(), None)
    

  def stepCreateIncomingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash transfer line 1 with banknotes of 10000 and check it has been well created
    """
    # create the cash transfer line
    self.addCashLineToDelivery(self.account_incident, 'valid_line_1', 'Incoming Account Incident Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/valid') + self.variation_list,
            self.quantity_10000)
    # execute tic
    self.stepTic()
    # check there is only one line created
    self.assertEqual(len(self.account_incident.objectValues(
                         portal_type='Incoming Account Incident Line')), 1)
    # get the cash transfer line
    self.valid_line_1 = getattr(self.account_incident, 'valid_line_1')
    # check its portal type
    self.assertEqual(self.valid_line_1.getPortalType(), 'Incoming Account Incident Line')
    # check the resource is banknotes of 10000
    self.assertEqual(self.valid_line_1.getResourceValue(), self.billet_10000)
    # chek the value of the banknote
    self.assertEqual(self.valid_line_1.getPrice(), 10000.0)
    # check the unit of banknote
    self.assertEqual(self.valid_line_1.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_line_1.objectValues()), 2)
    # now check for each variation (years 1992 and 2003)
    for variation in self.variation_list:
      # get the delivery cell
      cell = self.valid_line_1.getCell('emission_letter/p', variation, 'cash_status/valid')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      # check the source vault is usual_cash
      self.assertEqual(cell.getBaobabSourceValue(), None)
      # check the destination vault is counter
      self.assertEqual(cell.getBaobabDestination(), self.vault.getRelativeUrl())
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote for year 1992 is 2
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity of banknote for year 2003 is 3
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCheckSubTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the amount after the creation of cash transfer line 1
    """
    # Check quantity of banknotes (2 for 1992 and 3 for 2003)
    self.assertEqual(self.account_incident.getTotalQuantity(), 5.0)
    # Check the total price
    self.assertEqual(self.account_incident.getTotalPrice(), 10000 * 5.0)


  def stepCreateOutgoingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash transfer line 2 wiht coins of 200 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.account_incident, 'valid_line_2', 'Outgoing Account Incident Line', self.piece_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/valid') + self.variation_list,
            self.quantity_200)
    # execute tic
    self.stepTic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.account_incident.objectValues(
                         portal_type='Outgoing Account Incident Line')), 1)
    # get the second cash transfer line
    self.valid_line_2 = getattr(self.account_incident, 'valid_line_2')
    # check portal types
    self.assertEqual(self.valid_line_2.getPortalType(), 'Outgoing Account Incident Line')
    # check the resource is coin of 200
    self.assertEqual(self.valid_line_2.getResourceValue(), self.piece_200)
    # check the value of coin
    self.assertEqual(self.valid_line_2.getPrice(), 200.0)
    # check the unit of coin
    self.assertEqual(self.valid_line_2.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_line_2.objectValues()), 2)
    for variation in self.variation_list:
      # get the delivery  cell
      cell = self.valid_line_2.getCell('emission_letter/p', variation, 'cash_status/valid')
      # check the portal type
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      # check the source vault is usual_cash
      self.assertEqual(cell.getBaobabSource(), self.vault.getRelativeUrl())
      # check the destination vault is counter
      self.assertEqual(cell.getBaobabDestinationValue(), None)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity for coin for year 1992 is 5
        self.assertEqual(cell.getQuantity(), 5.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity for coin for year 2003 is 7
        self.assertEqual(cell.getQuantity(), 7.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepTryConfirmAccountIncidentWithTwoDifferentLines(self, sequence=None, sequence_list=None, **kwd):
    """
    """
    # fix amount (10000 * 5.0 + 200 * 12.0 + 5000 * 24)
    self.account_incident.setSourceTotalAssetPrice('172400.0')
    # try to do the workflow action "confirm_action', cath the exception ValidationFailed raised by workflow transition 
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.account_incident, 'confirm_action', wf_id='account_incident_workflow')
    # execute tic
    self.stepTic()
    # get state of the cash transfer
    state = self.account_incident.getSimulationState()
    # check the state is draft
    self.assertEqual(state, 'draft')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.account_incident, name='history', wf_id='account_incident_workflow')
    # check its len is 2
    self.assertEqual(len(workflow_history), 2)
    # check we get an "Insufficient balance" message in the workflow history because of the invalid line
    msg = workflow_history[-1]['error_message']
    self.assertEqual("You can't have excess and deficit on the document.", "%s" %(msg,))


  def stepDelOutgoingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Delete the invalid cash transfer line previously create
    """
    self.account_incident.deleteContent('valid_line_2')


  def stepTryConfirmAccountIncidentWithBadPrice(self, sequence=None, sequence_list=None, **kwd):
    """
    Try to confirm the cash transfer with a bad cash transfer line and
    check the try of confirm the cash transfer with the invalid line has failed
    """
    # try to do the workflow action "confirm_action', cath the exception ValidationFailed raised by workflow transition 
    self.assertRaises(ValidationFailed, self.workflow_tool.doActionFor, self.account_incident, 'confirm_action', wf_id='account_incident_workflow')
    # execute tic
    self.stepTic()
    # get state of the cash transfer
    state = self.account_incident.getSimulationState()
    # check the state is draft
    self.assertEqual(state, 'draft')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.account_incident, name='history', wf_id='account_incident_workflow')
    # check its len is 2
    self.assertEqual(len(workflow_history), 3)
    # check we get an "Insufficient balance" message in the workflow history because of the invalid line
    msg = workflow_history[-1]['error_message']
    self.assertEqual("Price differs between document and resource.", "%s" %(msg,))


  def stepCheckTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the total after the creation of the two cash transfer lines
    """
    # Check number of lines (line1 + line2)
    self.assertEqual(len(self.account_incident.objectValues(
                         portal_type='Incoming Account Incident Line')), 1)
    # Check quantity, banknotes : 2 for 1992 and 3 for 2003, coin : 5 for 1992 and 7 for 2003
    self.assertEqual(self.account_incident.getTotalQuantity(), 5.0)
    # check the total price
    self.assertEqual(self.account_incident.getTotalPrice(), 10000 * 5.0)


  def stepConfirmAccountIncident(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the cash transfer and check it
    """
    # fix amount (10000 * 5.0 + 200 * 12.0)
    self.account_incident.setSourceTotalAssetPrice('50000.0')
    # do the Workflow action
    self.workflow_tool.doActionFor(self.account_incident, 'confirm_action', wf_id='account_incident_workflow')
    # execute tic
    self.stepTic()
    # get state
    state = self.account_incident.getSimulationState()
    # check state is confirmed
    self.assertEqual(state, 'confirmed')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.account_incident, name='history', wf_id='account_incident_workflow')
    # check len of workflow history is 4
    self.assertEqual(len(workflow_history), 5)


  def stepDeliverAccountIncident(self, sequence=None, sequence_list=None, **kwd):
    """
    Deliver the cash transfer with a good user
    and check that the archive of a cash tranfer have achieved
    """
    # do the workflow transition "archive_action"
    self.workflow_tool.doActionFor(self.account_incident, 'deliver_action', wf_id='account_incident_workflow')
    # execute tic
    self.stepTic()
    # get state of cash transfer
    state = self.account_incident.getSimulationState()
    # check that state is archiveed
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.account_incident, name='history', wf_id='account_incident_workflow')
    # check len of len workflow history is 6
    self.assertEqual(len(workflow_history), 7)
    

  def stepCheckFinalInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the final, nothing should have changed
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in usual_cash
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 10.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 10.0)
    # check we have 12 coin of 200 in usual_cash
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.vault.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.vault.getRelativeUrl(), resource = self.piece_200.getRelativeUrl()), 12.0)
    # check the inventory of the bank account
    self.assertEqual(self.simulation_tool.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl(),resource=self.currency_1.getRelativeUrl()), 150000)
    self.assertEqual(self.simulation_tool.getFutureInventory(payment=self.bank_account_1.getRelativeUrl(),resource=self.currency_1.getRelativeUrl()), 150000)


  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingAccountIncident(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run: return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventory ' \
                    + 'CreateAccountIncident ' \
                    + 'CreateIncomingLine CheckSubTotal ' \
                    + 'CreateOutgoingLine ' \
                    + 'TryConfirmAccountIncidentWithTwoDifferentLines DelOutgoingLine Tic ' \
                    + 'TryConfirmAccountIncidentWithBadPrice ' \
                    + 'Tic CheckTotal ' \
                    + 'ConfirmAccountIncident ' \
                    + 'DeliverAccountIncident ' \
                    + 'CheckFinalInventory '
    sequence_list.addSequenceString(sequence_string)
    # play the sequence
    sequence_list.play(self)

# define how we launch the unit test
if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestERP5BankingAccountIncident))
    return suite
