#
# Skeleton ZopeTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from random import randint
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from zLOG import LOG

class TestERP5Type(ERP5TypeTestCase):

    # Some helper methods

    def getTitle(self):
      return "ERP5Type"

    def getBusinessTemplateList(self):
      """
        Return the list of business templates.
      """
      return ()

    def getRandomString(self):
      return str(randint(-10000000,100000000))

    def getTemplateTool(self):
      return getattr(self.getPortal(), 'portal_templates', None)

    def getCategoryTool(self):
      return getattr(self.getPortal(), 'portal_categories', None)

    def getTypeTool(self):
      return getattr(self.getPortal(), 'portal_types', None)

    # Here are the tests
    def testHasTemplateTool(self):
      # Test if portal_templates was created
      self.failUnless(self.getTemplateTool()!=None)

    def testHasCategoryTool(self):
      # Test if portal_categories was created
      self.failUnless(self.getCategoryTool()!=None)

    def testTemplateToolHasGetId(self):
      # Test if portal_templates has getId method (RAD)
      self.failUnless(self.getTemplateTool().getId() == 'portal_templates')

    def testCategoryToolHasGetId(self):
      # Test if portal_categories has getId method (RAD)
      self.failUnless(self.getCategoryTool().getId() == 'portal_categories')

    # erp5_common tests
    def testCommonHasParentBaseCategory(self):
      # Test if erp5_common parent base category was imported successfully
      self.failUnless(getattr(self.getCategoryTool(), 'parent', None) != None)

    def testCommonHasImageType(self):
      # Test if erp5_common parent base category was imported successfully
      self.failUnless(getattr(self.getTypeTool(), 'Image', None) != None)

    # Business Template Tests
    def testBusinessTemplate(self):
      # Create a business template and test if portal_type matches
      # Make a extension tests on basic accessors
      portal_templates = self.getTemplateTool()
      business_template = self.getTemplateTool().newContent(portal_type="Business Template") # Fails Why ?
                                                                               # may be because there is
                                                                               # no "Business Template"
                                                                               # in portal_types, it may
                                                                               # be added to erp5_common
      self.failUnless(business_template.getPortalType() == 'Business Template')
      # Test simple string accessor
      test_string = self.getRandomString()
      business_template.setTitle(test_string)
      self.failUnless(business_template.getTitle()==test_string)
    
    # Test Dynamic Code Generation
    def test_01_AqDynamic(self):
      portal = self.getPortal()
      #module = portal.person
      from Products.ERP5Type.Base import initializeClassDynamicProperties
      from Products.ERP5Type.Base import initializePortalTypeDynamicProperties
      from Products.ERP5Type.Base import Base
      from Products.ERP5Type import Document
      initializeClassDynamicProperties(portal, Base)
      # Base class should now have a state method
      #self.failUnless(hasattr(Base, 'getFirstName'))
    
    def test_02_AqDynamic(self):
      portal = self.getPortal()
      module = portal.person
      person = module.newContent(id='1', portal_type='Person')
      from Products.ERP5Type import Document
      # Person class should have no method getFirstName
      self.failUnless(not hasattr(Document.Person, 'getFirstName'))
      # Calling getFirstName should produce dynamic methods related to the portal_type
      name = person.getFirstName()
      # Person class should have no method getFirstName
      self.failUnless(not hasattr(Document.Person, 'getFirstName'))
      # Person class should now have method getFirstName
      self.failUnless(hasattr(person, 'getFirstName'))


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestERP5Type))
        return suite
