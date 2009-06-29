#############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                    Daniel Feliubadalo  <daniel@sip2000.com>
#                    Romain Courteaud  <romain@nexedi.com>
#                    Alexandre Boeglin  <alex@nexedi.com>
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

"""
Tests Resource Variations
"""
import unittest
import transaction
from Testing import ZopeTestCase
from zLOG import LOG
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import reindex
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl import getSecurityManager
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
from DateTime import DateTime

class ResourceVariationTestCase(ERP5TypeTestCase):
  """Tests starts with a preference activated for self.my_organisation, logged in
  as a user with Manager role.

  All documents created appart from this configuration will be deleted in
  teardown. So users of this test case are encouraged to create new documents
  rather than modifying default documents.
  """
  def logMessage(self, msg, tab=0):
    """
    Log a message.
    """
    if tab:
      msg = '  %s' % msg
    ZopeTestCase._print('\n%s' % msg)
    LOG('testResource.play', 0, msg)

  def _doWorkflowAction(self, ob, action, **kw):
    self.portal.portal_workflow.doActionFor(ob, action,
                                            comment = 'for unit test',**kw)

  @reindex
  def _makeOneResource(self, portal_type='Product',
                       validation_state='draft', **kw):
    """
    Creates an resource

    The default settings is for self.section.
    You can pass a list of mapping as lines, then lines will be created
    using this information.
    """
    rs = self.portal.getDefaultModule(portal_type).newContent(
                              portal_type=portal_type,**kw)

    if validation_state == 'validated':
      rs.validate()
    return rs

  @reindex
  def _makeOneResourceIndividualVariation(self, resource, **kw):
    """
    Creates a Individual variation sub object, and edit it with kw.
    """
    iv = resource.newContent(portal_type='%s Individual Variation' % \
                              resource.getPortalType(), **kw)
    return iv

  def login(self):
    """
    Login Manager roles.
    """
    uf = self.getPortal().acl_users
    uf._doAddUser('testmanager', 'test', ['Manager', 'Assignee', 'Assignor',
                               'Associate', 'Auditor', 'Author'], [])
    user = uf.getUserById('testmanager').__of__(uf)
    newSecurityManager(None, user)
    
  def loginUser(self):
    """
    Login without Manager roles.
    """
    uf = self.getPortal().acl_users
    uf._doAddUser('user', 'user',
                  ['Assignee', 'Assignor', 'Associate',
                   'Auditor', 'Author'], [])
    user = uf.getUserById('user').__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    """
    - create categories
    - create preference
    - make sure categories are included to portal types
    """
    self.portal = self.getPortal()
    self.portal_categories = self.portal.portal_categories
    self.portal_preferences = self.portal.portal_preferences
    self.product_module = self.portal.product_module
    self.service_module = self.portal.service_module
    self.component_module = self.portal.component_module

    # create variation categories
    category_type=('line', 'variation')
    if not self.portal_categories.hasContent('required_size'):
      size = self.portal_categories.newContent(portal_type='Base Category',
                                title='Required Size',
                                reference='required_size',
                                id='required_size',
                                category_type=category_type)
    else:
      size = self.portal_categories['required_size']

    size.newContent(portal_type='Category', title='Large',
                    reference='l',id='l')
    size.newContent(portal_type='Category', title='Medium',
                    reference='l',id='m')
    size.newContent(portal_type='Category', title='Small',
                    reference='l',id='s')
    size.newContent(portal_type='Category', title='XL',
                    reference='l',id='xl')
    size.newContent(portal_type='Category', title='XXL',
                    reference='l',id='xxl')

    if not self.portal_categories.hasContent('option_colour'):
      colour = self.portal_categories.newContent(portal_type='Base Category',
                                title='Optional Colour',
                                reference='option_colour',
                                id='option_colour',
                                category_type=category_type)
    else:
      colour = self.portal_categories['option_colour']

    colour.newContent(portal_type='Category', title='Blue',
                      reference='l',id='blue')
    colour.newContent(portal_type='Category', title='Green',
                      reference='l',id='green')
    colour.newContent(portal_type='Category', title='Red',
                      reference='l',id='red')

    if not self.portal_categories.hasContent('individual_aspect'):
      aspect = self.portal_categories.newContent(portal_type='Base Category',
                                title='Individual Aspect',
                                reference='individual_aspect',
                                id='individual_aspect',
                                category_type=category_type)

    aspect.newContent(portal_type='Category', title='Aspect 1',
                      reference='A1',id='a1')
    aspect.newContent(portal_type='Category', title='Aspect 2',
                      reference='A2',id='a2')

    #create resource variation preferences
    preference = getattr(self.portal_preferences, 'test_site_preference', None)
    if preference is None:
      preference = self.portal_preferences.newContent(portal_type='Preference',
                                title='Default Site Preference',
                                id='test_site_preference')
      preference.enable()

    value='individual_aspect'
    preference.setPreferredProductIndividualVariationBaseCategory(value)
    preference.setPreferredServiceIndividualVariationBaseCategory(value)
    preference.setPreferredComponentIndividualVariationBaseCategory(value)

    value=('required_size',)
    preference.setPreferredProductVariationBaseCategoryList(value)
    preference.setPreferredServiceVariationBaseCategoryList(value)
    preference.setPreferredComponentVariationBaseCategoryList(value)

    value=('option_colour',)
    preference.setPreferredProductOptionalVariationBaseCategory(value)
    preference.setPreferredServiceOptionalVariationBaseCategory(value)
    preference.setPreferredComponentOptionalVariationBaseCategory(value)

    # all this available to catalog

    #adding to base categories of resources
    #for use setRequiredSizeList and setOptionColourList methods
    self.portal.portal_types['Product'].base_category_list = [
                                            'required_size',
                                            'option_colour',
                                            'individual_aspect']
    self.portal.portal_types['Service'].base_category_list = [
                                            'required_size',
                                            'option_colour',
                                            'individual_aspect']
    self.portal.portal_types['Component'].base_category_list = [
                                            'required_size',
                                            'option_colour',
                                            'individual_aspect']
                                            
    transaction.commit()
    self.tic()

  def beforeTearDown(self):
    """Remove all documents.
    """
    transaction.abort()
    self.product_module.manage_delObjects(
                      list(self.service_module.objectIds()))
    self.service_module.manage_delObjects(
                      list(self.service_module.objectIds()))
    self.component_module.manage_delObjects(
                      list(self.component_module.objectIds()))
    self.portal_categories.manage_delObjects((['required_size',
                                    'individual_aspect','option_colour']))

    transaction.commit()
    self.tic()

  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    return ('erp5_base', 'erp5_pdm')
  
  def _testResourceDefaultConfig(self,resource):
    """
    Check variation API when creating a default resource.
    This should use what is defined in preferences.
    """
    # XXX Check default config
    self.assertSameSet(['required_size', 
                        'option_colour', 
                        'individual_aspect'],
                        resource.getVariationBaseCategoryList())
                        
    self.assertSameSet(['required_size/l',
                        'required_size/m', 
                        'required_size/s', 
                        'required_size/xl', 
                        'required_size/xxl', 
                        'individual_aspect/a1', 
                        'individual_aspect/a2', 
                        'option_colour/blue', 
                        'option_colour/green', 
                        'option_colour/red'], 
                        resource.getVariationRangeCategoryList())
                        
    self.assertSameSet([], resource.getVariationCategoryList())
    
  def _testResourceWithoutVariation(self,resource):
    """
    Check variation API when creating a resource and removing its variation
    axes
    """
    resource.edit(variation_base_category_list=[],
                  optional_variation_base_category_list=[],
                  individual_variation_base_category_list=[])

    self.assertSameSet([], resource.getVariationBaseCategoryList())
    self.assertSameSet([], resource.getVariationRangeCategoryList())
    self.assertSameSet([], resource.getVariationCategoryList())

    # XXX What happens when we create an individual variation
    resource_circular = self._makeOneResourceIndividualVariation(
              resource,
              id='1',
              title='Circular')

    self.assertSameSet([], resource.getVariationBaseCategoryList())
    self.assertSameSet([], resource.getVariationRangeCategoryList())
    self.assertSameSet([], resource.getVariationCategoryList())

  def _testResourceCategoryVariation(self,resource):
    """
    Check variation API when defining only category as variation
    axes
    """
    # Define variations
    resource.setRequiredSizeList(['l', 'm','s'])

    resource.setOptionColourList(['blue'])

    self.assertSameSet(['required_size','option_colour','individual_aspect'],
                       resource.getVariationBaseCategoryList())
    self.assertSameSet(['required_size/l',
                        'required_size/m',
                        'required_size/s',
                        'option_colour/blue'],
                       resource.getVariationCategoryList())
    self.assertSameSet(['required_size/l',
                        'required_size/m',
                        'required_size/s',
                        'required_size/xl',
                        'required_size/xxl',
                        'option_colour/blue',
                        'option_colour/green',
                        'option_colour/red',
                        'individual_aspect/a1',
                        'individual_aspect/a2'],
                        resource.getVariationRangeCategoryList())

    # Now, define aspect categories, which should not be used as variation
    resource.setIndividualAspectList(['a1'])

    self.assertSameSet(['required_size','option_colour','individual_aspect'],
                       resource.getVariationBaseCategoryList())
    self.assertSameSet(['required_size/l',
                        'required_size/m',
                        'required_size/s',
                        'option_colour/blue'],
                       resource.getVariationCategoryList())
    self.assertSameSet(['required_size/l',
                        'required_size/m',
                        'required_size/s',
                        'required_size/xl',
                        'required_size/xxl',
                        'option_colour/blue',
                        'option_colour/green',
                        'option_colour/red',
                        'individual_aspect/a1',
                        'individual_aspect/a2'],
                       resource.getVariationRangeCategoryList())

  def _testResourceIndividualVariation(self,resource):
    """
    Check variation API when defining individual variation
    """
    # Creating individual variations of resource
    resource_iv1 = self._makeOneResourceIndividualVariation(resource,
              id='1',
              title='Circular',
    )

    resource_iv2 = self._makeOneResourceIndividualVariation(resource,
              id='2',
              title='Triangular',
    )

    resource_iv3 = self._makeOneResourceIndividualVariation(resource,
              id='3',
              title='Square',
    )
    # Check default parameter
    self.assertSameSet([],
                       resource.getVariationCategoryList())
    self.assertSameSet(['individual_aspect/'+resource_iv1.getRelativeUrl(),
                        'individual_aspect/'+resource_iv2.getRelativeUrl(),
                        'individual_aspect/'+resource_iv3.getRelativeUrl()],
                        resource.getVariationCategoryList(
                                omit_individual_variation=0))
    self.assertSameSet(['required_size/l',
                        'required_size/m',
                        'required_size/s',
                        'required_size/xl',
                        'required_size/xxl',
                        'option_colour/blue',
                        'option_colour/green',
                        'option_colour/red',
                        'individual_aspect/'+resource_iv1.getRelativeUrl(),
                        'individual_aspect/'+resource_iv2.getRelativeUrl(),
                        'individual_aspect/'+resource_iv3.getRelativeUrl()],
                        resource.getVariationRangeCategoryList())
    self.assertSameSet(['required_size/l',
                        'required_size/m',
                        'required_size/s',
                        'required_size/xl',
                        'required_size/xxl',
                        'option_colour/blue',
                        'option_colour/green',
                        'option_colour/red',
                        'individual_aspect/'+resource_iv1.getRelativeUrl(),
                        'individual_aspect/'+resource_iv2.getRelativeUrl(),
                        'individual_aspect/'+resource_iv3.getRelativeUrl()],
                        resource.getVariationRangeCategoryList(
                                omit_individual_variation=0))

    # Now, define aspect categories, which should not be used as variation
    resource.setIndividualAspectList(['a1'])

    # Check default parameter
    self.assertSameSet([],
                       resource.getVariationCategoryList())
    self.assertSameSet(['individual_aspect/'+resource_iv1.getRelativeUrl(),
                        'individual_aspect/'+resource_iv2.getRelativeUrl(),
                        'individual_aspect/'+resource_iv3.getRelativeUrl()],
                       resource.getVariationCategoryList(
                                omit_individual_variation=0))
    self.assertSameSet(['required_size/l',
                        'required_size/m',
                        'required_size/s',
                        'required_size/xl',
                        'required_size/xxl',
                        'option_colour/blue',
                        'option_colour/green',
                        'option_colour/red',
                        'individual_aspect/'+resource_iv1.getRelativeUrl(),
                        'individual_aspect/'+resource_iv2.getRelativeUrl(),
                        'individual_aspect/'+resource_iv3.getRelativeUrl()],
                       resource.getVariationRangeCategoryList())
    self.assertSameSet(['required_size/l',
                        'required_size/m',
                        'required_size/s',
                        'required_size/xl',
                        'required_size/xxl',
                        'option_colour/blue',
                        'option_colour/green',
                        'option_colour/red',
                        'individual_aspect/'+resource_iv1.getRelativeUrl(),
                        'individual_aspect/'+resource_iv2.getRelativeUrl(),
                        'individual_aspect/'+resource_iv3.getRelativeUrl()],
                       resource.getVariationRangeCategoryList(
                                omit_individual_variation=0))

  def _testResourceVariation(self,resource):
    """
    Combine individual and category variations
    """
    resource.setRequiredSizeList(['l', 'm', 's'])

    resource.setOptionColourList(['blue'])

    # creating individual variations of resource
    resource_iv1=self._makeOneResourceIndividualVariation(resource,
              id='1',
              title='Circular',
    )

    resource_iv2=self._makeOneResourceIndividualVariation(resource,
              id='2',
              title='Triangular',
    )

    resource_iv3=self._makeOneResourceIndividualVariation(resource,
              id='3',
              title='Square',
    )

    self.assertSameSet(['option_colour',],
                             resource.getOptionalVariationBaseCategoryList())

    self.assertSameSet(['individual_aspect',],
                             resource.getIndividualVariationBaseCategoryList())

    # Check default parameters
    self.assertSameSet(['required_size','option_colour','individual_aspect'],
                             resource.getVariationBaseCategoryList())

    self.assertSameSet(['required_size','option_colour','individual_aspect'],
                             resource.getVariationBaseCategoryList(
                                         omit_individual_variation=0,
                                         omit_optional_variation=0))

    self.assertSameSet(['required_size','option_colour'],
                             resource.getVariationBaseCategoryList(
                                         omit_individual_variation=1,
                                         omit_optional_variation=0))

    self.assertSameSet(['required_size',],
                             resource.getVariationBaseCategoryList(
                                         omit_individual_variation=1,
                                         omit_optional_variation=1))

    # Check default parameters
    self.assertSameSet(['required_size/l',
                        'required_size/m',
                        'required_size/s',
                        'option_colour/blue'],
                             resource.getVariationCategoryList())

    self.assertSameSet(['required_size/l',
                        'required_size/m',
                        'required_size/s',
                        'option_colour/blue',
                        'individual_aspect/'+resource_iv1.getRelativeUrl(),
                        'individual_aspect/'+resource_iv2.getRelativeUrl(),
                        'individual_aspect/'+resource_iv3.getRelativeUrl()],
                             resource.getVariationCategoryList(
                                         omit_individual_variation=0))

    self.assertSameSet(['required_size/l',
                        'required_size/m',
                        'required_size/s',
                        'option_colour/blue'],
                             resource.getVariationCategoryList(
                                         omit_individual_variation=1))

    # Check default parameters
    self.assertSameSet(['required_size/l',
                        'required_size/m',
                        'required_size/s',
                        'required_size/xl',
                        'required_size/xxl',
                        'option_colour/blue',
                        'option_colour/green',
                        'option_colour/red',
                        'individual_aspect/'+resource_iv1.getRelativeUrl(),
                        'individual_aspect/'+resource_iv2.getRelativeUrl(),
                        'individual_aspect/'+resource_iv3.getRelativeUrl()],
                             resource.getVariationRangeCategoryList())

    self.assertSameSet(['required_size/l',
                        'required_size/m',
                        'required_size/s',
                        'required_size/xl',
                        'required_size/xxl',
                        'option_colour/blue',
                        'option_colour/green',
                        'option_colour/red',
                        'individual_aspect/'+resource_iv1.getRelativeUrl(),
                        'individual_aspect/'+resource_iv2.getRelativeUrl(),
                        'individual_aspect/'+resource_iv3.getRelativeUrl()],
                             resource.getVariationRangeCategoryList(
                                         omit_individual_variation=0))

    self.assertSameSet(['required_size/l',
                        'required_size/m',
                        'required_size/s',
                        'required_size/xl',
                        'required_size/xxl',
                        'option_colour/blue',
                        'option_colour/green',
                        'option_colour/red'],
                            resource.getVariationRangeCategoryList(
                                         omit_individual_variation=1))

class TestResourceVariation(ResourceVariationTestCase):
  """
  Test Resource Variation

  Test basic cases of gathering data to render forms, the purpose of those
  tests is to exercise basic variation results.
  """
  def getTitle(self):
    return "Resource Variations"

  def testResourceDefaultConfig(self):
    """
    Check variation API when creating a default resource.
    This should use what is defined in preferences.
    """
    self.logMessage('testResourceDefaultConfig')
    # Create Product
    product = self._makeOneResource(
              id='1',
              portal_type='Product',
              title='Product One',
              validation_state='validated',
              variation_base_category='required_size',
              optional_variation_base_category='option_colour',
              individual_variation_base_category='individual_aspect')
    self._testResourceDefaultConfig(product)
    # Create Service
    service = self._makeOneResource(
              id='1',
              portal_type='Service',
              title='Service One',
              validation_state='validated',
              variation_base_category='required_size',
              optional_variation_base_category='option_colour',
              individual_variation_base_category='individual_aspect')
    self._testResourceDefaultConfig(service)
    # Create Component
    component = self._makeOneResource(
              id='1',
              portal_type='Component',
              title='Component One',
              validation_state='validated',
              variation_base_category='required_size',
              optional_variation_base_category='option_colour',
              individual_variation_base_category='individual_aspect')
    self._testResourceDefaultConfig(component)

  def testResourceWithoutVariation(self):
    """
    Check variation API when creating a resource and removing its variation
    axes
    """
    self.logMessage('testResourceWithoutVariation')
    # Create Product
    product = self._makeOneResource(
              id='2',
              portal_type='Product',
              title='Product Two',
              validation_state='validated',
              variation_base_category='required_size',
              optional_variation_base_category='option_colour',
              individual_variation_base_category='individual_aspect')
    self._testResourceWithoutVariation(product)
    # Create Service
    service = self._makeOneResource(
              id='2',
              portal_type='Service',
              title='Service Two',
              validation_state='validated',
              variation_base_category='required_size',
              optional_variation_base_category='option_colour',
              individual_variation_base_category='individual_aspect')
    self._testResourceWithoutVariation(service)
    # Create Component
    component = self._makeOneResource(
              id='2',
              portal_type='Component',
              title='Component Two',
              validation_state='validated',
              variation_base_category='required_size',
              optional_variation_base_category='option_colour',
              individual_variation_base_category='individual_aspect')
    self._testResourceWithoutVariation(component)

  def testResourceCategoryVariation(self):
    """
    Check variation API when defining only category as variation
    axes
    """
    self.logMessage('testResourceCategoryVariation')
    # Create Product
    product = self._makeOneResource(
              id='3',
              portal_type='Product',
              title='Product Three',
              validation_state='validated',
              variation_base_category='required_size',
              optional_variation_base_category='option_colour',
              individual_variation_base_category='individual_aspect')
    self._testResourceCategoryVariation(product)
    # Create Service
    service = self._makeOneResource(
              id='3',
              portal_type='Service',
              title='Service Three',
              validation_state='validated',
              variation_base_category='required_size',
              optional_variation_base_category='option_colour',
              individual_variation_base_category='individual_aspect')
    self._testResourceCategoryVariation(service)
    # Create Component
    component = self._makeOneResource(
              id='3',
              portal_type='Component',
              title='Component Three',
              validation_state='validated',
              variation_base_category='required_size',
              optional_variation_base_category='option_colour',
              individual_variation_base_category='individual_aspect')
    self._testResourceCategoryVariation(component)

  def testResourceIndividualVariation(self):
    """
    Check variation API when defining individual variation
    """
    self.logMessage('testResourceIndividualVariation')
    # Create Product
    product = self._makeOneResource(
              id='4',
              portal_type='Product',
              title='Product Four',
              validation_state='validated',
              variation_base_category='required_size',
              optional_variation_base_category='option_colour',
              individual_variation_base_category='individual_aspect')
    self._testResourceIndividualVariation(product)
    # Create Service
    service = self._makeOneResource(
              id='4',
              portal_type='Service',
              title='Service Four',
              validation_state='validated',
              variation_base_category='required_size',
              optional_variation_base_category='option_colour',
              individual_variation_base_category='individual_aspect')
    self._testResourceIndividualVariation(service)
    # Create Component
    component = self._makeOneResource(
              id='4',
              portal_type='Component',
              title='Component Four',
              validation_state='validated',
              variation_base_category='required_size',
              optional_variation_base_category='option_colour',
              individual_variation_base_category='individual_aspect')
    self._testResourceIndividualVariation(component)

  def testResourceVariation(self):
    """
    Combine individual and category variations
    """
    # Resource Variation test.
    self.logMessage('testResourceVariation')
    # Create Product
    product = self._makeOneResource(
              id='5',
              portal_type='Product',
              title='Product Five',
              validation_state='validated',
              variation_base_category='required_size',
              optional_variation_base_category='option_colour',
              individual_variation_base_category='individual_aspect')
    self._testResourceVariation(product)
    # Create Service
    service = self._makeOneResource(
              id='5',
              portal_type='Service',
              title='Service Five',
              validation_state='validated',
              variation_base_category='required_size',
              optional_variation_base_category='option_colour',
              individual_variation_base_category='individual_aspect')
    self._testResourceVariation(service)
    # Create Component
    component = self._makeOneResource(
              id='5',
              portal_type='Component',
              title='Component Five',
              validation_state='validated',
              variation_base_category='required_size',
              optional_variation_base_category='option_colour',
              individual_variation_base_category='individual_aspect')
    self._testResourceVariation(component)
              
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestResourceVariation))
  return suite

