##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Yoshinori Okuji <yo@nexedi.com>
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



#
# Skeleton ZopeTestCase
#

from random import randint

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from DateTime import DateTime
from Acquisition import aq_base, aq_inner
from zLOG import LOG
import time

class TestFusion(ERP5TypeTestCase):
  """
    Test the fusion code 'mergeDeliveryList' in Simulation Tool.
    Need to test these types:

      - commande_vente (Sales Order)
      - livraison_vente (Sales Packing List)
      - facture_vente (Sale Invoice Transaction)
      - commande_achat (Purchase Order)
      - livraison_achat (Purchase Packing List)
      - ordre_fabrication (Production Order)
      - livraison_fabrication (Production Packing List)
      - rapport_fabrication (Production Report)
  """
  run_all_test = 1
  # Various variables used for this test
  customer_organisation_id = 'nexedi'
  customer_person_id = 'yo'
  vendor_organisation_id = 'coramy'
  vendor_person_id = 'tb'
  vendor_section = 'group/Coramy'

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.

      the business template crm give the following things :
      modules:
        - person
        - organisation
      base categories:
        - region
        - subordination

      /organisation
    """
    return ('erp5_crm', 'coramy_catalog', 'coramy_delivery', )
    #return ('erp5_crm', 'coramy_delivery', )

  def getCatalogTool(self):
    return getattr(self.getPortal(), 'portal_catalog', None)

  def getSimulationTool(self):
    return getattr(self.getPortal(), 'portal_simulation', None)

  def getPersonModule(self):
    return getattr(self.getPortal(), 'person', None)

  def getOrganisationModule(self):
    return getattr(self.getPortal(), 'organisation', None)

  def getSalesOrderModule(self):
    return getattr(self.getPortal(), 'commande_vente', None)

  def getSalesPackingListModule(self):
    return getattr(self.getPortal(), 'livraison_vente', None)

  def getSaleInvoiceTransactionModule(self):
    return getattr(self.getPortal(), 'facture_vente', None)

  def getPurchaseOrderModule(self):
    return getattr(self.getPortal(), 'commande_achat', None)

  def getPurchasePackingListModule(self):
    return getattr(self.getPortal(), 'livraison_achat', None)

  def getProductionOrderModule(self):
    return getattr(self.getPortal(), 'ordre_fabrication', None)

  def getProductionPackingListModule(self):
    return getattr(self.getPortal(), 'livraison_fabrication', None)

  def getProductionReportModule(self):
    return getattr(self.getPortal(), 'rapport_fabrication', None)

  def getComposantModule(self):
    return getattr(self.getPortal(), 'composant', None)

  def getAssortimentModule(self):
    return getattr(self.getPortal(), 'assortiment', None)

  def afterSetUp(self, quiet=1, run=1):
    self.login()
    portal = self.getPortal()
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()
    portal.ERP5_setAcquisition()
    portal.portal_categories.immediateReindexObject()
    for o in portal.portal_categories.objectValues():
      o.recursiveImmediateReindexObject()
    portal.portal_simulation.immediateReindexObject()
    for o in portal.portal_simulation.objectValues():
      o.recursiveImmediateReindexObject()
    portal.portal_rules.immediateReindexObject()
    # Create organisations.
    portal.portal_types.constructContent(type_name='Organisation Module',
                                         container=portal,
                                         id='organisation')
    organisation_module = portal.organisation
    self.customer_organisation = organisation_module.newContent(id=self.customer_organisation_id)
    self.vendor_organisation = organisation_module.newContent(id=self.vendor_organisation_id)
    # Create persons.
    portal.portal_types.constructContent(type_name='Person Module',
                                         container=portal,
                                         id='person')
    person_module = portal.person
    self.customer_person = person_module.newContent(id=self.customer_person_id)
    self.vendor_person = person_module.newContent(id=self.vendor_person_id)
    # Create models.
    modele_module = portal.modele
    self.model1 = modele_module.newContent(id='060E404')
    self.model1.newContent(id='B', portal_type='Variante Morphologique')
    self.model1.newContent(id='C', portal_type='Variante Morphologique')
    self.model1.newContent(id='Violet_rose', portal_type='Variante Modele')
    self.model1.newContent(id='noir_gris', portal_type='Variante Modele')
    self.model2 = modele_module.newContent(id='004C401')

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  """
  def test_01_SanityCheck(self, quiet=0, run=run_all_test):
    # Test if the environment is not broken
    if not run: return
    if not quiet:
      message = '\nTest Sanity Check '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    portal = self.getPortal()
    self.assertNotEqual(self.getOrganisationModule(), None)
    organisation_module = portal.organisation
    self.assertNotEqual(organisation_module._getOb(self.customer_organisation_id), None)
    self.assertNotEqual(organisation_module._getOb(self.vendor_organisation_id), None)
    self.assertNotEqual(self.getPersonModule(), None)
    person_module = portal.person
    self.assertNotEqual(person_module._getOb(self.customer_person_id), None)
    self.assertNotEqual(person_module._getOb(self.vendor_person_id), None)
    self.assertNotEqual(self.getSimulationTool(), None)
    self.assertNotEqual(self.getSalesOrderModule(), None)
    self.assertNotEqual(self.getSalesPackingListModule(), None)

  def test_02_InvalidDeliveriesPassed(self, quiet=0, run=run_all_test):
    # Test if mergeDeliveryList raises an exception when no delivery or a single one is passed
    # and when deliveries have different organisations/persons/discounts/payment conditions.
    if not run: return
    if not quiet:
      message = '\nInvalid Deliveries Passed '
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    portal_simulation = self.getSimulationTool()
    self.assertRaises(portal_simulation.MergeDeliveryListError,
                      portal_simulation.mergeDeliveryList,
                      [])
    self.assertRaises(portal_simulation.MergeDeliveryListError,
                      portal_simulation.mergeDeliveryList,
                      [None]) # None is okay here, since it is never used.
    module = self.getSalesOrderModule()
    # Test source sections.
    if module.hasContent('1'): module.deleteContent('1')
    if module.hasContent('2'): module.deleteContent('2')
    d1 = module.newContent(id='1', portal_type='Sales Order',
                           source_section=self.vendor_organisation.getRelativeUrl())
    self.assertEqual(d1.getSourceSection(), self.vendor_organisation.getRelativeUrl())
    d2 = module.newContent(id='2', portal_type='Sales Order',
                           source_section=self.customer_organisation.getRelativeUrl())
    self.assertEqual(d2.getSourceSection(), self.customer_organisation.getRelativeUrl())
    self.assertRaises(portal_simulation.MergeDeliveryListError,
                      portal_simulation.mergeDeliveryList,
                      [d1, d2])
    d2.setSourceSection(self.vendor_organisation.getRelativeUrl())
    self.assertEqual(d2.getSourceSection(), self.vendor_organisation.getRelativeUrl())
    # Test source decisions.
    d1.setSourceDecision(self.vendor_person.getRelativeUrl())
    d2.setSourceDecision(self.customer_person.getRelativeUrl())
    self.assertEqual(d1.getSourceDecision(), self.vendor_person.getRelativeUrl())
    self.assertEqual(d2.getSourceDecision(), self.customer_person.getRelativeUrl())
    self.assertRaises(portal_simulation.MergeDeliveryListError,
                      portal_simulation.mergeDeliveryList,
                      [d1, d2])
    d2.setSourceDecision(self.vendor_person.getRelativeUrl())
    self.assertEqual(d2.getSourceDecision(), self.vendor_person.getRelativeUrl())
    # Test discounts.
    r1 = d1.newContent(id='ESCOMPTE', portal_type='Remise', immediate_discount=1)
    r2 = d2.newContent(id='ESCOMPTE', portal_type='Remise', immediate_discount=0)
    self.assertEqual(r1.getImmediateDiscount(), 1)
    self.assertEqual(r2.getImmediateDiscount(), 0)
    self.assertRaises(portal_simulation.MergeDeliveryListError,
                      portal_simulation.mergeDeliveryList,
                      [d1, d2])
    r2.setImmediateDiscount(1)
    self.assertEqual(r2.getImmediateDiscount(), 1)
    # Test payment conditions.
    c1 = d1.newContent(id='RFA', portal_type='Condition Paiement', payment_term=90)
    c2 = d2.newContent(id='RFA', portal_type='Condition Paiement', payment_term=180)
    self.assertEqual(c1.getPaymentTerm(), 90)
    self.assertEqual(c2.getPaymentTerm(), 180)
    self.assertRaises(portal_simulation.MergeDeliveryListError,
                      portal_simulation.mergeDeliveryList,
                      [d1, d2])
    c2.setPaymentTerm(90)
    self.assertEqual(c2.getPaymentTerm(), 90)
    # Now fusion must succeed.
    portal_simulation.mergeDeliveryList([d1, d2])
  """

  def setCell(self, line, category_list, **kw):
    category_list = list(category_list)
    category_list.sort()
    LOG('setCell', 0, 'line = %s, line.contentValues() = %s, line.objectIds() = %s' % (repr(line), repr(line.contentValues()), repr(list(line.objectIds()))))
    for cell in line.contentValues():
      predicate_value_list = cell.getPredicateValueList()
      predicate_value_list.sort()
      if predicate_value_list == category_list:
        cell.edit(**kw)
        return cell

  def makeDeliveries(self, module, delivery_type, delivery_line_type):
    for id in ('1', '2', '3'):
      if module.hasContent(id):
        module.deleteContent(id)
    d1 = module.newContent(id='1', portal_type=delivery_type)
    self.assertEqual(d1.getPortalType(), delivery_type)
    d1_line1 = d1.newContent(id='1', portal_type=delivery_line_type,
                             resource='modele/004C401',
                             price=2.0,
                             quantity=1.0,
                             target_quantity=1.0)
    self.assertEqual(d1_line1.getPortalType(), delivery_line_type)
    d1_line2 = d1.newContent(id='2', portal_type=delivery_line_type,
                             resource='modele/060E404',
                             variation_base_category_list = ['morphologie', 'taille', 'coloris'],
                             variation_category_list = ['morphologie/modele/060E404/C', 'morphologie/modele/060E404/B', 'taille/adulte/38', 'taille/adulte/40', 'taille/adulte/42', 'coloris/modele/060E404/Violet_rose', 'coloris/modele/060E404/noir_gris'])
    self.assertEqual(d1_line2.getPortalType(), delivery_line_type)
    cell = self.setCell(d1_line2,
                        ('coloris/modele/060E404/Violet_rose', 'morphologie/modele/060E404/C', 'taille/adulte/38'),
                        price = 5.0,
                        quantity = 1.0,
                        target_quantity = 1.0)
    self.assertNotEqual(cell, None)
    #self.assertNotEqual(cell.getPortalType(), 'Delivery Cell')
    cell = self.setCell(d1_line2,
                        ('coloris/modele/060E404/noir_gris', 'morphologie/modele/060E404/C', 'taille/adulte/40'),
                        price = 5.0,
                        quantity = 2.0,
                        target_quantity = 2.0)
    self.assertNotEqual(cell, None)
    d1_line2.recursiveImmediateReindexObject()
    self.assertAlmostEqual(d1_line2.getTotalPrice(), 5.0 * (1.0 + 2.0))
    self.assertAlmostEqual(d1_line2.getTotalQuantity(), 1.0 + 2.0)
    d1_line3 = d1.newContent(id='3', portal_type=delivery_line_type,
                               resource='modele/060E404',
                               price=0.0,
                               variation_base_category_list = ['taille', 'coloris'],
                               variation_category_list = ['coloris/modele/060E404/Violet_rose', 'taille/adulte/38', 'taille/adulte/40', 'taille/adulte/42', 'coloris/modele/060E404/noir_gris'])
    cell = self.setCell(d1_line3,
                        ('coloris/modele/060E404/Violet_rose', 'taille/adulte/40'),
                        price = 3.0,
                        quantity = 3.0,
                        target_quantity = 3.0)
    self.assertNotEqual(cell, None)
    cell = self.setCell(d1_line3,
                        ('coloris/modele/060E404/noir_gris', 'taille/adulte/42'),
                        price = 4.0,
                        quantity = 5.0,
                        target_quantity = 5.0)
    self.assertNotEqual(cell, None)
    d1.recursiveImmediateReindexObject()
    LOG('testFusion _makeDeliveries', 0, 'cell = %s, cell.getVariationCategoryList() = %s, cell.showDict() = %s' % (repr(cell), str(cell.getVariationCategoryList()), repr(cell.showDict())))

    d2 = module.newContent(id='2', portal_type=delivery_type)
    d2_line1 = d2.newContent(id='1', portal_type=delivery_line_type,
                               resource='modele/004C401',
                               price=7.0,
                               quantity=2.0,
                               target_quantity=2.0)
    d2_line2 = d2.newContent(id='2', portal_type=delivery_line_type,
                               resource='modele/060E404',
                               variation_base_category_list = ['morphologie', 'taille', 'coloris'],
                               variation_category_list = ['morphologie/modele/060E404/C', 'morphologie/modele/060E404/B', 'taille/adulte/36', 'taille/adulte/38', 'taille/adulte/40', 'coloris/modele/060E404/Violet_rose', 'coloris/modele/060E404/noir_gris'])
    cell = self.setCell(d2_line2,
                        ('coloris/modele/060E404/Violet_rose', 'morphologie/modele/060E404/C', 'taille/adulte/36'),
                        price = 5.0,
                        quantity = 1.0,
                        target_quantity = 1.0)
    self.assertNotEqual(cell, None)
    cell = self.setCell(d2_line2,
                        ('coloris/modele/060E404/noir_gris', 'morphologie/modele/060E404/C', 'taille/adulte/40'),
                        price = 5.0,
                        quantity = 2.0,
                        target_quantity = 2.0)
    self.assertNotEqual(cell, None)
    d2_line2.recursiveImmediateReindexObject()
    self.assertAlmostEqual(d2_line2.getTotalPrice(), 5.0 * (1.0 + 2.0))
    self.assertAlmostEqual(d2_line2.getTotalQuantity(), 1.0 + 2.0)
    d2.recursiveImmediateReindexObject()

    d3 = module.newContent(id='3', portal_type=delivery_type)
    d3_line1 = d3.newContent(id='1', portal_type=delivery_line_type,
                               resource='modele/060E404',
                               variation_base_category_list = ['morphologie', 'taille', 'coloris'],
                               variation_category_list = ['morphologie/modele/060E404/C', 'morphologie/modele/060E404/B', 'taille/adulte/44', 'coloris/modele/060E404/Violet_rose', 'coloris/modele/060E404/noir_gris'])
    cell = self.setCell(d3_line1,
                        ('coloris/modele/060E404/Violet_rose', 'morphologie/modele/060E404/C', 'taille/adulte/44'),
                        price = 3.0,
                        quantity = 3.0,
                        target_quantity = 3.0)
    self.assertNotEqual(cell, None)
    d3.recursiveImmediateReindexObject()

  def _checkDeliveries(self, d1, d2, d3):
    self.assertEqual(len(d1.objectIds()), 3)
    self.assertEqual(d2.getSimulationState(), 'cancelled')
    self.assertEqual(d3.getSimulationState(), 'cancelled')
    line1 = line2 = line3 = None
    for line in d1.contentValues():
      if line.getResource() == 'modele/004C401':
        line1 = line
      elif line.getResource() == 'modele/060E404':
        if 'morphologie' in line.getVariationBaseCategoryList():
          line2 = line
        else:
          line3 = line
    LOG('_checkDeliveries', 0, 'line1 = %s, line1.objectIds() = %s' % (repr(line1), repr(list(line1.objectIds()))))
    LOG('_checkDeliveries', 0, 'line2 = %s, line2.objectIds() = %s' % (repr(line2), repr(list(line2.objectIds()))))
    LOG('_checkDeliveries', 0, 'line3 = %s, line3.objectIds() = %s' % (repr(line3), repr(list(line3.objectIds()))))
    self.assertNotEqual(line1, None)
    self.assertAlmostEqual(line1.getTotalQuantity(), 1.0 + 2.0)
    self.assertAlmostEqual(line1.getTotalPrice(), 2.0 * 1.0 + 7.0 * 2.0)
    self.assertAlmostEqual(line1.getPrice(), line1.getTotalPrice() / line1.getTotalQuantity())
    self.assertNotEqual(line2, None)
    self.assertAlmostEqual(line2.getTotalQuantity(), 1.0 + 2.0 + 1.0 + 2.0 + 3.0)
    self.assertAlmostEqual(line2.getTotalPrice(), 5.0 * 1.0 + 5.0 * 2.0 + 5.0 * 1.0 + 5.0 * 2.0 + 3.0 * 3.0)
    category_list = list(line2.getVariationCategoryList())
    category_list.sort()
    self.assertEqual(category_list, ['coloris/modele/060E404/Violet_rose', 'coloris/modele/060E404/noir_gris', 'morphologie/modele/060E404/B', 'morphologie/modele/060E404/C', 'taille/adulte/36', 'taille/adulte/38', 'taille/adulte/40', 'taille/adulte/42', 'taille/adulte/44'])
    #self.assertAlmostEqual(line2.getPrice(), line2.getTotalPrice() / line2.getTotalQuantity())
    self.assertNotEqual(line3, None)
    self.assertAlmostEqual(line3.getTotalQuantity(), 3.0 + 5.0)
    self.assertAlmostEqual(line3.getTotalPrice(), 3.0 * 3.0 + 4.0 * 5.0)
    category_list = list(line3.getVariationCategoryList())
    category_list.sort()
    self.assertEqual(category_list, ['coloris/modele/060E404/Violet_rose', 'coloris/modele/060E404/noir_gris', 'taille/adulte/38', 'taille/adulte/40', 'taille/adulte/42'])
    #self.assertAlmostEqual(line3.getPrice(), line3.getTotalPrice() / line3.getTotalQuantity())

  def _testDeliveries(self, module, delivery_type, delivery_line_type, quiet=0, run=run_all_test):
    # Test mergeDeliveryList with Deliveries. This is shared among various deliveries.
    if not run: return
    if not quiet:
      message = '\n%s ' % delivery_type
      ZopeTestCase._print(message)
      LOG('Testing... ',0,message)
    portal_simulation = self.getSimulationTool()

    self.makeDeliveries(module, delivery_type, delivery_line_type)
    pl = portal_simulation.mergeDeliveryList([module['1'], module['2'], module['3']])
    pl.recursiveImmediateReindexObject()
    self._checkDeliveries(module['1'], module['2'], module['3'])

    self.makeDeliveries(module, delivery_type, delivery_line_type)
    pl = portal_simulation.mergeDeliveryList([module['2'], module['3'], module['1']])
    pl.recursiveImmediateReindexObject()
    self._checkDeliveries(module['2'], module['3'], module['1'])

    self.makeDeliveries(module, delivery_type, delivery_line_type)
    pl = portal_simulation.mergeDeliveryList([module['3'], module['1'], module['2']])
    pl.recursiveImmediateReindexObject()
    self._checkDeliveries(module['3'], module['1'], module['2'])

  """
  def test_03_SalesOrders(self, quiet=0, run=run_all_test):
    # Test mergeDeliveryList with Sales Orders
    module = self.getSalesOrderModule()
    self._testDeliveries(module, 'Sales Order', 'Sales Order Line', quiet=quiet, run=run)

  def test_04_SalesPackingLists(self, quiet=0, run=run_all_test):
    # Test mergeDeliveryList with Sales Packing Lists
    module = self.getSalesPackingListModule()
    self._testDeliveries(module, 'Sales Packing List', 'Sales Packing List Line', quiet=quiet, run=run)

  def test_06_PurchaseOrders(self, quiet=0, run=run_all_test):
    # Test mergeDeliveryList with Purchase Orders
    module = self.getPurchaseOrderModule()
    self._testDeliveries(module, 'Purchase Order', 'Purchase Order Line', quiet=quiet, run=run)

  def test_07_PurchasePackingLists(self, quiet=0, run=run_all_test):
    # Test mergeDeliveryList with Purchase Packing Lists
    module = self.getPurchasePackingListModule()
    self._testDeliveries(module, 'Purchase Packing List', 'Purchase Packing List Line', quiet=quiet, run=run)

  def test_08_ProductionOrders(self, quiet=0, run=run_all_test):
    # Test mergeDeliveryList with Production Orders
    module = self.getProductionOrderModule()
    self._testDeliveries(module, 'Production Order', 'Production Order Line', quiet=quiet, run=run)

  def test_09_ProductionPackingLists(self, quiet=0, run=run_all_test):
    # Test mergeDeliveryList with Production Packing Lists
    module = self.getProductionPackingListModule()
    self._testDeliveries(module, 'Production Packing List', 'Production Packing List Line', quiet=quiet, run=run)

  def test_10_ProductionReports(self, quiet=0, run=run_all_test):
    # Test mergeDeliveryList with Production Reports
    module = self.getProductionReportModule()
    self._testDeliveries(module, 'Production Report', 'Production Report Component', quiet=quiet, run=run)

  """
  def test_11_Containers(self, quiet=0, run=run_all_test):
    # Test Containers with Sales Packing Lists.
    module = self.getComposantModule()
    composant = module.newContent(id='CAame', portal_type='Composant',
                                  type_composant = 'Carton')
    variante = composant.newContent(id='A', portal_type='Variante Composant',
                                    source_base_price = 0.6,
                                    default_source_reference = 'A',
                                    base_height = 400.0,
                                    base_length = 600.0,
                                    base_width = 300.0,
                                    base_price = None,
                                    base_weight = None)
    composant.recursiveImmediateReindexObject()
    LOG('test_11_Containers', 0, 'composant = %s, composant.showDict() = %s, variante = %s, variante.showDict() = %s' % (repr(composant), repr(composant.showDict()), repr(variante), repr(variante.showDict())))
    module = self.getSalesPackingListModule()
    for id in ('1', '2'):
      if module.hasContent(id):
        module.deleteContent(id)
      d = module.newContent(id=id, portal_type='Sales Packing List')
      c = d.newContent(id='c1', portal_type='Container',
                       resource='composant/CAame',
                       serial_number = '0000640009',
                       gross_weight = 0.0,
                       price = 0.0,
                       variation_base_category_list = ['variante'],
                       variation_category_list = ['variante/composant/CAame/A'])
      l = c.newContent(id='1', portal_type='Container Line',
                       resource = 'modele/060E404',
                       price = 0.0,
                       variation_base_category_list = ['coloris', 'taille'],
                       variation_category_list = ['taille/adulte/42', 'coloris/modele/060E404/Violet_rose'])
      cell = self.setCell(l,
                          ('taille/adulte/42', 'coloris/modele/060E404/Violet_rose'),
                          target_quantity = 53.0)
      self.assertNotEqual(cell, None)
      d.recursiveImmediateReindexObject()
      self.assertAlmostEqual(d.getTargetTotalQuantity(), 53.0)
    portal_simulation = self.getSimulationTool()
    d = portal_simulation.mergeDeliveryList([module['1'], module['2']])
    d.recursiveImmediateReindexObject()
    self.assertEqual(len(d.objectIds()), 2)
    self.assertAlmostEqual(d.getTargetTotalQuantity(), 53.0 * 2)

  def test_12_SaleInvoiceTransactions(self, quiet=0, run=run_all_test):
    # Test Sale Invoice Transacations.
    module = self.getAssortimentModule()
    assortiment = module.newContent(id='712C405UNI_12P', portal_type='Assortiment')
    assortiment = module.newContent(id='GALEC_067C403GLC(38-48)_12p', portal_type='Assortiment')
    assortiment.newContent(id='aura')
    assortiment.newContent(id='curaco')
    module = self.getSaleInvoiceTransactionModule()
    for id in ('1', '2'):
      if module.hasContent(id):
        module.deleteContent(id)
    i1 = module.newContent(id='1', portal_type='Sale Invoice Transaction')
    l = i1.newContent(id='1', portal_type='Invoice Line',
                      resource = 'assortiment/712C405UNI_12P',
                      quantity_unit = 'Unite',
                      price = 52.8,
                      quantity = 2.0,
                      variation_base_category_list = (),
                      variation_category_list = ())
    self.assertAlmostEqual(l.getPrice(), 52.8)
    self.assertAlmostEqual(l.getQuantity(), 2.0)
    l = i1.newContent(id='2', portal_type='Invoice Line',
                      resource = 'assortiment/GALEC_067C403GLC(38-48)_12p',
                      quantity_unit = 'Unite',
                      price = 0.0,
                      variation_base_category_list = ('coloris',),
                      variation_category_list = ('coloris/assortiment/GALEC_067C403GLC(38-48)_12p/aura', 'coloris/assortiment/GALEC_067C403GLC(38-48)_12p/curaco'))
    cell = self.setCell(l,
                        ('coloris/assortiment/GALEC_067C403GLC(38-48)_12p/aura',),
                        price = 67.0,
                        quantity = 1.0)
    self.assertNotEqual(cell, None)
    self.assertAlmostEqual(cell.getPrice(), 67.0)
    self.assertAlmostEqual(cell.getQuantity(), 1.0)
    cell = self.setCell(l,
                        ('coloris/assortiment/GALEC_067C403GLC(38-48)_12p/curaco',),
                        price = 67.0,
                        quantity = 1.0)
    self.assertNotEqual(cell, None)
    i1.recursiveImmediateReindexObject()
    i2 = module.newContent(id='2', portal_type='Sale Invoice Transaction')
    i2.newContent(id='1', portal_type='Invoice Line',
                  resource = 'assortiment/712C405UNI_12P',
                  quantity_unit = 'Unite',
                  price = 32.8,
                  quantity = 2.0,
                  variation_base_category_list = (),
                  variation_category_list = ())
    l = i2.newContent(id='2', portal_type='Invoice Line',
                      resource = 'assortiment/GALEC_067C403GLC(38-48)_12p',
                      quantity_unit = 'Unite',
                      price = 0.0,
                      variation_base_category_list = ('coloris',),
                      variation_category_list = ('coloris/assortiment/GALEC_067C403GLC(38-48)_12p/aura', 'coloris/assortiment/GALEC_067C403GLC(38-48)_12p/curaco'))
    cell = self.setCell(l,
                        ('coloris/assortiment/GALEC_067C403GLC(38-48)_12p/aura',),
                        price = 67.0,
                        quantity = 2.0)
    self.assertNotEqual(cell, None)
    cell = self.setCell(l,
                        ('coloris/assortiment/GALEC_067C403GLC(38-48)_12p/curaco',),
                        price = 67.0,
                        quantity = 3.0)
    self.assertNotEqual(cell, None)
    i2.recursiveImmediateReindexObject()
    portal_simulation = self.getSimulationTool()
    d = portal_simulation.mergeDeliveryList([i1, i2])
    d.recursiveImmediateReindexObject()
    LOG('test_12_SaleInvoiceTransactions', 0, 'd.getUid() = %s' % repr(d.getUid()))
    self.assertEqual(len(d.objectIds()), 3)
    self.assertAlmostEqual(d.getTotalPrice(), 52.8 * 2.0 + 32.8 * 2.0 + 67.0 * (1.0 + 1.0 + 2.0 + 3.0))



if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestFusion))
        return suite

