
##############################################################################
#
# Copyright (c) 2006-2010 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5Type.tests.Sequence import SequenceList
from erp5.component.module.TestERP5BankingMixin import TestERP5BankingMixin

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'


class TestERP5BankingCheckbookReception(TestERP5BankingMixin):
  """
    This class is a unit test to check the module of Cash Transfer

    Here are the following step that will be done in the test :

    XXX to be completed

  """


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
    self.traveler_check_model = self.createTravelerCheckModel('traveler_check_model')
    self.createCheckAndCheckbookModel()
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
    self.loginByUserName('super_user')

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


  def stepCreateCheckbookReception(self, sequence=None, sequence_list=None,
                                   id='checkbook_reception', imported=0, **kwd):
    """
    Create a checkbook reception document and check it
    """
    # Checkbook reception
    checkbook_reception = self.checkbook_reception_module.newContent(
                     id=id, portal_type='Checkbook Reception',
                     source_value=None, destination_value=self.destination_site,
                     resource_value=self.currency_1,
                     description='test',
                     start_date=self.date,
                     imported=imported)
    setattr(self, id, checkbook_reception)
    # get the checkbook reception document
    self.checkbook_reception = getattr(self.checkbook_reception_module, id)
    # check its portal type
    self.assertEqual(self.checkbook_reception.getPortalType(), 'Checkbook Reception')
    # check that its source is caisse_1
    self.assertEqual(self.checkbook_reception.getSource(), None)
    # check that its destination is caisse_2
    if imported:
      self.assertEqual(self.checkbook_reception.getBaobabDestination(), None)
    else:
      self.assertEqual(self.checkbook_reception.getBaobabDestination(),
                     'site/testsite/paris/caveau/auxiliaire/encaisse_des_billets_et_monnaies')
    return self.checkbook_reception

  def stepCreateCheckbookReception2(self, sequence=None, sequence_list=None, **kwd):
    self.stepCreateCheckbookReception(id='checkbook_reception2')

  def stepCreateCheckbookReception3(self, sequence=None, sequence_list=None, **kwd):
    self.stepCreateCheckbookReception(id='checkbook_reception3')

  def stepCreateCheckbookReception4(self, sequence=None, sequence_list=None, **kwd):
    self.stepCreateCheckbookReception(id='checkbook_reception4')

  def stepCreateCheckbookReception5(self, sequence=None, sequence_list=None, **kwd):
    self.stepCreateCheckbookReception(id='checkbook_reception5',
                                      imported=1)

  def stepCreateCheckbookReception6(self, sequence=None, sequence_list=None, **kwd):
    self.stepCreateCheckbookReception(id='checkbook_reception6')

  def stepCreateCheckAndCheckbookLineList2(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the checkbook
    """
    # Add a line for check and checkbook
    self.line_1 = self.checkbook_reception2.newContent(quantity=1,
                                 resource_value=self.checkbook_model_1,
                                 check_amount_value=self.checkbook_model_1.variant_1,
                                 destination_payment_value=self.bank_account_1,
                                 reference_range_min='0000050',
                                 reference_range_max='0000099',
                                 )

  def stepCreateCheckAndCheckbookLineList3(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the checkbook
    """
    # Add a line for check and checkbook
    self.line_1 = self.checkbook_reception3.newContent(quantity=1,
                                 resource_value=self.checkbook_model_1,
                                 check_amount_value=self.checkbook_model_1.variant_1,
                                 destination_payment_value=self.bank_account_1,
                                 reference_range_min='0000150',
                                 reference_range_max='0000199',
                                 )

  def stepCreateCheckAndCheckbookLineList4(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the checkbook
    """
    # This is not required to create checkbook items, they will be
    # automatically created with the confirm action worfklow transition

    # Add a line for check and checkbook
    self.line_1 = self.checkbook_reception4.newContent(quantity=1,
                                 resource_value=self.checkbook_model_1,
                                 check_amount_value=self.checkbook_model_1.variant_1,
                                 destination_payment_value=self.bank_account_1,
                                 reference_range_min='0000101',
                                 reference_range_max='0000150',
                                 )

  def stepCreateCheckAndCheckbookLineList5(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the checkbook
    """
    # This is not required to create checkbook items, they will be
    # automatically created with the confirm action worfklow transition

    # Add a line for check and checkbook
    self.line_1 = self.checkbook_reception5.newContent(quantity=1,
                                 resource_value=self.checkbook_model_1,
                                 check_amount_value=self.checkbook_model_1.variant_1,
                                 destination_payment_value=self.bank_account_1,
                                 reference_range_min='0000200',
                                 reference_range_max='0000249',
                                 )

  def stepCreateCheckAndCheckbookLineList6(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the checkbook
    """
    # This is not required to create checkbook items, they will be
    # automatically created with the confirm action worfklow transition

    # Add a line for check and checkbook
    self.line_1 = self.checkbook_reception6.newContent(quantity=1,
                                 resource_value=self.checkbook_model_2,
                                 check_amount_value=self.checkbook_model_2.variant_1,
                                 destination_payment_value=self.bank_account_1,
                                 reference_range_min='0000200',
                                 reference_range_max='0000249',
                                 )


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
                                 reference_range_min='0000001',
                                 reference_range_max='0000050'
                                 )
    self.line_2 = self.checkbook_reception.newContent(quantity=1,
                                 resource_value=self.check_model_1,
                                 check_amount_value=None,
                                 destination_payment_value=self.bank_account_2,
                                 reference_range_min='0000051',
                                 reference_range_max='0000051'
                                 )

  def stepCheckItemsCreated(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the checkbook
    """
    self.checkbook_1 = None
    self.check_1 = None

    for line in self.checkbook_reception.objectValues():
      aggregate_value_list = line.getAggregateValueList()
      self.assertEqual(len(aggregate_value_list), 1)
      aggregate_value = aggregate_value_list[0]
      if aggregate_value.getPortalType()=='Checkbook':
        self.checkbook_1 = aggregate_value
      elif aggregate_value.getPortalType()=='Check':
        self.check_1 = aggregate_value
        # Make sure new check is in draft mode
        self.assertEqual(self.check_1.getSimulationState(), 'draft')
    self.assertNotEquals(None, self.checkbook_1)
    self.assertNotEquals(None, self.check_1)
    # Make sure that all checks inside checkbook are create
    self.assertEqual(len(self.checkbook_1.objectValues()), 50)
    # Make sure that all checks inside checkbook are not issued yet
    self.assertEqual(self.checkbook_1.objectValues()[0].getSimulationState(),
                      'draft')

  def stepConfirmCheckbookReception(self, sequence=None, sequence_list=None, **kwd):
    """
    confirm the monetary reception
    """
    state = self.checkbook_reception.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'empty')
    self.workflow_tool.doActionFor(self.checkbook_reception, 'confirm_action', wf_id='checkbook_reception_workflow')
    self.assertEqual(self.checkbook_reception.getSimulationState(), 'confirmed')
    workflow_history = self.workflow_tool.getInfoFor(ob=self.checkbook_reception, name='history', wf_id='checkbook_reception_workflow')
    # check len of len workflow history is 6
    self.assertEqual(len(workflow_history), 3)

  def stepConfirmCheckbookReception2(self, sequence=None, sequence_list=None, **kwd):
    """
    confirm the monetary reception
    """
    self.workflow_tool.doActionFor(self.checkbook_reception2, 'confirm_action',
                                   wf_id='checkbook_reception_workflow')
    self.assertEqual(self.checkbook_reception2.getSimulationState(), 'confirmed')

  def stepConfirmCheckbookReception3(self, sequence=None, sequence_list=None, **kwd):
    """
    confirm the monetary reception
    """
    self.workflow_tool.doActionFor(self.checkbook_reception3, 'confirm_action',
                                   wf_id='checkbook_reception_workflow')
    self.assertEqual(self.checkbook_reception3.getSimulationState(), 'confirmed')

  def stepConfirmCheckbookReception4(self, sequence=None, sequence_list=None, **kwd):
    """
    confirm the monetary reception
    """
    self.workflow_tool.doActionFor(self.checkbook_reception4, 'confirm_action',
                                   wf_id='checkbook_reception_workflow')
    self.assertEqual(self.checkbook_reception4.getSimulationState(), 'confirmed')

  def stepConfirmCheckbookReception5(self, sequence=None, sequence_list=None, **kwd):
    """
    confirm the monetary reception
    """
    self.workflow_tool.doActionFor(self.checkbook_reception5, 'confirm_action',
                                   wf_id='checkbook_reception_workflow')
    self.assertEqual(self.checkbook_reception5.getSimulationState(), 'confirmed')

  def stepConfirmCheckbookReception6(self, sequence=None, sequence_list=None, **kwd):
    """
    confirm the monetary reception
    """
    self.workflow_tool.doActionFor(self.checkbook_reception6, 'confirm_action',
                                   wf_id='checkbook_reception_workflow')
    self.assertEqual(self.checkbook_reception6.getSimulationState(), 'confirmed')

  def stepDeliverCheckbookReception2Fails(self, sequence=None, sequence_list=None, **kwd):
    """
    confirm the monetary reception
    """
    msg = self.assertWorkflowTransitionFails(self.checkbook_reception2,
        'checkbook_reception_workflow', 'deliver_action')
    self.assertTrue(msg.find('The following references are already allocated')
                    >=0)
    self.assertTrue(msg.find('50')>=0)

  def stepDeliverCheckbookReception3(self, sequence=None, sequence_list=None, **kwd):
    """
    confirm the monetary reception
    """
    self.workflow_tool.doActionFor(self.checkbook_reception3, 'deliver_action',
                                   wf_id='checkbook_reception_workflow')
    self.assertEqual(self.checkbook_reception3.getSimulationState(), 'delivered')

  def stepDeliverCheckbookReception4Fails(self, sequence=None, sequence_list=None, **kwd):
    """
    confirm the monetary reception
    """
    msg = self.assertWorkflowTransitionFails(self.checkbook_reception4,
        'checkbook_reception_workflow', 'deliver_action')
    self.assertTrue(msg.find('The following references are already allocated')
                    >=0)
    self.assertTrue(msg.find('150')>=0)

  def stepDeliverCheckbookReception5(self, sequence=None, sequence_list=None, **kwd):
    """
    confirm the monetary reception
    """
    self.workflow_tool.doActionFor(self.checkbook_reception5, 'deliver_action',
                                   wf_id='checkbook_reception_workflow')
    self.assertEqual(self.checkbook_reception5.getSimulationState(), 'delivered')

  def stepDeliverCheckbookReception6(self, sequence=None, sequence_list=None, **kwd):
    """
    confirm the monetary reception
    """
    self.workflow_tool.doActionFor(self.checkbook_reception6, 'deliver_action',
                                   wf_id='checkbook_reception_workflow')
    self.assertEqual(self.checkbook_reception6.getSimulationState(), 'delivered')

  def stepDeliverCheckbookReception(self, sequence=None, sequence_list=None, **kw):
    """
    Deliver the monetary reception
    """
    state = self.checkbook_reception.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'confirmed')
    self.workflow_tool.doActionFor(self.checkbook_reception, 'deliver_action', wf_id='checkbook_reception_workflow')
    # execute tic
    self.tic()
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
    self.failIfDifferentSet(checkbook_object_list, [self.checkbook_1, self.check_1])
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(node=self.reception.getRelativeUrl())), 2)

  def stepCheckConfirmedCheckbookForImport(self, sequence=None, sequence_list=None, **kw):
    """
    Check cash checkbook in item table
    """
    checkbook = self.checkbook_reception5.objectValues()[0].getAggregateValue()
    self.assertEqual(checkbook.getValidationState(), 'confirmed')
    check = checkbook.objectValues()[0]
    self.assertEqual(check.getSimulationState(), 'confirmed')

  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingCheckbookReception(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
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

    # Make sure it is impossible to create a checkbook with a reference
    # wich is inside the range of another checkbook
    sequence_string = 'Tic ' \
                    + 'CreateCheckbookReception2 Tic ' \
                    + 'CreateCheckAndCheckbookLineList2 Tic ' \
                    + 'ConfirmCheckbookReception2 Tic ' \
                    + 'DeliverCheckbookReception2Fails Tic '
    sequence_list.addSequenceString(sequence_string)

    # Make sure it is impossible to create in the same time
    # two checkbooks with the same reference, so we must
    # do deliver without tic
    sequence_string = 'Tic ' \
                    + 'CreateCheckbookReception3 Tic ' \
                    + 'CreateCheckbookReception4 Tic ' \
                    + 'CreateCheckAndCheckbookLineList3 Tic ' \
                    + 'ConfirmCheckbookReception3 Tic ' \
                    + 'CreateCheckAndCheckbookLineList4 Tic ' \
                    + 'ConfirmCheckbookReception4 Tic ' \
                    + 'DeliverCheckbookReception3 Tic ' \
                    + 'DeliverCheckbookReception4Fails '
    sequence_list.addSequenceString(sequence_string)

    # Make sure that if we have an import, then everything
    # will be confirmed automatically
    sequence_string = 'Tic ' \
                    + 'CreateCheckbookReception5 Tic ' \
                    + 'CreateCheckAndCheckbookLineList5 Tic ' \
                    + 'ConfirmCheckbookReception5 Tic ' \
                    + 'DeliverCheckbookReception5 Tic ' \
                    + 'CheckConfirmedCheckbookForImport Tic '
    sequence_list.addSequenceString(sequence_string)

    # Check that it is possible to have 2 receptions on the same range for 2 different checkbook models
    sequence_string = 'Tic ' \
                    + 'CreateCheckbookReception6 Tic ' \
                    + 'CreateCheckAndCheckbookLineList6 Tic ' \
                    + 'ConfirmCheckbookReception6 Tic ' \
                    + 'DeliverCheckbookReception6 Tic'
    sequence_list.addSequenceString(sequence_string)

    # play the sequence
    sequence_list.play(self)

