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
from DateTime import DateTime
from Products.ERP5.Document.Person import Person
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from Products.ERP5SyncML.Conduit.ERP5Conduit import ERP5Conduit
from Products.ERP5SyncML.SyncCode import SyncCode
from zLOG import LOG
import time

class Test(ERP5TypeTestCase):

  # Different variables used for this test
  run_all_test = 1

  def getTitle(self):
    """
    """
    return "Domain Tool"


  def getBusinessTemplateList(self):
    """
      Return the list of business templates.

    """
    return ('erp5_trade',)

  def getPortalId(self):
    return self.getPortal().getId()

  def logMessage(self,message):
    ZopeTestCase._print('\n%s ' % message)
    LOG('Testing... ',0,message)

  def getSalePackingListModule(self):
    return getattr(self.getPortal(),'sale_packing_list',None)

  def getSaleOrderModule(self):
    return getattr(self.getPortal(),'sale_order',None)

  def getOrderLine(self):
    return self.getSaleOrderModule()['1']['1']

  def getPredicate(self):
    return self.getSalePackingListModule()['1']

  def createData(self):
    # We have no place to put a Predicate, we will put it in a
    # Sale Packing List Module
    portal = self.getPortal()
    type_tool = self.getTypeTool()
    module_type = type_tool['Sale Packing List Module']
    module_type.allowed_content_types += ('Predicate Group',)
    packing_list_module = self.getSalePackingListModule()
    predicate = packing_list_module.newContent(id='1',portal_type='Predicate Group')
    predicate.setCriterion('quantity',identity=None,min=None,max=None)
    predicate.immediateReindexObject()
    
    # Then create an order with a particular line
    order_module = self.getSaleOrderModule()
    order =  order_module.newContent(id='1',portal_type='Sale Order')
    line = order.newContent(id='1',portal_type='Sale Order Line')
    line.immediateReindexObject()

    # Then create a base category
    portal_categories = self.getCategoryTool()
    for bc in ('region', ):
      if not hasattr(portal_categories, bc):
        portal_categories.newContent(portal_type='Base Category',id=bc)
      portal_categories[bc].setAcquisitionMaskValue(1)
      portal_categories[bc].setAcquisitionCopyValue(0)
      portal_categories[bc].setAcquisitionAppendValue(0)
      if not 'europe' in portal_categories[bc].objectIds():
        big_region = portal_categories[bc].newContent(id='europe',portal_type='Category')
      if not 'africa' in portal_categories[bc].objectIds():
        big_region = portal_categories[bc].newContent(id='africa',portal_type='Category')
      if not 'asia' in portal_categories[bc].objectIds():
        big_region = portal_categories[bc].newContent(id='asia',portal_type='Category')




  def checkPredicate(self, test=None):

    predicate = self.getPredicate()
    #predicate.setMembershipCriterionBaseCategoryList([])
    #predicate.setMembershipCriterionCategoryList([])
    #predicate.setCriterion('quantity',identity=45,min=None,max=None)
    predicate.immediateReindexObject()


    order_line = self.getOrderLine()
    domain_tool = self.getDomainTool()

    test = 0
    # Test with order line and predicate to none
    predicate_list = domain_tool.searchPredicateList(order_line,test=test)
    self.assertEquals(len(predicate_list),1) # Actually, a predicate where
                                             # nothing is defined is ok

    # Test with order line not none and predicate to none
    order_line.setQuantity(45)
    predicate_list = domain_tool.searchPredicateList(order_line,test=test)
    self.assertEquals(len(predicate_list),1)

    # Test with order line not none and predicate to identity
    order_line.setQuantity(45)
    predicate.setCriterion('quantity',identity=45,min=None,max=None)
    predicate.immediateReindexObject()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test)
    #get_transaction().commit()
    self.assertEquals(len(predicate_list),1)
    order_line.setQuantity(40)
    predicate_list = domain_tool.searchPredicateList(order_line,test=test)
    self.assertEquals(len(predicate_list),0)

    # Test with order line not none and predicate to min
    order_line.setQuantity(45)
    predicate = self.getPredicate()
    predicate.setCriterion('quantity',identity=None,min=30,max=None)
    predicate.immediateReindexObject()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test)
    self.assertEquals(len(predicate_list),1)
    order_line.setQuantity(10)
    predicate_list = domain_tool.searchPredicateList(order_line,test=test)
    self.assertEquals(len(predicate_list),0)

    # Test with order line not none and predicate to max
    order_line.setQuantity(45)
    predicate = self.getPredicate()
    predicate.setCriterion('quantity',identity=None,min=None,max=50)
    predicate.immediateReindexObject()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test)
    self.assertEquals(len(predicate_list),1)
    order_line.setQuantity(60)
    predicate_list = domain_tool.searchPredicateList(order_line,test=test)
    self.assertEquals(len(predicate_list),0)

    # Test with order line not none and predicate to min max
    order_line.setQuantity(20)
    predicate = self.getPredicate()
    predicate.setCriterion('quantity',identity=None,min=30,max=50)
    predicate.immediateReindexObject()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test)
    self.assertEquals(len(predicate_list),0)
    order_line.setQuantity(60)
    predicate_list = domain_tool.searchPredicateList(order_line,test=test)
    self.assertEquals(len(predicate_list),0)
    order_line.setQuantity(45)
    predicate_list = domain_tool.searchPredicateList(order_line,test=test)
    self.assertEquals(len(predicate_list),1)

    # Test with order line not none and predicate to min max
    # and also predicate to a category
    predicate.setMembershipCriterionBaseCategoryList(['region'])
    predicate.setMembershipCriterionCategoryList(['region/europe'])
    predicate.immediateReindexObject()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test)
    #get_transaction().commit()
    self.assertEquals(len(predicate_list),0)
    order_line.setCategoryList(['region/africa'])
    predicate_list = domain_tool.searchPredicateList(order_line,test=test)
    self.assertEquals(len(predicate_list),0)
    order_line.setCategoryList(['region/europe'])
    predicate_list = domain_tool.searchPredicateList(order_line,test=test)
    self.assertEquals(len(predicate_list),1)
    order_line.setQuantity(60)
    predicate_list = domain_tool.searchPredicateList(order_line,test=test)
    self.assertEquals(len(predicate_list),0)

  def test_01_SearchPredidateListWithNoTest(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Search Predicate List With No Test')
    self.createData()
    self.checkPredicate(test=0)

  def test_02_SearchPredidateListWithTest(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Search Predicate List With Test')
    self.createData()
    self.checkPredicate(test=1)


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(Test))
        return suite

