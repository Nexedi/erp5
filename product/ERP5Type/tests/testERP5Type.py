##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import md5
import unittest

from random import randint
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import DummyLocalizer
from zLOG import LOG, INFO
from Products.CMFCore.tests.base.testcase import LogInterceptor
from Products.ERP5Type.Base import _aq_reset
from Products.ERP5Type.tests.utils import installRealClassTool
from Products.ERP5Type.Utils import removeLocalPropertySheet
from AccessControl.SecurityManagement import newSecurityManager

class PropertySheetTestCase(ERP5TypeTestCase):
  """Base test case class for property sheets tests.
  Inherits from this class to get methods to easily add new property sheets,
  constraints and documents in tests.

  TODO : only property sheets are supported at this time.
  """
  def setUp(self):
    """Set up the fixture. """
    ERP5TypeTestCase.setUp(self)
    installRealClassTool(self.getPortal())
    # keep a mapping type info name -> property sheet list, to remove them in
    # tear down.
    self._added_property_sheets = {}

  def tearDown(self):
    """Clean up """
    ttool = self.getTypesTool()
    class_tool = self.getClassTool()
    # remove all property sheet we added to type informations
    for ti_name, psheet_list in self._added_property_sheets.items():
      ti = ttool.getTypeInfo(ti_name)
      ps_list = ti.property_sheet_list
      for psheet in psheet_list:
        if psheet in ps_list:
          ps_list.remove(psheet)
          # physically remove property sheet, otherwise invalid property sheet
          # could break next tests.
          removeLocalPropertySheet(psheet)
      ti.property_sheet_list = ps_list
    _aq_reset()
    ERP5TypeTestCase.tearDown(self)
    
  def _addProperty(self, portal_type_name, property_definition_code):
    """quickly add a property to a type information."""
    m = md5.new()
    m.update(portal_type_name + property_definition_code)
    property_sheet_name = 'TestPS%s' % m.hexdigest()
    property_sheet_code = """
from Products.CMFCore.Expression import Expression
class %(property_sheet_name)s:
  _properties = ( %(property_definition_code)s, )
""" % locals()
    self._addPropertySheet(portal_type_name,
                           property_sheet_code,
                           property_sheet_name)

  def _addPropertySheet(self, portal_type_name, property_sheet_code,
                       property_sheet_name='TestPropertySheet'):
    """Utility method to add a property sheet to a type information.
    You might be interested in the higer level method _addProperty
    This method registers all added property sheets, to be able to remove
    them in tearDown.
    """
    # install the 'real' class tool
    class_tool = self.getClassTool()

    class_tool.newPropertySheet(property_sheet_name)
    # XXX need to commit the transaction at this point, because class tool
    # files are no longer available to the current transaction.
    get_transaction().commit()
    class_tool.editPropertySheet(property_sheet_name, property_sheet_code)
    get_transaction().commit()
    class_tool.importPropertySheet(property_sheet_name)
    
    # We set the property sheet on the portal type
    ti = self.getTypesTool().getTypeInfo(portal_type_name)
    ti.property_sheet_list = list(ti.property_sheet_list) +\
                                [property_sheet_name]
    # remember that we added a property sheet for tear down
    self._added_property_sheets.setdefault(
                portal_type_name, []).append(property_sheet_name)
    # reset aq_dynamic cache
    _aq_reset()

class TestERP5Type(PropertySheetTestCase, LogInterceptor):

    run_all_test = 1
    quiet = 1

    # Some helper methods

    def getTitle(self):
      return "ERP5Type"

    def getBusinessTemplateList(self):
      """
        Return the list of business templates.
      """
      return ('erp5_base',)

    def afterSetUp(self):
      self.login()
      # all those tests does strange things with Person type, so we won't
      # filter content types to add inside Person.
      self.getTypesTool().getTypeInfo('Person').filter_content_types = 0

    def beforeTearDown(self):
      get_transaction().abort()
      for module in [ self.getPersonModule(),
                      self.getOrganisationModule(),
                      self.getCategoryTool().region ]:
        module.manage_delObjects(list(module.objectIds()))

      # set Person.acquire_local_roles back.
      if getattr(self, 'person_acquire_local_roles', None) is not None:
        self.getTypesTool().getTypeInfo('Person').acquire_local_roles = self.person_acquire_local_roles
        self.portal.portal_caches.clearAllCache()

      get_transaction().commit()
      self.tic()

    def loginWithNoRole(self, quiet=0, run=run_all_test):
      uf = self.getPortal().acl_users
      uf._doAddUser('ac', '', [], [])
      user = uf.getUserById('ac').__of__(uf)
      newSecurityManager(None, user)

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
      self.assertNotEquals(self.getTemplateTool(), None)

    def testHasCategoryTool(self):
      # Test if portal_categories was created
      self.assertNotEquals(self.getCategoryTool(), None)

    def testTemplateToolHasGetId(self):
      # Test if portal_templates has getId method (RAD)
      self.assertEquals(self.getTemplateTool().getId(), 'portal_templates')

    def testCategoryToolHasGetId(self):
      # Test if portal_categories has getId method (RAD)
      self.assertEquals(self.getCategoryTool().getId(), 'portal_categories')

    # erp5_common tests
    def testCommonHasParentBaseCategory(self):
      # Test if erp5_common parent base category was imported successfully
      self.assertNotEquals(getattr(self.getCategoryTool(), 'parent', None), None)

    def testCommonHasImageType(self):
      # Test if erp5_common parent base category was imported successfully
      self.assertNotEquals(getattr(self.getTypeTool(), 'Image', None), None)

    # Business Template Tests
    def testBusinessTemplate(self):
      # Create a business template and test if portal_type matches
      # Make a extension tests on basic accessors
      portal_templates = self.getTemplateTool()
      business_template = self.getTemplateTool().newContent(
                            portal_type="Business Template")
      self.assertEquals(business_template.getPortalType(), 'Business Template')
      # Test simple string accessor
      test_string = self.getRandomString()
      business_template.setTitle(test_string)
      self.assertEquals(business_template.getTitle(), test_string)
    
    # Test Dynamic Code Generation
    def test_02_AqDynamic(self, quiet=quiet, run=run_all_test):
      if not run: return
      portal = self.getPortal()
      module = self.getPersonModule()
      person = module.newContent(id='1', portal_type='Person')
      from Products.ERP5Type import Document
      # Person class should have no method getFirstName
      self.assertFalse(hasattr(Document.Person, 'getFirstName'))
      # Calling getFirstName should produce dynamic methods related to the
      # portal_type
      name = person.getFirstName()
      # Person class should have no method getFirstName
      self.assertFalse(hasattr(Document.Person, 'getFirstName'))
      # Person class should now have method getFirstName
      self.assertTrue(hasattr(person, 'getFirstName'))

    def test_03_NewTempObject(self, quiet=quiet, run=run_all_test):
      if not run: return
      portal = self.getPortal()

      from Products.ERP5Type.Document import newTempPerson
      o = newTempPerson(portal, 1.2)
      o.setTitle('toto')
      self.assertEquals(o.getTitle(), 'toto')
      self.assertEquals(str(o.getId()), str(1.2))

      from Products.ERP5Type.Document import newTempOrganisation
      o = newTempOrganisation(portal, -123)
      o.setTitle('toto')
      self.assertEquals(o.getTitle(), 'toto')
      self.assertEquals(str(o.getId()), str(-123))

      # Try to edit with any property and then get it with getProperty
      o = newTempOrganisation(portal,'a') 
      o.edit(tutu='toto')
      self.assertEquals(o.getProperty('tutu'), 'toto')

      # Same thing with an integer
      o = newTempOrganisation(portal,'b') 
      o.edit(tata=123)
      self.assertEquals(o.getProperty('tata'), 123)

      # Make sure this is a Temp Object
      self.assertEquals(o.isTempObject(), 1)

      # Create a subobject and make sure it is a Temp Object
      a = o.newContent(portal_type = 'Telephone')      
      self.assertEquals(a.isTempObject(), 1)

      # Test newContent with the temp_object parameter
      o = portal.person_module.newContent(id=987, portal_type="Person", temp_object=1)
      o.setTitle('bar')
      self.assertEquals(o.getTitle(), 'bar')
      self.assertEquals(str(o.getId()), str(987))
      self.assertEquals(o.isTempObject(), 1)
      a = o.newContent(id=1, portal_type="Telephone", temp_object=1)
      self.assertEquals(str(a.getId()), str(1))
      self.assertEquals(a.isTempObject(), 1)
      b = o.newContent(id=2, portal_type="Telephone")
      self.assertEquals(b.isTempObject(), 1)
      self.assertEquals(b.getId(), str(2))

      # check we can create temp object without specific roles/permissions
      self.logout()
      self.loginWithNoRole()
      o = newTempOrganisation(portal,'b')
      self.assertEquals(o.isTempObject(), 1)
      a = o.newContent(portal_type = 'Telephone')
      self.assertEquals(a.isTempObject(), 1)
      self.logout()
      self.login()

    def test_04_CategoryAccessors(self, quiet=quiet, run=run_all_test):
      """
        This test provides basic testing of category
        accessors using the region base category.

        setRegion (with base = 0 or base =1)
        setRegionValue
        getRegion
        getRegionId
        getRegionTitle
        getRegionRelatedList
        getRegionRelatedValueList
        getRegionRelatedIdList
        getRegionRelatedTitleList

        This tests also makes sure that the related accessors are
        compatible with acquisition of category. Although region
        is not defined on a Person, Person documents are member
        of a region and should thus be accessible from the region
        category through getRegionRelated accessors
      """
      if not run: return
      portal = self.getPortal()
      region_category = self.getPortal().portal_categories.region
      
      category_title = "Solar System"
      category_id = "solar_system"
      category_object = region_category.newContent(
              portal_type = "Category",
              id = category_id,
              title = category_title, )
      category_relative_url = category_object.getRelativeUrl()
 
      person_title = "Toto"
      person_id = "toto"
      person_object = self.getPersonModule().newContent(
              portal_type = "Person",
              id = person_id,
              title = person_title,)
      person_relative_url = person_object.getRelativeUrl()

      def checkRelationSet(self):
        get_transaction().commit()
        person_object.reindexObject()
        category_object.reindexObject()
        self.tic()
        self.assertEquals( person_object.getRegion(), category_id)
        self.assertEquals( person_object.getRegion(base=1), category_relative_url)
        self.assertEquals( person_object.getRegionValue(), category_object)
        self.assertEquals( person_object.getRegionId(), category_id)
        self.assertEquals( person_object.getRegionTitle(), category_title)
        self.assertEquals( category_object.getRegionRelatedValueList(
                            portal_type = "Person"), [person_object] )
        self.assertEquals( category_object.getRegionRelatedTitleList(
                            portal_type = "Person"), [person_title] )
        self.assertEquals( category_object.getRegionRelatedList(
                            portal_type = "Person"), [person_relative_url] )
        self.assertEquals( category_object.getRegionRelatedIdList(
                            portal_type = "Person"), [person_id] )
      def checkRelationUnset(self):
        get_transaction().commit()
        person_object.reindexObject()
        category_object.reindexObject()
        self.tic()
        self.assertEquals( person_object.getRegion(), None)
        self.assertEquals( person_object.getRegionValue(), None)
        self.assertEquals( person_object.getRegionId(), None)
        self.assertEquals( person_object.getRegionTitle(), None)
        self.assertEquals( category_object.getRegionRelatedValueList(
                            portal_type = "Person"), [] )
        self.assertEquals( category_object.getRegionRelatedTitleList(
                            portal_type = "Person"), [] )
        self.assertEquals( category_object.getRegionRelatedList(
                            portal_type = "Person"), [] )
        self.assertEquals( category_object.getRegionRelatedIdList(
                            portal_type = "Person"), [] )

      # Test setRegion in default mode (base = 0)
      person_object.setRegion(category_id)
      checkRelationSet(self)
      person_object.setRegion(None)
      checkRelationUnset(self)
      # Test setRegion in default mode (base = 1)
      person_object.setRegion(category_relative_url, base=1)
      checkRelationSet(self)
      person_object.setRegion(None)
      checkRelationUnset(self)
      # Test setRegion in value mode
      person_object.setRegionValue(category_object)
      checkRelationSet(self)
      person_object.setRegionValue(None)
      checkRelationUnset(self)
      
    def test_05_setProperty(self, quiet=quiet, run=run_all_test):
      """
        In this test we create a subobject (ie. a phone number)
        and show the difference between calling getProperty and
        an accessor.

        Accessors can be acquired thus returning a property value
        defined on a parent object whereas getProperty / setProperty
        always act at the level of the object itself.

        We also do some basic tests on the telephone number parser

        XXX I think this is inconsistent because it prevents from
        using getProperty / setProperty as a generic way to use
        accessors from subobjects.
      """
      if not run: return
      portal = self.getPortal()
      module = self.getOrganisationModule()
      organisation = module.newContent(id='1', portal_type='Organisation')
      organisation.setDefaultTelephoneText('+55(0)66-5555')
      self.assertEquals(organisation.default_telephone.getTelephoneCountry(),'55')
      self.assertEquals(organisation.default_telephone.getTelephoneArea(),'66')
      self.assertEquals(organisation.default_telephone.getTelephoneNumber(),'5555')
      organisation.setCorporateName('Nexedi')
      #self.assertEquals(organisation.default_telephone.getProperty('corporate_name'),'Nexedi') # Who is right ? XXX
      organisation.default_telephone.setProperty('corporate_name','Toto')
      self.assertEquals(organisation.corporate_name,'Nexedi')
      self.assertEquals(organisation.default_telephone.getCorporateName(),'Nexedi')
      self.assertEquals(organisation.default_telephone.corporate_name,'Toto')
      self.assertEquals(organisation.default_telephone.getProperty('corporate_name'),'Toto')

    def test_06_CachingMethod(self, quiet=quiet, run=run_all_test):
      """Tests Caching methods."""
      if not run: return
      cached_var = cached_var_orig = 'cached_var1'

      def _cache():
        return cached_var
      
      from Products.ERP5Type.Cache import CachingMethod, clearCache
      cache = CachingMethod(_cache, id='testing_cache')
      
      self.assertEquals(cache(), cached_var)
      
      # change the variable
      cached_var = 'cached_var (modified)'
      # cache hit -> still the old variable
      self.assertEquals(cache(), cached_var_orig)
        
      clearCache()
      self.assertEquals(cache(), cached_var)

    def test_07_afterCloneScript(self, quiet=quiet, run=run_all_test):
      """manage_afterClone can call a type based script."""
      if not run: return
      # setup the script for Person portal type
      custom_skin = self.getPortal().portal_skins.custom
      method_id = 'Person_afterClone'
      if method_id in custom_skin.objectIds():
        custom_skin.manage_delObjects([method_id])
      
      custom_skin.manage_addProduct['PythonScripts']\
                    .manage_addPythonScript(id = method_id)
      script = custom_skin[method_id]
      script.ZPythonScript_edit('', "context.setTitle('reseted')")
      self.getPortal().changeSkin(None)
    
      # copy / pasted person have their title reseted
      folder = self.getPersonModule()
      pers = folder.newContent(portal_type='Person',
                              title='something', )
      copy_data = folder.manage_copyObjects([pers.getId()])
      new_id = folder.manage_pasteObjects(copy_data)[0]['new_id']
      new_pers = folder[new_id]
      self.assertEquals(new_pers.getTitle(), 'reseted')
      
      # we can even change subobjects in the script
      if not hasattr(pers, 'default_address'):
        pers.newContent(portal_type='Address', id='default_address')
      pers.default_address.setTitle('address_title')
      # modify script to update subobject title
      script.ZPythonScript_edit('',
          "context.default_address.setTitle('address_title_reseted')")
      copy_data = folder.manage_copyObjects([pers.getId()])
      new_id = folder.manage_pasteObjects(copy_data)[0]['new_id']
      new_pers = folder[new_id]
      self.assertEquals(new_pers.default_address.getTitle(),
                        'address_title_reseted')
      
      # of course, other portal types are not affected
      folder = self.getOrganisationModule()
      orga = folder.newContent(portal_type='Organisation',
                              title='something', )
      copy_data = folder.manage_copyObjects([orga.getId()])
      new_id = folder.manage_pasteObjects(copy_data)[0]['new_id']
      new_orga = folder[new_id]
      self.assertEquals(new_orga.getTitle(), 'something')
      
    def test_08_AccessorGeneration(self, quiet=quiet, run=run_all_test):
      """Tests accessor generation doesn't generate error messages.
      """
      if not run: return
      from Products.ERP5Type.Base import _aq_reset
      _aq_reset()
      self._catch_log_errors(ignored_level=INFO)
      folder = self.getOrganisationModule()
      orga = folder.newContent(portal_type='Organisation',)
      # call an accessor, _aq_dynamic will generate accessors
      orga.getId()
      self._ignore_log_errors()
    
    def test_09_RenameObjects(self, quiet=quiet, run=run_all_test):
      """Test object renaming.

         As we overloaded some parts of OFS, it's better to test again some basic
         features.
      """
      if not run: return
      folder = self.getOrganisationModule()
      id_list = [chr(x) for x in range(ord('a'), ord('z')+1)]
      for id_ in id_list:
        folder.newContent(portal_type='Organisation', id=id_)
      # commit a subtransaction, so that we can rename objecs (see
      # OFS.ObjectManager._getCopy)
      get_transaction().commit(1)

      for obj in folder.objectValues():
        new_id = '%s_new' % obj.getId()
        folder.manage_renameObjects([obj.getId()], [new_id])
        self.assertEquals(obj.getId(), new_id)

      for obj_id in folder.objectIds():
        self.assertTrue(obj_id.endswith('_new'),
                        'bad object id: %s' % obj_id)
      for id_ in id_list:
        new_id = '%s_new' % id_
        self.assertEquals(folder._getOb(new_id).getId(), new_id)

    def test_10_ConstraintNotFound(self, quiet=quiet, run=run_all_test):
      """
      When a Constraint is not found while importing a PropertySheet,
      AttributeError was raised, and generated a infinite loop.
      This is a test to make sure this will not happens any more
      """
      if not run: return
      text = """
class TestPropertySheet:
    \"\"\"
        TestPropertySheet for this unit test
    \"\"\"

    _properties = (
        {   'id'          : 'strange_property',
            'description' : 'A local property description',
            'type'        : 'string',
            'mode'        : '' },
      )

    _constraints = (
        { 'id'            : 'toto',
          'description'   : 'define a bad constraint',
          'type'          : 'TestConstraintNotFoundClass',
        },
      )

"""
      self._addPropertySheet('Organisation', text)
      folder = self.getOrganisationModule()
      # We check that we raise exception when we create new object
      from Products.ERP5Type.Utils import ConstraintNotFound
      organisation =  self.assertRaises(ConstraintNotFound, folder.newContent,
                                        portal_type='Organisation')

    def test_11_valueAccessor(self, quiet=quiet, run=run_all_test):
      """
        The purpose of this test is to make sure that category accessors
        work as expected.

        List accessors support ordering and multiple entries
        but they are incompatible with default value

        Set accessors preserve the default value but
        they do not preserver order or multiple entries

        The test is implemented for both Category and Value
        accessors.
      """
      if not run: return

      if not quiet:
        message = 'Test Category setters'
        ZopeTestCase._print('\n '+message)
        LOG('Testing... ', 0, message)

      # Create a few categories
      region_category = self.getPortal().portal_categories.region
      alpha = region_category.newContent(
              portal_type = "Category",
              id =          "alpha",
              title =       "Alpha System", )
      beta = region_category.newContent(
              portal_type = "Category",
              id =          "beta",
              title =       "Beta System", )
      zeta = region_category.newContent(
              portal_type = "Category",
              id =          "zeta",
              title =       "Zeta System", )
      function_category = self.getPortal().portal_categories.function
      nofunction = function_category.newContent(
              portal_type = "Category",
              id =          "nofunction",
              title =       "No Function", )

      self.assertEquals(alpha.getRelativeUrl(), 'region/alpha')

      alpha.reindexObject()
      beta.reindexObject()
      zeta.reindexObject()
      nofunction.reindexObject()
      get_transaction().commit()
      self.tic() # Make sure categories are reindexed

      # Create a new person
      module = self.getPersonModule()
      person = module.newContent(portal_type='Person')

      # Value setters (list, set, default)
      person.setFunction('nofunction')  # Fill at least one other category
      person.setDefaultRegionValue(alpha)
      self.assertEquals(person.getDefaultRegion(), 'alpha')
      self.assertEquals(person.getRegion(), 'alpha')
      person.setRegionValue(alpha)
      self.assertEquals(person.getRegion(), 'alpha')
      person.setRegionValueList([alpha, alpha])
      self.assertEquals(person.getRegionList(), ['alpha', 'alpha'])
      person.setRegionValueSet([alpha, alpha])
      self.assertEquals(person.getRegionSet(), ['alpha'])
      person.setRegionValueList([alpha, beta, alpha])
      self.assertEquals(person.getRegionList(), ['alpha', 'beta', 'alpha'])
      person.setRegionValueSet([alpha, beta, alpha])
      result = person.getRegionSet()
      result.sort()
      self.assertEquals(result, ['alpha', 'beta'])
      person.setDefaultRegionValue(beta)
      self.assertEquals(person.getDefaultRegion(), 'beta')
      result = person.getRegionSet()
      result.sort()
      self.assertEquals(result, ['alpha', 'beta'])
      self.assertEquals(person.getRegionList(), ['beta', 'alpha'])
      person.setDefaultRegionValue(alpha)
      self.assertEquals(person.getDefaultRegion(), 'alpha')
      result = person.getRegionSet()
      result.sort()
      self.assertEquals(result, ['alpha', 'beta'])
      self.assertEquals(person.getRegionList(), ['alpha', 'beta'])
      # Test accessor on documents rather than on categories
      person.setDefaultRegionValue(person)
      self.assertEquals(person.getDefaultRegion(), person.getRelativeUrl())
      self.assertEquals(person.getRegionList(), [person.getRelativeUrl(), 'alpha', 'beta'])
      person.setRegionValue([person, alpha, beta])
      self.assertEquals(person.getRegionList(), [person.getRelativeUrl(), 'alpha', 'beta'])

      # Category setters (list, set, default)
      person = module.newContent(portal_type='Person')
      person.setFunction('nofunction')  # Fill at least one other category
      person.setDefaultRegion('alpha')
      self.assertEquals(person.getRegion(), 'alpha')
      self.assertEquals(person.getDefaultRegion(), 'alpha')
      person.setRegion('alpha')
      self.assertEquals(person.getRegion(), 'alpha')
      person.setRegionList(['alpha', 'alpha'])
      self.assertEquals(person.getRegionList(), ['alpha', 'alpha'])
      person.setRegionSet(['alpha', 'alpha'])
      self.assertEquals(person.getRegionSet(), ['alpha'])
      person.setRegionList(['alpha', 'beta', 'alpha'])
      self.assertEquals(person.getRegionList(), ['alpha', 'beta', 'alpha'])
      person.setRegionSet(['alpha', 'beta', 'alpha'])
      result = person.getRegionSet()
      result.sort()
      self.assertEquals(result, ['alpha', 'beta'])
      person.setDefaultRegion('beta')
      self.assertEquals(person.getDefaultRegion(), 'beta')
      result = person.getRegionSet()
      result.sort()
      self.assertEquals(result, ['alpha', 'beta'])
      self.assertEquals(person.getRegionList(), ['beta', 'alpha'])
      person.setDefaultRegion('alpha')
      self.assertEquals(person.getDefaultRegion(), 'alpha')
      result = person.getRegionSet()
      result.sort()
      self.assertEquals(result, ['alpha', 'beta'])
      self.assertEquals(person.getRegionList(), ['alpha', 'beta'])
      # Test accessor on documents rather than on categories
      person.setDefaultRegion(person.getRelativeUrl())
      self.assertEquals(person.getDefaultRegion(), person.getRelativeUrl())
      self.assertEquals(person.getRegionList(), [person.getRelativeUrl(), 'alpha', 'beta'])
      person.setRegion([person.getRelativeUrl(), 'alpha', 'beta'])
      self.assertEquals(person.getRegionList(), [person.getRelativeUrl(), 'alpha', 'beta'])

      # Uid setters (list, set, default)
      person = module.newContent(portal_type='Person')
      person.reindexObject()
      get_transaction().commit()
      self.tic() # Make sure person is reindexed
      person.setFunction('nofunction')  # Fill at least one other category
      person.setDefaultRegionUid(alpha.getUid())
      self.assertEquals(person.getRegion(), 'alpha')
      self.assertEquals(person.getDefaultRegion(), 'alpha')
      person.setRegionUid(alpha.getUid())
      self.assertEquals(person.getRegion(), 'alpha')
      person.setRegionUidList([alpha.getUid(), alpha.getUid()])
      self.assertEquals(person.getRegionList(), ['alpha', 'alpha'])
      person.setRegionUidSet([alpha.getUid(), alpha.getUid()])
      self.assertEquals(person.getRegionSet(), ['alpha'])
      person.setRegionUidList([alpha.getUid(), beta.getUid(), alpha.getUid()])
      self.assertEquals(person.getRegionList(), ['alpha', 'beta', 'alpha'])
      person.setRegionUidSet([alpha.getUid(), beta.getUid(), alpha.getUid()])
      result = person.getRegionSet()
      result.sort()
      self.assertEquals(result, ['alpha', 'beta'])
      person.setDefaultRegionUid(beta.getUid())
      self.assertEquals(person.getDefaultRegion(), 'beta')
      result = person.getRegionSet()
      result.sort()
      self.assertEquals(result, ['alpha', 'beta'])
      self.assertEquals(person.getRegionList(), ['beta', 'alpha'])
      person.setDefaultRegionUid(alpha.getUid())
      self.assertEquals(person.getDefaultRegion(), 'alpha')
      result = person.getRegionSet()
      result.sort()
      self.assertEquals(result, ['alpha', 'beta'])
      self.assertEquals(person.getRegionList(), ['alpha', 'beta'])
      # Test accessor on documents rather than on categories
      person.setDefaultRegionUid(person.getUid())
      self.assertEquals(person.getDefaultRegion(), person.getRelativeUrl())
      self.assertEquals(person.getRegionList(), [person.getRelativeUrl(), 'alpha', 'beta'])
      person.setRegionUid([person.getUid(), alpha.getUid(), beta.getUid()])
      self.assertEquals(person.getRegionList(), [person.getRelativeUrl(), 'alpha', 'beta'])

    def test_12_listAccessor(self, quiet=quiet, run=run_all_test):
      """
      The purpose of this test is to make sure that accessor for
      sequence types support the same kind of semantics as the
      one on categories. We use 'subject' of the DublinCore propertysheet
      on organisation documents for this test.
      """
      if not run: return

      if not quiet:
        message = 'Test Category setters'
        ZopeTestCase._print('\n '+message)
        LOG('Testing... ', 0, message)

      # Create a new person
      module = self.getPersonModule()
      person = module.newContent(portal_type='Person')

      # Do the same tests as in test_11_valueAccessor 
      person.setSubject('alpha')
      self.assertEquals(person.getSubject(), 'alpha')
      person.setSubjectList(['alpha', 'alpha'])
      self.assertEquals(person.getSubjectList(), ['alpha', 'alpha'])
      person.setSubjectSet(['alpha', 'alpha'])
      self.assertEquals(person.getSubjectSet(), ['alpha'])
      person.setSubjectList(['alpha', 'beta', 'alpha'])
      self.assertEquals(person.getSubjectList(), ['alpha', 'beta', 'alpha'])
      person.setSubjectSet(['alpha', 'beta', 'alpha'])
      result = person.getSubjectSet()
      result.sort()
      self.assertEquals(result, ['alpha', 'beta'])
      person.setDefaultSubject('beta')
      self.assertEquals(person.getDefaultSubject(), 'beta')
      result = person.getSubjectSet()
      result.sort()
      self.assertEquals(result, ['alpha', 'beta'])
      self.assertEquals(person.getSubjectList(), ['beta', 'alpha'])
      person.setDefaultSubject('alpha')
      self.assertEquals(person.getDefaultSubject(), 'alpha')
      result = person.getSubjectSet()
      result.sort()
      self.assertEquals(result, ['alpha', 'beta'])
      self.assertEquals(person.getSubjectList(), ['alpha', 'beta'])

    def test_13_acquiredAccessor(self, quiet=quiet, run=run_all_test):
      """
      The purpose of this test is to make sure that accessor for
      sequence types support the same kind of semantics as the
      one on categories. We use 'subject' of the DublinCore propertysheet
      on organisation documents for this test.
      """

      # If address is updated on subordination, then
      # address is updated on person

      # If address is changed on person, it rem

      # If address not available on one organisation
      # it is found on the mapping related organisation
      # which is one step higher in the site 
      pass

    def test_15_DefaultValue(self):
      """
      Tests that the default value is returned correctly
      """
      portal = self.getPortal()
      module = self.getPersonModule()
      person = module.newContent(id='1', portal_type='Person')
      
      def getFirstName(default=None):
        "dummy method to check default is passed correctly"
        return default

      person.getFirstName = getFirstName

      # test static method
      self.assertEquals(person.getFirstName(), None)
      self.assertEquals(person.getFirstName('foo'), 'foo')
      self.assertEquals(person.getFirstName(default='foo'), 'foo')
      # test dynamic method
      self.assertEquals(person.getLastName(), None)
      self.assertEquals(person.getLastName('foo'), 'foo')
      #self.assertEquals(person.getLastName(default='foo'), 'foo')
      # test static method through getProperty
      self.assertEquals(person.getProperty('first_name'), None)
      self.assertEquals(person.getProperty('first_name', 'foo'), 'foo')
      self.assertEquals(person.getProperty('first_name', d='foo'), 'foo')
      # test dynamic method through getProperty
      self.assertEquals(person.getProperty('last_name'), None)
      self.assertEquals(person.getProperty('last_name', 'foo'), 'foo')
      self.assertEquals(person.getProperty('last_name', d='foo'), 'foo')
      # test simple property through getProperty
      property_name = 'XXXthis_property_does_not_exist123123'
      self.assertEquals(person.getProperty(property_name), None)
      self.assertEquals(person.getProperty(property_name, 'foo'), 'foo')
      self.assertEquals(person.getProperty(property_name, d='foo'), 'foo')

    def test_15b_DefaultValueDefinedOnPropertySheet(self, quiet=quiet, 
                                                    run=run_all_test):
      """Tests that the default value is returned correctly when a default
      value is defined using the property sheet.
      """
      if not run: return
      self._addProperty('Person', '''{'id': 'dummy_ps_prop',
                                      'type': 'string',
                                      'mode': 'w',
                                      'default': 'ps_default',}''')
      module = self.getPersonModule()
      person = module.newContent(id='1', portal_type='Person')
      # The default ps value will be returned, when using generated accessor
      self.assertEquals('ps_default', person.getDummyPsProp())
      # (unless you explicitly pass a default value.
      self.assertEquals('default', person.getDummyPsProp('default'))
      # using getProperty
      self.assertEquals('ps_default', person.getProperty('dummy_ps_prop'))
      self.assertEquals('default', person.getProperty('dummy_ps_prop', 'default'))

      # None can be a default value too
      self.assertEquals(None, person.getProperty('dummy_ps_prop', None))
      self.assertEquals(None, person.getDummyPsProp(None))
      
      # once the value has been set, there's no default
      value = 'a value'
      person.setDummyPsProp(value)
      self.assertEquals(value, person.getDummyPsProp())
      self.assertEquals(value, person.getDummyPsProp('default'))
      self.assertEquals(value, person.getProperty('dummy_ps_prop'))
      self.assertEquals(value, person.getProperty('dummy_ps_prop', d='default'))


    def test_15b_ListAccessorsDefaultValueDefinedOnPropertySheet(self):
      """Tests that the default value is returned correctly when a default
      value is defined using the property sheet, on list accesors.
      """
      self._addProperty('Person', '''{'id': 'dummy_ps_prop',
                                      'type': 'lines',
                                      'mode': 'w',
                                      'default': [1, 2, 3],}''')
      module = self.getPersonModule()
      person = module.newContent(id='1', portal_type='Person')
      # default accessor and list accessors are generated
      self.assertTrue(hasattr(person, 'getDummyPsProp'))
      self.assertTrue(hasattr(person, 'getDummyPsPropList'))

      # The default ps value will be returned, when using generated accessor
      self.assertEquals([1, 2, 3], person.getDummyPsPropList())
      # (unless you explicitly pass a default value.
      self.assertEquals(['default'], person.getDummyPsPropList(['default']))
      # using getProperty
      self.assertEquals([1, 2, 3], person.getProperty('dummy_ps_prop_list'))
      self.assertEquals(['default'],
                        person.getProperty('dummy_ps_prop_list', ['default']))

      # once the value has been set, there's no default
      value_list = ['some', 'values']
      person.setDummyPsPropList(value_list)
      self.assertEquals(value_list, person.getDummyPsPropList())
      self.assertEquals(value_list, person.getDummyPsPropList(['default']))
      self.assertEquals(value_list, person.getProperty('dummy_ps_prop_list'))
      self.assertEquals(value_list,
              person.getProperty('dummy_ps_prop_list', d=['default']))


    def test_15c_getDescriptionDefaultValue(self):
      """
      Tests that the default value of getDescription is returned correctly
      """
      person = self.getPersonModule().newContent(portal_type='Person')

      # test default value of getDescription accessor
      # as defined in the DublinCore PropertySheet
      self.assertEquals('', person.getDescription())
      self.assertEquals('foo',
                        person.getDescription('foo'))

    def test_16_SimpleStringAccessor(self,quiet=quiet, run=run_all_test):
      """Tests a simple string accessor.
      This is also a way to test _addProperty method """
      if not run: return
      self._addProperty('Person', '''{'id': 'dummy_ps_prop',
                                      'type': 'string',
                                      'mode': 'w',}''')
      person = self.getPersonModule().newContent(id='1', portal_type='Person')
      self.assertEquals('string', person.getPropertyType('dummy_ps_prop'))
      self.assertTrue(hasattr(person, 'getDummyPsProp'))
      self.assertTrue(hasattr(person, 'setDummyPsProp'))
      person.setDummyPsProp('a value')
      self.assertTrue(person.hasProperty('dummy_ps_prop'))
      self.assertEquals('a value', person.getDummyPsProp())

    def test_17_WorkflowStateAccessor(self,quiet=quiet, run=run_all_test):
      """Tests for workflow state. assumes that validation state is chained to
      the Person portal type and that this workflow has 'validation_state' as
      state_variable.
      """
      if not run: return
      person = self.getPersonModule().newContent(id='1', portal_type='Person')
      wf = self.getWorkflowTool().validation_workflow
      # those are assumptions for this test.
      self.assertTrue(wf.getId() in
                        self.getWorkflowTool().getChainFor('Person'))
      self.assertEquals('validation_state', wf.variables.getStateVar())
      initial_state = wf.states[wf.initial_state]
      other_state = wf.states['validated']

      self.assertTrue(hasattr(person, 'getValidationState'))
      self.assertTrue(hasattr(person, 'getValidationStateTitle'))
      self.assertTrue(hasattr(person, 'getTranslatedValidationStateTitle'))

      self.assertEquals(initial_state.getId(), person.getValidationState())
      self.assertEquals(initial_state.title,
                        person.getValidationStateTitle())
      # XXX we do not have translation system set up at that point
      self.assertEquals(initial_state.title,
                        person.getTranslatedValidationStateTitle())
      
      self.assertEquals(initial_state.getId(),
                        person.getProperty('validation_state'))
      self.assertEquals(initial_state.title,
                        person.getProperty('validation_state_title'))
      # XXX we do not have translation system set up at that point
      self.assertEquals(initial_state.title,
                        person.getProperty('translated_validation_state_title'))
      
      # default parameter is accepted by getProperty for compatibility
      self.assertEquals(initial_state.getId(),
                        person.getProperty('validation_state', 'default'))
      self.assertEquals(initial_state.title,
                        person.getProperty('validation_state_title', 'default'))
      # XXX we do not have translation system set up at that point
      self.assertEquals(initial_state.title,
                        person.getProperty('translated_validation_state_title',
                        'default'))

      # pass a transition and check accessors again.
      person.validate()
      self.assertEquals(other_state.getId(), person.getValidationState())
      self.assertEquals(other_state.title,
                        person.getValidationStateTitle())
      self.assertEquals(other_state.title,
                        person.getTranslatedValidationStateTitle())
      self.assertEquals(other_state.getId(),
                        person.getProperty('validation_state'))
      self.assertEquals(other_state.title,
                        person.getProperty('validation_state_title'))
      self.assertEquals(other_state.title,
                        person.getProperty('translated_validation_state_title'))
    
    DEFAULT_ORGANISATION_TITLE_PROP = '''
                      { 'id':         'organisation',
                        'storage_id': 'default_organisation',
                        'type':       'content',
                        'portal_type': ('Organisation', ),
                        'acquired_property_id': ('title', ),
                        'mode':       'w', }'''

    def test_18_SimpleContentAccessor(self,quiet=quiet, run=run_all_test):
      """Tests a simple content accessor.
      """
      if not run: return
      # For testing purposes, we add a default_organisation inside a person, 
      # and we add code to generate a 'default_organisation_title' property on
      # this person that will returns the organisation title.
      self._addProperty('Person', self.DEFAULT_ORGANISATION_TITLE_PROP)
      person = self.getPersonModule().newContent(id='1', portal_type='Person')
      self.assertTrue(hasattr(person, 'getDefaultOrganisationTitle'))
      self.assertTrue(hasattr(person, 'setDefaultOrganisationTitle'))
      person.setDefaultOrganisationTitle('The organisation title')
      # XXX content generated properties are not in propertyMap. is it a bug ?
      #self.assertTrue(person.hasProperty('default_organisation_title'))
      
      # an organisation is created inside the person.
      default_organisation = person._getOb('default_organisation', None)
      self.assertNotEquals(None, default_organisation)
      self.assertEquals('Organisation',
                        default_organisation.getPortalTypeName())
      self.assertEquals('The organisation title',
                        default_organisation.getTitle())
    
    def test_18b_ContentAccessorWithIdClash(self):
      """Tests a content setters do not set the property on acquired object
      that may have the same id, using same scenario as test_18
      Note that we only test Setter for now.
      """
      self._addProperty('Person', self.DEFAULT_ORGANISATION_TITLE_PROP)
      person = self.getPersonModule().newContent(id='1', portal_type='Person')
      another_person = self.getPersonModule().newContent(
                                        id='default_organisation',
                                        portal_type='Person')
      another_person_title = 'This is the other person'
      another_person.setTitle(another_person_title)
      person.setDefaultOrganisationTitle('The organisation title')
      # here we want to make sure we didn't modify this 'default_organisation'
      # we could have get by acquisition.
      self.assertNotEquals(another_person_title,
                           person.getDefaultOrganisationTitle())
      # an organisation is created inside the person.
      default_organisation = person._getOb('default_organisation', None)
      self.assertNotEquals(None, default_organisation)
      self.assertEquals('The organisation title',
                        person.getDefaultOrganisationTitle())
    
    DEFAULT_ORGANISATION_TITLE_ACQUIRED_PROP = '''
          { 'id':         'organisation',
            'storage_id': 'default_organisation',
            'type':       'content',
            'portal_type': ('Organisation', ),
            'acquired_property_id': ('title', ),
            'acquisition_base_category': ( 'destination', ),
            'acquisition_portal_type'  : ( 'Person', ),
            'acquisition_accessor_id'  : 'getDefaultOrganisationValue',
            'acquisition_copy_value'   : 0,
            'acquisition_mask_value'   : 1,
            'acquisition_sync_value'   : 0,
            'acquisition_depends'      : None,
            'mode':       'w', }'''
    
    def test_19_AcquiredContentAccessor(self,quiet=quiet, run=run_all_test):
      """Tests an acquired content accessor.
      """
      if not run: return
      # For testing purposes, we add a default_organisation inside a person, 
      # and we add code to generate a 'default_organisation_title' property on
      # this person that will returns the organisation title. If this is not
      # defined, then we will acquire the default organisation title of the
      # `destination` person. This is a stupid example, but it works with
      # objects we have in our testing environnement
      self._addProperty('Person', self.DEFAULT_ORGANISATION_TITLE_ACQUIRED_PROP)
      # add destination base category to Person TI
      person_ti = self.getTypesTool().getTypeInfo('Person')
      if 'destination' not in person_ti.base_category_list:
          person_ti.base_category_list = tuple(list(
                self.getTypesTool().getTypeInfo('Person').base_category_list) +
                ['destination', ])
      person = self.getPersonModule().newContent(id='1', portal_type='Person')
      other_pers = self.getPersonModule().newContent(id='2', portal_type='Person')
      other_pers_title = 'This is the title we should acquire'
      other_pers.setDefaultOrganisationTitle(other_pers_title)
      person.setDestinationValue(other_pers)
      
      # title is acquired from the other person
      self.assertEquals(other_pers_title,
                        person.getDefaultOrganisationTitle())
      
      # now if we save, it should create a default_organisation inside this
      # person, but do not modify the other_pers.
      person.setDefaultOrganisationTitle('Our organisation title')
      self.assertEquals('Our organisation title',
                        person.getDefaultOrganisationTitle())
      self.assertEquals(other_pers_title,
                        other_pers.getDefaultOrganisationTitle())
      
    def test_19b_AcquiredContentAccessorWithIdClash(self,quiet=quiet, run=run_all_test):
      """Tests a content setters do not set the property on acquired object
      that may have the same id, using same scenario as test_19
      Note that we only test Setter for now.
      """
      if not run: return
      self._addProperty('Person', self.DEFAULT_ORGANISATION_TITLE_ACQUIRED_PROP)
      # add destination base category to Person TI
      person_ti = self.getTypesTool().getTypeInfo('Person')
      if 'destination' not in person_ti.base_category_list:
          person_ti.base_category_list = tuple(list(
                self.getTypesTool().getTypeInfo('Person').base_category_list) +
                ['destination', ])
      
      person = self.getPersonModule().newContent(id='1', portal_type='Person')
      another_person = self.getPersonModule().newContent(
                                        id='default_organisation',
                                        portal_type='Person')
      another_person_title = 'This is the other person'
      another_person.setTitle(another_person_title)
      person.setDefaultOrganisationTitle('The organisation title')
      # here we want to make sure we didn't modify this 'default_organisation'
      # we could have get by acquisition.
      self.assertNotEquals(another_person_title,
                           person.getDefaultOrganisationTitle())
      # an organisation is created inside the person.
      default_organisation = person._getOb('default_organisation', None)
      self.assertNotEquals(None, default_organisation)
      self.assertEquals('The organisation title',
                        person.getDefaultOrganisationTitle())
    
    def test_20_AsContext(self,quiet=quiet, run=run_all_test):
      """asContext method return a temporary copy of an object.
      Any modification made to the copy does not change the original object.
      """
      if not run: return
      obj = self.getPersonModule().newContent(portal_type='Person')
      obj.setTitle('obj title')
      copy = obj.asContext()
      copy.setTitle('copy title')
      self.assertEquals('obj title', obj.getTitle())
      self.assertEquals('copy title', copy.getTitle())

      # asContext method accepts parameters, and edit the copy with those
      # parameters
      obj = self.getPersonModule().newContent(portal_type='Person', id='obj')
      obj.setTitle('obj title')
      copy = obj.asContext(title='copy title')
      self.assertEquals('obj title', obj.getTitle())
      self.assertEquals('copy title', copy.getTitle())
    
      # acquisition context is the same
      self.assertEquals(self.getPersonModule(), obj.getParentValue())
      self.assertEquals(self.getPersonModule(), copy.getParentValue())

      # Test category accessor
      gender = self.getCategoryTool().gender.newContent(
                            portal_type='Category', id='male')
      # Category can not be used as asContext parameter
#       new_copy = obj.asContext(gender=gender.getCategoryRelativeUrl())
#       self.assertEquals(gender.getCategoryRelativeUrl(), new_copy.getGender())
      new_copy = obj.asContext()
      new_copy.edit(gender=gender.getCategoryRelativeUrl())
      get_transaction().commit()
      self.tic()
      self.assertEquals(gender.getCategoryRelativeUrl(), new_copy.getGender())
      self.assertEquals(None, obj.getGender())

    def test_21_ActionCondition(self, quiet=quiet, run=run_all_test):
      """Tests action conditions
      """
      if not run: return
      type_tool = self.getTypeTool()
      portal_type_object = type_tool['Organisation']
      def addCustomAction(name,condition):
        portal_type_object.addAction(
          id = name
          , name = 'Become Geek'
          , action = 'become_geek_action'
          , condition = condition
          , permission = ('View', )
          , category = 'object_action'
          , visible = 1
          , priority = 2.0 )
      addCustomAction('action1','python: object.getDescription()=="foo"')
      obj = self.getOrganisationModule().newContent(portal_type='Organisation')
      action_tool = self.getPortal().portal_actions
      actions = action_tool.listFilteredActionsFor(obj)
      action_id_list = [x['id'] for x in actions.get('object_action',[])]
      self.assertTrue('action1' not in action_id_list)
      obj.setDescription('foo')
      actions = action_tool.listFilteredActionsFor(obj)
      action_id_list = [x['id'] for x in actions.get('object_action',[])]
      self.assertTrue('action1' in action_id_list)
      addCustomAction('action2',"python: portal_url not in (None,'')")
      actions = action_tool.listFilteredActionsFor(obj)
      action_id_list = [x['id'] for x in actions.get('object_action',[])]
      self.assertTrue('action2' in action_id_list)
      addCustomAction('action3',"python: object_url not in (None,'')")
      actions = action_tool.listFilteredActionsFor(obj)
      action_id_list = [x['id'] for x in actions.get('object_action',[])]
      self.assertTrue('action3' in action_id_list)

    def test_22_securityReindex(self, quiet=quiet, run=run_all_test):
      """
      Tests that the security is reindexed when a role is changed on an object.
      
      Note: Turn on Person.acquire_local_roles to 0 in afterSetUp.
      """
      if not run: return

      from AccessControl import getSecurityManager
      portal = self.getPortal()

      # turn on Person.acquire_local_roles
      person = self.getTypesTool().getTypeInfo('Person')
      self.person_acquire_local_roles = person.acquire_local_roles
      person.acquire_local_roles = True
      portal.portal_caches.clearAllCache()

      # Make a plain user.
      uf = portal.acl_users
      uf._doAddUser('yo', '', [], [])
      user = uf.getUserById('yo').__of__(uf)

      person_module = self.getPersonModule()
      person = person_module.newContent(portal_type='Person', title='foo')
      person.manage_permission('View', roles=['Auditor'], acquire=0)

      # The user may not view the person object.
      get_transaction().commit() ; self.tic()
      self.assertTrue('Auditor' not in user.getRolesInContext(person))
      self.logout()
      newSecurityManager(None, user)
      self.assertEquals(len(person_module.searchFolder(id=person.getId())), 0)
      self.logout()
      self.login()

      # Now allow him to view it.
      person_module.manage_addLocalRoles(user.getId(), ['Auditor'])

      # This might look odd (indeed it is), but the catalog should not
      # reflect the security change, until the affected objects are
      # reindexed, and Jean-Paul believes that this should not be
      # automatic.
      get_transaction().commit() ; self.tic()
      self.assertTrue('Auditor' in user.getRolesInContext(person))
      self.logout()
      newSecurityManager(None, user)
      self.assertEquals(len(person_module.searchFolder(id=person.getId())), 0)
      self.logout()
      self.login()

      # Now invoke the reindexing explicitly, so the catalog should be
      # synchronized.
      person_module.recursiveReindexObject()
      get_transaction().commit() ; self.tic()
      self.assertTrue('Auditor' in user.getRolesInContext(person))
      self.logout()
      newSecurityManager(None, user)
      self.assertEquals(len(person_module.searchFolder(id=person.getId())), 1)
      self.logout()
      self.login()

    def test_23_titleIsNotDefinedByDefault(self, quiet=quiet, run=run_all_test):
      """
      Tests that no title attribute is set on new content
      """
      if not run: return
      portal = self.getPortal()
      person_module = self.getPersonModule()
      person = person_module.newContent(portal_type='Person')
      self.assertFalse(person.hasTitle())
      self.assertFalse(person.__dict__.has_key('title'))

    def test_24_relatedValueAccessor(self, quiet=quiet, run=run_all_test):
      """
      The purpose of this test is to make sure that category related 
      accessors work as expected.

      The test is implemented for both Category and Value
      accessors.

      Test that checked_permission is well configured for View permission
      """
      if not run: return

      if not quiet:
        message = 'Test Related Value Accessors'
        ZopeTestCase._print('\n '+message)
        LOG('Testing... ', 0, message)

      # Create a few categories
      region_category = self.getPortal().portal_categories.region
      alpha = region_category.newContent(
              portal_type = "Category",
              id =          "alpha",
              title =       "Alpha System", )
      alpha_path = alpha.getRelativeUrl()

      self.assertEquals(alpha.getRelativeUrl(), 'region/alpha')

      # Create a new person
      module = self.getPersonModule()
      doo = module.newContent(portal_type='Person', title='Doo')
      bar = module.newContent(portal_type='Person', title='Bar')
      foo = module.newContent(portal_type='Person', title='Foo')

      doo.setDefaultRegionValue(alpha)
      doo_path = doo.getRelativeUrl()
      bar.setDefaultRegionValue(alpha)
      bar_path = bar.getRelativeUrl()
      foo.setDefaultRegionValue(alpha)
      foo.manage_permission('View', roles=[], acquire=0)
      foo_path = foo.getRelativeUrl()

      # Make sure categories are reindexed
      get_transaction().commit()
      self.tic() 

      # Related accessor
      self.assertSameSet(alpha.getRegionRelatedList(), 
                        [alpha_path, doo_path, bar_path, foo_path])
      self.assertSameSet(alpha.getRegionRelatedList(
                                              checked_permission="View"), 
                        [alpha_path, doo_path, bar_path, ])
      self.assertSameSet(alpha.getRegionRelatedList(portal_type='Person'), 
                        [doo_path, bar_path, foo_path])
      self.assertSameSet(
                   alpha.getRegionRelatedList(portal_type='Person',
                                              checked_permission="View"), 
                   [doo_path, bar_path, ])

      # Related value accessor
      self.assertSameSet(alpha.getRegionRelatedValueList(), 
                        [alpha, doo, bar, foo])
      self.assertSameSet(alpha.getRegionRelatedValueList(
                                              checked_permission="View"), 
                        [alpha, doo, bar, ])
      self.assertSameSet(alpha.getRegionRelatedValueList(portal_type='Person'),
                        [doo, bar, foo])
      self.assertSameSet(
             alpha.getRegionRelatedValueList(portal_type='Person',
                                             checked_permission="View"), 
             [doo, bar, ])

      # Related id accessor
      self.assertSameSet(alpha.getRegionRelatedIdList(), 
                        [alpha.getId(), doo.getId(), bar.getId(), foo.getId()])
      self.assertSameSet(alpha.getRegionRelatedIdList(
                                             checked_permission="View"),
                        [alpha.getId(), doo.getId(), bar.getId(), ])
      self.assertSameSet(alpha.getRegionRelatedIdList(portal_type='Person'), 
                        [doo.getId(), bar.getId(), foo.getId()])
      self.assertSameSet(
             alpha.getRegionRelatedIdList(portal_type='Person',
                                          checked_permission="View"), 
             [doo.getId(), bar.getId(), ])

      # Related title accessor
      self.assertSameSet(
            alpha.getRegionRelatedTitleList(), 
            [alpha.getTitle(), doo.getTitle(), bar.getTitle(), foo.getTitle()])
      self.assertSameSet(alpha.getRegionRelatedTitleList(
                                          checked_permission="View"), 
                        [alpha.getTitle(), doo.getTitle(), bar.getTitle(), ])
      self.assertSameSet(alpha.getRegionRelatedTitleList(portal_type='Person'), 
                        [doo.getTitle(), bar.getTitle(), foo.getTitle()])
      self.assertSameSet(
             alpha.getRegionRelatedTitleList(portal_type='Person', 
                                             checked_permission="View"), 
             [doo.getTitle(), bar.getTitle(), ])

    def test_25_AqDynamicWithTempObject(self, quiet=quiet, run=run_all_test):
      """Check if _aq_dynamic works correctly, regardless of whether
      it is first called for a temporary object or a persistent object.

      This test is based on the fact that a portal type is shared between
      a temporary document and a persistent document, and if a class for
      the temporary document is used for generating new methods, calling
      such methods from a persistent object may fail, because such a
      persistent object is not an instance of the temporary document class.
      """
      if not run: return
      portal = self.getPortal()

      # Clear out all generated methods.
      _aq_reset()

      # Create a new temporary person object.
      from Products.ERP5Type.Document import newTempPerson
      o = newTempPerson(portal, 'temp_person_1')
      self.assertTrue(o.isTempObject())

      # This should generate a workflow method.
      self.assertEquals(o.getValidationState(), 'draft')
      o.validate()
      self.assertEquals(o.getValidationState(), 'validated')

      # Create a new persistent person object.
      person_module = portal.person_module
      person_id = 'person_1'
      if person_id in person_module.objectIds():
        person_module.manage_delObjects([person_id])
      o = person_module.newContent(id=person_id, portal_type='Person')
      self.failIf(o.isTempObject())

      # This should call methods generated above for the temporary object.
      self.assertEquals(o.getValidationState(), 'draft')
      o.validate()
      self.assertEquals(o.getValidationState(), 'validated')

      # Paranoia: test the reverse snenario as well, although this
      # should succeed anyway.

      # Create a new persistent person object.
      person_id = 'person_2'
      if person_id in person_module.objectIds():
        person_module.manage_delObjects([person_id])
      o = person_module.newContent(id=person_id, portal_type='Person')
      self.failIf(o.isTempObject())

      # Clear out all generated methods.
      _aq_reset()

      # This should generate workflow methods.
      self.assertEquals(o.getValidationState(), 'draft')
      o.validate()
      self.assertEquals(o.getValidationState(), 'validated')

      # Create a new temporary person object.
      o = newTempPerson(portal, 'temp_person_2')
      self.assertTrue(o.isTempObject())

      # This should call methods generated for the persistent object.
      self.assertEquals(o.getValidationState(), 'draft')
      o.validate()
      self.assertEquals(o.getValidationState(), 'validated')

    def test_26_hasAccessors(self):
      """Test 'has' Accessor.
      This accessor returns true if the property is set on the document.
      """
      self._addProperty('Person',
                  ''' { 'id':         'foo_bar',
                        'type':       'string',
                        'mode':       'w', }''')
      obj = self.getPersonModule().newContent(portal_type='Person')
      self.assertTrue(hasattr(obj, 'hasFooBar'))
      self.failIf(obj.hasFooBar())
      obj.setFooBar('something')
      self.assertTrue(obj.hasFooBar())

    def test_27_categoryAccessors(self, quiet=quiet, run=run_all_test):
      """
      The purpose of this test is to make sure that category
      accessors work as expected.

      The test is implemented for both Category and Value
      accessors.

      Test that checked_permission is well configured 
      for View permission
      """
      if not run: return

      if not quiet:
        message = 'Test Category Accessors'
        ZopeTestCase._print('\n '+message)
        LOG('Testing... ', 0, message)

      # Create a few categories
      region_category = self.getPortal().portal_categories.region
      beta_id = "beta"
      beta_title = "Beta System"
      beta = region_category.newContent(
              portal_type = "Category",
              id =          beta_id,
              title =       beta_title, )
      beta_path = beta.getCategoryRelativeUrl()

      checked_permission = 'View'
      beta.manage_permission(checked_permission, roles=[], acquire=0)

      gamma_id = "gamma"
      gamma_title = "Gamma System"
      gamma = region_category.newContent(
              portal_type = "Category",
              id =          gamma_id,
              title =       gamma_title, )
      gamma_path = gamma.getCategoryRelativeUrl()

      # Make sure categories are reindexed
      get_transaction().commit()
      self.tic() 

      self.assertEquals(beta.getRelativeUrl(), 'region/beta')

      # Create a new person
      module = self.getPersonModule()
      foo = module.newContent(portal_type='Person', title='Foo')

      # Check getDefaultCategory accessor
      foo.setDefaultRegionValue(beta)
      self.assertEquals(beta_path, foo.getDefaultRegion())
      self.assertEquals(
          None,
          foo.getDefaultRegion(checked_permission=checked_permission))

      # Check getCategory accessor
      foo.setDefaultRegionValue(beta)
      self.assertEquals(beta_path, foo.getRegion())
      self.assertEquals(
          None,
          foo.getRegion(checked_permission=checked_permission))

      # Check getCategoryId accessor
      foo.setDefaultRegionValue(beta)
      self.assertEquals(beta_id, foo.getRegionId())
      self.assertEquals(
          None,
          foo.getRegionId(checked_permission=checked_permission))

      # Check getCategoryTitle accessor
      foo.setDefaultRegionValue(beta)
      self.assertEquals(beta_title, foo.getRegionTitle())
      self.assertEquals(
          None,
          foo.getRegionTitle(checked_permission=checked_permission))

      # Check getCategoryValue accessor
      foo.setDefaultRegionValue(beta)
      self.assertEquals(beta, foo.getRegionValue())
      self.assertEquals(
          None,
          foo.getRegionValue(checked_permission=checked_permission))

      # Check getCategoryList accessor
      foo.setDefaultRegionValue(beta)
      self.assertSameSet([beta_path], foo.getRegionList())
      self.assertSameSet(
          [],
          foo.getRegionList(checked_permission=checked_permission))

      # Check getCategoryIdList accessor
      foo.setDefaultRegionValue(beta)
      self.assertSameSet([beta_id], foo.getRegionIdList())
      self.assertSameSet(
          [],
          foo.getRegionIdList(checked_permission=checked_permission))

      # Check getCategoryTitleList accessor
      foo.setDefaultRegionValue(beta)
      self.assertSameSet([beta_title], foo.getRegionTitleList())
      self.assertSameSet(
          [],
          foo.getRegionTitleList(
            checked_permission=checked_permission))

      # Check getCategoryValueList accessor
      foo.setDefaultRegionValue(beta)
      self.assertSameSet([beta], foo.getRegionValueList())
      self.assertSameSet(
          [],
          foo.getRegionValueList(
            checked_permission=checked_permission))

      # Check getCategorySet accessor
      foo.setDefaultRegionValue(beta)
      self.assertSameSet(set([beta_path]), foo.getRegionSet())
      self.assertSameSet(
          set(),
          foo.getRegionSet(checked_permission=checked_permission))

      # Check getCategoryIdSet accessor
      foo.setDefaultRegionValue(beta)
      self.assertSameSet(set([beta_id]), foo.getRegionIdSet())
      self.assertSameSet(
          set(),
          foo.getRegionIdSet(checked_permission=checked_permission))

      # Check getCategoryTitleSet accessor
      foo.setDefaultRegionValue(beta)
      self.assertSameSet(set([beta_title]), foo.getRegionTitleSet())
      self.assertSameSet(
          set(),
          foo.getRegionTitleSet(
            checked_permission=checked_permission))

      # Check getCategoryValueSet accessor
      foo.setDefaultRegionValue(beta)
      self.assertSameSet(set([beta]), foo.getRegionValueSet())
      self.assertSameSet(
          set(),
          foo.getRegionValueSet(
            checked_permission=checked_permission))

      foo.setRegionValue(None)
      self.assertEquals(None, foo.getRegion())
      # Check setCategoryValue accessor
      foo.setRegionValue(beta)
      self.assertEquals(beta_path, foo.getRegion())
      foo.setRegionValue(None)
      foo.setRegionValue(gamma, 
                         checked_permission=checked_permission)
      self.assertSameSet([gamma_path], foo.getRegionList())
      foo.setRegionValue(beta)
      foo.setRegionValue(gamma, 
                         checked_permission=checked_permission)
      self.assertSameSet([beta_path, gamma_path], foo.getRegionList())

      foo.setRegionValue(None)
      self.assertEquals(None, foo.getRegion())
      # Check setDefaultCategoryValue accessor
      foo.setDefaultRegionValue(beta)
      self.assertEquals(beta_path, foo.getRegion())
      # XXX setDefaultValue seems buggy when passing None
#       foo.setDefaultRegionValue(None)
      foo.setRegionValue(None)
      foo.setDefaultRegionValue(gamma, 
                                checked_permission=checked_permission)
      self.assertEquals(gamma_path, foo.getRegion())
      foo.setDefaultRegionValue(beta_path)
      foo.setDefaultRegionValue(gamma_path, 
                                checked_permission=checked_permission)
      self.assertEquals(gamma_path, foo.getDefaultRegion())
      self.assertSameSet([beta_path, gamma_path], foo.getRegionList())

      foo.setRegionValue(None)
      self.assertEquals(None, foo.getRegion())
      # Check setCategory accessor
      foo.setRegion(beta_path)
      self.assertEquals(beta_path, foo.getRegion())
      foo.setRegion(None)
      foo.setRegion(gamma_path, 
                    checked_permission=checked_permission)
      self.assertEquals(gamma_path, foo.getRegion())
      foo.setRegion(beta_path)
      foo.setRegion(gamma_path, 
                    checked_permission=checked_permission)
      self.assertSameSet([beta_path, gamma_path], foo.getRegionList())
      self.assertEquals(gamma_path,
                        foo.getRegion(checked_permission=checked_permission))

      foo.setRegionValue(None)
      self.assertEquals(None, foo.getRegion())
      # Check setDefaultCategory accessor
      foo.setDefaultRegion(beta_path)
      self.assertEquals(beta_path, foo.getRegion())
      foo.setRegion(None)
      foo.setDefaultRegion(gamma_path, 
                    checked_permission=checked_permission)
      self.assertEquals(gamma_path, foo.getRegion())
      foo.setDefaultRegion(beta_path)
      foo.setDefaultRegion(gamma_path, 
                    checked_permission=checked_permission)
      self.assertSameSet([beta_path, gamma_path], foo.getRegionList())
      self.assertEquals(gamma_path,
                        foo.getDefaultRegion())

      foo.setRegionValue(None)
      self.assertEquals(None, foo.getRegion())
      # Check setCategoryList accessor
      foo.setRegionList([beta_path])
      self.assertEquals(beta_path, foo.getRegion())
      foo.setRegionList([])
      foo.setRegionList([gamma_path], 
                    checked_permission=checked_permission)
      self.assertEquals(gamma_path, foo.getRegion())
      foo.setRegionList([beta_path])
      foo.setRegionList([gamma_path], 
                    checked_permission=checked_permission)
      self.assertSameSet([beta_path, gamma_path], foo.getRegionList())

      foo.setRegionValue(None)
      self.assertEquals(None, foo.getRegion())
      # Check setCategoryValueList accessor
      foo.setRegionValueList([beta])
      self.assertEquals(beta_path, foo.getRegion())
      foo.setRegionList([])
      foo.setRegionValueList([gamma], 
                    checked_permission=checked_permission)
      self.assertEquals(gamma_path, foo.getRegion())
      foo.setRegionValueList([beta])
      foo.setRegionValueList([gamma], 
                    checked_permission=checked_permission)
      self.assertSameSet([beta_path, gamma_path], foo.getRegionList())

      foo.setRegionValue(None)
      self.assertEquals(None, foo.getRegion())
      # Check setCategorySet accessor
      foo.setRegionSet([beta_path])
      self.assertEquals(beta_path, foo.getRegion())
      foo.setRegionSet([])
      foo.setRegionSet([gamma_path],
                    checked_permission=checked_permission)
      self.assertEquals(gamma_path, foo.getRegion())
      foo.setRegionSet([beta_path])
      foo.setRegionSet([gamma_path], 
                    checked_permission=checked_permission)
      self.assertSameSet([beta_path, gamma_path], foo.getRegionList())

      foo.setRegionValue(None)
      self.assertEquals(None, foo.getRegion())
      # Check setCategoryValueSet accessor
      foo.setRegionValueSet([beta])
      self.assertEquals(beta_path, foo.getRegion())
      foo.setRegionSet([])
      foo.setRegionValueSet([gamma], 
                    checked_permission=checked_permission)
      self.assertEquals(gamma_path, foo.getRegion())
      foo.setRegionValueSet([beta])
      foo.setRegionValueSet([gamma], 
                    checked_permission=checked_permission)
      self.assertSameSet([beta_path, gamma_path], foo.getRegionList())
    
    def test_list_accessors(self):
      self._addProperty('Person', '''{'id': 'dummy',
                                      'type': 'lines',
                                      'mode': 'w',}''')
      module = self.getPersonModule()
      # we set the property on the module, to check acquisition works as
      # expected.
      module.dummy = 'value acquired on the module'
      person = module.newContent(id='1', portal_type='Person')

      # default accessor and list accessors are generated
      self.assertTrue(hasattr(person, 'getDummy'))
      self.assertTrue(hasattr(person, 'getDummyList'))

      self.assertEquals(person.getDummy(), None)
      self.assertEquals(person.getDummyList(), None)
      self.assertEquals(person.getDummySet(), None)

      person.setDummyList(['a', 'b'])
      self.assertEquals(person.getDummy(), 'a')
      self.assertEquals(person.getDummyList(), ['a', 'b'])
      self.assertEquals(person.getDummySet(), ['a', 'b'])

      person.setDummy('value')
      self.assertEquals(person.getDummy(), 'value')
      self.assertEquals(person.getDummyList(), ['value'])
      self.assertEquals(person.getDummySet(), ['value'])

    def test_translated_accessors(self):
      self._addProperty('Person', '''{'id': 'dummy',
                                      'type': 'string',
                                      'translatable': 1,
                                      'translation_domain': 'erp5_ui',
                                      'mode': 'w',}''')
      self.portal.Localizer = DummyLocalizer()
      doc = self.portal.person_module.newContent(portal_type='Person')

      # translated and translation domain accessors are generated
      self.assertTrue(hasattr(doc, 'getTranslatedDummy'))
      self.assertTrue(hasattr(doc, 'getDummyTranslationDomain'))
      
      self.assertEquals('erp5_ui', doc.getDummyTranslationDomain())
      doc.setDummy('foo')
      self.assertEquals('foo', doc.getTranslatedDummy())
      # the value of the property is translated with erp5_ui
      self.assertEquals(['foo'], self.portal.Localizer.erp5_ui._translated)

      # we can change the translation domain on the portal type
      self.portal.portal_types.Person.changeTranslations(
                                    dict(dummy='erp5_content'))
      self.assertEquals('erp5_content', doc.getDummyTranslationDomain())
      self.assertEquals('foo', doc.getTranslatedDummy())
      self.assertEquals(['foo'],
                  self.portal.Localizer.erp5_content._translated)

      # set on instance. It has priority over portal type
      doc.setDummyTranslationDomain('default')
      self.assertEquals('default', doc.getDummyTranslationDomain())
      self.assertEquals('foo', doc.getTranslatedDummy())
      self.assertEquals(['foo'], self.portal.Localizer.default._translated)


    # _aq_reset should be called implicitly when the system configuration
    # changes:
    def test_aq_reset_on_portal_types_properties_change(self):
      doc = self.portal.person_module.newContent(portal_type='Person')
      ti = self.getTypesTool()['Person']
      self.assertFalse(hasattr(doc, 'getDestination'))
      ti.manage_editProperties(dict(base_category_list=
                               list(ti.base_category_list) + ['destination']))
      self.assertTrue(hasattr(doc, 'getDestination'))

    def test_aq_reset_on_workflow_chain_change(self):
      doc = self.portal.person_module.newContent(portal_type='Person')
      ti = self.getTypesTool()['Person']
      self.assertFalse(hasattr(doc, 'getCausalityState'))
      # chain the portal type with a workflow that has 'causality_state' as
      # state variable name, this should regenerate the getCausalityState
      # accessor. This test might have to be updated whenever
      # delivery_causality_workflow changes.
      self.portal.portal_workflow.manage_changeWorkflows(
          default_chain='',
          props=dict(chain_Person='delivery_causality_workflow'))
      self.assertTrue(hasattr(doc, 'getCausalityState'))

    def test_aq_reset_on_workflow_method_change(self):
      doc = self.portal.person_module.newContent(portal_type='Person')
      ti = self.getTypesTool()['Person']
      self.portal.portal_workflow.manage_changeWorkflows(
          default_chain='',
          props=dict(chain_Person='delivery_causality_workflow'))
      self.assertTrue(hasattr(doc, 'diverge'))

      wf = self.portal.portal_workflow.delivery_causality_workflow
      wf.transitions.addTransition('dummy_workflow_method')
      from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD
      wf.transitions.dummy_workflow_method.setProperties(
          title='', new_state_id='', trigger_type=TRIGGER_WORKFLOW_METHOD)
      self.assertTrue(hasattr(doc, 'dummyWorkflowMethod'))

      wf.transitions.deleteTransitions(['dummy_workflow_method'])
      self.assertFalse(hasattr(doc, 'dummyWorkflowMethod'))

    def test_aq_reset_on_workflow_state_variable_change(self):
      doc = self.portal.person_module.newContent(portal_type='Person')
      ti = self.getTypesTool()['Person']
      self.portal.portal_workflow.manage_changeWorkflows(
          default_chain='',
          props=dict(chain_Person='delivery_causality_workflow'))
      self.assertTrue(hasattr(doc, 'getCausalityState'))
      wf = self.portal.portal_workflow.delivery_causality_workflow
      wf.variables.setStateVar('dummy_state')
      self.assertTrue(hasattr(doc, 'getDummyState'))

    # ... other cases should be added here


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Type))
  return suite
