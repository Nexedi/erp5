##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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

class TestOrder(ERP5TypeTestCase):

  # Different variables used for this test
  run_all_test = 1
  source_company_id = 'Nexedi'
  destination_company_id = 'Coramy'
  component_id = 'brick'
  sales_order_id = '1'
  quantity = 10
  base_price = 0.7832

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
    return ('erp5_crm','coramy_order')

  def getCategoriesTool(self):
    return getattr(self.getPortal(), 'portal_categories', None)

  def getCatalogTool(self):
    return getattr(self.getPortal(), 'portal_catalog', None)

  def getSqlConnection(self):
    return getattr(self.getPortal(), 'erp5_sql_connection', None)

  def getTypesTool(self):
    return getattr(self.getPortal(), 'portal_types', None)

  def getSimulationTool(self):
    return getattr(self.getPortal(), 'portal_simulation', None)

  def getRuleTool(self):
    return getattr(self.getPortal(), 'portal_Rules', None)

  def getPersonModule(self):
    return getattr(self.getPortal(), 'person', None)

  def getOrganisationModule(self):
    return getattr(self.getPortal(), 'organisation', None)

  def getSalesModule(self):
    return getattr(self.getPortal(), 'commande_vente', None)

  def getComponentModule(self):
    return getattr(self.getPortal(), 'composant', None)

  def getPortalId(self):
    return self.getPortal().getId()

  def testHasEverything(self, quiet=0, run=run_all_test):
    # Test if portal_synchronizations was created
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Has Everything ')
      LOG('Testing... ',0,'testHasEverything')
    self.failUnless(self.getCategoriesTool()!=None)
    self.failUnless(self.getPersonModule()!=None)
    self.failUnless(self.getOrganisationModule()!=None)
    self.failUnless(self.getSalesModule()!=None)
    self.failUnless(self.getComponentModule()!=None)
    self.failUnless(self.getSimulationTool()!=None)

  #def populate(self, quiet=1, run=1):
  def afterSetUp(self, quiet=1, run=1):
    self.login()
    portal = self.getPortal()
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()
    # First reindex
    # portal.ERP5Site_reindexAll()
    LOG('afterSetup',0,'portal.portal_categories.immediateReindexObject')
    portal.portal_categories.immediateReindexObject()
    for o in portal.portal_categories.objectValues():
      o.recursiveImmediateReindexObject()
    LOG('afterSetup',0,'portal.portal_simulation.immediateReindexObject')
    portal.portal_simulation.immediateReindexObject()
    for o in portal.portal_simulation.objectValues():
      o.recursiveImmediateReindexObject()
    LOG('afterSetup',0,'portal.portal_rules.immediateReindexObject')
    portal.portal_rules.immediateReindexObject()
    # Then add new components
    portal.portal_types.constructContent(type_name='Person Module',
                                       container=portal,
                                       id='person')
    portal.portal_types.constructContent(type_name='Organisation Module',
                                       container=portal,
                                       id='organisation')
    portal.portal_types.constructContent(type_name='Sales Order Module',
                                       container=portal,
                                       id='commande_vente')
    portal.portal_types.constructContent(type_name='Purchase Order Module',
                                       container=portal,
                                       id='commande_achat')
    portal.portal_types.constructContent(type_name='Composant Module',
                                       container=portal,
                                       id='composant')
    portal.portal_types.constructContent(type_name='Production Order Module',
                                       container=portal,
                                       id='ordre_fabrication')
    organisation_module = self.getOrganisationModule()
    o1 = organisation_module.newContent(id=self.source_company_id)
    o2 = organisation_module.newContent(id=self.destination_company_id)
    component_module = self.getComponentModule()
    c1 = component_module.newContent(id=self.component_id)
    c1.setBasePrice(self.base_price)

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def testAddSalesOrder(self, quiet=0, run=0):
    # Test if we can add a complete sales order
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Add Sales Order ')
      LOG('Testing... ',0,'testAddSalesOrder')
    # Test if we can add a complete sales order
    sales_module = self.getSalesModule()
    sales_order = sales_module.newContent(id=self.sales_order_id,portal_type='Sales Order')
    source_company = self.getOrganisationModule()._getOb(self.source_company_id)
    sales_order.setSourceValue(source_company)
    destination_company = self.getOrganisationModule()._getOb(self.destination_company_id)
    sales_order.setDestinationValue(destination_company)
    # Set date
    date = DateTime() # the value is now 
    target_start_date = date + 10 # Add 10 days
    target_stop_date = date + 12 # Add 12 days
    sales_order.setTargetStartDate(target_start_date)
    sales_order.setTargetStopDate(target_stop_date)
    # Set Profile
    sales_order.setSourceValue(source_company)
    sales_order.setSourceSectionValue(source_company)
    sales_order.setSourceDecisionValue(source_company)
    sales_order.setSourceAdministrationValue(source_company)
    sales_order.setSourcePaymentValue(source_company)
    sales_order.setDestinationValue(destination_company)
    sales_order.setDestinationSectionValue(destination_company)
    sales_order.setDestinationDecisionValue(destination_company)
    sales_order.setDestinationAdministrationValue(destination_company)
    sales_order.setDestinationPaymentValue(destination_company)
    # Add a sales order line
    sales_order_line = sales_order.newContent(id='1',portal_type='Sales Order Line')
    component_module = self.getComponentModule()
    component = component_module._getOb(self.component_id)
    sales_order_line.setResourceValue(component)
    self.assertEquals(sales_order_line.getResourceValue(),component)
    sales_order_line.setTargetQuantity(self.quantity)
    # Look if the profile is good 
    self.failUnless(sales_order.getSourceValue()!=None)
    self.failUnless(sales_order.getDestinationValue()!=None)
    self.failUnless(sales_order.getSourceSectionValue()!=None)
    self.failUnless(sales_order.getDestinationSectionValue()!=None)
    self.failUnless(sales_order.getSourceDecisionValue()!=None)
    self.failUnless(sales_order.getDestinationDecisionValue()!=None)
    self.failUnless(sales_order.getSourceAdministrationValue()!=None)
    self.failUnless(sales_order.getDestinationAdministrationValue()!=None)
    self.failUnless(sales_order.getSourcePaymentValue()!=None)
    self.failUnless(sales_order.getDestinationPaymentValue()!=None)
    # See what's the output of Order_lightControl
    result=sales_order.Order_lightControl()
    self.assertEquals(result,'')

  def testPlanSimpleOrder(self, quiet=0, run=run_all_test):
    # Test if we can add a complete sales order
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Plan Simple Order ')
      LOG('Testing... ',0,'testPlanSimpleOrder')
    portal = self.getPortal()
    self.testAddSalesOrder(quiet=1,run=1)
    sales_module = self.getSalesModule()
    sales_order = sales_module._getOb(self.sales_order_id)
    sales_order_line = sales_order._getOb('1')
    #self.assertEquals(len(sales_order_line.objectValues()),0)
    # Test Before if there is uid on portal_simulation
    simulation_tool = self.getSimulationTool()
    LOG('testPlanSimpleOrder.CHECK',0,portal.portal_simulation.uid)
    LOG('testPlanSimpleOrder.CHECK2',0,getattr(aq_base(simulation_tool),'uid',None))
    #LOG('testPlanSimpleOrder',0,'portal.portal_simulation.immediateReindexObject')
    #LOG('testPlanSimpleOrder, portal_simulation',0,simulation_tool)
    sql_connection = self.getSqlConnection()
    sql = 'select uid from catalog'
    result = sql_connection.manage_test(sql)
    uid_list = map(lambda x: x['uid'],result)
    LOG('testPlanSimpleOrder, uid_list',0,uid_list)
    portal_id = self.getPortalId()
    #simulation_tool.immediateReindexObject()
    # Get the movement index
    #LOG('testPlanSimpleOrder, movementIndex:',0,sales_order.getMovementIndex())
    sales_order.plan()
    simulation_tool = self.getSimulationTool()
    simulation_object_list = simulation_tool.objectValues()
    self.assertEquals(len(simulation_object_list),1)
    simulation_object = simulation_object_list[0]
    self.assertEquals(simulation_object.getCausalityValue(),sales_order)
    # See what's the output of Order_heavyControl
    result=sales_order.Order_heavyControl()
    self.assertEquals(result,'')
    source_state_list = ('auto_planned', 'planned', 'ordered', 'confirmed', \
                         'getting_ready', 'ready', 'started', 'stopped', 'delivered', 'invoiced')
    inventory_list = portal.SimulationTool_getGroupFutureInventoryList(simulation_state=source_state_list)
    for inventory in inventory_list:
      LOG('inventory.inventory',0,inventory['inventory'])
      LOG('inventory.section_title',0,inventory['section_title'])
      LOG('inventory.resource_title',0,inventory['resource_title'])
      LOG('inventory.resource_relative_url',0,inventory['resource_relative_url'])
      LOG('inventory.path',0,inventory['path'])
      LOG('inventory.variation_text',0,inventory['variation_text'])
    LOG('Testing... inventory_list',0,inventory_list)
    portal.SimulationTool_activateRequirementList()
    #portal.portal_activities.tic()


# vérifier quand confirmé, que les délivery sont bien créées

# essayer en mode actif, combiner des morceaux de unit test précédent,
#a, b, tic, e, tic, f, tic
# genre on confirme quand l'applied rule n'est pas faite (elle est en faite
# dans le portal_activities




if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestOrder))
        return suite

