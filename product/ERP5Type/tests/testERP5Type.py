#
# Skeleton ZopeTestCase
#

from random import randint

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestERP5Type(ERP5TypeTestCase):

    # Some helper methods

    #def afterSetUp(self):

    def getBusinessTemplateList(self):
      """
        Return the list of business templates.
      """
      return ('erp5_common', )

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

    def testTemplateToolHasGetId(self):
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
      from Products.ERP5.Document import addBusinessTemplate
      portal_templates = self.getTemplateTool()
      new_id =  portal_templates.generateNewId()
      #bt = self.getTemplateTool().newContent(portal_type="Business Template") # Fails Why ?
      addBusinessTemplate(portal_templates, new_id)
      business_template = getattr(portal_templates, new_id)
      self.failUnless(business_template.getPortalType() == 'Business Template')
      # Test simple string accessor
      test_string = self.getRandomString()
      business_template.setTitle(test_string)
      self.failUnless(business_template.getTitle()==test_string)


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestERP5Type))
        return suite