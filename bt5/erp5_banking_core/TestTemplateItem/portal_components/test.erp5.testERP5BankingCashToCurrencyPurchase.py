
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

class TestERP5BankingCashToCurrencyPurchase(TestERP5BankingMixin):
  RUN_ALL_TEST = 1
  QUIET = 0
  # Relative to "site" category
  COUNTER_RELATIVE_URL = 'testsite/paris/surface/banque_interne/guichet_1'
  # Relative to counter
  INCOMING_COUNTER_RELATIVE_URL = 'encaisse_des_devises/usd/sortante'
  OUTGOING_COUNTER_RELATIVE_URL = 'encaisse_des_billets_et_monnaies/sortante'

  outgoing_quantity_5000 = {'variation/1992': 4, 'variation/2003': 6}
  outgoing_quantity_100 = {'variation/1992': 120, 'variation/2003': 0}

  def getTitle(self):
    return "ERP5BankingCashToCurrencyPurchase"

  def afterSetUp(self):
    self.initDefaultVariable()
    self.cash_to_currency_purchase_module = self.getCashToCurrencyPurchaseModule()
    self.createManagerAndLogin()
    self.createFunctionGroupSiteCategory()
    self.guichet = counter = self.getPortalObject().portal_categories.site.\
      unrestrictedTraverse(self.COUNTER_RELATIVE_URL)
    self.guichet_entrante = counter.unrestrictedTraverse(
      self.INCOMING_COUNTER_RELATIVE_URL)
    self.guichet_sortante = outgoing_counter = counter.unrestrictedTraverse(
      self.OUTGOING_COUNTER_RELATIVE_URL)
    self.createCashInventory(
      source=None,
      destination=outgoing_counter,
      currency=self.currency_1,
      line_list=[
        {
          'id': 'inventory_line_1',
          'resource': self.billet_5000,
          'variation_id': ('emission_letter', 'cash_status', 'variation'),
          'variation_value': ('emission_letter/p', 'cash_status/valid') + self.variation_list,
          'quantity': self.outgoing_quantity_5000,
        }, {
          'id': 'inventory_line_2',
          'resource': self.piece_100,
          'variation_id': ('emission_letter', 'cash_status', 'variation'),
          'variation_value': ('emission_letter/not_defined', 'cash_status/valid') + self.variation_list,
          'quantity': self.outgoing_quantity_100,
        },
      ],
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
    self.openCounterDate(site=outgoing_counter)
    self.openCounter(site=counter)

  def stepCheckObjects(self, sequence=None, sequence_list=None, **kwd):
    self.checkResourceCreated()
    module = self.cash_to_currency_purchase_module
    self.assertEqual(module.getPortalType(), 'Cash To Currency Purchase Module')
    self.assertEqual(len(module), 0)

  def stepCheckInitialInventoryGuichet_Entrante(self, sequence=None, sequence_list=None,
      **kwd):
    assertEqual = self.assertEqual
    simulation_tool = self.getSimulationTool()
    node = node=self.guichet_entrante.getRelativeUrl()
    resource = self.usd_billet_20.getRelativeUrl()
    assertEqual(simulation_tool.getCurrentInventory(node=node, resource=resource), 0.0)
    assertEqual(simulation_tool.getFutureInventory(node=node, resource=resource), 0.0)

  def stepCheckInitialInventoryGuichet_Sortante(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    assertEqual = self.assertEqual
    simulation_tool = self.getSimulationTool()
    node = node=self.guichet_sortante.getRelativeUrl()
    banknote_10k = self.billet_10000.getRelativeUrl()
    banknote_5k = self.billet_5000.getRelativeUrl()
    coin_200 = self.piece_200.getRelativeUrl()
    coin_100 = self.piece_100.getRelativeUrl()
    assertEqual(simulation_tool.getCurrentInventory(node=node, resource=banknote_10k), 0.0)
    assertEqual(simulation_tool.getFutureInventory(node=node, resource=banknote_10k), 0.0)
    assertEqual(simulation_tool.getCurrentInventory(node=node, resource=coin_200), 0.0)
    assertEqual(simulation_tool.getFutureInventory(node=node, resource=coin_200), 0.0)
    assertEqual(simulation_tool.getCurrentInventory(node=node, resource=banknote_5k), 10.0)
    assertEqual(simulation_tool.getFutureInventory(node=node, resource=banknote_5k), 10.0)
    assertEqual(simulation_tool.getCurrentInventory(node=node, resource=coin_100), 120.0)
    assertEqual(simulation_tool.getFutureInventory(node=node, resource=coin_100), 120.0)

  def stepCreateCashToCurrencyPurchase(self, sequence=None, sequence_list=None, **kwd):
    portal = self.getPortalObject()
    module = self.cash_to_currency_purchase_module
    self.cash_to_currency_purchase = document = module.newContent(
      id='cash_to_currency_purchase_1',
      portal_type='Cash To Currency Purchase',
      source_value=self.guichet,
      destination_value=None,
      description='test',
      resource_value=self.currency_2,
      source_total_asset_price=100.0,
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
      currency_exchange_type='purchase',
      start_date=document.getStartDate(),
    )[0]
    self.assertEqual(rate, 650.0)
    script = document.CurrencyPurchase_getQuantity
    self.assertEqual(script(), 65000)
    document.setDiscountRatio(0.01)
    self.assertEqual(script(), 64350)
    document.setDiscountRatio(None)
    document.setDiscount(3000)
    self.assertEqual(script(), 62000)
    document.setCurrencyExchangeRate(660)
    self.assertEqual(script(), 63000)
    document.setCurrencyExchangeRate(None)
    self.assertEqual(script(), 62000)

  def stepCreateValidIncomingLine(self, sequence=None, sequence_list=None,
      **kwd):
    document = self.cash_to_currency_purchase
    line_1_id = 'valid_incoming_line_1'
    self.addCashLineToDelivery(
      document,
      line_1_id,
      'Incoming Cash To Currency Purchase Line',
      self.usd_billet_20,
      ('emission_letter', 'cash_status', 'variation'),
      ('emission_letter/not_defined', 'cash_status/not_defined') + \
        self.usd_variation_list,
      self.quantity_usd_20,
      variation_list=self.usd_variation_list,
    )
    self.tic()
    self.assertEqual(len(document), 1)
    line = getattr(document, line_1_id)
    self.assertEqual(line.getResourceValue(), self.usd_billet_20)
    self.assertEqual(line.getPrice(), 20.0)
    self.assertEqual(line.getQuantityUnit(), 'unit')
    self.assertEqual(len(line), 1)
    for variation in self.usd_variation_list:
      cell = line.getCell('emission_letter/not_defined', variation,
        'cash_status/not_defined')
      self.assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      self.assertEqual(cell.getResourceValue(), self.usd_billet_20)
      self.assertEqual(cell.getBaobabSource(), None)
      self.assertEqual(cell.getBaobabDestination(),
        self.guichet_entrante.getRelativeUrl())
      cell_id = cell.getId()
      if cell_id == 'movement_0_0_0':
        self.assertEqual(cell.getQuantity(), 5.0)
      else:
        self.fail('Unexpected cell id: %s' % (cell_id, ))

  def stepCheckSubTotal(self, sequence=None, sequence_list=None, **kwd):
    document = self.cash_to_currency_purchase
    assertEqual = self.assertEqual
    assertEqual(len(document), 1)
    assertEqual(document.getTotalQuantity(fast=0,
      portal_type="Incoming Cash To Currency Purchase Line"), 5.0)
    assertEqual(document.getTotalPrice(fast=0,
      portal_type="Incoming Cash To Currency Purchase Line"), 20 * 5.0)

  def stepCreateValidOutgoingLine(self, sequence=None, sequence_list=None, **kwd):
    document = self.cash_to_currency_purchase
    assertEqual = self.assertEqual
    source = self.guichet_sortante.getRelativeUrl()
    line_2_id = 'valid_outgoing_line_1'
    self.addCashLineToDelivery(
      document,
      line_2_id,
      'Outgoing Cash To Currency Purchase Line',
      self.billet_5000,
      ('emission_letter', 'cash_status', 'variation'),
      ('emission_letter/p', 'cash_status/valid') + self.variation_list,
      self.outgoing_quantity_5000,
    )
    self.tic()
    assertEqual(len(document), 2)
    line = getattr(document, line_2_id)
    assertEqual(line.getPortalType(),
      'Outgoing Cash To Currency Purchase Line')
    assertEqual(line.getResourceValue(), self.billet_5000)
    assertEqual(line.getPrice(), 5000.0)
    assertEqual(line.getQuantityUnit(), 'unit')
    assertEqual(len(line), 2)
    for variation in self.variation_list:
      cell = line.getCell('emission_letter/p', variation, 'cash_status/valid')
      assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      assertEqual(cell.getBaobabSource(), source)
      assertEqual(cell.getBaobabDestination(), None)
      cell_id = cell.getId()
      if cell_id == 'movement_0_0_0':
        assertEqual(cell.getQuantity(), 4.0)
      elif cell_id == 'movement_0_1_0':
        assertEqual(cell.getQuantity(), 6.0)
      else:
        self.fail('Unexpected cell id: %s' % (cell_id, ))

    self.addCashLineToDelivery(
      document,
      'valid_outgoing_line_2',
      'Outgoing Cash To Currency Purchase Line',
      self.piece_100,
      ('emission_letter', 'cash_status', 'variation'),
      ('emission_letter/not_defined', 'cash_status/valid') + self.variation_list,
      self.outgoing_quantity_100,
    )
    self.tic()
    assertEqual(len(document), 3)
    line = document.valid_outgoing_line_2
    assertEqual(line.getPortalType(), 'Outgoing Cash To Currency Purchase Line')
    assertEqual(line.getResourceValue(), self.piece_100)
    assertEqual(line.getPrice(), 100.0)
    assertEqual(line.getQuantityUnit(), 'unit')
    assertEqual(len(line), 2)
    for variation in self.variation_list:
      cell = line.getCell('emission_letter/not_defined', variation, 'cash_status/valid')
      assertEqual(cell.getPortalType(), 'Cash Delivery Cell')
      assertEqual(cell.getBaobabSource(), source)
      assertEqual(cell.getBaobabDestination(), None)
      cell_id = cell.getId()
      if cell_id == 'movement_0_0_0':
        assertEqual(cell.getQuantity(), 120.0)
      elif cell_id == 'movement_0_1_0':
        assertEqual(cell.getQuantity(), 0.0)
      else:
        self.fail('Unexpected cell id: %s' % (cell_id, ))
    self.tic()

  def stepCheckTotal(self, sequence=None, sequence_list=None, **kwd):
    document = self.cash_to_currency_purchase
    assertEqual = self.assertEqual
    assertEqual(len(document.objectValues()), 3)
    assertEqual(document.getTotalQuantity(fast=0,
      portal_type="Outgoing Cash To Currency Purchase Line"), 130.0)
    assertEqual(document.getTotalPrice(fast=0,
      portal_type="Outgoing Cash To Currency Purchase Line"),
      5000 * 4.0 + 100 * 0.0 + 5000 * 6.0 + 100 * 120.0)

  def stepDeliverCashToCurrencyPurchase(self, sequence=None, sequence_list=None,
      **kwd):
    document = self.cash_to_currency_purchase
    self.workflow_tool.doActionFor(document, 'deliver_action',
      wf_id='cash_to_currency_purchase_workflow')
    self.tic()
    self.assertEqual(document.getSimulationState(), 'delivered')
    workflow_history = self.workflow_tool.getInfoFor(ob=document,
      name='history', wf_id='cash_to_currency_purchase_workflow')
    self.assertEqual(len(workflow_history), 3)

  def stepCheckFinalInventoryGuichet_Entrante(self, sequence=None, sequence_list=None, **kwd):
    assertEqual = self.assertEqual
    simulation_tool = self.getSimulationTool()
    node = self.guichet_entrante.getRelativeUrl()
    resource = resource=self.usd_billet_20.getRelativeUrl()
    assertEqual(simulation_tool.getCurrentInventory(node=node,
      resource=resource), 5.0)
    assertEqual(simulation_tool.getFutureInventory(node=node,
      resource=resource), 5.0)

  def stepCheckFinalInventoryGuichet_Sortante(self, sequence=None,
      sequence_list=None, **kwd):
    assertEqual = self.assertEqual
    simulation_tool = self.getSimulationTool()
    node = node=self.guichet_sortante.getRelativeUrl()
    banknote_5k = self.billet_5000.getRelativeUrl()
    coin_100 = self.piece_100.getRelativeUrl()
    assertEqual(simulation_tool.getCurrentInventory(node=node,
      resource=banknote_5k), 0.0)
    assertEqual(simulation_tool.getFutureInventory(node=node,
      resource=banknote_5k), 0.0)
    assertEqual(simulation_tool.getCurrentInventory(node=node,
      resource=coin_100), 0.0)
    assertEqual(simulation_tool.getFutureInventory(node=node,
      resource=coin_100), 0.0)

  def test_01_ERP5BankingCashToCurrencyPurchase(self, quiet=QUIET,
      run=RUN_ALL_TEST):
    if not run:
      return
    sequence_list = SequenceList()
    sequence_list.addSequenceString("""
      stepTic
      stepCheckObjects
      stepTic
      stepCheckInitialInventoryGuichet_Entrante
      stepCheckInitialInventoryGuichet_Sortante
      stepCreateCashToCurrencyPurchase
      stepCreateValidIncomingLine
      stepCheckSubTotal
      stepCreateValidOutgoingLine
      stepTic
      stepCheckTotal
      stepDeliverCashToCurrencyPurchase
      stepTic
      stepCheckFinalInventoryGuichet_Entrante
      stepCheckFinalInventoryGuichet_Sortante
    """)
    sequence_list.play(self)

