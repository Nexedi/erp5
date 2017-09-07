##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Nicolas Dumazet <nicolas.dumazet@nexedi.com>
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
##############################################################################

import gc
import os
import shutil
import tempfile
import unittest

import transaction
from persistent import Persistent
from ZODB.broken import BrokenModified
from zExceptions import Forbidden, NotFound
from AccessControl.SecurityManagement import \
  getSecurityManager, setSecurityManager, noSecurityManager
from Products.ERP5Type.dynamic.portal_type_class import synchronizeDynamicModules
from Products.ERP5Type.dynamic.lazy_class import ERP5BaseBroken, InitGhostBase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript

from zope.interface import Interface, implementedBy

class TestPortalTypeClass(ERP5TypeTestCase):
  def getBusinessTemplateList(self):
    return 'erp5_base',

  def testMigrateOldObject(self):
    """
    Check migration of persistent objects with old classes
    like Products.ERP5(Type).Document.Person.Person
    """
    from Products.ERP5Type.Document.Person import Person
    person_module = self.portal.person_module
    connection = person_module._p_jar
    newId = self.portal.person_module.generateNewId

    def unload(id):
      oid = person_module._tree[id]._p_oid
      person_module._tree._p_deactivate()
      connection._cache.invalidate(oid)
      gc.collect()
      # make sure we manage to remove the object from memory
      assert connection._cache.get(oid, None) is None
      return oid

    def check(migrated):
      klass = old_object.__class__
      self.assertEqual(klass.__module__,
        migrated and 'erp5.portal_type' or 'Products.ERP5.Document.Person')
      self.assertEqual(klass.__name__, 'Person')
      self.assertEqual(klass.__setstate__ is Persistent.__setstate__, migrated)

    # Import a .xml containing a Person created with an old
    # Products.ERP5Type.Document.Person.Person type
    self.importObjectFromFile(person_module, 'non_migrated_person.xml')
    self.commit()
    unload('non_migrated_person')
    old_object = person_module.non_migrated_person
    # object unpickling should have instanciated a new style object directly
    check(1)

    obj_id = newId()
    person_module._setObject(obj_id, Person(obj_id))
    self.commit()
    unload(obj_id)
    old_object = person_module[obj_id]
    # From now on, everything happens as if the object was a old, non-migrated
    # object with an old Products.ERP5(Type).Document.Person.Person
    check(0)
    # reload the object
    old_object._p_activate()
    check(1)
    # automatic migration is not persistent
    old_object = None
    # (note we get back the object directly from its oid to make sure we test
    # the class its pickle and not the one in its container)
    old_object = connection.get(unload(obj_id))
    check(0)

    # Test persistent migration
    old_object.migrateToPortalTypeClass()
    old_object = None
    self.commit()
    old_object = connection.get(unload(obj_id))
    check(1)
    # but the container still have the old class
    old_object = None
    unload(obj_id)
    old_object = person_module[obj_id]
    check(0)

    # Test persistent migration of containers
    obj_id = newId()
    person_module._setObject(obj_id, Person(obj_id))
    self.commit()
    unload(obj_id)
    person_module.migrateToPortalTypeClass()
    self.commit()
    unload(obj_id)
    old_object = person_module[obj_id]
    check(1)
    # not recursive by default
    old_object = None
    old_object = connection.get(unload(obj_id))
    check(0)

    # Test recursive migration
    old_object = None
    unload(obj_id)
    person_module.migrateToPortalTypeClass(True)
    self.commit()
    old_object = connection.get(unload(obj_id))
    check(1)

  def testChangeMixin(self):
    """
    Take an existing object, change the mixin definitions of its portal type.
    Check that the new methods are there.
    """
    portal = self.portal
    person_module = portal.person_module
    person = person_module.newContent(id='John Dough', portal_type='Person')

    person_type = portal.portal_types.Person
    self.assertEqual(person_type.getTypeMixinList() or [], [])

    try:
      self.assertEqual(getattr(person, 'asText', None), None)
      # just use a mixin/method that Person does not have yet
      person_type.setTypeMixin('TextConvertableMixin')

      self.commit()

      self.assertNotEquals(getattr(person, 'asText', None), None)
    finally:
      # reset the type
      person_type.setTypeMixin(None)
      self.commit()

  def testChangeDocument(self):
    """
    Take an existing object, change its document class
    Check that the new methods are there.
    """
    portal = self.portal
    person_module = portal.person_module
    person = person_module.newContent(id='Eva Dough', portal_type='Person')

    person_type = portal.portal_types.Person
    self.assertEqual(person_type.getTypeClass(), 'Person')

    try:
      self.assertEqual(getattr(person, 'getCorporateName', None), None)
      # change the base type class
      person_type.setTypeClass('Organisation')

      self.commit()

      self.assertNotEquals(getattr(person, 'getCorporateName', None), None)
    finally:
      # reset the type
      person_type.setTypeClass('Person')
      self.commit()

  def testTempPortalType(self):
    newType = self.portal.portal_types.newContent
    new_type_list = [newType(portal_type='Base Type', type_class='Folder',
                             type_filter_content_type=False).getId()
                     for i in (0, 1)]
    newDocument = self.portal.newContent(self.id(), 'Folder').newContent
    for temp_first, portal_type in enumerate(new_type_list):
      obj = newDocument(portal_type='Folder', temp_object=temp_first)
      obj.newContent('file', portal_type)
      obj.file.aq_base
      obj = newDocument(portal_type='Folder', temp_object=not temp_first)
      obj.newContent('file', portal_type)
      obj.file.aq_base

  def testBoundMethodCaching(self):
    """Test that it is safe to cache a bound method during a transaction

    This test currently fails with the following exception:
      TypeError: unbound method newContent() must be called with FolderMixIn
                 instance as first argument (got Folder instance instead)

    What is the scope of this failure ? Is this test a realistic use case ?
    Is there anyway to reset dynamic classes without triggering this error ?
    Or do we need to reset the fewest classes as possible ?
    """
    newDocument = self.portal.newContent(self.id(), 'Folder').newContent
    self.portal.portal_types.resetDynamicDocuments()
    newDocument(portal_type='Folder')

  def testInterfaces(self):
    types_tool = self.portal.portal_types

    # a new interface
    class IForTest(Interface):
      pass
    from Products.ERP5Type import interfaces
    interfaces.IForTest = IForTest


    # one new type
    dummy_type = types_tool.newContent('InterfaceTestType',
                                       'Base Type')
    # implementing IForTest
    dummy_type.edit(type_class='Person',
                    type_interface_list=['IForTest',],)
    self.commit()

    from erp5.portal_type import InterfaceTestType

    # it's necessary to load the class
    # to have a correct list of interfaces
    implemented_by = list(implementedBy(InterfaceTestType))
    self.assertFalse(IForTest in implemented_by)
    InterfaceTestType.loadClass()

    implemented_by = list(implementedBy(InterfaceTestType))
    self.assertTrue(IForTest in implemented_by,
                    'IForTest not in %s' % implemented_by)

    InterfaceTestType.restoreGhostState()
    implemented_by = list(implementedBy(InterfaceTestType))
    self.assertFalse(IForTest in implemented_by)

  def testClassHierarchyAfterReset(self):
    """
    Check that after a class reset, the class hierarchy is unchanged until
    un-ghostification happens. This is very important for multithreaded
    environments:
      Thread A. reset dynamic classes
      Thread B. in Folder code for instance: CMFBTreeFolder.method(self)

    If a reset happens before the B) method call, and does not keep the
    correct hierarchy (for instance Folder superclass is removed from
    the mro()), a TypeError might be raised:
      "method expected CMFBTreeFolder instance, got erp5.portal_type.xxx
      instead"

    This used to be broken because the ghost state was only what is called
    lazy_class.InitGhostBase: a "simple" subclass of ERP5Type.Base
    """
    name = "testClassHierarchyAfterReset Module"
    types_tool = self.portal.portal_types

    ptype = types_tool.newContent(id=name, type_class="Folder")
    self.commit()
    module_class = types_tool.getPortalTypeClass(name)
    module_class.loadClass()

    # first manually reset and check that everything works
    from Products.ERP5Type.Core.Folder import Folder
    self.assertTrue(issubclass(module_class, Folder))
    synchronizeDynamicModules(self.portal, force=True)
    self.assertTrue(issubclass(module_class, Folder))

    # then change the type value to something not descending from Folder
    # and check behavior
    ptype.setTypeClass(types_tool.Address.getTypeClass())

    # while the class has not been reset is should still descend from Folder
    self.assertTrue(issubclass(module_class, Folder))
    # finish transaction and trigger workflow/DynamicModule reset
    self.commit()
    # while the class has not been unghosted it's still a Folder
    self.assertTrue(issubclass(module_class, Folder))
    # but it changes as soon as the class is loaded
    module_class.loadClass()
    self.assertFalse(issubclass(module_class, Folder))

  def testAttributeValueComputedFromAccessorHolderList(self):
    """
    Check that attributes such as constraints and _categories,
    containing respectively all the constraints and categories define
    on their Property Sheets, loads the portal type class as some
    static getters (for example getInstanceBaseCategoryList() use
    _categories directly)
    """
    import erp5.portal_type

    synchronizeDynamicModules(self.portal, force=True)
    self.assertTrue(erp5.portal_type.Person.__isghost__)
    self.assertTrue('constraints' not in erp5.portal_type.Person.__dict__)

    getattr(erp5.portal_type.Person, 'constraints')
    self.assertTrue(not erp5.portal_type.Person.__isghost__)
    self.assertTrue('constraints' in erp5.portal_type.Person.__dict__)

    synchronizeDynamicModules(self.portal, force=True)
    self.assertTrue(erp5.portal_type.Person.__isghost__)
    self.assertTrue('_categories' not in erp5.portal_type.Person.__dict__)

    getattr(erp5.portal_type.Person, '_categories')
    self.assertTrue(not erp5.portal_type.Person.__isghost__)
    self.assertTrue('_categories' in erp5.portal_type.Person.__dict__)

class TestZodbPropertySheet(ERP5TypeTestCase):
  """
  XXX: WORK IN PROGRESS
  """
  def getBusinessTemplateList(self):
    return 'erp5_base',

  def _newStandardProperty(self, operation_type):
    """
    Create a new Standard Property within test Property Sheet
    """
    self.test_property_sheet.newContent(
      portal_type='Standard Property',
      reference='test_standard_property_' + operation_type,
      property_default='python: "test_default_value"',
      elementary_type='string')

  def _newAcquiredProperty(self, operation_type):
    """
    Create a new Acquired Property within test Property Sheet
    """
    self.test_property_sheet.newContent(
      portal_type='Acquired Property',
      reference='test_acquired_property_' + operation_type,
      elementary_type='content',
      storage_id='default_address',
      acquisition_mask_value=True,
      acquisition_base_category=('subordination',),
      acquisition_portal_type="python: ('Organisation',)",
      acquisition_accessor_id='getDefaultAddressValue',
      content_portal_type="python: ('Address',)",
      content_acquired_property_id=('street_address',))

  def _newCategoryTree(self, base_category_id, operation_type):
    """
    Create new categories for the tests (for the category accessors to
    be created, it's necessary that the category properties referenced
    in the web-based Property Sheet exist)
    """
    new_base_category = self.portal.portal_categories.newContent(
      id=base_category_id, portal_type='Base Category')

    # Create a dummy sub-category
    new_base_category.newContent(reference='sub_category1',
                                 portal_type='Category')

    new_base_category.newContent(reference='sub_category2',
                                 portal_type='Category')

    if operation_type == 'change_reference':
      self.portal.portal_categories.newContent(
        id=base_category_id + '_renamed',
        portal_type='Base Category')

  def _newCategoryProperty(self, operation_type):
    """
    Create a new Category Property within test Property Sheet
    """
    category_id = 'test_category_property_' + operation_type

    self._newCategoryTree(category_id, operation_type)

    self.test_property_sheet.newContent(
      reference=category_id,
      portal_type='Category Property')

  def _newDynamicCategoryProperty(self, operation_type):
    """
    Create a new Dynamic Category Property within test Property Sheet
    """
    category_id = 'test_dynamic_category_property_' + operation_type

    self._newCategoryTree(category_id, operation_type)

    expression = "python: ('%s',)" % category_id

    self.test_property_sheet.newContent(
      portal_type='Dynamic Category Property',
      category_expression=expression,
      reference=category_id)

  def _newPropertyExistenceConstraint(self):
    """
    Create a new Property Existence Constraint within test Property
    Sheet
    """
    self.test_property_sheet.newContent(
      reference='test_property_existence_constraint',
      portal_type='Property Existence Constraint',
      constraint_property_list=('test_standard_property_constraint',))

  def _newCategoryExistenceConstraint(self):
    """
    Create a new Category Existence Constraint within test Property
    Sheet
    """
    self._newCategoryProperty('constraint')

    self.test_property_sheet.newContent(
      reference='test_category_existence_constraint',
      portal_type='Category Existence Constraint',
      constraint_base_category_list=('test_category_property_constraint',))
      # XXX
      # constraint_portal_type=('TODO',))

  def _newAttributeEqualityConstraint(self):
    """
    Create a new Attribute Equality Constraint within test Property
    Sheet
    """
    # For testing primitive type as attribute value
    self.test_property_sheet.newContent(
      reference='test_attribute_equality_constraint',
      portal_type='Attribute Equality Constraint',
      constraint_attribute_name='title',
      constraint_attribute_value='python: "my_valid_title"')

    # For testing list type as attribute value
    self.test_property_sheet.newContent(
      reference='test_attribute_list_equality_constraint',
      portal_type='Attribute Equality Constraint',
      constraint_attribute_name='categories_list',
      constraint_attribute_value='python: ("sub_category1", "sub_category2")')

  def _newContentExistenceConstraint(self):
    """
    Create a new Content Existence Constraint within test Property
    Sheet
    """
    self.test_property_sheet.newContent(
      reference='test_content_existence_constraint',
      portal_type='Content Existence Constraint',
      constraint_portal_type='python: ("Test Document")')

  def _newCategoryMembershipArityConstraint(self,
                                            reference,
                                            use_acquisition=False):
    """
    Create a new Category Membership Arity Constraint within test
    Property Sheet (with or without acquisition)
    """
    self.portal.portal_categories.newContent(
      id=reference, portal_type='Base Category')

    self.test_property_sheet.newContent(
      reference=reference,
      portal_type='Category Membership Arity Constraint',
      min_arity=1,
      max_arity=1,
      use_acquisition=use_acquisition,
      constraint_portal_type="python: ('Test Migration',)",
      constraint_base_category=(reference,))

  def _newCategoryRelatedMembershipArityConstraint(self):
    """
    Create a new Category Related Membership Arity Constraint within
    test Property Sheet, using an existing Base Category because
    creating a new Base Category would involve clearing up the cache
    """
    self.test_property_sheet.newContent(
      reference='test_category_related_membership_arity_constraint',
      portal_type='Category Related Membership Arity Constraint',
      min_arity=1,
      max_arity=1,
      constraint_portal_type="python: ('Test Migration',)",
      constraint_base_category=('gender',))

  def _newTALESConstraint(self):
    """
    Create a new TALES Constraint within test Property Sheet
    """
    self.test_property_sheet.newContent(
      reference='test_tales_constraint',
      portal_type='TALES Constraint',
      expression='python: object.getTitle() == "my_tales_constraint_title"')

  def _newPropertyTypeValidityConstraint(self):
    """
    Create a new Property Type Validity Constraint within test
    Property Sheet
    """
    self.test_property_sheet.newContent(
      reference='test_property_type_validity_constraint',
      portal_type='Property Type Validity Constraint')

  def afterSetUp(self):
    """
    Create a test Property Sheet (and its properties)
    """
    portal = self.portal

    # Create the test Property Sheet
    try:
      self.test_property_sheet = portal.portal_property_sheets.TestMigration
      do_create = False
    except AttributeError:
      self.test_property_sheet = \
        portal.portal_property_sheets.newContent(id='TestMigration',
                                                 portal_type='Property Sheet')
      do_create = True

    if do_create:
      # Create a new Standard Property to test constraints and a
      # Property Existence Constraint in the test Property Sheet
      self._newStandardProperty('constraint')
      self._newPropertyExistenceConstraint()

      # Create a Category Existence Constraint in the test Property
      # Sheet
      self._newCategoryExistenceConstraint()

      # Create an Attribute Equality Constraint in the test Property
      # Sheet
      self._newAttributeEqualityConstraint()

      # Create a Content Existence Constraint in the test Property
      # Sheet
      self._newContentExistenceConstraint()

      # Create a Category Membership Arity Constraint without
      # acquisition in the test Property Sheet
      self._newCategoryMembershipArityConstraint(
        'test_category_membership_arity_constraint')

      # Create a Category Membership Arity Constraint with acquisition
      # in the test Property Sheet
      self._newCategoryMembershipArityConstraint(
        'test_category_membership_arity_constraint_with_acquisition',
        use_acquisition=True)

      # Create a Category Related Membership Arity Constraint in the
      # test Property Sheet
      self._newCategoryRelatedMembershipArityConstraint()

      # Create a TALES Constraint in the test Property Sheet
      self._newTALESConstraint()

      # Create a Property Type Validity Constraint in the test Property Sheet
      self._newPropertyTypeValidityConstraint()

      # Create all the test Properties
      for operation_type in ('change_reference', 'change', 'delete', 'assign'):
        self._newStandardProperty(operation_type)
        self._newAcquiredProperty(operation_type)
        self._newCategoryProperty(operation_type)
        self._newDynamicCategoryProperty(operation_type)

    # Bind all test properties to this instance, so they can be
    # accessed easily in further tests
    for property in self.test_property_sheet.contentValues():
      setattr(self, property.getReference(), property)

    # Create a Portal Type for the tests, this is necessary, otherwise
    # there will be no accessor holder generated
    try:
      self.test_portal_type = getattr(portal.portal_types, 'Test Migration')
    except AttributeError:
      self.test_portal_type = portal.portal_types.newContent(
        id='Test Migration',
        portal_type='Base Type',
        type_class='Folder',
        type_property_sheet_list=('TestMigration',),
        type_base_category_list=('test_category_existence_constraint',),
        type_filter_content_type=False)
    # Create a Portal Type for subobject of Test Migration
    try:
      self.test_subobject_portal_type = getattr(portal.portal_types, 'Test Document')
    except AttributeError:
      self.test_subobject_portal_type = portal.portal_types.newContent(
        id='Test Document',
        portal_type='Base Type',
        type_class='Folder',
        type_filter_content_type=False)
      self.test_portal_type.setTypeAllowedContentTypeList(['Test Document'])

    # Create a test module, meaningful to force generation of
    # TestMigration accessor holders and check the constraints
    try:
      self.test_module = getattr(portal, 'Test Migration')
    except AttributeError:
      self.test_module = portal.newContent(id='Test Migration',
                                           portal_type='Test Migration')

    # Make sure there is no pending transaction which could interfere
    # with the tests
    self.tic()

    # Ensure that erp5.acessor_holder is empty
    synchronizeDynamicModules(portal, force=True)

  def _forceTestAccessorHolderGeneration(self):
    """
    Force generation of TestMigration accessor holder by accessing any
    accessor, which will run the interaction workflow trigger, on
    commit at the latest
    """
    self.commit()
    self.test_module.getId()

  def testAssignUnassignZodbPropertySheet(self):
    """
    From an existing portal type, assign ZODB Property Sheets and
    check that
    """
    import erp5

    portal = self.portal
    person_type = portal.portal_types.Person

    self.assertFalse('TestMigration' in person_type.getTypePropertySheetList())

    new_person = None
    try:
      # Assign ZODB test Property Sheet to the existing Person type
      # and create a new Person, this should generate the test
      # accessor holder which should be in the Person type inheritance
      person_type.setTypePropertySheetList('TestMigration')

      self.commit()

      self.assertTrue('TestMigration' in person_type.getTypePropertySheetList())

      # The accessor holder will be generated once the new Person will
      # be created as Person type has test Property Sheet
      self.failIfHasAttribute(erp5.accessor_holder.property_sheet,
                              'TestMigration')

      new_person = portal.person_module.newContent(
        id='testAssignZodbPropertySheet', portal_type='Person')

      self.assertHasAttribute(erp5.accessor_holder.property_sheet,
                              'TestMigration')

      self.assertTrue(erp5.accessor_holder.property_sheet.TestMigration in \
                      erp5.portal_type.Person.mro())

      # Check that the accessors have been properly created for all
      # the properties of the test Property Sheet and set a new value
      # to make sure that everything is fine
      #
      # Standard Property
      self.assertHasAttribute(new_person, 'setTestStandardPropertyAssign')

      self.assertEqual(new_person.getTestStandardPropertyAssign(),
                        "test_default_value")

      new_person.setTestStandardPropertyAssign('value')

      self.assertEqual(new_person.getTestStandardPropertyAssign(), 'value')

      # Acquired Property
      self.assertHasAttribute(
        new_person, 'setDefaultTestAcquiredPropertyAssignStreetAddress')

      new_person.setDefaultTestAcquiredPropertyAssignStreetAddress('value')

      self.assertHasAttribute(new_person, 'default_address')
      self.assertHasAttribute(new_person.default_address, 'getDefaultAddress')
      self.assertNotEqual(None, new_person.default_address.getDefaultAddress())

      self.assertEqual(
        new_person.getDefaultTestAcquiredPropertyAssignStreetAddress(),
        'value')

      # Category Property
      self.assertHasAttribute(new_person, 'setTestCategoryPropertyAssign')

      new_person.setTestCategoryPropertyAssign('sub_category1')

      self.assertEqual(new_person.getTestCategoryPropertyAssign(),
                        'sub_category1')

      # Dynamic Category Property
      self.assertHasAttribute(new_person,
                              'setTestDynamicCategoryPropertyAssign')

      new_person.setTestDynamicCategoryPropertyAssign('sub_category1')

      self.assertEqual(new_person.getTestDynamicCategoryPropertyAssign(),
                        'sub_category1')

    finally:
      # Perform a commit here because Workflow interactions keeps a
      # TransactionalVariable whose key is computed from the ID of the
      # workflow and the ID of the interaction and where the value is
      # a boolean stating whether the transition method has already
      # been called before.  Thus, the next statement may not reset
      # erp5.accessor_holder as loading Person portal type calls
      # '_setType*'
      self.commit()

      person_type.setTypePropertySheetList(())

      if new_person is not None:
        portal.person_module.deleteContent(new_person.getId())

      new_person = None

    # Check that the new-style Property Sheet has been properly
    # unassigned by creating a new person in Person module
    self.commit()

    self.assertFalse('TestMigration' in person_type.getTypePropertySheetList())

    try:
      new_person = portal.person_module.newContent(
        id='testAssignZodbPropertySheet', portal_type='Person')

      self.failIfHasAttribute(erp5.accessor_holder.property_sheet, 'TestMigration')
      self.failIfHasAttribute(new_person, 'getTestStandardPropertyAssign')

    finally:
      if new_person is not None:
        portal.person_module.deleteContent(new_person.getId())

  def _checkAddPropertyToZodbPropertySheet(self,
                                          new_property_function,
                                          added_accessor_name):
    import erp5.accessor_holder.property_sheet

    self.failIfHasAttribute(erp5.accessor_holder.property_sheet,
                            'TestMigration')

    new_property_function('add')
    self._forceTestAccessorHolderGeneration()

    self.assertHasAttribute(erp5.accessor_holder.property_sheet,
                            'TestMigration')

    self.assertHasAttribute(erp5.accessor_holder.property_sheet.TestMigration,
                            added_accessor_name)

  def testAddStandardPropertyToZodbPropertySheet(self):
    """
    Take an existing new-style Property Sheet, add a new Standard
    Property and check that it has been properly added
    """
    self._checkAddPropertyToZodbPropertySheet(
      self._newStandardProperty,
      'getTestStandardPropertyAdd')

  def testAddAcquiredPropertyToZodbPropertySheet(self):
    """
    Take an existing new-style Property Sheet, add a new Acquired
    Property and check that it has been properly added
    """
    self._checkAddPropertyToZodbPropertySheet(
      self._newAcquiredProperty,
      'getDefaultTestAcquiredPropertyAddStreetAddress')

  def testAddCategoryPropertyToZodbPropertySheet(self):
    """
    Take an existing ZODB Property Sheet, add a new Category Property
    and check that it has been properly added
    """
    self._checkAddPropertyToZodbPropertySheet(
      self._newCategoryProperty,
      'getTestCategoryPropertyAdd')

  def testAddDynamicCategoryPropertyToZodbPropertySheet(self):
    """
    Take an existing ZODB Property Sheet, add a new Dynamic Category
    Property and check that it has been properly added
    """
    self._checkAddPropertyToZodbPropertySheet(
      self._newDynamicCategoryProperty,
      'getTestDynamicCategoryPropertyAdd')

  def _checkChangePropertyReferenceOfZodbPropertySheet(self,
                                                       change_setter_func,
                                                       new_value,
                                                       changed_accessor_name):
    import erp5.accessor_holder.property_sheet

    self.failIfHasAttribute(erp5.accessor_holder.property_sheet,
                            'TestMigration')

    change_setter_func(new_value)
    self._forceTestAccessorHolderGeneration()

    self.assertHasAttribute(erp5.accessor_holder.property_sheet,
                            'TestMigration')

    self.assertHasAttribute(erp5.accessor_holder.property_sheet.TestMigration,
                            changed_accessor_name)

  def testChangeStandardPropertyReferenceOfZodbPropertySheet(self):
    """
    Take the test Property Sheet, change the 'reference' field of a
    Standard Property and check that the accessor name has changed

    Interaction: PropertySheet_resetDynamicClasses (manage_renameObject)
    """
    self._checkChangePropertyReferenceOfZodbPropertySheet(
      self.test_standard_property_change_reference.setReference,
      'test_standard_property_change_reference_renamed',
      'getTestStandardPropertyChangeReferenceRenamed')

  def testChangeAcquiredPropertyReferenceOfZodbPropertySheet(self):
    """
    Take the test Property Sheet, change the 'reference' field of an
    Acquired Property and check that the accessor name has changed

    Interaction: PropertySheet_resetDynamicClasses (manage_renameObject)
    """
    self._checkChangePropertyReferenceOfZodbPropertySheet(
      self.test_acquired_property_change_reference.setReference,
      'test_acquired_property_change_reference_renamed',
      'getDefaultTestAcquiredPropertyChangeReferenceRenamedStreetAddress')

  def testChangeCategoryPropertyReferenceOfZodbPropertySheet(self):
    """
    Take the test Property Sheet, change the 'id' field of a Category Property
    to another existing category and check that the accessor name has changed.

    Interaction: PropertySheet_resetDynamicClasses (manage_renameObject)
    """
    self._checkChangePropertyReferenceOfZodbPropertySheet(
      self.test_category_property_change_reference.setReference,
      'test_category_property_change_reference_renamed',
      'getTestCategoryPropertyChangeReferenceRenamed')

  def testChangeDynamicCategoryPropertyReferenceOfZodbPropertySheet(self):
    """
    Take the test Property Sheet, change the 'category_expression'
    field of a Dynamic Category Property to another existing category
    and check that the accessor name has changed

    Interaction: PropertySheet_resetDynamicClasses (manage_renameObject)
    """
    self._checkChangePropertyReferenceOfZodbPropertySheet(
      self.test_dynamic_category_property_change_reference.setCategoryExpression,
      "python: ('test_dynamic_category_property_change_reference_renamed',)",
      'getTestDynamicCategoryPropertyChangeReferenceRenamed')

  def _checkChangePropertyOfZodbPropertySheet(self,
                                              property_obj,
                                              accessor_name):
    import erp5.accessor_holder.property_sheet

    self.failIfHasAttribute(erp5.accessor_holder.property_sheet,
                            'TestMigration')

    property_obj.setReadPermission('Manage Portal')
    self._forceTestAccessorHolderGeneration()

    self.assertHasAttribute(erp5.accessor_holder.property_sheet,
                            'TestMigration')

    accessor_holder = erp5.accessor_holder.property_sheet.TestMigration
    permission_accessor_tuple = dict(accessor_holder.__ac_permissions__).get(
      'Manage Portal', ())

    self.assertTrue(
      accessor_name in permission_accessor_tuple,
      msg="'%s' not found in 'Manage Portal' Permission tuple: %r" % (
        accessor_name,
        permission_accessor_tuple))

  def testChangeStandardPropertyOfZodbPropertySheet(self):
    """
    Take the test Property Sheet, change the 'read_permission' field of a
    Standard Property and check that the accessor Permission has been changed

    Interaction: ChangeProperty_resetDynamicClasses
    """
    self._checkChangePropertyOfZodbPropertySheet(
      self.test_standard_property_change,
      'getTestStandardPropertyChange')

  def testChangeAcquiredPropertyOfZodbPropertySheet(self):
    """
    Take the test Property Sheet, change the 'read_permission' field of an
    Acquired Property and check that the accessor Permission has been changed

    Interaction: ChangeProperty_resetDynamicClasses
    """
    self._checkChangePropertyOfZodbPropertySheet(
      self.test_acquired_property_change,
      'getTestAcquiredPropertyChange')

  def _checkDeletePropertyFromZodbPropertySheet(self,
                                               property_id,
                                               accessor_name):
    """
    Delete the given property from the test Property Sheet and check
    whether its corresponding accessor is not there anymore
    """
    import erp5.accessor_holder.property_sheet

    self.failIfHasAttribute(erp5.accessor_holder, 'TestMigration')

    # Delete the property and force re-generation of TestMigration
    # accessor holder
    self.test_property_sheet.deleteContent(property_id)
    self._forceTestAccessorHolderGeneration()

    self.assertHasAttribute(erp5.accessor_holder.property_sheet, 'TestMigration')
    self.failIfHasAttribute(erp5.accessor_holder.property_sheet.TestMigration,
                            accessor_name)

  def testDeleteStandardPropertyFromZodbPropertySheet(self):
    """
    Take the test Property Sheet, delete a Standard Property and check
    that the accessor is not there anymore
    """
    self._checkDeletePropertyFromZodbPropertySheet(
      self.test_standard_property_delete.getId(),
      'getTestStandardPropertyDelete')

  def testDeleteAcquiredPropertyFromZodbPropertySheet(self):
    """
    Take the test Property Sheet, delete an Acquired Property and
    check that the accessor is not there anymore
    """
    self._checkDeletePropertyFromZodbPropertySheet(
      self.test_acquired_property_delete.getId(),
      'getTestAcquiredPropertyDelete')

  def testDeleteCategoryPropertyFromZodbPropertySheet(self):
    """
    Take the test Property Sheet, delete a Category Property and check
    that the accessor is not there anymore
    """
    self._checkDeletePropertyFromZodbPropertySheet(
      self.test_category_property_delete.getId(),
      'getTestCategoryPropertyDelete')

  def testDeleteDynamicCategoryPropertyFromZodbPropertySheet(self):
    """
    Take the test Property Sheet, delete a Category Property and check
    that the accessor is not there anymore
    """
    self._checkDeletePropertyFromZodbPropertySheet(
      self.test_dynamic_category_property_delete.getId(),
      'getTestDynamicCategoryPropertyDelete')

  def _getConstraintByReference(self, reference):
    for constraint in self.test_module.constraints:
      try:
        if constraint.getReference() == reference:
          return constraint
      except AttributeError:
        pass

    return None

  def _checkConstraint(self,
                       constraint_reference,
                       setter_function,
                       *args,
                       **kw):
    constraint = self._getConstraintByReference(constraint_reference)
    self.assertNotEqual(None, constraint)

    # Use Base.checkConsistency!!
    # This is the standard interface which real users are always using.
    # Never call ConstraintMixin.checkConsistency directly in unit test.
    # You will miss serious bugs.
    self.assertEqual(1, len(self.test_module.checkConsistency(filter={'reference':constraint_reference})))

    setter_function(*args, **kw)
    self.assertEqual([], self.test_module.checkConsistency(filter={'reference':constraint_reference}))

  def testPropertyExistenceConstraint(self):
    """
    Take the test module and check whether the Property Existence
    Constraint is there. Until the property has been set to a value,
    the constraint should fail
    """
    # See ERP5Type.Base.Base.hasProperty()
    self._checkConstraint('test_property_existence_constraint',
                          self.test_module.setTestStandardPropertyConstraint,
                          'foobar')

  def testCategoryExistenceConstraint(self):
    """
    Take the test module and check whether the Property Existence
    Constraint is there. Until the category has been set to an
    existing category, the constraint should fail
    """
    self._checkConstraint('test_category_existence_constraint',
                          self.test_module.setTestCategoryPropertyConstraint,
                          'sub_category1')

  def testAttributeEqualityConstraint(self):
    """
    Take the test module and check whether the Attribute Equality
    Constraint is there. Until the attribute to be checked has been
    set to its expected value, the constraint should fail. The purpose
    is to test only primitive types (e.g. not list)
    """
    # As checkConsistency calls hasProperty before checking the value,
    # the property to be tested has to be set at least once (whatever
    # the value)
    self.test_module.setTitle('invalid_value')

    self._checkConstraint('test_attribute_equality_constraint',
                          self.test_module.setTitle,
                          'my_valid_title')

  def testAttributeListEqualityConstraint(self):
    """
    Take the test module and check whether the Attribute Equality
    Constraint is there. Until the attribute to be checked has been
    set to its expected value (a list of categories), the constraint
    should fail. The purpose is to test only list types

    @see testAttributeEqualityConstraint
    """
    self.test_module.setCategoryList(('sub_category1',))

    self._checkConstraint('test_attribute_list_equality_constraint',
                          self.test_module.setCategoryList,
                          ('sub_category1', 'sub_category2'))

  def testContentExistenceConstraint(self):
    """
    Take the test module and check whether the Test Document is there.
    Until there is at least one subobject of 'Test Module' whose Portal
    Type is 'Folder', the constraint should fail
    """
    self._checkConstraint('test_content_existence_constraint',
                          self.test_module.newContent,
                          id='Test Content Existence Constraint',
                          portal_type='Test Document')

  def testCategoryMembershipArityConstraint(self):
    """
    Take the test module and check whether the Category Membership
    Arity Constraint is there. Until a Base Category is set on the
    Test Module, the constraint should fail
    """
    self._checkConstraint('test_category_membership_arity_constraint',
                          self.test_module.setCategoryList,
                          ('test_category_membership_arity_constraint/'\
                           'Test Migration',))

  def testCategoryMembershipArityConstraintWithAcquisition(self):
    """
    Take the test module and check whether the Category Acquired
    Membership Arity Constraint is there. Until a Base Category is set
    on the Test Module, the constraint should fail

    XXX: Test with acquisition?
    """
    self._checkConstraint(
      'test_category_membership_arity_constraint_with_acquisition',
      self.test_module.setCategoryList,
      ('test_category_membership_arity_constraint_with_acquisition/Test Migration',))

  def testCategoryRelatedMembershipArityConstraint(self):
    """
    Take the test module and check whether the Category Related
    Membership Arity Constraint is there. Until a Base Category is set
    on the Test Module, the constraint should fail

    XXX: Test filter_parameter
    """
    constraint = self._getConstraintByReference(
      'test_category_related_membership_arity_constraint')

    self.assertNotEqual(None, constraint)
    self.assertEqual(1, len(constraint.checkConsistency(self.test_module)))

    self.test_module.setCategoryList(('gender/Test Migration',))
    self.tic()

    self.assertEqual([], constraint.checkConsistency(self.test_module))

  def testTALESConstraint(self):
    """
    Take the test module and check whether the TALES Constraint is
    there. Until the title of Test Module has been set to the expected
    value, the constraint should fail
    """
    self._checkConstraint('test_tales_constraint',
                          self.test_module.setTitle,
                          'my_tales_constraint_title')

  def testPropertyTypeValidityConstraint(self):
    """
    Take the test module and check whether the Property Type Validity
    Constraint is there, then set the title of Test Module to any
    value besides of a string. Until the title of Test Module has been
    set to any string, the constraint should fail
    """
    self.test_module.title = 123

    self._checkConstraint('test_property_type_validity_constraint',
                          self.test_module.setTitle,
                          'my_property_type_validity_constraint_title')

  def testConstraintAfterClosingZODBConnection(self):
    """
    Make sure that constraint works even if ZODB connection close.
    This test is added for the bug #20110628-ABAA76.
    """
    # Open new connection and add a new constraint.
    db = self.app._p_jar.db()
    tm = transaction.TransactionManager()
    con = db.open(transaction_manager=tm)
    app = con.root()['Application'].__of__(self.app.aq_parent)
    portal = app[self.getPortalName()]
    from Products.ERP5.ERP5Site import getSite, setSite
    old_site = getSite()
    setSite(portal)

    import erp5
    dummy = getattr(erp5.portal_type, 'TALES Constraint')(id='dummy')
    portal.portal_property_sheets.TestMigration._setObject('dummy', dummy)
    dummy = portal.portal_property_sheets.TestMigration.dummy
    dummy.edit(reference='test_dummy_constraint',
               expression='python: object.getTitle() == "my_tales_constraint_title"')
    dummy.Predicate_view()

    tm.commit()

    # Recreate class with a newly added constraint
    synchronizeDynamicModules(portal, force=True)
    # Load test_module
    getattr(portal, 'Test Migration').objectValues()
    # Then close this new connection.
    tm.abort()
    con.close()
    # This code depends on ZODB implementation.
    for i in db.pool.available[:]:
      if i[1] == con:
        db.pool.available.remove(i)
    db.pool.all.remove(con)
    del con

    # Back to the default connection.
    self.abort()
    self.app._p_jar._resetCache()
    setSite(old_site)

    # Call checkConsistency and make sure that ConnectionStateError does not occur.
    self.assert_(self.test_module.checkConsistency())

  def testAddEmptyProperty(self):
    """
    When users create properties in a PropertySheet, the property is
    first empty. Check that accessor generation can cope with such
    invalid properties
    """
    property_sheet_tool = self.portal.portal_property_sheets
    arrow = property_sheet_tool.Arrow
    person_module = self.portal.person_module
    person = person_module.newContent(portal_type="Person")

    # Action -> add Acquired Property
    arrow.newContent(portal_type="Acquired Property")
    # a user is doing this, so commit after each request
    self.commit()

    accessor = getattr(property_sheet_tool, "setTitle", None)
    # sites used to break at this point
    self.assertNotEquals(None, accessor)
    # try to create a Career, which uses Arrow Property Sheet
    try:
      person.newContent(portal_type="Career")
    except Exception:
      # Arrow property holder could not be created from the
      # invalid Arrow Property Sheet
      self.fail("Creating an empty Acquired Property raises an error")

    arrow.newContent(portal_type="Category Property")
    self.commit()
    try:
      person.newContent(portal_type="Career")
    except Exception:
      self.fail("Creating an empty Category Property raises an error")

    dynamic_category = arrow.newContent(portal_type="Dynamic Category Property")
    self.commit()
    try:
      person.newContent(portal_type="Career")
    except Exception:
      self.fail("Creating an empty Dynamic Category Property raises an error")

    arrow.newContent(portal_type="Property Existence Constraint")
    self.commit()
    try:
      person.newContent(portal_type="Career")
    except Exception:
      self.fail("Creating an empty Constraint raises an error")

  def testAddInvalidProperty(self):
    """
    Check that setting an invalid TALES Expression as a property
    attribute value does not raise any error

    XXX: For now, this test fails because the accessors generation
    going through Utils does catch errors when evaluating TALES
    Expression, but this will be addressed in per-property document
    accessors generation
    """
    arrow = self.portal.portal_property_sheets.Arrow
    person = self.portal.person_module.newContent(portal_type="Person")

    # be really nasty, and test that code is still foolproof (this
    # None value should never appear in an expression... unless the
    # method has a mistake)
    dynamic_category = arrow.newContent(
      portal_type="Dynamic Category Property",
      category_expression='python: ["foo", None, "region"]')

    self.commit()
    try:
      person.newContent(portal_type="Career")
    except Exception:
      self.fail("Creating a Category Expression with None as one of the "\
                "category ID raises an error")

    # Action -> add Acquired Property
    arrow.newContent(portal_type="Acquired Property",
                     acquisition_portal_type="python: ('foo', None)",
                     content_portal_type="python: ('goo', None)")
    # a user is doing this, so commit after each request
    self.commit()
    try:
      person.newContent(portal_type="Career")
    except Exception:
      self.fail("Creating an Acquired Property with invalid TALES expression "\
                "raises an error")

    # Check invalid syntax in TALES Expression, we check only for
    # DynamicCategoryProperty because it's exactly the same function
    # called for StandardProperty and AcquiredProperty, namely
    # evaluateExpressionFromString
    dynamic_category.setCategoryExpression('python: [')
    self.commit()
    try:
      person.newContent(portal_type="Career")
    except Exception:
      self.fail("Creating a Category Expression with syntax error raises "\
                "an error")

from Products.ERP5Type.Tool.ComponentTool import ComponentTool
ComponentTool._original_reset = ComponentTool.reset
ComponentTool._reset_performed = False

def assertResetNotCalled(*args, **kwargs):
  """
  Assert that reset has *not* been called, ignoring reset() which has not
  actually been done because force has not been specified (for example when
  reset is being called from __of__). When a Component is validated or
  modified after being validated, reset will always be forced anyway...

  This function is supposed to replace ComponentTool.reset() which is restored
  afterwards
  """
  reset_performed = ComponentTool._original_reset(*args, **kwargs)
  if reset_performed:
    raise AssertionError("reset should not have been performed")

  return reset_performed

def assertResetCalled(*args, **kwargs):
  """
  Assert that reset has been called, ignoring reset() which has not actually
  been done because force has not been specified (for example when reset is
  being called from __of__). When a Component is validated or modified after
  being validated, reset will always be forced anyway...

  This function is supposed to replace ComponentTool.reset() which is restored
  afterwards
  """
  reset_performed = ComponentTool._original_reset(*args, **kwargs)
  if reset_performed:
    ComponentTool._reset_performed = True

  return reset_performed

import abc

from Products.ERP5Type.mixin.component import ComponentMixin
from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
from App.config import getConfiguration

class _TestZodbComponent(SecurityTestCase):
  """
  Abstract class which defined convenient methods used by any Component Test
  and tests ran for all Component Test classes
  """
  __metaclass__ = abc.ABCMeta

  def getBusinessTemplateList(self):
    return ('erp5_base',)

  def afterSetUp(self):
    self._component_tool = self.portal.portal_components
    self._module = __import__(self._getComponentModuleName(),
                              fromlist=['erp5.component'])
    self._component_tool.reset(force=True,
                               reset_portal_type_at_transaction_boundary=True)

  def _newComponent(self, reference, text_content, version='erp5', id_=None):
    """
    Create new Component
    """
    full_id = '%s.%s.%s' % (self._getComponentModuleName(),
                            version + '_version',
                            reference)

    if id_ is not None:
      full_id += '.%s' % id_

    return self._component_tool.newContent(
      id=full_id,
      version=version,
      reference=reference,
      text_content=text_content,
      portal_type=self._component_portal_type)

  @abc.abstractmethod
  def _getComponentModuleName(self):
    """
    Abstract method defining ZODB Component top-level package name
    """

  def _getComponentFullModuleName(self, module_name):
    return self._getComponentModuleName() + '.' + module_name

  def failIfModuleImportable(self, module_name):
    """
    Check that the given module name is *not* importable (ZODB Components
    relies solely on import hooks)
    """
    try:
      self._importModule(module_name)
    except ImportError:
      pass
    else:
      self.fail("Component '%s' should not have been generated" % \
                  full_module_name)

      self._component_tool.reset(force=True,
                                 reset_portal_type_at_transaction_boundary=False)

  def assertModuleImportable(self,
                             module_name,
                             expected_default_version=None,
                             expected_additional_version_tuple=(),
                             reset=True):
    """
    Check that the given module name is importable (ZODB Components relies
    solely on import hooks)
    """
    try:
      self._importModule(module_name)
    except ImportError:
      self.fail("Component '%s' should have been generated" % \
                  full_module_name)

    if expected_default_version is not None:
      top_module_name = self._getComponentModuleName()
      top_module = __import__(top_module_name, level=0, fromlist=[top_module_name])

      # The module must be available in its default version
      self.assertHasAttribute(top_module, expected_default_version)
      self.assertHasAttribute(getattr(top_module, expected_default_version),
                              module_name)
      self.assertModuleImportable('%s.%s' % (expected_default_version, module_name),
                                  reset=False)

      for expected_version in expected_additional_version_tuple:
        # But other version with lowest attribute should not even be there
        # until there is an explicit import
        self.failIfHasAttribute(top_module, expected_version)

        self.assertModuleImportable('%s.%s' % (expected_version, module_name),
                                    reset=False)

        self.assertHasAttribute(top_module, expected_version)
        self.assertHasAttribute(getattr(top_module, expected_version), module_name)

    if reset:
      # There should be no side-effect by calling this function so reset
      # everything (it hide a bug in ExternalMethod when adding a new one, the
      # Extension Component was not loaded at all)
      self._component_tool.reset(force=True,
                                 reset_portal_type_at_transaction_boundary=False)

  def _importModule(self, module_name):
    return __import__(self._getComponentFullModuleName(module_name),
                      fromlist=[self._getComponentModuleName()],
                      level=0)

  def testValidateInvalidateDelete(self):
    """
    The new Component should only be in erp5.component.XXX when validated,
    otherwise it should not be importable at all
    """
    uf = self.portal.acl_users
    if not uf.getUserById('ERP5TypeTestCase_NonDeveloper'):
      uf._doAddUser('ERP5TypeTestCase_NonDeveloper',
                    '', ['Manager', 'Member', 'Assignee',
                         'Assignor', 'Author', 'Auditor', 'Associate'], [])

    test_component = self._newComponent(
      'TestValidateInvalidateComponent',
      'def foobar(*args, **kwargs):\n  return "ValidateInvalidate"')

    self.failIfUserCanPassWorkflowTransition('ERP5TypeTestCase_NonDeveloper',
                                             'validate_action',
                                             test_component)

    self.failIfUserCanPassWorkflowTransition('ERP5TypeTestCase',
                                             'invalidate_action',
                                             test_component)

    from Products.CMFCore.WorkflowCore import WorkflowException
    sm = getSecurityManager()
    try:
      self._loginAsUser('ERP5TypeTestCase_NonDeveloper')
      self.assertRaises(WorkflowException,
                        self.portal.portal_workflow.doActionFor,
                        test_component, 'delete_action')
    finally:
      setSecurityManager(sm)

    self.failIfModuleImportable('TestValidateInvalidateComponent')
    self.portal.portal_workflow.doActionFor(test_component, 'validate_action')
    self.tic()

    self.assertModuleImportable('TestValidateInvalidateComponent')

    self.failIfUserCanPassWorkflowTransition('ERP5TypeTestCase_NonDeveloper',
                                             'invalidate_action',
                                             test_component)

    self.failIfUserCanPassWorkflowTransition('ERP5TypeTestCase',
                                             'validate_action',
                                             test_component)

    self.assertRaises(WorkflowException,
                      self.portal.portal_workflow.doActionFor,
                      test_component, 'delete_action')

    self.portal.portal_workflow.doActionFor(test_component, 'invalidate_action')
    self.tic()
    self.failIfModuleImportable('TestValidateInvalidateComponent')

    self.portal.portal_workflow.doActionFor(test_component, 'validate_action')
    self.tic()
    self.assertModuleImportable('TestValidateInvalidateComponent')

    self.portal.portal_workflow.doActionFor(test_component, 'invalidate_action')
    self.tic()
    self.failIfModuleImportable('TestValidateInvalidateComponent')

    sm = getSecurityManager()
    try:
      self._loginAsUser('ERP5TypeTestCase_NonDeveloper')
      self.assertRaises(WorkflowException,
                        self.portal.portal_workflow.doActionFor,
                        test_component, 'delete_action')
    finally:
      setSecurityManager(sm)

    self.portal.portal_workflow.doActionFor(test_component, 'delete_action')
    self.tic()
    self.failIfModuleImportable('TestValidateInvalidateComponent')
    self.assertEqual([o for o in self.portal.portal_components.contentValues()
                      if o.getReference() == 'TestValidateInvalidateComponent'],
                     [])

  def testReferenceWithReservedKeywords(self):
    """
    Check whether checkConsistency has been properly implemented for checking
    Component Reference, e.g. no reserved keywords can be used.

    Also, check resets which should be performed when the Component is
    validated but not when an error was encountered (implemented in
    dynamic_class_generation_interaction_workflow)
    """
    valid_reference = 'TestReferenceWithReservedKeywords'
    ComponentTool.reset = assertResetCalled
    try:
      component = self._newComponent(valid_reference,
                                     'def foobar():\n  return 42')

      component.validate()
      self.tic()

      self.assertEqual(ComponentTool._reset_performed, True)
    finally:
      ComponentTool.reset = ComponentTool._original_reset
      ComponentTool._reset_performed = False

    self.assertEqual(component.getValidationState(), 'validated')
    self.assertEqual(component.checkConsistency(), [])
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(), [])
    self.assertEqual(component.getReference(), valid_reference)
    self.assertEqual(component.getReference(validated_only=True), valid_reference)
    self.assertModuleImportable(valid_reference)

    # Check that checkConsistency returns the proper error message for the
    # following reserved keywords
    invalid_reference_dict = {
      # '_version' could clash with Version package name
      'ReferenceReservedKeywords_version': ComponentMixin._message_invalid_reference,
      # Besides of clashing with protected attributes/methods, it does not
      # make sense to have reference starting with '_'
      '_ReferenceReservedKeywords': ComponentMixin._message_invalid_reference,
      # Clash with reset()
      'reset': ComponentMixin._message_invalid_reference,
      # PEP-302 required functions defined on top-level Component Package
      'find_module': ComponentMixin._message_invalid_reference,
      'load_module': ComponentMixin._message_invalid_reference}

    for invalid_reference, error_message in invalid_reference_dict.iteritems():
      # Reset should not be performed
      ComponentTool.reset = assertResetNotCalled
      try:
        component.setReference(invalid_reference)
        self.tic()
      finally:
        ComponentTool.reset = ComponentTool._original_reset

      # Should be in modified state as an error has been encountered
      self.assertEqual(component.getValidationState(), 'modified')
      self.assertEqual([m.getMessage().translate()
                         for m in component.checkConsistency()],
                        [error_message])
      self.assertEqual(component.getTextContentErrorMessageList(), [])
      self.assertEqual(component.getTextContentWarningMessageList(), [])
      self.assertEqual(component.getReference(), invalid_reference)
      self.assertEqual(component.getReference(validated_only=True), valid_reference)
      self._component_tool.reset(force=True,
                                 reset_portal_type_at_transaction_boundary=True)
      self.assertModuleImportable(valid_reference)

    # Set a valid reference and check that the Component is in validated state
    # and no error was raised
    ComponentTool.reset = assertResetCalled
    try:
      component.setReference(valid_reference)
      self.tic()

      self.assertEqual(ComponentTool._reset_performed, True)
    finally:
      ComponentTool.reset = ComponentTool._original_reset
      ComponentTool._reset_performed = False

    self.assertEqual(component.getValidationState(), 'validated')
    self.assertEqual(component.checkConsistency(), [])
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(), [])
    self.assertEqual(component.getReference(), valid_reference)
    self.assertEqual(component.getReference(validated_only=True), valid_reference)
    self.assertModuleImportable(valid_reference)

  def testVersionWithReservedKeywords(self):
    """
    Check whether checkConsistency has been properly implemented for checking
    Component version field, e.g. no reserved keywords can be used.

    Also, check resets which should be performed when the Component is
    validated but not when an error was encountered (implemented in
    dynamic_class_generation_interaction_workflow)
    """
    reference = 'TestVersionWithReservedKeywords'
    valid_version = 'erp5'
    ComponentTool.reset = assertResetCalled
    try:
      component = self._newComponent(reference,
                                     'def foobar():\n  return 42',
                                     valid_version)

      component.validate()
      self.tic()

      self.assertEqual(ComponentTool._reset_performed, True)
    finally:
      ComponentTool.reset = ComponentTool._original_reset
      ComponentTool._reset_performed = False

    self.assertEqual(component.getValidationState(), 'validated')
    self.assertEqual(component.checkConsistency(), [])
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(), [])
    self.assertEqual(component.getVersion(), valid_version)
    self.assertEqual(component.getVersion(validated_only=True), valid_version)
    self.assertModuleImportable(reference)

    # Check that checkConsistency returns the proper error message for the
    # following reserved keywords
    invalid_version_dict = {
      '': ComponentMixin._message_version_not_set,
      # Besides of clashing with protected attributes/methods, it does not
      # make sense to have reference starting with '_'
      '_TestVersionWithReservedKeywords': ComponentMixin._message_invalid_version}

    for invalid_version, error_message in invalid_version_dict.iteritems():
      # Reset should not be performed
      ComponentTool.reset = assertResetNotCalled
      try:
        component.setVersion(invalid_version)
        self.tic()
      finally:
        ComponentTool.reset = ComponentTool._original_reset

      # Should be in modified state as an error has been encountered
      self.assertEqual(component.getValidationState(), 'modified')
      self.assertEqual([m.getMessage().translate()
                         for m in component.checkConsistency()],
                        [error_message])
      self.assertEqual(component.getTextContentErrorMessageList(), [])
      self.assertEqual(component.getTextContentWarningMessageList(), [])
      self.assertEqual(component.getVersion(), invalid_version)
      self.assertEqual(component.getVersion(validated_only=True), valid_version)
      self._component_tool.reset(force=True,
                                 reset_portal_type_at_transaction_boundary=True)
      self.assertModuleImportable(reference)

    # Set a valid version and check that the Component is in validated state
    # and no error was raised
    ComponentTool.reset = assertResetCalled
    try:
      component.setVersion(valid_version)
      self.tic()

      self.assertEqual(ComponentTool._reset_performed, True)
    finally:
      ComponentTool.reset = ComponentTool._original_reset
      ComponentTool._reset_performed = False

    self.assertEqual(component.getValidationState(), 'validated')
    self.assertEqual(component.checkConsistency(), [])
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(), [])
    self.assertEqual(component.getVersion(), valid_version)
    self.assertEqual(component.getVersion(validated_only=True), valid_version)
    self.assertModuleImportable(reference)

  def testInvalidSourceCode(self):
    """
    Check whether checkConsistency has been properly implemented for checking
    Component source code field.

    Also, check resets which should be performed when the Component is
    validated but not when an error was encountered (implemented in
    dynamic_class_generation_interaction_workflow)
    """
    # Error/Warning properties must be set everytime the source code is
    # modified, even in Draft state
    component = self._newComponent('TestComponentWithSyntaxError', 'print "ok"')
    self.tic()
    self.assertEqual(component.checkConsistency(), [])
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(), [])

    component.setTextContent('import sys')
    self.tic()
    self.assertEqual(component.checkConsistency(), [])
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(),
                      ["W:  1,  0: Unused import sys (unused-import)"])

    component.setTextContent('import unexistent_module')
    self.tic()
    self.assertEqual(
      [m.getMessage().translate() for m in component.checkConsistency()],
      ["Error in Source Code: F:  1,  0: Unable to import 'unexistent_module' (import-error)"])
    self.assertEqual(component.getTextContentErrorMessageList(),
                      ["F:  1,  0: Unable to import 'unexistent_module' (import-error)"])
    self.assertEqual(component.getTextContentWarningMessageList(),
                      ["W:  1,  0: Unused import unexistent_module (unused-import)"])

    valid_code = 'def foobar():\n  return 42'
    ComponentTool.reset = assertResetCalled
    try:
      component.setTextContent(valid_code)
      component.validate()
      self.tic()

      self.assertEqual(ComponentTool._reset_performed, True)
    finally:
      ComponentTool.reset = ComponentTool._original_reset
      ComponentTool._reset_performed = False

    self.assertEqual(component.getValidationState(), 'validated')
    self.assertEqual(component.checkConsistency(), [])
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(), [])
    self.assertEqual(component.getTextContent(), valid_code)
    self.assertEqual(component.getTextContent(validated_only=True), valid_code)
    self.assertModuleImportable('TestComponentWithSyntaxError')

    # Check that checkConsistency returns the proper error message for the
    # following Python errors
    invalid_code_dict = (
      (None,
       # There could be no source code until validated, so checkConsistency()
       # is used instead
       [ComponentMixin._message_text_content_not_set],
       [],
       []),
      ('def foobar(*args, **kwargs)\n  return 42',
       ["Error in Source Code: E:  1,  0: invalid syntax (syntax-error)"],
       ["E:  1,  0: invalid syntax (syntax-error)"],
       []),
      # Make sure that foobar NameError is at the end to make sure that after
      # defining foobar function, it is not available at all
      ('foobar',
       ["Error in Source Code: E:  1,  0: Undefined variable 'foobar' (undefined-variable)"],
       ["E:  1,  0: Undefined variable 'foobar' (undefined-variable)"],
       ["W:  1,  0: Statement seems to have no effect (pointless-statement)"]))

    for (invalid_code,
         check_consistency_list,
         error_list,
         warning_list) in invalid_code_dict:
      # Reset should not be performed
      ComponentTool.reset = assertResetNotCalled
      try:
        component.setTextContent(invalid_code)
        self.tic()
      finally:
        ComponentTool.reset = ComponentTool._original_reset

      # Should be in modified state as an error has been encountered
      self.assertEqual(component.getValidationState(), 'modified')
      self.assertEqual([m.getMessage().translate()
                         for m in component.checkConsistency()],
                        check_consistency_list)
      self.assertEqual(component.getTextContentErrorMessageList(), error_list)
      self.assertEqual(component.getTextContentWarningMessageList(), warning_list)

      self.assertEqual(component.getTextContent(), invalid_code)
      self.assertEqual(component.getTextContent(validated_only=True), valid_code)
      self._component_tool.reset(force=True,
                                 reset_portal_type_at_transaction_boundary=True)
      self.assertModuleImportable('TestComponentWithSyntaxError')

    # Set a valid source code and check that the Component is in validated
    # state and no error was raised
    ComponentTool.reset = assertResetCalled
    try:
      component.setTextContent(valid_code)
      self.tic()

      self.assertEqual(ComponentTool._reset_performed, True)
    finally:
      ComponentTool.reset = ComponentTool._original_reset
      ComponentTool._reset_performed = False

    self.assertEqual(component.getValidationState(), 'validated')
    self.assertEqual(component.checkConsistency(), [])
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(), [])
    self.assertEqual(component.getTextContent(), valid_code)
    self.assertEqual(component.getTextContent(validated_only=True), valid_code)
    self.assertModuleImportable('TestComponentWithSyntaxError')

  def testImportVersionedComponentOnly(self):
    """
    Most of the time, erp5.component.XXX.COMPONENT_NAME is imported but
    sometimes it may be useful to import a specific version of a Component,
    available as erp5.component.XXX.VERSION_version.COMPONENT_NAME.
    """
    component = self._newComponent(
      'TestImportedVersionedComponentOnly',
      """def foo(*args, **kwargs):
  return "TestImportedVersionedComponentOnly"
""")

    component.validate()
    self.tic()

    top_module_name = self._getComponentModuleName()

    # Create a new Component which uses a specific version of the previously
    # created Component
    component_import = self._newComponent(
      'TestImportVersionedComponentOnly',
      """from %s.erp5_version.TestImportedVersionedComponentOnly import foo

def bar(*args, **kwargs):
  return 'Bar' + foo(*args, **kwargs)
""" % top_module_name)

    component_import.validate()
    self.tic()

    # Versioned package and its alias must be available
    self.assertModuleImportable('TestImportVersionedComponentOnly',
                                expected_default_version='erp5_version')

    # Versioned Component of imported Component must be importable and check
    # later that the module has not been added to the top-level package
    self.assertModuleImportable('erp5_version.TestImportedVersionedComponentOnly')

    top_module = __import__(top_module_name, level=0,
                            fromlist=[top_module_name])

    self._importModule('erp5_version.TestImportedVersionedComponentOnly')

    # Function defined in versioned Component must be available and callable
    self.assertHasAttribute(
      top_module.erp5_version.TestImportedVersionedComponentOnly, 'foo')

    self.assertEqual(
      top_module.erp5_version.TestImportedVersionedComponentOnly.foo(),
      'TestImportedVersionedComponentOnly')

    # The alias module on the top-level package must not have been created as
    # only the versioned Component has been used
    self.failIfHasAttribute(top_module, 'TestImportedVersionedComponentOnly')

    # As well as functions defined on unversioned Component
    self._importModule('TestImportVersionedComponentOnly')
    self.assertHasAttribute(top_module.TestImportVersionedComponentOnly, 'bar')

    self.assertEqual(
      top_module.TestImportVersionedComponentOnly.bar(),
      'BarTestImportedVersionedComponentOnly')

  def testVersionPriority(self):
    """
    Check whether Version priorities properly works by adding and removing
    version priorities on ERP5Site and checking whether the proper Component
    is loaded
    """
    component_erp5_version = self._newComponent(
      'TestVersionPriority',
      """def function_foo(*args, **kwargs):
  return "TestERP5VersionPriority"
""")

    component_erp5_version.validate()
    self.tic()

    component_foo_version = self._newComponent(
      'TestVersionPriority',
      """def function_foo(*args, **kwargs):
  return "TestFooVersionPriority"
""",
      'foo')

    component_foo_version.validate()
    self.tic()

    self.assertModuleImportable('TestVersionPriority',
                                expected_default_version='erp5_version')

    # Component for 'foo_version' must not be importable as 'foo' has not been
    # added to ERP5Site version priorities
    self.failIfModuleImportable('foo_version.TestVersionPriority')

    top_module_name = self._getComponentModuleName()
    top_module = __import__(top_module_name, level=0,
                            fromlist=[top_module_name])

    self._importModule('TestVersionPriority')
    self.assertHasAttribute(top_module.TestVersionPriority, 'function_foo')
    self.assertEqual(top_module.TestVersionPriority.function_foo(),
                      "TestERP5VersionPriority")

    from Products.ERP5.ERP5Site import getSite
    site = getSite()
    ComponentTool.reset = assertResetCalled
    priority_tuple = site.getVersionPriorityList()
    try:
      # Add 'foo' version with a higher priority as 'erp5' version and check
      # whether 'foo' version of the Component is used and not erp5 version
      site.setVersionPriorityList(('foo | 99.0',) + priority_tuple)
      self.tic()

      self.assertEqual(ComponentTool._reset_performed, True)

      self.assertModuleImportable(
        'TestVersionPriority',
        expected_default_version='foo_version',
        expected_additional_version_tuple=('erp5_version',))

      self._importModule('TestVersionPriority')
      self.assertHasAttribute(top_module.TestVersionPriority, 'function_foo')
      self.assertEqual(top_module.TestVersionPriority.function_foo(),
                        "TestFooVersionPriority")

    finally:
      ComponentTool.reset = ComponentTool._original_reset
      site.setVersionPriorityList(priority_tuple)
      self.tic()

  def testDeveloperRoleSecurity(self):
    """
    Only Developer Role must be able to manage Components

    XXX-arnau: test with different users and workflows
    """
    component = self._newComponent('TestDeveloperRoleSecurity',
                                   'def foo():\n  print "ok"')

    self.tic()

    # Anonymous should not even be able to view/access Component Tool
    self.failIfUserCanViewDocument(None, self._component_tool)
    self.failIfUserCanAccessDocument(None, self._component_tool)
    self.failIfUserCanViewDocument(None, component)
    self.failIfUserCanAccessDocument(None, component)

    user_id = 'ERP5TypeTestCase'

    self.assertUserCanChangeLocalRoles(user_id, self._component_tool)
    self.assertUserCanModifyDocument(user_id, self._component_tool)
    self.assertUserCanDeleteDocument(user_id, self._component_tool)
    self.assertUserCanChangeLocalRoles(user_id, component)
    self.assertUserCanDeleteDocument(user_id, component)

    getConfiguration().product_config['erp5'].developer_list = []

    # Component Tool and the Component should be viewable by Manager
    self.assertUserCanViewDocument(user_id, self._component_tool)
    self.assertUserCanAccessDocument(user_id, self._component_tool)
    self.assertUserCanViewDocument(user_id, component)
    self.assertUserCanAccessDocument(user_id, component)

    # But nothing else should be permitted on Component Tool nor Component
    self.failIfUserCanAddDocument(user_id, self._component_tool)
    self.failIfUserCanModifyDocument(user_id, self._component_tool)
    self.failIfUserCanDeleteDocument(user_id, self._component_tool)
    self.failIfUserCanModifyDocument(user_id, component)
    self.failIfUserCanDeleteDocument(user_id, component)
    self.failIfUserCanChangeLocalRoles(user_id, component)

    getConfiguration().product_config['erp5'].developer_list = [user_id]

    self.assertUserCanChangeLocalRoles(user_id, self._component_tool)
    self.assertUserCanModifyDocument(user_id, self._component_tool)
    self.assertUserCanDeleteDocument(user_id, self._component_tool)
    self.assertUserCanChangeLocalRoles(user_id, component)
    self.assertUserCanModifyDocument(user_id, component)
    self.assertUserCanDeleteDocument(user_id, component)

  def testValidateComponentWithSameReferenceVersionAlreadyValidated(self):
    reference = 'ValidateComponentWithSameReferenceVersionAlreadyValidated'

    component = self._newComponent(reference, 'def foo():\n  print "ok"')
    self.commit()
    component.validate()
    self.tic()

    component_dup = self._newComponent(reference, 'def foo():\n  print "ok"',
                                       id_='duplicated')

    self.tic()

    from Products.DCWorkflow.DCWorkflow import ValidationFailed
    self.assertRaises(ValidationFailed,
                      self.portal.portal_workflow.doActionFor,
                      component_dup, 'validate_action')

    self.assertEqual(component_dup.getValidationState(), 'draft')

    component_dup.setReference(reference + '_copy')
    component_dup.validate()
    self.tic()

    component_dup.setReference(reference)
    self.tic()
    self.assertEqual(component_dup.getValidationState(), 'modified')
    self.assertEqual(component_dup.getReference(), reference)
    self.assertEqual(component_dup.getReference(validated_only=True),
                      reference + '_copy')

    component_dup.invalidate()
    self.tic()
    component_dup.setReference(reference)
    self.assertRaises(ValidationFailed,
                      self.portal.portal_workflow.doActionFor,
                      component_dup, 'validate_action')

    self.assertEqual(component_dup.getValidationState(), 'invalidated')

from Products.ERP5Type.Core.ExtensionComponent import ExtensionComponent

class TestZodbExtensionComponent(_TestZodbComponent):
  """
  Tests specific to ZODB Extension Component (previously defined in bt5 and
  installed on the filesystem in $INSTANCE_HOME/Extensions)
  """
  _component_portal_type = 'Extension Component'

  def _getComponentModuleName(self):
    return ExtensionComponent._getDynamicModuleNamespace()

  def testExternalMethod(self):
    """
    Check that ExternalMethod monkey-patch to use ZODB Components works well
    by creating a new External Method and then a Python Script to call it
    """
    module = 'TestExternalMethodComponent'
    test_component = self._newComponent(module, """# a method
class foobar:
  def f(self, x, y=1, *z):
    return sum(z, x + y)
foobar = foobar().f
""")

    test_component.validate()
    self.tic()

    self.assertModuleImportable(module)

    # Add an External Method using the Extension Component defined above
    from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
    manage_addExternalMethod(self.portal,
                             'TestExternalMethod',
                             'title',
                             module,
                             'foobar')

    self.commit()

    external_method = self.portal.TestExternalMethod
    external_method._p_deactivate()
    self.assertFalse(hasattr(external_method, '_v_f'))
    self.assertEqual(external_method(1, 2, 3, 4), 10)
    self.assertTrue(hasattr(external_method, '_v_f'))

    # Check that the External Method returns expected result through Publisher
    base = self.portal.getPath()
    for query in 'x:int=-24&y:int=66', 'x:int=41':
      path = '%s/TestExternalMethod?%s' % (base, query)
      self.assertEqual(self.publish(path).getBody(), '42')

    # Test from a Python Script
    createZODBPythonScript(self.portal.portal_skins.custom,
      'TestPythonScript', '**kw', 'return context.TestExternalMethod(**kw)')
    self.assertEqual(self.portal.TestPythonScript(x=2), 3)

    # Check that the External Method is reloaded automatically if the component
    # changes. We also test that the context is passed automatically.
    test_component.setTextContent("""# a function
def foobar(self, a, b="portal_type"):
  return getattr(getattr(self, a), b)
""")
    self.commit()

    external_method.manage_setGuard({'guard_roles': 'Member'})
    self.assertEqual(self.portal.TestPythonScript(a='portal_ids'), 'Id Tool')
    self.assertEqual(self.publish(base + '/portal_types/TestExternalMethod?'
      'a=Types Tool&b=type_class', 'ERP5TypeTestCase:').getBody(), 'TypesTool')

    sm = getSecurityManager()
    try:
      noSecurityManager()
      self.assertRaises(Forbidden, external_method, "portal_types")
      external_method.manage_setGuard({})
      self.assertEqual(external_method('portal_types'), 'Types Tool')
    finally:
      setSecurityManager(sm)

    # Invalidate the Extension Component and check that it's not callable
    # anymore
    test_component.invalidate()
    self.commit()

    self.assertRaisesRegexp(NotFound, "The specified module,"
        " '%s', couldn't be found." % module, external_method)

    # Check fallback on FS, and also callable objects.
    cfg = getConfiguration()
    assert not hasattr(cfg, "extensions")
    cfg.extensions = tempfile.mkdtemp()
    try:
      with open(os.path.join(cfg.extensions, module + '.py'), "w") as f:
        f.write("foobar = lambda **kw: sorted(kw.iteritems())")
      self.assertEqual(external_method(z=1, a=0), [('a', 0), ('z', 1)])
    finally:
      shutil.rmtree(cfg.extensions)
      del cfg.extensions

from Products.ERP5Type.Core.DocumentComponent import DocumentComponent

class TestZodbDocumentComponent(_TestZodbComponent):
  """
  Tests specific to ZODB Document Component. This is only for Document
  previously defined in bt5 and installed on the filesystem in
  $INSTANCE_HOME/Document. Later on, Product Documents will also be migrated
  """
  _component_portal_type = 'Document Component'

  def _getComponentModuleName(self):
    return DocumentComponent._getDynamicModuleNamespace()

  def testAssignToPortalTypeClass(self):
    """
    Create a new Document Component inheriting from Person Document and try to
    assign it to Person Portal Type, then create a new Person and check
    whether it has been successfully added to its Portal Type class bases and
    that the newly-defined function on ZODB Component can be called as well as
    methods from Person Document
    """
    from Products.ERP5.Document.Person import Person as PersonDocument

    self.failIfModuleImportable('TestPortalType')

    # Create a new Document Component inheriting from Person Document which
    # defines only one additional method (meaningful to make sure that the
    # class (and not the module) has been added to the class when the
    # TypeClass is changed)
    test_component = self._newComponent(
      'TestPortalType',
      """
from Products.ERP5Type.Document.Person import Person

class TestPortalType(Person):
  def test42(self):
    return 42
""")

    test_component.validate()
    self.tic()

    # As TestPortalType Document Component has been validated, it should now
    # be available
    self.assertModuleImportable('TestPortalType')

    person_type = self.portal.portal_types.Person
    person_type_class = person_type.getTypeClass()
    self.assertEqual(person_type_class, 'Person')

    # Create a new Person
    person_module = self.portal.person_module
    person = person_module.newContent(id='Foo Bar', portal_type='Person')
    self.assertTrue(PersonDocument in person.__class__.mro())

    # There is no reason that TestPortalType Document Component has been
    # assigned to a Person
    self.failIfHasAttribute(person, 'test42')
    self.failIfHasAttribute(self._module, 'TestPortalType')
    for klass in person.__class__.mro():
      self.assertNotEqual(klass.__name__, 'TestPortalType')

    # Reset Portal Type classes to ghost to make sure that everything is reset
    self._component_tool.reset(force=True,
                               reset_portal_type_at_transaction_boundary=True)

    # TestPortalType must be available in type class list
    self.assertTrue('TestPortalType' in person_type.getDocumentTypeList())
    try:
      person_type.setTypeClass('TestPortalType')
      self.commit()

      self.assertHasAttribute(person, 'test42')
      self.assertEqual(person.test42(), 42)

      # The Portal Type class should not be in ghost state by now as we tried
      # to access test42() defined in TestPortalType Document Component
      self.assertHasAttribute(self._module, 'TestPortalType')
      self.assertTrue(self._module.TestPortalType.TestPortalType in person.__class__.mro())
      self.assertTrue(PersonDocument in person.__class__.mro())

    finally:
      person_type.setTypeClass('Person')
      self.commit()

  def testDocumentWithImport(self):
    """
    Create two new Components and check whether one can import the other one
    after the latter has been validated
    """
    self.failIfModuleImportable('TestDocumentWithImport')
    self.failIfModuleImportable('TestDocumentImported')

    # Create a new Document Component inheriting from Person Document which
    # defines only one additional method (meaningful to make sure that the
    # class (and not the module) has been added to the class when the
    # TypeClass is changed)
    test_imported_component = self._newComponent(
      'TestDocumentImported',
      """
from Products.ERP5Type.Document.Person import Person

class TestDocumentImported(Person):
  def test42(self):
    return 42
""")

    test_component = self._newComponent(
      'TestDocumentWithImport',
      """
from Products.ERP5.Document.Person import Person
from erp5.component.document.TestDocumentImported import TestDocumentImported

class TestDocumentWithImport(TestDocumentImported):
  def test42(self):
    return 4242
""")

    self.tic()

    self.failIfModuleImportable('TestDocumentWithImport')
    self.failIfModuleImportable('TestDocumentImported')

    test_imported_component.validate()
    test_component.validate()
    self.tic()

    # TestPortalWithImport must be imported first to check if
    # TestPortalImported could be imported without being present before
    self.assertModuleImportable('TestDocumentWithImport')
    self.assertModuleImportable('TestDocumentImported')

from Products.ERP5Type.Core.TestComponent import TestComponent

class TestZodbTestComponent(_TestZodbComponent):
  """
  Tests specific to ZODB Test Component (known as Live Tests, and previously
  defined in bt5 and installed in $INSTANCE_HOME/test)
  """
  _component_portal_type = 'Test Component'

  def _getComponentModuleName(self):
    return TestComponent._getDynamicModuleNamespace()

  def testRunLiveTest(self):
    """
    Create a new ZODB Test Component and try to run it as a live tests and
    check the expected output
    """
    # First try with a test which run successfully
    source_code = '''
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class Test(ERP5TypeTestCase):
  def getTitle(self):
    return "SampleTest"

  def getBusinessTemplateList(self):
    return ('erp5_core',)

  def _setUpDummyMailHost(self):
    """
    Dummy mail host has already been set up when running tests
    """
    pass

  def _restoreMailHost(self):
    """
    Dummy mail host has already been set up when running tests
    """
    pass

  def test_01_sampleTest(self):
    self.assertEqual(0, 0)
'''

    component = self._newComponent('testRunLiveTest', source_code)
    component.validate()
    self.tic()

    self.assertEqual(component.getValidationState(), 'validated')
    self.assertModuleImportable('testRunLiveTest')
    self._component_tool.reset(force=True,
                               reset_portal_type_at_transaction_boundary=True)

    # ERP5TypeLiveTestCase.runLiveTest patches ERP5TypeTestCase bases, thus it
    # needs to be restored after calling runLiveTest
    base_tuple = ERP5TypeTestCase.__bases__
    try:
      self._component_tool.runLiveTest('testRunLiveTest')
    finally:
      ERP5TypeTestCase.__bases__ = base_tuple

    # assertRegexpMatches is only available from Python >= 2.7
    import re
    output = self._component_tool.readTestOutput()
    self.assertNotEqual(re.search('Ran 1 test.*OK', output, re.DOTALL), None,
                        "Expected 'Ran 1 test.*OK' in '%s'" % output)


    # Secondly, add a test which will always fail
    source_code += '''
  def test_02_sampleTestWithFailure(self):
    self.assertEqual(0, 1)
'''

    component.setTextContent(source_code)
    self.tic()

    self.assertEqual(component.getValidationState(), 'validated')
    self.assertModuleImportable('testRunLiveTest')
    self._component_tool.reset(force=True,
                               reset_portal_type_at_transaction_boundary=True)

    base_tuple = ERP5TypeTestCase.__bases__
    try:
      self._component_tool.runLiveTest('testRunLiveTest')
    finally:
      ERP5TypeTestCase.__bases__ = base_tuple

    # assertRegexpMatches is only available from Python >= 2.7
    import re
    output = self._component_tool.readTestOutput()
    expected_msg_re_str = 'Ran 2 tests.*FAILED \(failures=1\)'
    self.assertNotEqual(re.search(expected_msg_re_str, output, re.DOTALL), None,
                        "Expected '%s' in '%s'" % (expected_msg_re_str, output))

  def testERP5Broken(self):
    # Create a broken ghost object
    import erp5.portal_type
    name = self._testMethodName
    types_tool = self.portal.portal_types
    ptype = types_tool.newContent(name, type_class="File")
    file = ptype.constructInstance(self.portal, name, data="foo")
    self.assertEqual(file.size, 3)
    self.commit()
    try:
      self.portal._p_jar.cacheMinimize()
      del file
      delattr(erp5.portal_type, name)
      ptype.setTypeClass(name)
      self.commit()
      file = self.portal.__dict__[name]
      self.assertTrue(isinstance(file, InitGhostBase))
      # Check that the class is unghosted before resolving __setattr__
      self.assertRaises(BrokenModified, setattr, file, "size", 0)
      self.assertTrue(isinstance(file, ERP5BaseBroken))
      self.assertEqual(file.size, 3)
    finally:
      self.portal._delObject(name)
      types_tool._delObject(name)
      self.commit()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPortalTypeClass))
  suite.addTest(unittest.makeSuite(TestZodbPropertySheet))
  suite.addTest(unittest.makeSuite(TestZodbExtensionComponent))
  suite.addTest(unittest.makeSuite(TestZodbDocumentComponent))
  suite.addTest(unittest.makeSuite(TestZodbTestComponent))
  return suite
