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
from Globals import PersistentMapping
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
import time
  

class TestOrder(ERP5TypeTestCase):

  # Different variables used for this test
  run_all_test = 1
  source_company_id = 'Nexedi'
  sale_manager_id = 'seb'
  destination_company_stock = 'site/Stock_MP/Gravelines'
  production_destination_site = 'site/Stock_PF/Gravelines'
  production_destination_site2 = 'site/Stock_PF/Bonningues'
  production_source_site = 'site/Piquage/France/Sylitex'
  second_production_source_site = 'site/Piquage/Tunisie/String'
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
  simulation_line_id_list = ('1_movement_0_0','1_movement_0_1','1_movement_1_0','1_movement_1_1')
  simple_simulation_line_id_list = ('1')

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
    #return ('erp5_crm','coramy_catalog','coramy_order')
    return ('erp5_core','coramy_catalog','coramy_order')

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

  def getProductionPackingListModule(self):
    return getattr(self.getPortal(), 'livraison_fabrication', None)

  def getProductionOrderModule(self):
    return getattr(self.getPortal(), 'ordre_fabrication', None)

  def getGammeModule(self):
    return getattr(self.getPortal(), 'gamme', None)

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
    LOG('failIfDifferentSet',0,'a:%s b:%s' % (repr(a),repr(b)))
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
      LOG('afterSetup portal_categies',0,o.getPath())
      o.recursiveImmediateReindexObject()
    LOG('afterSetup',0,'portal.portal_simulation.immediateReindexObject')
    portal.portal_simulation.immediateReindexObject()
    for o in portal.portal_simulation.objectValues():
      o.recursiveImmediateReindexObject()
    LOG('afterSetup',0,'portal.portal_rules.immediateReindexObject')
    portal.portal_rules.immediateReindexObject()

    organisation_module = self.getOrganisationModule()
    organisation_module.immediateReindexObject()
    o1 = organisation_module.newContent(id=self.source_company_id)
    o2 = organisation_module.newContent(id=self.destination_company_id)
    component_module = self.getComponentModule()
    component_module.immediateReindexObject()
    c1 = component_module.newContent(id=self.component_id)
    c1.setBasePrice(self.base_price1)
    c1.setPrice(self.base_price1)
    c1 = component_module.newContent(id=self.component_id2)
    c1.setBasePrice(self.base_price2)
    c1.setPrice(self.base_price2)
    person_module = self.getPersonModule()
    person_module.immediateReindexObject()
    p1 = person_module.newContent(id=self.sale_manager_id)
    kw = {'first_name':self.first_name1,'last_name':self.last_name1}
    p1.edit(**kw)
    modele_module = self.getModeleModule()

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
    if order_type == 'Production Order':
      stock_category = portal_categories.resolveCategory(self.production_destination_site)
      source_company = portal_categories.resolveCategory(self.production_source_site)
    else:
      stock_category = portal_categories.resolveCategory(self.destination_company_stock)
    group_category = portal_categories.resolveCategory(self.destination_company_group)
    sequence.edit(source_value=source_company,
                  source_section_value=source_company,
                  source_decision_value=source_company,
                  source_administration_value=source_company,
                  source_payment_value=source_company,
                  destination_value=stock_category,
                  destination_section_value=group_category,
                  destination_decision_value=destination_company,
                  destination_administration_value=sale_manager,
                  destination_payment_value=destination_company)
    order.setTargetSourceValue(source_company)
    order.setTargetSourceSectionValue(source_company)
    order.setSourceDecisionValue(source_company)
    order.setSourceAdministrationValue(source_company)
    order.setSourcePaymentValue(source_company)
    order.setTargetDestinationValue(stock_category)
    order.setTargetDestinationSectionValue(group_category)
    order.setDestinationDecisionValue(destination_company)
    order.setDestinationAdministrationValue(sale_manager)
    order.setDestinationPaymentValue(destination_company)
    # Look if the profile is good 
    self.failUnless(order.getTargetSourceValue()!=None)
    self.failUnless(order.getTargetDestinationValue()!=None)
    self.failUnless(order.getTargetSourceSectionValue()!=None)
    self.failUnless(order.getTargetDestinationSectionValue()!=None)
    self.failUnless(order.getSourceDecisionValue()!=None)
    self.failUnless(order.getDestinationDecisionValue()!=None)
    self.failUnless(order.getSourceAdministrationValue()!=None)
    self.failUnless(order.getDestinationAdministrationValue()!=None)
    self.failUnless(order.getSourcePaymentValue()!=None)
    self.failUnless(order.getDestinationPaymentValue()!=None)
    attribute_name = self.convertToLowerCase(order_type)
    kw = {attribute_name:order}
    sequence.edit(**kw)
    sequence.edit(order_type=order_type)

#  def constructEmptySalesOrder(self, sequence=None, sequence_list=None,**kw):
#    # Test if we can add a complete sales order
#    self.constructEmptyOrder(sequence=sequence,sequence_list=sequence_list,
#                             order_type='Sales Order', **kw)
#
#  def constructEmptyProductionOrder(self, sequence=None, sequence_list=None,**kw):
#    # Test if we can add a complete sales order
#    self.constructEmptyOrder(sequence=sequence,sequence_list=sequence_list,
#                             order_type='Production Order', **kw)
#
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
    category_variante_modele_1 = 'coloris/modele/%s/%s' % (modele.getId(),self.variante_id1)
    sequence.edit(category_variante_modele_1=category_variante_modele_1)
    variante_modele_2 = modele.newContent(id=self.variante_id2,portal_type='Variante Modele')
    category_variante_modele_2 = 'coloris/modele/%s/%s' % (modele.getId(),self.variante_id2)
    sequence.edit(category_variante_modele_2=category_variante_modele_2)
    sequence.edit(resource=modele)
    # We should also construct the corresponding transformation
    transformation_module = self.getTransformationModule()
    transformation = transformation_module.newContent(portal_type='Transformation')
    sequence.edit(transformation=transformation)
    transformation.setResourceValue(modele)
    transformation.setVariationBaseCategoryList(self.variation_base_category_list1)
    transformation.setVariationBaseCategoryLine('coloris')
    transformation.setVariationBaseCategoryColumn('taille')
    variation_category_list = (category_variante_modele_1, category_variante_modele_2,
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
    self.addTissuToTransformation(sequence=sequence,sequence_list=sequence_list)
    sequence.edit(good_tissu_list=sequence.get('tissu_list'))
    # We should construct the corresponding gamme
    # XXX Finally I'm not sure we really need the gamme XXX
#    gamme_module = self.getGammeModule()
#    gamme = gamme_module.newContent(portal_type='Gamme')
#    modele.setSpecialiseValue(gamme)
#    sequence.edit(gamme=gamme)
#    tissu1_variante1 = sequence.get('tissu1_variante1')
#    tissu1_variante2 = sequence.get('tissu1_variante2')
#    variante_gamme1 = gamme.newContent(portal_type='Variante Gamme',id=self.variante_id1)
#    variante_gamme1.setCouleurValueList([tissu1_variante1])
#    variante_gamme2 = gamme.newContent(portal_type='Variante Gamme',id=self.variante_id2)
#    variante_gamme2.setCouleurValueList([tissu1_variante2])
#    LOG("transformation._getOb('1').__dict__",0,transformation._getOb('1').__dict__)
#    LOG("transformation._getOb('1').quantity_0_0.__dict__",0,transformation._getOb('1').quantity_0_0.__dict__)
#    LOG("gamme.__dict__",0,gamme.__dict__)
#    LOG("variante_gamme1.__dict__",0,variante_gamme1.__dict__)
    LOG("modele.__dict__",0,modele.__dict__)
    LOG("transformation.sowDict()",0,transformation.showDict())
    LOG("transformation.getAggregatedAmountList()",0,transformation.getAggregatedAmountList())

  def addTissuToTransformation(self, sequence=None, sequence_list=None, **kw):
    # We should construct the corresponding tissu
    tissu_list = sequence.get('tissu_list',[])
    transformation = sequence.get('transformation')
    tissu_module = self.getTissuModule()
    tissu = tissu_module.newContent(portal_type='Tissu')
    tissu.setSourceBasePrice('7.7')
    tissu.setPricedQuantity('1')
    tissu.setVariationBaseCategoryList(['coloris'])
    tissu_list.extend([tissu])
    sequence.edit(tissu_list=tissu_list)
    tissu.setQuantityUnit('Longueur/Metre')
    tissu_variante1 = tissu.newContent(portal_type='Variante Tissu',id=self.variante_id1)
    category_tissu_variante1 = 'coloris/tissu/%s/%s' % (tissu.getId(),tissu_variante1.getId())
    tissu_variante2 = tissu.newContent(portal_type='Variante Tissu',id=self.variante_id2)
    category_tissu_variante2 = 'coloris/tissu/%s/%s' % (tissu.getId(),tissu_variante2.getId())
    seq_kw = {'tissu%s' % tissu.getId():tissu,
          'tissu%s_variante1' % tissu.getId():tissu_variante1,
          'tissu%s_variante2' % tissu.getId():tissu_variante2,
          'category_tissu%s_variante1' % tissu.getId():category_tissu_variante1,
          'category_tissu%s_variante2' % tissu.getId():category_tissu_variante2}
    sequence.edit(**seq_kw)
    if sequence.get('tissu_first') is None:
      sequence.edit(tissu_first=tissu)
    elif sequence.get('tissu_second') is None:
      sequence.edit(tissu_second=tissu)
    # Add a transformed resource to this transformation
    transformation_component = transformation.newContent(portal_type='Transformation Component')
    transformation_component.setResourceValue(tissu)
    transformation_component.setElementComposition(True) # This is one element of the transformation
    transformation_component.setVVariationBaseCategoryList(['coloris'])
    transformation_component.setQVariationBaseCategoryList(['taille'])
    #transformation_component.setTailleList(['taille/adulte/40','taille/adulte/42'])
    # Create quantity cells for the transformation component
    args = (None,'taille/adulte/40')
    kw = {'base_id':'quantity'}
    cell = transformation_component.newCell(*args,**kw)
    cell.setPredicateOperator('SUPERSET_OF')
    cell.setMembershipCriterionCategoryList(['taille/adulte/40'])
    cell.setMembershipCriterionBaseCategoryList(['taille'])
    cell.setMappedValuePropertyList(['quantity'])
    cell.setQuantity(4200.0)
    LOG('transformation_cell.showDict()',0,cell.showDict())
    args = (None,'taille/adulte/42')
    kw = {'base_id':'quantity'}
    cell = transformation_component.newCell(*args,**kw)
    cell.setPredicateOperator('SUPERSET_OF')
    cell.setMembershipCriterionCategoryList(['taille/adulte/42'])
    cell.setMembershipCriterionBaseCategoryList(['taille'])
    cell.setMappedValuePropertyList(['quantity'])
    cell.setQuantity(4500.0)
    LOG('transformation_cell.showDict()',0,cell.showDict())
    cell_list = transformation_component.objectValues()
    cell_list = filter(lambda x: x.getId().find('quantity')==0, cell_list)
    self.assertEquals(len(cell_list),2)
    # Create variation cells for the transformation component
    # First variation cell
    category_variante_modele_1 = sequence.get('category_variante_modele_1')
    args = (category_variante_modele_1,None)
    kw = {'base_id':'variation'}
    cell = transformation_component.newCell(*args,**kw)
    cell.setPredicateOperator('SUPERSET_OF')
    cell.setMembershipCriterionBaseCategoryList(['coloris'])
    cell.setMappedValueBaseCategoryList(['coloris']) # XXX This looks like mandatory in TransformedResource for
                                                     # getAggregatedAmountList, why ????
    cell.setMembershipCriterionCategoryList([category_variante_modele_1])
    cell.setCategoryList([category_tissu_variante1])
    # Second variation cell
    category_variante_modele_2 = sequence.get('category_variante_modele_2')
    LOG('transformation_cell.showDict()',0,cell.showDict())
    args = (category_variante_modele_2,None)
    kw = {'base_id':'variation'}
    cell = transformation_component.newCell(*args,**kw)
    cell.setPredicateOperator('SUPERSET_OF')
    cell.setMembershipCriterionBaseCategoryList(['coloris'])
    cell.setMappedValueBaseCategoryList(['coloris']) # XXX This looks like mandatory in TransformedResource for
                                                     # getAggregatedAmountList, why ????
    cell.setMembershipCriterionCategoryList([category_variante_modele_2])
    cell.setCategoryList([category_tissu_variante2])
    LOG('transformation_cell.showDict()',0,cell.showDict())
    # Finally check the number of cells
    cell_list = transformation_component.objectValues()
    cell_list = filter(lambda x: x.getId().find('variation')==0, cell_list)
    self.assertEquals(len(cell_list),2)
    LOG('transformation_component.showDict()',0,transformation_component.showDict())

  def stepAddSalesOrder(self, sequence=None, sequence_list=None,**kw):
    self.constructEmptyOrder(sequence=sequence,sequence_list=sequence_list,
                             order_type='Sales Order', **kw)
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
    #self.constructEmptySalesOrder(sequence=sequence,sequence_list=sequence_list,**kw)
    self.constructEmptyOrder(sequence=sequence,sequence_list=sequence_list,
                             order_type='Sales Order', **kw)
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
      
  def stepAddProductionOrder(self, sequence=None, sequence_list=None,**kw):
    #self.constructEmptyProductionOrder(sequence=sequence,sequence_list=sequence_list,**kw)
    self.constructEmptyOrder(sequence=sequence,sequence_list=sequence_list,
                             order_type='Production Order', **kw)
    production_order = sequence.get('production_order')
    order_line = production_order.newContent(id='1',portal_type='Production Order Line')
    self.constructVariatedResource(sequence=sequence,sequence_list=sequence_list,**kw)
    sequence.edit(variated_order=1)
    resource = sequence.get('resource')
    order_line.setResourceValue(resource)
    order_line.setVariationBaseCategoryList(self.variation_base_category_list1)
    variation_category_list = sequence.get('variation_category_list')
    order_line.setVariationCategoryList(variation_category_list)
    self.assertEquals(tuple(order_line.getVariationBaseCategoryList()),self.variation_base_category_list1)
    self.assertEquals(tuple(order_line.getVariationCategoryList()),variation_category_list)
    cell_list = order_line.objectValues()
    self.assertEquals(len(cell_list),4)
    LOG('stepAddProductionOrder, order.showDict',0,production_order.showDict())
    LOG('stepAddProductionOrder, order_line.showDict',0,order_line.showDict())
    transformation = sequence.get('transformation')
    for cell in cell_list:
      cell.setTargetQuantity(self.quantity)
      LOG('stepAddProductionOrder, cell.showDict',0,cell.showDict())
      variation = cell.getVariationCategoryList()
      LOG('stepAddProductionOrder, cell.getVariationCategoryList',0,variation)
      LOG('stepAddProductionOrder, transformation.getAggregatedAmountList',0,transformation.getAggregatedAmountList(REQUEST = {'categories':variation}))
      REQUEST = {'categories':variation}
      REQUEST = transformation.asContext(context=transformation,REQUEST=REQUEST)
      LOG('stepAddProductionOrder, line.getAggregatedAmountList',0,transformation._getOb('1').getAggregatedAmountList(REQUEST))
      LOG('stepAddProductionOrder, line.getAgg[0].__dict__',0,transformation._getOb('1').getAggregatedAmountList(REQUEST)[0][0].__dict__)

    # See what's the output of Order_lightControl
    result=production_order.Order_lightControl()
    self.assertEquals(result,'')
      
  def stepConfirmSalesOrder(self, sequence=None,sequence_list=None):
    sales_order = sequence.get('sales_order')
    #sales_order.confirm()
    LOG('stepConfirmSalesOrder, sales_order',0,sales_order)
    sales_order.portal_workflow.doActionFor(sales_order,'user_confirm',
                                wf_id='order_workflow')

  def stepAcceptPackingList(self, sequence=None,sequence_list=None):
    packing_list = sequence.get('packing_list')
    LOG('stepAcceptPackingList, packing_list.isDivergent()',0,packing_list.isDivergent())
    portal_workflow = self.getWorkflowTool()
    packing_list.portal_workflow.doActionFor(packing_list,'accept_delivery',
                                wf_id='delivery_causality_workflow')

  def stepSplitAndDeferPackingList(self, sequence=None,sequence_list=None):
    portal_workflow = self.getWorkflowTool()
    date = DateTime() # the value is now 
    target_start_date = date + 10 # Add 10 days
    target_stop_date = date + 12 # Add 12 days
    packing_list = sequence.get('packing_list')
    packing_list.portal_workflow.doActionFor(packing_list,'split_defer_delivery',
                                wf_id='delivery_causality_workflow',
                                target_start_date=target_start_date,
                                target_stop_date=target_stop_date)

  # XXX To be checked
  def stepRedirectPackingList(self, sequence=None,sequence_list=None):
    packing_list = sequence.get('packing_list')
    portal_workflow = self.getWorkflowTool()
    packing_list.portal_workflow.doActionFor(packing_list,'redirect_delivery',
                                wf_id='delivery_causality_workflow')

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

  def stepConfirmProductionOrder(self, sequence=None, sequence_list=None, **kw):
    portal = self.getPortal()
    production_order = sequence.get('production_order')
    production_order.portal_workflow.doActionFor(production_order,'usof_confirm',
                                wf_id='order_workflow')

  def stepOrderProductionOrder(self, sequence=None, sequence_list=None, **kw):
    portal = self.getPortal()
    production_order = sequence.get('production_order')
    production_order.portal_workflow.doActionFor(production_order,'usof_order',
                                wf_id='order_workflow')

  def stepPlanProductionOrder(self, sequence=None, sequence_list=None, **kw):
    portal = self.getPortal()
    production_order = sequence.get('production_order')
    production_order.portal_workflow.doActionFor(production_order,'usof_plan',
                                wf_id='order_workflow')

  def stepCheckConfirmOrder(self, sequence=None, sequence_list=None, **kw):
    if sequence.get('order_type') == 'Production Order':
      order = sequence.get('production_order')
    else:
      order = sequence.get('sales_order')
    order_line = order._getOb('1')
    simulation_tool = self.getSimulationTool()
    simulation_object_list = simulation_tool.objectValues()
    self.failUnless(len(simulation_object_list)>0)
    related_simulation_object_list = []
    simulation_object = None
    for o in simulation_object_list:
      if o.getCausalityValue()==order:
        related_simulation_object_list.append(o)
    if len(related_simulation_object_list)>0:
      simulation_object = related_simulation_object_list[0]
    sequence.edit(simulation_object=simulation_object)
    self.assertNotEquals(simulation_object,None)
    sequence.edit(simulation_object_list=related_simulation_object_list)
    self.assertEquals(len(related_simulation_object_list),1)
    sequence.edit(simulation_object=simulation_object)

    # XXX to be removed
    packing_list = sequence.get('packing_list')
    if packing_list is not None:
      LOG('stepCheckConfirmOrder, packing_list.isConvergent()',0,packing_list.isConvergent())
      LOG('stepCheckConfirmOrder, packing_list.getMovementList()',0,packing_list.getMovementList())


    # Check if there is a line on the simulation object
    # And if this line get all informations
    line_list = simulation_object.objectValues()
    line = line_list[0]
    sequence.edit(simulation_line_list=line_list)
    if sequence.get('variated_order') is None:
      self.assertEquals(len(line_list),1)
      self.assertEquals(line.getQuantity(),self.quantity)
    else:
      self.assertEquals(len(line_list),4)
      # Check if the order of each line of the simulation
      # object is a cell of the order
      cell_list = order_line.objectValues()
      LOG('CheckConfirmOrder cell_list',0,cell_list)
      order_list = map(lambda x: x.getOrderValue(), line_list)
      LOG('CheckConfirmOrder order_list',0,order_list)
      self.failIfDifferentSet(cell_list,order_list)
      color_and_size_list = sequence.get('color_and_size_list')
      cell_color_and_size_list = map(lambda x: x.getCategoryList(),cell_list)
      LOG('stepCheckConfirmOrder color_and_size_list',0,color_and_size_list)
      LOG('stepCheckConfirmOrder cell_color_and_size_list',0,cell_color_and_size_list)
      self.failIfDifferentSet(color_and_size_list,cell_color_and_size_list)
      for cell in cell_list:
        LOG('stepCheckConfirmOrder cell.getPhysicalPath()',0,cell.getPhysicalPath())
        self.assertEquals(cell.getTargetQuantity(),self.quantity)
        self.failIfDifferentSet(cell.getDomainBaseCategoryList(),self.variation_base_category_list1)
        # Check the profile for this cell
        if sequence.get('modified_packing_list_path') is None: # if 
          self.assertEquals(cell.getSourceValue(),sequence.get('source_value'))
          self.assertEquals(cell.getSourceSectionValue(),sequence.get('source_section_value'))
          self.assertEquals(cell.getSourceDecisionValue(),sequence.get('source_decision_value'))
          self.assertEquals(cell.getSourceAdministrationValue(),sequence.get('source_administration_value'))
          self.assertEquals(cell.getSourcePaymentValue(),sequence.get('source_payment_value'))
          self.assertEquals(cell.getDestinationValue(),sequence.get('destination_value'))
          self.assertEquals(cell.getDestinationSectionValue(),sequence.get('destination_section_value'))
          self.assertEquals(cell.getDestinationDecisionValue(),sequence.get('destination_decision_value'))
          self.assertEquals(cell.getDestinationAdministrationValue(),sequence.get('destination_administration_value'))
          self.assertEquals(cell.getDestinationPaymentValue(),sequence.get('destination_payment_value'))
      # Check membership criterion
      membership_criterion_category_list_list = map(lambda x: tuple(x.getMembershipCriterionCategoryList()),cell_list)
      LOG('stepCheckConfirmOrder, color_and_size_list',0,color_and_size_list)
      LOG('stepCheckConfirmOrder, membership_criterion_category_list_list',0,membership_criterion_category_list_list)
      self.failIfDifferentSet(color_and_size_list,membership_criterion_category_list_list)
      predicate_value_list_list = map(lambda x: tuple(x.getPredicateValueList()),cell_list)
      LOG('stepCheckConfirmOrder, color_and_size_list',0,color_and_size_list)
      LOG('stepCheckConfirmOrder, predicate_value_list_list',0,predicate_value_list_list)
      self.failIfDifferentSet(color_and_size_list,predicate_value_list_list)

  def stepCheckPackingListDiverged(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    portal_workflow = self.getWorkflowTool()
    LOG('stepCheckPackingListDiverged, isDivergent()',0,packing_list.isDivergent())
    LOG('stepCheckPackingListDiverged, isConvergent()',0,packing_list.isConvergent())
    self.assertEquals(packing_list.isDivergent(),1)
    self.assertEquals(portal_workflow.getInfoFor(packing_list,'causality_state'),'diverged')

  def stepCheckPackingListConverged(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    portal_workflow = self.getWorkflowTool()
    LOG('stepCheckPackingListConverged, packing_list.isConvergent()',0,packing_list.isConvergent())
    self.assertEquals(portal_workflow.getInfoFor(packing_list,'causality_state'),'solved')

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
    mp_packing_list_list = [] # mp stands for Raw Material
    packing_list_list = []
    if sequence.get('order_type') == 'Production Order':
      packing_list_module = self.getProductionPackingListModule()
      order = sequence.get('production_order')
    else:
      packing_list_module = self.getSalesPackingListModule()
      order = sequence.get('sales_order')
    all_packing_list_list = packing_list_module.objectValues()
    packing_list = None
    related_list = []
    for o in all_packing_list_list:
      if o.getCausalityValue()==order:
        related_list.append(o)
        LOG('stepCheckActivateRequirementList, 1 packing_list.asXML()',0,o.asXML())
    if sequence.get('order_type')=='Production Order': 
      # We should find the packing list corresponding the the 
      # delivery of the resource, not the delivery of raw materials
      if sequence.get('modified_packing_list_resource') == 1:
        self.assertEquals(len(related_list),3)
      else:
        #self.assertEquals(len(related_list),2)
        self.assertEquals(len(related_list),2) # XXXXXXXXXXXXXXXXXXXXXXXXXXX must be 2
    else:
      self.assertEquals(len(related_list),1)
    for p in related_list:
      LOG('stepCheckActivateRequirementList, packing_list.asXML()',0,p.asXML())
      for o in p.objectValues():
        found = 0
        if o.getResourceValue()==sequence.get('resource'):
          packing_list_list.extend([p])
          found = 1
        if not found:
          mp_packing_list_list.extend([p])

    self.assertEquals(len(packing_list_list),1)
    portal_workflow = self.getWorkflowTool()
    sequence.edit(packing_list=packing_list_list[0])
    sequence.edit(mp_packing_list_list=mp_packing_list_list)

    # Check everything inside the simulation
    # Check the applied rule
    simulation_object = sequence.get('simulation_object')
    self.assertEquals(simulation_object.getLastExpandSimulationState(),'confirmed')
    self.assertEquals(simulation_object.getSpecialiseId(),'default_order_rule')
    self.assertEquals(simulation_object.getCausalityValue(),order)
    # Then check every line of the applied rule
    simulation_line_list = sequence.get('simulation_line_list')
    simulation_line_id_list = map(lambda x: x.getId(),simulation_line_list)
    #if sequence.get('order_type') == 'Production Order':
    if sequence.get('variated_order'):
      self.failIfDifferentSet(self.simulation_line_id_list,simulation_line_id_list)
    else:
      self.failIfDifferentSet(self.simple_simulation_line_id_list,simulation_line_id_list)
    for line in simulation_line_list:
      self.assertEquals(line.getDeliverable(),1)
      self.assertEquals(line.getCausalityState(),'expanded')
      #if sequence.get('order_type') == 'Production Order':
      if sequence.get('variated_order'):
        delivery_line_id = line.getId().split('_',1)[1]
        self.assertEquals(line.getOrderValue(),order._getOb('1')._getOb(delivery_line_id))
      else:
        delivery_line_id = line.getId()
        self.assertEquals(line.getOrderValue(),order._getOb('1'))
      self.assertEquals(line.getStartDate(),order.getStartDate())
      self.assertEquals(line.getStopDate(),order.getStopDate())
      #FAILS self.assertEquals(line.getTargetStartDate(),order.getTargetStartDate())
      #FAILS self.assertEquals(line.getTargetStopDate(),order.getTargetStopDate())
      self.assertEquals(line.getTargetSourceValue(),sequence.get('source_value'))
      self.assertEquals(line.getSourceValue(),sequence.get('source_value'))
      self.assertEquals(line.getSourceSectionValue(),sequence.get('source_section_value'))
      self.assertEquals(line.getSourceDecisionValue(),sequence.get('source_decision_value'))
      self.assertEquals(line.getSourceAdministrationValue(),sequence.get('source_administration_value'))
      self.assertEquals(line.getSourcePaymentValue(),sequence.get('source_payment_value'))
      self.assertEquals(line.getDestinationValue(),sequence.get('destination_value'))
      self.assertEquals(line.getDestinationSectionValue(),sequence.get('destination_section_value'))
      self.assertEquals(line.getDestinationDecisionValue(),sequence.get('destination_decision_value'))
      self.assertEquals(line.getDestinationAdministrationValue(),sequence.get('destination_administration_value'))
      self.assertEquals(line.getDestinationPaymentValue(),sequence.get('destination_payment_value'))
      order_cell = line.getOrderValue()
      delivery_cell = line.getDeliveryValue()
      root_order = order_cell.getRootDeliveryValue()
      root_delivery = delivery_cell.getRootDeliveryValue()
      self.assertEquals(line.getQuantityUnit(),order_cell.getQuantityUnit())
      # now check the rule inside this line
      rule_list = line.objectValues()

      if sequence.get('order_type') == 'Production Order':
        self.assertEquals(len(rule_list),1)
        rule = rule_list[0]
        self.assertEquals(rule.getId(),'default_transformation_rule')
        self.assertEquals(rule.getSpecialiseId(),'default_transformation_rule')
        self.assertEquals(rule.getCausalityValue(),sequence.get('transformation'))
        # now check objects inside this rule
        rule_line_list = rule.objectValues()
        rule_line_list = rule.objectValues()
        self.assertEquals(len(rule_line_list),2)
        good_rule_line_id_list = ('produced_resource','transformed_resource_0')
        rule_line_id_list = map(lambda x: x.getId(),rule_line_list)
        self.failIfDifferentSet(good_rule_line_id_list,rule_line_id_list)
        for rule_line in rule_line_list:
          self.assertEquals(rule_line.getPortalType(),'Simulation Movement')
          if rule_line.getId()=='produced_resource':
            self.assertEquals(rule_line.getResourceValue(),sequence.get('resource'))
            #self.assertEquals(rule_line.getTargetStartDate(),order.getTargetStartDate())
            self.assertEquals(rule_line.getCausalityState(),'expanded')
            #self.assertEquals(rule_line.getDestinationSection(),sequence.get('destination_section_value'))
            self.failIfDifferentSet(line.getVariationCategoryList(),rule_line.getVariationCategoryList())
            # Check if there is nothing inside
            self.assertEquals(len(rule_line.objectValues()),0)
          if rule_line.getId()=='transformed_resource_0':
            tissu = rule_line.getResourceValue()
            self.assertNotEquals(tissu,None)
            #good_variation_list = [sequence.get('category_tissu%s_variante')]
            #good_variation_list = filter(lambda x: x.find('color')==0,line.getVariationCategoryList())
            self.assertEquals(len(rule_line.getVariationCategoryList()),1)
            variante = rule_line.getVariationCategoryList()[0]
            variante = variante.split('_')[len(variante.split('_'))-1]
            good_variation_list = [sequence.get('category_tissu%s_variante%s' % (tissu.getId(),variante))]

            LOG('good_variation_list',0,good_variation_list)
            LOG('rule_line.getVariationCategoryList()',0,rule_line.getVariationCategoryList())
            LOG('rule_line.showDict',0,rule_line.showDict())
            self.failIfDifferentSet(good_variation_list,rule_line.getVariationCategoryList())
            tissu = sequence.get('tissu_list')[0]
            self.assertEquals(rule_line.getResourceValue(),tissu)
            self.assertEquals(rule_line.getSourceValue(),sequence.get('source_value'))
            self.assertEquals(rule_line.getSourceSectionValue(),sequence.get('source_section_value'))
            # Check object inside
            sourcing_line_list = rule_line.objectValues()
            self.assertEquals(len(sourcing_line_list),1)
            sourcing_line = sourcing_line_list[0]
            self.assertEquals(sourcing_line.getId(),'default_transformation_sourcing_rule')
            self.assertEquals(sourcing_line.getSpecialiseId(),'default_transformation_sourcing_rule')
            self.assertEquals(sourcing_line.getPortalType(),'Applied Rule')
            transformation_source_list = sourcing_line.objectValues()
            self.assertEquals(len(transformation_source_list),1)
            transformation_source = transformation_source_list[0]
            self.assertEquals(transformation_source.getId(),'transformation_source')
            LOG('transformation_source.getVariationCategoryList()',0,transformation_source.getVariationCategoryList())
            self.failIfDifferentSet(transformation_source.getVariationCategoryList(),good_variation_list)
            LOG('transformation_source.showDict()',0,transformation_source.showDict())
            resource_delivery_cell = transformation_source.getDeliveryValue()
            resource_root_delivery = resource_delivery_cell.getRootDeliveryValue()
            LOG('resource_root_delivery.getPath()',0,resource_root_delivery.getPath())
            self.assertNotEquals(resource_root_delivery,root_delivery)
      else:
        self.assertEquals(len(rule_list),0)

    # Check all packing list
    cancelled_list = []
    for packing_list in related_list:
      if sequence.get('modified_packing_list_resource') == 1:
        if portal_workflow.getInfoFor(packing_list,'simulation_state') == 'cancelled':
          # Here we have a canceled packing list after the fusion
          cancelled_list.append(packing_list)
          continue
      self.assertEquals(portal_workflow.getInfoFor(packing_list,'simulation_state'),'confirmed')
      LOG('looking at packing_list:',0,packing_list.getPhysicalPath())
      # Check if there is a line on the packing_list
      # And if this line get all informations
      line_list = packing_list.objectValues()
      if packing_list in packing_list_list:
        self.assertEquals(len(line_list),1)
        line = line_list[0]
        resource = sequence.get('resource')
        self.assertEquals(line.getResourceValue(),resource)
      else:
        tissu_list = sequence.get('good_tissu_list')
        all_tissu_list = sequence.get('tissu_list')
        line_resource_list = map(lambda x: x.getResourceValue(),line_list)
        LOG('CheckActivateRequirementList, tissu_list:',0,tissu_list)
        LOG('CheckActivateRequirementList, line_resource_list:',0,line_resource_list)
        self.assertEquals(len(line_list),len(tissu_list))
        if sequence.get('modified_packing_list_resource') == 1:
          self.failIfDifferentSet(line_resource_list,all_tissu_list)
          #for tissu in tissu_list:
          #  LOG('CheckActivateRequirementList, good_tissu_list',0,tissu_list)
          #  LOG('CheckActivateRequirementList, line_resource_list',0,line_resource_list)
          #  self.assertEquals(True,tissu in line_resource_list)

        else:
          self.failIfDifferentSet(line_resource_list,tissu_list)

      for line in line_list:
        if sequence.get('variated_order') is None:
          self.assertEquals(line.getTotalQuantity(),self.quantity)
          self.assertEquals(len(line.objectValues()),0)
        else:
          cell_list = line.objectValues()
          if line.getResourceValue()==sequence.get('resource'):
            self.assertEquals(len(line.objectValues()),4)
          else:
            # This is the packing list for the raw material
            self.assertEquals(len(line.objectValues()),2)

          # check variation_base_category_list
          if line.getResourceValue()==sequence.get('resource'):
            self.failIfDifferentSet(line.getVariationBaseCategoryList(),self.variation_base_category_list1)
            self.assertEquals(len(cell_list),4)
            color_and_size_list = sequence.get('color_and_size_list')
            membership_criterion_category_list = map(lambda x: tuple(x.getMembershipCriterionCategoryList()),cell_list)
            LOG('stepCheckActivateRequirementList, color_and_size_list',0,color_and_size_list)
            LOG('stepCheckActivateRequirementList, membership_criterion_category_list',0,membership_criterion_category_list)
            self.failIfDifferentSet(color_and_size_list,membership_criterion_category_list)
            for cell in cell_list:
              LOG('stepCheckActivateRequirementList, cell.getCategoryList',0,cell.getCategoryList())
              self.assertEquals(cell.getTargetQuantity(),self.quantity)
              self.assertEquals(cell.getSourceValue(),sequence.get('source_value'))
              self.assertEquals(cell.getSourceSectionValue(),sequence.get('source_section_value'))
              self.assertEquals(cell.getSourceDecisionValue(),sequence.get('source_decision_value'))
              self.assertEquals(cell.getSourceAdministrationValue(),sequence.get('source_administration_value'))
              self.assertEquals(cell.getSourcePaymentValue(),sequence.get('source_payment_value'))
              self.assertEquals(cell.getDestinationValue(),sequence.get('destination_value'))
              self.assertEquals(cell.getDestinationSectionValue(),sequence.get('destination_section_value'))
              self.assertEquals(cell.getDestinationDecisionValue(),sequence.get('destination_decision_value'))
              self.assertEquals(cell.getDestinationAdministrationValue(),sequence.get('destination_administration_value'))
              self.assertEquals(cell.getDestinationPaymentValue(),sequence.get('destination_payment_value'))
          else:
            self.assertEquals(True,line.getResourceValue() in sequence.get('tissu_list'))
            if not (sequence.get('modified_packing_list_resource') == 1):
              self.assertEquals(line.getResourceValue(),sequence.get('tissu_list')[0])
    if sequence.get('modified_packing_list_resource') == 1:
      self.assertEquals(len(cancelled_list),1)


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

  def stepModifyPackingListDestination(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    portal_categories = self.getCategoryTool()
    stock_category = portal_categories.resolveCategory(self.production_destination_site2)
    LOG('stepModifyPackingListDestination, stock_category',0,stock_category.getPhysicalPath())
    LOG('stepModifyPackingListDestination, packing_list.getDestinationValue()',0,packing_list.getDestinationValue().getPhysicalPath())
    packing_list.setTargetDestinationValue(stock_category)
    sequence.edit(destination_value=stock_category)
    sequence.edit(modified_packing_list_path=1)

  #def stepLazyModifyPackingListResource(self, sequence=None, sequence_list=None, lazy=0,**kw):
  #  self.stepModifyPackingListResource(sequence=sequence,sequence_list=sequence_list,lazy=1,**kw)

  def stepModifyPackingListResource(self, sequence=None, sequence_list=None, lazy=0,**kw):
    packing_list_list = sequence.get('mp_packing_list_list')
    packing_list = packing_list_list[0]
    tissu1 = sequence.get('tissu_first')
    # We should construct another tissu
    tissu_module = self.getTissuModule()
    tissu = tissu_module.newContent(portal_type='Tissu')
    tissu.setQuantityUnit('Longueur/Metre')
    tissu_variante1 = tissu.newContent(portal_type='Variante Tissu',id=self.variante_id1)
    category_tissu_variante1 = 'coloris/tissu/%s/%s' % (tissu.getId(),tissu_variante1.getId())
    tissu_variante2 = tissu.newContent(portal_type='Variante Tissu',id=self.variante_id2)
    category_tissu_variante2 = 'coloris/tissu/%s/%s' % (tissu.getId(),tissu_variante2.getId())
    seq_kw = {'tissu%s' % tissu.getId():tissu,
          'tissu%s_variante1' % tissu.getId():tissu_variante1,
          'tissu%s_variante2' % tissu.getId():tissu_variante2,
          'category_tissu%s_variante1' % tissu.getId():category_tissu_variante1,
          'category_tissu%s_variante2' % tissu.getId():category_tissu_variante2}
    sequence.edit(**seq_kw)
    sequence.edit(**seq_kw)
    tissu_list = sequence.get('tissu_list',[])
    tissu_list.extend([tissu])
    sequence.edit(tissu_list=tissu_list)
    for line in packing_list.objectValues():
      if line.getResourceValue()==tissu1:
        line.setResourceValue(tissu)
        if lazy!=1: # This means that we will change everything, including cells
          def rename_list(value,from_string,to_string):
            new_list = []
            for item in value:
              item = item.replace(from_string,to_string)
              new_list.append(item)
            return new_list
          from_string = 'tissu/' + tissu1.getId()
          to_string = 'tissu/' + tissu.getId()
          new_category_list = rename_list(line.getCategoryList(),from_string,to_string)
          line.setCategoryList(new_category_list)
          #new_variation_category_list = rename_list(line.getVariationCategoryList(),from_string,to_string)
          #line.setVariationCategoryList(new_variation_category_list)
          def rename_dict(mydict,from_string,to_string):
            newdict = PersistentMapping()
            for key in mydict.keys():
              new_value = mydict[key]
              if getattr(mydict[key],'keys',None) is not None:
                new_value = rename_dict(mydict[key],from_string,to_string)
              if type(key) is type('a'):
                if key.find(from_string)>=0:
                  new_key = key.replace(from_string,to_string)
                  newdict[new_key] = PersistentMapping()
                  newdict[new_key] = new_value
                else:
                  newdict[key] = PersistentMapping()
                  newdict[key] = new_value
              else:
                newdict[key] = PersistentMapping()
                newdict[key] = new_value
            return newdict

          line.index = rename_dict(line.index,from_string,to_string)

          #for id in line.objectIds():
          #  line._delObject(id)
          for cell in line.objectValues():
            LOG('cell.getPath()',0,cell.getPath())
            LOG('cell.getMembershipCriterionCategoryList',0,cell.getMembershipCriterionCategoryList())
            new_list = rename_list(cell.getMembershipCriterionCategoryList(),from_string,to_string)
            cell.setMembershipCriterionCategoryList(new_list)
      line.edit() # This simulate the user change, like this we will call propagateFromSimulation
    sequence.edit(modified_packing_list_resource=1)
    packing_list.recursiveImmediateReindexObject()

  def stepAddLinesToSalesPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    packing_list_line = packing_list.newContent(portal_type='Sales Packing List Line')
    component_module = self.getComponentModule()
    component = component_module._getOb(self.component_id)
    packing_list_line.setResourceValue(component)
    packing_list_line.setTargetQuantity(self.quantity)
    sequence.edit(new_packing_list_line=packing_list_line)

  def stepSetLessQuantityToPackingList(self, sequence=None, sequence_list=None, **kw):
    #packing_list = sequence.get('packing_list')
    #packing_list_line = packing_list._getOb('1')
    #packing_list_line.setTargetQuantity(self.low_quantity) # The user can change only the target
    #packing_list.edit() # so that we call workflow methods
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
    line.edit() # So that we calls workflow methods

  def stepCheckLessQuantityInSimulation(self, sequence=None, sequence_list=None, **kw):
    simulation_object=sequence.get('simulation_object')
    line_list = simulation_object.objectValues()
    self.assertEquals(len(line_list),1)
    line = line_list[0]
    #component_module = self.getComponentModule()
    #component = component_module._getOb(self.component_id)
    self.assertEquals(line.getQuantity(),self.quantity-1)

  def stepTic(self,**kw):
    self.tic()

  def testOrder(self, quiet=0,run=1):
    sequence_list = SequenceList()
    # Simple sequence with only some tic when it is required,
    # We create a sales order, confirm and then make sure the corresponding
    # packing list is made
    # ... OK
    sequence_string =   'AddSalesOrder PlanSalesOrder OrderSalesOrder ConfirmSalesOrder' \
                      + ' Tic Tic Tic Tic CheckConfirmOrder' \
                      + ' Tic Tic CheckActivateRequirementList'
    sequence_list.addSequenceString(sequence_string)

    # Simple sequence (same as the previous one) with only some tic when it is required and with no plan,
    # ... OK
    sequence_string =   'AddSalesOrder Tic ConfirmSalesOrder Tic CheckConfirmOrder ' \
                      + 'Tic CheckActivateRequirementList'
    sequence_list.addSequenceString(sequence_string)

    # Sequence where we set less quantity in the packing list
    # And we want to be sure that we will have less quantity in the simulation after we did accept
    # OK
    sequence_string =   'AddSalesOrder PlanSalesOrder OrderSalesOrder' \
                      + ' ConfirmSalesOrder Tic Tic Tic Tic CheckConfirmOrder' \
                      + ' Tic CheckActivateRequirementList SetLessQuantityToPackingList' \
                      + ' Tic Tic CheckPackingListDiverged AcceptPackingList Tic Tic Tic' \
                      + ' CheckLessQuantityInSimulation' 
    sequence_list.addSequenceString(sequence_string)

    # Simple sequence including variated resource with only some tic when it is required,
    # We create a sales order, confirm and then make sure the corresponding
    # packing list is made
    # ... OK
    sequence_string =   'AddVariatedSalesOrder PlanSalesOrder OrderSalesOrder' \
                      + ' ConfirmSalesOrder Tic Tic Tic Tic CheckConfirmOrder' \
                      + ' Tic Tic CheckActivateRequirementList'
    sequence_list.addSequenceString(sequence_string)

    # Sequence where we confirm an order, the corresponding packing list is automatically
    # created, we then check if the packing list is converged.
    # ... OK
    sequence_string =   'AddSalesOrder Tic Tic ConfirmSalesOrder Tic Tic CheckConfirmOrder Tic' \
                      + ' Tic Tic Tic Tic CheckActivateRequirementList Tic CheckPackingListConverged'
    sequence_list.addSequenceString(sequence_string)

    # Sequence where we confirm an order, the corresponding packing list is automatically
    # created, then we add new lines to the packing list by hand, we accept, we then check
    # if the packing list is converged.
    # ... FAILS
    sequence_string =   'AddSalesOrder Tic Tic ConfirmSalesOrder Tic Tic CheckConfirmOrder Tic' \
                      + ' Tic Tic Tic Tic CheckActivateRequirementList Tic CheckPackingListConverged' \
                      + ' AddLinesToSalesPackingList Tic Tic Tic Tic Tic CheckPackingListDiverged' 
    #sequence_list.addSequenceString(sequence_string)

    # Sequence where we confirm an order, the corresponding packing list is automatically
    # created, then we rename the color of the variated resource, everything should take
    # into account the new name
    # ... OK
    sequence_string =   'AddVariatedSalesOrder PlanSalesOrder OrderSalesOrder' \
                      + ' ConfirmSalesOrder Tic Tic Tic Tic CheckConfirmOrder' \
                      + ' Tic Tic CheckActivateRequirementList' \
                      + ' Tic Tic ModifyVariationId Tic Tic CheckConfirmOrder' \
                      + ' Tic Tic CheckActivateRequirementList'
    sequence_list.addSequenceString(sequence_string)

    # Sequence where we create an order, then the color is renamed, then we confirm
    # and we look if everyhing is going fine on the simulation and that the 
    # packing list is created correctly
    # ... OK
    sequence_string =   'AddVariatedSalesOrder Tic Tic ModifyVariationId Tic Tic Tic' \
                      + ' ConfirmSalesOrder Tic Tic CheckConfirmOrder Tic' \
                      + ' Tic Tic Tic Tic CheckActivateRequirementList Tic'
    sequence_list.addSequenceString(sequence_string)

    # Sequence where we confirm an order, the corresponding packing list is automatically
    # created, then we wants to only send one part of the packing list and finally 
    # we split and defer the packing list
    # ... Fails but was OK
    sequence_string =   'AddVariatedSalesOrder PlanSalesOrder OrderSalesOrder' \
                      + ' ConfirmSalesOrder Tic Tic Tic Tic CheckConfirmOrder' \
                      + ' CheckActivateRequirementList Tic Tic Tic' \
                      + ' UserGetReadyPackingList Tic Tic UserSetReadyPackingList Tic Tic' \
                      + ' UserStartPackingList Tic Tic Tic Tic' \
                      + ' AcceptDeliveryPackingList Tic CheckPackingListConverged Tic' \
                      + ' SetLessQuantityToPackingList Tic CheckPackingListDiverged Tic' \
                      + ' SplitAndDeferPackingList Tic Tic Tic' \
                      + ' CheckSplittedAndDefferedPackingList'  
    sequence_list.addSequenceString(sequence_string)

    # Sequence where we build a Production Order, we confirm this production order, then
    # we see if there is an the corresponding packing list is built
    # ... OK
    sequence_string =   'AddProductionOrder Tic PlanProductionOrder Tic OrderProductionOrder Tic Tic' \
                      + ' ConfirmProductionOrder Tic Tic Tic CheckConfirmOrder Tic Tic' \
                      + ' CheckActivateRequirementList Tic Tic' 
    sequence_list.addSequenceString(sequence_string)


    # Sequence where we build a Production Order, we confirm this production order, then
    # we have many packing list, we change the destination of one of the packing_list,
    # we must be sure that this change is taken into account into the simulation
    # ... ??? may be ok
    sequence_string =   'AddProductionOrder Tic PlanProductionOrder Tic OrderProductionOrder Tic Tic' \
                      + ' ConfirmProductionOrder Tic Tic Tic CheckConfirmOrder Tic Tic' \
                      + ' CheckActivateRequirementList Tic Tic ModifyPackingListDestination Tic Tic' \
                      + ' Tic Tic Tic RedirectPackingList Tic Tic Tic CheckConfirmOrder Tic CheckActivateRequirementList'  
    #sequence_list.addSequenceString(sequence_string)

    # Sequence where we build a Production Order, we plan this production order, then
    # we have many packing list, we change the resource of one of them,
    # we must be sure that this change is taken into account into the simulation,
    # ie a new line with the previous resource should be automatically created
    # ... OK 
    sequence_string =   'AddProductionOrder Tic PlanProductionOrder Tic OrderProductionOrder Tic Tic' \
                      + ' ConfirmProductionOrder Tic Tic Tic CheckConfirmOrder Tic Tic' \
                      + ' CheckActivateRequirementList Tic Tic ModifyPackingListResource Tic Tic' \
                      + ' Tic Tic Tic Tic Tic CheckConfirmOrder Tic CheckActivateRequirementList'  
    sequence_list.addSequenceString(sequence_string)

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
#    sequence.addStep('CheckConfirmOrder')
#    sequence.addStep('ActivateRequirementList')
#    sequence.addStep('Tic',required=0,max_replay=5)
#    sequence_list.addSequence(sequence)
    # Finally play all sequences
    sequence_list.play(self)



if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestOrder))
        return suite

