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

class TestResource(ERP5TypeTestCase):
  """
    Test ERP5 document Resource
  """
  run_all_test = 1

  # Global variables
  resource_portal_type = 'Apparel Model'
  variation_base_category_list = ['colour', 'size', 'morphology']
  size_list = ['size/Child','size/Man'] 

  def getBusinessTemplateList(self):
    """
      Install needed business template
    """
    return ('erp5_apparel_depend','erp5_apparel')

  def getTitle(self):
    return "Resource"

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

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('rc', '', ['Manager'], [])
    user = uf.getUserById('rc').__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    self.login()
    self.portal = self.getPortal()
    self.category_tool = self.getCategoryTool()
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()
    self.createCategories()

  def createCategories(self):
    """ 
      Light install create only base categories, so we create 
      some categories for testing them
    """
    size_category_list = ['Baby', 'Child', 'Man', 'Woman']
    if len(self.category_tool.size.contentValues()) == 0 :
      for category_id in size_category_list:
        o = self.category_tool.size.newContent(portal_type='Category',
                                               id=category_id)
    self.size_category_list = map(lambda x: 'size/%s' % x, 
                                  size_category_list)

    colour_category_list = ['blue', 'green']
    if len(self.category_tool.colour.contentValues()) == 0 :
      for category_id in colour_category_list:
        o = self.category_tool.colour.newContent(portal_type='Category',
                                               id=category_id)
    self.colour_category_list = map(lambda x: 'colour/%s' % x, 
                                    colour_category_list)

    self.morphology_category_list = []
    self.base_category_content_list = {
      'size':self.size_category_list,
      'colour':self.colour_category_list,
      'morphology':self.morphology_category_list
    }

  def stepTic(self,**kw):
    self.tic()

  def stepCreateResource(self, sequence=None, sequence_list=None, **kw):
    """
      Create a resource without variation
    """
    resource_module = self.portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent( \
                                 portal_type=self.resource_portal_type)
    resource.edit(
      title = "Resource"
    )
    sequence.edit(resource=resource)
    self.category_list = []
    # Actually, resource has no individual variation
    for base_category in resource.getVariationBaseCategoryList():
      sequence.edit(**{base_category:None})

  def stepCheckGetVariationBaseCategoryList(self, sequence=None, 
                                             sequence_list=None, **kw):
    """
      Check if getVariationBaseCategoryList returns the good result
    """
    resource = sequence.get('resource')
    vbcl = resource.getVariationBaseCategoryList()
    self.failIfDifferentSet(self.variation_base_category_list, vbcl)

  def stepCheckGetVariationRangeCategoryList(self, sequence=None, 
                                             sequence_list=None, **kw):
    """
      Check if getVariationRangeCategoryList returns the good result
    """
    resource = sequence.get('resource')
    vbcl = resource.getVariationBaseCategoryList()
    correct_variation_range_category_list = []
    for base_category in vbcl:
      # Check if resource has individual variations
      individual_variation_list = sequence.get(base_category)
      if individual_variation_list is None:
        correct_variation_range_category_list.extend(
                               self.base_category_content_list[base_category])
      else:
        correct_variation_range_category_list.extend(individual_variation_list)

    vrcl = resource.getVariationRangeCategoryList()
#    ZopeTestCase._print('\n')
#    ZopeTestCase._print('correct_variation_range_category_list: %s\n' %
#        str(correct_variation_range_category_list))
#    ZopeTestCase._print('vrcl: %s\n' % str(vrcl))
    self.failIfDifferentSet(correct_variation_range_category_list, vrcl)

  def stepSetCategoryVariation(self, sequence=None, sequence_list=None, **kw):
    """
      Set category variation to current resource
    """
    resource = sequence.get('resource')
    size_list = map(lambda x: x[len('size/'):], self.size_list)
    resource.setSizeList(size_list) 
    self.category_list = self.size_list[:]

  def stepSetIndividualVariationWithEmptyBase(self, sequence=None, 
                                              sequence_list=None, **kw):
    """
      Set individual variation to current resource with empty base 
      category
    """
    resource = sequence.get('resource')
    morphology_list = []
    morphology_variation_count = 2
    for i in range(morphology_variation_count) :
      variation_portal_type = 'Apparel Model Morphology Variation'
      variation = resource.newContent(portal_type=variation_portal_type)
      variation.edit(
        title = 'MorphologyVariation%s' % str(i)
      )
      morphology_list.append('morphology/%s' %
                                        variation.getRelativeUrl())
    # store individual resource
    sequence.edit(morphology=morphology_list)

  def stepSetIndividualVariationWithFillBase(self, sequence=None, 
                                              sequence_list=None, **kw):
    """
      Set individual variation to current resource with fill base 
      category
    """
    resource = sequence.get('resource')
    colour_list = []
    colour_variation_count = 1 
    for i in range(colour_variation_count) :
      variation_portal_type = 'Apparel Model Colour Variation'
      variation = resource.newContent(portal_type=variation_portal_type)
      variation.edit(
        title = 'ColourVariation%s' % str(i)
      )
      colour_list.append('colour/%s' % variation.getRelativeUrl())
    # store individual resource
    sequence.edit(colour=colour_list)

  def test_01_getVariationBaseCategoryList(self, quiet=0, run=run_all_test):
    """
      Test the method getVariationBaseCategoryList on a resource.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when resource has no variation
    sequence_string = '\
                      CreateResource \
                      CheckGetVariationBaseCategoryList \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def genericTest(self, test_method_name):
    """
      Generic test on a resource.
    """
    sequence_list = SequenceList()
    # Test when resource has no variation
    sequence_string = '\
                      CreateResource \
                      %s \
                      ' % test_method_name
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has category variations
    sequence_string = '\
                      CreateResource \
                      SetCategoryVariation \
                      %s \
                      ' % test_method_name
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has individual variation and base category
    # has no content
    sequence_string = '\
                      CreateResource \
                      SetIndividualVariationWithEmptyBase \
                      Tic \
                      %s \
                      ' % test_method_name
    sequence_list.addSequenceString(sequence_string)
    # Test when resource has individual variation and base category
    # has category content
    sequence_string = '\
                      CreateResource \
                      SetIndividualVariationWithFillBase \
                      Tic \
                      %s \
                      ' % test_method_name
    sequence_list.addSequenceString(sequence_string)
    # Test with all cases
    sequence_string = '\
                      CreateResource \
                      SetCategoryVariation \
                      SetIndividualVariationWithEmptyBase \
                      SetIndividualVariationWithFillBase \
                      Tic \
                      %s \
                      ' % test_method_name
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_02_getVariationRangeCategoryList(self, quiet=0, run=run_all_test):
    """
      Test the method getVariationRangeCategoryList on a resource.
    """
    if not run: return
    self.genericTest('CheckGetVariationRangeCategoryList')

  def stepCheckGetVariationRangeCategoryItemList(self, sequence=None, 
                                                 sequence_list=None, **kw):
    """
      Check if getVariationRangeCategoryItemList returns the good result.
      Does not test display...
      Item are left display.
    """
    resource = sequence.get('resource')
    vrcl = resource.getVariationRangeCategoryList()
    vrcil = resource.getVariationRangeCategoryItemList()
#    ZopeTestCase._print('\n')
#    ZopeTestCase._print('vrcl: %s\n' % str(vrcl))
#    ZopeTestCase._print('vrcil: %s\n' % str(vrcil))
    self.failIfDifferentSet(vrcl, map(lambda x: x[1], vrcil))

  def test_03_getVariationRangeCategoryItemList(self, quiet=0, 
                                                run=run_all_test):
    """
      Test the method getVariationRangeCategoryItemList on a resource.
    """
    if not run: return
    self.genericTest('CheckGetVariationRangeCategoryItemList')

  def stepCheckGetVariationCategoryList(self, sequence=None, 
                                                 sequence_list=None, **kw):
    """
      Check if getVariationCategoryList returns the good result,
      with parameter omit_individual_variation=1.
    """
    resource = sequence.get('resource')
    vcl = resource.getVariationCategoryList()
#    ZopeTestCase._print('\n')
#    ZopeTestCase._print('vcl: %s\n' % str(vcl))
    self.failIfDifferentSet(self.category_list, vcl)

  def test_04_getVariationCategoryList(self, quiet=0, run=run_all_test):
    """
      Test the method getVariationCategoryList on a resource.
    """
    if not run: return
    self.genericTest('CheckGetVariationCategoryList')

  def stepCheckGetVariationCategoryListWithoutOmit(self, sequence=None, 
                                                 sequence_list=None, **kw):
    """
      Check if getVariationCategoryList returns the good result,
      with parameter omit_individual_variation=0.
    """
    resource = sequence.get('resource')
    vcl = resource.getVariationCategoryList(omit_individual_variation=0)
    correct_vcl = self.category_list[:]

    for base_category in resource.getVariationBaseCategoryList():
      # Check if resource has individual variations
      individual_variation_list = sequence.get(base_category)
      if individual_variation_list is not None:
        correct_vcl.extend(individual_variation_list)

#    ZopeTestCase._print('\n')
#    ZopeTestCase._print('vcl: %s\n' % str(vcl))
#    ZopeTestCase._print('correct_vcl: %s\n' % str(correct_vcl))
    self.failIfDifferentSet(correct_vcl, vcl)

  def test_05_getVariationCategoryList(self, quiet=0, run=run_all_test):
    """
      Test the method getVariationCategoryList on a resource
      with parameter omit_individual_variation=0.
    """
    if not run: return
    self.genericTest('CheckGetVariationCategoryListWithoutOmit')

  def stepCheckGetVariationCategoryItemList(self, sequence=None, 
                                                 sequence_list=None, **kw):
    """
      Check if getVariationCategoryItemList returns the good result,
      with parameter omit_individual_variation=1.
    """
    resource = sequence.get('resource')
    vcl = resource.getVariationCategoryList()
    vcil = resource.getVariationCategoryItemList()
#    ZopeTestCase._print('\n')
#    ZopeTestCase._print('vcl: %s\n' % str(vcl))
#    ZopeTestCase._print('vcil: %s\n' % str(vcil))
    self.failIfDifferentSet(vcl, map(lambda x: x[1], vcil))

  def test_06_getVariationCategoryItemList(self, quiet=0, run=run_all_test):
    """
      Test the method getVariationCategoryItemList on a resource.
    """
    if not run: return
    self.genericTest('CheckGetVariationCategoryItemList')

  def stepCheckGetVariationCategoryItemListWithoutOmit(self, sequence=None, 
                                                 sequence_list=None, **kw):
    """
      Check if getVariationCategoryItemList returns the good result,
      with parameter omit_individual_variation=0.
    """
    resource = sequence.get('resource')
    vcl = resource.getVariationCategoryList(omit_individual_variation=0)
    vcil = resource.getVariationCategoryItemList(omit_individual_variation=0)
#     ZopeTestCase._print('\n')
#     ZopeTestCase._print('vcl: %s\n' % str(vcl))
#     ZopeTestCase._print('vcil: %s\n' % str(vcil))
    self.failIfDifferentSet(vcl, map(lambda x: x[1], vcil))

  def test_07_getVariationCategoryItemList(self, quiet=0, run=run_all_test):
    """
      Test the method getVariationCategoryItemList on a resource
      with parameter omit_individual_variation=0.
    """
    if not run: return
    self.genericTest('CheckGetVariationCategoryItemListWithoutOmit')

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestResource))
        return suite
