# -*- coding: utf-8 -*-
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
import warnings
import re
import sys

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
import six

class TestPortalTypeClass(ERP5TypeTestCase):
  def getBusinessTemplateList(self):
    return 'erp5_base',

  def testMigrateOldObject(self):
    """
    Check migration of persistent objects with non-erp5.portal_type classes
    (which used to be the full module name and not only the class name)
    """
    from erp5.component.document.Person import Person
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
        migrated and 'erp5.portal_type' or 'erp5.component.document.erp5_version.Person')
      self.assertEqual(klass.__name__, 'Person')
      self.assertEqual(klass.__setstate__ is Persistent.__setstate__, migrated)

    # Import a .xml containing a Person created with the full module name
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
    # object
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

      self.assertNotEqual(getattr(person, 'asText', None), None)
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

      self.assertNotEqual(getattr(person, 'getCorporateName', None), None)
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
    self.assertNotIn('IForTest', self.portal.portal_types.getInterfaceTypeList())
    from Products.ERP5Type import interfaces
    interfaces.IForTest = IForTest
    self.assertIn('IForTest', self.portal.portal_types.getInterfaceTypeList())

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
    self.assertNotIn(IForTest, implemented_by)
    InterfaceTestType.loadClass()

    implemented_by = list(implementedBy(InterfaceTestType))
    self.assertTrue(IForTest in implemented_by,
                    'IForTest not in %s' % implemented_by)

    InterfaceTestType.restoreGhostState()
    implemented_by = list(implementedBy(InterfaceTestType))
    self.assertNotIn(IForTest, implemented_by)

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
    self.assertNotIn('constraints', erp5.portal_type.Person.__dict__)

    getattr(erp5.portal_type.Person, 'constraints')
    self.assertTrue(not erp5.portal_type.Person.__isghost__)
    self.assertIn('constraints', erp5.portal_type.Person.__dict__)

    synchronizeDynamicModules(self.portal, force=True)
    self.assertTrue(erp5.portal_type.Person.__isghost__)
    self.assertNotIn('_categories', erp5.portal_type.Person.__dict__)

    getattr(erp5.portal_type.Person, '_categories')
    self.assertTrue(not erp5.portal_type.Person.__isghost__)
    self.assertIn('_categories', erp5.portal_type.Person.__dict__)

  def testWorkflowHistoryAccessor(self):
    person = self.portal.person_module.newContent(portal_type='Person')

    from Products.ERP5Type.Utils import UpperCase
    for transition_id in ('delete',
                          'delete_action',
                          'invalidate',
                          'invalidate_action',
                          'validate',
                          'validate_action'):
      method_id = 'get%sTransitionDate' % UpperCase(transition_id)
      self.assertNotEqual(getattr(person, method_id, None), None)
      self.assertEqual(getattr(person, method_id)('hoge'), 'hoge')

      list_method_id = 'get%sTransitionDateList' % UpperCase(transition_id)
      self.assertNotEqual(getattr(person, list_method_id, None), None)
      self.assertEqual(getattr(person, list_method_id)('hoge'), 'hoge')

    person.validate()
    self.assertEqual(len(person.getInvalidateTransitionDateList()), 0)
    validate_date_list = person.getValidateTransitionDateList()
    self.assertEqual(len(validate_date_list), 1)
    self.assertEqual(
      sorted([ workflow_history_dict['time']
               for workflow_history_dict in person.workflow_history['validation_workflow']
               if workflow_history_dict['action'] == 'validate' ]),
      validate_date_list)
    self.assertEqual(person.getValidateTransitionDate(), validate_date_list[0])

    person.invalidate()
    invalidate_date_list = person.getInvalidateTransitionDateList()
    self.assertEqual(len(invalidate_date_list), 1)
    self.assertEqual(
      sorted([ workflow_history_dict['time']
               for workflow_history_dict in person.workflow_history['validation_workflow']
               if workflow_history_dict['action'] == 'invalidate' ]),
      invalidate_date_list)
    self.assertEqual(person.getInvalidateTransitionDate(), invalidate_date_list[0])
    self.assertEqual(person.getValidateTransitionDateList(), validate_date_list)

    person.validate()
    self.assertEqual(person.getInvalidateTransitionDateList(), invalidate_date_list)
    validate_date_list = person.getValidateTransitionDateList()
    self.assertEqual(len(validate_date_list), 2)
    self.assertEqual(
      sorted([ workflow_history_dict['time']
               for workflow_history_dict in person.workflow_history['validation_workflow']
               if workflow_history_dict['action'] == 'validate' ]),
      validate_date_list)
    self.assertEqual(person.getValidateTransitionDate(), validate_date_list[-1])

  def testNoPortalTypeAccessorGeneratedOnPartiallyGeneratedPortalTypeClass(self):
    """
    Test for `is_partially_generated` ({lazy_class,portal_type_class}.py):
    Portal Type accessors must not be generated on a partially loaded Portal
    Type class (eg "inner" class)
    """
    from Products.ERP5Type.dynamic.lazy_class import PortalTypeMetaClass
    PortalTypeMetaClass_generatePortalTypeAccessors = PortalTypeMetaClass.generatePortalTypeAccessors
    def generatePortalTypeAccessors(cls, *args, **kw):
      assert len(cls.__bases__) > 2
      return PortalTypeMetaClass_generatePortalTypeAccessors(cls, *args, **kw)
    try:
      PortalTypeMetaClass.generatePortalTypeAccessors = generatePortalTypeAccessors
      self.portal.portal_types.resetDynamicDocuments()
      import erp5.portal_type
      getattr(erp5.portal_type, 'Document Component').loadClass()
    finally:
      PortalTypeMetaClass.generatePortalTypeAccessors = PortalTypeMetaClass_generatePortalTypeAccessors

class TestZodbPropertySheet(ERP5TypeTestCase):
  """
  XXX: WORK IN PROGRESS
  """


  def getBusinessTemplateList(self):
    return 'erp5_core_proxy_field_legacy', 'erp5_base'

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

    self.assertNotIn('TestMigration', person_type.getTypePropertySheetList())

    new_person = None
    try:
      # Assign ZODB test Property Sheet to the existing Person type
      # and create a new Person, this should generate the test
      # accessor holder which should be in the Person type inheritance
      person_type.setTypePropertySheetList('TestMigration')

      self.commit()

      self.assertIn('TestMigration', person_type.getTypePropertySheetList())

      # The accessor holder will be generated once the new Person will
      # be created as Person type has test Property Sheet
      self.failIfHasAttribute(erp5.accessor_holder.property_sheet,
                              'TestMigration')

      new_person = portal.person_module.newContent(
        id='testAssignZodbPropertySheet', portal_type='Person')

      self.assertHasAttribute(erp5.accessor_holder.property_sheet,
                              'TestMigration')

      self.assertIn(erp5.accessor_holder.property_sheet.TestMigration, \
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

    self.assertNotIn('TestMigration', person_type.getTypePropertySheetList())

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
    self.assertTrue(self.test_module.checkConsistency())

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
    self.assertNotEqual(None, accessor)
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

  def testCategoryValueRelationShowsWarningIfStringIsPassedAsParameter(self):
    person_module = self.portal.person_module
    person = person_module.newContent()

    def _testDeprecationWarning(method, *args, **kw):
      with warnings.catch_warnings(record=True) as warning_list:
       warnings.simplefilter("always")
       method(*args, **kw)
      warning, = warning_list
      self.assertTrue(issubclass(warning.category, DeprecationWarning))
      self.assertEqual(
        str(warning.message),
        "Only objects should be passed to value accessors",
      )

    # Passing a string to a Value setter should raise
    organisation = self.portal.organisation_module.newContent()
    _testDeprecationWarning(
      person.setSubordinationValue,
      organisation.getRelativeUrl(),
    )
    _testDeprecationWarning(
      person_module.newContent,
      subordination_value=organisation.getRelativeUrl(),
    )

    # Same test but with a category instead of an object
    social_title_value = self.portal.portal_categories.social_title.newContent(id='Mme')
    _testDeprecationWarning(
      person.setSocialTitleValue,
      social_title_value.getRelativeUrl(),
    )

  def testCategoryRelationRaisesIfValueisPassedAsParameter(self):
    person_module = self.portal.person_module
    person = person_module.newContent()

    # Passing an ERP5 object to a not-Value setter should raise
    with self.assertRaises(TypeError):
      organisation = self.portal.organisation_module.newContent()
      person.setSubordination(organisation)
      person_module.newContent(
        subordination=organisation,
      )

    # Same test with a category instead of an object
    social_title_value = self.portal.portal_categories.social_title.newContent(id='Mr')
    with self.assertRaises(TypeError):
      person.setSocialTitle(social_title_value)

    with self.assertRaises(TypeError):
      organisation = self.portal.organisation_module.newContent()
      if six.PY2:
        # Passing a unicode object to a not-Value setter should raise
        person.setSubordination(six.text_type(organisation.getRelativeUrl()))
      else:
        # Passing a bytes object to a not-Value setter should raise
        person.setSubordination(organisation.getRelativeUrl().encode())


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

from Products.ERP5Type.mixin.component import ComponentMixin
from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
from App.config import getConfiguration
from Products.ERP5Type.Core.ModuleComponent import ModuleComponent

class TestZodbModuleComponent(SecurityTestCase):
  """
  Tests for ZODB Module Component (base class of all other Component
  classes)
  """
  _portal_type = 'Module Component'
  _document_class = ModuleComponent

  def getBusinessTemplateList(self):
    return ('erp5_base',)

  def afterSetUp(self):
    self._component_tool = self.portal.portal_components
    self._module = __import__(self._document_class._getDynamicModuleNamespace(),
                              fromlist=['erp5.component'] if six.PY2 else ['erp5'])
    self._component_tool.reset(force=True,
                               reset_portal_type_at_transaction_boundary=True)

  def _generateReference(self, base_name):
    return base_name

  def _getValidSourceCode(self, *_):
    return '''def foobar(*args, **kwargs):
  return 'Anything'
'''

  def _newComponent(self, reference, text_content=None, version='erp5', id_=None):
    """
    Create new Component
    """
    if id_ is None:
      id_ = '%s.%s.%s' % (self._document_class.getIdPrefix(), version, reference)

    if text_content is None:
      text_content = self._getValidSourceCode(reference)

    return self._component_tool.newContent(
      id=id_,
      version=version,
      reference=reference,
      text_content=text_content,
      portal_type=self._portal_type)

  def _getComponentFullModuleName(self, module_name, version=None):
    if version is None:
      return (self._document_class._getDynamicModuleNamespace() + '.' +
              module_name)
    else:
      return (self._document_class._getDynamicModuleNamespace() + '.' +
              version + '_version' + '.' + module_name)

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
      self.fail("Component '%s' should not have been generated" %
                self._getComponentFullModuleName(module_name))

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
      self.fail("Component '%s' should have been generated" %
                self._getComponentFullModuleName(module_name))

    if expected_default_version is not None:
      top_module_name = self._document_class._getDynamicModuleNamespace()
      top_module = __import__(
        top_module_name,
        level=0,
        fromlist=[top_module_name] if six.PY2 else ['erp5'])

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
    module_name = self._getComponentFullModuleName(module_name)
    module = __import__(
      module_name,
      fromlist=[self._document_class._getDynamicModuleNamespace()]
        if six.PY2 else ['erp5'],
      level=0)
    self.assertIn(module_name, sys.modules)
    return module

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

    reference = self._generateReference('TestValidateInvalidateComponent')
    test_component = self._newComponent(reference)

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

    self.failIfModuleImportable(reference)
    self.portal.portal_workflow.doActionFor(test_component, 'validate_action')
    self.tic()

    self.assertModuleImportable(reference)

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
    self.assertModuleImportable(reference)

    self.portal.portal_workflow.doActionFor(test_component, 'invalidate_action')
    self.tic()
    self.failIfModuleImportable(reference)

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
    self.failIfModuleImportable(reference)
    self.assertEqual([o for o in self.portal.portal_components.contentValues()
                      if o.getReference() == reference],
                     [])

  def testInvalidId(self):
    """
    Check whether checkConsistency has been properly implemented for checking
    Component ID which should follow the format 'getIdPrefix().VERSION.REFERENCE'
    """
    valid_reference = self._generateReference("TestWithInvalidId")
    component = self._newComponent(valid_reference)
    self.tic()
    self.assertEqual(component.checkConsistency(), [])

    valid_id_prefix = self._document_class.getIdPrefix()
    valid_id = component.getId()
    valid_version = component.getVersion()
    for invalid_id in ("INVALID_PREFIX.%s.%s" % (valid_version, valid_reference),
                       "%s.INVALID_VERSION.%s" % (valid_id_prefix, valid_reference),
                       "%s.%s.INVALID_REFERENCE" % (valid_id_prefix, valid_version)):
      component.setId(invalid_id)
      self.tic()
      self.assertEqual(
        [m.getMessage().translate() for m in component.checkConsistency()],
        [self.portal.Base_translateString(ComponentMixin._message_invalid_id,
                                          mapping={'id_prefix': valid_id_prefix})])

      component.setId(valid_id)
      self.tic()
      self.assertEqual(component.checkConsistency(), [])


  def testWorkflowErrorMessage(self):
    """Check that validation error messages are stored in workflow
    """
    component = self._newComponent(self._generateReference('WorkflowErrorMessage'))
    valid_id = component.getId()
    self.tic()
    component.setId('wrong')
    from Products.ERP5Type.Core.Workflow import ValidationFailed
    with self.assertRaises(ValidationFailed):
      self.portal.portal_workflow.doActionFor(component, 'validate_action')
    last_error_message = str(
        self.portal.portal_workflow.getInfoFor(
            component, 'history',
            wf_id='component_validation_workflow')[-1]['error_message'][0])
    self.assertEqual(
        last_error_message,
        self.portal.Base_translateString(
            ComponentMixin._message_invalid_id,
            mapping={'id_prefix': self._document_class.getIdPrefix()}))
    self.tic()

    # non-regression test: when there is no error the error is no longer
    # in workflow history
    component.setId(valid_id)
    component.validate()
    self.tic()
    last_error_message = self.portal.portal_workflow.getInfoFor(
            component, 'history',
            wf_id='component_validation_workflow')[-1]['error_message']
    self.assertEqual(last_error_message, '')

  def testReferenceWithReservedKeywords(self):
    """
    Check whether checkConsistency has been properly implemented for checking
    Component Reference, e.g. no reserved keywords can be used.

    Also, check resets which should be performed when the Component is
    validated but not when an error was encountered (implemented in
    dynamic_class_generation_interaction_workflow)
    """
    valid_reference = self._generateReference('TestReferenceWithReservedKeywords')
    ComponentTool.reset = assertResetCalled
    try:
      component = self._newComponent(valid_reference)
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

    for invalid_reference, error_message in six.iteritems(invalid_reference_dict):
      # Reset should not be performed
      ComponentTool.reset = assertResetNotCalled
      try:
        component.setReference(invalid_reference)
        # 'Class XXX must be defined' error from Document Components checked
        # in its own test method
        component.setTextContent(self._getValidSourceCode(invalid_reference))
        self.tic()

      finally:
        ComponentTool.reset = ComponentTool._original_reset

      # Should be in modified state as an error has been encountered
      self.assertEqual(component.getValidationState(), 'modified')
      self.assertIn(error_message, [m.getMessage().translate()
                                        for m in component.checkConsistency()])
      self.assertEqual(component.getTextContentErrorMessageList(), [])
      self.assertEqual(component.getTextContentWarningMessageList(), [])
      self.assertEqual(component.getReference(), invalid_reference)
      self.assertEqual(component.getReference(validated_only=True), valid_reference)
      self._component_tool.reset(force=True,
                                 reset_portal_type_at_transaction_boundary=True)
      self.assertModuleImportable(valid_reference)

    # Set a valid reference and check that the Component is in validated state
    # and no error was raised
    self.tic()
    ComponentTool.reset = assertResetCalled
    try:
      component.setReference(valid_reference)
      # 'Class XXX must be defined' error from Document Components
      component.setTextContent(self._getValidSourceCode(valid_reference))
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
    reference = self._generateReference('TestVersionWithReservedKeywords')
    valid_version = 'erp5'
    ComponentTool.reset = assertResetCalled
    try:
      component = self._newComponent(reference, version=valid_version)
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

    invalid_id_error_message = self.portal.Base_translateString(
      ComponentMixin._message_invalid_id,
      mapping={'id_prefix': self._document_class.getIdPrefix()})

    for invalid_version, error_message in six.iteritems(invalid_version_dict):
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
                        [invalid_id_error_message,
                         error_message])
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
    reference = self._generateReference('TestComponentWithSyntaxError')
    component = self._newComponent(reference)
    valid_code = component.getTextContent()
    self.tic()
    self.assertEqual(component.checkConsistency(), [])
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(), [])

    component.setTextContent("""import sys
""" + valid_code)
    self.tic()
    self.assertEqual(component.checkConsistency(), [])
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(),
                      ["W:  1,  0: Unused import sys (unused-import)"])

    component.setTextContent("""import unexistent_module
""" + valid_code)
    self.tic()
    if six.PY2:
      self.assertEqual(
        [m.getMessage().translate() for m in component.checkConsistency()],
        ["Error in Source Code: F:  1,  0: Unable to import 'unexistent_module' (import-error)"])
      self.assertEqual(component.getTextContentErrorMessageList(),
                        ["F:  1,  0: Unable to import 'unexistent_module' (import-error)"])
    else:
      self.assertEqual(
        [m.getMessage().translate() for m in component.checkConsistency()],
        ["Error in Source Code: E:  1,  0: Unable to import 'unexistent_module' (import-error)"])
      self.assertEqual(component.getTextContentErrorMessageList(),
                        ["E:  1,  0: Unable to import 'unexistent_module' (import-error)"])
    self.assertEqual(component.getTextContentWarningMessageList(),
                      ["W:  1,  0: Unused import unexistent_module (unused-import)"])

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
    self.assertModuleImportable(reference)

    # Check that checkConsistency returns the proper error message for the
    # following Python errors
    invalid_code_dict = (
      (None,
       # There could be no source code until validated, so checkConsistency()
       # is used instead
       [ComponentMixin._message_text_content_not_set],
       [],
       []),
      ("""def foobar(*args, **kwargs)
  return 42
""" + valid_code,
       ["Error in Source Code: E:  1,  0: invalid syntax (syntax-error)"],
       ["E:  1,  0: invalid syntax (syntax-error)"],
       []),
      # Make sure that foobar NameError is at the end to make sure that after
      # defining foobar function, it is not available at all
      ("""foobar2
""" + valid_code,
       ["Error in Source Code: E:  1,  0: Undefined variable 'foobar2' (undefined-variable)"],
       ["E:  1,  0: Undefined variable 'foobar2' (undefined-variable)"],
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
      self.assertModuleImportable(reference)

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
    self.assertModuleImportable(reference)

  def testImportVersionedComponentOnly(self):
    """
    Most of the time, erp5.component.XXX.COMPONENT_NAME is imported but
    sometimes it may be useful to import a specific version of a Component,
    available as erp5.component.XXX.VERSION_version.COMPONENT_NAME.
    """
    imported_reference = self._generateReference('TestImportedVersionedComponentOnly')
    component = self._newComponent(
      imported_reference,
      self._getValidSourceCode(imported_reference) + """
def foo(*args, **kwargs):
  return "TestImportedVersionedComponentOnly"
""")

    component.validate()
    self.tic()

    top_module_name = self._document_class._getDynamicModuleNamespace()

    # Create a new Component which uses a specific version of the previously
    # created Component
    reference = self._generateReference('TestImportVersionedComponentOnly')
    component_import = self._newComponent(
      reference,
      self._getValidSourceCode(reference) + """
from %s.erp5_version.%s import foo

def bar(*args, **kwargs):
  return 'Bar' + foo(*args, **kwargs)
""" % (top_module_name, imported_reference))

    component_import.validate()
    self.tic()

    # Versioned package and its alias must be available
    self.assertModuleImportable(reference,
                                expected_default_version='erp5_version')

    # Versioned Component of imported Component must be importable and check
    # later that the module has not been added to the top-level package
    self.assertModuleImportable('erp5_version.%s' % imported_reference)

    top_module = __import__(top_module_name, level=0,
                            fromlist=[top_module_name] if six.PY2 else ['erp5'])

    self._importModule('erp5_version.%s' % imported_reference)

    # Function defined in versioned Component must be available and callable
    versioned_module = getattr(top_module.erp5_version, imported_reference)
    self.assertHasAttribute(versioned_module, 'foo')
    self.assertEqual(versioned_module.foo(), 'TestImportedVersionedComponentOnly')

    # The alias module on the top-level package must not have been created as
    # only the versioned Component has been used
    self.failIfHasAttribute(top_module, imported_reference)

    # As well as functions defined on unversioned Component
    self._importModule(reference)
    module = getattr(top_module, reference)
    self.assertHasAttribute(module, 'bar')
    self.assertEqual(module.bar(), 'BarTestImportedVersionedComponentOnly')

    # Now check that the alias module on the top-level package is properly
    # created when importing it
    self._importModule(imported_reference)

  def testVersionPriority(self):
    """
    Check whether Version priorities properly works by adding and removing
    version priorities on ERP5Site and checking whether the proper Component
    is loaded
    """
    reference = self._generateReference('TestVersionPriority')
    source_code = self._getValidSourceCode(reference)
    priority_tuple = self.portal.getVersionPriorityList()
    try:
      self.portal.setVersionPriorityList(('bar | 42.0',) + priority_tuple)
      component_bar_version = self._newComponent(
        reference,
        source_code + """
def function_foo(*args, **kwargs):
  return "TestBarVersionPriority"
  """,
        'bar')
      component_bar_version.validate()
      self.tic()

      component_foo_version = self._newComponent(
        reference,
        source_code + """
def function_foo(*args, **kwargs):
  return "TestFooVersionPriority"
  """,
        'foo')
      component_foo_version.validate()
      self.tic()

      self.assertModuleImportable(reference,
                                  expected_default_version='bar_version')

      # Component for 'foo_version' must not be importable as 'foo' has not been
      # added to ERP5Site version priorities
      self.failIfModuleImportable('foo_version.%s' % reference)

      top_module_name = self._document_class._getDynamicModuleNamespace()
      top_module = __import__(top_module_name, level=0,
                              fromlist=[top_module_name] if six.PY2 else ['erp5'])

      self._importModule(reference)
      module = getattr(top_module, reference)
      self.assertHasAttribute(module, 'function_foo')
      self.assertEqual(module.function_foo(), "TestBarVersionPriority")

      ComponentTool.reset = assertResetCalled

      # Add 'foo' version with a higher priority as 'bar' version and check
      # whether 'foo' version of the Component is used and not bar version
      self.portal.setVersionPriorityList(('foo | 99.0', 'bar | 42.0') +
                                         priority_tuple)
      self.tic()

      self.assertEqual(ComponentTool._reset_performed, True)

      self.assertModuleImportable(
        reference,
        expected_default_version='foo_version',
        expected_additional_version_tuple=('bar_version',))

      self._importModule(reference)
      module = getattr(top_module, reference)
      self.assertHasAttribute(module, 'function_foo')
      self.assertEqual(module.function_foo(), "TestFooVersionPriority")

    finally:
      ComponentTool.reset = ComponentTool._original_reset
      self.portal.setVersionPriorityList(priority_tuple)
      self.tic()

  def testDeveloperRoleSecurity(self):
    """
    Only Developer Role must be able to manage Components

    XXX-arnau: test with different users and workflows
    """
    component = self._newComponent(self._generateReference('TestDeveloperRoleSecurity'))
    self.tic()

    # Anonymous should not even be able to view/access Component Tool
    self.failIfUserCanViewDocument(None, self._component_tool)
    self.failIfUserCanAccessDocument(None, self._component_tool)
    self.failIfUserCanViewDocument(None, component)
    self.failIfUserCanAccessDocument(None, component)

    user_id = 'ERP5TypeTestCase'
    DEVELOPER_ROLE_ID = 'Developer'

    self.assertUserCanChangeLocalRoles(user_id, self._component_tool)
    self.assertUserCanModifyDocument(user_id, self._component_tool)
    self.assertUserCanDeleteDocument(user_id, self._component_tool)
    self.assertUserCanChangeLocalRoles(user_id, component)
    self.assertUserCanDeleteDocument(user_id, component)

    getConfiguration().product_config['erp5'].developer_list = []
    # Add global & local roles, which must be ignored.
    zodb_roles = self.portal.acl_users.zodb_roles
    try:
      zodb_roles.addRole(DEVELOPER_ROLE_ID, '', '')
    except KeyError:
      pass
    zodb_roles.assignRoleToPrincipal(DEVELOPER_ROLE_ID, user_id)
    self._component_tool.manage_addLocalRoles(user_id, [DEVELOPER_ROLE_ID])
    component.manage_addLocalRoles(user_id, [DEVELOPER_ROLE_ID])

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
    zodb_roles.removeRoleFromPrincipal(DEVELOPER_ROLE_ID, user_id)
    # Keep the role available (unassigned) in zodb_roles, it should be
    # harmless.
    def revokeLocalRole(document_value, user_id, role):
      role_list = [
        x
        for x in document_value.get_local_roles_for_userid(user_id)
        if x != role
      ]
      if role_list:
        document_value.manage_setLocalRoles(user_id, role_list)
      else:
        document_value.manage_delLocalRoles(user_id)
    revokeLocalRole(self._component_tool, user_id, DEVELOPER_ROLE_ID)
    revokeLocalRole(component, user_id, DEVELOPER_ROLE_ID)

    self.assertUserCanChangeLocalRoles(user_id, self._component_tool)
    self.assertUserCanModifyDocument(user_id, self._component_tool)
    self.assertUserCanDeleteDocument(user_id, self._component_tool)
    self.assertUserCanChangeLocalRoles(user_id, component)
    self.assertUserCanModifyDocument(user_id, component)
    self.assertUserCanDeleteDocument(user_id, component)

  def _assertAstroidCacheContent(self,
                                 must_be_in_cache_set,
                                 must_not_be_in_cache_set):
    from astroid.builder import MANAGER
    should_not_be_in_cache_list = []
    for modname in MANAGER.astroid_cache:
      if (modname.startswith('checkPythonSourceCode') or
          modname in must_not_be_in_cache_set):
        should_not_be_in_cache_list.append(modname)

      if modname in must_be_in_cache_set:
        must_be_in_cache_set.remove(modname)

    self.assertEqual(should_not_be_in_cache_list, [])
    self.assertEqual(must_be_in_cache_set, set())

  def testPylint(self):
    # One 'imported' Component for each use case:
    #   from erp5.component.module import M1
    #   from erp5.component.module.M1 import hoge
    imported_reference1 = self._generateReference('TestPylintImported1')
    imported_component1 = self._newComponent(imported_reference1)
    imported_component1.setTextContent(imported_component1.getTextContent() + """
def hoge():
  return 'OK'
""")

    imported_reference2 = self._generateReference('TestPylintImported2')
    imported_component2 = self._newComponent(imported_reference2)
    imported_component2.setTextContent(imported_component2.getTextContent() + """
def hoge():
  return 'OK'
""")

    reference = self._generateReference('TestPylint')
    component = self._newComponent(reference)
    self.portal.portal_workflow.doActionFor(component, 'validate_action')
    self.tic()
    self.assertEqual(component.getValidationState(), 'validated')
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(), [])
    self.assertModuleImportable(reference)

    namespace = self._document_class._getDynamicModuleNamespace()

    imported_module1 = self._getComponentFullModuleName(
      imported_reference1)
    imported_module1_with_version = self._getComponentFullModuleName(
      imported_reference1, version='erp5')

    imported_module2 = self._getComponentFullModuleName(
      imported_reference2)
    imported_module2_with_version = self._getComponentFullModuleName(
      imported_reference2, version='erp5')

    component.setTextContent(
      """# -*- coding: utf-8 -*-
# Source code with non-ASCII character should not fail: éàホゲ
from %(namespace)s import %(reference1)s
from %(namespace)s.erp5_version import %(reference1)s

from %(module2)s import hoge
from %(module2_with_version)s import hoge

import %(module2)s
import %(module2_with_version)s

# To avoid 'unused-import' warnings...
%(reference1)s.hoge()
hoge()
%(module2)s.hoge()
%(module2_with_version)s.hoge()

# Attributes added through Products.XXX.patches: Must not raise error nor
# warnings when being used.
from Products.ERP5Type.Core.Workflow import ValidationFailed
class FooBar(ValidationFailed):
  def __init__(self, *args, **kw):
    super(FooBar, self).__init__(*args, **kw)

# Test for various pylint fixes

# Transforms for Zope which should ideally be upstream'ed
from AccessControl.PermissionRole import rolesForPermissionOn, PermissionRole, imPermissionRole, _what_not_even_god_should_do # pylint: disable=unused-import

# Monkey patch of astroid 1.3.8: it raised 'no-name-in-module' because
# Shared.DC was not considered a namespace package
from Shared.DC.ZRDB.Results import Results # pylint: disable=unused-import

import lxml.etree
lxml.etree.Element('test')

from BTrees.OOBTree import OOBTree
OOBTree()

from cryptography.hazmat.primitives.asymmetric import rsa
rsa.generate_private_key(
  public_exponent=65537,
  key_size=2048,
).public_key()

def xmlsec_decrypt():
  # from https://xmlsec.readthedocs.io/en/stable/examples.html#decrypt
  import xmlsec
  manager = xmlsec.KeysManager()
  key = xmlsec.Key.from_file('rsakey.pem', xmlsec.constants.KeyDataFormatPem)
  manager.add_key(key)
  enc_ctx = xmlsec.EncryptionContext(manager)
  root = lxml.etree.parse("enc1-res.xml").getroot()
  enc_data = xmlsec.tree.find_child(root, "EncryptedData", xmlsec.constants.EncNs)
  decrypted = enc_ctx.decrypt(enc_data)
  print(lxml.etree.tostring(decrypted))

import numpy
numpy.sin([])
import pandas
pandas.DataFrame([])

# wendelin is special top-level module for which we added custom pylint support
import wendelin
from wendelin import bigarray
from wendelin.bigarray import array_zodb
from wendelin.bigarray.array_zodb import ZBigArray
_ = wendelin
_ = bigarray
_ = array_zodb
_ = ZBigArray

""" % (dict(namespace=namespace,
            reference1=imported_reference1,
            module2=imported_module2,
            module2_with_version=imported_module2_with_version)) +
      component.getTextContent())

    self._assertAstroidCacheContent(
      must_be_in_cache_set={'%s' % namespace},
      must_not_be_in_cache_set={'%s.erp5_version' % namespace,
                                imported_module1,
                                imported_module1_with_version,
                                imported_module2,
                                imported_module2_with_version})
    component.checkSourceCode()
    self._assertAstroidCacheContent(
      must_be_in_cache_set={'%s' % namespace,
                            '%s.erp5_version' % namespace},
      must_not_be_in_cache_set={imported_module1,
                                imported_module1_with_version,
                                imported_module2,
                                imported_module2_with_version})

    self.tic()
    self.assertEqual(component.getValidationState(), 'modified')
    self.assertEqual(
      component.getTextContentErrorMessageList(),
      ["E:  3,  0: No name '%s' in module '%s' (no-name-in-module)" %
       (imported_reference1, namespace),
       "E:  4,  0: No name '%s' in module '%s.erp5_version' (no-name-in-module)" %
       (imported_reference1, namespace),
       # Spurious message but same as filesystem modules: 2 errors raised
       # (no-name-in-module and import-error)
       "E:  6,  0: No name '%s' in module '%s' (no-name-in-module)" %
       (imported_reference2, namespace),
       "F:  6,  0: Unable to import '%s' (import-error)" %
       imported_module2,
       # Spurious message (see above comment)
       "E:  7,  0: No name '%s' in module '%s.erp5_version' (no-name-in-module)" %
       (imported_reference2, namespace),
       "F:  7,  0: Unable to import '%s' (import-error)" %
       imported_module2_with_version,
       # Spurious message (see above comment)
       "E:  9,  0: No name '%s' in module '%s' (no-name-in-module)" %
       (imported_reference2, namespace),
       "F:  9,  0: Unable to import '%s' (import-error)" %
       imported_module2,
       # Spurious message (see above comment)
       "E: 10,  0: No name '%s' in module '%s.erp5_version' (no-name-in-module)" %
       (imported_reference2, namespace),
       "F: 10,  0: Unable to import '%s' (import-error)" %
       imported_module2_with_version])
    self.assertEqual(component.getTextContentWarningMessageList(), [])

    ## Simulate user:
    # 1) First check and validate 'imported' Components
    self.portal.portal_workflow.doActionFor(imported_component1, 'validate_action')
    self.portal.portal_workflow.doActionFor(imported_component2, 'validate_action')
    self.tic()
    self.assertEqual(imported_component1.getValidationState(), 'validated')
    self.assertEqual(imported_component2.getValidationState(), 'validated')

    message_list = component.checkSourceCode()
    self.assertEqual(message_list, [])
    self._assertAstroidCacheContent(
      must_be_in_cache_set={'%s' % namespace,
                            '%s.erp5_version' % namespace,
                            imported_module1,
                            imported_module1_with_version,
                            imported_module2,
                            imported_module2_with_version},
      must_not_be_in_cache_set=set())

    # 2) Then modify the main one so that it automatically 'validate'
    component.setTextContent(component.getTextContent() + '\n')
    self.tic()
    self._assertAstroidCacheContent(
      must_be_in_cache_set={'%s' % namespace},
      must_not_be_in_cache_set={'%s.erp5_version' % namespace,
                                imported_module1,
                                imported_module1_with_version,
                                imported_module2,
                                imported_module2_with_version})
    self.assertEqual(component.getValidationState(), 'validated')
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(), [])

    component.setTextContent(
      """# -*- coding: utf-8 -*-
from %(module)s import undefined
from %(module_with_version)s import undefined

# To avoid 'unused-import' warning...
undefined()

""" % (dict(module=imported_module2,
            module_with_version=imported_module2_with_version)) +
      component.getTextContent())
    self.tic()
    self.assertEqual(component.getValidationState(), 'modified')
    self.assertEqual(
      component.getTextContentErrorMessageList(),
      ["E:  2,  0: No name 'undefined' in module '%s' (no-name-in-module)" %
       imported_module2_with_version,
       "E:  3,  0: No name 'undefined' in module '%s' (no-name-in-module)" %
       imported_module2_with_version])
    self.assertEqual(component.getTextContentWarningMessageList(), [])

  def testPylintAstroidModuleGeneratedOnce(self):
    imported_reference = self._generateReference('TestPylintAstroidModuleGeneratedOnceImported')
    imported_component = self._newComponent(imported_reference)
    self.portal.portal_workflow.doActionFor(imported_component, 'validate_action')
    imported_component.setTextContent(imported_component.getTextContent() + """
def hoge():
  return 'OK'
""")
    self.tic()
    self.assertEqual(imported_component.getValidationState(), 'validated')
    self.assertEqual(imported_component.getTextContentErrorMessageList(), [])
    self.assertEqual(imported_component.getTextContentWarningMessageList(), [])

    priority_tuple = self.portal.getVersionPriorityList()
    try:
      self.portal.setVersionPriorityList(('bar | 42.0',) + priority_tuple)
      self.tic()

      imported_module_with_bar_version = self._getComponentFullModuleName(
        imported_reference, version='erp5')
      imported_bar_component = self._newComponent(imported_reference, version='bar')
      self.portal.portal_workflow.doActionFor(imported_bar_component, 'validate_action')
      imported_bar_component.setTextContent(imported_component.getTextContent())
      self.tic()
      self.assertEqual(imported_bar_component.getValidationState(), 'validated')
      self.assertEqual(imported_bar_component.getTextContentErrorMessageList(), [])
      self.assertEqual(imported_bar_component.getTextContentWarningMessageList(), [])

      reference = self._generateReference('TestPylintAstroidModuleGeneratedOnce')
      component = self._newComponent(reference)
      component.setTextContent(component.getTextContent() + """
from %(namespace)s import %(reference)s
from %(namespace)s.bar_version import %(reference)s
from %(namespace)s.erp5_version import %(reference)s

# To avoid 'unused-import' warning...
%(reference)s.hoge()
""" % dict(namespace=self._document_class._getDynamicModuleNamespace(),
           reference=imported_reference))

      component.checkSourceCode()
      from astroid.builder import MANAGER
      imported_module = self._getComponentFullModuleName(imported_reference)
      self.assertEqual(
        MANAGER.astroid_cache[self._getComponentFullModuleName(imported_reference, version='bar')],
        MANAGER.astroid_cache[imported_module])
      self.assertNotEqual(
        MANAGER.astroid_cache[self._getComponentFullModuleName(imported_reference, version='erp5')],
        MANAGER.astroid_cache[imported_module])

      self.portal.portal_workflow.doActionFor(component, 'validate_action')
      self.tic()
      self.assertEqual(component.getValidationState(), 'validated')
      self.assertEqual(component.getTextContentErrorMessageList(), [])
      self.assertEqual(component.getTextContentWarningMessageList(), [])

    finally:
      self.portal.setVersionPriorityList(priority_tuple)
      self.tic()

  def testPylintNamedtupleUnicodeLiteralsRegression(self):
    # regression for a bug with our pylint patches on guess encoding
    # a named tuple with unicode_literals enabled cause UnicodeDecodeError
    component = self._newComponent(
        self._generateReference('TestPylintNamedtupleUnicodeLiteralsRegression'))
    component.setTextContent("""
from __future__ import unicode_literals
from collections import namedtuple
namedtuple('NamedTuple', 'foo bar')(1, 2)
""")
    self.tic()
    self.assertEqual(component.getTextContentWarningMessageList(), [])
    self.assertEqual(component.getTextContentErrorMessageList(), [])

  def testModuleSecurityInfo(self):
    """
    AccessControl.SecurityInfo.ModuleSecurityInfo() function allows to declare
    public/private classes and functions at Module level.

    When called, an entry is added to AccessControl.SecurityInfo._moduleSecurity
    dict (mapping module name to _ModuleSecurityInfo class instance). Later on,
    when this module is imported from 'Restricted Code', securities will be
    applied to the Module and then be moved to from _moduleSecurity to
    AccessControl.SecurityInfo._appliedModuleSecurity dict.

    For ZODB Components, we have the versioned Module and its alias. This test
    ensures that securities are also properly defined for the alias to be
    importable (and not raising an 'Unauthorized' exception).
    """
    from AccessControl.SecurityInfo import (_moduleSecurity,
                                            _appliedModuleSecurity)
    from Products.ERP5Type.patches.Restricted import MNAME_MAP

    reference = self._generateReference('TestModuleSecurityInfo')
    component = self._newComponent(reference)
    version_package = (self._document_class._getDynamicModuleNamespace() +
                       '.erp5_version')
    module = self._getComponentFullModuleName(reference)
    module_versioned = self._getComponentFullModuleName(reference,
                                                        version='erp5')
    # __name__ == erp5.component.XXX.erp5_version.TestModuleSecurityInfo
    # (erp5.component.XXX.TestModuleSecurityInfo is just an alias)
    component.setTextContent("""
class TestModuleSecurityInfoException(Exception):
  pass
from AccessControl.SecurityInfo import ModuleSecurityInfo
ModuleSecurityInfo(__name__).declarePublic('TestModuleSecurityInfoException')
""" + component.getTextContent())
    self.portal.portal_workflow.doActionFor(component, 'validate_action')
    self.tic()
    self.assertEqual(component.getValidationState(), 'validated')
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(), [])
    self.assertModuleImportable(reference,
                                expected_default_version='erp5_version',
                                reset=True)
    self.assertNotIn(module_versioned, _moduleSecurity)
    self.assertNotIn(module_versioned, _appliedModuleSecurity)

    # Define another ZODB Component to check that not importing the module
    # beforehand works
    reference2 = self._generateReference('TestModuleSecurityInfo2')
    component2 = self._newComponent(reference2)
    module2 = self._getComponentFullModuleName(reference2)
    module_versioned2 = self._getComponentFullModuleName(reference2,
                                                        version='erp5')
    # __name__ == erp5.component.XXX.erp5_version.TestModuleSecurityInfo2
    # (erp5.component.XXX.TestModuleSecurityInfo2 is just an alias)
    component2.setTextContent("""
class TestModuleSecurityInfoException2(Exception):
  pass
from AccessControl.SecurityInfo import ModuleSecurityInfo
ModuleSecurityInfo(__name__).declarePublic('TestModuleSecurityInfoException2')
""" + component2.getTextContent())
    self.portal.portal_workflow.doActionFor(component2, 'validate_action')
    self.tic()
    self.assertEqual(component2.getValidationState(), 'validated')
    self.assertEqual(component2.getTextContentErrorMessageList(), [])
    self.assertEqual(component2.getTextContentWarningMessageList(), [])
    self.assertModuleImportable(reference2,
                                expected_default_version='erp5_version',
                                reset=True)

    ## Import module from non-'Restricted Code': it must be only in
    ## _moduleSecurity
    self._importModule('erp5_version.%s' % reference)
    self.assertNotIn(module, MNAME_MAP)
    self.assertIn(module_versioned, _moduleSecurity)
    self.assertNotIn(module, _appliedModuleSecurity)
    self.assertNotIn(module2, MNAME_MAP)
    self.assertNotIn(module2, _moduleSecurity)
    self.assertNotIn(module2, _appliedModuleSecurity)

    ## Import module from 'Restricted Code': it must be in
    ## _appliedModuleSecurity and no longer in _moduleSecurity
    createZODBPythonScript(self.portal.portal_skins.custom,
      'TestModuleSecurityInfoPythonScript', '',
      """
from %s import TestModuleSecurityInfoException
from %s import TestModuleSecurityInfoException

from %s import TestModuleSecurityInfoException2
from %s import TestModuleSecurityInfoException2
return 'OK'
""" % (module_versioned, module,
       module_versioned2, module2))
    self.assertEqual(self.portal.TestModuleSecurityInfoPythonScript(), 'OK')
    self.assertEqual(MNAME_MAP.get(module), module_versioned)
    self.assertNotIn(module_versioned, _moduleSecurity)
    self.assertIn(module_versioned, _appliedModuleSecurity)
    self.assertEqual(MNAME_MAP.get(module2), module_versioned2)
    self.assertNotIn(module_versioned2, _moduleSecurity)
    self.assertIn(module_versioned2, _appliedModuleSecurity)

    ## Reset must clear everything including the version package as this is
    ## dynamic (no need to clear erp5.component.XXX though)...
    self._component_tool.reset(force=True,
                               reset_portal_type_at_transaction_boundary=True)
    self.tic()
    self.assertNotIn(version_package, _moduleSecurity)
    self.assertNotIn(version_package, _appliedModuleSecurity)
    self.assertNotIn(module, MNAME_MAP)
    self.assertNotIn(module_versioned, _moduleSecurity)
    self.assertNotIn(module_versioned, _appliedModuleSecurity)
    self.assertNotIn(module2, MNAME_MAP)
    self.assertNotIn(module_versioned2, _moduleSecurity)
    self.assertNotIn(module_versioned2, _appliedModuleSecurity)

from Products.ERP5Type.Core.ExtensionComponent import ExtensionComponent

class TestZodbExtensionComponent(TestZodbModuleComponent):
  """
  Tests specific to ZODB Extension Component (previously defined in bt5 and
  installed on the filesystem in $INSTANCE_HOME/Extensions)
  """
  _portal_type = 'Extension Component'
  _document_class = ExtensionComponent

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
      self.assertEqual(self.publish(path).getBody(), b'42')

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

    self.assertRaisesRegex(NotFound, "The specified module,"
        " '%s', couldn't be found." % module, external_method, 'portal_ids')

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

class _TestZodbDocumentComponentMixin(TestZodbModuleComponent):
  """
  Common to all Component class inheriting from Document Component (so
  Interface, Tool and Mixin)
  """
  def testAtLeastOneClassNamedAfterReference(self):
    component = self._newComponent(
      self._generateReference('TestClassNamedAfterReference'))
    self.tic()
    self.assertEqual(component.checkConsistency(), [])
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(), [])

    component.setTextContent("""from erp5.component.document.Person import Person

class DifferentFromReference(Person):
  pass
""")
    self.assertEqual(
      [m.getMessage().translate() for m in component.checkConsistency()],
      [self.portal.Base_translateString(
        self._document_class._message_reference_class_not_defined,
        mapping={'reference': component.getReference()})])
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(), [])

  def testImportFromAnotherComponent(self):
    """
    Create two new Components and check whether one can import the other one
    after the latter has been validated
    """
    self.failIfModuleImportable('TestWithImport')
    self.failIfModuleImportable('TestImported')

    test_imported_component = self._newComponent('TestImported')
    test_component = self._newComponent(
      'TestWithImport',
      """
from %s.TestImported import TestImported

class TestWithImport(TestImported):
  pass
""" % self._document_class._getDynamicModuleNamespace())
    self.tic()
    self.failIfModuleImportable('TestWithImport')
    self.failIfModuleImportable('TestImported')

    test_imported_component.validate()
    test_component.validate()
    self.tic()

    # TestWithImport must be imported first to check if TestImported could be
    # imported without being present before
    self.assertModuleImportable('TestWithImport')
    self.assertModuleImportable('TestImported')

  def testGC(self):
    """
    Zope Implements and ClassProvides keep a reference to the class itself,
    thus creating a circular reference which can only be garbage collected by
    'gc' module (and not by reference counting).

    So check that ZODB Components modules are properly garbage collectable
    after a reset (in 'gc' terms: considered 'unreachable' but 'collectable'
    and could be freed).
    """
    from zope.interface import Interface
    class ITestGC(Interface):
      """Anything"""
      def foo():
        """Anything"""
    from types import ModuleType
    interface_module = ModuleType('ITestGC')
    interface_module.ITestGC = ITestGC
    sys.modules['ITestGC'] = interface_module

    self.failIfModuleImportable('TestGC')
    test_component = self._newComponent(
      'TestGC',
      """from Products.ERP5Type.XMLObject import XMLObject
from ITestGC import ITestGC
import zope.interface

@zope.interface.implementer(ITestGC)
class TestGC(XMLObject):
  def foo(self):
      pass
""")
    self.tic()
    self.failIfModuleImportable('TestGC')

    test_component.validate()
    self.tic()

    import gc
    initial_gc_debug_flags = gc.get_debug()
    initial_stderr = sys.stderr
    from six.moves import cStringIO as StringIO
    stderr = StringIO()
    try:
      gc.disable()

      gc.collect()
      self.assertModuleImportable('TestGC', reset=False)
      class_id = id(self._module.TestGC.TestGC)
      Implements_id = id(self._module.TestGC.TestGC.__implemented__)
      ClassProvides_id = id(self._module.TestGC.TestGC.__provides__)
      self.assertEqual(gc.collect(), 0)
      self.assertEqual(gc.garbage, [])

      self._component_tool.reset(force=True)
      gc.collect()
      self.assertEqual(gc.garbage, [])

      import erp5.component
      debug_flags = (
        gc.DEBUG_STATS
        | gc.DEBUG_UNCOLLECTABLE
        | gc.DEBUG_COLLECTABLE )
      if six.PY2:
        debug_flags |= (
          gc.DEBUG_OBJECTS
          | gc.DEBUG_INSTANCES)
      gc.set_debug(debug_flags)
      sys.stderr = stderr
      # Still not garbage collectable as RefManager still keeps a reference
      erp5.component.ref_manager.clear()
      # Once deleted, the ZODB Component module must be collectable...
      self.assertNotEqual(gc.collect(), 0)

    finally:
      gc.set_debug(initial_gc_debug_flags)
      gc.enable()

      sys.stderr = initial_stderr

    # And make sure that it has really be collected thanks to DEBUG_COLLECTABLE
    self.assertEqual(gc.garbage, [])
    stderr.seek(0)
    found_line_list = []
    for line in stderr:
      if ('0x%x>' % class_id in line or
          '0x%x>' % Implements_id in line or
          '0x%x>' % ClassProvides_id in line):
        found_line_list.append(line)

    self.assertEqual(
      ['gc: collectable <ClassProvides 0x%x>\n' % ClassProvides_id,
       'gc: collectable <ExtensionClass.ExtensionClass 0x%x>\n' % class_id,
       'gc: collectable <Implements 0x%x>\n' % Implements_id],
      sorted(found_line_list))

class TestZodbDocumentComponent(_TestZodbDocumentComponentMixin):
  """
  Tests specific to ZODB Document Component. This is only for Document
  previously defined in bt5 and installed on the filesystem in
  $INSTANCE_HOME/Document. Later on, Product Documents will also be migrated
  """
  _portal_type = 'Document Component'
  _document_class = DocumentComponent

  def _getValidSourceCode(self, class_name):
    return '''from erp5.component.document.Person import Person

class %sAnything:
  pass

class %s(Person):
  pass
''' % (class_name, class_name)

  def testAssignToPortalTypeClass(self):
    """
    Create a new Document Component inheriting from Person Document and try to
    assign it to Person Portal Type, then create a new Person and check
    whether it has been successfully added to its Portal Type class bases and
    that the newly-defined function on ZODB Component can be called as well as
    methods from Person Document
    """
    ## Create an Interface assigned to the test ZODB Component to check that
    ## only resetting Portal Type classes do not have any side-effect on
    ## Interfaces defined on ZODB Components
    from zope.interface import Interface
    class ITestPortalType(Interface):
      """Anything"""
      def foo():
        """Anything"""
    from types import ModuleType
    interface_module = ModuleType('ITestPortalType')
    interface_module.ITestPortalType = ITestPortalType
    sys.modules['ITestPortalType'] = interface_module

    self.failIfModuleImportable('TestPortalType')

    # Create a new Document Component inheriting from Person Document which
    # defines only one additional method (meaningful to make sure that the
    # class (and not the module) has been added to the class when the
    # TypeClass is changed)
    test_component = self._newComponent(
      'TestPortalType',
      """
from erp5.component.document.Person import Person

from ITestPortalType import ITestPortalType
import zope.interface

zope.interface.implementer(ITestPortalType)
class TestPortalType(Person):
  def test42(self):
    return 42

  def foo(self):
    pass
""")
    test_component.validate()
    self.tic()

    # As TestPortalType Document Component has been validated, it should now
    # be available
    self.assertModuleImportable('TestPortalType', reset=False)
    self.assertTrue(ITestPortalType.implementedBy(self._module.TestPortalType.TestPortalType))

    self._component_tool.reset(force=True,
                               reset_portal_type_at_transaction_boundary=True)

    person_type = self.portal.portal_types.Person
    person_type_class = person_type.getTypeClass()
    self.assertEqual(person_type_class, 'Person')

    # Create a new Person
    person_module = self.portal.person_module
    person = person_module.newContent(id='Foo Bar', portal_type='Person')
    from erp5.component.document.Person import Person as PersonDocument
    self.assertIn(PersonDocument, person.__class__.mro())

    # There is no reason that TestPortalType Document Component has been
    # assigned to a Person
    self.failIfHasAttribute(person, 'test42')
    self.failIfHasAttribute(self._module, 'TestPortalType')
    self.assertFalse(ITestPortalType.providedBy(person))
    self.assertFalse(ITestPortalType.implementedBy(person.__class__))
    for klass in person.__class__.mro():
      self.assertNotEqual(klass.__name__, 'TestPortalType')

    def _check():
      self.assertHasAttribute(person, 'test42')
      self.assertEqual(person.test42(), 42)

      # The Portal Type class should not be in ghost state by now as we tried
      # to access test42() defined in TestPortalType Document Component
      self.assertHasAttribute(self._module, 'TestPortalType')
      self.assertIn(self._module.TestPortalType.TestPortalType, person.__class__.mro())
      from erp5.component.document.Person import Person as PersonDocument
      self.assertIn(PersonDocument, person.__class__.mro())
      self.assertTrue(ITestPortalType.providedBy(person))
      self.assertTrue(ITestPortalType.implementedBy(person.__class__))

    # Reset Portal Type classes to ghost to make sure that everything is reset
    self._component_tool.reset(force=True,
                               reset_portal_type_at_transaction_boundary=False)
    # TestPortalType must be available in type class list
    self.assertIn('TestPortalType', person_type.getDocumentTypeList())
    try:
      person_type.setTypeClass('TestPortalType')
      self.commit()
      _check()

      self.portal.portal_types.resetDynamicDocuments()
      _check()

    finally:
      person_type.setTypeClass('Person')
      self.commit()

  def testProductsERP5DocumentCompatibility(self):
    """Check that document class also exist in its original namespace (source_reference)

    Document Component that were moved from file system Products/*/Document needs
    to be still importable from their initial location, as there might be classes
    in the database of these instances.

    There is no such test for Mixin/Interface/Tool because the code is the
    same for all of them (component_package.py).
    """
    self.failIfModuleImportable('TestProductsERP5DocumentCompatibility')

    test_component = self._newComponent(
        'TestProductsERP5DocumentCompatibility',
        """\
from Products.ERP5Type.Base import Base
class TestProductsERP5DocumentCompatibility(Base):
  portal_type = 'Test ProductsERP5Document Compatibility'
  test_attribute = 'TestProductsERP5DocumentCompatibility'
"""
    )
    test_component.setSourceReference('Products.ERP5.Document.TestProductsERP5DocumentCompatibility')
    test_component.validate()
    self.tic()

    self.assertModuleImportable('TestProductsERP5DocumentCompatibility')

    from Products.ERP5.Document.TestProductsERP5DocumentCompatibility import TestProductsERP5DocumentCompatibility  # pylint:disable=import-error,no-name-in-module
    self.assertEqual(TestProductsERP5DocumentCompatibility.test_attribute, 'TestProductsERP5DocumentCompatibility')

    # this also exist in Products.ERP5Type.Document
    from Products.ERP5Type.Document.TestProductsERP5DocumentCompatibility import TestProductsERP5DocumentCompatibility as TestProductsERP5DocumentCompatibility_from_ProductsERP5Type  # pylint:disable=import-error,no-name-in-module
    self.assertIs(TestProductsERP5DocumentCompatibility_from_ProductsERP5Type, TestProductsERP5DocumentCompatibility)

    # another component can also import the migrated component from its original name
    test_component_importing = self._newComponent(
        'TestComponentImporting',
        """\
from Products.ERP5.Document.TestProductsERP5DocumentCompatibility import TestProductsERP5DocumentCompatibility
class TestComponentImporting(TestProductsERP5DocumentCompatibility):
  pass
"""
    )
    test_component_importing.validate()
    self.tic()

    self.assertModuleImportable('TestComponentImporting')
    from erp5.component.document.TestComponentImporting import TestComponentImporting  # pylint:disable=import-error,no-name-in-module

    from Products.ERP5.Document.TestProductsERP5DocumentCompatibility import TestProductsERP5DocumentCompatibility  # pylint:disable=import-error,no-name-in-module
    self.assertTrue(issubclass(TestComponentImporting, TestProductsERP5DocumentCompatibility))

    test_component.invalidate()
    self.tic()

    # after invalidating the component, the legacy modules are no longer importable
    with self.assertRaises(ImportError):
      from Products.ERP5.Document.TestProductsERP5DocumentCompatibility import TestProductsERP5DocumentCompatibility  # pylint:disable=import-error,no-name-in-module
    with self.assertRaises(ImportError):
      from Products.ERP5Type.Document.TestProductsERP5DocumentCompatibility import TestProductsERP5DocumentCompatibility  # pylint:disable=import-error,no-name-in-module

  def testProductsERP5TypeDocumentCompatibility(self):
    """Check that document class also exist in Products.ERP5Type.Document namespace
    for compatibility.

    We also check that this module is properly reloaded when a document component
    is modified.
    """
    self.failIfModuleImportable('TestProductsERP5TypeDocumentCompatibility')

    test_component = self._newComponent(
        'TestProductsERP5TypeDocumentCompatibility',
        """\
from Products.ERP5Type.Base import Base
class TestProductsERP5TypeDocumentCompatibility(Base):
  portal_type = 'Test ProductsERP5TypeDocument Compatibility'
  generation = 1
"""
    )
    test_component.validate()
    self.tic()

    self.assertModuleImportable('TestProductsERP5TypeDocumentCompatibility')

    from Products.ERP5Type.Document.TestProductsERP5TypeDocumentCompatibility import TestProductsERP5TypeDocumentCompatibility  # pylint:disable=import-error,no-name-in-module
    self.assertEqual(TestProductsERP5TypeDocumentCompatibility.generation, 1)

    test_component.setTextContent(
        """\
from Products.ERP5Type.Base import Base
class TestProductsERP5TypeDocumentCompatibility(Base):
  portal_type = 'Test ProductsERP5TypeDocument Compatibility'
  generation = 2
""")
    self.tic()
    self.assertModuleImportable('TestProductsERP5TypeDocumentCompatibility')
    from Products.ERP5Type.Document.TestProductsERP5TypeDocumentCompatibility import TestProductsERP5TypeDocumentCompatibility  # pylint:disable=import-error,no-name-in-module
    self.assertEqual(TestProductsERP5TypeDocumentCompatibility.generation, 2)

from Products.ERP5Type.Core.ToolComponent import ToolComponent

class TestZodbToolComponent(_TestZodbDocumentComponentMixin):
  """
  Tests specific to ZODB Tool Component
  """
  _portal_type = 'Tool Component'
  _document_class = ToolComponent

  def _getValidSourceCode(self, class_name):
    return '''from Products.ERP5Type.Tool.BaseTool import BaseTool
class %(class_name)s(BaseTool):
  id = 'portal_%(class_name)s'
  portal_type = 'Delivery Tool'
  meta_type = 'ERP5 %(meta_type)s'

from Products.ERP5Type.Globals import InitializeClass
InitializeClass(%(class_name)s)
''' % dict(class_name=class_name,
           meta_type=''.join([(c if c.islower() else ' ' + c)
                              for c in class_name]).strip())

  def testHookAfterLoad(self):
    component = self._newComponent('TestHookAfterLoadTool')
    self.tic()
    response = self.publish(
      '%s/manage_addProduct/ERP5/manage_addToolForm' % self.portal.getPath(),
      'ERP5TypeTestCase:')
    self.assertEqual(response.getStatus(), 200)
    self.assertNotIn(b'ERP5 Test Hook After Load Tool', response.getBody())

    component.validate()
    self.tic()
    self.assertEqual(component.getValidationState(), 'validated')
    self.assertEqual(component.checkConsistency(), [])
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(), [])
    response = self.publish(
      '%s/manage_addProduct/ERP5/manage_addToolForm' % self.portal.getPath(),
      'ERP5TypeTestCase:')
    self.assertEqual(response.getStatus(), 200)
    self.assertIn(b'ERP5 Test Hook After Load Tool', response.getBody())

from Products.ERP5Type.Core.TestComponent import TestComponent

class TestZodbTestComponent(TestZodbModuleComponent):
  """
  Tests specific to ZODB Test Component (known as Live Tests, and previously
  defined in bt5 and installed in $INSTANCE_HOME/test)
  """
  _portal_type = 'Test Component'
  _document_class = TestComponent

  def _getValidSourceCode(self, *_):
    return '''from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import os

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

    request = self.portal.REQUEST
    self.assertIsNone(request.get('foo'))

    request.set('foo', 'bar')
    self.assertEqual(request.get('foo'), 'bar')

    from zope.globalrequest import getRequest
    self.assertEqual(getRequest().get('foo'), 'bar')

    self.publish(self.portal.getId())
    self.assertEqual(self.portal.REQUEST.get('foo'), 'bar')
    self.assertEqual(getRequest().get('foo'), 'bar')

  def afterClear(self):
    super(Test, self).afterClear()

    # Checked that this module has not been GC'ed until the very end...
    self.assertNotEqual(os, None)
'''

  def testRunLiveTest(self):
    """
    Create a new ZODB Test Component and try to run it as a live tests and
    check the expected output
    """
    # First try with a test which run successfully
    source_code = self._getValidSourceCode()
    component = self._newComponent('testRunLiveTest', source_code)
    component.validate()
    self.tic()

    from Products.ERP5Type.tests.runUnitTest import ERP5TypeTestLoader
    ERP5TypeTestLoader_loadTestsFromNames = ERP5TypeTestLoader.loadTestsFromNames
    def loadTestsFromNames(self, *args, **kwargs):
      """
      Monkey patched to simulate a reset right after importing the ZODB Test
      Component whose Unit Tests are going to be executed
      """
      ret = ERP5TypeTestLoader_loadTestsFromNames(self, *args, **kwargs)

      from Products.ERP5.ERP5Site import getSite
      getSite().portal_components.reset(force=True)

      # Simulate a new REQUEST while the old one has been GC'ed
      import erp5.component
      erp5.component.ref_manager.clear()

      import gc
      gc.collect()

      return ret

    self.assertEqual(component.getValidationState(), 'validated')
    self.assertModuleImportable('testRunLiveTest')
    self._component_tool.reset(force=True,
                               reset_portal_type_at_transaction_boundary=True)

    # set a request key, that should not be set from the test request
    self.portal.REQUEST.set('foo', 'something from main request')

    def runLiveTest(test_name):
      # ERP5TypeLiveTestCase.runLiveTest patches ERP5TypeTestCase bases, thus it
      # needs to be restored after calling runLiveTest
      base_tuple = ERP5TypeTestCase.__bases__
      ERP5TypeTestLoader.loadTestsFromNames = loadTestsFromNames
      try:
        self._component_tool.runLiveTest(test_name)
      finally:
        ERP5TypeTestCase.__bases__ = base_tuple
        ERP5TypeTestLoader.loadTestsFromNames = ERP5TypeTestLoader_loadTestsFromNames
      return self._component_tool.readTestOutput()

    output = runLiveTest('testRunLiveTest')
    expected_msg_re = re.compile('Ran 1 test.*OK', re.DOTALL)
    self.assertRegex(output, expected_msg_re)

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

    output = runLiveTest('testRunLiveTest')
    expected_msg_re = re.compile('Ran 2 tests.*FAILED \(failures=1\)', re.DOTALL)
    self.assertRegex(output, expected_msg_re)

    # Now try addCleanup
    source_code = self._getValidSourceCode() +  '''
  def test_02_addCleanup(self):
    self.portal.portal_activities.setTitle("changed")
    self.tic()
    def cleanup():
      self.portal.portal_activities.setTitle({activity_tool_title!r})
      self.tic()
    self.addCleanup(cleanup)

  def test_03_checkAfterCleanUp(self):
    self.assertEqual(self.portal.portal_activities.getTitle(), {activity_tool_title!r})
'''.format(activity_tool_title=self.portal.portal_activities.getTitle())

    component.setTextContent(source_code)
    self.tic()
    self.assertEqual(component.getValidationState(), 'validated')
    self.assertModuleImportable('testRunLiveTest')
    self._component_tool.reset(force=True,
                               reset_portal_type_at_transaction_boundary=True)

    output = runLiveTest('testRunLiveTest')
    expected_msg_re = re.compile('Ran 3 test.*OK', re.DOTALL)
    self.assertRegex(output, expected_msg_re)

  def testRunLiveTestImportError(self):
    source_code = '''
def break_at_import():
  import non.existing.module # pylint:disable=import-error
break_at_import()
'''
    component = self._newComponent('testRunLiveTestImportError', source_code)
    component.validate()
    self.tic()

    from Products.ERP5Type.tests.runUnitTest import ERP5TypeTestLoader
    ERP5TypeTestLoader_loadTestsFromNames = ERP5TypeTestLoader.loadTestsFromNames
    def loadTestsFromNames(self, *args, **kwargs):
      """
      Monkey patched to simulate a reset right after importing the ZODB Test
      Component whose Unit Tests are going to be executed
      """
      ret = ERP5TypeTestLoader_loadTestsFromNames(self, *args, **kwargs)

      from Products.ERP5.ERP5Site import getSite
      getSite().portal_components.reset(force=True)

      # Simulate a new REQUEST while the old one has been GC'ed
      import erp5.component
      erp5.component.ref_manager.clear()

      import gc
      gc.collect()

      return ret

    self.assertEqual(component.getValidationState(), 'validated')
    self._component_tool.reset(force=True,
                               reset_portal_type_at_transaction_boundary=True)

    def runLiveTest(test_name):
      # ERP5TypeLiveTestCase.runLiveTest patches ERP5TypeTestCase bases, thus it
      # needs to be restored after calling runLiveTest
      base_tuple = ERP5TypeTestCase.__bases__
      ERP5TypeTestLoader.loadTestsFromNames = loadTestsFromNames
      try:
        self._component_tool.runLiveTest(test_name)
      finally:
        ERP5TypeTestCase.__bases__ = base_tuple
        ERP5TypeTestLoader.loadTestsFromNames = ERP5TypeTestLoader_loadTestsFromNames
      return self._component_tool.readTestOutput()

    output = runLiveTest('testRunLiveTestImportError')
    self.assertIn('''
  File "<portal_components/test.erp5.testRunLiveTestImportError>", line 4, in <module>
    break_at_import()
  File "<portal_components/test.erp5.testRunLiveTestImportError>", line 3, in break_at_import
    import non.existing.module # pylint:disable=import-error
ImportError: No module named non.existing.module
''', output)

    output = runLiveTest('testDoesNotExist_import_error_because_module_does_not_exist')
    self.assertIn(
      "ImportError: No module named testDoesNotExist_import_error_because_module_does_not_exist",
      output)

  def testERP5Broken(self):
    # Create a broken ghost object
    import erp5.portal_type
    name = self._testMethodName
    types_tool = self.portal.portal_types
    ptype = types_tool.newContent(name, type_class="File", portal_type='Base Type')
    file = ptype.constructInstance(self.portal, name, data=b"foo")
    file_uid = file.getUid()
    self.assertEqual(file.size, len(b"foo"))
    self.commit()
    try:
      self.portal._p_jar.cacheMinimize()
      del file
      delattr(erp5.portal_type, name)

      # Simulate a portal type using a non existing class.
      # Instances of this portal type are broken and can not be modified.
      ptype.setTypeClass(name)
      self.commit()
      file = self.portal.__dict__[name]
      self.assertIsInstance(file, InitGhostBase)
      # Check that the class is unghosted before resolving __setattr__
      self.assertRaises(BrokenModified, setattr, file, "size", 0)
      self.assertIsInstance(file, ERP5BaseBroken)
      self.assertEqual(file.size, len(b"foo"))

      # Now if we repair the portal type definition, instances will
      # no longer be broken and be modifiable again.
      ptype.setTypeClass("File")
      self.commit()

      file = self.portal[name]
      self.assertNotIsInstance(file, ERP5BaseBroken)
      self.assertEqual(file.getUid(), file_uid)
      self.assertEqual(file.getData(), b"foo")
      file.setData(b"something else")
      self.assertEqual(file.getData(), b"something else")
      self.assertNotIn("__Broken_state__", file.__dict__)
    finally:
      self.portal._delObject(name)
      types_tool._delObject(name)
      self.commit()

from Products.ERP5Type.Core.InterfaceComponent import InterfaceComponent
class TestZodbInterfaceComponent(_TestZodbDocumentComponentMixin):
  """
  Tests specific to ZODB Interface Component.
  """
  _portal_type = 'Interface Component'
  _document_class = InterfaceComponent

  def _generateReference(self, base_name):
    return 'I' + base_name

  def _getValidSourceCode(self, class_name):
    return '''from zope.interface import Interface

class %s(Interface):
  def test42():
    """
    Return 42
    """
''' % class_name

  def testNamingConsistency(self):
    valid_reference = self._generateReference('TestNaming')
    component = self._newComponent(valid_reference)
    component.validate()
    self.tic()

    self.assertEqual(component.getValidationState(), 'validated')
    self.assertEqual(component.checkConsistency(), [])
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(), [])
    self.assertEqual(component.getReference(), valid_reference)
    self.assertEqual(component.getReference(validated_only=True), valid_reference)
    self.assertModuleImportable(valid_reference)

    invalid_reference = 'TestNaming'
    ComponentTool.reset = assertResetNotCalled
    try:
      component.setReference(invalid_reference)
      # Checked in another test methods
      component.setId("%s.%s.%s" % (self._document_class.getIdPrefix(),
                                    component.getVersion(),
                                    invalid_reference))
      component.setTextContent(self._getValidSourceCode(invalid_reference))
      self.tic()
    finally:
      ComponentTool.reset = ComponentTool._original_reset

    self.assertEqual(component.getValidationState(), 'modified')
    self.assertEqual([m.getMessage().translate()
                      for m in component.checkConsistency()],
                     [self._document_class._message_reference_wrong_naming])
    self.assertEqual(component.getTextContentErrorMessageList(), [])
    self.assertEqual(component.getTextContentWarningMessageList(), [])
    self.assertEqual(component.getReference(), invalid_reference)
    self.assertEqual(component.getReference(validated_only=True), valid_reference)

  def testAssignToPortalTypeClass(self):
    """
    Create a new Document Component inheriting from Person Document and try to
    assign it to Person Portal Type, then create a new Person and check
    whether it has been successfully added to its Portal Type class bases and
    that the newly-defined function on ZODB Component can be called as well as
    methods from Person Document
    """
    import erp5.portal_type
    import erp5.accessor_holder
    person_type = self.portal.portal_types.Person
    person_type_class = erp5.portal_type.Person

    component = self._newComponent('ITestPortalType')
    self.tic()
    self.failIfModuleImportable('ITestPortalType')
    self.assertNotIn('ITestPortalType', person_type.getInterfaceTypeList())
    self.failIfHasAttribute(erp5.accessor_holder.BaseAccessorHolder,
                            'providesITestPortalType')

    component.validate()
    self.assertModuleImportable('ITestPortalType')
    self.assertIn('ITestPortalType', person_type.getInterfaceTypeList())

    from erp5.component.interface.ITestPortalType import ITestPortalType

    person_type_class.loadClass()
    implemented_by_list = list(implementedBy(person_type_class))
    self.assertNotIn(ITestPortalType, implemented_by_list)
    self.assertHasAttribute(erp5.accessor_holder.BaseAccessorHolder,
                            'providesITestPortalType')
    self.assertHasAttribute(person_type_class, 'providesITestPortalType')
    new_person = self.portal.person_module.newContent(portal_type='Person')
    self.assertNotIn('providesITestPortalType', person_type_class.__dict__)
    self.assertFalse(new_person.providesITestPortalType())
    self.assertIn('providesITestPortalType', person_type_class.__dict__)
    # Called again to check the alias created on erp5.portal_type.Person on
    # the first call of providesITestPortalType() (optimization)
    self.assertFalse(new_person.providesITestPortalType())
    person_original_interface_type_list = list(person_type.getTypeInterfaceList())
    try:
      person_type.setTypeInterfaceList(person_original_interface_type_list +
                                       ['ITestPortalType'])
      self.commit()
      self.assertEqual(person_type_class.__isghost__, True)

      person_type_class.loadClass()
      implemented_by_list = list(implementedBy(person_type_class))
      self.assertIn(ITestPortalType, implemented_by_list)

      self.assertNotIn('providesITestPortalType', person_type_class.__dict__)
      self.assertTrue(new_person.providesITestPortalType())
      self.assertIn('providesITestPortalType', person_type_class.__dict__)
      self.assertTrue(new_person.providesITestPortalType())

    finally:
      person_type.setTypeInterfaceList(person_original_interface_type_list)
      self.commit()
      self.assertFalse(new_person.providesITestPortalType())

from Products.ERP5Type.Core.MixinComponent import MixinComponent
class TestZodbMixinComponent(TestZodbInterfaceComponent):
  """
  Tests specific to ZODB Mixin Component.
  """
  _portal_type = 'Mixin Component'
  _document_class = MixinComponent

  def _generateReference(self, base_name):
    return base_name + 'Mixin'

  def _getValidSourceCode(self, class_name):
    return '''class %s:
  def test42(self):
    """
    Return 42
    """
''' % class_name

  def testAssignToPortalTypeClass(self):
    """
    Create a new Document Component inheriting from Person Document and try to
    assign it to Person Portal Type, then create a new Person and check
    whether it has been successfully added to its Portal Type class bases and
    that the newly-defined function on ZODB Component can be called as well as
    methods from Person Document
    """
    import erp5.portal_type
    person_type = self.portal.portal_types.Person
    person_type_class = erp5.portal_type.Person

    component = self._newComponent('TestPortalTypeMixin')
    self.tic()
    self.failIfModuleImportable('TestPortalTypeMixin')
    self.assertNotIn('TestPortalTypeMixin', person_type.getMixinTypeList())

    component.validate()
    self.assertModuleImportable('TestPortalTypeMixin')
    self.assertIn('TestPortalTypeMixin', person_type.getMixinTypeList())

    from erp5.component.mixin.TestPortalTypeMixin import TestPortalTypeMixin

    person_type_class.loadClass()
    person_type_class_mro_list = person_type_class.__mro__
    self.assertNotIn(TestPortalTypeMixin, person_type_class_mro_list)
    person_original_mixin_type_list = list(person_type.getTypeMixinList())
    try:
      person_type.setTypeMixinList(person_original_mixin_type_list +
                                   ['TestPortalTypeMixin'])
      self.commit()
      self.assertEqual(person_type_class.__isghost__, True)

      person_type_class.loadClass()
      person_type_class_mro_list = person_type_class.__mro__
      from erp5.component.mixin.TestPortalTypeMixin import TestPortalTypeMixin
      self.assertIn(TestPortalTypeMixin, person_type_class_mro_list)

    finally:
      person_type.setTypeMixinList(person_original_mixin_type_list)
      self.commit()


class TestZodbDocumentComponentReload(ERP5TypeTestCase):
  def getBusinessTemplateList(self):
    return (
      'erp5_core',
      'erp5_base',
      'erp5_pdm',
      'erp5_simulation',
      'erp5_trade',
    )

  def _setBusinessProcessComponentTextContent(self, value):
    component = self.portal.portal_components['document.erp5.BusinessProcess']
    component.setTextContent(value)
    self.tic()

  def testAsComposedDocumentCacheIsCorrectlyFlushed(self):
    component = self.portal.portal_components['document.erp5.BusinessProcess']
    component_original_text_content = component.getTextContent()
    self.addCleanup(
      self._setBusinessProcessComponentTextContent,
      component_original_text_content)

    self._setBusinessProcessComponentTextContent(
      component_original_text_content + """
  def getVersion(self):
    return 1
        """
    )

    movement = self.portal.newContent(portal_type='Movement')
    composed_movement = movement.asComposedDocument()
    self.assertEqual(composed_movement.getVersion(), 1)

    self._setBusinessProcessComponentTextContent(
      component_original_text_content + """
  def getVersion(self):
    return 2
        """
    )

    composed_movement = movement.asComposedDocument()
    self.assertEqual(composed_movement.getVersion(), 2)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPortalTypeClass))
  suite.addTest(unittest.makeSuite(TestZodbPropertySheet))
  suite.addTest(unittest.makeSuite(TestZodbModuleComponent))
  suite.addTest(unittest.makeSuite(TestZodbExtensionComponent))
  suite.addTest(unittest.makeSuite(TestZodbDocumentComponent))
  suite.addTest(unittest.makeSuite(TestZodbToolComponent))
  suite.addTest(unittest.makeSuite(TestZodbTestComponent))
  suite.addTest(unittest.makeSuite(TestZodbInterfaceComponent))
  suite.addTest(unittest.makeSuite(TestZodbMixinComponent))
  suite.addTest(unittest.makeSuite(TestZodbDocumentComponentReload))
  return suite
