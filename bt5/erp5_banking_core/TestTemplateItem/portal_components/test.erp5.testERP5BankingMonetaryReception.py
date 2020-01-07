
##############################################################################
#
# Copyright (c) 2006-2010 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5Type.tests.Sequence import SequenceList
from erp5.component.module.TestERP5BankingMixin import TestERP5BankingMixin

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'


class TestERP5BankingMonetaryReception(TestERP5BankingMixin):
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
    return "ERP5BankingMonetaryReception"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    # Set some variables :
    self.initDefaultVariable()
    # the cash inventory module
    self.monetary_reception_module = self.getMonetaryReceptionModule()

    self.createManagerAndLogin()
    self.createFunctionGroupSiteCategory(site_list=['paris'])
    self.reception = self.paris.caveau.serre.encaisse_des_billets_neufs_non_emis
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
    self.openCounterDate(site=self.paris)


  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that MonetaryReception Module was created
    self.assertEqual(self.monetary_reception_module.getPortalType(), 'Monetary Reception Module')
    # check cash inventory module is empty
    self.assertEqual(len(self.monetary_reception_module.objectValues()), 0)


  def stepCheckInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check we have 0 banknotes of 10000 in caisse_1
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.reception.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.reception.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)


  def stepCheckInitialContainerInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check initial cash container on source
    """
    self.assertEqual(len(self.simulation_tool.getCurrentTrackingList(node=self.reception.getRelativeUrl())), 0)
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(node=self.reception.getRelativeUrl())), 0)


  def stepCreateMonetaryReception(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a cash inventory document and check it
    """
    # Cash inventory has caisse_1 for source, caisse_2 for destination, and a price cooreponding to the sum of banknote of 10000 abd coin of 200 ( (2+3) * 1000 + (5+7) * 200 )
    self.monetary_reception = self.monetary_reception_module.newContent(
                                    id='monetary_reception',
                                    portal_type='Monetary Reception',
                                    source_value=None,
                                    destination_value=self.reception,
                                    description='test',
                                    resource_value=self.currency_1)
    #     self.setDestinationValue(self.reception)
    #     self.setResourceValue(self.currency_1)
    # execute tic
    self.tic()
    # get the cash inventory document
    self.monetary_reception = getattr(self.monetary_reception_module, 'monetary_reception')
    # check its portal type
    self.assertEqual(self.monetary_reception.getPortalType(), 'Monetary Reception')
    # check that its source is caisse_1
    self.assertEqual(self.monetary_reception.getSource(), None)
    # check that its destination is caisse_2
    self.assertEqual(self.monetary_reception.getBaobabDestination(), 'site/testsite/paris/caveau/serre/encaisse_des_billets_neufs_non_emis')


  def stepCreateCashContainer(self, sequence=None, sequence_list=None, **kwd):
    """
    Create the cash container
    """
    global_dict = {}
    global_dict['emission_letter'] = 'p'
    global_dict['variation'] = '2003'
    global_dict['cash_status'] = 'new_not_emitted'
    global_dict['resource'] = self.billet_10000

    line_list = []
    line_1 = {}
    line_1['reference'] = 'unit_test_1'
    line_1['range_start'] = 0
    line_1['range_stop'] = 100
    line_1['quantity'] = 100
    line_list.append(line_1)

    line_2 = {}
    line_2['reference'] = 'unit_test_2'
    line_2['range_start'] = 100
    line_2['range_stop'] = 200
    line_2['quantity'] = 100
    line_list.append(line_2)

    self.createCashContainer(self.monetary_reception, 'Cash Container Item', global_dict, line_list)
    # execute tic
    self.tic()
    # check there is two line created
    self.assertEqual(len(self.monetary_reception.objectValues()), 3)

  def stepCheckCashDeliveryLine(self, sequence=None, sequence_list=None):
    """
    Check the cash delivery line
    """
    # check the cash delivery line
    self.valid_line_1 = getattr(self.monetary_reception, 'movement')
    # check its portal type
    self.assertEqual(self.valid_line_1.getPortalType(), 'Cash Delivery Line')
    # check the resource is banknotes of 10000
    self.assertEqual(self.valid_line_1.getResourceValue(), self.billet_10000)
    # chek the value of the banknote
    self.assertEqual(self.valid_line_1.getPrice(), 10000.0)
    # check the unit of banknote
    self.assertEqual(self.valid_line_1.getQuantityUnit(), 'unit')
    # check we have one delivery cells
    self.assertEqual(len(self.valid_line_1.objectValues()), 1)
    # now check for variation 2003
    variation = 'variation/2003'
    # get the delivery cell
    cell = self.valid_line_1.getCell('emission_letter/p', variation, 'cash_status/new_not_emitted')
    # chek portal types
    self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
    # check the banknote of the cell is banknote of 10000
    self.assertEqual(cell.getResourceValue(), self.billet_10000)
    # check the source vault is caisse_1
    self.assertEqual(cell.getSourceValue(), None)
    # check the destination vault is caisse_2
    self.assertEqual(cell.getDestinationValue(), self.reception)
    self.assertEqual(cell.getQuantity(), 200.0)


  def stepCheckCashContainer1(self, sequence=None, sequence_list=None):
    """
    Check the cash container
    """
    # check the cash delivery line
    self.container_1 = getattr(self.monetary_reception, '1')
    # check its portal type
    self.assertEqual(self.container_1.getPortalType(), 'Cash Container Item')
    self.assertEqual(self.container_1.getReference(), 'unit_test_1')
    self.assertEqual(self.container_1.getCashNumberRangeStart(), '0')
    self.assertEqual(self.container_1.getCashNumberRangeStop(), '100')
    self.assertEqual(len(self.container_1.getAggregateValueList()), 1)
    self.assertEqual(self.container_1.getAggregateValueList()[0], self.container_1)
    self.assertEqual(len(self.container_1.objectIds()), 1)
    # now get the line and check it
    self.container_line_1 = self.container_1.objectValues()[0]
    self.assertEqual(self.container_line_1.getPortalType(), 'Container Line')
    # check the resource is banknotes of 10000
    self.assertEqual(self.container_line_1.getResourceValue(), self.billet_10000)
    # check we have one delivery cells
    self.assertEqual(len(self.container_1.objectValues()), 1)
    # now check for variation 2003
    cell = self.container_line_1.objectValues()[0]
    # chek portal types
    self.assertEqual(cell.getPortalType(), 'Container Cell')
    # check the banknote of the cell is banknote of 10000
    self.assertEqual(cell.getResourceValue(), self.billet_10000)
    # chek the value of the banknote
    self.assertEqual(cell.getPrice(), 10000.0)
    # check the source vault is caisse_1
    self.assertEqual(cell.getSourceValue(), None)
    # check the destination vault is caisse_2
    self.assertEqual(cell.getDestinationValue(), self.reception)
    self.assertEqual(cell.getQuantity(), 100.0)


  def stepCheckCashContainer2(self, sequence=None, sequence_list=None):
    """
    Check the cash container
    """
    # check the cash delivery line
    self.container_2 = getattr(self.monetary_reception, '2')
    # check its portal type
    self.assertEqual(self.container_2.getPortalType(), 'Cash Container Item')
    self.assertEqual(self.container_2.getReference(), 'unit_test_2')
    self.assertEqual(self.container_2.getCashNumberRangeStart(), '100')
    self.assertEqual(self.container_2.getCashNumberRangeStop(), '200')
    self.assertEqual(len(self.container_2.getAggregateValueList()), 1)
    self.assertEqual(self.container_2.getAggregateValueList()[0], self.container_2)
    self.assertEqual(len(self.container_2.objectIds()), 1)
    # now get the line and check it
    self.container_line_2 = self.container_2.objectValues()[0]
    self.assertEqual(self.container_line_2.getPortalType(), 'Container Line')
    # check the resource is banknotes of 10000
    self.assertEqual(self.container_line_2.getResourceValue(), self.billet_10000)
    # check we have one delivery cells
    self.assertEqual(len(self.container_2.objectValues()), 1)
    # now check for variation 2003
    cell = self.container_line_2.objectValues()[0]
    # chek portal types
    self.assertEqual(cell.getPortalType(), 'Container Cell')
    # check the banknote of the cell is banknote of 10000
    self.assertEqual(cell.getResourceValue(), self.billet_10000)
    # chek the value of the banknote
    self.assertEqual(cell.getPrice(), 10000.0)
    # check the source vault is caisse_1
    self.assertEqual(cell.getSourceValue(), None)
    # check the destination vault is caisse_2
    self.assertEqual(cell.getDestinationValue(), self.reception)
    self.assertEqual(cell.getQuantity(), 100.0)


  def stepConfirmMonetaryReception(self, sequence=None, sequence_list=None, **kwd):
    """
    confirm the monetary reception
    """
    state = self.monetary_reception.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'empty')
    self.workflow_tool.doActionFor(self.monetary_reception, 'confirm_action', wf_id='monetary_reception_workflow')
    self.assertEqual(self.monetary_reception.getSimulationState(), 'confirmed')
    workflow_history = self.workflow_tool.getInfoFor(ob=self.monetary_reception, name='history', wf_id='monetary_reception_workflow')
    # check len of len workflow history is 6
    self.assertEqual(len(workflow_history), 3)


  def stepCheckConfirmedInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault caisse_2 is right after confirm and before deliver
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.reception.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 0.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.reception.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 200.0)


  def stepCheckConfirmedContainerInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check cash container in item table
    """
    self.assertEqual(len(self.simulation_tool.getCurrentTrackingList(node=self.reception.getRelativeUrl())), 0)
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(node=self.reception.getRelativeUrl())), 2)


  def stepDeliverMonetaryReception(self, sequence=None, sequence_list=None, **kw):
    """
    Deliver the monetary reception
    """
    state = self.monetary_reception.getSimulationState()
    # check that state is draft
    self.assertEqual(state, 'confirmed')
    self.workflow_tool.doActionFor(self.monetary_reception, 'deliver_action', wf_id='monetary_reception_workflow')
    # execute tic
    self.tic()
    # get state of cash sorting
    state = self.monetary_reception.getSimulationState()
    # check that state is delivered
    self.assertEqual(state, 'delivered')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(ob=self.monetary_reception, name='history', wf_id='monetary_reception_workflow')
    # check len of len workflow history is 6
    self.assertEqual(len(workflow_history), 5)


  def stepCheckFinalInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that compution of inventory at vault caisse_2 is right after confirm and before deliver
    """
    self.assertEqual(self.simulation_tool.getCurrentInventory(node=self.reception.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 200.0)
    self.assertEqual(self.simulation_tool.getFutureInventory(node=self.reception.getRelativeUrl(), resource = self.billet_10000.getRelativeUrl()), 200.0)

  def stepCheckFinalContainerInventory(self, sequence=None, sequence_list=None, **kw):
    """
    Check cash container in item table
    """
    container_list = self.simulation_tool.getCurrentTrackingList(node=self.reception.getRelativeUrl())
    self.assertEqual(len(container_list), 2)
    # check we have cash container 1
    container_object_list = [x.getObject() for x in container_list]
    self.failIfDifferentSet([self.container_1, self.container_2],
                            container_object_list)
    self.assertEqual(len(self.simulation_tool.getFutureTrackingList(node=self.reception.getRelativeUrl())), 2)

  ##################################
  ##  Tests
  ##################################

  def test_01_ERP5BankingMonetaryReception(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckInitialInventory CheckInitialContainerInventory ' \
                    + 'CreateMonetaryReception Tic ' \
                    + 'CreateCashContainer Tic CheckCashDeliveryLine ' \
                    + 'CheckCashContainer1 CheckCashContainer2 ' \
                    + 'ConfirmMonetaryReception Tic CheckConfirmedInventory CheckConfirmedContainerInventory ' \
                    + 'DeliverMonetaryReception Tic CheckFinalInventory CheckFinalContainerInventory'
    sequence_list.addSequenceString(sequence_string)
    # play the sequence
    sequence_list.play(self)

