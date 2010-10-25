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

import os, shutil
import unittest

import transaction

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.backportUnittest import skip

class TestPortalTypeClass(ERP5TypeTestCase):
  def getBusinessTemplateList(self):
    return 'erp5_base',

  def testImportNonMigratedPerson(self):
    """
    Import a .zexp containing a Person created with an old
    Products.ERP5Type.Document.Person.Person type
    """
    file_name = 'non_migrated_person.zexp'
    import Products.ERP5Type.tests as test_module
    test_path = test_module.__path__
    if isinstance(test_path, list):
      test_path = test_path[0]

    zexp_path = os.path.join(test_path, 'input', file_name)
    self.assertTrue(os.path.exists(zexp_path))

    import_path = os.path.join(os.environ['INSTANCE_HOME'], 'import')
    if not os.path.exists(import_path):
      os.mkdir(import_path)
    shutil.copy(zexp_path, import_path)

    person_module = self.getPortal().person_module
    person_module.manage_importObject(file_name)

    transaction.commit()

    non_migrated_person = person_module.non_migrated_person
    # check that object unpickling instanciated a new style object
    from erp5.portal_type import Person as erp5_document_person
    self.assertEquals(non_migrated_person.__class__, erp5_document_person)

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
    self.assertEquals(person_type.getTypeMixinList(), None)

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
    return self.test_property_sheet.newContent(
      portal_type='Standard Property',
      reference='test_standard_property_' + operation_type,
      elementary_type='string')

  def _newAcquiredProperty(self, operation_type):
    """
    Create a new Acquired Property within test Property Sheet
    """
    return self.test_property_sheet.newContent(
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
    new_base_category.newContent(reference='sub_category',
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

    return self.test_property_sheet.newContent(
      reference=category_id,
      portal_type='Category Property')

  def _newDynamicCategoryProperty(self, operation_type):
    """
    Create a new Dynamic Category Property within test Property Sheet
    """
    category_id = 'test_dynamic_category_property_' + operation_type

    self._newCategoryTree(category_id, operation_type)

    expression = "python: ('%s',)" % category_id

    return self.test_property_sheet.newContent(
      portal_type='Dynamic Category Property',
      category_expression=expression,
      reference=category_id)

  def _newPropertyExistenceConstraint(self):
    """
    Create a new Property Existence Constraint within test Property
    Sheet
    """
    return self.test_property_sheet.newContent(
      reference='test_property_existence_constraint',
      portal_type='Property Existence Constraint',
      constraint_property_list=('test_standard_property_constraint',))

  def _newCategoryExistenceConstraint(self):
    """
    Create a new Category Existence Constraint within test Property
    Sheet
    """
    self._newCategoryProperty('constraint')

    return self.test_property_sheet.newContent(
      reference='test_category_existence_constraint',
      portal_type='Category Existence Constraint',
      constraint_base_category_list=('test_category_property_constraint',))
      # XXX
      # constraint_portal_type=('TODO',))

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

      # Create all the test Properties
      for op in ('change', 'delete', 'assign'):
        self._newStandardProperty(op)
        self._newAcquiredProperty(op)
        self._newCategoryProperty(op)
        self._newDynamicCategoryProperty(op)

    # Bind all test properties to this instance, so they can be
    # accessed easily in further tests
    for prop in self.test_property_sheet.contentValues():
      setattr(self, prop.getReference(), prop)

    # Create a Portal Type for the tests, this is necessary, otherwise
    # there will be no accessor holder generated
    try:
      self.test_portal_type = getattr(portal.portal_types, 'Test Migration')
    except AttributeError:
      self.test_portal_type = portal.portal_types.newContent(
        id='Test Migration',
        portal_type='Base Type',
        type_class='Folder',
        # XXX: to be renamed to type_property_sheet_list as soon as
        #      the migration has been finished
        type_zodb_property_sheet_list=('TestMigration',),
        type_base_category_list=('test_category_existence_constraint',))

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
    from Products.ERP5Type.Dynamic.portaltypeclass import \
        synchronizeDynamicModules

    synchronizeDynamicModules(portal, force=True)

    # Make sure there is no pending transaction which could interfere
    # with the tests
    transaction.commit()
    self.tic()

  def _forceTestAccessorHolderGeneration(self):
    """
    Force generation of TestMigration accessor holder by accessing any
    accessor, which will run the interaction workflow trigger, on
    commit at the latest
    """
    self.test_module.getId()
    transaction.commit()

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

    self.failIf('TestMigration' in \
                (person_type.getTypeZodbPropertySheetList() or []))

    new_person = None
    try:
      # Assign ZODB test Property Sheet to the existing Person type
      # and create a new Person, this should generate the test
      # accessor holder which should be in the Person type inheritance
      person_type.setTypeZodbPropertySheetList('TestMigration')

      transaction.commit()

      self.assertTrue('TestMigration' in \
                      person_type.getTypeZodbPropertySheetList())

      # The accessor holder will be generated once the new Person will
      # be created as Person type has test Property Sheet
      self.failIfHasAttribute(erp5.zodb_accessor_holder, 'TestMigration')

      new_person = portal.person_module.newContent(
        id='testAssignZodbPropertySheet', portal_type='Person')

      self.assertHasAttribute(erp5.zodb_accessor_holder, 'TestMigration')

      self.assertTrue(erp5.zodb_accessor_holder.TestMigration in \
                      erp5.portal_type.Person.mro())

      # Check that the accessors have been properly created for all
      # the properties of the test Property Sheet and set a new value
      # to make sure that everything is fine
      #
      # Standard Property
      self.assertHasAttribute(new_person, 'setTestStandardPropertyAssign')

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

      new_person.setTestCategoryPropertyAssign('sub_category')

      self.assertEquals(new_person.getTestCategoryPropertyAssign(),
                        'sub_category')

      # Dynamic Category Property
      self.assertHasAttribute(new_person,
                              'setTestDynamicCategoryPropertyAssign')

      new_person.setTestDynamicCategoryPropertyAssign('sub_category')

      self.assertEquals(new_person.getTestDynamicCategoryPropertyAssign(),
                        'sub_category')

    finally:
      # Perform a commit here because Workflow interactions keeps a
      # TransactionalVariable whose key is computed from the ID of the
      # workflow and the ID of the interaction and where the value is
      # a boolean stating whether the transition method has already
      # been called before.  Thus, the next statement may not reset
      # erp5.zodb_accessor_holder as loading Person portal type calls
      # '_setType*'
      transaction.commit()

      person_type.setTypeZodbPropertySheetList(None)

      if new_person is not None:
        portal.person_module.deleteContent(new_person.getId())

      new_person = None

    # Check that the new-style Property Sheet has been properly
    # unassigned by creating a new person in Person module
    transaction.commit()

    self.failIf('TestMigration' in \
                (person_type.getTypeZodbPropertySheetList() or []))

    try:
      new_person = portal.person_module.newContent(
        id='testAssignZodbPropertySheet', portal_type='Person')

      self.failIfHasAttribute(new_person, 'getTestStandardPropertyAssign')
      self.failIfHasAttribute(erp5.zodb_accessor_holder, 'TestMigration')

    finally:
      if new_person is not None:
        portal.person_module.deleteContent(new_person.getId())

  def _checkAddPropertyToZodbPropertySheet(self,
                                          new_property_function,
                                          added_accessor_name):
    import erp5.zodb_accessor_holder

    self.failIfHasAttribute(erp5.zodb_accessor_holder, 'TestMigration')

    new_property_function('add')
    self._forceTestAccessorHolderGeneration()

    self.assertHasAttribute(erp5.zodb_accessor_holder, 'TestMigration')
    self.assertHasAttribute(erp5.zodb_accessor_holder.TestMigration,
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
    import erp5.zodb_accessor_holder

    self.failIfHasAttribute(erp5.zodb_accessor_holder, 'TestMigration')

    change_setter_func(new_value)
    self._forceTestAccessorHolderGeneration()

    self.assertHasAttribute(erp5.zodb_accessor_holder, 'TestMigration')
    self.assertHasAttribute(erp5.zodb_accessor_holder.TestMigration,
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
    import erp5.zodb_accessor_holder

    self.failIfHasAttribute(erp5.zodb_accessor_holder, 'TestMigration')

    # Delete the property and force re-generation of TestMigration
    # accessor holder
    self.test_property_sheet.deleteContent(property_id)
    self._forceTestAccessorHolderGeneration()

    self.assertHasAttribute(erp5.zodb_accessor_holder, 'TestMigration')
    self.failIfHasAttribute(erp5.zodb_accessor_holder.TestMigration,
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

  def testPropertyExistenceConstraint(self):
    """
    Take the test module and check whether the Property Existence
    Constraint is available. Until the property has been set to a
    value, the constraint should fail
    """
    constraint = self._getConstraintByReference(
      'test_property_existence_constraint')

    self.failIfEqual(None, constraint)

    self.assertEquals(1, len(constraint.checkConsistency(self.test_module)))

    # See ERP5Type.Base.Base.hasProperty()
    self.test_module.setTestStandardPropertyConstraint('foobar')

    self.assertEquals([], constraint.checkConsistency(self.test_module))

  def testCategoryExistenceConstraint(self):
    """
    Take the test module and check whether the Property Existence
    Constraint is available. Until the category has been set to an
    existing category, the constraint should fail
    """
    constraint = self._getConstraintByReference(
      'test_category_existence_constraint')

    self.failIfEqual(None, constraint)

    self.assertEquals(1, len(constraint.checkConsistency(self.test_module)))

    self.test_module.setTestCategoryPropertyConstraint('sub_category')

    self.assertEquals([], constraint.checkConsistency(self.test_module))

TestZodbPropertySheet = skip("ZODB Property Sheets code is not enabled yet")(
  TestZodbPropertySheet)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPortalTypeClass))
  suite.addTest(unittest.makeSuite(TestZodbPropertySheet))
  return suite
