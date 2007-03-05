##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
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
import os, sys
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, \
                                             noSecurityManager
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList

class TestAmount(ERP5TypeTestCase):

  run_all_test = 1
  resource_portal_type = "Apparel Model"
  amount_portal_type = "Transformation Transformed Resource"
  amount_parent_portal_type = "Transformation"
  # It is important to use property which are not defined on amount.
  variation_property_list = ['composition', 'margin_ratio']
  variation_property_dict = {
    'composition': 'azertyuio', 
    'margin_ratio': 2.4
  }
  failed_variation_property_dict = {
    'composition': 'azertyuio', 
    'margin_ratio': 2.4,
    'sfdvdfbdgbfgbfgbfgbfg': None,
  }

  def getTitle(self):
    return "Amount"

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_apparel')

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('rc', '', ['Manager'], [])
    user = uf.getUserById('rc').__of__(uf)
    newSecurityManager(None, user)

  def enableLightInstall(self):
    """
    You can override this. 
    Return if we should do a light install (1) or not (0)
    """
    return 1

  def enableActivityTool(self):
    """
    You can override this.
    Return if we should create (1) or not (0) an activity tool.
    """
    return 1

  def afterSetUp(self, quiet=1, run=run_all_test):
    self.login()

  def stepTic(self,**kw):
    self.tic()

  def stepCreateResource(self, sequence=None, sequence_list=None, **kw):
    """
      Create a resource
    """
    portal = self.getPortal()
    module = portal.getDefaultModule(self.resource_portal_type)
    resource = module.newContent(portal_type=self.resource_portal_type)
    # As the current resource as no variation property, 
    # we will create some for the test.
    resource.setVariationPropertyList(self.variation_property_list)
    sequence.edit(
        resource=resource,
    )

  def stepCreateAmount(self, sequence=None, sequence_list=None, **kw):
    """
      Create a amount to test
    """
    portal = self.getPortal()
    module = portal.getDefaultModule(self.amount_parent_portal_type)
    amount_parent = module.newContent(
                      portal_type=self.amount_parent_portal_type)
    amount = amount_parent.newContent(
                      portal_type=self.amount_portal_type)
    sequence.edit(
       amount=amount,
    )

  def stepSetAmountResource(self, sequence=None, sequence_list=None, **kw):
    """
      Add a resource to the amount.
    """
    amount = sequence.get('amount')
    resource = sequence.get('resource')
    amount.setResourceValue(resource)
    sequence.edit(
       variation_property_dict= \
           dict([(x, None) for x in self.variation_property_dict])
    )

  def stepCheckEmptyGetVariationPropertyDict(self, sequence=None, 
                                             sequence_list=None, **kw):
    """
      Test the method GetVariationPropertyDict.
    """
    amount = sequence.get('amount')
    vpd = amount.getVariationPropertyDict()
    self.assertEquals(vpd, {})

  def stepCheckEmptySetVariationPropertyDict(self, sequence=None, 
                                             sequence_list=None, **kw):
    """
      Test the method GetVariationPropertyDict.
    """
    amount = sequence.get('amount')
    self.assertRaises(KeyError, amount.setVariationPropertyDict,
                      self.variation_property_dict)

  def stepSetVariationPropertyDict(self, sequence=None, 
                                        sequence_list=None, **kw):
    """
      Test the method GetVariationPropertyDict.
    """
    amount = sequence.get('amount')
    amount.setVariationPropertyDict(self.variation_property_dict)
    sequence.edit(
       variation_property_dict=self.variation_property_dict
    )

  def stepCheckGetVariationPropertyDict(self, sequence=None, 
                                        sequence_list=None, **kw):
    """
      Test the method GetVariationPropertyDict.
    """
    amount = sequence.get('amount')
    vpd = amount.getVariationPropertyDict()
    self.failIfDifferentSet(vpd.keys(), 
                            sequence.get('variation_property_dict').keys())
    for key in vpd.keys():
      self.assertEquals(vpd[key], sequence.get('variation_property_dict')[key])

  def stepSetWrongVariationPropertyDict(self, sequence=None, 
                                        sequence_list=None, **kw):
    """
      Test the method GetVariationPropertyDict.
    """
    amount = sequence.get('amount')
    self.assertRaises(KeyError, amount.setVariationPropertyDict,
                      self.failed_variation_property_dict)

  def stepCheckEdit(self, sequence=None, sequence_list=None, **kw):
    """
      Test edit method on amount.
    """
    amount = sequence.get('amount')
    # If edit doesn't raise a error, it's ok.
    amount.edit(**self.variation_property_dict)
    sequence.edit(
       variation_property_dict=self.variation_property_dict
    )

  def test_01_variationProperty(self, quiet=0, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()
    # Test setVariationPropertyDict and
    # getVariationPropertyDict without
    # resource on Amount.
    sequence_string = '\
              CreateAmount \
              CheckEmptyGetVariationPropertyDict \
              CheckEmptySetVariationPropertyDict \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test setVariationPropertyDict and
    # getVariationPropertyDict
    sequence_string = '\
              CreateResource \
              CreateAmount \
              SetAmountResource \
              CheckGetVariationPropertyDict \
              SetVariationPropertyDict \
              CheckGetVariationPropertyDict \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test setVariationPropertyDict with a wrong property
    sequence_string = '\
              CreateResource \
              CreateAmount \
              SetAmountResource \
              SetWrongVariationPropertyDict \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test edit method on amount
    sequence_string = '\
              CreateResource \
              CreateAmount \
              SetAmountResource \
              CheckEdit \
              CheckGetVariationPropertyDict \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)


class TestMovement(ERP5TypeTestCase):
  """Tests for Movement class
  """
  def afterSetUp(self):
    self.login()
    self.portal = self.getPortal()

  def getPortalName(self):
    forced_portal_id = os.environ.get('erp5_tests_portal_id')
    if forced_portal_id:
      return str(forced_portal_id)
    return 'movement_test'

  def _makeOne(self, *args, **kw):
    from Products.ERP5.Document.Movement import Movement
    mvt = Movement(*args, **kw)
    # return it wrapped, so that it can access the types tool in _aq_dynamic
    return mvt.__of__(self.portal)

  def testQuantity(self):
    mvt = self._makeOne('mvt')
    mvt.setQuantity(10)
    self.assertEquals(10, mvt.getQuantity())
    self.assertEquals(None, mvt.getTotalPrice())
    mvt.edit(quantity=20)
    self.assertEquals(20, mvt.getQuantity())
  
  def testPrice(self):
    mvt = self._makeOne('mvt')
    self.assertEquals(None, mvt.getPrice())
    mvt.setPrice(10)
    self.assertEquals(10, mvt.getPrice())
    self.assertEquals(0, mvt.getTotalPrice())
    mvt.setQuantity(1)
    self.assertEquals(10, mvt.getTotalPrice())
    
  def testSourceDebit(self):
    mvt = self._makeOne('mvt')
    mvt.setSourceDebit(10)
    self.assertEquals(10, mvt.getSourceDebit())
    self.assertEquals(0, mvt.getSourceCredit())
    self.assertEquals(-10, mvt.getQuantity())

    mvt.edit(source_debit=20)
    self.assertEquals(20, mvt.getSourceDebit())
    self.assertEquals(0, mvt.getSourceCredit())
    self.assertEquals(-20, mvt.getQuantity())
  
  def testSourceCredit(self):
    mvt = self._makeOne('mvt')
    mvt.setSourceCredit(10)
    self.assertEquals(0, mvt.getSourceDebit())
    self.assertEquals(10, mvt.getSourceCredit())
    self.assertEquals(10, mvt.getQuantity())

    mvt.edit(source_credit=20)
    self.assertEquals(0, mvt.getSourceDebit())
    self.assertEquals(20, mvt.getSourceCredit())
    self.assertEquals(20, mvt.getQuantity())
  
  def testSourceDebitCredit(self):
    mvt = self._makeOne('mvt')
    mvt.setSourceCredit(10)
    mvt.edit(source_credit=0, source_debit=10)
    self.assertEquals(10, mvt.getSourceDebit())
    self.assertEquals(0, mvt.getSourceCredit())
    self.assertEquals(-10, mvt.getQuantity())

  def testDestinationDebit(self):
    mvt = self._makeOne('mvt')
    mvt.setDestinationDebit(10)
    self.assertEquals(10, mvt.getDestinationDebit())
    self.assertEquals(0, mvt.getDestinationCredit())
    self.assertEquals(10, mvt.getQuantity())

    mvt.edit(destination_debit=20)
    self.assertEquals(20, mvt.getDestinationDebit())
    self.assertEquals(0, mvt.getDestinationCredit())
    self.assertEquals(20, mvt.getQuantity())
  
  def testDestinationCredit(self):
    mvt = self._makeOne('mvt')
    mvt.setDestinationCredit(10)
    self.assertEquals(0, mvt.getDestinationDebit())
    self.assertEquals(10, mvt.getDestinationCredit())
    self.assertEquals(-10, mvt.getQuantity())

    mvt.edit(destination_credit=20)
    self.assertEquals(0, mvt.getDestinationDebit())
    self.assertEquals(20, mvt.getDestinationCredit())
    self.assertEquals(-20, mvt.getQuantity())
  
  def testDestinationDebitCredit(self):
    mvt = self._makeOne('mvt')
    mvt.setDestinationCredit(10)
    mvt.edit(destination_credit=0, destination_debit=10)
    self.assertEquals(10, mvt.getDestinationDebit())
    self.assertEquals(0, mvt.getDestinationCredit())
    self.assertEquals(10, mvt.getQuantity())
  
  # TODO: test asset price


class TestAccountingTransactionLine(TestMovement):
  """Tests for Accounting Transaction Line class, which have an overloaded
  'edit' method.
  """
  def _makeOne(self, *args, **kw):
    from Products.ERP5.Document.AccountingTransactionLine import \
          AccountingTransactionLine
    mvt = AccountingTransactionLine(*args, **kw)
    return mvt.__of__(self.portal)

  def testPrice(self):
    # price is always 1 for accounting transactions lines
    mvt = self._makeOne('mvt')
    self.assertEquals(1, mvt.getPrice())
  
  def testQuantity(self):
    mvt = self._makeOne('mvt')
    mvt.setQuantity(10)
    self.assertEquals(10, mvt.getQuantity())
    # self.assertEquals(None, mvt.getTotalPrice()) 
    # ... not with Accounting Transaction Lines, because price is 1
    mvt.edit(quantity=20)
    self.assertEquals(20, mvt.getQuantity())

  def testDefautSourceTotalAssetDebit(self):
    mvt = self._makeOne('mvt')
    mvt.edit(source_debit=100)
    self.assertEquals(100, mvt.getSourceInventoriatedTotalAssetDebit())
    self.assertEquals(0, mvt.getSourceInventoriatedTotalAssetCredit())
    self.assertEquals(100, mvt.getSourceInventoriatedTotalAssetPrice())
    
  def testDefautSourceTotalAssetCredit(self):
    mvt = self._makeOne('mvt')
    mvt.edit(source_credit=100)
    self.assertEquals(0, mvt.getSourceInventoriatedTotalAssetDebit())
    self.assertEquals(100, mvt.getSourceInventoriatedTotalAssetCredit())
    self.assertEquals(-100, mvt.getSourceInventoriatedTotalAssetPrice())
  
  def testDefautDestinationTotalAssetDebit(self):
    mvt = self._makeOne('mvt')
    mvt.edit(destination_debit=100)
    self.assertEquals(100, mvt.getDestinationInventoriatedTotalAssetDebit())
    self.assertEquals(0, mvt.getDestinationInventoriatedTotalAssetCredit())
    self.assertEquals(100, mvt.getDestinationInventoriatedTotalAssetPrice())
    
  def testDefautDestinationTotalAssetCredit(self):
    mvt = self._makeOne('mvt')
    mvt.edit(destination_credit=100)
    self.assertEquals(0, mvt.getDestinationInventoriatedTotalAssetDebit())
    self.assertEquals(100, mvt.getDestinationInventoriatedTotalAssetCredit())
    self.assertEquals(-100, mvt.getDestinationInventoriatedTotalAssetPrice())
  
  # TODO: more asset price tests


if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAmount))
    suite.addTest(unittest.makeSuite(TestMovement))
    suite.addTest(unittest.makeSuite(TestAccountingTransactionLine))
    return suite
