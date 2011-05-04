##############################################################################
#
# Copyright (c) 2005-2010 Nexedi SA and Contributors. All Rights Reserved.
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
import os
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Banking.tests.TestERP5BankingMixin import TestERP5BankingMixin

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

class TestERP5BankingCashToCurrencySale(TestERP5BankingMixin):

  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet

  outgoing_quantity_5000 = {'variation/1992': 4, 'variation/2003': 6}
  outgoing_quantity_100 = {'variation/1992': 163, 'variation/2003': 0}

  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingCashToCurrencySale"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    self.initDefaultVariable()
    # Set some variables :
    self.cash_to_currency_sale_module = \
      self.getPortal().cash_to_currency_sale_module
    # Create a user and login as manager to populate the erp5 portal with
    # objects for tests.
    self.createManagerAndLogin()
    self.createFunctionGroupSiteCategory()
    """
    Windows to create the BANKNOTES of 10 000 and 5000, coins 200.
    It s same to click to the fast input button.
    """
    self.line_list = line_list_sortante = [{
      'id': 'inventory_line_1',
      'resource': self.usd_billet_20,
      'variation_id': ('emission_letter', 'cash_status', 'variation'),
      'variation_value': ('emission_letter/not_defined',
        'cash_status/not_defined') + self.usd_variation_list,
      'variation_list': self.usd_variation_list,
      'quantity': self.quantity_usd_20,
    }, ]

    self.guichet = counter = self.paris.surface.banque_interne.guichet_1
    self.guichet_entrante = counter.encaisse_des_billets_et_monnaies.entrante
    self.guichet_sortante = counter.encaisse_des_devises.usd.sortante
    self.createCashInventory(source=None, destination=self.guichet_sortante,
      currency=self.currency_2, line_list=line_list_sortante)

    # now we need to create a user as Manager to do the test
    # in order to have an assigment defined which is used to do transition
    # Create an Organisation that will be used for users assignment
    self.checkUserFolderType()
    self.organisation = self.organisation_module.newContent(id='paris',
      portal_type='Organisation', function='banking', group='baobab',
      site=self.paris.getRelativeUrl())
    # define the user
    self.createERP5Users({
      'super_user' : [['Manager'], self.organisation, 'banking/comptable',
        'baobab', counter.getRelativeUrl()],
    }, )
    self.logout()
    self.login('super_user')
    # open counter date and counter
    self.openCounterDate(site=counter)
    self.openCounter(site=counter)

  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    """
    Check that all the objects we created in afterSetUp or
    that were added by the business template and that we rely
    on are really here.
    """
    self.checkResourceCreated()
    # check that CashToCurrencySale Module was created
    self.assertEqual(self.cash_to_currency_sale_module.getPortalType(),
      'Cash To Currency Sale Module')
    # check cash sorting module is empty
    self.assertEqual(len(self.cash_to_currency_sale_module.objectValues()), 0)

  def stepCheckInitialInventoryGuichet(self, sequence=None, sequence_list=None,
      **kwd):
    """
    Check the initial inventory before any operations
    """
    simulation_tool = self.getSimulationTool()
    getCurrentInventory = simulation_tool.getCurrentInventory
    getFutureInventory = simulation_tool.getFutureInventory
    incoming_counter = self.guichet_entrante.getRelativeUrl()
    outgoing_counter = self.guichet_sortante.getRelativeUrl()
    banknote_5000 = self.billet_5000.getRelativeUrl()
    banknote_100 = self.billet_100.getRelativeUrl()
    banknote_usd_20 = self.usd_billet_20.getRelativeUrl()

    self.assertEqual(getCurrentInventory(node=incoming_counter,
      resource=banknote_5000), 0.0)
    self.assertEqual(getFutureInventory(node=incoming_counter,
      resource=banknote_5000), 0.0)
    self.assertEqual(getCurrentInventory(node=incoming_counter,
      resource=banknote_100), 0.0)
    self.assertEqual(getFutureInventory(node=incoming_counter,
      resource=banknote_100), 0.0)

    self.assertEqual(getCurrentInventory(node=outgoing_counter,
      resource=banknote_usd_20), 5.0)
    self.assertEqual(getFutureInventory(node=outgoing_counter,
      resource=banknote_usd_20), 5.0)

  def stepCreateCashToCurrencySale(self, sequence=None, sequence_list=None, **kwd):
    """
    Create a cash sorting document and check it
    """
    module = self.cash_to_currency_sale_module
    self.cash_to_currency_sale = cash_to_currency_sale = module.newContent(
      id='cash_to_currency_sale_1', 
      portal_type='Cash To Currency Sale', 
      source_value=self.guichet, 
      destination_value=None, 
      description='test',
      resource_value=self.currency_2, 
      source_total_asset_price=100.0, 
      discount_ratio=0.02, # 1300
    )
    self.assertEqual(len(module), 1)
    self.assertEqual(cash_to_currency_sale.getSource(),
      'site/testsite/paris/surface/banque_interne/guichet_1')
    self.assertEqual(cash_to_currency_sale.getDestination(), None)
    self.setDocumentSourceReference(cash_to_currency_sale)
    self.stepTic()
    # Check the default exchange rate
    rate = cash_to_currency_sale.CurrencyExchange_getExchangeRateList(from_currency=cash_to_currency_sale.getResource(),
                                                                      to_currency='currency_module/%s' % (cash_to_currency_sale.Baobab_getPortalReferenceCurrencyID()),
                                                                      currency_exchange_type='sale',
                                                                      start_date=cash_to_currency_sale.getStartDate())[0]
    self.assertEqual(rate, 650.0)


  def stepCreateValidIncomingLine(self, sequence=None, sequence_list=None,
      **kwd):
    container = self.cash_to_currency_sale
    line_1_id = 'valid_incoming_line_1'
    self.addCashLineToDelivery(
      container,
      line_1_id,
      'Incoming Cash To Currency Sale Line',
      self.billet_5000,
      ('emission_letter', 'cash_status', 'variation'),
      ('emission_letter/not_defined', 'cash_status/valid') + \
        self.variation_list,
      self.outgoing_quantity_5000,
    )
    self.assertEqual(len(container), 1)
    line_1 = getattr(container, line_1_id)
    self.assertEqual(line_1.getResourceValue(), self.billet_5000)
    self.assertEqual(line_1.getPrice(), 5000.0)
    self.assertEqual(line_1.getQuantityUnit(), 'unit')
    self.assertEqual(len(line_1), 2)
    for variation in self.variation_list:
      cell = line_1.getCell('emission_letter/not_defined', variation,
        'cash_status/valid')
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getResourceValue(), self.billet_5000)
      self.assertEqual(cell.getBaobabSource(), None)
      self.assertEqual(cell.getBaobabDestination(),
        self.guichet_entrante.getRelativeUrl())
      cell_id = cell.getId()
      if cell_id == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 4.0)
      elif cell_id == 'movement_0_1_0':
        self.assertEqual(cell.getQuantity(), 6.0)
      else:
        self.fail('Unexpected cell id: %s' % (cell_id, ))

    line_2_id = 'valid_incoming_line_2'
    self.addCashLineToDelivery(
      container,
      line_2_id,
      'Incoming Cash To Currency Sale Line',
      self.piece_100,
      ('emission_letter', 'cash_status', 'variation'),
      ('emission_letter/not_defined', 'cash_status/valid') + \
        self.variation_list,
      self.outgoing_quantity_100,
    )
    self.assertEqual(len(container), 2)
    line_2 = getattr(self.cash_to_currency_sale, line_2_id)
    self.assertEqual(line_2.getPortalType(),
      'Incoming Cash To Currency Sale Line')
    self.assertEqual(line_2.getResourceValue(), self.piece_100)
    self.assertEqual(line_2.getPrice(), 100.0)
    self.assertEqual(line_2.getQuantityUnit(), 'unit')
    self.assertEqual(len(line_2), 2)
    for variation in self.variation_list:
      cell = line_2.getCell('emission_letter/not_defined', variation,
        'cash_status/valid')
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getResourceValue(), self.piece_100)
      self.assertEqual(cell.getBaobabSource(), None)
      self.assertEqual(cell.getBaobabDestination(),
        self.guichet_entrante.getRelativeUrl())
      cell_id = cell.getId()
      if cell_id == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 163.0)
      elif cell_id == 'movement_0_1_0':
        self.assertEqual(cell.getQuantity(), 0.0)
      else:
        self.fail('Unexpected cell id: %s' % (cell_id, ))
    # execute tic
    self.stepTic()

  def stepCheckSubTotal(self, sequence=None, sequence_list=None, **kwd):
    document = self.cash_to_currency_sale
    # Check number of lines
    self.assertEqual(len(document), 2)
    self.assertEqual(document.getTotalQuantity(fast=0,
      portal_type="Incoming Cash To Currency Sale Line"), 173)
    # Check the total price
    self.assertEqual(document.getTotalPrice(fast=0,
      portal_type="Incoming Cash To Currency Sale Line"),
      5000 * 4.0 + 100 * 0.0 + 5000 * 6.0 + 100 * 163.0)

  def stepCreateValidOutgoingLine(self, sequence=None, sequence_list=None,
      **kwd):
    container = self.cash_to_currency_sale
    line_id = 'valid_outgoing_line_1'
    self.addCashLineToDelivery(
      container,
      line_id,
      'Outgoing Cash To Currency Sale Line',
      self.usd_billet_20,
      ('emission_letter', 'cash_status', 'variation'),
      ('emission_letter/not_defined', 'cash_status/not_defined') + \
        self.usd_variation_list,
      self.quantity_usd_20,
      variation_list=self.usd_variation_list,
    )
    self.assertEqual(len(container), 3)
    # get the cash exchange line
    line = getattr(container, line_id)
    # check its portal type
    self.assertEqual(line.getPortalType(),
      'Outgoing Cash To Currency Sale Line')
    # check the resource is banknotes of 20
    self.assertEqual(line.getResourceValue(), self.usd_billet_20)
    # chek the value of the banknote
    self.assertEqual(line.getPrice(), 20.0)
    self.assertEqual(line.getQuantityUnit(), 'unit')
    self.assertEqual(len(line), 1)
    for variation in self.usd_variation_list:
      cell = line.getCell('emission_letter/not_defined', variation,
        'cash_status/not_defined')
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getResourceValue(), self.usd_billet_20)
      self.assertEqual(cell.getBaobabSource(),
        self.guichet_sortante.getRelativeUrl())
      self.assertEqual(cell.getBaobabDestination(), None)
      cell_id = cell.getId()
      if cell_id == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 5.0)
      else:
        self.fail('Wrong cell created : %s' % (cell_id, ))
    self.stepTic()

  def stepCheckTotal(self, sequence=None, sequence_list=None, **kwd):
    document = self.cash_to_currency_sale
    self.assertEqual(len(document), 3)
    self.assertEqual(document.getTotalQuantity(fast=0,
      portal_type="Outgoing Cash To Currency Sale Line"), 5.0)
    self.assertEqual(document.getTotalPrice(fast=0,
      portal_type="Outgoing Cash To Currency Sale Line"), 20 * 5.0)

  def stepDeliverCashToCurrencySale(self, sequence=None, sequence_list=None, 
      **kwd):
    #self.cash_to_currency_sale.setSourceTotalAssetPrice('52400.0')
    #     self.security_manager = AccessControl.getSecurityManager()
    #     self.user = self.security_manager.getUser()
    # do the workflow transition "deliver_action"
    document = self.cash_to_currency_sale
    self.workflow_tool.doActionFor(document, 'deliver_action',
      wf_id='cash_to_currency_sale_workflow')
    # check that state is delivered
    self.assertEqual(document.getSimulationState(), 'delivered')
    # execute tic
    self.stepTic()

  def stepCheckFinalInventoryGuichet(self, sequence=None,
      sequence_list=None, **kwd):
    simulation_tool = self.getSimulationTool()
    getCurrentInventory = simulation_tool.getCurrentInventory
    getFutureInventory = simulation_tool.getFutureInventory
    incoming_counter = self.guichet_entrante.getRelativeUrl()
    outgoing_counter = self.guichet_sortante.getRelativeUrl()
    banknote_5000 = self.billet_5000.getRelativeUrl()
    coin_100 = self.piece_100.getRelativeUrl()
    banknote_usd_20 = self.usd_billet_20.getRelativeUrl()

    self.assertEqual(getCurrentInventory(node=incoming_counter,
      resource=banknote_5000), 10.0)
    self.assertEqual(getFutureInventory(node=incoming_counter,
      resource=banknote_5000), 10.0)
    self.assertEqual(getCurrentInventory(node=incoming_counter,
      resource=coin_100), 163.0)
    self.assertEqual(getFutureInventory(node=incoming_counter,
      resource=coin_100), 163.0)

    self.assertEqual(getCurrentInventory(node=outgoing_counter,
      resource=banknote_usd_20), 0.0)
    self.assertEqual(getFutureInventory(node=outgoing_counter,
      resource=banknote_usd_20), 0.0)

  def stepDelCashToCurrencySale(self, sequence=None, sequence_list=None,
      **kwd):
    self.cash_to_currency_sale_module.deleteContent('cash_to_currency_sale_1')

  def stepResetSourceInventory(self, sequence=None, sequence_list=None,
      **kwd):
    """
    Reset a vault
    """
    self.resetInventory(
      destination=self.guichet_sortante,
      currency=self.currency_1,
      line_list=self.line_list,
      extra_id='_reset_out',
    )

  def stepDeliverCashToCurrencySaleFails(self, sequence=None,
      sequence_list=None, **kwd):
    """
    Try if we get Insufficient balance
    """
    message = self.assertWorkflowTransitionFails(self.cash_to_currency_sale,
      'cash_to_currency_sale_workflow', 'deliver_action')
    self.assertTrue(message.find('Insufficient balance') >= 0, message)

  # Backward compatibility (merged steps)
  def _noop(*args, **kw):
    pass
  stepCheckInitialInventoryGuichet_Entrante = stepCheckInitialInventoryGuichet
  stepCheckFinalInventoryGuichet_Entrante = stepCheckFinalInventoryGuichet
  stepCheckFinalInventoryGuichet_Sortante = _noop
  stepCheckInitialInventoryGuichet_Sortante = _noop

  def test_01_ERP5BankingCashToCurrencySale(self, quiet=QUIET,
      run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run:
      return
    sequence_list = SequenceList()
    sequence_list.addSequenceString('stepTic stepCheckObjects stepTic '
      'stepCheckInitialInventoryGuichet '
      'stepCreateCashToCurrencySale '
      'stepCreateValidIncomingLine stepCheckSubTotal '
      'stepCreateValidOutgoingLine '
      'stepTic stepCheckTotal '
      'stepResetSourceInventory stepTic '
      'stepDeliverCashToCurrencySaleFails stepTic '
      'stepDeleteResetInventory stepTic '
      'stepDeliverCashToCurrencySale stepTic '
      'stepCheckFinalInventoryGuichet_Entrante '
      'stepCheckFinalInventoryGuichet_Sortante'
    )
    sequence_list.play(self)

