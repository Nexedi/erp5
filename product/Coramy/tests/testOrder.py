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
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
import time
  

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
  component_id2 = 'tissu'
  sales_order_id = '1'
  purchase_order_id = '1'
  quantity = 10
  low_quantity = 4
  modele_id1 = '001B402'
  base_price1 = 0.7832
  base_price2 = 5.3349
  variante_id1 = 'variante_1'
  variante_id2 = 'variante_2'
  taille_list1 = ('taille/adulte/36','taille/adulte/40','taille/adulte/42')
  variation_base_category_list1 = ('coloris','taille')
  variation_category_list1 = ('coloris/modele/%s/%s' % (modele_id1,variante_id1),
                              'coloris/modele/%s/%s' % (modele_id1,variante_id2),
                              'taille/adulte/40','taille/adulte/42')

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
    return ('erp5_crm','coramy_catalog','coramy_order')

  def convertToLowerCase(self, key):
    """
      This function returns an attribute name 
      thanks to the name of a class
      for example convert 'Purchase Order' to 'purchase_order' 
    """
    result = key.lower()
    result = result.replace(' ','_')
    return result


  def getPersonModule(self):
    return getattr(self.getPortal(), 'person', None)

  def getOrganisationModule(self):
    return getattr(self.getPortal(), 'organisation', None)

  def getModeleModule(self):
    return getattr(self.getPortal(), 'modele', None)

  def getTransformationModule(self):
    return getattr(self.getPortal(), 'transformation', None)

  def getPurchaseOrderModule(self):
    return getattr(self.getPortal(), 'commande_achat', None)

  def getPurchasePackingListModule(self):
    return getattr(self.getPortal(), 'livraison_achat', None)

  def getSalesPackingListModule(self):
    return getattr(self.getPortal(), 'livraison_vente', None)

  def getSalesOrderModule(self):
    return getattr(self.getPortal(), 'commande_vente', None)

  def getTissuModule(self):
    return getattr(self.getPortal(), 'tissu', None)

  def getTransformationModule(self):
    return getattr(self.getPortal(), 'transformation', None)

  def getComponentModule(self):
    return getattr(self.getPortal(), 'composant', None)

  def getPortalId(self):
    return self.getPortal().getId()

  def failIfDifferentSet(self, a,b):
    for i in a:
      self.failUnless(i in b)
    for i in b:
      self.failUnless(i in a)
    self.assertEquals(len(a),len(b))

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
    c1.setBasePrice(self.base_price1)
    c1.setPrice(self.base_price1)
    c1 = component_module.newContent(id=self.component_id2)
    c1.setBasePrice(self.base_price2)
    c1.setPrice(self.base_price2)
    person_module = self.getPersonModule()
    p1 = person_module.newContent(id=self.sale_manager_id)
    kw = {'first_name':self.first_name1,'last_name':self.last_name1}
    p1.edit(**kw)
    modele_module = self.getModeleModule()
    # Define a modele
    modele = modele_module.newContent(id=self.modele_id1)
    modele.setTailleList(self.taille_list1)
    # Add variation to the modele
    variante_modele_1 = modele.newContent(id=self.variante_id1,portal_type='Variante Modele')
    variante_modele_2 = modele.newContent(id=self.variante_id2,portal_type='Variante Modele')
    # Create a Transformation
    transformation_module = self.getTransformationModule()
    transformation = transformation_module.newContent(id=self.modele_id1,portal_type='Transformation')
    transformation.setResourceValue(modele)

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager','Superviseur'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def constructEmptyOrder(self, sequence=None, sequence_list=None,order_type=None,**kw):
    # create a complete order
    #sales_module = self.getSalesOrderModule()
    method_name = 'get' + order_type.replace(' ','') + 'Module'
    method = getattr(self,method_name)
    order_module = method()
    order = order_module.newContent(portal_type=order_type)
    sequence.edit(order=order)
    portal = self.getPortal()
    source_company = self.getOrganisationModule()._getOb(self.source_company_id)
    destination_company = self.getOrganisationModule()._getOb(self.destination_company_id)
    sale_manager = self.getPersonModule()._getOb(self.sale_manager_id)
    # Set date
    date = DateTime() # the value is now 
    target_start_date = date + 10 # Add 10 days
    target_stop_date = date + 12 # Add 12 days
    order.setTargetStartDate(target_start_date)
    order.setTargetStopDate(target_stop_date)
    # Set Profile
    portal_categories = self.getCategoryTool()
    stock_category = portal_categories.resolveCategory(self.destination_company_stock)
    group_category = portal_categories.resolveCategory(self.destination_company_group)
    order.setSourceValue(source_company)
    order.setSourceSectionValue(source_company)
    order.setSourceDecisionValue(source_company)
    order.setSourceAdministrationValue(source_company)
    order.setSourcePaymentValue(source_company)
    order.setDestinationValue(stock_category)
    order.setDestinationSectionValue(group_category)
    order.setDestinationDecisionValue(destination_company)
    order.setDestinationAdministrationValue(destination_company)
    order.setDestinationPaymentValue(destination_company)
    order.setDestinationAdministrationValue(sale_manager)
    # Look if the profile is good 
    self.failUnless(order.getSourceValue()!=None)
    self.failUnless(order.getDestinationValue()!=None)
    self.failUnless(order.getSourceSectionValue()!=None)
    self.failUnless(order.getDestinationSectionValue()!=None)
    self.failUnless(order.getSourceDecisionValue()!=None)
    self.failUnless(order.getDestinationDecisionValue()!=None)
    self.failUnless(order.getSourceAdministrationValue()!=None)
    self.failUnless(order.getDestinationAdministrationValue()!=None)
    self.failUnless(order.getSourcePaymentValue()!=None)
    self.failUnless(order.getDestinationPaymentValue()!=None)
    attribute_name = self.convertToLowerCase(order_type)
    kw = {attribute_name:order}
    sequence.edit(**kw)

  def constructEmptySalesOrder(self, sequence=None, sequence_list=None,**kw):
    # Test if we can add a complete sales order
    self.constructEmptyOrder(sequence=sequence,sequence_list=sequence_list,
                             order_type='Sales Order', **kw)

  def constructEmptyProductionOrder(self, sequence=None, sequence_list=None,**kw):
    # Test if we can add a complete sales order
    self.constructEmptyOrder(sequence=sequence,sequence_list=sequence_list,
                             order_type='Production Order', **kw)

  def constructResource(self, sequence=None, sequence_list=None,**kw):
    component_module = self.getComponentModule()
    resource = component_module.newContent()
    resource.setBasePrice(self.base_price1)
    resource.setPrice(self.base_price1)
    sequence.edit(resource=resource)
    resource2 = component_module.newContent()
    resource2.setBasePrice(self.base_price1)
    resource2.setPrice(self.base_price1)
    sequence.edit(resource2=resource2)

  def constructVariatedResource(self, sequence=None, sequence_list=None,**kw):
    modele_module = self.getModeleModule()
    modele = modele_module.newContent()
    modele.setTailleList(self.taille_list1)
    # Add variation to the modele
    variante_modele_1 = modele.newContent(id=self.variante_id1,portal_type='Variante Modele')
    variante_modele_2 = modele.newContent(id=self.variante_id2,portal_type='Variante Modele')
    sequence.edit(resource=modele)
    # We should also construct the corresponding transformation
    transformation_module = self.getTransformationModule()
    transformation = transformation_module.newContent(portal_type='Transformation')
    transformation.setResourceValue(modele)
    transformation.setVariationBaseCategoryList(self.variation_base_category_list1)
    variation_category_list = ('coloris/modele/%s/%s' % (modele.getId(),self.variante_id1),
                                'coloris/modele/%s/%s' % (modele.getId(),self.variante_id2),
                                'taille/adulte/40','taille/adulte/42')
    sequence.edit(variation_category_list=variation_category_list)
    transformation.setVariationCategoryList(variation_category_list)
    color_list = filter(lambda x: x.find('coloris')>=0,variation_category_list)
    sequence.edit(color_list=color_list)
    size_list = filter(lambda x: x.find('taille')>=0,variation_category_list)
    sequence.edit(size_list=size_list)
    color_and_size_list = []
    # This define (('coloris/modele/1/1,taille/adulte/40',('coloris/modele/1/1',taille/adulte/42)...)
    for c in color_list:
      for s in size_list:
        color_and_size_list.append((c,s))
    sequence.edit(color_and_size_list=color_and_size_list)
    # And add transformed resource to this transformation
    tissu_module = self.getTissuModule()
    tissu = tissu_module.newContent(portal_type='Tissu')
    sequence.edit(tissu=tissu)
    transformation_component = transformation.newContent(portal_type='Transformation Component')
    transformation_component.setResourceValue(tissu)


  def stepAddSalesOrder(self, sequence=None, sequence_list=None,**kw):
    self.constructEmptySalesOrder(sequence=sequence,sequence_list=sequence_list,**kw)
    # Add a sales order line
    sales_order = sequence.get('sales_order')
    sales_order_line = sales_order.newContent(id='1',portal_type='Sales Order Line')
    component_module = self.getComponentModule()
    component = component_module._getOb(self.component_id)
    sequence.edit(resource=component)
    self.constructResource(sequence=sequence,sequence_list=sequence_list,**kw)
    component = sequence.get('resource')
    sales_order_line.setResourceValue(component)
    self.assertEquals(sales_order_line.getResourceValue(),component)
    sales_order_line.setTargetQuantity(self.quantity)
    sales_order_line.setPrice(self.base_price1)
    # See what's the output of Order_lightControl
    result=sales_order.Order_lightControl()
    self.assertEquals(result,'')
    # See what's the output of Order_heavyControl
    result=sales_order.Order_heavyControl()
    result = result.replace('\n','')
    self.assertEquals(result,'')

  def stepModifyVariationId(self, sequence=None, sequence_list=None,**kw):
    resource = sequence.get('resource')
    content_list = resource.contentValues(filter={'portal_type':'Variante Modele'})
    # Rename the first variation
    variation  = content_list[0]
    #variation.setId('renamed_' + variation.getId())
    variation.setId('renamed_' + variation.getId())
    variation_category_list = ('coloris/modele/%s/%s' % (resource.getId(),content_list[0].getId()),
                                'coloris/modele/%s/%s' % (resource.getId(),content_list[1].getId()),
                                'taille/adulte/40','taille/adulte/42')
    sequence.edit(variation_category_list=variation_category_list)
    color_list = filter(lambda x: x.find('coloris')>=0,variation_category_list)
    sequence.edit(color_list=color_list)
    size_list = filter(lambda x: x.find('taille')>=0,variation_category_list)
    sequence.edit(size_list=size_list)
    sequence.edit(renamed_variation=1)
    color_and_size_list = []
    # This define (('coloris/modele/1/1,taille/adulte/40'),('coloris/modele/1/1',taille/adulte/42)...)
    for c in color_list:
      for s in size_list:
        color_and_size_list.append((c,s))
    sequence.edit(color_and_size_list=color_and_size_list)

  def stepAddVariatedSalesOrder(self, sequence=None, sequence_list=None,**kw):
    self.constructEmptySalesOrder(sequence=sequence,sequence_list=sequence_list,**kw)
    # Add lines with many variations
    sales_order = sequence.get('sales_order')
    sales_order_line = sales_order.newContent(id='1',portal_type='Sales Order Line')
    self.constructVariatedResource(sequence=sequence,sequence_list=sequence_list,**kw)
    sequence.edit(variated_order=1)
    resource = sequence.get('resource')
    sales_order_line.setResourceValue(resource)
    self.assertEquals(sales_order_line.getResourceValue(),resource)
    sales_order_line.setVariationBaseCategoryList(self.variation_base_category_list1)
    variation_category_list = sequence.get('variation_category_list')
    sales_order_line.setVariationCategoryList(variation_category_list)
    self.assertEquals(tuple(sales_order_line.getVariationBaseCategoryList()),self.variation_base_category_list1)
    self.assertEquals(tuple(sales_order_line.getVariationCategoryList()),variation_category_list)
    cell_list = sales_order_line.objectValues()
    self.assertEquals(len(cell_list),4)
    for cell in cell_list:
      cell.setTargetQuantity(self.quantity)
      cell.setPrice(self.base_price1)
    # See what's the output of Order_lightControl
    result=sales_order.Order_lightControl()
    self.assertEquals(result,'')
      
  def stepConfirmSalesOrder(self, sequence=None,sequence_list=None):
    sales_order = sequence.get('sales_order')
    #sales_order.confirm()
    LOG('stepConfirmSalesOrder, sales_order',0,sales_order)
    sales_order.portal_workflow.doActionFor(sales_order,'user_confirm',
                                wf_id='order_workflow')

  def stepAcceptPackingList(self, sequence=None,sequence_list=None):
    packing_list = sequence.get('packing_list')
    portal_workflow = self.getWorkflowTool()
    packing_list.portal_workflow.doActionFor(packing_list,'accept_delivery',
                                wf_id='delivery_causality_workflow')

  def stepSplitAndDeferPackingList(self, sequence=None,sequence_list=None):
    packing_list = sequence.get('packing_list')
    # set quantities
    line = packing_list.objectValues()[0]
    LOG('stepSplitAndDeferPackingList line.getPortalType:',0,line.getPortalType())
    new_quantity = self.quantity - 1
    if sequence.get('variated_order') is not None:
      cell_list = line.objectValues()
      for cell in cell_list:
        cell.setTargetQuantity(new_quantity)
    else:
      line.setTargetQuantity(new_quantity)
    portal_workflow = self.getWorkflowTool()
    date = DateTime() # the value is now 
    target_start_date = date + 10 # Add 10 days
    target_stop_date = date + 12 # Add 12 days
    packing_list.portal_workflow.doActionFor(packing_list,'split_defer_delivery',
                                wf_id='delivery_causality_workflow',
                                target_start_date=target_start_date,
                                target_stop_date=target_stop_date)

  def stepAcceptDeliveryPackingList(self, sequence=None,sequence_list=None):
    packing_list = sequence.get('packing_list')
    packing_list.portal_workflow.doActionFor(packing_list,'accept_delivery',
                                wf_id='delivery_causality_workflow')

  def stepUserGetReadyPackingList(self, sequence=None,sequence_list=None):
    packing_list = sequence.get('packing_list')
    packing_list.portal_workflow.doActionFor(packing_list,'user_get_ready',
                                wf_id='delivery_workflow')

  def stepUserSetReadyPackingList(self, sequence=None,sequence_list=None):
    packing_list = sequence.get('packing_list')
    packing_list.portal_workflow.doActionFor(packing_list,'user_set_ready',
                                wf_id='delivery_workflow')

  def stepUserStartPackingList(self, sequence=None,sequence_list=None):
    packing_list = sequence.get('packing_list')
    packing_list.portal_workflow.doActionFor(packing_list,'user_start',
                                wf_id='delivery_workflow')

  def stepUserConfirmPackingList(self, sequence=None,sequence_list=None):
    packing_list = sequence.get('packing_list')
    packing_list.portal_workflow.doActionFor(packing_list,'user_confirm',
                                wf_id='delivery_workflow')

  def stepOrderSalesOrder(self, sequence=None,sequence_list=None):
    sales_order = sequence.get('sales_order')
    sales_order.portal_workflow.doActionFor(sales_order,'user_order',
                                wf_id='order_workflow')

  def stepPlanSalesOrder(self, sequence=None, sequence_list=None, **kw):
    portal = self.getPortal()
    sales_order = sequence.get('sales_order')
    sales_order.portal_workflow.doActionFor(sales_order,'user_plan',
                                wf_id='order_workflow')

  def stepCheckConfirmSalesOrder(self, sequence=None, sequence_list=None, **kw):
    sales_order = sequence.get('sales_order')
    sales_order_line = sales_order._getOb('1')
    simulation_tool = self.getSimulationTool()
    simulation_object_list = simulation_tool.objectValues()
    self.failUnless(len(simulation_object_list)>0)
    related_simulation_object_list = []
    simulation_object = None
    for o in simulation_object_list:
      if o.getCausalityValue()==sales_order:
        related_simulation_object_list.append(o)
    if len(related_simulation_object_list)>0:
      simulation_object = related_simulation_object_list[0]
    sequence.edit(simulation_object=simulation_object)
    self.assertNotEquals(simulation_object,None)
    self.assertEquals(len(related_simulation_object_list),1)
    sequence.edit(simulation_object=simulation_object)
    # Check if there is a line on the simulation object
    # And if this line get all informations
    line_list = simulation_object.objectValues()
    line = line_list[0]
    if sequence.get('variated_order') is None:
      self.assertEquals(len(line_list),1)
      self.assertEquals(line.getQuantity(),self.quantity)
    else:
      LOG('CheckConfirmSalesOrder line.asXML',0,line.asXML())
      self.assertEquals(len(line_list),4)
      # Check if the order of each line of the simulation
      # object is a cell of the order
      cell_list = sales_order_line.objectValues()
      LOG('CheckConfirmSalesOrder cell_list',0,cell_list)
      order_list = map(lambda x: x.getOrderValue(), line_list)
      LOG('CheckConfirmSalesOrder order_list',0,order_list)
      self.failIfDifferentSet(cell_list,order_list)
      color_and_size_list = sequence.get('color_and_size_list')
      cell_color_and_size_list = map(lambda x: x.getCategoryList(),cell_list)
      LOG('stepCheckConfirmSalesOrder color_and_size_list',0,color_and_size_list)
      LOG('stepCheckConfirmSalesOrder cell_color_and_size_list',0,cell_color_and_size_list)
      self.failIfDifferentSet(color_and_size_list,cell_color_and_size_list)
      for cell in cell_list:
        LOG('CheckConfirmSalesOrder cell.asXML',0,cell.asXML())
        self.assertEquals(cell.getTargetQuantity(),self.quantity)
        self.failIfDifferentSet(cell.getDomainBaseCategoryList(),self.variation_base_category_list1)
      # Check membership criterion
      membership_criterion_category_list_list = map(lambda x: tuple(x.getMembershipCriterionCategoryList()),cell_list)
      LOG('stepCheckActivateRequirementList, color_and_size_list',0,color_and_size_list)
      LOG('stepCheckActivateRequirementList, membership_criterion_category_list_list',0,membership_criterion_category_list_list)
      self.failIfDifferentSet(color_and_size_list,membership_criterion_category_list_list)
      predicate_value_list_list = map(lambda x: tuple(x.getPredicateValueList()),cell_list)
      LOG('stepCheckActivateRequirementList, color_and_size_list',0,color_and_size_list)
      LOG('stepCheckActivateRequirementList, predicate_value_list_list',0,predicate_value_list_list)
      self.failIfDifferentSet(color_and_size_list,predicate_value_list_list)

  def stepCheckPackingListDiverged(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    portal_workflow = self.getWorkflowTool()
    self.assertEquals(portal_workflow.getInfoFor(packing_list,'causality_state'),'diverged')

  def stepCheckPackingListConverged(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    portal_workflow = self.getWorkflowTool()
    self.assertEquals(portal_workflow.getInfoFor(packing_list,'causality_state'),'converged')

  def stepModifySalesOrder(self, sequence=None, sequence_list=None, **kw):
    sales_order = sequence.get('sales_order')
    sales_order_line = sales_order._getOb('1')
    sales_order_line.setTargetQuantity(self.quantity + 1)
    component_module = self.getComponentModule()
    component = component_module._getOb(self.component_id2)
    sales_order_line.setResourceValue(component)
    self.assertEquals(sales_order_line.getResourceValue(),component)

  def stepActivateRequirementList(self, sequence=None, sequence_list=None, **kw):
    portal = self.getPortal()
    result = portal.SimulationTool_activateRequirementList()
    result = result.replace('\n','')
    self.assertEquals(result,'')

  def stepCheckActivateRequirementList(self, sequence=None, sequence_list=None, **kw):
    packing_list_module = self.getSalesPackingListModule()
    sales_order = sequence.get('sales_order')
    packing_list_list = packing_list_module.objectValues()
    packing_list = None
    related_list = []
    for o in packing_list_list:
      if o.getCausalityValue()==sales_order:
        related_list.append(o)
    if len(related_list)>0:
      packing_list=related_list[0]
    self.assertNotEquals(packing_list,None)
    self.assertEquals(len(related_list),1)
    portal_workflow = self.getWorkflowTool()
    self.assertEquals(portal_workflow.getInfoFor(packing_list,'simulation_state'),'confirmed')
    sequence.edit(packing_list=packing_list)
    # Check if there is a line on the packing_list
    # And if this line get all informations
    line_list = packing_list.objectValues()
    self.assertEquals(len(line_list),1)
    line = line_list[0]
    resource = sequence.get('resource')
    self.assertEquals(line.getResourceValue(),resource)
    if sequence.get('variated_order') is None:
      self.assertEquals(line.getTotalQuantity(),self.quantity)
      self.assertEquals(len(line.objectValues()),0)
    else:
      cell_list = line.objectValues()
      # check variation_base_category_list
      self.failIfDifferentSet(line.getVariationBaseCategoryList(),self.variation_base_category_list1)
      LOG('stepCheckActivateRequirementList, line.asXML',0,line.asXML())
      self.assertEquals(len(cell_list),4)
      for cell in cell_list:
        LOG('stepCheckActivateRequirementList, cell.getCategoryList',0,cell.getCategoryList())
        self.assertEquals(cell.getTargetQuantity(),self.quantity)
      color_and_size_list = sequence.get('color_and_size_list')
      membership_criterion_category_list = map(lambda x: tuple(x.getMembershipCriterionCategoryList()),cell_list)
      LOG('stepCheckActivateRequirementList, color_and_size_list',0,color_and_size_list)
      LOG('stepCheckActivateRequirementList, membership_criterion_category_list',0,membership_criterion_category_list)
      self.failIfDifferentSet(color_and_size_list,membership_criterion_category_list)

  def stepCheckSplittedAndDefferedPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list_module = self.getSalesPackingListModule()
    sales_order = sequence.get('sales_order')
    packing_list_list = packing_list_module.objectValues()
    packing_list = None
    related_list = []
    for o in packing_list_list:
      if o.getCausalityValue()==sales_order:
        related_list.append(o)
    self.assertEquals(len(related_list),2)
    def sort_by_id(x,y):
      return cmp(int(x.getId()),int(y.getId()))
    # Like this we will have the related_list sorted
    # by the order where the packing list where created
    related_list.sort(sort_by_id)
    packing_list1 = related_list[0] # The First one
    line = packing_list1.objectValues()[0]
    for cell in line.objectValues():
      self.assertEquals(cell.getTargetQuantity(),self.quantity-1)
    packing_list2 = related_list[1] # The First one
    line = packing_list2.objectValues()[0]
    for cell in line.objectValues():
      self.assertEquals(cell.getTargetQuantity(),1)




  def stepAddLinesToSalesPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    packing_list_line = packing_list.newContent(portal_type='Sales Packing List Line')
    component_module = self.getComponentModule()
    component = component_module._getOb(self.component_id)
    packing_list_line.setResourceValue(component)
    packing_list_line.setTargetQuantity(self.quantity)
    sequence.edit(new_packing_list_line=packing_list_line)

  def stepSetLessQuantityToPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    packing_list_line = packing_list._getOb('1')
    packing_list_line.setQuantity(self.low_quantity)

  def stepCheckLessQuantityInSimulation(self, sequence=None, sequence_list=None, **kw):
    simulation_object=sequence.get('simulation_object')
    line_list = simulation_object.objectValues()
    self.assertEquals(len(line_list),1)
    line = line_list[0]
    component_module = self.getComponentModule()
    component = component_module._getOb(self.component_id)
    self.assertEquals(line.getQuantity(),self.low_quantity)

  def stepTic(self,**kw):
    portal = self.getPortal()
    portal.portal_activities.distribute()
    portal.portal_activities.tic()

  def testOrder(self, quiet=0,run=1):
    sequence_list = SequenceList()
    # Simple sequence with only some tic when it is required,
    # We create a sales order, confirm and then make sure the corresponding
    # packing list is made
    # ... OK
    #sequence_string =   'AddSalesOrder PlanSalesOrder OrderSalesOrder ConfirmSalesOrder' \
    #                  + ' Tic Tic Tic Tic CheckConfirmSalesOrder' \
    #                  + ' Tic Tic CheckActivateRequirementList'
    #sequence_list.addSequenceString(sequence_string)

    # Simple sequence (same as the previous one) with only some tic when it is required and with no plan,
    # ... OK
    #sequence_string =   'AddSalesOrder Tic ConfirmSalesOrder Tic CheckConfirmSalesOrder ' \
    #                  + 'Tic CheckActivateRequirementList'
    #sequence_list.addSequenceString(sequence_string)

    # Sequence where we set less quantity in the packing list
    # And we want to be sure that we will have less quantity in the simulation after we did accept
    # ... FAILS
    #sequence_string =   'AddSalesOrder PlanSalesOrder OrderSalesOrder' \
    #                  + ' ConfirmSalesOrder Tic Tic Tic Tic CheckConfirmSalesOrder' \
    #                  + ' Tic CheckActivateRequirementList SetLessQuantityToPackingList' \
    #                  + ' Tic Tic AcceptPackingList Tic Tic Tic CheckLessQuantityInSimulation' 
    #sequence_list.addSequenceString(sequence_string)

    # Simple sequence including variated resource with only some tic when it is required,
    # We create a sales order, confirm and then make sure the corresponding
    # packing list is made
    # ... OK
    #sequence_string =   'AddVariatedSalesOrder PlanSalesOrder OrderSalesOrder' \
    #                  + ' ConfirmSalesOrder Tic Tic Tic Tic CheckConfirmSalesOrder' \
    #                  + ' Tic Tic CheckActivateRequirementList'
    #sequence_list.addSequenceString(sequence_string)

    # Sequence where we confirm an order, the corresponding packing list is automatically
    # created, then we add new lines to the packing list by hand, we accept, we then check
    # if the packing list is converged.
    # ... FAILS
    #sequence_string =   'AddSalesOrder Tic Tic ConfirmSalesOrder Tic Tic CheckConfirmSalesOrder Tic' \
    #                  + ' Tic Tic Tic Tic Tic Tic CheckConfirmSalesOrder' \
    #                  + ' Tic Tic Tic Tic CheckActivateRequirementList Tic' \
    #                  + ' AddLinesToSalesPackingList Tic Tic Tic AcceptPackingList Tic Tic Tic CheckPackingListConverged' 
    #sequence_list.addSequenceString(sequence_string)

    # Sequence where we confirm an order, the corresponding packing list is automatically
    # created, then we rename the color of the variated resource, everything should take
    # into account the new name
    # ... FAILS
    sequence_string =   'AddVariatedSalesOrder PlanSalesOrder OrderSalesOrder' \
                      + ' ConfirmSalesOrder Tic Tic Tic Tic CheckConfirmSalesOrder' \
                      + ' Tic Tic CheckActivateRequirementList' \
                      + ' Tic Tic ModifyVariationId Tic Tic CheckConfirmSalesOrder' \
                      + ' Tic Tic CheckActivateRequirementList'
    sequence_list.addSequenceString(sequence_string)

    # Sequence where we create an order, then the color is renamed, then we confirm
    # and we look if everyhing is going fine on the simulation and that the 
    # packing list is created correctly
    # ... FAILS
    #sequence_string =   'AddVariatedSalesOrder Tic Tic ModifyVariationId Tic Tic Tic' \
    #                  + ' ConfirmSalesOrder Tic Tic CheckConfirmSalesOrder Tic' \
    #                  + ' Tic Tic Tic Tic CheckActivateRequirementList Tic'
    #sequence_list.addSequenceString(sequence_string)

    # Sequence where we confirm an order, the corresponding packing list is automatically
    # created, then we wants to only send one part of the packing list and finally 
    # we split and defer the packing list
    # ... OK
    #sequence_string =   'AddVariatedSalesOrder PlanSalesOrder OrderSalesOrder' \
    #                  + ' ConfirmSalesOrder Tic Tic Tic Tic CheckConfirmSalesOrder' \
    #                  + ' CheckActivateRequirementList Tic Tic Tic' \
    #                  + ' UserGetReadyPackingList Tic Tic UserSetReadyPackingList Tic Tic' \
    #                  + ' UserStartPackingList Tic Tic Tic Tic' \
    #                  + ' AcceptDeliveryPackingList Tic Tic SplitAndDeferPackingList Tic Tic Tic' \
    #                  + ' CheckSplittedAndDefferedPackingList'  
    #sequence_list.addSequenceString(sequence_string)


    # Sequence where we build a Production Order, we confirm this production order, then
    # we have many packing list, we change the destination of one of the packing_list,
    # we must be sure that this change is taken into account into the simulation
    # ... ???
    #sequence_string =   'AddVariatedSalesOrder PlanSalesOrder OrderSalesOrder' \
    #                  + ' ConfirmSalesOrder Tic Tic Tic Tic CheckConfirmSalesOrder' \
    #                  + ' CheckActivateRequirementList Tic Tic Tic' \
    #                  + ' UserGetReadyPackingList Tic Tic UserSetReadyPackingList Tic Tic' \
    #                  + ' UserStartPackingList Tic Tic Tic Tic' \
    #                  + ' AcceptDeliveryPackingList Tic Tic SplitAndDeferPackingList Tic Tic Tic' \
    #                  + ' CheckSplittedAndDefferedPackingList'  
    #sequence_list.addSequenceString(sequence_string)


    # Now add a non defined sequence
#    sequence = Sequence()
#    sequence.addStep('AddSalesOrder')
#    sequence.addStep('Tic',required=0,max_replay=3)
#    sequence.addStep('PlanSalesOrder',required=0)
#    sequence.addStep('Tic',required=0,max_replay=3)
#    sequence.addStep('OrderSalesOrder',required=0)
#    sequence.addStep('Tic',required=0,max_replay=3)
#    sequence.addStep('ConfirmSalesOrder')
#    sequence.addStep('Tic',required=0,max_replay=3)
#    sequence.addStep('ModifySalesOrder',required=0)
#    sequence.addStep('Tic',required=0,max_replay=3)
#    sequence.addStep('CheckConfirmSalesOrder')
#    sequence.addStep('ActivateRequirementList')
#    sequence.addStep('Tic',required=0,max_replay=5)
#    sequence_list.addSequence(sequence)
    # Finally play the three sequences
    sequence_list.play(self)



if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestOrder))
        return suite

