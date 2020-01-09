# -*- coding: utf-8 -*-
##############################################################################
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

try:
  from ZODB._compat import cPickle
except ImportError: # BBB: ZODB < 4
  import cPickle
import unittest
import sys
import mock

import transaction
from random import randint
from unittest import expectedFailure
from Acquisition import aq_base
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import DummyLocalizer
from zLOG import INFO
from zExceptions import Forbidden
from Products.CMFCore.Expression import Expression
from Products.ERP5Type.tests.utils import LogInterceptor
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
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
  def beforeTearDown(self):
    """Clean up """
    ttool = self.getTypesTool()
    # remove all property sheet we added to type informations
    for ti_name, psheet_list in getattr(self, '_added_property_sheets',
                                   {}).items():
      ti = ttool.getTypeInfo(ti_name)
      property_sheet_set = set(ti.getTypePropertySheetList())
      for psheet in psheet_list:
        if psheet in property_sheet_set:
          property_sheet_set.remove(psheet)
      ti._setTypePropertySheetList(list(property_sheet_set))
    # this is useful if somehow the interaction workflows is set
    # wrongly. If the interaction has been called already it does nothing,
    # but in the other hand, if isolates the test "just in case"
    ttool.resetDynamicDocumentsOnceAtTransactionBoundary()
    self.tic()
    super(PropertySheetTestCase, self).beforeTearDown()

  def _addProperty(self, portal_type_name, property_sheet_id,
                   property_id=None,
                   commit=True, **kw):
    """quickly add a property to a type

    It always associate / create the property sheet with id
    property_sheet_id to the portal type portal_type_name.

    When property_sheet_id is passed, we create a property of this
    id, using kw** as parameters to the constructor.
    """

    ps = self._addPropertySheet(portal_type_name,
                                property_sheet_name=property_sheet_id)

    if property_id is not None:
      if "\n" in property_id:
        raise ValueError("Please update this test to use ZODB property sheets")

      self.assertTrue('portal_type' in kw, "You need to specify the portal_type"
          " you want to use to create that new property")

      suffix = ps.newContent(temp_object=1, **kw).getIdAsReferenceSuffix()
      property_id_as_reference = property_id + suffix
      property = getattr(ps, property_id_as_reference, None)
      if property is not None:
        ps._delObject(property_id_as_reference)

      property = ps.newContent(reference=property_id, **kw)
    if commit:
      self.commit()

class TestERP5Type(PropertySheetTestCase, LogInterceptor):
    """Tests ERP5TypeInformation and per portal type generated accessors.
    """
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
      self.commit()

      # save workflow chain for Person type
      self.person_chain = self.getWorkflowTool().getChainFor('Person')

    def beforeTearDown(self):
      self.abort()
      # THIS IS UGLY, WE MUST REMOVE AS SOON AS POSSIBLE, NOT COMPATIBLE
      # WITH LIVE TEST
      for module in [ self.getPersonModule(),
                      self.getOrganisationModule(),
                      self.getCategoryTool().region ]:
        module.manage_delObjects(list(module.objectIds()))

      # set Person.acquire_local_roles back.
      if getattr(self, 'person_acquire_local_roles', None) is not None:
        self.getTypesTool().getTypeInfo('Person').setTypeAcquireLocalRole(self.person_acquire_local_roles)

      # restore workflows for other tests
      self.getWorkflowTool().setChainForPortalTypes(
        ['Person'], self.person_chain)

      super(TestERP5Type, self).beforeTearDown()

    def loginWithNoRole(self):
      uf = self.portal.acl_users
      uf._doAddUser('ac', '', [], [])
      user = uf.getUserById('ac').__of__(uf)
      newSecurityManager(None, user)

    def getRandomString(self):
      return str(randint(-10000000,100000000))

    def testTemplateToolHasGetId(self):
      # Test if portal_templates has getId method (RAD)
      self.assertEqual(self.getTemplateTool().getId(), 'portal_templates')

    def testCategoryToolHasGetId(self):
      # Test if portal_categories has getId method (RAD)
      self.assertEqual(self.getCategoryTool().getId(), 'portal_categories')

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
      self.assertEqual(business_template.getPortalType(), 'Business Template')
      # Test simple string accessor
      test_string = self.getRandomString()
      business_template.setTitle(test_string)
      self.assertEqual(business_template.getTitle(), test_string)

    # Test Dynamic Code Generation
    def test_02_AqDynamic(self):
      module = self.getPersonModule()
      person = module.newContent(id='1', portal_type='Person')
      from Products.ERP5Type.Document import Person
      # Person class should have no method getFirstName
      self.assertFalse(hasattr(Person.Person, 'getFirstName'))
      # Calling getFirstName should produce dynamic methods related to the
      # portal_type
      name = person.getFirstName()
      # Person class should have no method getFirstName
      self.assertFalse(hasattr(Person.Person, 'getFirstName'))
      # Person class should now have method getFirstName
      self.assertTrue(hasattr(person, 'getFirstName'))

    def test_03_NewTempObject(self):
      portal = self.portal

      # WARNING: `newTemp<PortalType>(self, ID)` is deprecated in favor of
      # `self.newContent(portal_type=<PortalType>, temp_object=True, id=ID)`
      from Products.ERP5Type.Document import newTempPerson
      o = newTempPerson(portal, 1.2)
      o.setTitle('toto')
      self.assertEqual(o.getTitle(), 'toto')
      self.assertEqual(str(o.getId()), str(1.2))

      from Products.ERP5Type.Document import newTempOrganisation
      o = newTempOrganisation(portal, -123)
      o.setTitle('toto')
      self.assertEqual(o.getTitle(), 'toto')
      self.assertEqual(str(o.getId()), str(-123))

      # Try to edit with any property and then get it with getProperty
      o = newTempOrganisation(portal,'a')
      o.edit(tutu='toto')
      self.assertEqual(o.getProperty('tutu'), 'toto')

      # Same thing with an integer
      o = newTempOrganisation(portal,'b')
      o.edit(tata=123)
      self.assertEqual(o.getProperty('tata'), 123)

      # Make sure this is a Temp Object
      self.assertEqual(o.isTempObject(), 1)

      # Create a subobject and make sure it is a Temp Object
      a = o.newContent(portal_type = 'Telephone')
      self.assertEqual(a.isTempObject(), 1)

      # Test newContent with the temp_object parameter
      o = portal.person_module.newContent(id=987, portal_type="Person", temp_object=1)
      o.setTitle('bar')
      self.assertEqual(o.getTitle(), 'bar')
      self.assertEqual(str(o.getId()), str(987))
      self.assertEqual(o.isTempObject(), 1)
      a = o.newContent(id=1, portal_type="Telephone", temp_object=1)
      self.assertEqual(str(a.getId()), str(1))
      self.assertEqual(a.isTempObject(), 1)
      b = o.newContent(id=2, portal_type="Telephone")
      self.assertEqual(b.isTempObject(), 1)
      self.assertEqual(b.getId(), str(2))

      # Test newContent with the temp_object parameter and without ID
      o = portal.person_module.newContent(portal_type="Person", temp_object=1)
      o.setTitle('bar')
      self.assertEqual(o.getTitle(), 'bar')
      self.assertEqual(o.isTempObject(), 1)
      a = o.newContent(id=1, portal_type="Telephone", temp_object=1)
      self.assertEqual(str(a.getId()), str(1))
      self.assertEqual(a.isTempObject(), 1)
      b = o.newContent(id=2, portal_type="Telephone")
      self.assertEqual(b.isTempObject(), 1)
      self.assertEqual(b.getId(), str(2))

      # Test newContent with the temp_object parameter on the Portal
      o = portal.newContent(portal_type="Person", temp_object=1)
      o.setTitle('bar')
      self.assertEqual(o.getTitle(), 'bar')
      self.assertEqual(o.isTempObject(), 1)
      a = o.newContent(id=1, portal_type="Telephone", temp_object=1)
      self.assertEqual(str(a.getId()), str(1))
      self.assertEqual(a.isTempObject(), 1)
      b = o.newContent(id=2, portal_type="Telephone")
      self.assertEqual(b.isTempObject(), 1)
      self.assertEqual(b.getId(), str(2))

      # Test newContent with the temp_object parameter and where a non-temp_object would not be allowed
      o = portal.person_module.newContent(portal_type="Organisation", temp_object=1)
      o.setTitle('bar')
      self.assertEqual(o.getTitle(), 'bar')
      self.assertEqual(o.isTempObject(), 1)
      a = o.newContent(id=1, portal_type="Telephone", temp_object=1)
      self.assertEqual(str(a.getId()), str(1))
      self.assertEqual(a.isTempObject(), 1)
      b = o.newContent(id=2, portal_type="Telephone")
      self.assertEqual(b.isTempObject(), 1)
      self.assertEqual(b.getId(), str(2))

      # check we can create temp object without specific roles/permissions
      self.logout()
      self.loginWithNoRole()
      ## newTemp<PORTAL_TYPE>
      o = newTempOrganisation(portal.organisation_module,'b')
      self.assertEqual(o.isTempObject(), 1)
      a = o.newContent(portal_type = 'Telephone')
      self.assertEqual(a.isTempObject(), 1)
      self.assertEqual(a, guarded_getattr(o, a.getId()))
      ## newContent
      o = portal.organisation_module.newContent(portal_type='Organisation',
                                                temp_object=1)
      self.assertEqual(o.isTempObject(), 1)
      a = o.newContent(portal_type = 'Telephone')
      self.assertEqual(a.isTempObject(), 1)
      self.assertEqual(a, guarded_getattr(o, a.getId()))
      self.logout()
      self.login()

      # Check that temp object creation do not write in the ZODB
      class WriteError(Exception):
        pass
      def _setLastId(self, id):
        raise WriteError
      portal.person_module.__class__._setLastId = _setLastId
      try:
        o = portal.person_module.newContent(portal_type="Person", temp_object=1)
      except WriteError:
        self.fail("Container last ID modified")
      finally:
        del portal.person_module.__class__._setLastId

      # the module is not changed from ZODB point of view
      self.assertFalse(portal.person_module._p_changed)
      # the object is not in ZODB
      self.assertEqual(o._p_jar, None)
      self.commit()
      self.assertEqual(o._p_jar, None)

      # Temp objects always get a dummy ID by default.
      o = portal.person_module.newContent(portal_type="Person",
                                          temp_object=1)
      first_id = o.getId()
      o = portal.person_module.newContent(portal_type="Person",
                                          temp_object=1)
      second_id = o.getId()
      self.assertEqual(first_id, second_id)
      self.assertEqual('None', second_id)

      # Make sure a temp object can't be stored in the ZODB
      portal.person_module._setObject(o.getId(), aq_base(o))
      try:
        self.commit()
      except cPickle.PicklingError:
        self.abort()
      else:
        self.fail("No exception raised when storing explicitly a temp object"
                  " on a persistent object")

      # Check temp objects subobjects can be accessed with OFS API
      parent = portal.person_module.newContent(portal_type="Person",
                                               temp_object=1)
      child1 = parent.newContent(portal_type='Person', id='1')
      child11 = child1.newContent(portal_type='Person', id='1')
      child2 = parent.newContent(portal_type='Person', id='2')

      self.assertEqual(child1, parent._getOb('1'))
      self.assertEqual(child2, parent._getOb('2'))

      self.assertEqual(child1, parent['1'])
      self.assertEqual(child2, parent['2'])

      self.assertEqual(child1, getattr(parent, '1'))
      self.assertEqual(child2, getattr(parent, '2'))

      self.assertEqual(child1, parent.restrictedTraverse('1'))
      self.assertEqual(child11, parent.restrictedTraverse('1/1'))
      self.assertEqual(child2, parent.restrictedTraverse('2'))

      self.assertEqual(('person_module', 'None', '1', '1'),
          self.portal.portal_url.getRelativeContentPath(child11))


    def test_04_CategoryAccessors(self):
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
      region_category = self.portal.portal_categories.region

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
        self.commit()
        person_object.reindexObject()
        category_object.reindexObject()
        self.tic()
        self.assertEqual( person_object.getRegion(), category_id)
        self.assertEqual( person_object.getRegion(base=1), category_relative_url)
        self.assertEqual( person_object.getRegionValue(), category_object)
        self.assertEqual( person_object.getRegionId(), category_id)
        self.assertEqual( person_object.getRegionTitle(), category_title)
        self.assertEqual( category_object.getRegionRelatedValueList(
                            portal_type = "Person"), [person_object] )
        self.assertEqual( category_object.getRegionRelatedTitleList(
                            portal_type = "Person"), [person_title] )
        self.assertEqual( category_object.getRegionRelatedTitleSet(
                            portal_type = "Person"), [person_title] )
        self.assertEqual( category_object.getRegionRelatedList(
                            portal_type = "Person"), [person_relative_url] )
        self.assertEqual( category_object.getRegionRelatedIdList(
                            portal_type = "Person"), [person_id] )
        self.assertEqual( category_object.getRegionRelatedIdSet(
                            portal_type = "Person"), [person_id] )

      def checkRelationUnset(self):
        self.commit()
        person_object.reindexObject()
        category_object.reindexObject()
        self.tic()
        self.assertEqual( person_object.getRegion(), None)
        self.assertEqual( person_object.getRegionValue(), None)
        self.assertEqual( person_object.getRegionId(), None)
        self.assertEqual( person_object.getRegionTitle(), None)
        self.assertEqual( category_object.getRegionRelatedValueList(
                            portal_type = "Person"), [] )
        self.assertEqual( category_object.getRegionRelatedTitleList(
                            portal_type = "Person"), [] )
        self.assertEqual( category_object.getRegionRelatedList(
                            portal_type = "Person"), [] )
        self.assertEqual( category_object.getRegionRelatedIdList(
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
      self.commit()
      self.assertFalse(person_object.hasActivity())
      person_object.setRegion(None)
      self.commit()
      self.assertTrue(person_object.hasActivity())
      self.tic()

      # category tool, base categories, properties
      # are likely to be handled specifically for accessor generation,
      # since they are the first portal types to be loaded.
      # double-check that they also have group accessors
      category_tool = self.portal.portal_categories.aq_inner
      method = getattr(category_tool, 'getRegionRelatedList', None)
      self.assertNotEquals(None, method)

      region_category = category_tool.region.aq_inner
      method = getattr(region_category, 'getRegionRelatedList', None)
      self.assertNotEquals(None, method)

      property_sheet_tool = self.portal.portal_property_sheets
      person_property_sheet = property_sheet_tool.Person.aq_inner
      method = getattr(person_property_sheet, 'getRegionRelatedList', None)
      self.assertNotEquals(None, method)


    def test_05_setProperty(self):
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
      module = self.getOrganisationModule()
      organisation = module.newContent(id='1', portal_type='Organisation')
      organisation.setDefaultTelephoneText('+55(0)66-5555')
      self.assertEqual(organisation.default_telephone.getTelephoneCountry(),'55')
      self.assertEqual(organisation.default_telephone.getTelephoneArea(),'66')
      self.assertEqual(organisation.default_telephone.getTelephoneNumber(),'5555')
      organisation.setCorporateName('Nexedi')
      #self.assertEqual(organisation.default_telephone.getProperty('corporate_name'),'Nexedi') # Who is right ? XXX
      organisation.default_telephone.setProperty('corporate_name','Toto')
      self.assertEqual(organisation.corporate_name,'Nexedi')
      self.assertEqual(organisation.default_telephone.getCorporateName(),'Nexedi')
      self.assertEqual(organisation.default_telephone.corporate_name,'Toto')
      self.assertEqual(organisation.default_telephone.getProperty('corporate_name'),'Toto')

    def test_06_CachingMethod(self):
      """Tests Caching methods."""
      cached_var = cached_var_orig = 'cached_var1'

      def _cache():
        return cached_var

      from Products.ERP5Type.Cache import CachingMethod
      cache = CachingMethod(_cache, id='testing_cache')

      self.assertEqual(cache(), cached_var)

      # change the variable
      cached_var = 'cached_var (modified)'
      # cache hit -> still the old variable
      self.assertEqual(cache(), cached_var_orig)

      self.portal.portal_caches.clearCache()
      self.assertEqual(cache(), cached_var)

    def test_07_afterCloneScript(self):
      """manage_afterClone can call a type based script."""
      # setup the script for Person portal type
      custom_skin = self.portal.portal_skins.custom
      method_id = 'Person_afterClone'
      if method_id in custom_skin.objectIds():
        custom_skin.manage_delObjects([method_id])

      custom_skin.manage_addProduct['PythonScripts']\
                    .manage_addPythonScript(id = method_id)
      script = custom_skin[method_id]
      script.ZPythonScript_edit('', "context.setTitle('reseted')")
      self.portal.changeSkin(None)

      # copy / pasted person have their title reseted
      folder = self.getPersonModule()
      pers = folder.newContent(portal_type='Person',
                              title='something', )
      copy_data = folder.manage_copyObjects([pers.getId()])
      new_id = folder.manage_pasteObjects(copy_data)[0]['new_id']
      new_pers = folder[new_id]
      self.assertEqual(new_pers.getTitle(), 'reseted')

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
      self.assertEqual(new_pers.default_address.getTitle(),
                        'address_title_reseted')

      # of course, other portal types are not affected
      folder = self.getOrganisationModule()
      orga = folder.newContent(portal_type='Organisation',
                              title='something', )
      copy_data = folder.manage_copyObjects([orga.getId()])
      new_id = folder.manage_pasteObjects(copy_data)[0]['new_id']
      new_orga = folder[new_id]
      self.assertEqual(new_orga.getTitle(), 'something')

    def test_08_AccessorGeneration(self):
      """Tests accessor generation doesn't generate error messages.
      """
      self.portal.portal_types.resetDynamicDocuments()
      self._catch_log_errors(ignored_level=INFO)
      try:
        folder = self.getOrganisationModule()
        orga = folder.newContent(portal_type='Organisation',)
        # call an accessor, _aq_dynamic will generate accessors
        orga.getId()
      finally:
        self._ignore_log_errors()

    def test_09_RenameObjects(self):
      """Test object renaming.

         As we overloaded some parts of OFS, it's better to test again some basic
         features.
      """
      folder = self.getOrganisationModule()
      id_list = [chr(x) for x in range(ord('a'), ord('z')+1)]
      for id_ in id_list:
        folder.newContent(portal_type='Organisation', id=id_)
      # commit a subtransaction, so that we can rename objecs (see
      # OFS.ObjectManager._getCopy)
      transaction.savepoint(optimistic=True)

      for obj in folder.objectValues():
        new_id = '%s_new' % obj.getId()
        folder.manage_renameObjects([obj.getId()], [new_id])
        self.assertEqual(obj.getId(), new_id)

      for obj_id in folder.objectIds():
        self.assertTrue(obj_id.endswith('_new'),
                        'bad object id: %s' % obj_id)
      for id_ in id_list:
        new_id = '%s_new' % id_
        self.assertEqual(folder._getOb(new_id).getId(), new_id)

    def test_11_valueAccessor(self):
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
      # Create a few categories
      region_category = self.portal.portal_categories.region
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
      function_category = self.portal.portal_categories.function
      nofunction = function_category.newContent(
              portal_type = "Category",
              id =          "nofunction",
              title =       "No Function", )

      self.assertEqual(alpha.getRelativeUrl(), 'region/alpha')

      alpha.reindexObject()
      beta.reindexObject()
      zeta.reindexObject()
      nofunction.reindexObject()
      self.tic()# Make sure categories are reindexed

      # Create a new person
      module = self.getPersonModule()
      person = module.newContent(portal_type='Person')

      # Value setters (list, set, default)
      person.setFunction('nofunction')  # Fill at least one other category
      person.setDefaultRegionValue(alpha)
      self.assertEqual(person.getDefaultRegion(), 'alpha')
      self.assertEqual(person.getRegion(), 'alpha')
      person.setRegionValue(alpha)
      self.assertEqual(person.getRegion(), 'alpha')
      person.setRegionValueList([alpha, alpha])
      self.assertEqual(person.getRegionList(), ['alpha', 'alpha'])
      person.setRegionValueSet([alpha, alpha])
      self.assertEqual(person.getRegionList(), ['alpha'])
      self.assertEqual(person.getRegionSet(), ['alpha'])
      person.setRegionValueList([beta, alpha, beta])
      self.assertEqual(person.getRegionList(), ['beta', 'alpha', 'beta'])
      self.assertEqual(person.getRegionSet(), ['beta', 'alpha']) # Order is kept in Set getter.
      self.assertEqual(person.getRegionValueSet(), [beta, alpha]) # Order is kept in Set getter.
      person.setRegionValueList([alpha, beta, alpha])
      self.assertEqual(person.getRegionList(), ['alpha', 'beta', 'alpha'])
      self.assertEqual(person.getRegionSet(), ['alpha', 'beta'])
      self.assertEqual(person.getRegionValueSet(), [alpha, beta])
      person.setRegionValueSet([alpha, beta, alpha])
      self.assertEqual(person.getRegionList(), ['alpha', 'beta'])
      person.setRegionValueSet([beta, alpha, zeta, alpha])
      self.assertEqual(person.getRegionList(), ['alpha', 'beta', 'zeta']) # Default is kept, then order is kept in Set setter.
      person.setDefaultRegionValue(beta)
      self.assertEqual(person.getDefaultRegion(), 'beta')
      self.assertEqual(person.getRegionList(), ['beta', 'alpha', 'zeta'])
      person.setRegion(None)
      person.setRegionValueSet([beta, alpha, alpha])
      self.assertEqual(person.getRegionList(), ['beta', 'alpha'])
      person.setDefaultRegionValue(alpha)
      self.assertEqual(person.getDefaultRegion(), 'alpha')
      self.assertEqual(person.getRegionSet(), ['alpha', 'beta'])
      self.assertEqual(person.getRegionList(), ['alpha', 'beta'])
      # Test accessor on documents rather than on categories
      person.setDefaultRegionValue(person)
      self.assertEqual(person.getDefaultRegion(), person.getRelativeUrl())
      self.assertEqual(person.getRegionList(), [person.getRelativeUrl(), 'alpha', 'beta'])
      person.setRegionValue([person, alpha, beta])
      self.assertEqual(person.getRegionList(), [person.getRelativeUrl(), 'alpha', 'beta'])

      # Category setters (list, set, default)
      person = module.newContent(portal_type='Person')
      person.setFunction('nofunction')  # Fill at least one other category
      person.setDefaultRegion('alpha')
      self.assertEqual(person.getRegion(), 'alpha')
      self.assertEqual(person.getDefaultRegion(), 'alpha')
      person.setRegion('alpha')
      self.assertEqual(person.getRegion(), 'alpha')
      person.setRegionList(['alpha', 'alpha'])
      self.assertEqual(person.getRegionList(), ['alpha', 'alpha'])
      self.assertEqual(person.getRegionSet(), ['alpha'])
      person.setRegionSet(['beta', 'alpha', 'zeta', 'alpha'])
      self.assertEqual(person.getRegionList(), ['alpha', 'beta', 'zeta'])
      person.setRegionList(['beta', 'alpha', 'alpha'])
      self.assertEqual(person.getRegionList(), ['beta', 'alpha', 'alpha'])
      # at this point the person have a default region set to the first item in
      # the list.
      self.assertEqual(person.getDefaultRegion(), 'beta')
      person.setRegionSet(['alpha', 'beta', 'alpha'])
      self.assertEqual(person.getRegionList(), ['beta', 'alpha'])
      # calling a set setter did not change the default region
      self.assertEqual(person.getDefaultRegion(), 'beta')

      person.setDefaultRegion('alpha')
      self.assertEqual(person.getDefaultRegion(), 'alpha')
      self.assertEqual(sorted(person.getRegionSet()), ['alpha', 'beta'])
      self.assertEqual(person.getRegionList(), ['alpha', 'beta'])
      person.setDefaultRegion('beta')
      self.assertEqual(person.getDefaultRegion(), 'beta')
      self.assertEqual(sorted(person.getRegionSet()), ['alpha', 'beta'])
      self.assertEqual(person.getRegionList(), ['beta', 'alpha'])
      # Test accessor on documents rather than on categories
      person.setDefaultRegion(person.getRelativeUrl())
      self.assertEqual(person.getDefaultRegion(), person.getRelativeUrl())
      self.assertEqual(person.getRegionList(), [person.getRelativeUrl(), 'beta', 'alpha'])
      person.setRegion([person.getRelativeUrl(), 'alpha', 'beta'])
      self.assertEqual(person.getRegionList(), [person.getRelativeUrl(), 'alpha', 'beta'])

      # Uid setters (list, set, default)
      person = module.newContent(portal_type='Person')
      person.reindexObject()
      self.tic()# Make sure person is reindexed
      person.setFunction('nofunction')  # Fill at least one other category
      person.setDefaultRegionUid(alpha.getUid())
      self.assertEqual(person.getRegion(), 'alpha')
      self.assertEqual(person.getDefaultRegion(), 'alpha')
      person.setRegionUid(alpha.getUid())
      self.assertEqual(person.getRegion(), 'alpha')
      person.setRegionUidList([beta.getUid(), beta.getUid()])
      self.assertEqual(person.getRegionList(), ['beta', 'beta'])
      person.setRegionUidSet([alpha.getUid(), alpha.getUid()])
      self.assertEqual(person.getRegionList(), ['alpha'])
      person.setRegionUidList([alpha.getUid(), beta.getUid(), alpha.getUid()])
      self.assertEqual(person.getRegionList(), ['alpha', 'beta', 'alpha'])
      person.setRegionUidSet([alpha.getUid(), beta.getUid(), alpha.getUid()])
      self.assertEqual(sorted(person.getRegionSet()), ['alpha', 'beta'])
      person.setDefaultRegionUid(beta.getUid())
      self.assertEqual(person.getDefaultRegion(), 'beta')
      self.assertEqual(sorted(person.getRegionSet()), ['alpha', 'beta'])
      self.assertEqual(person.getRegionList(), ['beta', 'alpha'])
      person.setDefaultRegionUid(alpha.getUid())
      self.assertEqual(person.getDefaultRegion(), 'alpha')
      self.assertEqual(sorted(person.getRegionSet()), ['alpha', 'beta'])
      self.assertEqual(person.getRegionList(), ['alpha', 'beta'])
      # Test accessor on documents rather than on categories
      person.setDefaultRegionUid(person.getUid())
      self.assertEqual(person.getDefaultRegion(), person.getRelativeUrl())
      self.assertEqual(person.getRegionList(), [person.getRelativeUrl(), 'alpha', 'beta'])
      person.setRegionUid([person.getUid(), alpha.getUid(), beta.getUid()])
      self.assertEqual(person.getRegionList(), [person.getRelativeUrl(), 'alpha', 'beta'])

    def test_12_listAccessor(self):
      """
      The purpose of this test is to make sure that accessor for
      sequence types support the same kind of semantics as the
      one on categories. We use 'subject' of the DublinCore propertysheet
      on organisation documents for this test.
      """
      # Create a new person
      module = self.getPersonModule()
      person = module.newContent(portal_type='Person')

      # Do the same tests as in test_11_valueAccessor
      person.setSubject('beta')
      self.assertEqual(person.getSubject(), 'beta')
      person.setSubjectList(['alpha', 'alpha'])
      self.assertEqual(person.getSubjectList(), ['alpha', 'alpha'])
      self.assertEqual(person.getSubjectSet(), ['alpha'])
      person.setSubjectSet(['beta', 'beta'])
      self.assertEqual(person.getSubjectList(), ['beta'])
      self.assertEqual(person.getSubjectSet(), ['beta'])
      person.setSubjectList(['beta', 'alpha', 'beta'])
      self.assertEqual(person.getSubjectList(), ['beta', 'alpha', 'beta'])
      person.setSubjectSet(['alpha', 'beta', 'alpha'])
      self.assertEqual(person.getSubjectList(), ['beta', 'alpha'])
      result = person.getSubjectSet()
      result.sort()
      self.assertEqual(result, ['alpha', 'beta'])
      person.setDefaultSubject('beta')
      self.assertEqual(person.getDefaultSubject(), 'beta')
      result = person.getSubjectSet()
      result.sort()
      self.assertEqual(result, ['alpha', 'beta'])
      self.assertEqual(person.getSubjectList(), ['beta', 'alpha'])
      person.setDefaultSubject('alpha')
      self.assertEqual(person.getDefaultSubject(), 'alpha')
      result = person.getSubjectSet()
      result.sort()
      self.assertEqual(result, ['alpha', 'beta'])
      self.assertEqual(person.getSubjectList(), ['alpha', 'beta'])

    def test_storage_id_accessor(self):
      self._addProperty('Person',
          self.id(),
          'foo_bar',
          elementary_type='string',
          storage_id='foo_bar_storage',
          portal_type='Standard Property')
      obj = self.getPersonModule().newContent(portal_type='Person')
      obj.setFooBar('foo')
      self.assertEqual('foo', obj.getFooBar())
      self.assertEqual('foo', getattr(obj, 'foo_bar_storage', 'unset'))
      obj.edit(foo_bar='bar')
      self.assertEqual('bar', obj.getFooBar())
      self.assertEqual('bar', getattr(obj, 'foo_bar_storage', 'unset'))

    def test_13_acquiredAccessor(self):
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

    def test_15_DefaultValue(self):
      """
      Tests that the default value is returned correctly
      """
      module = self.getPersonModule()
      person = module.newContent(id='1', portal_type='Person')

      def getFirstName(default=None):
        "dummy method to check default is passed correctly"
        return default

      person.getFirstName = getFirstName

      # test static method
      self.assertEqual(person.getFirstName(), None)
      self.assertEqual(person.getFirstName('foo'), 'foo')
      self.assertEqual(person.getFirstName(default='foo'), 'foo')
      # test dynamic method
      self.assertEqual(person.getLastName(), None)
      self.assertEqual(person.getLastName('foo'), 'foo')
      #self.assertEqual(person.getLastName(default='foo'), 'foo')
      # test static method through getProperty
      self.assertEqual(person.getProperty('first_name'), None)
      self.assertEqual(person.getProperty('first_name', 'foo'), 'foo')
      self.assertEqual(person.getProperty('first_name', d='foo'), 'foo')
      # test dynamic method through getProperty
      self.assertEqual(person.getProperty('last_name'), None)
      self.assertEqual(person.getProperty('last_name', 'foo'), 'foo')
      self.assertEqual(person.getProperty('last_name', d='foo'), 'foo')
      # test simple property through getProperty
      property_name = 'XXXthis_property_does_not_exist123123'
      self.assertEqual(person.getProperty(property_name), None)
      self.assertEqual(person.getProperty(property_name, 'foo'), 'foo')
      self.assertEqual(person.getProperty(property_name, d='foo'), 'foo')

    def test_15b_DefaultValueDefinedOnPropertySheet(self):
      """Tests that the default value is returned correctly when a default
      value is defined using the property sheet.
      """
      self._addProperty('Person',
          'test_15b_DefaultValueDefinedOnPropertySheet',
          'dummy_ps_prop',
          elementary_type='string',
          portal_type='Standard Property',
          property_default='python: "ps_default"')

      module = self.getPersonModule()
      person = module.newContent(id='1', portal_type='Person')
      # The default ps value will be returned, when using generated accessor
      self.assertEqual('ps_default', person.getDummyPsProp())
      # (unless you explicitly pass a default value.
      self.assertEqual('default', person.getDummyPsProp('default'))
      # using getProperty
      self.assertEqual('ps_default', person.getProperty('dummy_ps_prop'))
      self.assertEqual('default', person.getProperty('dummy_ps_prop', 'default'))

      # None can be a default value too
      self.assertEqual(None, person.getProperty('dummy_ps_prop', None))
      self.assertEqual(None, person.getDummyPsProp(None))

      # once the value has been set, there's no default
      value = 'a value'
      person.setDummyPsProp(value)
      self.assertEqual(value, person.getDummyPsProp())
      self.assertEqual(value, person.getDummyPsProp('default'))
      self.assertEqual(value, person.getProperty('dummy_ps_prop'))
      self.assertEqual(value, person.getProperty('dummy_ps_prop', d='default'))


    def test_15b_ListAccessorsDefaultValueDefinedOnPropertySheet(self):
      """Tests that the default value is returned correctly when a default
      value is defined using the property sheet, on list accesors.
      """
      self._addProperty('Person',
          'test_15b_ListAccessorsDefaultValueDefinedOnPropertySheet',
          'dummy_ps_prop',
          elementary_type='lines',
          portal_type='Standard Property',
          property_default='python: [1,2,3]')

      module = self.getPersonModule()
      person = module.newContent(id='1', portal_type='Person')
      # default accessor and list accessors are generated
      self.assertTrue(hasattr(person, 'getDummyPsProp'))
      self.assertTrue(hasattr(person, 'getDummyPsPropList'))

      # The default ps value will be returned, when using generated accessor
      self.assertEqual([1, 2, 3], person.getDummyPsPropList())
      # (unless you explicitly pass a default value.
      self.assertEqual(['default'], person.getDummyPsPropList(['default']))
      # using getProperty
      self.assertEqual([1, 2, 3], person.getProperty('dummy_ps_prop_list'))
      self.assertEqual(['default'],
                        person.getProperty('dummy_ps_prop_list', ['default']))

      # once the value has been set, there's no default
      value_list = ['some', 'values']
      person.setDummyPsPropList(value_list)
      self.assertEqual(value_list, person.getDummyPsPropList())
      self.assertEqual(value_list, person.getDummyPsPropList(['default']))
      self.assertEqual(value_list, person.getProperty('dummy_ps_prop_list'))
      self.assertEqual(value_list,
              person.getProperty('dummy_ps_prop_list', d=['default']))


    def test_15c_getDescriptionDefaultValue(self):
      """
      Tests that the default value of getDescription is returned correctly
      """
      person = self.getPersonModule().newContent(portal_type='Person')

      # test default value of getDescription accessor
      # as defined in the DublinCore PropertySheet
      self.assertEqual('', person.getDescription())
      self.assertEqual('foo',
                        person.getDescription('foo'))

    def test_16_SimpleStringAccessor(self):
      """Tests a simple string accessor.
      This is also a way to test _addProperty method """
      self._addProperty('Person',
          'test_16_SimpleStringAccessor',
          'dummy_ps_prop',
          elementary_type='string',
          portal_type='Standard Property')
      person = self.getPersonModule().newContent(id='1', portal_type='Person')
      self.assertEqual('string', person.getPropertyType('dummy_ps_prop'))
      self.assertTrue(hasattr(person, 'getDummyPsProp'))
      self.assertTrue(hasattr(person, 'setDummyPsProp'))
      person.setDummyPsProp('a value')
      self.assertTrue(person.hasProperty('dummy_ps_prop'))
      self.assertEqual('a value', person.getDummyPsProp())

      # string accessors converts the data type, if provided an unicode, it
      # will store an utf-8 encoded string
      person.setDummyPsProp(u'type convérsion')
      self.assertEqual('type convérsion', person.getDummyPsProp())
      # if provided anything else, it will store it's string representation
      person.setDummyPsProp(1)
      self.assertEqual('1', person.getDummyPsProp())

      class Dummy:
        def __str__(self):
          return 'string representation'
      person.setDummyPsProp(Dummy())
      self.assertEqual('string representation', person.getDummyPsProp())


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
      self.assertEqual('validation_state', wf.variables.getStateVar())
      initial_state = wf.states[wf.initial_state]
      other_state = wf.states['validated']

      self.assertTrue(hasattr(person, 'getValidationState'))
      self.assertTrue(hasattr(person, 'getValidationStateTitle'))
      self.assertTrue(hasattr(person, 'getTranslatedValidationStateTitle'))

      self.assertEqual(initial_state.getId(), person.getValidationState())
      self.assertEqual(initial_state.title,
                        person.getValidationStateTitle())
      self.assertEqual(initial_state.title,
                        person.getTranslatedValidationStateTitle())
      self.assertTrue([initial_state.title], message_catalog._translated)

      self.assertEqual(initial_state.getId(),
                        person.getProperty('validation_state'))
      self.assertEqual(initial_state.title,
                        person.getProperty('validation_state_title'))
      message_catalog._translated = []
      self.assertEqual(initial_state.title,
                        person.getProperty('translated_validation_state_title'))
      self.assertTrue([initial_state.title], message_catalog._translated)

      # default parameter is accepted by getProperty for compatibility
      self.assertEqual(initial_state.getId(),
                        person.getProperty('validation_state', 'default'))
      self.assertEqual(initial_state.title,
                        person.getProperty('validation_state_title', 'default'))
      message_catalog._translated = []
      self.assertEqual(initial_state.title,
                        person.getProperty('translated_validation_state_title',
                        'default'))
      self.assertTrue([initial_state.title], message_catalog._translated)

      # pass a transition and check accessors again.
      person.validate()
      self.assertEqual(other_state.getId(), person.getValidationState())
      self.assertEqual(other_state.title,
                        person.getValidationStateTitle())
      self.assertEqual(other_state.title,
                        person.getTranslatedValidationStateTitle())
      self.assertEqual(other_state.getId(),
                        person.getProperty('validation_state'))
      self.assertEqual(other_state.title,
                        person.getProperty('validation_state_title'))
      message_catalog._translated = []
      self.assertEqual(other_state.title,
                        person.getProperty('translated_validation_state_title'))
      self.assertTrue([other_state.title], message_catalog._translated)

    DEFAULT_ORGANISATION_TITLE_PROP = {
                        'portal_type': 'Acquired Property',
                        'storage_id': 'default_organisation',
                        'elementary_type':       'content',
                        'content_portal_type': 'python: (\'Organisation\', )',
                        'content_acquired_property_id': ('title', 'reference'), }

    def test_18_SimpleContentAccessor(self):
      """Tests a simple content accessor.
      This tests content accessors, for properties that have class methods.
      """
      # For testing purposes, we add a default_organisation inside a person,
      # and we add code to generate a 'default_organisation_title' property on
      # this person that will returns the organisation title.
      self._addProperty('Person',
          'test_18_SimpleContentAccessor',
          'organisation',
          **self.DEFAULT_ORGANISATION_TITLE_PROP)
      person = self.getPersonModule().newContent(id='1', portal_type='Person')
      self.assertTrue(getattr(person, 'getDefaultOrganisationTitle'))
      self.assertTrue(getattr(person, 'setDefaultOrganisationTitle'))
      self.assertTrue(getattr(person, 'hasDefaultOrganisationTitle'))
      self.assertTrue(getattr(person, 'hasOrganisationTitle'))
      self.assertFalse(person.hasDefaultOrganisation())
      self.assertFalse(person.hasOrganisation())
      self.assertFalse(person.hasDefaultOrganisationTitle())
      self.assertFalse(person.hasOrganisationTitle())
      person.setDefaultOrganisationTitle('The organisation title')
      # XXX content generated properties are not in propertyMap. is it a bug ?
      #self.assertTrue(person.hasProperty('default_organisation_title'))

      # an organisation is created inside the person.
      default_organisation = person._getOb('default_organisation', None)
      self.assertNotEquals(None, default_organisation)
      self.assertEqual('Organisation',
                        default_organisation.getPortalTypeName())
      self.assertEqual('The organisation title',
                        default_organisation.getTitle())
      self.assertTrue(person.hasDefaultOrganisation())
      self.assertTrue(person.hasOrganisation())
      self.assertTrue(person.hasDefaultOrganisationTitle())
      self.assertTrue(person.hasOrganisationTitle())
      # make sure this new organisation is indexed
      self.commit()
      self.assertEqual(1, len([m for m in
        self.portal.portal_activities.getMessageList()
        if m.method_id == 'immediateReindexObject'
            and m.object_path == default_organisation.getPhysicalPath()]))
      self.tic()

      # edit once again, this time no new organisation is created, the same is
      # edited, and reindexed
      self.assertEqual(1, len(person.objectIds()))
      self.assertFalse(person._p_changed)
      person.setDefaultOrganisationTitle('New title')
      self.assertEqual('New title',
                        default_organisation.getTitle())
      self.commit()
      self.assertEqual(1, len([m for m in
        self.portal.portal_activities.getMessageList()
        if m.method_id == 'immediateReindexObject'
            and m.object_path == default_organisation.getPhysicalPath()]))
      self.tic()

      # edit once again (this time, with edit method), this time no new
      # organisation is created, the same is edited, and reindexed
      self.assertEqual(1, len(person.objectIds()))
      self.assertFalse(person._p_changed)
      person.edit(default_organisation_title='New title 2')
      self.assertEqual('New title 2',
                        default_organisation.getTitle())
      self.assertEqual(0, len([m for m in
                        self.portal.portal_activities.getMessageList()]))
      self.commit()
      self.assertEqual(1, len([m for m in
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
      self._addProperty('Person',
          'test_18_SimpleContentAccessorWithGeneratedAccessor',
          'organisation',
          **self.DEFAULT_ORGANISATION_TITLE_PROP)
      person = self.getPersonModule().newContent(id='1', portal_type='Person')
      self.assertTrue(hasattr(person, 'getDefaultOrganisationReference'))
      self.assertTrue(hasattr(person, 'setDefaultOrganisationReference'))
      person.setDefaultOrganisationReference('The organisation ref')

      default_organisation = person._getOb('default_organisation', None)
      self.assertNotEquals(None, default_organisation)
      self.assertEqual('Organisation',
                        default_organisation.getPortalTypeName())
      self.assertEqual('The organisation ref',
                        default_organisation.getReference())

      # make sure this new organisation is indexed
      self.commit()
      self.assertEqual(1, len([m for m in
        self.portal.portal_activities.getMessageList()
        if m.method_id == 'immediateReindexObject'
            and m.object_path == default_organisation.getPhysicalPath()]))
      self.tic()

      # edit once again, this time no new organisation is created, the same is
      # edited, and reindexed
      self.assertEqual(1, len(person.objectIds()))
      self.assertFalse(person._p_changed)
      person.setDefaultOrganisationReference('New reference')
      self.assertEqual('New reference',
                        default_organisation.getReference())
      self.commit()
      self.assertEqual(1, len([m for m in
        self.portal.portal_activities.getMessageList()
        if m.method_id == 'immediateReindexObject'
            and m.object_path == default_organisation.getPhysicalPath()]))
      self.tic()

      # edit once again (this time, with edit method), this time no new
      # organisation is created, the same is edited, and reindexed
      self.assertEqual(1, len(person.objectIds()))
      self.assertFalse(person._p_changed)
      person.edit(default_organisation_reference='New reference 2')
      self.assertEqual('New reference 2',
                        default_organisation.getReference())
      self.assertEqual(0, len([m for m in
                        self.portal.portal_activities.getMessageList()]))
      self.commit()
      self.assertEqual(1, len([m for m in
        self.portal.portal_activities.getMessageList()
        if m.method_id == 'immediateReindexObject'
            and m.object_path == default_organisation.getPhysicalPath()]))
      self.tic()


    def test_18b_ContentAccessorWithIdClash(self):
      """Tests a content setters do not set the property on acquired object
      that may have the same id, using same scenario as test_18
      Note that we only test Setter for now.
      """
      self._addProperty('Person',
          'test_18b_ContentAccessorWithIdClash',
          'organisation',
          **self.DEFAULT_ORGANISATION_TITLE_PROP)
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
      self.assertEqual('The organisation title',
                        person.getDefaultOrganisationTitle())

    DEFAULT_ORGANISATION_TITLE_ACQUIRED_PROP = {
            'portal_type': 'Acquired Property',
            'storage_id': 'default_organisation',
            'elementary_type':       'content',
            'content_portal_type': "python: ('Organisation', )",
            'content_acquired_property_id': ('title', ),
            'acquisition_base_category': ( 'destination', ),
            'acquisition_portal_type'  : "python: ( 'Person', )",
            'acquisition_accessor_id'  : 'getDefaultOrganisationValue',
            'acquisition_copy_value'   : 0,
            'acquisition_mask_value'   : 1
    }

    def test_19_AcquiredContentAccessor(self):
      """Tests an acquired content accessor.
      """
      # For testing purposes, we add a default_organisation inside a person,
      # and we add code to generate a 'default_organisation_title' property on
      # this person that will returns the organisation title. If this is not
      # defined, then we will acquire the default organisation title of the
      # `destination` person. This is a stupid example, but it works with
      # objects we have in our testing environnement
      self._addProperty('Person',
          'test_19_AcquiredContentAccessor',
          'organisation',
          **self.DEFAULT_ORGANISATION_TITLE_ACQUIRED_PROP)
      # add destination base category to Person TI
      person_ti = self.getTypesTool().getTypeInfo('Person')
      base_category_list = person_ti.getTypeBaseCategoryList()
      if 'destination' not in base_category_list:
        person_ti._setTypeBaseCategoryList(base_category_list + ['destination'])
        self.commit()

      person = self.getPersonModule().newContent(id='1', portal_type='Person')
      other_pers = self.getPersonModule().newContent(id='2', portal_type='Person')
      other_pers_title = 'This is the title we should acquire'
      other_pers.setDefaultOrganisationTitle(other_pers_title)
      person.setDestinationValue(other_pers)

      # title is acquired from the other person
      self.assertEqual(other_pers_title,
                        person.getDefaultOrganisationTitle())

      # now if we save, it should create a default_organisation inside this
      # person, but do not modify the other_pers.
      person.setDefaultOrganisationTitle('Our organisation title')
      self.assertEqual('Our organisation title',
                        person.getDefaultOrganisationTitle())
      self.assertEqual(other_pers_title,
                        other_pers.getDefaultOrganisationTitle())

    def test_19b_AcquiredContentAccessorWithIdClash(self):
      """Tests a content setters do not set the property on acquired object
      that may have the same id, using same scenario as test_19
      Note that we only test Setter for now.
      """
      self._addProperty('Person',
          'test_19b_AcquiredContentAccessorWithIdClash',
          'organisation',
          **self.DEFAULT_ORGANISATION_TITLE_ACQUIRED_PROP)
      # add destination base category to Person TI
      person_ti = self.getTypesTool().getTypeInfo('Person')
      base_category_list = person_ti.getTypeBaseCategoryList()
      if 'destination' not in base_category_list:
        person_ti._setTypeBaseCategoryList(base_category_list + ['destination'])
        self.commit()

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
      self.assertEqual('The organisation title',
                        person.getDefaultOrganisationTitle())

    DEFAULT_LANGUAGE_PROP = {
            'portal_type' : 'Acquired Property',
            'elementary_type':       'tokens',
            'property_default': 'python: ()',
            'content_acquired_property_id': ('subject', ),
            'acquisition_base_category': ( 'parent', ),
            'acquisition_portal_type'  : "python: ( 'Person', )",
            'acquisition_copy_value'   : 0,
            'acquisition_mask_value'   : 1,
            'acquisition_accessor_id'  : 'getAvailableLanguageList',
    }

    def test_19c_AcquiredTokensAccessor(self):
      """Tests an acquired tokens accessor.
         We check in particular that getDefault[Property] and
         setDefault[Property] are working correctly
      """
      self._addProperty('Person',
          'test_19c_AcquiredTokensAccessor_Person',
          'available_language',
          commit=False,
          **self.DEFAULT_LANGUAGE_PROP)
      self._addProperty('Email',
          'test_19c_AcquiredTokensAccessor_Email',
          'available_language',
          **self.DEFAULT_LANGUAGE_PROP)

      # Category setters (list, set, default)
      person = self.getPersonModule().newContent(id='1', portal_type='Person')
      email = person.newContent(portal_type='Email')

      self.assertEqual(0, len(email.getAvailableLanguageList()))
      email.setAvailableLanguageSet(['fr', 'en', 'ja'])
      self.assertEqual(email.getAvailableLanguageList(), ('fr', 'en', 'ja'))
      self.assertEqual(email.getAvailableLanguage(), 'fr')
      self.assertEqual(email.getDefaultAvailableLanguage(), 'fr')
      email.setDefaultAvailableLanguage('ja')
      self.assertEqual(email.getAvailableLanguage(), 'ja')
      self.assertEqual(email.getDefaultAvailableLanguage(), 'ja')
      self.assertEqual(email.getAvailableLanguageList(), ('ja', 'fr', 'en'))

    SUBORDINATION_ORGANISATION_REFERENCE = {
            'portal_type': 'Acquired Property',
            'elementary_type':       'string',
            'acquisition_base_category': ( 'subordination', ),
            'acquisition_portal_type'  : "python: ( 'Organisation', )",
            'acquisition_copy_value'   : 0,
            'acquisition_mask_value'   : 1,
            'acquisition_accessor_id'  : 'getReference',
    }

    def test_19c2_AcquiredStringAccessor(self):
      """Tests an acquired string accessor.
         We check in particular that getDefault[Property] and
         setDefault[Property] are working correctly
         This test focus on acquisition_mask_value parameter
      """
      self._addProperty('Person',
          'test_19c2_AcquiredStringAccessor',
          'subordination_organisation_reference',
          **self.SUBORDINATION_ORGANISATION_REFERENCE)

      person = self.getPersonModule().newContent(portal_type='Person')
      organisation = self.getOrganisationModule()\
                          .newContent(portal_type='Organisation')

      person_reference = 'person_terry'
      person.setSubordinationOrganisationReference(person_reference)
      # Relation is not setted up, accessor must return
      # local value
      self.assertEqual(person.getSubordinationOrganisationReference(),
                        person_reference)

      person.setSubordinationValue(organisation)
      self.tic()

      # mask_value is True, so local value take precedence
      self.assertEqual(person.getSubordinationOrganisationReference(),
                        person_reference)

      organisation_reference = 'organisation_terry'
      organisation.setReference(organisation_reference)
      self.assertEqual(person.getSubordinationOrganisationReference(),
                        person_reference)
      person.setSubordinationOrganisationReference(None)
      self.assertEqual(person.getSubordinationOrganisationReference(),
                        organisation_reference)

    SUBORDINATION_ORGANISATION_SOURCE_REFERENCE = {
            'portal_type': 'Acquired Property',
            'elementary_type':       'string',
            'acquisition_base_category': ( 'subordination', ),
            'acquisition_portal_type'  : "python: ( 'Organisation', )",
            'acquisition_copy_value'   : 0,
            'acquisition_mask_value'   : 0,
            'acquisition_accessor_id'  : 'getSourceReference',
    }

    def test_19c3_AcquiredStringAccessor(self):
      """Tests an acquired string accessor.
         We check in particular that getDefault[Property] and
         setDefault[Property] are working correctly
         This test focus on acquisition_mask_value parameter
      """
      self._addProperty('Person',
          'test_19c3_AcquiredStringAccessor',
          'subordination_organisation_source_reference',
          **self.SUBORDINATION_ORGANISATION_SOURCE_REFERENCE)

      person = self.getPersonModule().newContent(portal_type='Person')
      organisation = self.getOrganisationModule()\
                          .newContent(portal_type='Organisation')

      person_reference = 'person_terry'
      person.setSubordinationOrganisationSourceReference(person_reference)
      # Relation is not setted up, accessor must return
      # local value
      self.assertEqual(person.getSubordinationOrganisationSourceReference(),
                        person_reference)

      person.setSubordinationValue(organisation)
      self.tic()

      # mask_value is False, acquired value take precedence
      # Because relation exists but distant document has no
      # value, accessors fallback on local_value to display
      # something to the user.
      self.assertEqual(person.getSubordinationOrganisationSourceReference(),
                        person_reference)

      organisation_reference = 'organisation_terry'
      organisation.setSourceReference(organisation_reference)
      self.assertEqual(person.getSubordinationOrganisationSourceReference(),
                        organisation_reference)
      person.setSubordinationOrganisationSourceReference(None)
      self.assertEqual(person.getSubordinationOrganisationSourceReference(),
                        organisation_reference)


    NAME_INCLUDED_PROPERTY_EMAIL = '''
          { 'id':         'name_included_in_address',
            'type':       'boolean',
            'default'     : True,
            'acquired_property_id': ('name_included_in_address', ),
            'acquisition_base_category': ( 'parent', ),
            'acquisition_portal_type'  : ( 'Person', ),
            'acquisition_copy_value'   : 0,
            'acquisition_mask_value'   : 1,
            'acquisition_accessor_id'  : 'getNameIncludedInAddress',
            'acquisition_depends'      : None,
            'mode':       'rw', }
    '''

    @expectedFailure
    def test_19d_AcquiredBooleanAccessor(self):
      """Tests acquired boolean accessor.
      Boolean accessors generate both an getPropertyName and an isPropertyName
      Check in particular that both behave the same way regarding acquisition
      """
      self._addProperty('Person',
          'test_19d_AcquiredBooleanAccessor_Person',
          'name_included_in_address',
          commit=False,
          portal_type='Standard Property',
          property_default="python: True",
          elementary_type="boolean")
      self._addProperty('Email',
          'test_19d_AcquiredBooleanAccessor_Email',
          'name_included_in_address',
          'name_included_in_address',
          content_acquired_property_id=('name_included_in_address', ),
          acquisition_base_category=( 'parent', ),
          acquisition_portal_type="python: ( 'Person', )",
          acquisition_copy_value=0,
          acquisition_mask_value=1,
          acquisition_accessor_id='getNameIncludedInAddress',
          portal_type='Acquired Property',
          property_default="python: True",
          elementary_type="boolean")

      person = self.getPersonModule().newContent(portal_type='Person')
      email = person.newContent(portal_type='Email')

      self.assertTrue(person.getNameIncludedInAddress())
      self.assertTrue(person.isNameIncludedInAddress())
      self.assertTrue(email.getNameIncludedInAddress())
      self.assertTrue(email.isNameIncludedInAddress())
      # setting the property on the acquisition target should be reflected on
      # the object acquiring the value
      person.setNameIncludedInAddress(False)
      self.assertFalse(person.getNameIncludedInAddress())
      self.assertFalse(person.isNameIncludedInAddress())
      self.assertFalse(email.getNameIncludedInAddress())
      self.assertFalse(email.isNameIncludedInAddress())
      # setting the property on the acquiring object should mask the value on
      # the acquisition target.
      email.setNameIncludedInAddress(True)
      self.assertFalse(person.getNameIncludedInAddress())
      self.assertFalse(person.isNameIncludedInAddress())
      self.assertTrue(email.getNameIncludedInAddress())
      self.assertTrue(email.isNameIncludedInAddress())

    def test_20_AsContext(self):
      """asContext method return a temporary copy of an object.
      Any modification made to the copy does not change the original object.
      """
      obj = self.getPersonModule().newContent(portal_type='Person')
      obj.setTitle('obj title')
      copy = obj.asContext()
      self.assertTrue(copy.isTempObject(), '%r is not a temp object' % (copy,))
      self.assertEqual(obj, copy.getOriginalDocument())
      self.assertEqual(obj.absolute_url(),
                        copy.getOriginalDocument().absolute_url())
      copy.setTitle('copy title')
      self.assertEqual('obj title', obj.getTitle())
      self.assertEqual('copy title', copy.getTitle())
      self.assertEqual(obj.getId(), copy.getId())

      # asContext method accepts parameters, and edit the copy with those
      # parameters
      obj = self.getPersonModule().newContent(portal_type='Person', id='obj')
      obj.setTitle('obj title')
      copy = obj.asContext(title='copy title')
      self.assertTrue(copy.isTempObject(), '%r is not a temp object' % (copy,))
      self.assertEqual('obj title', obj.getTitle())
      self.assertEqual('copy title', copy.getTitle())
      self.assertEqual(obj.getId(), copy.getId())

      # acquisition context is the same
      self.assertEqual(self.getPersonModule(), obj.getParentValue())
      self.assertEqual(self.getPersonModule(), copy.getParentValue())

      # Test category accessor
      gender = self.getCategoryTool().gender._getOb('male', None)
      if gender is None:
        gender = self.getCategoryTool().gender.newContent(
                            portal_type='Category', id='male')
      # Category can not be used as asContext parameter
#       new_copy = obj.asContext(gender=gender.getCategoryRelativeUrl())
#       self.assertEqual(gender.getCategoryRelativeUrl(), new_copy.getGender())
      new_copy = obj.asContext()
      self.assertTrue(new_copy.isTempObject(),
              '%r is not a temp object' % (new_copy,))
      self.assertEqual(obj.getId(), new_copy.getId())
      new_copy.edit(gender=gender.getCategoryRelativeUrl())
      self.tic()
      self.assertEqual(gender.getCategoryRelativeUrl(), new_copy.getGender())
      self.assertEqual(None, obj.getGender())

      # Make sure that we can do the same for a tool.
      category_tool = self.getCategoryTool()
      original_title = category_tool.getTitle()
      copy_title = 'copy of %s' % (original_title,)
      copy_of_category_tool = category_tool.asContext(title=copy_title)
      self.assertTrue(copy_of_category_tool.isTempObject(),
              '%r is not a temp object' % (copy_of_category_tool,))
      self.assertEqual(category_tool.getTitle(), original_title)
      self.assertEqual(copy_of_category_tool.getTitle(), copy_title)
      self.assertEqual(category_tool.getId(), copy_of_category_tool.getId())

    def test_21_ActionCondition(self):
      """Tests action conditions
      """
      type_tool = self.getTypeTool()
      portal_type_object = type_tool['Organisation']
      def addCustomAction(name,condition):
        portal_type_object.newContent(portal_type='Action Information',
          reference=name,
          title='Become Geek',
          action='string:${object_url}/become_geek_action',
          condition=condition,
          action_permission='View',
          action_type='object_action',
          visible=1,
          float_index=2.0)
      addCustomAction('action1','python: here.getDescription()=="foo"')
      obj = self.getOrganisationModule().newContent(portal_type='Organisation')
      action_tool = self.portal.portal_actions
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


    def test_21bis_getDefaultViewFor(self):
      """check that any action, in category view, with higher priority
      than 'view' take precedence
      """
      type_tool = self.getTypeTool()
      portal_type = 'Organisation'
      portal_type_object = type_tool[portal_type]
      obj = self.getOrganisationModule().newContent(portal_type=portal_type)
      default_view_list = [view for view in portal_type_object.listActions()
                           if view.getReference() == 'view']
      # we got only one default view on this portal type
      self.assertEqual(1, len(default_view_list))
      default_view = default_view_list[0]

      self.assertEqual("Organisation_view",
                        portal_type_object.getDefaultViewFor(obj).getId())

      # Add new action with low priority to replace default view
      new_default_view = portal_type_object.newContent(portal_type='Action Information',
          reference="web_view",
          title='Web view',
          action='string:${object_url}/Organisation_viewDetails',
          condition=None,
          action_permission='View',
          action_type='object_web_view',
          visible=1,
          float_index=0.5)

      # check new default view is resturn
      self.assertEqual("Organisation_viewDetails",
                  portal_type_object.getDefaultViewFor(obj).getId())

      # Add new action with low priority
      # We set it no visible
      hidden_action = portal_type_object.newContent(portal_type='Action Information',
          reference="financial_view",
          title='Financial view',
          action='string:${object_url}/Organisation_viewFinancialInformationList',
          condition=None,
          action_permission='View',
          action_type='object_view',
          visible=0,
          float_index=0.3)

      # Default view must not change
      self.assertEqual("Organisation_viewDetails",
                  portal_type_object.getDefaultViewFor(obj).getId())

      # If no action belong to view category, getDefaultViewFor
      # should fallback to first valid Action.
      # This is the current behaviour for Actions on modules.

      # delete all current actions
      portal_type_object.manage_delObjects([action.getId() for action in \
          portal_type_object.contentValues(portal_type='Action Information')])

      # Add new action which does not belong to view category ( action_type: 'object_list')
      default_list = portal_type_object.newContent(portal_type='Action Information',
          reference="view_list",
          title='Web view',
          action='string:${object_url}/Organisation_viewFinancialInformationList',
          condition=None,
          action_permission='View',
          action_type='object_list',
          visible=1,
          float_index=0.2)

      # check new custom action '_list' is return
      self.assertEqual("Organisation_viewFinancialInformationList",
                  portal_type_object.getDefaultViewFor(obj).getId())

      # Avoid deletion of actions fo rother tests
      self.abort()

    def test_22_securityReindex(self):
      """
      Tests that the security is reindexed when a role is changed on an object.

      Note: Turn on Person.acquire_local_roles to 0 in afterSetUp.
      """
      portal = self.portal

      # turn on Person.acquire_local_roles
      person = self.getTypesTool().getTypeInfo('Person')
      self.person_acquire_local_roles = person.getTypeAcquireLocalRole()
      person.setTypeAcquireLocalRole(True)

      # Make a plain user.
      uf = portal.acl_users
      uf._doAddUser('yo', '', [], [])
      user = uf.getUserById('yo').__of__(uf)

      person_module = self.getPersonModule()
      person = person_module.newContent(portal_type='Person', title='foo')
      person.manage_permission('View', roles=['Auditor'], acquire=0)

      # The user may not view the person object.
      self.tic()
      self.assertTrue('Auditor' not in user.getRolesInContext(person))
      self.logout()
      newSecurityManager(None, user)
      self.assertEqual(len(person_module.searchFolder(id=person.getId())), 0)
      self.logout()
      self.login()

      # Now allow him to view it.
      person_module.manage_addLocalRoles(user.getId(), ['Auditor'])

      # This might look odd (indeed it is), but the catalog should not
      # reflect the security change, until the affected objects are
      # reindexed, and Jean-Paul believes that this should not be
      # automatic.
      self.tic()
      self.assertTrue('Auditor' in user.getRolesInContext(person))
      self.logout()
      newSecurityManager(None, user)
      self.assertEqual(len(person_module.searchFolder(id=person.getId())), 0)
      self.logout()
      self.login()

      # Now invoke the reindexing explicitly, so the catalog should be
      # synchronized.
      person_module.recursiveReindexObject()
      self.tic()
      self.assertTrue('Auditor' in user.getRolesInContext(person))
      self.logout()
      newSecurityManager(None, user)
      self.assertEqual(len(person_module.searchFolder(id=person.getId())), 1)
      self.logout()
      self.login()

    def test_23_titleIsNotDefinedByDefault(self):
      """
      Tests that no title attribute is set on new content
      """
      person_module = self.getPersonModule()
      person = person_module.newContent(portal_type='Person')
      self.assertFalse(person.hasTitle())
      self.assertFalse(person.__dict__.has_key('title'))

    def test_24_relatedValueAccessor(self):
      """
      The purpose of this test is to make sure that category related
      accessors work as expected.

      The test is implemented for both Category and Value
      accessors.

      Test that checked_permission is well configured for View permission
      """
      # Create a few categories
      region_category = self.portal.portal_categories.region
      alpha = region_category.newContent(
              portal_type = "Category",
              id =          "alpha",
              title =       "Alpha System", )
      alpha_path = alpha.getRelativeUrl()

      self.assertEqual(alpha.getRelativeUrl(), 'region/alpha')

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

    def test_25_AqDynamicWithTempObject(self):
      """Check if _aq_dynamic works correctly, regardless of whether
      it is first called for a temporary object or a persistent object.

      This test is based on the fact that a portal type is shared between
      a temporary document and a persistent document, and if a class for
      the temporary document is used for generating new methods, calling
      such methods from a persistent object may fail, because such a
      persistent object is not an instance of the temporary document class.
      """
      portal = self.portal
      # Clear out all generated methods.
      portal.portal_types.resetDynamicDocuments()

      # Create a new temporary person object.
      from Products.ERP5Type.Document import newTempPerson
      o = newTempPerson(portal, 'temp_person_1')
      self.assertTrue(o.isTempObject())
      self.assertEqual(o.getOriginalDocument(), None)

      # This should generate a workflow method.
      self.assertEqual(o.getValidationState(), 'draft')
      o.validate()
      self.assertEqual(o.getValidationState(), 'validated')

      # Create a new persistent person object.
      person_module = portal.person_module
      person_id = 'person_1'
      if person_id in person_module.objectIds():
        person_module.manage_delObjects([person_id])
      o = person_module.newContent(id=person_id, portal_type='Person')
      self.assertFalse(o.isTempObject())

      # This should call methods generated above for the temporary object.
      self.assertEqual(o.getValidationState(), 'draft')
      o.validate()
      self.assertEqual(o.getValidationState(), 'validated')

      # Paranoia: test the reverse snenario as well, although this
      # should succeed anyway.

      # Create a new persistent person object.
      person_id = 'person_2'
      if person_id in person_module.objectIds():
        person_module.manage_delObjects([person_id])
      o = person_module.newContent(id=person_id, portal_type='Person')
      self.assertFalse(o.isTempObject())

      # Clear out all generated methods.
      self.portal.portal_types.resetDynamicDocuments()

      # This should generate workflow methods.
      self.assertEqual(o.getValidationState(), 'draft')
      o.validate()
      self.assertEqual(o.getValidationState(), 'validated')

      # Create a new temporary person object.
      o = newTempPerson(portal, 'temp_person_2')
      self.assertTrue(o.isTempObject())

      # This should call methods generated for the persistent object.
      self.assertEqual(o.getValidationState(), 'draft')
      o.validate()
      self.assertEqual(o.getValidationState(), 'validated')

    def test_26_hasAccessors(self):
      """Test 'has' Accessor.
      This accessor returns true if the property is set on the document.
      """
      self._addProperty('Person',
          'test_26_hasAccessors',
          'foo_bar',
          elementary_type='string',
          portal_type='Standard Property')
      obj = self.getPersonModule().newContent(portal_type='Person')
      self.assertTrue(hasattr(obj, 'hasFooBar'))
      self.assertFalse(obj.hasFooBar())
      obj.setFooBar('something')
      self.assertTrue(obj.hasFooBar())

    def test_27_categoryAccessors(self):
      """
      The purpose of this test is to make sure that category
      accessors work as expected.

      The test is implemented for both Category and Value
      accessors.

      Test that checked_permission is well configured
      for View permission
      """
      # Create a few categories
      region_category = self.portal.portal_categories.region
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

      alpha = gamma.newContent(portal_type='Category',
                               id='alpha',
                               title='Alpha')

      # Make sure categories are reindexed
      self.tic()

      self.assertEqual(beta.getRelativeUrl(), 'region/beta')

      # Create a new person
      module = self.getPersonModule()
      foo = module.newContent(portal_type='Person', title='Foo')

      # Check getDefaultCategory accessor
      foo.setDefaultRegionValue(beta)
      self.assertEqual(beta_path, foo.getDefaultRegion())
      self.assertEqual(
          None,
          foo.getDefaultRegion(checked_permission=checked_permission))

      # Check getCategory accessor
      foo.setDefaultRegionValue(beta)
      self.assertEqual(beta_path, foo.getRegion())
      self.assertEqual(
          None,
          foo.getRegion(checked_permission=checked_permission))

      # Check getCategoryId accessor
      foo.setDefaultRegionValue(beta)
      self.assertEqual(beta_id, foo.getRegionId())
      self.assertEqual(
          None,
          foo.getRegionId(checked_permission=checked_permission))

      # Check getCategoryTitle accessor
      foo.setDefaultRegionValue(beta)
      self.assertEqual(beta_title, foo.getRegionTitle())
      self.assertEqual(
          None,
          foo.getRegionTitle(checked_permission=checked_permission))

      # Check getCategoryLogicalPath accesor
      foo.setDefaultRegionValue(beta)
      self.assertEqual(beta_title, foo.getRegionLogicalPath())

      foo.setDefaultRegionValue(alpha)
      self.assertEqual('Gamma System/Alpha', foo.getRegionLogicalPath())

      # Check getCategoryValue accessor
      # XXX did you know ?
      # calling setDefaultRegionValue here would append a default region, and
      # the region list would be [beta, alpha].
      # bug or feature ? I don't know ...
      foo.setRegionValue(beta)
      self.assertEqual(beta, foo.getRegionValue())
      self.assertEqual(
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
      self.assertSameSet({beta_path}, foo.getRegionSet())
      self.assertSameSet(
          set(),
          foo.getRegionSet(checked_permission=checked_permission))

      # Check getCategoryIdSet accessor
      foo.setDefaultRegionValue(beta)
      self.assertSameSet({beta_id}, foo.getRegionIdSet())
      self.assertSameSet(
          set(),
          foo.getRegionIdSet(checked_permission=checked_permission))

      # Check getCategoryTitleSet accessor
      foo.setDefaultRegionValue(beta)
      self.assertSameSet({beta_title}, foo.getRegionTitleSet())
      self.assertSameSet(
          set(),
          foo.getRegionTitleSet(
            checked_permission=checked_permission))

      # Check getCategoryValueSet accessor
      foo.setDefaultRegionValue(beta)
      self.assertSameSet({beta}, foo.getRegionValueSet())
      self.assertSameSet(
          set(),
          foo.getRegionValueSet(
            checked_permission=checked_permission))

      foo.setRegionValue(None)
      self.assertEqual(None, foo.getRegion())
      # Check setCategoryValue accessor
      foo.setRegionValue(beta)
      self.assertEqual(beta_path, foo.getRegion())
      foo.setRegionValue(None)
      foo.setRegionValue(gamma,
                         checked_permission=checked_permission)
      self.assertSameSet([gamma_path], foo.getRegionList())
      foo.setRegionValue(beta)
      foo.setRegionValue(gamma,
                         checked_permission=checked_permission)
      self.assertSameSet([beta_path, gamma_path], foo.getRegionList())

      foo.setRegionValue(None)
      self.assertEqual(None, foo.getRegion())
      # Check setDefaultCategoryValue accessor
      foo.setDefaultRegionValue(beta)
      self.assertEqual(beta_path, foo.getRegion())
      # XXX setDefaultValue seems buggy when passing None
#       foo.setDefaultRegionValue(None)
      foo.setRegionValue(None)
      foo.setDefaultRegionValue(gamma,
                                checked_permission=checked_permission)
      self.assertEqual(gamma_path, foo.getRegion())
      foo.setDefaultRegionValue(beta_path)
      foo.setDefaultRegionValue(gamma_path,
                                checked_permission=checked_permission)
      self.assertEqual(gamma_path, foo.getDefaultRegion())
      self.assertSameSet([beta_path, gamma_path], foo.getRegionList())

      foo.setRegionValue(None)
      self.assertEqual(None, foo.getRegion())
      # Check setCategory accessor
      foo.setRegion(beta_path)
      self.assertEqual(beta_path, foo.getRegion())
      foo.setRegion(None)
      foo.setRegion(gamma_path,
                    checked_permission=checked_permission)
      self.assertEqual(gamma_path, foo.getRegion())
      foo.setRegion(beta_path)
      foo.setRegion(gamma_path,
                    checked_permission=checked_permission)
      self.assertSameSet([beta_path, gamma_path], foo.getRegionList())
      self.assertEqual(gamma_path,
                        foo.getRegion(checked_permission=checked_permission))

      foo.setRegionValue(None)
      self.assertEqual(None, foo.getRegion())
      # Check setDefaultCategory accessor
      foo.setDefaultRegion(beta_path)
      self.assertEqual(beta_path, foo.getRegion())
      foo.setRegion(None)
      foo.setDefaultRegion(gamma_path,
                    checked_permission=checked_permission)
      self.assertEqual(gamma_path, foo.getRegion())
      foo.setDefaultRegion(beta_path)
      foo.setDefaultRegion(gamma_path,
                    checked_permission=checked_permission)
      self.assertSameSet([beta_path, gamma_path], foo.getRegionList())
      self.assertEqual(gamma_path,
                        foo.getDefaultRegion())

      foo.setRegionValue(None)
      self.assertEqual(None, foo.getRegion())
      # Check setCategoryList accessor
      foo.setRegionList([beta_path])
      self.assertEqual(beta_path, foo.getRegion())
      foo.setRegionList([])
      foo.setRegionList([gamma_path],
                    checked_permission=checked_permission)
      self.assertEqual(gamma_path, foo.getRegion())
      foo.setRegionList([beta_path])
      foo.setRegionList([gamma_path],
                    checked_permission=checked_permission)
      self.assertSameSet([beta_path, gamma_path], foo.getRegionList())

      foo.setRegionValue(None)
      self.assertEqual(None, foo.getRegion())
      # Check setCategoryValueList accessor
      foo.setRegionValueList([beta])
      self.assertEqual(beta_path, foo.getRegion())
      foo.setRegionList([])
      foo.setRegionValueList([gamma],
                    checked_permission=checked_permission)
      self.assertEqual(gamma_path, foo.getRegion())
      foo.setRegionValueList([beta])
      foo.setRegionValueList([gamma],
                    checked_permission=checked_permission)
      self.assertSameSet([beta_path, gamma_path], foo.getRegionList())

      foo.setRegionValue(None)
      self.assertEqual(None, foo.getRegion())
      # Check setCategorySet accessor
      foo.setRegionSet([beta_path])
      self.assertEqual(beta_path, foo.getRegion())
      foo.setRegionSet([])
      foo.setRegionSet([gamma_path],
                    checked_permission=checked_permission)
      self.assertEqual(gamma_path, foo.getRegion())
      foo.setRegionSet([beta_path])
      foo.setRegionSet([gamma_path],
                    checked_permission=checked_permission)
      self.assertSameSet([beta_path, gamma_path], foo.getRegionList())

      foo.setRegionValue(None)
      self.assertEqual(None, foo.getRegion())
      # Check setCategoryValueSet accessor
      foo.setRegionValueSet([beta])
      self.assertEqual(beta_path, foo.getRegion())
      foo.setRegionSet([])
      foo.setRegionValueSet([gamma],
                    checked_permission=checked_permission)
      self.assertEqual(gamma_path, foo.getRegion())
      foo.setRegionValueSet([beta])
      foo.setRegionValueSet([gamma],
                    checked_permission=checked_permission)
      self.assertSameSet([beta_path, gamma_path], foo.getRegionList())

      # check hasCategory accessors
      foo.setRegionValue(None)
      self.assertEqual(None, foo.getRegion())
      self.assertFalse(foo.hasRegion())
      foo.setRegionValue(beta)
      self.assertTrue(foo.hasRegion())

    def test_category_accessor_to_unaccessible_documents(self):
      # Category Accessors raises Unauthorized when you try to access objects
      # you cannot Access, unless you explictly pass checked_permission=

      region_category = self.portal.portal_categories.region
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
      self.assertEqual([beta_path, gamma_path],
                        foo.getRegionList())
      self.assertEqual([gamma_path],
          foo.getRegionList(checked_permission='View'))

      # getRegionValueList raises Unauthorized if document is related to
      # private documents (as always, unless you pass checked_permission)
      self.assertRaises(Unauthorized, foo.getRegionValueList)
      self.assertRaises(Unauthorized, foo.getRegionValueSet)
      self.assertEqual([gamma],
          foo.getRegionValueList(checked_permission='View'))

      # same for property accessors
      self.assertRaises(Unauthorized, foo.getRegionTitleList)
      self.assertRaises(Unauthorized, foo.getRegionTitleSet)
      self.assertEqual(["Gamma System"],
          foo.getRegionTitleList(checked_permission='View'))

      # same for default accessors
      self.assertRaises(Unauthorized, foo.getRegionValue)
      self.assertRaises(Unauthorized, foo.getRegionTitle)

    def test_acquired_property_to_unaccessible_documents(self):
      # Acquired Accessors raises Unauthorized when you try to access objects
      # you cannot Access, unless you explictly pass checked_permission=

      region_category = self.portal.portal_categories.region
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
      self.tic()

      beta.manage_permission('View', roles=[], acquire=0)
      beta.manage_permission('Access contents information', roles=[], acquire=0)
      # with this security setting, it's not possible to access "beta":
      self.assertRaises(Unauthorized,
          region_category.restrictedTraverse, "beta")

      # Define the acquired property
      self._addProperty('Person',
          'Person_test_unaccessible',
          'wrapped_region_title',
          portal_type='Acquired Property',
          elementary_type='lines',
          description='The title of the region',
          content_acquired_property_id=('description', ),
          acquisition_base_category=( 'region', ),
          acquisition_portal_type="python: ( 'Category', )",
          alt_accessor_id=('_categoryGetRegionTitle', ),
          acquisition_copy_value=0,
          acquisition_accessor_id='getTitle')

      # Create a new person, and associate it to beta and gamma.
      module = self.getPersonModule()
      foo = module.newContent(portal_type='Person', title='Foo')
      foo.setRegionValueList((beta, gamma))

      # getRegionList returns relative URLs, no security checks are applied
      self.assertEqual([beta_path, gamma_path],
                        foo.getRegionList())
      self.assertEqual([gamma_path],
          foo.getRegionList(checked_permission='View'))

      # getWrappedRegionTitleList raise Unauthorized if a related document is
      # private
      self.assertRaises(Unauthorized, foo.getWrappedRegionTitleList)
      self.assertEqual(["Gamma System"],
          foo.getWrappedRegionTitleList(checked_permission='View'))

      # Remove permission from parent object, the behaviour of acessor should
      # be kept. If you have no permission to the parent, this means that the
      # sub objects cannot be accessed too.
      gamma.getParentValue().manage_permission("View", [], acquire=0)

      # getProperty is used by forms
      self.assertEqual(None,foo.getProperty("wrapped_region_title_list",
                                                            checked_permission='View'))
      self.assertEqual(None,
                foo.getWrappedRegionTitleList(checked_permission='View'))

      self.assertEqual(["Gamma System"],
                      foo.getWrappedRegionTitleList(checked_permission='Access contents information'))

      gamma.getParentValue().manage_permission("Access contents information", [], acquire=0)
      self.assertEqual(None,
                foo.getWrappedRegionTitleList(checked_permission='View'))

      self.assertEqual(None,
                      foo.getWrappedRegionTitleList(checked_permission='Access contents information'))


    def test_category_accessor_to_non_existing_documents(self):
      # tests behaviour of category accessors with relations to non existing
      # documents.
      region_category = self.portal.portal_categories.region
      beta_id = "beta"
      beta_title = "Beta System"
      beta = region_category.newContent(
              portal_type = "Category",
              id =          beta_id,
              title =       beta_title, )
      beta_path = beta.getCategoryRelativeUrl()

      # gamma does not exist

      # Make sure categories are reindexed
      self.tic()

      # Create a new person, and associate it to beta and gamma.
      module = self.getPersonModule()
      foo = module.newContent(portal_type='Person', title='Foo')
      foo.setRegionList(('beta', 'gamma'))

      self.assertEqual([beta_path, 'gamma'],
                        foo.getRegionList())
      # using relations to non existant objects will issue a warning in
      # event.log
      self._catch_log_errors(ignored_level=sys.maxint)
      self.assertEqual([beta],
                        foo.getRegionValueList())
      self.assertEqual([beta_title],
                        foo.getRegionTitleList())
      self._ignore_log_errors()
      logged_errors = [ logrecord for logrecord in self.logged
                        if logrecord.name == 'CMFCategory' ]
      self.assertEqual('Could not get object region/gamma',
                        logged_errors[0].getMessage())

    def test_list_accessors(self):
      self._addProperty('Person', 'test_list_accessors', 'dummy',
          elementary_type='lines',
          portal_type='Standard Property')
      module = self.getPersonModule()
      # we set the property on the module, to check acquisition works as
      # expected.
      module.dummy = 'value acquired on the module'
      person = module.newContent(id='1', portal_type='Person')

      # default accessor and list accessors are generated
      self.assertTrue(hasattr(person, 'getDummy'))
      self.assertTrue(hasattr(person, 'getDummyList'))

      self.assertEqual(person.getDummy(), None)
      self.assertEqual(person.getDummyList(), None)
      self.assertEqual(person.getDummySet(), None)

      person.setDummyList(['a', 'b'])
      self.assertEqual(person.getDummy(), 'a')
      self.assertEqual(person.getDummyList(), ['a', 'b'])
      self.assertEqual(person.getDummySet(), ['a', 'b'])

      person.setDummy('value')
      self.assertEqual(person.getDummy(), 'value')
      self.assertEqual(person.getDummyList(), ['value'])
      self.assertEqual(person.getDummySet(), ['value'])

    def test_translated_accessors(self):
      self._addProperty('Person',
          'test_translated_accessors',
          'dummy',
          elementary_type='string',
          translatable=1,
          translation_domain='erp5_ui',
          portal_type='Standard Property')
      self.portal.Localizer = DummyLocalizer()
      doc = self.portal.person_module.newContent(portal_type='Person')

      # translated and translation domain accessors are generated
      self.assertTrue(hasattr(doc, 'getTranslatedDummy'))
      self.assertTrue(hasattr(doc, 'getDummyTranslationDomain'))

      self.assertEqual('erp5_ui', doc.getDummyTranslationDomain())
      doc.setDummy('foo')
      self.assertEqual('foo', doc.getTranslatedDummy())
      # the value of the property is translated with erp5_ui
      self.assertEqual(['foo'], self.portal.Localizer.erp5_ui._translated)

      # we can change the translation domain on the portal type
      self.portal.portal_types.Person.setTranslationDomain('dummy',
          'erp5_content')
      self.commit()

      self.assertEqual('erp5_content', doc.getDummyTranslationDomain())
      self.assertEqual('foo', doc.getTranslatedDummy())
      self.assertEqual(['foo'],
                  self.portal.Localizer.erp5_content._translated)

      # set on instance. It has priority over portal type
      doc.setDummyTranslationDomain('default')
      self.assertEqual('default', doc.getDummyTranslationDomain())
      self.assertEqual('foo', doc.getTranslatedDummy())
      self.assertEqual(['foo'], self.portal.Localizer.default._translated)

      # if domain is empty, no translation is performed
      doc = self.portal.person_module.newContent(portal_type='Person')
      self.portal.Localizer = DummyLocalizer()
      self.portal.portal_types.Person.setTranslationDomain('dummy', None)
      self.commit()

      doc.setDummy('foo')
      self.assertFalse(doc.getDummyTranslationDomain())
      self.assertEqual('foo', doc.getTranslatedDummy())
      self.assertEqual([], self.portal.Localizer.erp5_ui._translated)

    def test_translated_category_accessors(self):
      region_category = self.portal.portal_categories.region
      gamma = region_category.newContent(portal_type="Category",
                                         id="gamma",
                                         title="Gamma System")
      alpha = gamma.newContent(portal_type='Category',
                               id='alpha',
                               title='Alpha')
      self.portal.Localizer = DummyLocalizer()
      doc = self.portal.person_module.newContent(portal_type='Person',
                                                 region='gamma/alpha')

      self.assertEqual('Alpha', doc.getRegionTranslatedTitle())
      # the value of the category title is translated with erp5_content
      self.assertEqual(['Alpha'], self.portal.Localizer.erp5_content._translated)

      self.portal.Localizer.erp5_content._translated = []
      self.assertEqual(['Alpha'], doc.getRegionTranslatedTitleList())
      self.assertEqual(['Alpha'], self.portal.Localizer.erp5_content._translated)

      self.portal.Localizer.erp5_content._translated = []
      self.assertEqual('Gamma System/Alpha', doc.getRegionTranslatedLogicalPath())
      self.assertEqual(['Gamma System', 'Alpha'],
                        self.portal.Localizer.erp5_content._translated)


    # _aq_reset should be called implicitly when the system configuration
    # changes:
    def test_aq_reset_on_portal_types_properties_change(self):
      doc = self.portal.person_module.newContent(portal_type='Person')
      ti = self.getTypesTool()['Person']
      base_category_list = ti.getTypeBaseCategoryList()
      # this test is poorly isolated, and the _19*_ add destination
      # to the base categories
      if 'destination' not in base_category_list:

        self.assertFalse(hasattr(doc, 'getDestination'))
        ti.edit(type_base_category_list=
          base_category_list + ['destination'])

        self.commit()
        self.assertTrue(hasattr(doc, 'getDestination'))
      else:
        self.assertTrue(hasattr(doc, 'getDestination'))
        base_category_list.remove('destination')
        ti.edit(type_base_category_list=base_category_list)

        self.commit()
        self.assertFalse(hasattr(doc, 'getDestination'))

    def test_aq_reset_on_workflow_chain_change(self):
      doc = self.portal.person_module.newContent(portal_type='Person')
      self.assertFalse(hasattr(doc, 'getCausalityState'))
      # chain the portal type with a workflow that has 'causality_state' as
      # state variable name, this should regenerate the getCausalityState
      # accessor. This test might have to be updated whenever
      # delivery_causality_workflow changes.
      self.getWorkflowTool().setChainForPortalTypes(
        ['Person'], ('delivery_causality_workflow'))

      self.commit()
      self.assertTrue(hasattr(doc, 'getCausalityState'))

    def test_aq_reset_on_workflow_method_change(self):
      doc = self.portal.person_module.newContent(portal_type='Person')
      self.getWorkflowTool().setChainForPortalTypes(
        ['Person'], ('delivery_causality_workflow'))

      self.commit()
      self.assertTrue(hasattr(doc, 'diverge'))

      wf = self.portal.portal_workflow.delivery_causality_workflow
      wf.transitions.addTransition('dummy_workflow_method')
      from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD
      wf.transitions.dummy_workflow_method.setProperties(
          title='', new_state_id='', trigger_type=TRIGGER_WORKFLOW_METHOD)

      self.commit()
      self.assertTrue(hasattr(doc, 'dummyWorkflowMethod'))

      wf.transitions.deleteTransitions(['dummy_workflow_method'])

      self.commit()
      self.assertFalse(hasattr(doc, 'dummyWorkflowMethod'))

    def test_aq_reset_on_workflow_state_variable_change(self):
      doc = self.portal.person_module.newContent(portal_type='Person')
      self.getWorkflowTool().setChainForPortalTypes(
        ['Person'], ('delivery_causality_workflow'))

      self.commit()
      self.assertTrue(hasattr(doc, 'getCausalityState'))
      wf = self.portal.portal_workflow.delivery_causality_workflow
      wf.variables.setStateVar('dummy_state')

      self.commit()
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
      self.assertEqual('returned_attr', getattr(ok, 'attr'))
      self.assertEqual(ok.aq_dynamic_calls, ['attr'])

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

    def test_renameObjectsReindexSubobjects(self):
      """Test that renaming an object with subobjects causes them to be
         reindexed (their path must be updated).
      """
      folder = self.getOrganisationModule()
      sql_catalog = self.portal.portal_catalog.getSQLCatalog()
      initial_id = 'foo'
      final_id = 'bar'
      subdocument_id = 'sub'
      object = folder.newContent(portal_type='Organisation', id=initial_id)
      object.newContent(id=subdocument_id)
      self.tic()
      folder = self.getOrganisationModule()
      folder.manage_renameObjects([initial_id], [final_id])
      self.tic()
      folder = self.getOrganisationModule()
      subdocument = folder[final_id][subdocument_id]
      subdocument_record = sql_catalog.getRecordForUid(subdocument.uid)
      self.assertEqual(subdocument.getPath(), subdocument_record.path)

    def test_getCreationDate(self):
      """
      Check that getCreationDate does not acquire creation_date property from
      site.
      """
      portal = self.getPortalObject()
      folder = self.getOrganisationModule()
      object = folder.newContent(portal_type='Organisation')
      self.assertNotEquals(object.getCreationDate(), portal.CreationDate())
      self.assertNotEquals(object.getCreationDate(), folder.getCreationDate())

    def test_copyWithoutModificationRight(self):
      """
      Check that it is possible to copy an object on which user doesn't have
      "Modify portal content" permission.
      """
      portal = self.getPortalObject()
      folder = self.getOrganisationModule()
      object = folder.newContent(portal_type='Organisation')
      script_container = portal.portal_skins.custom
      script_id = '%s_afterClone' % (object.getPortalType().replace(' ', ''), )
      createZODBPythonScript(script_container, script_id, '', 'context.setTitle("couscous")')
      try:
        security_manager = getSecurityManager()
        self.assertEqual(1, security_manager.checkPermission('Access contents information', object))
        self.assertEqual(1, security_manager.checkPermission('Modify portal content', object))
        object.manage_permission('Modify portal content')
        clipboard = folder.manage_copyObjects(ids=[object.id])
        # Test fails if this method raises.
        folder.manage_pasteObjects(clipboard)
      finally:
        removeZODBPythonScript(script_container, script_id)

    def test_DefaultSecurityOnAccessors(self):
      # Test accessors are protected correctly
      self._addProperty('Person',
          'test_DefaultSecurityOnAccessors',
          'foo_bar',
          elementary_type='string',
          portal_type='Standard Property')
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
          'test_DefaultSecurityOnListAccessors',
          'foo_bar',
          elementary_type='lines',
          portal_type='Standard Property')
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
          'test_PropertySheetSecurityOnAccessors',
          'foo_bar',
          elementary_type='string',
          write_permission='Set own password',
          read_permission='Manage users',
          portal_type='Standard Property')
      obj = self.getPersonModule().newContent(portal_type='Person', foo_bar='value')
      self.assertTrue(guarded_hasattr(obj, 'setFooBar'))
      self.assertTrue(guarded_hasattr(obj, 'getFooBar'))

      obj.manage_permission('Set own password', [], 0)
      self.assertFalse(guarded_hasattr(obj, 'setFooBar'))
      self.assertTrue(guarded_hasattr(obj, 'getFooBar'))

      obj.manage_permission('Set own password', ['Manager'], 1)
      obj.manage_permission('Manage users', [], 0)
      self.assertTrue(guarded_hasattr(obj, 'setFooBar'))
      self.assertFalse(guarded_hasattr(obj, 'getFooBar'))
      # getProperty also raises
      self.assertRaises(Unauthorized, obj.getProperty, 'foo_bar')
      # ... unless called with checked_permission=
      self.assertEqual(None,
        obj.getProperty('foo_bar', checked_permission='Access content information'))

      # When a document has protected properties, PropertyManager API does not
      # "leak" protected properties when user cannot access.
      self.assertRaises(Unauthorized, obj.propertyItems)
      self.assertRaises(Unauthorized, obj.propertyValues)
      # Other ERP5 APIs do not allow accessing private properties either.
      self.assertRaises(Unauthorized, obj.asXML)

    @expectedFailure
    def test_PropertySheetSecurityOnAccessors_nonstandard_permissions(self):
      """Make sure that we can use 'Access contents information' as
      write permission and 'Modify portal content' as read permission.

      note about the expectedFailure:
      `Access contents information` and `Modify portal content` are
      special cased and currently cannot be applied for other cases as
      getter use access and setter use modify.

      This is done in AccessorHolderType._skip_permission_set from
      product/ERP5Type/dynamic/accessor_holder.py . Maybe we could be more
      specific and define the skip permission on the accessor class, so that
      we can define separatly the skipped permission for setter and getter.
      For now I (Jerome) feel it's not important.
      """
      self._addProperty('Person',
          'test_PropertySheetSecurityOnAccessors',
          'hoge_hoge',
          elementary_type='string',
          write_permission='Access contents information',
          read_permission='Modify portal content',
          portal_type='Standard Property')
      obj = self.getPersonModule().newContent(portal_type='Person')
      self.assertTrue(guarded_hasattr(obj, 'setHogeHoge'))
      self.assertTrue(guarded_hasattr(obj, 'getHogeHoge'))

      obj.manage_permission('Access contents information', [], 0)
      self.assertFalse(guarded_hasattr(obj, 'setHogeHoge'))
      self.assertTrue(guarded_hasattr(obj, 'getHogeHoge'))

      obj.manage_permission('Access contents information', ['Manager'], 1)
      obj.manage_permission('Modify portal content', [], 0)
      self.assertTrue(guarded_hasattr(obj, 'setHogeHoge'))
      self.assertFalse(guarded_hasattr(obj, 'getHogeHoge'))

      # Make sure that getProperty and setProperty respect accessor's
      # security protection.
      createZODBPythonScript(self.portal.portal_skins.custom,
                             'Base_callAccessorHogeHoge',
                             'mode',
                             '''\
if mode == 'getter':
  context.getHogeHoge()
elif mode == 'getProperty':
  context.getProperty('hoge_hoge')
elif mode == 'setter':
  context.setHogeHoge('waa')
elif mode == 'setProperty':
  context.setProperty('hoge_hoge', 'waa')
return True''')
      # test accessors
      obj.manage_permission('Access contents information', ['Manager'], 1)
      obj.manage_permission('Modify portal content', ['Manager'], 1)
      self.assertTrue(guarded_hasattr(obj, 'setHogeHoge'))
      self.assertTrue(guarded_hasattr(obj, 'getHogeHoge'))
      self.assertTrue(obj.Base_callAccessorHogeHoge(mode='getter'))
      self.assertTrue(obj.Base_callAccessorHogeHoge(mode='setter'))
      self.assertTrue(obj.Base_callAccessorHogeHoge(mode='getProperty'))
      self.assertTrue(obj.Base_callAccessorHogeHoge(mode='setProperty'))

      obj.manage_permission('Access contents information', [], 0)
      obj.manage_permission('Modify portal content', [], 0)
      self.assertFalse(guarded_hasattr(obj, 'setHogeHoge'))
      self.assertFalse(guarded_hasattr(obj, 'getHogeHoge'))
      self.assertRaises(Unauthorized, obj.Base_callAccessorHogeHoge, mode='getter')
      self.assertRaises(Unauthorized, obj.Base_callAccessorHogeHoge, mode='setter')
      self.assertRaises(Unauthorized, obj.Base_callAccessorHogeHoge, mode='getProperty')
      self.assertRaises(Unauthorized, obj.Base_callAccessorHogeHoge, mode='setProperty')

    def test_edit(self):
      self._addProperty('Person',
          'test_edit',
          'foo_bar',
          elementary_type='string',
          write_permission='Set own password',
          read_permission='Manage users',
          portal_type='Standard Property')
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
      object_portal_type = 'Test Add Permission Document'
      self.portal.portal_types.newContent(id=object_portal_type,
          type_factory_method_id='addDocument',
          portal_type='Base Type')

      type_info = self.portal.portal_types.getTypeInfo(object_portal_type)

      # allow this type info in Person Module
      container_type_info = self.getTypesTool().getTypeInfo('Person Module')
      container_type_info._setTypeAllowedContentTypeList(
        container_type_info.getTypeAllowedContentTypeList()
        + [object_portal_type])
      self.commit()

      # by default this is empty, which implictly means "Add portal content",
      # the default permission
      self.assertEqual(type_info.permission, '')

      container = self.portal.person_module

      self.assertTrue(getSecurityManager().getUser().has_permission(
                      'Add portal content', container))
      self.assertTrue(type_info in container.allowedContentTypes())
      container.newContent(portal_type=object_portal_type)

      container.manage_permission('Add portal content', [], 0)
      self.assertFalse(type_info in container.allowedContentTypes())
      self.assertRaises(Unauthorized, container.newContent,
                        portal_type=object_portal_type)

      type_info.permission = 'Manage portal'
      container.manage_permission('Manage portal', [], 0)
      self.assertFalse(type_info in container.allowedContentTypes())
      self.assertRaises(Unauthorized, container.newContent,
                        portal_type=object_portal_type)

      container.manage_permission('Manage portal', ['Anonymous'], 0)
      self.assertTrue(type_info in container.allowedContentTypes())
      doc = container.newContent(portal_type=object_portal_type)

      # we can also clone such documents only with the permission registered on
      # the type information
      copy_data = container.manage_copyObjects([doc.getId()])
      container.manage_pasteObjects(copy_data)

      container.manage_permission('Manage portal', [], 0)
      self.assertRaises(Unauthorized, container.manage_pasteObjects, copy_data)


    def testPropertyListWithMonoValuedProperty(self):
      """
      Check that we can use setPropertyList and getPropertyList
      on a mono valued property
      """
      self._addProperty('Person',
          'testPropertyListWithMonoValuedProperty',
          'foo_bar',
          elementary_type='string',
          portal_type='Standard Property')
      person = self.getPersonModule().newContent(portal_type='Person')
      email = person.newContent(portal_type='Email')
      self.assertEqual(None, getattr(person, 'getFooBarList', None))
      self.assertEqual(person.getFooBar(), None)
      self.assertFalse(person.hasProperty('foo_bar'))
      self.assertEqual(person.getProperty('foo_bar'), None)
      self.assertEqual(person.getPropertyList('foo_bar'), [None])
      person.setFooBar('foo')
      self.assertEqual(person.getProperty('foo_bar'), 'foo')
      self.assertEqual(person.getPropertyList('foo_bar'), ['foo'])
      person.setFooBar(None)
      self.assertEqual(person.getProperty('foo_bar'), None)
      person.setPropertyList('foo_bar', ['bar'])
      self.assertEqual(person.getProperty('foo_bar'), 'bar')
      self.assertEqual(person.getPropertyList('foo_bar'), ['bar'])
      self.assertRaises(TypeError, person.setPropertyList, 'foo_bar',
                        ['a', 'b'])

    def testPropertyListOnMonoValuedAcquiredProperty(self):
      """
      Check that we can use setPropertyList and getPropertyList
      on a mono valued acquired property
      """
      self._addProperty('Person',
          'testPropertyListOnMonoValuedAcquiredProperty_Person',
          'foo_bar',
          commit=False,
          elementary_type='string',
          portal_type='Standard Property')
      self._addProperty('Email',
          'testPropertyListOnMonoValuedAcquiredProperty_Email',
          'foo_bar',
          elementary_type='string',
          portal_type='Acquired Property',
          content_acquired_property_id=('description', ),
          acquisition_base_category=( 'parent', ),
          acquisition_portal_type="python: ( 'Person', )",
          acquisition_copy_value=0,
          acquisition_mask_value=1,
          acquisition_accessor_id='getFooBar')
      person = self.getPersonModule().newContent(portal_type='Person')
      email = person.newContent(portal_type='Email')
      self.assertEqual(email.getPropertyList('foo_bar'), [None])
      person.setPropertyList('foo_bar', ['foo'])
      self.assertEqual(email.getPropertyList('foo_bar'), ['foo'])
      email.setPropertyList('foo_bar', ['bar'])
      self.assertEqual(email.getPropertyList('foo_bar'), ['bar'])
      email.setPropertyList('foo_bar', [None])
      self.assertEqual(email.getPropertyList('foo_bar'), ['foo'])
      person.setPropertyList('foo_bar', [None])
      self.assertEqual(email.getPropertyList('foo_bar'), [None])

    def testPropertyListWithMultiValuedProperty(self):
      """
      Check that we can use setPropertyList and getPropertyList
      on a multi valued property
      """
      self._addProperty('Person',
          'testPropertyListWithMultiValuedProperty',
          'foo_bar',
          elementary_type='lines',
          portal_type='Standard Property')
      person = self.getPersonModule().newContent(portal_type='Person')
      # We have None, like test_list_accessors
      self.assertEqual(person.getFooBarList(), None)
      self.assertEqual(person.getPropertyList('foo_bar'), None)
      person.setPropertyList('foo_bar', ['foo', 'bar'])
      self.assertEqual(person.getPropertyList('foo_bar'), ['foo', 'bar'])
      person.setPropertyList('foo_bar', [])
      self.assertEqual(person.getFooBarList(), [])

    def testPropertyNoAcquisition(self):
      """
      Check that getPropertyList (and getProperty as well as
      getPropertyList calls getProperty) do not get the property
      defined on its parent through acquisition
      """
      self._addProperty('Person Module',
                        'testPropertyListWithMultivaluedPropertyNoAcquisition',
                        'multivalued_no_acquisition',
                        elementary_type='lines',
                        portal_type='Standard Property')

      person_module = self.getPersonModule()
      person_module.setPropertyList('multivalued_no_acquisition', ['foo'])
      self.assertEqual(
        person_module.getPropertyList('multivalued_no_acquisition'), ['foo'])

      person = self.getPersonModule().newContent(portal_type='Person')
      self.assertEqual(
        person.getPropertyList('multivalued_no_acquisition', ['bar']), ['bar'])

    def testUndefinedProperties(self):
      """
      Make sure that getProperty and setProperty on a property not defined
      in a propertysheet is working properly.
      """
      person = self.getPersonModule().newContent(portal_type='Person')
      self.assertEqual(person.getProperty('foo_bar'), None)
      person.setProperty('foo_bar', 'foo')
      self.assertEqual(person.getProperty('foo_bar'), 'foo')
      self.assertEqual(person.getPropertyList('foo_bar_list'), None)
      person.setProperty('foo_bar_list', ['foo', 'bar'])
      self.assertEqual(list(person.getProperty('foo_bar_list')), ['foo', 'bar'])

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

    def test_PropertyConstantGetter(self):
      """
      Check the boolean constant getter. Make sure
      it works both like a property and a method
      """
      person = self.getPersonModule().newContent(portal_type='Person')
      person.foo = ConstantGetter('foo', value=False)
      self.assertFalse(person.foo)
      self.assertFalse(person.foo())
      self.assertEqual(person.foo(), 0)
      self.assertEqual(person.foo, 0)
      person.foo = ConstantGetter('foo', value=True)
      self.assertTrue(person.foo)
      self.assertTrue(person.foo())
      self.assertEqual(person.foo(), 1)
      self.assertEqual(person.foo, 1)

    def test_GroupTypeAccessors(self):
      """
      Check that we have automatic accessors in order to check
      if the portal type of an instance is part of a group
      """
      person = self.getPersonModule().newContent(portal_type='Person')
      method = getattr(person, 'isDeliveryType', None)
      self.assertNotEquals(None, method)
      self.assertEqual(0, method())
      method = getattr(person, 'isNodeType', None)
      self.assertNotEquals(None, method)
      self.assertEqual(1, method())

    def test_providesAccessors(self):
      """
      Check that we have automatic accessors in order to check
      if an instance provices a particular interface
      """
      person = self.getPersonModule().newContent(portal_type='Person')
      method = getattr(person, 'providesIMovement', None)
      self.assertNotEquals(None, method)
      self.assertEqual(False, method())
      method = getattr(person, 'providesICategoryAccessProvider', None)
      self.assertNotEquals(None, method)
      self.assertTrue(method())

    def test_dynamic_accessor_mockable(self):
      """Test dynamic accessors also work with mock and that
      generally mock is usable in erp5 tests.
      """
      self._addProperty(
          'Credit Card',
          self.id(),
          'test_mocked_property',
          elementary_type='string',
          portal_type='Standard Property')
      doc = self.portal.person_module.newContent(
          portal_type='Person',
      ).newContent(
          portal_type='Credit Card',
          test_mocked_property='original')
      with mock.patch('erp5.portal_type.Credit Card.getTestMockedProperty', return_value='mocked'):
        self.assertEqual('mocked', doc.getTestMockedProperty())
      self.assertEqual('original', doc.getTestMockedProperty())

    def test_type_provider(self):
      self.portal.newContent(id='dummy_type_provider', portal_type="Types Tool")

      types_tool = self.portal.portal_types
      # register our dummy type provider
      types_tool.type_provider_list = types_tool.type_provider_list + (
                                            'dummy_type_provider',)

      # types created in our type provider are available
      dummy_type = self.portal.dummy_type_provider.newContent(
              portal_type='Base Type',
              id='Dummy Type',
              type_class='Folder', )

      self.commit()

      # our type is available from types tool
      self.assertNotEquals(None, types_tool.getTypeInfo('Dummy Type'))
      self.assertTrue('Dummy Type' in [ti.getId() for ti in
                                        types_tool.listTypeInfo()])

      # not existing types are not an error
      self.assertEqual(None, types_tool.getTypeInfo(self.id()))

      # we can create instances from our type provider
      container = self.portal.newContent(portal_type='Folder', id='test_folder')
      dummy_instance = container.newContent(portal_type='Dummy Type')

      # and use generated accessors on them
      dummy_type.edit(type_property_sheet_list=('Reference', ))

      self.tic()

      dummy_instance.setReference('test')
      self.assertEqual('test', dummy_instance.getReference())

    def test_getIcon(self):
      """
      Check that getIcon returns proper icon.
      """
      portal = self.getPortalObject()
      folder = self.getOrganisationModule()
      o = folder.newContent(portal_type='Organisation')
      self.assertTrue(o.getIcon().endswith(portal.portal_types['Organisation']\
          .getTypeIcon()))

    def test_actionPriority(self):
      """Tests action priority
      """
      portal = self.getPortalObject()
      portal_actions = self.portal.portal_actions
      try:
        module = self.getPersonModule()
        person = module.newContent(id='1', portal_type='Person')
        def addCustomAction(name, priority):
          portal_actions.addAction(id=name,
                                   name=name,
                                   description='',
                                   action='string:${object_url}/Base_viewDict',
                                   condition='',
                                   permission='View',
                                   category='object_view',
                                   priority=priority)
        initial_action_list = portal_actions.listFilteredActionsFor(person)\
            .get('object_view',[])
        addCustomAction('test_before', -1)
        max_priority = max([x.get('priority', 0) for x in initial_action_list])
        addCustomAction('test_after', max_priority + 1)
        final_action_list = portal_actions.listFilteredActionsFor(person)\
            .get('object_view',[])
        self.assertEqual(len(final_action_list), len(initial_action_list) + 2)
        self.assertEqual(final_action_list[0]['id'], 'test_before')
        self.assertEqual(final_action_list[-1]['id'], 'test_after')
        # check that we have another portal types action in the middle
        self.assertTrue('view' in [x['id'] for x in final_action_list[1:-1]])
      finally:
        index_list = []
        action_list = portal_actions._cloneActions()
        for action in action_list:
          if action.id in ('test_before', 'test_after'):
            index_list.append(action_list.index(action))
        if len(index_list):
          portal_actions.deleteActions(selections=index_list)

    def test_propertyMap_unique_properties(self):
      person = self.portal.person_module.newContent(portal_type='Person')
      property_id_list = [p['id'] for p in person.propertyMap()]
      self.assertEqual(len(property_id_list), len(set(property_id_list)),
                       property_id_list)

    def testLocalProperties(self):
      portal = self.getPortalObject()
      person = portal.person_module.newContent(portal_type='Person')
      person.edit(foo_property='bar')
      self.assertEqual('bar', person.getProperty('foo_property'))
      del person.__dict__['foo_property']
      self.assertEqual(None, person.getProperty('foo_property'))
      self.assertEqual(None, person.getProperty('foobar_property'))

    def test_getInstancePropertyAndBaseCategorySet(self):
      """
        Check that the method getInstancePropertyAndBaseCategorySet return
        properties from property sheets correctly
      """
      portal_type = self.portal.portal_types.Person
      result_set = portal_type.getInstancePropertyAndBaseCategorySet()
      # Test a simple property, an acquired one on and a category.
      for x in "id", "address_city", "function":
        self.assertTrue(x in result_set, "%s not in %s" % (x, result_set))
      # Values from which acquired properties are fetched are not returned.
      self.assertFalse("address" in result_set)

    def test_callable_guards(self):
      skin = self.getSkinsTool().custom
      script = createZODBPythonScript(skin, self.id(), 'x', 'return x+1')
      script.manage_setGuard({'guard_roles': 'Manager'})
      self.assertEqual(script(1), 2)
      self.assertTrue(script.checkGuard())
      self.loginWithNoRole()
      self.assertRaises(Forbidden, script, 2)
      self.assertFalse(script.checkGuard())
      script.manage_setGuard({})
      self.assertEqual(script(1), 2)
      self.assertTrue(script.checkGuard())

    def test_updateLocalRolesOnSecurityGroups(self):
      # Boilerplate stuff...
      category_script_id = 'ERP5Type_getSecurityCategoryFromContentRelatedList'
      createZODBPythonScript(
        self.getSkinsTool().custom,
        category_script_id,
        'base_category_list, user_name, document, portal_type',
        '''\
return [
  {
    base_category: [x.getRelativeUrl() for x in document.getRelatedValueList(base_category_list=base_category)]
  }
  for base_category in base_category_list
]
'''
      )
      role1 = 'Auditor'
      role2 = 'Associate'
      alternate = self.portal.portal_categories.local_role_group.newContent(
        portal_type='Category',
        reference='Alternate',
        id='Alternate',
      )
      function = self.portal.portal_categories.function.newContent(
        portal_type='Category',
        id='some_function',
        codification='SF1',
      )
      # End of boilerplate stuff

      organisation = self.portal.organisation_module.newContent(
        portal_type='Organisation',
      )
      person = self.portal.person_module.newContent(
        portal_type='Person',
        career_subordination_value=organisation,
      )
      person.newContent(
        portal_type='Assignment',
        function_value=function,
      ).open()
      self.tic()
      user = self.portal.acl_users.getUserById(person.Person_getUserId())
      hasRole = lambda role: user.has_role(role, organisation)
      # No role given, so no role present
      self.assertFalse(hasRole(role1))
      self.assertFalse(hasRole(role2))
      # Recomputing roles does not modify organisation
      tid_before = organisation._p_serial
      organisation.updateLocalRolesOnSecurityGroups()
      self.tic()
      self.assertEqual(tid_before, organisation._p_serial)
      # Giving roles and recomputing makes these roles present
      self.portal.portal_types.Organisation.newContent(
        portal_type='Role Information',
        role_name=role1,
        role_base_category_list=['subordination'],
        role_base_category_script_id=category_script_id,
      )
      self.portal.portal_types.Organisation.newContent(
        portal_type='Role Information',
        role_name=role2,
        local_role_group_value=alternate,
        role_category=function.getRelativeUrl(),
      )
      organisation.updateLocalRolesOnSecurityGroups()
      self.tic()
      self.assertTrue(hasRole(role1))
      self.assertTrue(hasRole(role2))
      # Test self-check: document modification detection actually works
      self.assertNotEqual(tid_before, organisation._p_serial)
      # Re-computing roles without role definition (nor category) change does
      # not modify the document.
      tid_before = organisation._p_serial
      organisation.updateLocalRolesOnSecurityGroups()
      self.tic()
      self.assertEqual(tid_before, organisation._p_serial)
      self.assertTrue(hasRole(role1))
      self.assertTrue(hasRole(role2))
      # Re-computing roles after relation change removes role
      person.setCareerSubordinationValue(None)
      # XXX: Person reindexation is needed as it acquires categories from
      # Career subobject. This does not automatically happens, and should
      # likely happen (by interaction workflow maybe ?).
      person.recursiveReindexObject()
      self.tic()
      # Note: in a proper setup, updateLocalRolesOnSecurityGroups would
      # automatically get called, likely by interaction workflow, whenever
      # any role condition changes onrelated documents.
      organisation.updateLocalRolesOnSecurityGroups()
      self.tic()
      self.assertFalse(hasRole(role1))
      # but this did not affect the other role
      self.assertTrue(hasRole(role2))

    def test_repr(self):
      document = self.portal.organisation_module.newContent(
          portal_type='Organisation',
          id='organisation_id'
      )
      self.assertEqual(
          '<Organisation at /%s/organisation_module/organisation_id>' % self.portal.getId(),
          repr(document))


class TestAccessControl(ERP5TypeTestCase):
  # Isolate test in a dedicaced class in order not to break other tests
  # when this one fails.
  expression = 'python: context.getPortalType() or 1'

  def getTitle(self):
    return "ERP5Type"

  def getBusinessTemplateList(self):
    return 'erp5_base',

  def afterSetUp(self):
    self.login()

    method = self.getCatalogTool().getSQLCatalog()._getOb('z_catalog_object_list')
    method.setFiltered(1)
    method.setExpression(self.expression)

  def test(self):
    self.portal.person_module.newContent(immediate_reindex=True)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Type))
  suite.addTest(unittest.makeSuite(TestAccessControl))
  return suite
