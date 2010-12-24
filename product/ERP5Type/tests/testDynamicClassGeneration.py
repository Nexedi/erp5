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

import unittest
import transaction

from Products.ERP5Type.dynamic.portal_type_class import synchronizeDynamicModules
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.backportUnittest import expectedFailure

from zope.interface import Interface, implementedBy

class TestPortalTypeClass(ERP5TypeTestCase):
  def getBusinessTemplateList(self):
    return 'erp5_base',

  def testImportNonMigratedPerson(self):
    """
    Import a .xml containing a Person created with an old
    Products.ERP5Type.Document.Person.Person type
    """
    person_module = self.portal.person_module
    self.importObjectFromFile(person_module, 'non_migrated_person.xml')
    transaction.commit()

    non_migrated_person = person_module.non_migrated_person
    # check that object unpickling instanciated a new style object
    person_class = self.portal.portal_types.getPortalTypeClass('Person')
    self.assertEquals(non_migrated_person.__class__, person_class)

  @expectedFailure
  def testImportNonMigratedDocumentUsingContentClass(self):
    """
    Import a .xml containing a Base Type with old Document path
    Products.ERP5Type.ERP5Type.ERP5TypeInformation

    This Document class is different because it's a content_class,
    i.e. it was not in Products.ERP5Type.Document.** but was
    imported directly as such.
    """
    self.importObjectFromFile(self.portal, 'Category.xml')
    transaction.commit()

    non_migrated_type = self.portal.Category
    # check that object unpickling instanciated a new style object
    base_type_class = self.portal.portal_types.getPortalTypeClass('Base Type')
    self.assertEquals(non_migrated_type.__class__, base_type_class)

  def testMigrateOldObjectFromZODB(self):
    """
    Load an object with ERP5Type.Document.Person.Person from the ZODB
    and check that migration works well
    """
    from Products.ERP5Type.Document.Person import Person

    # remove temporarily the migration
    from Products.ERP5Type.Utils import PersistentMigrationMixin
    PersistentMigrationMixin.migrate = 0

    person_module = self.getPortal().person_module
    obj_id = "this_object_is_old"
    old_object = Person(obj_id)
    person_module._setObject(obj_id, old_object)
    old_object = person_module._getOb(obj_id)

    transaction.commit()
    self.assertEquals(old_object.__class__.__module__, 'Products.ERP5Type.Document.Person')
    self.assertEquals(old_object.__class__.__name__, 'Person')

    self.assertTrue(hasattr(old_object.__class__, '__setstate__'))

    # unload/deactivate the object
    old_object._p_invalidate()

    # From now on, everything happens as if the object was a old, non-migrated
    # object with an old Products.ERP5Type.Document.Person.Person

    # now turn on migration
    PersistentMigrationMixin.migrate = 1

    # reload the object
    old_object._p_activate()

    self.assertEquals(old_object.__class__.__module__, 'erp5.portal_type')
    self.assertEquals(old_object.__class__.__name__, 'Person')

  def testChangeMixin(self):
    """
    Take an existing object, change the mixin definitions of its portal type.
    Check that the new methods are there.
    """
    portal = self.getPortal()
    person_module = portal.person_module
    person = person_module.newContent(id='John Dough', portal_type='Person')

    person_type = portal.portal_types.Person
    self.assertEquals(person_type.getTypeMixinList() or [], [])

    try:
      self.assertEquals(getattr(person, 'asText', None), None)
      # just use a mixin/method that Person does not have yet
      person_type.setTypeMixin('TextConvertableMixin')

      transaction.commit()

      self.assertNotEquals(getattr(person, 'asText', None), None)
    finally:
      # reset the type
      person_type.setTypeMixin(None)
      transaction.commit()

  def testChangeDocument(self):
    """
    Take an existing object, change its document class
    Check that the new methods are there.
    """
    portal = self.getPortal()
    person_module = portal.person_module
    person = person_module.newContent(id='Eva Dough', portal_type='Person')

    person_type = portal.portal_types.Person
    self.assertEquals(person_type.getTypeClass(), 'Person')

    try:
      self.assertEquals(getattr(person, 'getCorporateName', None), None)
      # change the base type class
      person_type.setTypeClass('Organisation')

      transaction.commit()

      self.assertNotEquals(getattr(person, 'getCorporateName', None), None)
    finally:
      # reset the type
      person_type.setTypeClass('Person')
      transaction.commit()

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

  def testPropertyGenerationOnTempPortalType(self):
    portal = self.portal
    temp = portal.organisation_module.newContent('temp_portal_type',
                                                 'Organisation',
                                                 temp_object=True)
    temp.setCorporateName('foobar')
    synchronizeDynamicModules(portal, force=True)

    # check what is happening if aq_dynamic is called on the
    # temp portal type first
    accessor = temp._aq_dynamic('getCorporateName')
    self.failIfEqual(accessor, None)
    self.assertEquals(accessor(), 'foobar')
    self.assertEquals(temp.__class__.__module__, 'erp5.temp_portal_type')

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
    transaction.commit()

    from erp5.portal_type import InterfaceTestType

    # it's necessary to load the class
    # to have a correct list of interfaces
    implemented_by = list(implementedBy(InterfaceTestType))
    self.failIf(IForTest in implemented_by)
    InterfaceTestType.loadClass()

    implemented_by = list(implementedBy(InterfaceTestType))
    self.assertTrue(IForTest in implemented_by,
                    'IForTest not in %s' % implemented_by)

    InterfaceTestType.restoreGhostState()
    implemented_by = list(implementedBy(InterfaceTestType))
    self.failIf(IForTest in implemented_by)

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
    transaction.commit()
    module_class = types_tool.getPortalTypeClass(name)
    module_class.loadClass()

    # first manually reset and check that everything works
    from Products.ERP5Type.Core.Folder import Folder
    self.assertTrue(issubclass(module_class, Folder))
    synchronizeDynamicModules(self.portal, force=True)
    self.assertTrue(issubclass(module_class, Folder))

    # then change the type value to something not descending from Folder
    # and check behavior
    ptype.setTypeClass('Address')

    # while the class has not been reset is should still descend from Folder
    self.assertTrue(issubclass(module_class, Folder))
    # finish transaction and trigger workflow/DynamicModule reset
    transaction.commit()
    # while the class has not been unghosted it's still a Folder
    self.assertTrue(issubclass(module_class, Folder))
    # but it changes as soon as the class is loaded
    module_class.loadClass()
    self.assertFalse(issubclass(module_class, Folder))

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
    new_base_category = self.getPortal().portal_categories.newContent(
      id=base_category_id, portal_type='Base Category')

    # Create a dummy sub-category
    new_base_category.newContent(reference='sub_category1',
                                 portal_type='Category')

    new_base_category.newContent(reference='sub_category2',
                                 portal_type='Category')

    if operation_type == 'change':
      self.getPortal().portal_categories.newContent(
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
      constraint_portal_type='python: ("Content Existence Constraint")')

  def _newCategoryMembershipArityConstraint(self, reference, portal_type):
    """
    Create a new Category Membership Arity Constraint within test
    Property Sheet, allowing testing of Category Acquired Membership
    Arity Constraint too
    """
    self.getPortal().portal_categories.newContent(
      id=reference, portal_type='Base Category')

    self.test_property_sheet.newContent(
      reference=reference,
      portal_type=portal_type,
      min_arity=1,
      max_arity=1,
      constraint_portal_type=('Test Migration',),
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
      constraint_portal_type=('Test Migration',),
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
    portal = self.getPortal()

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

      # Create a Category Membership Arity Constraint in the test
      # Property Sheet
      self._newCategoryMembershipArityConstraint(
        'test_category_membership_arity_constraint',
        'Category Membership Arity Constraint')

      # Create a Category Acquired Membership Arity Constraint in the
      # test Property Sheet
      self._newCategoryMembershipArityConstraint(
        'test_category_acquired_membership_arity_constraint',
        'Category Acquired Membership Arity Constraint')

      # Create a Category Related Membership Arity Constraint in the
      # test Property Sheet
      self._newCategoryRelatedMembershipArityConstraint()

      # Create a TALES Constraint in the test Property Sheet
      self._newTALESConstraint()

      # Create a Property Type Validity Constraint in the test Property Sheet
      self._newPropertyTypeValidityConstraint()

      # Create all the test Properties
      for operation_type in ('change', 'delete', 'assign'):
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
        type_allowed_content_type_list=('Content Existence Constraint',))

    # Create a test module, meaningful to force generation of
    # TestMigration accessor holders and check the constraints
    try:
      self.test_module = getattr(portal, 'Test Migration')
    except AttributeError:
      self.test_module = portal.newContent(id='Test Migration',
                                           portal_type='Test Migration')

    # Make sure there is no pending transaction which could interfere
    # with the tests
    transaction.commit()
    self.tic()

    # Ensure that erp5.acessor_holder is empty
    synchronizeDynamicModules(portal, force=True)

  def _forceTestAccessorHolderGeneration(self):
    """
    Force generation of TestMigration accessor holder by accessing any
    accessor, which will run the interaction workflow trigger, on
    commit at the latest
    """
    transaction.commit()
    self.test_module.getId()

  def assertHasAttribute(self, obj, attribute, msg=None):
    self.failIfEqual(None, getattr(obj, attribute, None),
                     msg or '%s: no attribute %s' % (obj.__name__,
                                                     attribute))

  def failIfHasAttribute(self, obj, attribute, msg=None):
    self.assertEquals(None, getattr(obj, attribute, None),
                      msg or '%s: attribute %s present' % (obj.__name__,
                                                           attribute))

  def testAssignUnassignZodbPropertySheet(self):
    """
    From an existing portal type, assign ZODB Property Sheets and
    check that
    """
    import erp5

    portal = self.getPortal()
    person_type = portal.portal_types.Person

    self.failIf('TestMigration' in person_type.getTypePropertySheetList())

    new_person = None
    try:
      # Assign ZODB test Property Sheet to the existing Person type
      # and create a new Person, this should generate the test
      # accessor holder which should be in the Person type inheritance
      person_type.setTypePropertySheetList('TestMigration')

      transaction.commit()

      self.assertTrue('TestMigration' in person_type.getTypePropertySheetList())

      # The accessor holder will be generated once the new Person will
      # be created as Person type has test Property Sheet
      self.failIfHasAttribute(erp5.accessor_holder, 'TestMigration')

      new_person = portal.person_module.newContent(
        id='testAssignZodbPropertySheet', portal_type='Person')

      self.assertHasAttribute(erp5.accessor_holder, 'TestMigration')

      self.assertTrue(erp5.accessor_holder.TestMigration in \
                      erp5.portal_type.Person.mro())

      # Check that the accessors have been properly created for all
      # the properties of the test Property Sheet and set a new value
      # to make sure that everything is fine
      #
      # Standard Property
      self.assertHasAttribute(new_person, 'setTestStandardPropertyAssign')

      self.assertEquals(new_person.getTestStandardPropertyAssign(),
                        "test_default_value")

      new_person.setTestStandardPropertyAssign('value')

      self.assertEquals(new_person.getTestStandardPropertyAssign(), 'value')

      # Acquired Property
      self.assertHasAttribute(
        new_person, 'setDefaultTestAcquiredPropertyAssignStreetAddress')

      new_person.setDefaultTestAcquiredPropertyAssignStreetAddress('value')

      self.assertHasAttribute(new_person, 'default_address')
      self.assertHasAttribute(new_person.default_address, 'getDefaultAddress')
      self.failIfEqual(None, new_person.default_address.getDefaultAddress())

      self.assertEquals(
        new_person.getDefaultTestAcquiredPropertyAssignStreetAddress(),
        'value')

      # Category Property
      self.assertHasAttribute(new_person, 'setTestCategoryPropertyAssign')

      new_person.setTestCategoryPropertyAssign('sub_category1')

      self.assertEquals(new_person.getTestCategoryPropertyAssign(),
                        'sub_category1')

      # Dynamic Category Property
      self.assertHasAttribute(new_person,
                              'setTestDynamicCategoryPropertyAssign')

      new_person.setTestDynamicCategoryPropertyAssign('sub_category1')

      self.assertEquals(new_person.getTestDynamicCategoryPropertyAssign(),
                        'sub_category1')

    finally:
      # Perform a commit here because Workflow interactions keeps a
      # TransactionalVariable whose key is computed from the ID of the
      # workflow and the ID of the interaction and where the value is
      # a boolean stating whether the transition method has already
      # been called before.  Thus, the next statement may not reset
      # erp5.accessor_holder as loading Person portal type calls
      # '_setType*'
      transaction.commit()

      person_type.setTypePropertySheetList(())

      if new_person is not None:
        portal.person_module.deleteContent(new_person.getId())

      new_person = None

    # Check that the new-style Property Sheet has been properly
    # unassigned by creating a new person in Person module
    transaction.commit()

    self.failIf('TestMigration' in person_type.getTypePropertySheetList())

    try:
      new_person = portal.person_module.newContent(
        id='testAssignZodbPropertySheet', portal_type='Person')

      self.failIfHasAttribute(erp5.accessor_holder, 'TestMigration')
      self.failIfHasAttribute(new_person, 'getTestStandardPropertyAssign')

    finally:
      if new_person is not None:
        portal.person_module.deleteContent(new_person.getId())

  def _checkAddPropertyToZodbPropertySheet(self,
                                          new_property_function,
                                          added_accessor_name):
    import erp5.accessor_holder

    self.failIfHasAttribute(erp5.accessor_holder, 'TestMigration')

    new_property_function('add')
    self._forceTestAccessorHolderGeneration()

    self.assertHasAttribute(erp5.accessor_holder, 'TestMigration')
    self.assertHasAttribute(erp5.accessor_holder.TestMigration,
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

  def _checkChangePropertyOfZodbPropertySheet(self,
                                             change_setter_func,
                                             new_value,
                                             changed_accessor_name):
    import erp5.accessor_holder

    self.failIfHasAttribute(erp5.accessor_holder, 'TestMigration')

    change_setter_func(new_value)
    self._forceTestAccessorHolderGeneration()

    self.assertHasAttribute(erp5.accessor_holder, 'TestMigration')
    self.assertHasAttribute(erp5.accessor_holder.TestMigration,
                            changed_accessor_name)

  def testChangeStandardPropertyOfZodbPropertySheet(self):
    """
    Take the test Property Sheet, change the 'reference' field of a
    Standard Property and check that the accessor name has changed
    """
    self._checkChangePropertyOfZodbPropertySheet(
      self.test_standard_property_change.setReference,
      'test_standard_property_change_renamed',
      'getTestStandardPropertyChangeRenamed')

  def testChangeAcquiredPropertyOfZodbPropertySheet(self):
    """
    Take the test Property Sheet, change the 'reference' field of an
    Acquired Property and check that the accessor name has changed
    """
    self._checkChangePropertyOfZodbPropertySheet(
      self.test_acquired_property_change.setReference,
      'test_acquired_property_change_renamed',
      'getDefaultTestAcquiredPropertyChangeRenamedStreetAddress')

  def testChangeCategoryPropertyOfZodbPropertySheet(self):
    """
    Take the test Property Sheet, change the 'id' field of a Category
    Property to another existing category and check that the accessor
    name has changed
    """
    self._checkChangePropertyOfZodbPropertySheet(
      self.test_category_property_change.setReference,
      'test_category_property_change_renamed',
      'getTestCategoryPropertyChangeRenamed')

  def testChangeDynamicCategoryPropertyOfZodbPropertySheet(self):
    """
    Take the test Property Sheet, change the 'category_expression'
    field of a Dynamic Category Property to another existing category
    and check that the accessor name has changed
    """
    self._checkChangePropertyOfZodbPropertySheet(
      self.test_dynamic_category_property_change.setCategoryExpression,
      "python: ('test_dynamic_category_property_change_renamed',)",
      'getTestDynamicCategoryPropertyChangeRenamed')

  def _checkDeletePropertyFromZodbPropertySheet(self,
                                               property_id,
                                               accessor_name):
    """
    Delete the given property from the test Property Sheet and check
    whether its corresponding accessor is not there anymore
    """
    import erp5.accessor_holder

    self.failIfHasAttribute(erp5.accessor_holder, 'TestMigration')

    # Delete the property and force re-generation of TestMigration
    # accessor holder
    self.test_property_sheet.deleteContent(property_id)
    self._forceTestAccessorHolderGeneration()

    self.assertHasAttribute(erp5.accessor_holder, 'TestMigration')
    self.failIfHasAttribute(erp5.accessor_holder.TestMigration,
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
    self.failIfEqual(None, constraint)
    self.assertEquals(1, len(constraint.checkConsistency(self.test_module)))

    setter_function(*args, **kw)
    self.assertEquals([], constraint.checkConsistency(self.test_module))

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
    Take the test module and check whether the Content Existence
    Constraint is there. Until there is at least one subobject of
    'Test Module' whose Portal Type is 'Folder', the constraint should
    fail
    """
    self._checkConstraint('test_content_existence_constraint',
                          self.test_module.newContent,
                          id='Test Content Existence Constraint',
                          portal_type='Content Existence Constraint')

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

  def testCategoryAcquiredMembershipArityConstraint(self):
    """
    Take the test module and check whether the Category Acquired
    Membership Arity Constraint is there. Until a Base Category is set
    on the Test Module, the constraint should fail

    XXX: Test with acquisition?
    """
    self._checkConstraint(
      'test_category_acquired_membership_arity_constraint',
      self.test_module.setCategoryList,
      ('test_category_acquired_membership_arity_constraint/Test Migration',))

  def testCategoryRelatedMembershipArityConstraint(self):
    """
    Take the test module and check whether the Category Related
    Membership Arity Constraint is there. Until a Base Category is set
    on the Test Module, the constraint should fail

    XXX: Test filter_parameter
    """
    constraint = self._getConstraintByReference(
      'test_category_related_membership_arity_constraint')

    self.failIfEqual(None, constraint)
    self.assertEquals(1, len(constraint.checkConsistency(self.test_module)))

    self.test_module.setCategoryList(('gender/Test Migration',))
    transaction.commit()
    self.tic()

    self.assertEquals([], constraint.checkConsistency(self.test_module))

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

from Products.ERP5Type import PropertySheet
from Products.CMFCore.Expression import Expression

class TestZodbImportFilesystemPropertySheet(ERP5TypeTestCase):
  """
  Check that importing filesystem Property Sheets into ZODB the same
  properties and their values
  """
  # The following fields of properties are no longer defined in ZODB
  # Property Sheets because they have been deprecated
  deprecated_field_name_tuple = ('mode',
                                 'select_variable',
                                 'label',
                                 'acquisition_depends',
                                 'acquisition_sync_value')

  def afterSetUp(self):
    # Mapping between the field name of a property and the default
    # value as defined in StandardProperty and AcquiredProperty,
    # meaningful because exporting a property relies on accessor which
    # returns the default value if the field value is not set
    self.filesystem_field_default_value_dict = {}

    from Products.ERP5Type.PropertySheet import StandardProperty, AcquiredProperty
    for property_dict in StandardProperty._properties + AcquiredProperty._properties:
      try:
        self.filesystem_field_default_value_dict[property_dict['id']] = \
            property_dict['default']
      except KeyError:
        # Some fields may not defined a default value (such as 'id')
        continue

  def _checkPropertyField(self,
                          property_sheet_name,
                          field_name,
                          filesystem_value,
                          zodb_value):
    """
    Check whether the given filesystem property value and the given
    ZODB property value are equal
    """
    if isinstance(zodb_value, (list, tuple)):
      self.failIfDifferentSet(
        zodb_value, filesystem_value,
        msg="%s: %s: filesystem value: %s, ZODB value: %s" % \
          (property_sheet_name, field_name, filesystem_value, zodb_value))

    else:
      # In ZODB Property Sheets, we have to get the TALES Expression
      # as a string for properties, which used to be Expression in
      # filesystem Property Sheets or are now Expression (because they
      # used to be defined as Python types, such as tuple or int...)
      if isinstance(zodb_value, Expression):
        # In filesystem Property Sheets, acquisition_portal_type and
        # portal_type, might be instances of Expression
        if isinstance(filesystem_value, Expression):
          zodb_value = zodb_value.text
          filesystem_value = filesystem_value.text
        # Otherwise, just convert the filesystem value to a TALES
        # Expression string
        else:
          zodb_value = zodb_value.text
          filesystem_value = 'python: ' + repr(filesystem_value)

      self.failUnlessEqual(
        zodb_value, filesystem_value,
        msg="%s: %s: filesystem value: %s, ZODB value: %s" % \
          (property_sheet_name, field_name, filesystem_value,
           zodb_value))

  def _checkPropertyDefinitionTuple(self,
                                    property_sheet_name,
                                    filesystem_property_tuple,
                                    zodb_property_tuple):
    """
    Check whether all properties have been properly converted from
    the filesystem to the ZODB Property Sheet
    """
    # Check whether all the properties are present in the given ZODB
    # Property Sheet
    self.assertEqual(
      len(filesystem_property_tuple), len(zodb_property_tuple),
      msg="%s: too many properties: filesystem: %s, ZODB: %s" % \
      (property_sheet_name, filesystem_property_tuple, zodb_property_tuple))

    # Map filesystem property IDs to their definition
    filesystem_property_id_dict = {}
    for property_dict in filesystem_property_tuple:
      filesystem_property_id_dict[property_dict['id']] = property_dict

    # Check each property defined in ZODB against the filesystem dict
    # defined before
    for zodb_property_dict in zodb_property_tuple:
      # Meaningful to ensure that there is no missing field within a
      # property
      validated_field_counter = 0

      filesystem_property_dict = \
         filesystem_property_id_dict[zodb_property_dict['id']]

      # Check each property field
      for field_name, zodb_value in zodb_property_dict.iteritems():
        if field_name in filesystem_property_dict:
          self._checkPropertyField(property_sheet_name,
                                   field_name,
                                   filesystem_property_dict[field_name],
                                   zodb_value)
        # As we are using accessors when exporting the ZODB Property
        # Sheet to its filesystem definition, there may be additional
        # fields set to their default value
        elif field_name in self.filesystem_field_default_value_dict:
          self.assertEqual(
            self.filesystem_field_default_value_dict[field_name],
            zodb_value,
            msg="%s: Wrong default value %s for %s" % \
                (property_sheet_name, zodb_value, field_name))

        validated_field_counter += 1

      if len(filesystem_property_dict) != validated_field_counter:
        missing_field_name_list = [
          k for k in filesystem_property_dict \
          if k not in zodb_property_dict and \
             k not in self.deprecated_field_name_tuple ]

        self.assertTrue(
          len(missing_field_name_list) == 0,
          msg="%s: missing fields: %s: filesystem: %s, ZODB: %s" % \
          (property_sheet_name, missing_field_name_list,
           filesystem_property_dict, zodb_property_dict))

  def _checkCategoryTuple(self,
                          property_sheet_name,
                          filesystem_category_tuple,
                          zodb_category_tuple):
    """
    Check whether all categories have been properly converted
    """
    # There should be the same number of categories
    self.assertEqual(
      len(filesystem_category_tuple), len(zodb_category_tuple),
      msg="%s: Missing/added categories: filesystem: %s, ZODB: %s" % \
      (property_sheet_name, filesystem_category_tuple, zodb_category_tuple))

    # Some Categories are instance of Expression, so compute a list of
    # categories as strings
    zodb_category_list = [
      isinstance(category, Expression) and category.text or category \
      for category in zodb_category_tuple ]

    # Now, compare filesystem categories with ZODB
    for category in filesystem_category_tuple:
      if isinstance(category, Expression):
        category = category.text

      self.assertTrue(
        category in zodb_category_list,
        msg="%s: Missing category %s: ZODB: %s" % \
        (property_sheet_name, category, zodb_category_list))

  def testZodbImportPropertySheet(self):
    """
    Create Property Sheets on portal_property_sheets from their
    definition on the filesystem and then test that they are
    equivalent

    TODO: Constraints
    """
    portal = self.getPortalObject().portal_property_sheets

    from Products.ERP5Type import PropertySheet
    # Get all the property sheets defined on the filesystem
    for name, klass in PropertySheet.__dict__.iteritems():
      if name[0] == '_' or isinstance(klass, basestring):
        continue
      filesystem_property_sheet = klass
      property_sheet_name = name

      # Rename the filesystem Property Sheet class to avoid clashing
      # with existing Property Sheets in portal_property_sheets
      filesystem_property_sheet.__name__ = "%s_%s" % \
          (self.__class__.__name__, property_sheet_name)

      zodb_property_sheet = portal.createPropertySheetFromFilesystemClass(
        filesystem_property_sheet)

      zodb_property_tuple, zodb_category_tuple, zodb_constraint_tuple = \
          portal.exportPropertySheetToFilesystemDefinitionTuple(
              zodb_property_sheet)

      self._checkPropertyDefinitionTuple(property_sheet_name,
                                         getattr(filesystem_property_sheet,
                                                 '_properties', []),
                                         zodb_property_tuple)

      self._checkCategoryTuple(property_sheet_name,
                               getattr(filesystem_property_sheet,
                                       '_categories', []),
                               zodb_category_tuple)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPortalTypeClass))
  suite.addTest(unittest.makeSuite(TestZodbPropertySheet))
  suite.addTest(unittest.makeSuite(TestZodbImportFilesystemPropertySheet))
  return suite
