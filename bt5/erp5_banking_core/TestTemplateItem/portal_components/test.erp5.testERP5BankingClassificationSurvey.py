
##############################################################################
#
# Copyright (c) 2006-2010 Nexedi SA and Contributors. All Rights Reserved.
#                   Aurelien Calonne <aurel@nexedi.com>
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


class TestERP5BankingClassificationSurvey(TestERP5BankingMixin):


  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet


  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingClassificationSurvey"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    self.initDefaultVariable()
    # Set some variables :
    self.classification_survey_module = self.getClassificationSurveyModule()

    # Create a user and login as manager to populate the erp5 portal with objects for tests.
    self.createManagerAndLogin()

    self.createFunctionGroupSiteCategory()

    inventory_dict_line_1 = {'id' : 'inventory_line_1',
                             'resource': self.billet_10000,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/not_defined', 'cash_status/not_defined') + self.variation_list,
                             'quantity': self.quantity_10000}

    inventory_dict_line_2 = {'id' : 'inventory_line_2',
                             'resource': self.billet_200,
                             'variation_id': ('emission_letter', 'cash_status', 'variation'),
                             'variation_value': ('emission_letter/not_defined', 'cash_status/not_defined') + self.variation_list,
                             'quantity': self.quantity_200}


    self.line_list = line_list = [inventory_dict_line_1, inventory_dict_line_2]
    self.encaisse_des_billets_ventiles_et_detruits = self.paris.caveau.auxiliaire.encaisse_des_billets_ventiles_et_detruits
    self.encaisse_des_billets_retires_de_la_circulation = self.paris.caveau.serre.encaisse_des_billets_retires_de_la_circulation
    self.encaisse_externe = self.paris.caveau.auxiliaire.encaisse_des_externes

    self.createCashInventory(source=None, destination=self.encaisse_des_billets_ventiles_et_detruits, currency=self.currency_1,
                             line_list=line_list)

    # now we need to create a user as Manager to do the test
    # in order to have an assigment defined which is used to do transition
    # Create an Organisation that will be used for users assignment
    self.checkUserFolderType()
    self.organisation = self.organisation_module.newContent(id='paris', portal_type='Organisation',
                          function='banking', group='baobab',  site='testsite/paris')
    # define the user
    user_dict = {
        'super_user' : [['Manager'], self.organisation, 'banking/comptable', 'baobab', 'testsite/paris']
      }
    # call method to create this user
    self.createERP5Users(user_dict)
    self.logout()
    self.loginByUserName('super_user')
    self.openCounterDate(site=self.testsite.paris)



  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that ClassificationSurvey Module was created
    self.assertEqual(self.classification_survey_module.getPortalType(), 'Classification Survey Module')
    # check classification surveyg module is empty
    self.assertEqual(len(self.classification_survey_module.objectValues()), 0)


  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 5 banknotes of 10000 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_des_billets_ventiles_et_detruits.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_des_billets_ventiles_et_detruits.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200 in encaisse_paris
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_des_billets_ventiles_et_detruits.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_des_billets_ventiles_et_detruits.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)


  def stepCheckSource(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory in source vault (encaisse_paris) before a confirm
    """
    # check we have 5 banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_des_billets_ventiles_et_detruits.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_des_billets_ventiles_et_detruits.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coin of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_des_billets_ventiles_et_detruits.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_des_billets_ventiles_et_detruits.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)


  def stepCheckDestination(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory in destination vault (caisse_2) before confirm
    """
    # check we don't have banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_des_billets_retires_de_la_circulation.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_des_billets_retires_de_la_circulation.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_externe.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_externe.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)

    # check we don't have coins of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_des_billets_retires_de_la_circulation.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_des_billets_retires_de_la_circulation.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_externe.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_externe.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)


  def stepCreateClassificationSurvey(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a classification surveyg document and check it
    """
    # classification surveyg has encaisse_paris for source, encaisse_externe for destination, and a price cooreponding to the sum of banknote of 10000 and banknotes of 200 ( (2+3) * 1000 + (5+7) * 200 )
    self.classification_survey = self.classification_survey_module.newContent(
                                      id='classification_survey_1',
                                      portal_type='Classification Survey',
                                      source_value=self.encaisse_des_billets_ventiles_et_detruits,
                                      destination_value=None,
                                      description='test',
                                      source_total_asset_price=52400.0)
    # execute tic
    self.tic()
    # set source reference
    self.setDocumentSourceReference(self.classification_survey)
    # check source reference
    self.assertNotEqual(self.classification_survey.getSourceReference(), '')
    self.assertNotEqual(self.classification_survey.getSourceReference(), None)
    # check we have only one classification surveyg
    self.assertEqual(len(self.classification_survey_module.objectValues()), 1)
    # get the classification surveyg document
    self.classification_survey = getattr(self.classification_survey_module, 'classification_survey_1')
    # check its portal type
    self.assertEqual(self.classification_survey.getPortalType(), 'Classification Survey')
    # check that its source is encaisse_paris
    self.assertEqual(self.classification_survey.getSource(), 'site/testsite/paris/caveau/auxiliaire/encaisse_des_billets_ventiles_et_detruits')
    # check that its destination is encaisse_externe
    self.assertEqual(self.classification_survey.getDestination(), None)


  def stepCreateTwoValidIncomingLine(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the classification surveyg incoming line  with banknotes of 10000 and check it has been well created
    """
    # create the classification surveyg line
    self.addCashLineToDelivery(self.classification_survey, 'valid_incoming_line_1', 'Incoming Classification Survey Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/not_defined') + self.variation_list,
            self.quantity_10000)
    # execute tic
    self.tic()
    # check there is only one line created
    self.assertEqual(len(self.classification_survey.objectValues()), 1)
    # get the classification surveyg line
    self.valid_incoming_line = getattr(self.classification_survey, 'valid_incoming_line_1')
    # check its portal type
    self.assertEqual(self.valid_incoming_line.getPortalType(), 'Incoming Classification Survey Line')
    # check the resource is banknotes of 10000
    self.assertEqual(self.valid_incoming_line.getResourceValue(), self.billet_10000)
    # chek the value of the banknote
    self.assertEqual(self.valid_incoming_line.getPrice(), 10000.0)
    # check the unit of banknote
    self.assertEqual(self.valid_incoming_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_incoming_line.objectValues()), 2)
    # now check for each variation (years 1992 and 2003)
    for variation in self.variation_list:
      # get the delivery cell
      cell = self.valid_incoming_line.getCell('emission_letter/not_defined', variation, 'cash_status/not_defined')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.billet_10000)
      # check the source vault is encaisse_paris
      self.assertEqual(cell.getSourceValue(), self.encaisse_des_billets_ventiles_et_detruits)
      # check the destination vault is encaisse_externe
      self.assertEqual(cell.getDestinationValue(), None)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote for year 1992 is 2
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity of banknote for year 2003 is 3
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())

    self.addCashLineToDelivery(self.classification_survey, 'valid_incoming_line_2', 'Incoming Classification Survey Line', self.billet_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/not_defined', 'cash_status/not_defined') + self.variation_list,
            self.quantity_200)
    # execute tic
    self.tic()
    # check there is only one line created
    self.assertEqual(len(self.classification_survey.objectValues()), 2)
    # get the classification surveyg line
    self.valid_incoming_line = getattr(self.classification_survey, 'valid_incoming_line_2')
    # check its portal type
    self.assertEqual(self.valid_incoming_line.getPortalType(), 'Incoming Classification Survey Line')
    # check the resource is banknotes of 10000
    self.assertEqual(self.valid_incoming_line.getResourceValue(), self.billet_200)
    # chek the value of the banknote
    self.assertEqual(self.valid_incoming_line.getPrice(), 200.0)
    # check the unit of banknote
    self.assertEqual(self.valid_incoming_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_incoming_line.objectValues()), 2)
    # now check for each variation (years 1992 and 2003)
    for variation in self.variation_list:
      # get the delivery cell
      cell = self.valid_incoming_line.getCell('emission_letter/not_defined', variation, 'cash_status/not_defined')
      # chek portal types
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      # check the banknote of the cell is banknote of 10000
      self.assertEqual(cell.getResourceValue(), self.billet_200)
      # check the source vault is encaisse_paris
      self.assertEqual(cell.getSourceValue(), self.encaisse_des_billets_ventiles_et_detruits)
      # check the destination vault is encaisse_externe
      self.assertEqual(cell.getDestinationValue(), None)
      if cell.getId() == 'movement_0_0_0':
        # check the quantity of banknote for year 1992 is 2
        self.assertEqual(cell.getQuantity(), 5.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity of banknote for year 2003 is 3
        self.assertEqual(cell.getQuantity(), 7.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCheckSubTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the amount after the creation of classification surveyg line 1
    """
    # Check number of lines
    self.assertEqual(len(self.classification_survey.objectValues()), 2)
    # Check quantity of banknotes (2 for 1992 and 3 for 2003)
    self.assertEqual(self.classification_survey.getTotalQuantity(fast=0, portal_type="Incoming Classification Survey Line"), 17.0)
    # Check the total price
    self.assertEqual(self.classification_survey.getTotalPrice(fast=0, portal_type="Incoming Classification Survey Line"), 10000 * 5.0 + 200 * 12.0)


  def stepCreateValidOutgoingLineForInternalBanknote(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the classification surveyg outgoing line wiht banknotes of 200 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.classification_survey, 'valid_outgoing_line_1', 'Outgoing Classification Survey Line', self.billet_10000,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/p', 'cash_status/cancelled') + self.variation_list,
            self.quantity_10000)
    # execute tic
    self.tic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.classification_survey.objectValues()), 3)
    # get the second classification surveyg line
    self.valid_outgoing_line = getattr(self.classification_survey, 'valid_outgoing_line_1')
    # check portal types
    self.assertEqual(self.valid_outgoing_line.getPortalType(), 'Outgoing Classification Survey Line')
    # check the resource is coin of 200
    self.assertEqual(self.valid_outgoing_line.getResourceValue(), self.billet_10000)
    # check the value of coin
    self.assertEqual(self.valid_outgoing_line.getPrice(), 10000.0)
    # check the unit of coin
    self.assertEqual(self.valid_outgoing_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_outgoing_line.objectValues()), 2)
    for variation in self.variation_list:
      # get the delivery  cell
      cell = self.valid_outgoing_line.getCell('emission_letter/p', variation, 'cash_status/cancelled')
      # check the portal type
      self.assertEqual(cell.getPortalType(), 'Outgoing Classification Survey Cell')
      variation_text = cell.getBaobabDestinationVariationText()
      cash_status = [x for x in variation_text.split('\n')
                     if x.startswith('cash_status')][0]
      self.assertEqual(cash_status, 'cash_status/retired')
      if cell.getId() == 'movement_0_0_0':
        # check the quantity for coin for year 1992 is 5
        self.assertEqual(cell.getQuantity(), 2.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity for coin for year 2003 is 7
        self.assertEqual(cell.getQuantity(), 3.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCreateValidOutgoingLineForExternalBanknote(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the classification surveyg outgoing line wiht banknotes of 200 and check it has been well created
    """
    # create the line
    self.addCashLineToDelivery(self.classification_survey, 'valid_outgoing_line_2', 'Outgoing Classification Survey Line', self.billet_200,
            ('emission_letter', 'cash_status', 'variation'), ('emission_letter/s', 'cash_status/cancelled') + self.variation_list,
            self.quantity_200)
    # execute tic
    self.tic()
    # check the number of lines (line1 + line2)
    self.assertEqual(len(self.classification_survey.objectValues()), 4)
    # get the second classification surveyg line
    self.valid_outgoing_line = getattr(self.classification_survey, 'valid_outgoing_line_2')
    # check portal types
    self.assertEqual(self.valid_outgoing_line.getPortalType(), 'Outgoing Classification Survey Line')
    # check the resource is coin of 200
    self.assertEqual(self.valid_outgoing_line.getResourceValue(), self.billet_200)
    # check the value of coin
    self.assertEqual(self.valid_outgoing_line.getPrice(), 200.0)
    # check the unit of coin
    self.assertEqual(self.valid_outgoing_line.getQuantityUnit(), 'unit')
    # check we have two delivery cells: (one for year 1992 and one for 2003)
    self.assertEqual(len(self.valid_outgoing_line.objectValues()), 2)
    for variation in self.variation_list:
      # get the delivery  cell
      cell = self.valid_outgoing_line.getCell('emission_letter/s', variation, 'cash_status/cancelled')
      # check the portal type
      self.assertEqual(cell.getPortalType(), 'Outgoing Classification Survey Cell')
      variation_text = cell.getBaobabDestinationVariationText()
      cash_status = [x for x in variation_text.split('\n')
                     if x.startswith('cash_status')][0]
      self.assertEqual(cash_status, 'cash_status/cancelled')
      if cell.getId() == 'movement_0_0_0':
        # check the quantity for coin for year 1992 is 5
        self.assertEqual(cell.getQuantity(), 5.0)
      elif cell.getId() == 'movement_0_1_0':
        # check the quantity for coin for year 2003 is 7
        self.assertEqual(cell.getQuantity(), 7.0)
      else:
        self.fail('Wrong cell created : %s' % cell.getId())


  def stepCheckTotal(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the total after the creation of the two classification surveyg lines
    """
    # Check number of lines (line1 + line2)
    self.assertEqual(len(self.classification_survey.objectValues()), 4)
    # Check quantity, banknotes : 2 for 1992 and 3 for 2003, coin : 5 for 1992 and 7 for 2003
    self.assertEqual(self.classification_survey.getTotalQuantity(fast=0), (5.0 + 12.0) * 2.0)
    # check the total price
    self.assertEqual(self.classification_survey.getTotalPrice(fast=0), (10000 * 5.0 + 200 * 12.0) * 2.0)


  def stepConfirmClassificationSurvey(self, sequence=None, sequence_list=None, **kwd):
    """
    Confirm the classification surveyg and check it
    """
    # do the Workflow action
    self.workflow_tool.doActionFor(self.classification_survey, 'confirm_action', wf_id='classification_survey_workflow')
    # execute tic
    self.tic()
    # get state
    state = self.classification_survey.getSimulationState()
    # check state is confirmed
    self.assertEqual(state, 'confirmed')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.classification_survey, name='history', wf_id='classification_survey_workflow')
    # check len of workflow history is 6
    self.assertEqual(len(workflow_history), 3)


  def stepCheckSourceDebitPlanned(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault encaisse_paris is right after confirm and before deliver
    """
    # check we have 5 banknotes of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_des_billets_ventiles_et_detruits.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we will have 0 banknote of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_des_billets_ventiles_et_detruits.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 12 coins of 200 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_des_billets_ventiles_et_detruits.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    # check we will have 0 coin of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_des_billets_ventiles_et_detruits.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)


  def stepCheckDestinationCreditPlanned(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault encaisse_externe is right after confirm and before deliver
    """
    # check we have 0 banknote of 10000 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_des_billets_retires_de_la_circulation.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we will have 5 banknotes of 10000 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_des_billets_retires_de_la_circulation.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 0 coin of 200 currently
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_externe.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)
    # check we will have 12 coins of 200 after deliver
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_externe.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)


  def stepDeliverClassificationSurvey(self, sequence=None, sequence_list=None, **kwd):
    """
    Deliver the classification surveyg with a good user
    and check that the deliver of a cash tranfer have achieved
    """
    #     self.security_manager = AccessControl.getSecurityManager()
    #     self.user = self.security_manager.getUser()
    # do the workflow transition "deliver_action"
    self.workflow_tool.doActionFor(self.classification_survey, 'deliver_action', wf_id='classification_survey_workflow')
    # execute tic
    self.tic()
    # get state of classification surveyg
    state = self.classification_survey.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.classification_survey, name='history', wf_id='classification_survey_workflow')


  def stepCheckSourceDebit(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at source (vault encaisse_paris) after deliver of the classification surveyg
    """
    # check we have 0 banknote of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_des_billets_ventiles_et_detruits.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_des_billets_ventiles_et_detruits.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    # check we have 0 coin of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_des_billets_ventiles_et_detruits.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_des_billets_ventiles_et_detruits.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 0.0)


  def stepCheckDestinationCredit(self, sequence=None, sequence_list=None, **kwd):
    """
    Check inventory at destination (vault encaisse_externe) after deliver of the classification surveyg
    """
    # check we have 5 banknotes of 10000
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_des_billets_retires_de_la_circulation.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_des_billets_retires_de_la_circulation.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 5.0)
    # check we have 12 coins of 200
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.encaisse_externe.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.encaisse_externe.getRelativeUrl(), resource = self.billet_200.getRelativeUrl()), 12.0)

  def stepResetSourceInventory(self,
               sequence=None, sequence_list=None, **kwd):
    """
    Reset a vault
    """
    node = self.encaisse_des_billets_ventiles_et_detruits
    line_list = self.line_list
    self.resetInventory(destination=node, currency=self.currency_1,
                        line_list=line_list,extra_id='_reset_out')

  def stepDeliverClassificationSurveyFails(self, sequence=None, sequence_list=None, **kwd):
    """
    Try if we get Insufficient balance
    """
    message = self.assertWorkflowTransitionFails(self.classification_survey,
              'classification_survey_workflow','deliver_action')
    self.assertTrue(message.find('Insufficient balance')>=0)

  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingClassificationSurvey(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventory CheckSource CheckDestination ' \
                    + 'CreateClassificationSurvey ' \
                    + 'CreateTwoValidIncomingLine CheckSubTotal ' \
                    + 'CreateValidOutgoingLineForInternalBanknote ' \
                    + 'CreateValidOutgoingLineForExternalBanknote ' \
                    + 'Tic CheckTotal ' \
                    + 'CheckSource CheckDestination ' \
                    + 'ConfirmClassificationSurvey Tic ' \
                    + 'CheckSourceDebitPlanned CheckDestinationCreditPlanned ' \
                    + 'ResetSourceInventory Tic ' \
                    + 'DeliverClassificationSurveyFails Tic ' \
                    + 'DeleteResetInventory Tic ' \
                    + 'DeliverClassificationSurvey Tic ' \
                    + 'CheckSourceDebit CheckDestinationCredit '
    sequence_list.addSequenceString(sequence_string)
    # play the sequence
    sequence_list.play(self)

