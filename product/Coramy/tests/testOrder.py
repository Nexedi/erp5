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
import random

class Step:

  def __init__(self,method_name='',required=1,max_replay=1):
    self._method_name = method_name
    self._required = required
    self._max_replay = max_replay

  def play(self,context,sequence=None):
    method_name = 'step' + self._method_name
    method = getattr(context,method_name)
    # We can in same cases replay many times the same step,
    # or not playing it at all
    nb_replay = random.randrange(0,self._max_replay+1)
    if self._required:
      if nb_replay==0:
        nb_replay=1
    for i in range(0,nb_replay):
      ZopeTestCase._print('\n  Playing step... %s' % self._method_name)
      LOG('Step.play',0,'Playing step... %s' % self._method_name)
      method(sequence=sequence)
    
class Sequence:

  def __init__(self):
    self._step_list = []
    self._dict = {}

  def play(self,context,sequence=None):
    ZopeTestCase._print('\nStarting New Sequence... ')
    LOG('Sequence.play',0,'Starting New Sequence... ')
    if sequence is None:
      for step in self._step_list:
        step.play(context,sequence=self)
        # commit transaction after each step
        get_transaction().commit()

  def addStep(self,method_name,required=1,max_replay=1):
    new_step = Step(method_name=method_name,
                    required=required,max_replay=max_replay)
    self._step_list.append(new_step)

  def set(self, keyword,value):
    self._dict[keyword]=value

  def edit(self, **kw):
    for k, v in kw.items():
      self._dict[k]=v

  def get(self, keyword):
    if self._dict.has_key(keyword):
      return self._dict[keyword]
    return None

class SequenceList:

  def __init__(self):
    self._sequence_list = []

  def addSequence(self,sequence):
    self._sequence_list.append(sequence)

  def addSequenceString(self,sequence_string):
    """
    The sequence string should be a string of method names
    separated by spaces
    """
    step_list = sequence_string.split(' ')
    self.addSequenceStringList(step_list)

  def addSequenceStringList(self,step_list):
    step_list
    sequence = Sequence()
    for step in step_list:
      sequence.addStep(step)
    self.addSequence(sequence)

  def play(self, context):
    for sequence in self._sequence_list:
      sequence.play(context)

  

class TestOrder(ERP5TypeTestCase):

  # Different variables used for this test
  run_all_test = 1
  source_company_id = 'Nexedi'
  sale_manager_id = 'seb'
  destination_company_stock = 'site/Stock_MP/Gravelines'
  destination_company_group = 'group/Coramy'
  first_name1 = 'Sebastien'
  last_name1 = 'Robin'
  destination_company_id = 'Coramy'
  component_id = 'brick'
  sales_order_id = '1'
  purchase_order_id = '1'
  quantity = 10
  modele_id = '001B402'
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

  def getPersonModule(self):
    return getattr(self.getPortal(), 'person', None)

  def getOrganisationModule(self):
    return getattr(self.getPortal(), 'organisation', None)

  def getModeleModule(self):
    return getattr(self.getPortal(), 'modele', None)

  def getPurchaseOrderModule(self):
    return getattr(self.getPortal(), 'commande_achat', None)

  def getPurchasePackingListModule(self):
    return getattr(self.getPortal(), 'livraison_achat', None)

  def getSalesPackingListModule(self):
    return getattr(self.getPortal(), 'livraison_vente', None)

  def getSalesOrderModule(self):
    return getattr(self.getPortal(), 'commande_vente', None)

  def getComponentModule(self):
    return getattr(self.getPortal(), 'composant', None)

  def getPortalId(self):
    return self.getPortal().getId()

  def afterSetUp(self, quiet=1, run=1):
    self.login()
    portal = self.getPortal()
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()
    # First set Acquisition
    portal.ERP5_setAcquisition()
    # Then reindex
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
    organisation_module = self.getOrganisationModule()
    o1 = organisation_module.newContent(id=self.source_company_id)
    o2 = organisation_module.newContent(id=self.destination_company_id)
    component_module = self.getComponentModule()
    c1 = component_module.newContent(id=self.component_id)
    c1.setBasePrice(self.base_price)
    person_module = self.getPersonModule()
    p1 = person_module.newContent(id=self.sale_manager_id)
    kw = {'first_name':self.first_name1,'last_name':self.last_name1}
    p1.edit(**kw)
    modele_module = self.getModeleModule()
    modele = modele_module.newContent(id=self.modele_id)
    # Add variation to the modele
    variante_modele_1 = modele.newContent(id='1',portal_type='Variante Modele')
    variante_modele_2 = modele.newContent(id='2',portal_type='Variante Modele')

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def stepAddPurchaseOrder(self, sequence=None, sequence_list=None,**kw):
    # Test if we can add a complete sales order
    purchase_module = self.getPurchaseOrderModule()
    purchase_order = purchase_module.newContent(portal_type='Purchase Order')
    sequence.edit(purchase_order=purchase_order)
    source_company = self.getOrganisationModule()._getOb(self.source_company_id)
    destination_company = self.getOrganisationModule()._getOb(self.destination_company_id)
    sale_manager = self.getPersonModule()._getOb(self.sale_manager_id)
    # Set date
    date = DateTime() # the value is now 
    target_start_date = date + 10 # Add 10 days
    target_stop_date = date + 12 # Add 12 days
    purchase_order.setTargetStartDate(target_start_date)
    purchase_order.setTargetStopDate(target_stop_date)
    # Set Profile
    portal_categories = self.getCategoriesTool()
    stock_category = portal_categories.resolveCategory(self.destination_company_stock)
    group_category = portal_categories.resolveCategory(self.destination_company_group)
    purchase_order.setSourceValue(source_company)
    purchase_order.setSourceSectionValue(source_company)
    purchase_order.setSourceDecisionValue(source_company)
    purchase_order.setSourceAdministrationValue(source_company)
    purchase_order.setSourcePaymentValue(source_company)
    purchase_order.setDestinationValue(stock_category)
    purchase_order.setDestinationSectionValue(group_category)
    purchase_order.setDestinationDecisionValue(destination_company)
    purchase_order.setDestinationAdministrationValue(destination_company)
    purchase_order.setDestinationPaymentValue(destination_company)
    purchase_order.setDestinationAdministrationValue(sale_manager)
    # Add a purchase order line
    purchase_order_line = purchase_order.newContent(id='1',portal_type='Purchase Order Line')
    component_module = self.getComponentModule()
    component = component_module._getOb(self.component_id)
    purchase_order_line.setResourceValue(component)
    self.assertEquals(purchase_order_line.getResourceValue(),component)
    purchase_order_line.setTargetQuantity(self.quantity)
    # Look if the profile is good 
    self.failUnless(purchase_order.getSourceValue()!=None)
    self.failUnless(purchase_order.getDestinationValue()!=None)
    self.failUnless(purchase_order.getSourceSectionValue()!=None)
    self.failUnless(purchase_order.getDestinationSectionValue()!=None)
    self.failUnless(purchase_order.getSourceDecisionValue()!=None)
    self.failUnless(purchase_order.getDestinationDecisionValue()!=None)
    self.failUnless(purchase_order.getSourceAdministrationValue()!=None)
    self.failUnless(purchase_order.getDestinationAdministrationValue()!=None)
    self.failUnless(purchase_order.getSourcePaymentValue()!=None)
    self.failUnless(purchase_order.getDestinationPaymentValue()!=None)
    # See what's the output of Order_lightControl
    result=purchase_order.Order_lightControl()
    self.assertEquals(result,'')
      
  def stepAddPurchaseOrderVariated(self, sequence=None, sequence_list=None,**kw):
    self.AddPurchaseOrder(sequence=sequence,sequence_list=sequence_list,**kw)
      
  def stepConfirmPurchaseOrder(self, sequence=None,sequence_list=None):
    purchase_order = sequence.get('purchase_order')
    purchase_order.confirm()

  def stepOrderPurchaseOrder(self, sequence=None,sequence_list=None):
    purchase_order = sequence.get('purchase_order')
    purchase_order.order()

  def stepPlanPurchaseOrder(self, sequence=None, sequence_list=None, **kw):
    portal = self.getPortal()
    purchase_order = sequence.get('purchase_order')
    purchase_order.plan()

  def stepCheckConfirmPurchaseOrder(self, sequence=None, sequence_list=None, **kw):
    purchase_order = sequence.get('purchase_order')
    purchase_order_line = purchase_order._getOb('1')
    simulation_tool = self.getSimulationTool()
    sql_connection = self.getSqlConnection()
    simulation_object_list = simulation_tool.objectValues()
    self.failUnless(len(simulation_object_list)>0)
    simulation_object = None
    for o in simulation_object_list:
      if o.getCausalityValue()==purchase_order:
        simulation_object = o
    self.assertNotEquals(simulation_object,None)
    sequence.edit(simulation_object=simulation_object)
    # Check if there is a line on the packing_list
    # And if this line get all informations
    line_list = simulation_object.objectValues()
    self.assertEquals(len(line_list),1)
    line = line_list[0]
    component_module = self.getComponentModule()
    component = component_module._getOb(self.component_id)
    self.assertEquals(line.getQuantity(),self.quantity)
    self.assertEquals(line.getOrderValue(),purchase_order_line)

  def stepActivateRequirementList(self, sequence=None, sequence_list=None, **kw):
    portal = self.getPortal()
    result = portal.SimulationTool_activateRequirementList()
    result = result.replace('\n','')
    # XXX This does not work yet
    self.assertEquals(result,'')

  def stepCheckActivateRequirementList(self, sequence=None, sequence_list=None, **kw):
    packing_list_module = self.getPurchasePackingListModule()
    purchase_order = sequence.get('purchase_order')
    packing_list_list = packing_list_module.objectValues()
    packing_list = None
    for o in packing_list_list:
      if o.getCausalityValue()==purchase_order:
        packing_list=o
    self.assertNotEquals(packing_list,None)
    sequence.edit(packing_list=packing_list)
    # Check if there is a line on the packing_list
    # And if this line get all informations
    line_list = packing_list.objectValues()
    self.assertEquals(len(line_list),1)
    line = line_list[0]
    component_module = self.getComponentModule()
    component = component_module._getOb(self.component_id)
    self.assertEquals(line.getResourceValue(),component)
    self.assertEquals(line.getTotalQuantity(),self.quantity)


      
  def stepTic(self,**kw):
    portal = self.getPortal()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()

  def testOrder(self, quiet=0,run=1):
    sequence_list = SequenceList()
    sequence_string =   'AddPurchaseOrder Tic PlanPurchaseOrder Tic ConfirmPurchaseOrder Tic CheckConfirmPurchaseOrder ' \
                      + 'Tic ActivateRequirementList Tic CheckActivateRequirementList'
    sequence_list.addSequenceString(sequence_string)
    sequence_string =   'AddPurchaseOrder Tic ConfirmPurchaseOrder Tic CheckConfirmPurchaseOrder ' \
                      + 'Tic ActivateRequirementList Tic CheckActivateRequirementList'
    sequence_list.addSequenceString(sequence_string)
    #sequence_string =   'AddPurchaseOrder ConfirmPurchaseOrder OrderPurchaseOrder ' \
    #                  + 'CheckConfirmPurchaseOrder ActivateRequirementList CheckActivateRequirementList'
    #sequence_list.addSequenceString(sequence_string)
    # Now add a non defined sequence
    sequence = Sequence()
    sequence.addStep('AddPurchaseOrder')
    sequence.addStep('Tic',required=0,max_replay=5)
    sequence.addStep('PlanPurchaseOrder',required=0)
    sequence.addStep('Tic',required=0,max_replay=5)
    sequence.addStep('OrderPurchaseOrder',required=0)
    sequence.addStep('Tic',required=0,max_replay=5)
    sequence.addStep('ConfirmPurchaseOrder')
    sequence.addStep('Tic',required=0,max_replay=5)
    sequence.addStep('CheckConfirmPurchaseOrder')
    sequence.addStep('ActivateRequirementList')
    sequence.addStep('Tic',required=0,max_replay=5)
    sequence_list.addSequence(sequence)
    # Finally play the three sequences
    sequence_list.play(self)

"""
bad sequence
Starting New Sequence... 
  Playing step... AddPurchaseOrder
  Playing step... Tic
  Playing step... ConfirmPurchaseOrder
  Playing step... Tic
  Playing step... Tic
  Playing step... Tic
  Playing step... Tic
  Playing step... Tic
  Playing step... OrderPurchaseOrder
  Playing step... Tic
  Playing step... Tic
  Playing step... Tic
  Playing step... Tic
  Playing step... Tic
  Playing step... CheckConfirmPurchaseOrderF


Erreur dans checkConfirmPurchaseOrder
    self.assertEquals(len(line_list),1)

"""


# movement


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

#  def testAddSalesOrder(self, quiet=0, run=0):
#    # Test if we can add a complete sales order
#    if not run: return
#    if not quiet:
#      ZopeTestCase._print('\nTest Add Sales Order ')
#      LOG('Testing... ',0,'testAddSalesOrder')
#    # Test if we can add a complete sales order
#    sales_module = self.getSalesModule()
#    sales_order = sales_module.newContent(id=self.sales_order_id,portal_type='Sales Order')
#    source_company = self.getOrganisationModule()._getOb(self.source_company_id)
#    sales_order.setSourceValue(source_company)
#    destination_company = self.getOrganisationModule()._getOb(self.destination_company_id)
#    sales_order.setDestinationValue(destination_company)
#    # Set date
#    date = DateTime() # the value is now 
#    target_start_date = date + 10 # Add 10 days
#    target_stop_date = date + 12 # Add 12 days
#    sales_order.setTargetStartDate(target_start_date)
#    sales_order.setTargetStopDate(target_stop_date)
#    # Set Profile
#    sales_order.setSourceValue(source_company)
#    sales_order.setSourceSectionValue(source_company)
#    sales_order.setSourceDecisionValue(source_company)
#    sales_order.setSourceAdministrationValue(source_company)
#    sales_order.setSourcePaymentValue(source_company)
#    sales_order.setDestinationValue(destination_company)
#    sales_order.setDestinationSectionValue(destination_company)
#    sales_order.setDestinationDecisionValue(destination_company)
#    sales_order.setDestinationAdministrationValue(destination_company)
#    sales_order.setDestinationPaymentValue(destination_company)
#    # Add a sales order line
#    sales_order_line = sales_order.newContent(id='1',portal_type='Sales Order Line')
#    component_module = self.getComponentModule()
#    component = component_module._getOb(self.component_id)
#    sales_order_line.setResourceValue(component)
#    self.assertEquals(sales_order_line.getResourceValue(),component)
#    sales_order_line.setTargetQuantity(self.quantity)
#    # Look if the profile is good 
#    self.failUnless(sales_order.getSourceValue()!=None)
#    self.failUnless(sales_order.getDestinationValue()!=None)
#    self.failUnless(sales_order.getSourceSectionValue()!=None)
#    self.failUnless(sales_order.getDestinationSectionValue()!=None)
#    self.failUnless(sales_order.getSourceDecisionValue()!=None)
#    self.failUnless(sales_order.getDestinationDecisionValue()!=None)
#    self.failUnless(sales_order.getSourceAdministrationValue()!=None)
#    self.failUnless(sales_order.getDestinationAdministrationValue()!=None)
#    self.failUnless(sales_order.getSourcePaymentValue()!=None)
#    self.failUnless(sales_order.getDestinationPaymentValue()!=None)
#    # See what's the output of Order_lightControl
#    result=sales_order.Order_lightControl()
#    self.assertEquals(result,'')
#    sales_order.confirm()


#  def testPlanSimpleOrder(self, quiet=0, run=0):
#    # Test if we can add a complete sales order
#    if not run: return
#    if not quiet:
#      ZopeTestCase._print('\nTest Plan Simple Order ')
#      LOG('Testing... ',0,'testPlanSimpleOrder')
#    portal = self.getPortal()
#    self.testAddSalesOrder(quiet=1,run=1)
#    sales_module = self.getSalesModule()
#    sales_order = sales_module._getOb(self.sales_order_id)
#    sales_order_line = sales_order._getOb('1')
#    #self.assertEquals(len(sales_order_line.objectValues()),0)
#    # Test Before if there is uid on portal_simulation
#    simulation_tool = self.getSimulationTool()
#    LOG('testPlanSimpleOrder.CHECK',0,portal.portal_simulation.uid)
#    LOG('testPlanSimpleOrder.CHECK2',0,getattr(aq_base(simulation_tool),'uid',None))
#    #LOG('testPlanSimpleOrder',0,'portal.portal_simulation.immediateReindexObject')
#    #LOG('testPlanSimpleOrder, portal_simulation',0,simulation_tool)
#    sql_connection = self.getSqlConnection()
#    sql = 'select uid from catalog'
#    result = sql_connection.manage_test(sql)
#    uid_list = map(lambda x: x['uid'],result)
#    LOG('testPlanSimpleOrder, uid_list',0,uid_list)
#    portal_id = self.getPortalId()
#    #simulation_tool.immediateReindexObject()
#    # Get the movement index
#    #LOG('testPlanSimpleOrder, movementIndex:',0,sales_order.getMovementIndex())
#    for m in portal.portal_activities.getMessageList():
#      portal.portal_activities.invoke(m)
#      LOG('Testing... message:',0,m)
#    sales_order.plan()
#    simulation_tool = self.getSimulationTool()
#    simulation_object_list = simulation_tool.objectValues()
#    self.assertEquals(len(simulation_object_list),1)
#    simulation_object = simulation_object_list[0]
#    self.assertEquals(simulation_object.getCausalityValue(),sales_order)
#    # See what's the output of Order_heavyControl
#    result=sales_order.Order_heavyControl()
#    self.assertEquals(result,'')
#    source_state_list = ('auto_planned', 'planned', 'ordered', 'confirmed', \
#                         'getting_ready', 'ready', 'started', 'stopped', 'delivered', 'invoiced')
#    inventory_list = portal.SimulationTool_getGroupFutureInventoryList(simulation_state=source_state_list)
#    for inventory in inventory_list:
#      LOG('inventory.inventory',0,inventory['inventory'])
#      LOG('inventory.section_title',0,inventory['section_title'])
#      LOG('inventory.resource_title',0,inventory['resource_title'])
#      LOG('inventory.resource_relative_url',0,inventory['resource_relative_url'])
#      LOG('inventory.path',0,inventory['path'])
#      LOG('inventory.variation_text',0,inventory['variation_text'])
#    LOG('Testing... inventory_list',0,inventory_list)
#    result = portal.SimulationTool_activateRequirementList()
#    LOG('Testing... SimulationTool_activateRequirementList:',0,result)
#    portal.portal_activities.distribute()
#    portal.portal_activities.tic()
#    for m in portal.portal_activities.getMessageList():
#      LOG('Testing... message:',0,m)
#      portal.portal_activities.invoke(m)

#  def testHasEverything(self, quiet=0, run=run_all_test):
#    # Test if portal_synchronizations was created
#    if not run: return
#    if not quiet:
#      ZopeTestCase._print('\nTest Has Everything ')
#      LOG('Testing... ',0,'testHasEverything')
#    self.failUnless(self.getCategoriesTool()!=None)
#    self.failUnless(self.getPersonModule()!=None)
#    self.failUnless(self.getOrganisationModule()!=None)
#    self.failUnless(self.getSalesModule()!=None)
#    self.failUnless(self.getComponentModule()!=None)
#    self.failUnless(self.getSimulationTool()!=None)
