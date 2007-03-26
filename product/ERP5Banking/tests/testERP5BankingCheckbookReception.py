##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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



class TestERP5BankingCheckbookReception(TestERP5BankingMixin, ERP5TypeTestCase):
  """
    This class is a unit test to check the module of Cash Transfer

    Here are the following step that will be done in the test :

    XXX to be completed

  """

  login = PortalTestCase.login

  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet


  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingCheckbookReception"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    # Set some variables :
    self.initDefaultVariable()
    # the cash inventory module
    self.checkbook_reception_module = self.getCheckbookReceptionModule()
    self.check_module = self.getCheckModule()
    self.checkbook_module = self.getCheckbookModule()
    self.checkbook_model_module = self.getCheckbookModelModule()

    self.createManagerAndLogin()
    self.createFunctionGroupSiteCategory()
    self.createBanknotesAndCoins()
    self.traveler_check_model = self.createTravelerCheckModel('traveler_check_model')
    self.checkbook_model_1 = self.createCheckbookModel('checkbook_model_1')
    self.check_model_1 = self.createCheckModel('check_model_1')
    self.reception = self.paris.caveau.auxiliaire.encaisse_des_billets_et_monnaies
    self.destination_site = self.paris
    self.checkUserFolderType()
    self.organisation = self.organisation_module.newContent(id='baobab_org', portal_type='Organisation',
                          function='banking', group='baobab',  site='testsite/paris')
    # define the user
    user_dict = {
        'super_user' : [['Manager'], self.organisation, 'banking/comptable', 'baobab', 'testsite/paris']
      }
    # call method to create this user
    self.createERP5Users(user_dict)
    self.logout()
    self.login('super_user')

    # create a person and a bank account
    self.person_1 = self.createPerson(id='person_1',
                                      first_name='Sebastien',
                                      last_name='Robin')
    self.bank_account_1 = self.createBankAccount(person=self.person_1,
                                                 account_id='bank_account_1',
                                                 currency=self.currency_1,
                                                 amount=100000)
    # create a person and a bank account
    self.person_2 = self.createPerson(id='person_2',
                                      first_name='Aurelien',
                                      last_name='Calonne')
    self.bank_account_2 = self.createBankAccount(person=self.person_2,
                                                 account_id='bank_account_1',
                                                 currency=self.currency_1,
                                                 amount=100000)


  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that CheckbookReception Module was created
    self.assertEqual(self.checkbook_reception_module.getPortalType(), 'Checkbook Reception Module')
    # check cash inventory module is empty
    self.assertEqual(len(self.checkbook_reception_module.objectValues()), 0)


  def stepCheckInitialCheckbookInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check initial cash checkbook on source
    """
    self.assertEqual(len(self.simulation_tool.getCurrentTrackingList(node=self.reception.getRelativeUrl())), 0)
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(node=self.reception.getRelativeUrl())), 0)


  def stepCreateCheckbookReception(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a checkbook reception document and check it
    """
    # Checkbook reception
    self.checkbook_reception = self.checkbook_reception_module.newContent(
                     id='checkbook_reception', portal_type='Checkbook Reception',
                     source_value=None, destination_value=self.destination_site,
                     resource_value=self.currency_1,
                     description='test',
                     start_date=self.date)
    # get the checkbook reception document
    self.checkbook_reception = getattr(self.checkbook_reception_module, 'checkbook_reception')
    # check its portal type
    self.assertEqual(self.checkbook_reception.getPortalType(), 'Checkbook Reception')
    # check that its source is caisse_1
    self.assertEqual(self.checkbook_reception.getSource(), None)
    # check that its destination is caisse_2
    self.assertEqual(self.checkbook_reception.getBaobabDestination(), 
                     'site/testsite/paris/caveau/auxiliaire/encaisse_des_billets_et_monnaies')


  def stepCreateCheckAndCheckbookLineList(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the checkbook
    """
    # This is not required to create checkbook items, they will be
    # automatically created with the confirm action worfklow transition

    # Add a line for check and checkbook
    self.line_1 = self.checkbook_reception.newContent(quantity=1,
                                 resource_value=self.checkbook_model_1,
                                 check_amount_value=self.checkbook_model_1.variant_1,
                                 destination_payment_value=self.bank_account_1,
                                 reference_range_min=1,
                                 reference_range_max=50
                                 )
    self.line_2 = self.checkbook_reception.newContent(quantity=1,
                                 resource_value=self.check_model_1,
                                 check_amount_value=None,
                                 destination_payment_value=self.bank_account_2,
                                 reference_range_min=51,
                                 reference_range_max=51
                                 )

  def stepCheckItemsCreated(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the checkbook
    """
    self.checkbook_1 = None
    self.check_1 = None

    for line in self.checkbook_reception.objectValues():
      aggregate_value_list = line.getAggregateValueList()
      self.assertEquals(len(aggregate_value_list),1)
      aggregate_value = aggregate_value_list[0]
      if aggregate_value.getPortalType()=='Checkbook':
        self.checkbook_1 = aggregate_value
      elif aggregate_value.getPortalType()=='Check':
        self.check_1 = aggregate_value
        # Make sure new check is in draft mode
        self.assertEquals(self.check_1.getSimulationState(),'draft')
    self.assertNotEquals(None,self.checkbook_1)
    self.assertNotEquals(None,self.check_1)
    # Make sure that all checks inside checkbook are create
    self.assertEquals(len(self.checkbook_1.objectValues()),50)
    # Make sure that all checks inside checkbook are not issued yet
    self.assertEquals(self.checkbook_1.objectValues()[0].getSimulationState(),
                      'draft')

  def stepConfirmCheckbookReception(self, sequence=None, sequence_list=None, **kwd):
    """
    confirm the monetary reception
    """
    state = self.checkbook_reception.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'draft')
    self.workflow_tool.doActionFor(self.checkbook_reception, 'confirm_action', wf_id='checkbook_reception_workflow')
    self.assertEqual(self.checkbook_reception.getSimulationState(), 'confirmed')
    workflow_history = self.workflow_tool.getInfoFor(ob=self.checkbook_reception, name='history', wf_id='checkbook_reception_workflow')
    # check len of len workflow history is 6
    self.assertEqual(len(workflow_history), 3)


  def stepDeliverCheckbookReception(self, sequence=None, sequence_list=None, **kw):
    """
    Deliver the monetary reception
    """
    state = self.checkbook_reception.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'confirmed')
    self.workflow_tool.doActionFor(self.checkbook_reception, 'deliver_action', wf_id='checkbook_reception_workflow')
    # execute tic
    self.stepTic()
    # get state of cash sorting
    state = self.checkbook_reception.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.checkbook_reception, name='history', wf_id='checkbook_reception_workflow')
    # check len of len workflow history is 6
    self.assertEqual(len(workflow_history), 5)


  def stepCheckFinalCheckbookInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check cash checkbook in item table
    """
    checkbook_list = self.simulation_tool.getCurrentTrackingList(node=self.reception.getRelativeUrl())
    self.assertEqual(len(checkbook_list), 2)
    # check we have cash checkbook 1
    checkbook_object_list = [x.getObject() for x in checkbook_list]
    self.failIfDifferentSet(checkbook_object_list,[self.checkbook_1,self.check_1])
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(node=self.reception.getRelativeUrl())), 2)

  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingCheckbookReception(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run: return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialCheckbookInventory ' \
                    + 'CreateCheckbookReception Tic ' \
                    + 'CreateCheckAndCheckbookLineList Tic ' \
                    + 'ConfirmCheckbookReception Tic ' \
                    + 'DeliverCheckbookReception Tic ' \
                    + 'CheckItemsCreated  ' \
                    + 'CheckFinalCheckbookInventory'
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
    suite.addTest(unittest.makeSuite(TestERP5BankingCheckbookReception))
    return suite
