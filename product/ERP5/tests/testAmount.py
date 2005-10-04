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
    return ('erp5_pdm', 'erp5_apparel')

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
    amount = module.newContent(
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
    try:
      amount.setVariationPropertyDict(self.variation_property_dict)
    except KeyError:
      return
    else:
      raise KeyError

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
    try:
      amount.setVariationPropertyDict(self.failed_variation_property_dict)
    except KeyError:
      return
    else:
      raise KeyError

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
    """
      Test property existence
    """
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

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestConstraint))
        return suite
