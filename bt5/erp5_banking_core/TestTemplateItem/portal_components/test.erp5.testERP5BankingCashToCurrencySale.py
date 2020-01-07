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
from erp5.component.module.TestERP5BankingMixin import TestERP5BankingMixin
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

class TestERP5BankingCashToCurrencySale(TestERP5BankingMixin):
  RUN_ALL_TEST = 1
  QUIET = 0
  # Relative to "site" category
  COUNTER_RELATIVE_URL = 'testsite/paris/surface/banque_interne/guichet_1'
  # Relative to counter
  INCOMING_COUNTER_RELATIVE_URL = 'encaisse_des_billets_et_monnaies/entrante'
  OUTGOING_COUNTER_RELATIVE_URL = 'encaisse_des_devises/usd/sortante'

  outgoing_quantity_5000 = {'variation/1992': 4, 'variation/2003': 6}
  outgoing_quantity_100 = {'variation/1992': 163, 'variation/2003': 0}

  def getTitle(self):
    return "ERP5BankingCashToCurrencySale"

  def afterSetUp(self):
    self.initDefaultVariable()
    self.cash_to_currency_sale_module = self.getPortal().cash_to_currency_sale_module
    self.createManagerAndLogin()
    self.createFunctionGroupSiteCategory()
    self.guichet = counter = self.getPortalObject().portal_categories.site.\
      unrestrictedTraverse(self.COUNTER_RELATIVE_URL)
    self.guichet_entrante = counter.unrestrictedTraverse(
      self.INCOMING_COUNTER_RELATIVE_URL)
    self.guichet_sortante = outgoing_counter = counter.unrestrictedTraverse(
      self.OUTGOING_COUNTER_RELATIVE_URL)
    self.line_list = line_list_sortante = [{
      'id': 'inventory_line_1',
      'resource': self.usd_billet_20,
      'variation_id': ('emission_letter', 'cash_status', 'variation'),
      'variation_value': ('emission_letter/not_defined',
        'cash_status/not_defined') + self.usd_variation_list,
      'variation_list': self.usd_variation_list,
      'quantity': self.quantity_usd_20,
    }, ]
    self.createCashInventory(
      source=None,
      destination=outgoing_counter,
      currency=self.currency_2,
      line_list=line_list_sortante,
    )
    self.checkUserFolderType()
    self.createERP5Users({
      'super_user' : [
        ['Manager'],
        self.organisation_module['site_P10'],
        'banking/comptable',
        'baobab',
        counter.getCategoryRelativeUrl(),
      ],
    })
    self.logout()
    self.loginByUserName('super_user')
    self.openCounterDate(site=counter)
    self.openCounter(site=counter)

  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    self.checkResourceCreated()
    module = self.cash_to_currency_sale_module
    self.assertEqual(module.getPortalType(), 'Cash To Currency Sale Module')
    self.assertEqual(len(module), 0)

  def stepCheckInitialInventoryGuichet(self, sequence=None, sequence_list=None,
      **kwd):
    assertEqual = self.assertEqual
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
    portal = self.getPortalObject()
    module = self.cash_to_currency_sale_module
    self.cash_to_currency_sale = document = module.newContent(
      id='cash_to_currency_sale_1',
      portal_type='Cash To Currency Sale',
      source_value=self.guichet,
      destination_value=None,
      description='test',
      resource_value=self.currency_2,
      source_total_asset_price=100.0,
      discount_ratio=0.02, # 1300
    )
    self.tic()
    self.assertEqual(len(module), 1)
    self.assertEqual(document.getSource(), self.guichet.getRelativeUrl())
    self.assertEqual(document.getDestination(), None)
    self.setDocumentSourceReference(document)
    self.tic()
    rate = document.CurrencyExchange_getExchangeRateList(
      from_currency=document.getResource(),
      to_currency='currency_module/%s' % (
        portal.Baobab_getPortalReferenceCurrencyID(), ),
      currency_exchange_type='sale',
      start_date=document.getStartDate(),
    )[0]
    self.assertEqual(rate, 650.0)

  def stepCreateValidIncomingLine(self, sequence=None, sequence_list=None,
      **kwd):
    document = self.cash_to_currency_sale
    line_1_id = 'valid_incoming_line_1'
    self.addCashLineToDelivery(
      document,
      line_1_id,
      'Incoming Cash To Currency Sale Line',
      self.billet_5000,
      ('emission_letter', 'cash_status', 'variation'),
      ('emission_letter/not_defined', 'cash_status/valid') + \
        self.variation_list,
      self.outgoing_quantity_5000,
    )
    self.tic()
    self.assertEqual(len(document), 1)
    line = getattr(document, line_1_id)
    self.assertEqual(line.getResourceValue(), self.billet_5000)
    self.assertEqual(line.getPrice(), 5000.0)
    self.assertEqual(line.getQuantityUnit(), 'unit')
    self.assertEqual(len(line), 2)
    for variation in self.variation_list:
      cell = line.getCell('emission_letter/not_defined', variation,
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
      document,
      line_2_id,
      'Incoming Cash To Currency Sale Line',
      self.piece_100,
      ('emission_letter', 'cash_status', 'variation'),
      ('emission_letter/not_defined', 'cash_status/valid') + \
        self.variation_list,
      self.outgoing_quantity_100,
    )
    self.tic()
    self.assertEqual(len(document), 2)
    line_2 = getattr(document, line_2_id)
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
    self.tic()

  def stepCheckSubTotal(self, sequence=None, sequence_list=None, **kwd):
    document = self.cash_to_currency_sale
    self.assertEqual(len(document), 2)
    self.assertEqual(document.getTotalQuantity(fast=0,
      portal_type="Incoming Cash To Currency Sale Line"), 173)
    self.assertEqual(document.getTotalPrice(fast=0,
      portal_type="Incoming Cash To Currency Sale Line"),
      5000 * 4.0 + 100 * 0.0 + 5000 * 6.0 + 100 * 163.0)

  def stepCreateValidOutgoingLine(self, sequence=None, sequence_list=None,
      **kwd):
    assertEqual = self.assertEqual
    document = self.cash_to_currency_sale
    line_id = 'valid_outgoing_line_1'
    self.addCashLineToDelivery(
      document,
      line_id,
      'Outgoing Cash To Currency Sale Line',
      self.usd_billet_20,
      ('emission_letter', 'cash_status', 'variation'),
      ('emission_letter/not_defined', 'cash_status/not_defined') + \
        self.usd_variation_list,
      self.quantity_usd_20,
      variation_list=self.usd_variation_list,
    )
    self.tic()
    assertEqual(len(document), 3)
    line = getattr(document, line_id)
    assertEqual(line.getPortalType(),
      'Outgoing Cash To Currency Sale Line')
    assertEqual(line.getResourceValue(), self.usd_billet_20)
    assertEqual(line.getPrice(), 20.0)
    assertEqual(line.getQuantityUnit(), 'unit')
    assertEqual(len(line), 1)
    for variation in self.usd_variation_list:
      cell = line.getCell('emission_letter/not_defined', variation,
        'cash_status/not_defined')
      assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      assertEqual(cell.getResourceValue(), self.usd_billet_20)
      assertEqual(cell.getBaobabSource(),
        self.guichet_sortante.getRelativeUrl())
      assertEqual(cell.getBaobabDestination(), None)
      cell_id = cell.getId()
      if cell_id == 'movement_0_0_0':
        assertEqual(cell.getQuantity(), 5.0)
      else:
        self.fail('Unexpected cell id: %s' % (cell_id, ))
    self.tic()

  def stepCheckTotal(self, sequence=None, sequence_list=None, **kwd):
    document = self.cash_to_currency_sale
    assertEqual = self.assertEqual
    assertEqual(len(document), 3)
    assertEqual(document.getTotalQuantity(fast=0,
      portal_type="Outgoing Cash To Currency Sale Line"), 5.0)
    assertEqual(document.getTotalPrice(fast=0,
      portal_type="Outgoing Cash To Currency Sale Line"), 20 * 5.0)

  def stepDeliverCashToCurrencySale(self, sequence=None, sequence_list=None,
      **kwd):
    document = self.cash_to_currency_sale
    self.workflow_tool.doActionFor(document, 'deliver_action',
      wf_id='cash_to_currency_sale_workflow')
    self.tic()
    self.assertEqual(document.getSimulationState(), 'delivered')
    self.tic()

  def stepCheckFinalInventoryGuichet(self, sequence=None,
      sequence_list=None, **kwd):
    assertEqual = self.assertEqual
    simulation_tool = self.getSimulationTool()
    getCurrentInventory = simulation_tool.getCurrentInventory
    getFutureInventory = simulation_tool.getFutureInventory
    incoming_counter = self.guichet_entrante.getRelativeUrl()
    outgoing_counter = self.guichet_sortante.getRelativeUrl()
    banknote_5000 = self.billet_5000.getRelativeUrl()
    coin_100 = self.piece_100.getRelativeUrl()
    banknote_usd_20 = self.usd_billet_20.getRelativeUrl()

    assertEqual(getCurrentInventory(node=incoming_counter,
      resource=banknote_5000), 10.0)
    assertEqual(getFutureInventory(node=incoming_counter,
      resource=banknote_5000), 10.0)
    assertEqual(getCurrentInventory(node=incoming_counter,
      resource=coin_100), 163.0)
    assertEqual(getFutureInventory(node=incoming_counter,
      resource=coin_100), 163.0)

    assertEqual(getCurrentInventory(node=outgoing_counter,
      resource=banknote_usd_20), 0.0)
    assertEqual(getFutureInventory(node=outgoing_counter,
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
  def _noop(self, *args, **kw):
    pass
  stepCheckInitialInventoryGuichet_Entrante = stepCheckInitialInventoryGuichet
  stepCheckFinalInventoryGuichet_Entrante = stepCheckFinalInventoryGuichet
  stepCheckFinalInventoryGuichet_Sortante = _noop
  stepCheckInitialInventoryGuichet_Sortante = _noop

  def test_01_ERP5BankingCashToCurrencySale(self, quiet=QUIET,
      run=RUN_ALL_TEST):
    if not run:
      return
    sequence_list = SequenceList()
    sequence_list.addSequenceString("""
      stepTic
      stepCheckObjects
      stepTic
      stepCheckInitialInventoryGuichet
      stepCreateCashToCurrencySale
      stepCreateValidIncomingLine stepCheckSubTotal
      stepCreateValidOutgoingLine
      stepTic
      stepCheckTotal
      stepResetSourceInventory
      stepTic
      stepDeliverCashToCurrencySaleFails
      stepTic
      stepDeleteResetInventory
      stepTic
      stepDeliverCashToCurrencySale
      stepTic
      stepCheckFinalInventoryGuichet_Entrante
      stepCheckFinalInventoryGuichet_Sortante
    """)
    sequence_list.play(self)

