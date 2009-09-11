##############################################################################
# -*- coding: utf-8 -*-
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

import cPickle
import md5
import unittest
import sys

import transaction
from random import randint
from Acquisition import aq_base
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import DummyLocalizer
from zLOG import LOG, INFO
from Products.CMFCore.Expression import Expression
from Products.CMFCore.tests.base.testcase import LogInterceptor
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.ERP5Type.Base import _aq_reset
from Products.ERP5Type.tests.utils import installRealClassTool
from Products.ERP5Type.Utils import removeLocalPropertySheet
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from AccessControl.ZopeGuards import guarded_getattr, guarded_hasattr
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5Type.tests.utils import removeZODBPythonScript
from Products.ERP5Type import Permissions

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
    transaction.abort()
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
    transaction.commit()
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
                           property_sheet_code=property_sheet_code,
                           property_sheet_name=property_sheet_name)

class TestERP5Type(PropertySheetTestCase, LogInterceptor):
    """Tests ERP5TypeInformation and per portal type generated accessors.
    """
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
      transaction.abort()
      for module in [ self.getPersonModule(),
                      self.getOrganisationModule(),
                      self.getCategoryTool().region ]:
        module.manage_delObjects(list(module.objectIds()))

      # set Person.acquire_local_roles back.
      if getattr(self, 'person_acquire_local_roles', None) is not None:
        self.getTypesTool().getTypeInfo('Person').acquire_local_roles = self.person_acquire_local_roles
        self.portal.portal_caches.clearAllCache()

      transaction.commit()
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

    # erp5_core tests
    def testERP5CoreHasParentBaseCategory(self):
      # Test if erp5_core parent base category was imported successfully
      self.assertNotEquals(getattr(self.getCategoryTool(), 'parent', None), None)

    def testERP5CoreHasImageType(self):
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
      o = newTempOrganisation(portal.organisation_module,'b')
      self.assertEquals(o.isTempObject(), 1)
      a = o.newContent(portal_type = 'Telephone')
      self.assertEquals(a.isTempObject(), 1)
      self.assertEquals(a, guarded_getattr(o, a.getId()))
      self.logout()
      self.login()

      # Check that temp object creation do not write in the ZODB
      class WriteError(Exception):
        pass
      def _setLastId(self, id):
        raise WriteError
      portal.person_module.__class__._setLastId = _setLastId
      try:
        try:
          o = portal.person_module.newContent(portal_type="Person", 
                                              temp_object=1)
        except WriteError:
          self.fail("Container last ID modified")
      finally:
        del portal.person_module.__class__._setLastId

      # the module is not changed from ZODB point of view
      self.assertFalse(portal.person_module._p_changed)
      # the object is not in ZODB
      self.assertEquals(o._p_jar, None)
      transaction.commit()
      self.assertEquals(o._p_jar, None)

      # Temp objects always get a dummy ID by default.
      o = portal.person_module.newContent(portal_type="Person", 
                                          temp_object=1)
      first_id = o.getId()
      o = portal.person_module.newContent(portal_type="Person", 
                                          temp_object=1)
      second_id = o.getId()
      self.assertEquals(first_id, second_id)
      self.assertEquals('None', second_id)

      # Make sure a temp object can't be stored in the ZODB
      portal.person_module._setObject(o.getId(), aq_base(o))
      try:
        transaction.commit()
      except cPickle.PicklingError:
        transaction.abort()
      else:
        self.fail("No exception raised when storing explicitly a temp object"
                  " on a persistent object")

      # Check temp objects subobjects can be accessed with OFS API
      parent = portal.person_module.newContent(portal_type="Person",
                                               temp_object=1)
      child1 = parent.newContent(portal_type='Person', id='1')
      child11 = child1.newContent(portal_type='Person', id='1')
      child2 = parent.newContent(portal_type='Person', id='2')

      self.assertEquals(child1, parent._getOb('1'))
      self.assertEquals(child2, parent._getOb('2'))

      self.assertEquals(child1, parent['1'])
      self.assertEquals(child2, parent['2'])

      self.assertEquals(child1, getattr(parent, '1'))
      self.assertEquals(child2, getattr(parent, '2'))

      self.assertEquals(child1, parent.restrictedTraverse('1'))
      self.assertEquals(child11, parent.restrictedTraverse('1/1'))
      self.assertEquals(child2, parent.restrictedTraverse('2'))

      self.assertEquals(('person_module', 'None', '1', '1'),
          self.portal.portal_url.getRelativeContentPath(child11))


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
        transaction.commit()
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
        transaction.commit()
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

      # Test _setRegion doesn't reindex the object.
      person_object._setRegion(category_id)
      transaction.commit()
      self.assertFalse(person_object.hasActivity())
      person_object.setRegion(None)
      transaction.commit()
      self.assertTrue(person_object.hasActivity())
      self.tic()

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
      try:
        folder = self.getOrganisationModule()
        orga = folder.newContent(portal_type='Organisation',)
        # call an accessor, _aq_dynamic will generate accessors
        orga.getId()
      finally:
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
      transaction.commit(1)

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
      self._addPropertySheet('Organisation', property_sheet_code=text)
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
      transaction.commit()
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
      transaction.commit()
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
      person.setSubject('beta')
      self.assertEquals(person.getSubject(), 'beta')
      person.setSubjectList(['alpha', 'alpha'])
      self.assertEquals(person.getSubjectList(), ['alpha', 'alpha'])
      self.assertEquals(person.getSubjectSet(), ['alpha'])
      person.setSubjectSet(['beta', 'beta'])
      self.assertEquals(person.getSubjectList(), ['beta'])
      self.assertEquals(person.getSubjectSet(), ['beta'])
      person.setSubjectList(['beta', 'alpha', 'beta'])
      self.assertEquals(person.getSubjectList(), ['beta', 'alpha', 'beta'])
      person.setSubjectSet(['alpha', 'beta', 'alpha'])
      self.assertEquals(person.getSubjectList(), ['beta', 'alpha'])
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

      # string accessors converts the data type, if provided an unicode, it
      # will store an utf-8 encoded string
      person.setDummyPsProp(u'type convérsion')
      self.assertEquals('type convérsion', person.getDummyPsProp())
      # if provided anything else, it will store it's string representation
      person.setDummyPsProp(1)
      self.assertEquals('1', person.getDummyPsProp())

      class Dummy:
        def __str__(self):
          return 'string representation'
      person.setDummyPsProp(Dummy())
      self.assertEquals('string representation', person.getDummyPsProp())


    def test_17_WorkflowStateAccessor(self):
      """Tests for workflow state. assumes that validation state is chained to
      the Person portal type and that this workflow has 'validation_state' as
      state_variable.
      """
      self.portal.Localizer = DummyLocalizer()
      message_catalog = self.portal.Localizer.erp5_ui
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
      self.assertEquals(initial_state.title,
                        person.getTranslatedValidationStateTitle())
      self.assertTrue([initial_state.title], message_catalog._translated)
      
      self.assertEquals(initial_state.getId(),
                        person.getProperty('validation_state'))
      self.assertEquals(initial_state.title,
                        person.getProperty('validation_state_title'))
      message_catalog._translated = []
      self.assertEquals(initial_state.title,
                        person.getProperty('translated_validation_state_title'))
      self.assertTrue([initial_state.title], message_catalog._translated)
      
      # default parameter is accepted by getProperty for compatibility
      self.assertEquals(initial_state.getId(),
                        person.getProperty('validation_state', 'default'))
      self.assertEquals(initial_state.title,
                        person.getProperty('validation_state_title', 'default'))
      message_catalog._translated = []
      self.assertEquals(initial_state.title,
                        person.getProperty('translated_validation_state_title',
                        'default'))
      self.assertTrue([initial_state.title], message_catalog._translated)

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
      message_catalog._translated = []
      self.assertEquals(other_state.title,
                        person.getProperty('translated_validation_state_title'))
      self.assertTrue([other_state.title], message_catalog._translated)
    
    DEFAULT_ORGANISATION_TITLE_PROP = '''
                      { 'id':         'organisation',
                        'storage_id': 'default_organisation',
                        'type':       'content',
                        'portal_type': ('Organisation', ),
                        'acquired_property_id': ('title', 'reference'),
                        'mode':       'w', }'''

    def test_18_SimpleContentAccessor(self,quiet=quiet, run=run_all_test):
      """Tests a simple content accessor.
      This tests content accessors, for properties that have class methods.
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

      # make sure this new organisation is indexed
      transaction.commit()
      self.assertEquals(1, len([m for m in
        self.portal.portal_activities.getMessageList()
        if m.method_id == 'immediateReindexObject' 
            and m.object_path == default_organisation.getPhysicalPath()]))
      self.tic()

      # edit once again, this time no new organisation is created, the same is
      # edited, and reindexed
      self.assertEquals(1, len(person.objectIds()))
      self.assertFalse(person._p_changed)
      person.setDefaultOrganisationTitle('New title')
      self.assertEquals('New title',
                        default_organisation.getTitle())
      transaction.commit()
      self.assertEquals(1, len([m for m in
        self.portal.portal_activities.getMessageList()
        if m.method_id == 'immediateReindexObject' 
            and m.object_path == default_organisation.getPhysicalPath()]))
      self.tic()

      # edit once again (this time, with edit method), this time no new 
      # organisation is created, the same is edited, and reindexed
      self.assertEquals(1, len(person.objectIds()))
      self.assertFalse(person._p_changed)
      person.edit(default_organisation_title='New title 2')
      self.assertEquals('New title 2',
                        default_organisation.getTitle())
      self.assertEquals(0, len([m for m in
                        self.portal.portal_activities.getMessageList()]))
      transaction.commit()
      self.assertEquals(1, len([m for m in
        self.portal.portal_activities.getMessageList()
        if m.method_id == 'immediateReindexObject' 
            and m.object_path == default_organisation.getPhysicalPath()]))
      self.tic()


    def test_18_SimpleContentAccessorWithGeneratedAccessor(self):
      # test reindexing of content accessors, on acquired properties which are
      # _aq_dynamic generated accessors.
      # This is test is very similar to test_18_SimpleContentAccessor, but we
      # use reference instead of title, because Reference accessors are
      # generated. 
      self._addProperty('Person', self.DEFAULT_ORGANISATION_TITLE_PROP)
      person = self.getPersonModule().newContent(id='1', portal_type='Person')
      self.assertTrue(hasattr(person, 'getDefaultOrganisationReference'))
      self.assertTrue(hasattr(person, 'setDefaultOrganisationReference'))
      person.setDefaultOrganisationReference('The organisation ref')

      default_organisation = person._getOb('default_organisation', None)
      self.assertNotEquals(None, default_organisation)
      self.assertEquals('Organisation',
                        default_organisation.getPortalTypeName())
      self.assertEquals('The organisation ref',
                        default_organisation.getReference())

      # make sure this new organisation is indexed
      transaction.commit()
      self.assertEquals(1, len([m for m in
        self.portal.portal_activities.getMessageList()
        if m.method_id == 'immediateReindexObject' 
            and m.object_path == default_organisation.getPhysicalPath()]))
      self.tic()

      # edit once again, this time no new organisation is created, the same is
      # edited, and reindexed
      self.assertEquals(1, len(person.objectIds()))
      self.assertFalse(person._p_changed)
      person.setDefaultOrganisationReference('New reference')
      self.assertEquals('New reference',
                        default_organisation.getReference())
      transaction.commit()
      self.assertEquals(1, len([m for m in
        self.portal.portal_activities.getMessageList()
        if m.method_id == 'immediateReindexObject' 
            and m.object_path == default_organisation.getPhysicalPath()]))
      self.tic()

      # edit once again (this time, with edit method), this time no new 
      # organisation is created, the same is edited, and reindexed
      self.assertEquals(1, len(person.objectIds()))
      self.assertFalse(person._p_changed)
      person.edit(default_organisation_reference='New reference 2')
      self.assertEquals('New reference 2',
                        default_organisation.getReference())
      self.assertEquals(0, len([m for m in
                        self.portal.portal_activities.getMessageList()]))
      transaction.commit()
      self.assertEquals(1, len([m for m in
        self.portal.portal_activities.getMessageList()
        if m.method_id == 'immediateReindexObject' 
            and m.object_path == default_organisation.getPhysicalPath()]))
      self.tic()
    

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
        _aq_reset()

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
    
    DEFAULT_LANGUAGE_PROP = '''
          { 'id':         'available_language',
            'type':       'tokens',
            'default'     : (),
            'acquired_property_id': ('subject', ),
            'acquisition_base_category': ( 'parent', ),
            'acquisition_portal_type'  : ( 'Person', ),
            'acquisition_copy_value'   : 0,
            'acquisition_mask_value'   : 1,
            'acquisition_accessor_id'  : 'getAvailableLanguageList',
            'acquisition_depends'      : None,
            'mode':       'rw', }'''
    
    def test_19c_AcquiredTokensAccessor(self,quiet=quiet, run=run_all_test):
      """Tests an acquired tokens accessor.
         We check in particular that getDefault[Property] and 
         setDefault[Property] are working correctly
      """
      if not run: return
      self._addProperty('Person', self.DEFAULT_LANGUAGE_PROP)
      self._addProperty('Email', self.DEFAULT_LANGUAGE_PROP)

      # Category setters (list, set, default)
      person = self.getPersonModule().newContent(id='1', portal_type='Person')
      email = person.newContent(portal_type='Email')

      self.assertEquals(0, len(email.getAvailableLanguageList()))
      email.setAvailableLanguageSet(['fr', 'en', 'ja'])
      self.assertEquals(email.getAvailableLanguageList(), ('fr', 'en', 'ja'))
      self.assertEquals(email.getAvailableLanguage(), 'fr')
      self.assertEquals(email.getDefaultAvailableLanguage(), 'fr')
      email.setDefaultAvailableLanguage('ja')
      self.assertEquals(email.getAvailableLanguage(), 'ja')
      self.assertEquals(email.getDefaultAvailableLanguage(), 'ja')
      self.assertEquals(email.getAvailableLanguageList(), ('ja', 'fr', 'en'))



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
      gender = self.getCategoryTool().gender._getOb('male', None)
      if gender is None:
        gender = self.getCategoryTool().gender.newContent(
                            portal_type='Category', id='male')
      # Category can not be used as asContext parameter
#       new_copy = obj.asContext(gender=gender.getCategoryRelativeUrl())
#       self.assertEquals(gender.getCategoryRelativeUrl(), new_copy.getGender())
      new_copy = obj.asContext()
      new_copy.edit(gender=gender.getCategoryRelativeUrl())
      transaction.commit()
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
      transaction.commit() ; self.tic()
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
      transaction.commit() ; self.tic()
      self.assertTrue('Auditor' in user.getRolesInContext(person))
      self.logout()
      newSecurityManager(None, user)
      self.assertEquals(len(person_module.searchFolder(id=person.getId())), 0)
      self.logout()
      self.login()

      # Now invoke the reindexing explicitly, so the catalog should be
      # synchronized.
      person_module.recursiveReindexObject()
      transaction.commit() ; self.tic()
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
      transaction.commit()
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
      transaction.commit()
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

      # check hasCategory accessors
      foo.setRegionValue(None)
      self.assertEquals(None, foo.getRegion())
      self.assertFalse(foo.hasRegion())
      foo.setRegionValue(beta)
      self.assertTrue(foo.hasRegion())
    
    def test_category_accessor_to_unaccessible_documents(self):
      # Category Accessors raises Unauthorized when you try to access objects
      # you cannot Access, unless you explictly pass checked_permission=

      region_category = self.getPortal().portal_categories.region
      beta_id = "beta"
      beta_title = "Beta System"
      beta = region_category.newContent(
              portal_type = "Category",
              id =          beta_id,
              title =       beta_title, )
      beta_path = beta.getCategoryRelativeUrl()

      gamma_id = "gamma"
      gamma_title = "Gamma System"
      gamma = region_category.newContent(
              portal_type = "Category",
              id =          gamma_id,
              title =       gamma_title, )
      gamma_path = gamma.getCategoryRelativeUrl()

      # Make sure categories are reindexed
      transaction.commit()
      self.tic()

      beta.manage_permission('View', roles=[], acquire=0)
      beta.manage_permission('Access contents information', roles=[], acquire=0)
      # with this security setting, it's not possible to access "beta":
      self.assertRaises(Unauthorized,
          region_category.restrictedTraverse, "beta")


      # Create a new person, and associate it to beta and gamma.
      module = self.getPersonModule()
      foo = module.newContent(portal_type='Person', title='Foo')
      foo.setRegionValueList((beta, gamma))

      # getRegionList returns relative URLs, no security checks are applied
      self.assertEquals([beta_path, gamma_path],
                        foo.getRegionList())
      self.assertEquals([gamma_path],
          foo.getRegionList(checked_permission='View'))
      
      # getRegionValueList raises Unauthorized if document is related to
      # private documents (as always, unless you pass checked_permission)
      self.assertRaises(Unauthorized, foo.getRegionValueList)
      self.assertRaises(Unauthorized, foo.getRegionValueSet)
      self.assertEquals([gamma],
          foo.getRegionValueList(checked_permission='View'))

      # same for property accessors 
      self.assertRaises(Unauthorized, foo.getRegionTitleList)
      self.assertRaises(Unauthorized, foo.getRegionTitleSet)
      self.assertEquals(["Gamma System"],
          foo.getRegionTitleList(checked_permission='View'))

      # same for default accessors
      self.assertRaises(Unauthorized, foo.getRegionValue)
      self.assertRaises(Unauthorized, foo.getRegionTitle)

    def test_acquired_property_to_unaccessible_documents(self):
      # Acquired Accessors raises Unauthorized when you try to access objects
      # you cannot Access, unless you explictly pass checked_permission=

      region_category = self.getPortal().portal_categories.region
      beta_id = "beta"
      beta_title = "Beta System"
      beta = region_category.newContent(
              portal_type = "Category",
              id =          beta_id,
              title =       beta_title, )
      beta_path = beta.getCategoryRelativeUrl()

      gamma_id = "gamma"
      gamma_title = "Gamma System"
      gamma = region_category.newContent(
              portal_type = "Category",
              id =          gamma_id,
              title =       gamma_title, )
      gamma_path = gamma.getCategoryRelativeUrl()

      # Make sure categories are reindexed
      transaction.commit()
      self.tic()

      beta.manage_permission('View', roles=[], acquire=0)
      beta.manage_permission('Access contents information', roles=[], acquire=0)
      # with this security setting, it's not possible to access "beta":
      self.assertRaises(Unauthorized,
          region_category.restrictedTraverse, "beta")

      # Define the acquired property
      text = """
class TestPropertySheet:
    \"\"\"
        TestAcquiredAccessorPropertySheet for this unit test
    \"\"\"

    _properties = (
        {   'id'          : 'wrapped_region_title',
            'description' : 'The title of the region',
            'type'        : 'string',
            'multivalued'        : 1,
            'acquisition_base_category'     : ('region',),
            'acquisition_portal_type'       : ('Category', ),
            'acquisition_copy_value'        : 0,
            'acquisition_accessor_id'       : 'getTitle',
            'acquisition_depends'           : None,
            'alt_accessor_id'               : ('_categoryGetRegionTitle', ),
            'mode'        : 'w' },
      )

"""
      self._addPropertySheet('Person', property_sheet_code=text)

      # Create a new person, and associate it to beta and gamma.
      module = self.getPersonModule()
      foo = module.newContent(portal_type='Person', title='Foo')
      foo.setRegionValueList((beta, gamma))

      # getRegionList returns relative URLs, no security checks are applied
      self.assertEquals([beta_path, gamma_path],
                        foo.getRegionList())
      self.assertEquals([gamma_path],
          foo.getRegionList(checked_permission='View'))

      # getWrappedRegionTitleList raise Unauthorized if a related document is
      # private
      self.assertRaises(Unauthorized, foo.getWrappedRegionTitleList)
      self.assertEquals(["Gamma System"],
          foo.getWrappedRegionTitleList(checked_permission='View'))

      # Remove permission from parent object, the behaviour of acessor should
      # be kept. If you have no permission to the parent, this means that the 
      # sub objects cannot be accessed too.
      gamma.getParentValue().manage_permission("View", [], acquire=0)

      # getProperty is used by forms
      self.assertEquals(None,foo.getProperty("wrapped_region_title_list",
                                                            checked_permission='View'))
      self.assertEquals(None,
                foo.getWrappedRegionTitleList(checked_permission='View'))

      self.assertEquals(["Gamma System"],
                      foo.getWrappedRegionTitleList(checked_permission='Access contents information'))

      gamma.getParentValue().manage_permission("Access contents information", [], acquire=0)
      self.assertEquals(None,
                foo.getWrappedRegionTitleList(checked_permission='View'))

      self.assertEquals(None,
                      foo.getWrappedRegionTitleList(checked_permission='Access contents information'))


    def test_category_accessor_to_non_existing_documents(self):
      # tests behaviour of category accessors with relations to non existing
      # documents.
      region_category = self.getPortal().portal_categories.region
      beta_id = "beta"
      beta_title = "Beta System"
      beta = region_category.newContent(
              portal_type = "Category",
              id =          beta_id,
              title =       beta_title, )
      beta_path = beta.getCategoryRelativeUrl()

      # gamma does not exist

      # Make sure categories are reindexed
      transaction.commit()
      self.tic()

      # Create a new person, and associate it to beta and gamma.
      module = self.getPersonModule()
      foo = module.newContent(portal_type='Person', title='Foo')
      foo.setRegionList(('beta', 'gamma'))

      self.assertEquals([beta_path, 'gamma'],
                        foo.getRegionList())
      # using relations to non existant objects will issue a warning in
      # event.log
      self._catch_log_errors(ignored_level=sys.maxint)
      self.assertEquals([beta],
                        foo.getRegionValueList())
      self.assertEquals([beta_title],
                        foo.getRegionTitleList())
      self._ignore_log_errors()
      logged_errors = [ logrecord for logrecord in self.logged
                        if logrecord[0] == 'CMFCategory' ]
      self.assertEquals('Could not access object region/gamma',
                        logged_errors[0][2])
      

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




    # Tests for _aq_dynamic patch. Probably not in the right place.
    def test_aq_dynamic(self):
      doc = self.portal.person_module.newContent(portal_type='Person')
      from Acquisition import Explicit

      class Ok(Explicit):
        aq_dynamic_calls = []
        def _aq_dynamic(self, name):
          self.aq_dynamic_calls.append(name)
          return 'returned_attr'

      ok = Ok().__of__(doc)
      self.assertEquals('returned_attr', getattr(ok, 'attr'))
      self.assertEquals(ok.aq_dynamic_calls, ['attr'])
      
    def test_aq_dynamic_exception(self):
      # if an exception is raised in _aq_dynamic, it should not be hidden
      doc = self.portal.person_module.newContent(portal_type='Person')
      from Acquisition import Explicit

      class NotOk(Explicit):
        def _aq_dynamic(self, name):
          raise ValueError()

      not_ok = NotOk().__of__(doc)
      self.assertRaises(ValueError, getattr, not_ok, 'attr')
      self.assertFalse(hasattr(not_ok, 'attr'))

    def test_renameObjectsReindexSubobjects(self, quiet=quiet, run=run_all_test):
      """Test that renaming an object with subobjects causes them to be
         reindexed (their path must be updated).
      """
      if not run: return
      folder = self.getOrganisationModule()
      initial_id = 'foo'
      final_id = 'bar'
      subdocument_id = 'sub'
      object = folder.newContent(portal_type='Organisation', id=initial_id)
      object.newContent(id=subdocument_id)
      transaction.commit()
      self.tic()
      folder = self.getOrganisationModule()
      folder.manage_renameObjects([initial_id], [final_id])
      transaction.commit()
      self.tic()
      folder = self.getOrganisationModule()
      subdocument = folder[final_id][subdocument_id]
      subdocument_catalogged_path = self.getPortalObject().portal_catalog.getSQLCatalog()[subdocument.uid].path
      self.assertEqual(subdocument.getPath(), subdocument_catalogged_path)

    def test_getCreationDate(self, quiet=quiet, run=run_all_test):
      """
      Check that getCreationDate does not acquire creation_date property from
      site.
      """
      if not run: return
      portal = self.getPortalObject()
      folder = self.getOrganisationModule()
      object = folder.newContent(portal_type='Organisation')
      self.assertNotEquals(object.getCreationDate(), portal.CreationDate())
      self.assertNotEquals(object.getCreationDate(), folder.getCreationDate())

    def test_copyWithoutModificationRight(self, quiet=quiet, run=run_all_test):
      """
      Check that it is possible to copy an object on which user doesn't have
      "Modify portal content" permission.
      """
      if not run: return
      portal = self.getPortalObject()
      folder = self.getOrganisationModule()
      object = folder.newContent(portal_type='Organisation')
      script_container = portal.portal_skins.custom
      script_id = '%s_afterClone' % (object.getPortalType().replace(' ', ''), )
      createZODBPythonScript(script_container, script_id, '', 'context.setTitle("couscous")')
      try:
        security_manager = getSecurityManager()
        self.assertEquals(1, security_manager.checkPermission('Access contents information', object))
        self.assertEquals(1, security_manager.checkPermission('Modify portal content', object))
        object.manage_permission('Modify portal content')
        clipboard = folder.manage_copyObjects(ids=[object.id])
        # Test fails if this method raises.
        folder.manage_pasteObjects(clipboard)
      finally:
        removeZODBPythonScript(script_container, script_id)

    def test_DefaultSecurityOnAccessors(self):
      # Test accessors are protected correctly
      self._addProperty('Person',
                  ''' { 'id':         'foo_bar',
                        'type':       'string',
                        'mode':       'w', }''')
      obj = self.getPersonModule().newContent(portal_type='Person')

      self.assertTrue(guarded_hasattr(obj, 'setFooBar'))
      self.assertTrue(guarded_hasattr(obj, 'getFooBar'))
      
      # setter is protected by default with modify portal content
      obj.manage_permission(Permissions.ModifyPortalContent, [], 0)
      self.assertFalse(guarded_hasattr(obj, 'setFooBar'))
      self.assertTrue(guarded_hasattr(obj, 'getFooBar'))
      
      # getter is protected with Access content information
      obj.manage_permission(Permissions.ModifyPortalContent, ['Manager'], 1)
      obj.manage_permission(Permissions.AccessContentsInformation, [], 0)
      self.assertTrue(guarded_hasattr(obj, 'setFooBar'))
      self.assertFalse(guarded_hasattr(obj, 'getFooBar'))

    def test_DefaultSecurityOnListAccessors(self):
      # Test list accessors are protected correctly
      self._addProperty('Person',
                  ''' { 'id':         'foo_bar',
                        'type':       'lines',
                        'mode':       'w', }''')
      obj = self.getPersonModule().newContent(portal_type='Person')
      self.assertTrue(guarded_hasattr(obj, 'setFooBarList'))
      self.assertTrue(guarded_hasattr(obj, 'getFooBarList'))
      
      # setter is protected by default with modify portal content
      obj.manage_permission(Permissions.ModifyPortalContent, [], 0)
      self.assertFalse(guarded_hasattr(obj, 'setFooBarList'))
      self.assertTrue(guarded_hasattr(obj, 'getFooBarList'))
      
      # getter is protected with Access content information
      obj.manage_permission(Permissions.ModifyPortalContent, ['Manager'], 1)
      obj.manage_permission(Permissions.AccessContentsInformation, [], 0)
      self.assertTrue(guarded_hasattr(obj, 'setFooBarList'))
      self.assertFalse(guarded_hasattr(obj, 'getFooBarList'))

    def test_DefaultSecurityOnCategoryAccessors(self):
      # Test category accessors are protected correctly
      obj = self.getPersonModule().newContent(portal_type='Person')
      self.assertTrue(guarded_hasattr(obj, 'setRegion'))
      self.assertTrue(guarded_hasattr(obj, 'setRegionValue'))
      self.assertTrue(guarded_hasattr(obj, 'setRegionList'))
      self.assertTrue(guarded_hasattr(obj, 'setRegionValueList'))
      self.assertTrue(guarded_hasattr(obj, 'getRegion'))
      self.assertTrue(guarded_hasattr(obj, 'getRegionValue'))
      self.assertTrue(guarded_hasattr(obj, 'getRegionList'))
      self.assertTrue(guarded_hasattr(obj, 'getRegionValueList'))
      self.assertTrue(guarded_hasattr(obj, 'getRegionRelatedValueList'))
      # setter is protected by default with modify portal content
      obj.manage_permission(Permissions.ModifyPortalContent, [], 0)
      self.assertFalse(guarded_hasattr(obj, 'setRegion'))
      self.assertFalse(guarded_hasattr(obj, 'setRegionValue'))
      self.assertFalse(guarded_hasattr(obj, 'setRegionList'))
      self.assertFalse(guarded_hasattr(obj, 'setRegionValueList'))
      self.assertTrue(guarded_hasattr(obj, 'getRegion'))
      self.assertTrue(guarded_hasattr(obj, 'getRegionValue'))
      self.assertTrue(guarded_hasattr(obj, 'getRegionList'))
      self.assertTrue(guarded_hasattr(obj, 'getRegionValueList'))
      self.assertTrue(guarded_hasattr(obj, 'getRegionRelatedValueList'))
      # getter is protected with Access content information
      obj.manage_permission(Permissions.ModifyPortalContent, ['Manager'], 1)
      obj.manage_permission(Permissions.AccessContentsInformation, [], 0)
      self.assertTrue(guarded_hasattr(obj, 'setRegion'))
      self.assertTrue(guarded_hasattr(obj, 'setRegionValue'))
      self.assertTrue(guarded_hasattr(obj, 'setRegionList'))
      self.assertTrue(guarded_hasattr(obj, 'setRegionValueList'))
      self.assertFalse(guarded_hasattr(obj, 'getRegion'))
      self.assertFalse(guarded_hasattr(obj, 'getRegionValue'))
      self.assertFalse(guarded_hasattr(obj, 'getRegionList'))
      self.assertFalse(guarded_hasattr(obj, 'getRegionValueList'))
      self.assertFalse(guarded_hasattr(obj, 'getRegionRelatedValueList'))

    def test_PropertySheetSecurityOnAccessors(self):
      # Test accessors are protected correctly when you specify the permission
      # in the property sheet.
      self._addProperty('Person',
                  ''' { 'id':         'foo_bar',
                        'write_permission' : 'Set own password',
                        'read_permission'  : 'Manage users',
                        'type':       'string',
                        'mode':       'w', }''')
      obj = self.getPersonModule().newContent(portal_type='Person')
      self.assertTrue(guarded_hasattr(obj, 'setFooBar'))
      self.assertTrue(guarded_hasattr(obj, 'getFooBar'))
      
      obj.manage_permission('Set own password', [], 0)
      self.assertFalse(guarded_hasattr(obj, 'setFooBar'))
      self.assertTrue(guarded_hasattr(obj, 'getFooBar'))
      
      obj.manage_permission('Set own password', ['Manager'], 1)
      obj.manage_permission('Manage users', [], 0)
      self.assertTrue(guarded_hasattr(obj, 'setFooBar'))
      self.assertFalse(guarded_hasattr(obj, 'getFooBar'))

    def test_edit(self):
      self._addProperty('Person',
                        ''' { 'id':         'foo_bar',
                        'write_permission' : 'Set own password',
                        'read_permission'  : 'Manage users',
                        'type':       'string',
                        'mode':       'w', }''')
      obj = self.getPersonModule().newContent(portal_type='Person')
      obj.edit(foo_bar="v1")
      self.assertEqual(obj.getFooBar(), "v1")

      obj.manage_permission('Set own password', [], 0)
      self.assertRaises(Unauthorized, obj.edit, foo_bar="v2")
      self.assertEqual(obj.getFooBar(), "v1")

      obj._edit(foo_bar="v3")
      self.assertEqual(obj.getFooBar(), "v3")

    def test_accessor_security_and_getTitle_acquisition(self):
      obj = self.getOrganisationModule().newContent(portal_type='Organisation')
      self.assertTrue(guarded_hasattr(obj, 'getTitle'))
      # getTitle__roles__ is defined on ERP5Site class, so it can be acquired,
      # and this would be wrong
      obj.manage_permission(Permissions.View, [], 0)
      obj.manage_permission(Permissions.AccessContentsInformation, [], 0)
      self.assertFalse(guarded_hasattr(obj, 'getTitle'))

    def test_AddPermission(self):
      # test "Add permission" on ERP5 Type Information
      self.portal.portal_types.manage_addTypeInformation(
            add_meta_type='ERP5 Type Information',
            id='Test Add Permission Document',
            typeinfo_name='ERP5Type: Document (ERP5 Document)')

      type_info = self.portal.portal_types.getTypeInfo(
                        'Test Add Permission Document')
      
      # allow this type info in Person Module
      container_type_info = self.portal.portal_types.getTypeInfo('Person Module')
      container_type_info.allowed_content_types = tuple(
              container_type_info.allowed_content_types) + (
              'Test Add Permission Document', )

      # by default this is empty, which implictly means "Add portal content",
      # the default permission
      self.assertEqual(type_info.permission, '')

      container = self.portal.person_module

      self.assertTrue(getSecurityManager().getUser().has_permission(
                      'Add portal content', container))
      self.assertTrue(type_info in container.allowedContentTypes())
      container.newContent(portal_type='Test Add Permission Document')

      container.manage_permission('Add portal content', [], 0)
      self.assertFalse(type_info in container.allowedContentTypes())
      self.assertRaises(Unauthorized, container.newContent,
                        portal_type='Test Add Permission Document')
      
      type_info.permission = 'Manage portal'
      container.manage_permission('Manage portal', [], 0)
      self.assertFalse(type_info in container.allowedContentTypes())
      self.assertRaises(Unauthorized, container.newContent,
                        portal_type='Test Add Permission Document')

      container.manage_permission('Manage portal', ['Anonymous'], 0)
      self.assertTrue(type_info in container.allowedContentTypes())
      container.newContent(portal_type='Test Add Permission Document')

    def testPropertyListWithMonoValuedProperty(self):
      """
      Check that we can use setPropertyList and getPropertyList
      on a mono valued property
      """
      self._addProperty('Person',
                  ''' { 'id':         'foo_bar',
                        'type':       'string',
                        'mode':       'rw', }''')
      person = self.getPersonModule().newContent(portal_type='Person')
      email = person.newContent(portal_type='Email')
      self.assertEquals(None, getattr(person, 'getFooBarList', None))
      self.assertEquals(person.getFooBar(), None)
      self.assertFalse(person.hasProperty('foo_bar'))
      self.assertEquals(person.getProperty('foo_bar'), None)
      self.assertEquals(person.getPropertyList('foo_bar'), [None])
      person.setFooBar('foo')
      self.assertEquals(person.getProperty('foo_bar'), 'foo')
      self.assertEquals(person.getPropertyList('foo_bar'), ['foo'])
      person.setFooBar(None)
      self.assertEquals(person.getProperty('foo_bar'), None)
      person.setPropertyList('foo_bar', ['bar'])
      self.assertEquals(person.getProperty('foo_bar'), 'bar')
      self.assertEquals(person.getPropertyList('foo_bar'), ['bar'])
      self.assertRaises(TypeError, person.setPropertyList, 'foo_bar', 
                        ['a', 'b'])

    def testPropertyListOnMonoValuedAcquiredProperty(self,quiet=quiet, run=run_all_test):
      """
      Check that we can use setPropertyList and getPropertyList
      on a mono valued acquired property
      """
      self._addProperty('Person',
                  ''' { 'id':         'foo_bar',
                        'type':       'string',
                        'mode':       'rw', }''')
      self._addProperty('Email',
                  ''' { 'id':         'foo_bar',
                        'type':       'string',
                        'acquired_property_id': ('description', ),
                        'acquisition_base_category': ( 'parent', ),
                        'acquisition_portal_type'  : ( 'Person', ),
                        'acquisition_copy_value'   : 0,
                        'acquisition_mask_value'   : 1,
                        'acquisition_accessor_id'  : 'getFooBar',
                        'acquisition_depends'      : None,
                        'mode':       'rw', }''')
      person = self.getPersonModule().newContent(portal_type='Person')
      email = person.newContent(portal_type='Email')
      self.assertEquals(email.getPropertyList('foo_bar'), [None])
      person.setPropertyList('foo_bar', ['foo'])
      self.assertEquals(email.getPropertyList('foo_bar'), ['foo'])
      email.setPropertyList('foo_bar', ['bar'])
      self.assertEquals(email.getPropertyList('foo_bar'), ['bar'])
      email.setPropertyList('foo_bar', [None])
      self.assertEquals(email.getPropertyList('foo_bar'), ['foo'])
      person.setPropertyList('foo_bar', [None])
      self.assertEquals(email.getPropertyList('foo_bar'), [None])

    def testPropertyListWithMultiValuedProperty(self):
      """
      Check that we can use setPropertyList and getPropertyList
      on a multi valued property
      """
      self._addProperty('Person',
                  ''' { 'id':         'foo_bar',
                        'type':       'string',
                        'multivalued': 1,
                        'mode':       'rw', }''')
      person = self.getPersonModule().newContent(portal_type='Person')
      # We have None, like test_list_accessors
      self.assertEquals(person.getFooBarList(), None)
      self.assertEquals(person.getPropertyList('foo_bar'), None)
      person.setPropertyList('foo_bar', ['foo', 'bar'])
      self.assertEquals(person.getPropertyList('foo_bar'), ['foo', 'bar'])
      person.setPropertyList('foo_bar', [])
      self.assertEquals(person.getFooBarList(), [])

    def testUndefinedProperties(self):
      """
      Make sure that getProperty and setProperty on a property not defined
      in a propertysheet is working properly.
      """
      person = self.getPersonModule().newContent(portal_type='Person')
      self.assertEquals(person.getProperty('foo_bar'), None)
      person.setProperty('foo_bar', 'foo')
      self.assertEquals(person.getProperty('foo_bar'), 'foo')
      self.assertEquals(person.getPropertyList('foo_bar_list'), None)
      person.setProperty('foo_bar_list', ['foo', 'bar'])
      self.assertEquals(list(person.getProperty('foo_bar_list')), ['foo', 'bar'])

    def test_objectValues_contentValues(self):
      """
      Test checked_permission parameter on Folder.objectValues and
      Folder.contentValues.
      Also test that there is no difference between objectValues and
      contentValues about security.
      """
      person = self.getPersonModule().newContent(portal_type='Person')
      address = person.newContent(portal_type='Address')

      def check(count):
        for values in person.objectValues, person.contentValues:
          self.assertEqual(1, len(values()))
          self.assertEqual(count, len(values(checked_permission='View')))
      check(1)

      for permission in 'View', 'Access contents information':
        address.manage_permission(permission, roles=(), acquire=0)
        check(0)

    def test_unsupportedTransitionRaises(self):
      """
      Check that an object must be in the expected state in order to execute
      a transition.
      """
      person = self.getPersonModule().newContent(portal_type='Person')
      person.validate()
      self.assertRaises(WorkflowException, person.validate)


class TestAccessControl(ERP5TypeTestCase):
  # Isolate test in a dedicaced class in order not to break other tests
  # when this one fails.
  expression = 'python: here.getPortalType() or 1'

  def getTitle(self):
    return "ERP5Type"

  def getBusinessTemplateList(self):
    return 'erp5_base',

  def afterSetUp(self):
    self.login()

    self.getCatalogTool().getSQLCatalog().filter_dict['z_catalog_object_list'] \
      = dict(filtered=1, type=[], expression=self.expression,
             expression_instance=Expression(self.expression))

    createZODBPythonScript(self.getSkinsTool().custom,
                           'Base_immediateReindexObject',
                           '',
                           'context.immediateReindexObject()'
                          ).manage_proxy(('Manager',))

  def test(self):
    self.getPortal().person_module.newContent().Base_immediateReindexObject()


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Type))
  suite.addTest(unittest.makeSuite(TestAccessControl))
  return suite
