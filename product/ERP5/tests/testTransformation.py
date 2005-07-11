##############################################################################
#
# Copyright (c) 2004, 2005 Nexedi SARL and Contributors. All Rights Reserved.
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
from AccessControl.SecurityManagement import newSecurityManager, \
                                             noSecurityManager
from DateTime import DateTime
from Acquisition import aq_base, aq_inner
from zLOG import LOG
from Products.ERP5Type.DateUtils import addToDate
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
import time
import os
from Products.ERP5Type import product_path
from Products.CMFCore.utils import getToolByName
from testOrder import TestOrderMixin

class Test(TestOrderMixin,ERP5TypeTestCase):
  """
    Test business template erp5_trade 
  """
  run_all_test = 1
  transformation_portal_type = 'Apparel Transformation'
  component_portal_type = 'Apparel Component'
  component_variation_portal_type = 'Apparel Component Variation'

  def getTitle(self):
    return "Transformation"

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

  def stepCreateComponent(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
      Create a variated component
    """
    portal = self.getPortal()
    component_module = portal.getDefaultModule(self.component_portal_type)
    component = component_module.newContent()
    sequence.edit(component=component)
    variation1 = component.newContent(portal_type=self.component_variation_portal_type,id='1')
    variation2 = component.newContent(portal_type=self.component_variation_portal_type,id='2')
    supply_line = component.newContent(portal_type='Supply Line')



  def stepCreateTransformation(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
      Create a resource with no variation
    """
    portal = self.getPortal()
    transformation_module = portal.getDefaultModule(self.transformation_portal_type)
    transformation = transformation_module.newContent(portal_type=self.transformation_portal_type)
    sequence.edit(transformation=transformation)
    resource = sequence.get('resource')
    transformation.setResourceValue(resource)
    transformation.setVariationBaseCategoryList(('size','colour'))

    #size_list = ['Baby','Child/32','Child/34','Man','Woman'] 

  def test_01_getAggregatedAmountList(self, quiet=0, run=run_all_test):
    """
      Test the method getAggregatedAmountList
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = '\
                      CreateComponent \
                      CreateVariatedResource \
                      CreateTransformation \
                      '
                      #CheckNewPackingListAfterStartDateAdopt \
    # XXX Check if there is a new packing list created
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)



if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(Test))
        return suite

