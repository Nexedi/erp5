# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005-2012 Nexedi SA and Contributors. All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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

import six
import unittest
from unittest import expectedFailure

from erp5.component.test.testERP5Type import PropertySheetTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.Sequence import SequenceList


class TestConstraint(PropertySheetTestCase):

  object_portal_type = "Organisation"
  object_content_portal_type = "Address"
  object_title = "Title test"

  def getTitle(self):
    return "Constraint"

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base',)

  def login(self):  # pylint:disable=arguments-differ
    uf = self.portal.acl_users
    uf._doAddUser('rc', '', ['Manager'], [])
    user = uf.getUserById('rc').__of__(uf)
    newSecurityManager(None, user)

  def stepLoginAsAssignee(self, sequence=None, sequence_list=None, **kw):
    uf = self.portal.acl_users
    uf._doAddUser('member', '', ['Member', 'Assignee'], [])
    user = uf.getUserById('member').__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    self.login()
    self.category_tool = self.getCategoryTool()
    self.createCategories()
    portal_property_sheets = self.portal.portal_property_sheets
    if getattr(portal_property_sheets, "test_constraint", None) != None:
      portal_property_sheets.manage_delObjects(ids=["test_constraint"])

  def beforeTearDown(self):
    self.login()
    self.abort()
    module = self.portal.organisation_module
    module.manage_delObjects(list(module.objectIds()))
    super(TestConstraint, self).beforeTearDown()
    portal_type = self.portal.portal_types[self.object_portal_type]
    if "TestConstraint" in portal_type.getTypePropertySheetList():
      portal_type.setTypePropertySheetList(
       [x for x in portal_type.getTypePropertySheetList() \
        if x != "TestConstraint"])

  def createCategories(self):
    """
      Light install create only base categories, so we create
      some categories for testing them
    """
    category_list = ['testGroup1', 'testGroup2']
    group = self.category_tool.group
    if 'testGroup1' not in group.contentIds():
      for category_id in category_list:
        group.newContent(portal_type='Category',
                             id=category_id)

  def stepDeleteObjectModuleContent(self, sequence=None,
                                    sequence_list=None, **kw):
    """
      Delete all objects in the module.
    """
    module = self.portal.getDefaultModule(self.object_portal_type)
    module.manage_delObjects(module.contentIds())

  def _makeOne(self):
    """Creates an object and reindex it
    """
    module = self.portal.getDefaultModule(self.object_portal_type)
    obj = module.newContent(portal_type=self.object_portal_type)
    self.tic()
    return obj

  def stepCreateObject(self, sequence=None, sequence_list=None, **kw):
    """
      Create a object which will be tested.
    """
    module = self.portal.getDefaultModule(self.object_portal_type)
    document = module.newContent(portal_type=self.object_portal_type)
    group1 = document.portal_categories.restrictedTraverse('group/testGroup1')
    if sequence:
      sequence.edit(
          document=document,
          group=group1,
      )
    return document

  def stepSetObjectGroup(self, sequence=None,
                         sequence_list=None, **kw):
    """
      Set a group to object
    """
    document = sequence.get('document')
    document.edit(group='testGroup1')
    self.assertNotEqual(
          document.getGroup(portal_type=()),
          None )

  def stepSetObjectGroupOrganisation(self, sequence=None,
                         sequence_list=None, **kw):
    """
      Set a group to object, forcing portal_type color to Organisation
    """
    document = sequence.get('document')
    document.setGroup(document.getRelativeUrl(),
                    portal_type='Organisation')
    self.assertNotEqual(
          document.getGroup(portal_type='Organisation'),
          None )

  def stepSetObjectGroupList(self, sequence=None,
                             sequence_list=None, **kw):
    """
      Set a group to object
    """
    document = sequence.get('document')
    document.edit(group_list=['testGroup1', 'testGroup2'])

  def stepSetObjectTitle(self, sequence=None,
                         sequence_list=None, **kw):
    """
      Set a different title value
    """
    document = sequence.get('document')
    object_title = self.object_title
    document.setTitle(object_title)

  def stepSetObjectNoneTitle(self, sequence=None,
                             sequence_list=None, **kw):
    """
      Set a different title value
    """
    document = sequence.get('document')
    # Do not call edit, as we want to explicitely modify the property
    # (and edit modify only if value is different)
    document.setTitle(None)

  def stepSetObjectEmptyTitle(self, sequence=None,
                              sequence_list=None, **kw):
    """
      Set a different title value
    """
    document = sequence.get('document')
    # Do not call edit, as we want to explicitely modify the property
    # (and edit modify only if value is different)
    document.setTitle('')

  def stepSetObjectIntTitle(self, sequence=None,
                            sequence_list=None, **kw):
    """
      Set a different title value
    """
    document = sequence.get('document')
    document.edit(title=12345)

  def stepSetObjectBadTypedProperty(self, sequence=None,
                            sequence_list=None, **kw):
    """
      Set a property with a bad type
    """
    document = sequence.get('document')
    property_name = 'ean13code'
    # make sure the property is defined on the document
    self.assertTrue(not document.hasProperty(property_name))
    self.assertTrue(document.getPropertyType(property_name) != 'int')
    document.setProperty(property_name, 12)

  def stepSetObjectIntLocalProperty(self, sequence=None,
                            sequence_list=None, **kw):
    """
      Set a local property on the document, with an int type.
    """
    document = sequence.get('document')
    document.edit(local_prop = 12345)

  def _createGenericConstraint(self, sequence=None, klass_name='Constraint',
                               **kw):
    """
      Create a Constraint
    """
    from Products.ERP5Type import Constraint
    module = Constraint
    file_path = "%s.%s" % (module.__name__, klass_name)
    __import__(file_path)
    klass = getattr(module, klass_name)
    constraint = klass(**kw)
    if sequence is not None:
      sequence.edit(constraint=constraint,)
    return constraint

  def stepCallCheckConsistency(self, sequence=None,
                               sequence_list=None, **kw):
    """
      Call checkConsistency of a Constraint.
    """
    document = sequence.get('document')
    constraint = sequence.get('constraint')
    # Check
    error_list = constraint.checkConsistency(document)
    sequence.edit(
        error_list=error_list
    )

  def stepCallFixConsistency(self, sequence=None,
                                      sequence_list=None, **kw):
    """
      Call checkConsistency of a Constraint, fixing the errors.
    """
    document = sequence.get('document')
    constraint = sequence.get('constraint')
    # Check
    error_list = constraint.checkConsistency(document, fixit=1)
    sequence.edit(
        error_list=error_list
    )

  def stepCallRelatedCheckConsistency(self, sequence=None,
                                      sequence_list=None, **kw):
    """
    Call checkConsistency of a Constraint.
    """
    document = sequence.get('group')
    constraint = sequence.get('constraint')
    # Check
    error_list = constraint.checkConsistency(document)
    sequence.edit(
        error_list=error_list
    )

  def stepCheckIfConstraintSucceeded(self, sequence=None,
                                     sequence_list=None, **kw):
    """
    Check that checkConsistency returns an empty list
    """
    error_list = sequence.get('error_list')
    self.failIfDifferentSet(error_list, [],
          "error_list : %s" % [x.message for x in error_list])

  def stepCheckIfConstraintFailed(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Check that checkConsistency does not return an empty list
    """
    error_list = sequence.get('error_list')
    self.assertTrue(error_list != [],
                    "error_list : %s" % error_list)
    # call getTranslatedMessage, to make sure messages have a valid mapping.
    for error in error_list:
      self.assertNotEqual('',
                           error.getTranslatedMessage())


  def stepCreateConstraint(self, sequence=None,
                           sequence_list=None, **kw):
    """
      Create a default Constraint
    """
    self._createGenericConstraint(sequence,
                                  klass_name='Constraint',
                                  id='default_constraint',
                                  description='constraint test')

  def test_01_Constraint(self):
    """
      Test default Constraint class
    """
    sequence_list = SequenceList()
    # Test Constraint without any configuration
    sequence_string = '\
              CreateObject \
              CreateConstraint \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCreatePropertyExistence0(self, sequence=None,
                                  sequence_list=None, **kw):
    """
      Create a PropertyExistence Constraint
    """
    self._createGenericConstraint(sequence,
                                  klass_name='PropertyExistence',
                                  id='property_existence',
                                  description='propertyExistence test')

  def stepCreatePropertyExistence1(self, sequence=None,
                                   sequence_list=None, **kw):
    """
      Create a PropertyExistence Constraint
    """
    self._createGenericConstraint(sequence,
                                  klass_name='PropertyExistence',
                                  id='property_existence',
                                  description='propertyExistence test',
                                  not_defined_property=None)

  def stepCreatePropertyExistence1TrueCondition(self, sequence=None,
                                   sequence_list=None, **kw):
    """
      Create a PropertyExistence Constraint with a true condition
    """
    self._createGenericConstraint(sequence,
                                  klass_name='PropertyExistence',
                                  id='property_existence',
                                  description='propertyExistence test',
                                  not_defined_property=None,
                                  condition='python: object.getPortalType()' \
                                      + ' == "%s"' % self.object_portal_type)

  def stepCreatePropertyExistence1FalseCondition(self, sequence=None,
                                   sequence_list=None, **kw):
    """
      Create a PropertyExistence Constraint with a false condition
    """
    self._createGenericConstraint(sequence,
                                  klass_name='PropertyExistence',
                                  id='property_existence',
                                  description='propertyExistence test',
                                  not_defined_property=None,
                                  condition='python: object.getPortalType()' \
                                      + ' == "False_PortalTypeXXX123"')

  def stepCreatePropertyExistence2(self, sequence=None,
                                   sequence_list=None, **kw):
    """
      Create a PropertyExistence Constraint
    """
    self._createGenericConstraint(sequence,
                                  klass_name='PropertyExistence',
                                  id='property_existence',
                                  description='propertyExistence test',
                                  title=None)

  def test_02_PropertyExistence(self):
    """
      Test property existence
    """
    sequence_list = SequenceList()
    # Test Constraint without any configuration
    sequence_string = '\
              CreateObject \
              CreatePropertyExistence0 \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property not defined in PropertySheet
    sequence_string = '\
              CreateObject \
              CreatePropertyExistence1 \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property not defined in PropertySheet and true
    # condition
    sequence_string = '\
              CreateObject \
              CreatePropertyExistence1TrueCondition \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property not defined in PropertySheet and false
    # condition
    sequence_string = '\
              CreateObject \
              CreatePropertyExistence1FalseCondition \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)

    # Test Constraint without title property
    # on object
    sequence_string = '\
              CreateObject \
              CreatePropertyExistence2 \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property defined on object
    # With None value
    # None is considered as a NULL value for string
    # and so, is considered as no data
    sequence_string = '\
              CreateObject \
              SetObjectNoneTitle \
              CreatePropertyExistence2 \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property defined on object
    # With '' value
    sequence_string = '\
              CreateObject \
              SetObjectEmptyTitle \
              CreatePropertyExistence2 \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property defined on object
    sequence_string = '\
              CreateObject \
              SetObjectTitle \
              CreatePropertyExistence2 \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCreatePropertyTypeValidity(self, sequence=None,
                                     sequence_list=None, **kw):
    """
      Create a PropertyExistence Constraint
    """
    self._createGenericConstraint(sequence,
                                  klass_name='PropertyTypeValidity',
                                  id='property_type_validity',
                                  description='propertyTypeValidity test')

  def test_03_PropertyTypeValidity(self):
    """
      Test property type validity
    """
    sequence_list = SequenceList()
    # Test Constraint without any configuration
    sequence_string = '\
              CreateObject \
              CreatePropertyTypeValidity \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property defined on object
    # With None value
    sequence_string = '\
              CreateObject \
              SetObjectNoneTitle \
              CreatePropertyTypeValidity \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property defined on object
    # With '' value
    sequence_string = '\
              CreateObject \
              SetObjectEmptyTitle \
              CreatePropertyTypeValidity \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property defined on object
    sequence_string = '\
              CreateObject \
              SetObjectTitle \
              CreatePropertyTypeValidity \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property defined on object
    # with a bad type
    sequence_string = '\
              CreateObject \
              SetObjectBadTypedProperty \
              CreatePropertyTypeValidity \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property defined on object
    # with a bad type (title is an exception, because it converts the
    # value ...)
    sequence_string = '\
              CreateObject \
              SetObjectIntTitle \
              CreatePropertyTypeValidity \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Fix consistency for property sheet properties
    sequence_string = '\
              CreateObject \
              SetObjectBadTypedProperty \
              CreatePropertyTypeValidity \
              CallFixConsistency \
              CheckIfConstraintFailed \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Fix consistency for local properties.
    # By default, when calling 'edit' with keys not defined in property
    # sheet, a local property is added on the object and this property
    # has 'string' type. This sequence depends on this behaviour.
    sequence_string = '\
              CreateObject \
              SetObjectIntLocalProperty \
              CreatePropertyTypeValidity \
              CallFixConsistency \
              CheckIfConstraintFailed \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCreateAttributeEquality0(self, sequence=None,
                                  sequence_list=None, **kw):
    """
      Create a AttributeEquality Constraint
    """
    self._createGenericConstraint(sequence,
                                  klass_name='AttributeEquality',
                                  id='attribute_equality',
                                  description='AttributeEquality test')

  def stepCreateAttributeEquality1(self, sequence=None,
                                  sequence_list=None, **kw):
    """
      Create a AttributeEquality Constraint
    """
    self._createGenericConstraint(sequence,
                                  klass_name='AttributeEquality',
                                  id='attribute_equality',
                                  description='AttributeEquality test',
                                  title=self.object_title)

  def test_04_AttributeEquality(self):
    """
      Test attribute equality
    """
    sequence_list = SequenceList()
    # Test Constraint without any configuration
    sequence_string = '\
              CreateObject \
              CreateAttributeEquality0 \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property defined on object
    # With None value
    sequence_string = '\
              CreateObject \
              SetObjectNoneTitle \
              CreateAttributeEquality1 \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property defined on object
    # With '' value
    sequence_string = '\
              CreateObject \
              SetObjectEmptyTitle \
              CreateAttributeEquality1 \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property defined on object
    sequence_string = '\
              CreateObject \
              SetObjectTitle \
              CreateAttributeEquality1 \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCreateCategoryExistence0(self, sequence=None,
                                  sequence_list=None, **kw):
    """
      Create a PropertyExistence Constraint
    """
    self._createGenericConstraint(sequence,
                                  klass_name='CategoryExistence',
                                  id='category_existence',
                                  description='CategoryExistence test')

  def stepCreateCategoryExistence1(self, sequence=None,
                                   sequence_list=None, **kw):
    """
      Create a PropertyExistence Constraint
    """
    self._createGenericConstraint(sequence,
                                  klass_name='CategoryExistence',
                                  id='category_existence',
                                  description='CategoryExistence test',
                                  unknown_base_category=None)

  def stepCreateCategoryExistence2(self, sequence=None,
                                   sequence_list=None, **kw):
    """
      Create a PropertyExistence Constraint
    """
    self._createGenericConstraint(sequence,
                                  klass_name='CategoryExistence',
                                  id='category_existence',
                                  description='CategoryExistence test',
                                  group=None)

  def stepCreateCategoryExistence3(self, sequence=None,
                                   sequence_list=None, **kw):
    """
      Create a PropertyExistence Constraint with portal_type
    """
    self._createGenericConstraint(sequence,
                                  klass_name='CategoryExistence',
                                  id='category_existence',
                                  description='CategoryExistence test',
                                  group=None,
                                  portal_type = ('Organisation', ))

  def test_05_CategoryExistence(self):
    """
      Test category existence
    """
    sequence_list = SequenceList()
    # Test Constraint without any configuration
    sequence_string = '\
              CreateObject \
              CreateCategoryExistence0 \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property not defined in PropertySheet
    sequence_string = '\
              CreateObject \
              CreateCategoryExistence1 \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property not defined on object
    sequence_string = '\
              CreateObject \
              CreateCategoryExistence2 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property defined on object
    sequence_string = '\
              CreateObject \
              SetObjectGroup \
              CreateCategoryExistence2 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property not defined on object
    sequence_string = '\
              CreateObject \
              CreateCategoryExistence3 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property defined on object, but wrong portal type
    sequence_string = '\
              CreateObject \
              SetObjectGroup \
              CreateCategoryExistence3 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property defined on object
    sequence_string = '\
              CreateObject \
              SetObjectGroupOrganisation \
              CreateCategoryExistence3 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCreateCategoryMembershipArity0(self, sequence=None,
                                         sequence_list=None, **kw):
    """
      Create a CategoryMembershipArity Constraint
    """
    self._createGenericConstraint(sequence,
                                  klass_name='CategoryMembershipArity',
                                  id='CategoryMembershipArity',
                                  description='CategoryMembershipArity test',
                                  min_arity=0,
                                  max_arity=0,
                                  portal_type=('Category', ),
                                  base_category=('group', ))

  def stepCreateCategoryMembershipArity1(self, sequence=None,
                                         sequence_list=None, **kw):
    """
      Create a CategoryMembershipArity Constraint
    """
    self._createGenericConstraint(sequence,
                                  klass_name='CategoryMembershipArity',
                                  id='CategoryMembershipArity',
                                  description='CategoryMembershipArity test',
                                  min_arity=1,
                                  max_arity=1,
                                  portal_type=('Category', ),
                                  base_category=('group', ))

  def stepCreateCategoryMembershipArity2(self, sequence=None,
                                         sequence_list=None, **kw):
    """
      Create a CategoryMembershipArity Constraint
    """
    self._createGenericConstraint(sequence,
                                  klass_name='CategoryMembershipArity',
                                  id='CategoryMembershipArity',
                                  description='CategoryMembershipArity test',
                                  min_arity=2,
                                  max_arity=2,
                                  portal_type=('Category', ),
                                  base_category=('group', ))

  def stepCreateCategoryMembershipArity3(self, sequence=None,
                                         sequence_list=None, **kw):
    """
      Create a CategoryMembershipArity Constraint
    """
    self._createGenericConstraint(sequence,
                                  klass_name='CategoryMembershipArity',
                                  id='CategoryMembershipArity',
                                  description='CategoryMembershipArity test',
                                  min_arity=0,
                                  max_arity=1,
                                  portal_type=('Category', ),
                                  base_category=('group', ))

  def stepCreateCategoryMembershipArity4(self, sequence=None,
                                         sequence_list=None, **kw):
    """
      Create a CategoryMembershipArity Constraint
    """
    self._createGenericConstraint(sequence,
                                  klass_name='CategoryMembershipArity',
                                  id='CategoryMembershipArity',
                                  description='CategoryMembershipArity test',
                                  min_arity=1,
                                  max_arity=2,
                                  portal_type=('Category', ),
                                  base_category=('group', ))

  def test_06_CategoryMembershipArity(self):
    """
      Test category existence
    """
    sequence_list = SequenceList()
    # Test Constraint with min=0, max=0
    sequence_string = '\
              CreateObject \
              CreateCategoryMembershipArity0 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=0, max=0
    sequence_string = '\
              CreateObject \
              SetObjectGroup \
              CreateCategoryMembershipArity0 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=0, max=0
    sequence_string = '\
              CreateObject \
              SetObjectGroupList \
              CreateCategoryMembershipArity0 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=1, max=1
    sequence_string = '\
              CreateObject \
              CreateCategoryMembershipArity1 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=1, max=1
    sequence_string = '\
              CreateObject \
              SetObjectGroup \
              CreateCategoryMembershipArity1 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=1, max=1
    sequence_string = '\
              CreateObject \
              SetObjectGroupList \
              CreateCategoryMembershipArity1 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=2, max=2
    sequence_string = '\
              CreateObject \
              CreateCategoryMembershipArity2 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=2, max=2
    sequence_string = '\
              CreateObject \
              SetObjectGroup \
              CreateCategoryMembershipArity2 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=2, max=2
    sequence_string = '\
              CreateObject \
              SetObjectGroupList \
              CreateCategoryMembershipArity2 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=0, max=1
    sequence_string = '\
              CreateObject \
              CreateCategoryMembershipArity3 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=0, max=1
    sequence_string = '\
              CreateObject \
              SetObjectGroup \
              CreateCategoryMembershipArity3 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=0, max=1
    sequence_string = '\
              CreateObject \
              SetObjectGroupList \
              CreateCategoryMembershipArity3 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=1, max=2
    sequence_string = '\
              CreateObject \
              CreateCategoryMembershipArity4 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=1, max=2
    sequence_string = '\
              CreateObject \
              SetObjectGroup \
              CreateCategoryMembershipArity4 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=1, max=2
    sequence_string = '\
              CreateObject \
              SetObjectGroupList \
              CreateCategoryMembershipArity4 \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_CategoryMembershipArityNoMax(self):
    obj = self._makeOne()
    constraint = self._createGenericConstraint(
                   id='dummy_constraint',
                   portal_type=('Category',),
                   base_category=('group',),
                   klass_name='CategoryMembershipArity',
                   min_arity=1)
    message_list = constraint.checkConsistency(obj)
    self.assertEqual(1, len(message_list))
    self.assertNotEqual('', message_list[0].getTranslatedMessage())
    obj.setGroup('testGroup1')
    self.assertEqual(0, len(constraint.checkConsistency(obj)))

  def test_CategoryAcquiredMembershipArityNoMax(self):
    obj = self._makeOne()
    constraint = self._createGenericConstraint(
                   id='dummy_constraint',
                   portal_type=('Category',),
                   base_category=('group',),
                   klass_name='CategoryAcquiredMembershipArity',
                   min_arity=1)
    message_list = constraint.checkConsistency(obj)
    self.assertEqual(1, len(message_list))
    self.assertNotEqual('', message_list[0].getTranslatedMessage())
    obj.setGroup('testGroup1')
    self.assertEqual(0, len(constraint.checkConsistency(obj)))

  def stepCreateCategoryRelatedMembershipArity0(self, sequence=None,
                                                sequence_list=None, **kw):
    """
      Create a CategoryMembershipArity Constraint
    """
    self._createGenericConstraint(
                            sequence,
                            klass_name='CategoryRelatedMembershipArity',
                            id='CategoryRelatedMembershipArity',
                            description='CategoryRelatedMembershipArity test',
                            min_arity=0,
                            max_arity=0,
                            portal_type=('Organisation', ),
                            base_category=('group', ))

  def stepCreateCategoryRelatedMembershipArity1(self, sequence=None,
                                                sequence_list=None, **kw):
    """
      Create a CategoryMembershipArity Constraint
    """
    self._createGenericConstraint(
                            sequence,
                            klass_name='CategoryRelatedMembershipArity',
                            id='CategoryRelatedMembershipArity',
                            description='CategoryRelatedMembershipArity test',
                            min_arity=1,
                            max_arity=1,
                            portal_type=('Organisation', ),
                            base_category=('group', ))

  def stepCreateCategoryRelatedMembershipArity2(self, sequence=None,
                                                sequence_list=None, **kw):
    """
      Create a CategoryMembershipArity Constraint
    """
    self._createGenericConstraint(
                            sequence,
                            klass_name='CategoryRelatedMembershipArity',
                            id='CategoryRelatedMembershipArity',
                            description='CategoryRelatedMembershipArity test',
                            min_arity=2,
                            max_arity=2,
                            portal_type=('Organisation', ),
                            base_category=('group', ))

  def test_07_CategoryRelatedMembershipArity(self):
    """
      Test related category existence
    """
    sequence_list = SequenceList()
    # Test Constraint with min=0, max=0
    sequence_string = '\
              DeleteObjectModuleContent \
              CreateObject \
              CreateCategoryRelatedMembershipArity0 \
              Tic \
              CallRelatedCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=0, max=0
    sequence_string = '\
              DeleteObjectModuleContent \
              CreateObject \
              SetObjectGroup \
              CreateCategoryRelatedMembershipArity0 \
              Tic \
              CallRelatedCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=1, max=1
    sequence_string = '\
              DeleteObjectModuleContent \
              CreateObject \
              CreateCategoryRelatedMembershipArity1 \
              Tic \
              CallRelatedCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=1, max=1
    sequence_string = '\
              DeleteObjectModuleContent \
              CreateObject \
              SetObjectGroup \
              CreateCategoryRelatedMembershipArity1 \
              Tic \
              CallRelatedCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=2, max=2
    sequence_string = '\
              DeleteObjectModuleContent \
              CreateObject \
              CreateCategoryRelatedMembershipArity2 \
              Tic \
              CallRelatedCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with min=2, max=2
    sequence_string = '\
              DeleteObjectModuleContent \
              CreateObject \
              SetObjectGroup \
              CreateCategoryRelatedMembershipArity2 \
              Tic \
              CallRelatedCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_RelatedCategoryMembershipArityNoMax(self):
    related_obj = self._makeOne()
    obj = self.portal.portal_categories.group.testGroup1
    constraint = self._createGenericConstraint(
                   id='dummy_constraint',
                   portal_type=('Organisation',),
                   base_category=('group',),
                   klass_name='CategoryRelatedMembershipArity',
                   min_arity=1)
    message_list = constraint.checkConsistency(obj)
    self.assertEqual(1, len(message_list))
    self.assertNotEqual('', message_list[0].getTranslatedMessage())
    related_obj.setGroupValue(obj)
    self.tic()
    self.assertEqual(0, len(constraint.checkConsistency(obj)))

  def test_BooleanPropertiesPropertyTypeValidity(self):
    """Tests PropertyTypeValidity can handle boolean values.
    """
    obj = self._makeOne()
    obj.manage_addProperty('dummy_boolean_property', True, type='boolean')
    self.assertEqual([], obj.checkConsistency())

  def test_BooleanPropertiesPropertyTypeValidityFix(self):
    """Tests PropertyTypeValidity can fix boolean values.
    """
    obj = self._makeOne()
    prop_name = 'dummy_boolean_property'
    obj.manage_addProperty(prop_name, True, type='boolean')
    obj.setProperty(prop_name, 2)
    obj.fixConsistency()
    # should be fixed now
    self.assertEqual([], obj.checkConsistency())
    self.assertTrue(obj.getPropertyType(prop_name))

  def test_TALESConstraint(self):
    """Tests TALESConstraint
    """
    constraint = self._createGenericConstraint(
                   klass_name='TALESConstraint',
                   id='tales_constraint',
                   expression='python: object.getTitle() != "foo"')
    obj = self._makeOne()
    self.assertEqual([], constraint.checkConsistency(obj))
    obj.setTitle('foo')
    message_list = constraint.checkConsistency(obj)
    self.assertEqual(1, len(message_list))
    self.assertNotEqual('', message_list[0].getTranslatedMessage())

  def test_TALESConstraintInvalidExpression(self):
    """Tests TALESConstraint with an invalid expression
    """
    constraint = self._createGenericConstraint(
                   klass_name='TALESConstraint',
                   id='tales_constraint',
                   expression='python: None / 3') # ValueError
    obj = self._makeOne()
    # an error during expression evaluation simply makes a consistency error
    message_list = constraint.checkConsistency(obj)
    self.assertEqual(1, len(message_list))
    self.assertNotEqual('', message_list[0].getTranslatedMessage())

    # an error during expression compilation is reraised to the programmer
    constraint = self._createGenericConstraint(
                   klass_name='TALESConstraint',
                   id='tales_constraint',
                   expression='python: None (" ')
    from Products.PageTemplates.Expressions import getEngine
    CompilerError = getEngine().getCompilerError()
    self.assertRaises(CompilerError, constraint.checkConsistency, obj)

    constraint = self._createGenericConstraint(
                   klass_name='TALESConstraint',
                   id='tales_constraint',
                   expression='error: " ')
    self.assertRaises(CompilerError, constraint.checkConsistency, obj)

  def test_PropertyTypeValidityFixLocalPropertiesIgnoresNoLocal(self):
    """Tests PropertyTypeValidity can repairs local property when this property
    is added on the class later, and this property is already in the good type.
    """
    constraint = self._createGenericConstraint(
                   klass_name='PropertyTypeValidity',
                   id='type_validity_constraint', )
    obj = self._makeOne()
    self._addProperty(obj.getPortalType(), "FixLocalPropertiesString",
                      portal_type="Standard Property",
                      property_id="local_property",
                      elementary_type="string")
    obj.edit(local_property='1')
    self.assertNotIn('_local_properties', obj.__dict__)
    self.assertEqual([], constraint.checkConsistency(obj))
    self.assertEqual([], constraint.fixConsistency(obj))
    self.assertNotIn('_local_properties', obj.__dict__)
    self.assertEqual('1', obj.getLocalProperty())
    obj.edit(local_property='something else')
    self.assertEqual('something else', obj.getLocalProperty())

  def test_PropertyTypeValidityFixLocalPropertiesString(self):
    """Tests PropertyTypeValidity can repairs local property when this property
    is added on the class later, and this property is already in the good type.
    """
    constraint = self._createGenericConstraint(
                   klass_name='PropertyTypeValidity',
                   id='type_validity_constraint', )
    obj = self._makeOne()
    obj.edit(local_property='1')
    self.assertEqual(1, len(obj._local_properties))
    self.assertEqual([], constraint.checkConsistency(obj))
    # now add a 'local_property' property defined on a property sheet
    self._addProperty(obj.getPortalType(), "FixLocalPropertiesString",
                      portal_type="Standard Property",
                      property_id="local_property",
                      elementary_type="string")
    self.assertEqual(['Property local_property was migrated from local properties.'],
      [str(q.getMessage()) for q in constraint.fixConsistency(obj)])
    self.assertEqual((), obj._local_properties)
    self.assertEqual('1', obj.getLocalProperty())
    obj.edit(local_property='something else')
    self.assertEqual('something else', obj.getLocalProperty())

  def test_PropertyTypeValidityFixLocalPropertiesFloat(self):
    """Tests PropertyTypeValidity can repairs local property when this property
    is added on the class later, and this property type changed.
    """
    constraint = self._createGenericConstraint(
                   klass_name='PropertyTypeValidity',
                   id='type_validity_constraint', )
    obj = self._makeOne()
    obj.edit(local_property=1.234)
    self.assertEqual(1, len(obj._local_properties))
    #self.assertEqual([], constraint.checkConsistency(obj))
    # now add a 'local_property' property defined on a property sheet
    self._addProperty(obj.getPortalType(), "FixLocalPropertiesFloat",
                      portal_type="Standard Property",
                      property_id="local_property",
                      elementary_type="float")
    self.assertEqual(['Property local_property was migrated from local properties.'],
      [str(q.getMessage()) for q in constraint.fixConsistency(obj)])
    self.assertEqual((), obj._local_properties)
    self.assertEqual(1.234, obj.getLocalProperty())
    obj.edit(local_property=3)
    self.assertEqual(3., obj.getLocalProperty())

  def test_PropertyTypeValidityFixLocalPropertiesContent(self):
    """Tests PropertyTypeValidity can repairs local property of type content
    when this property is added on the class later.
    """
    constraint = self._createGenericConstraint(
                   klass_name='PropertyTypeValidity',
                   id='type_validity_constraint', )
    obj = self._makeOne()
    obj.edit(default_organisation_title='foo')
    self.assertEqual(1, len(obj._local_properties))
    self.assertEqual([], constraint.checkConsistency(obj))
    # now add a 'local_property' property defined on a property sheet
    self._addProperty(obj.getPortalType(), "FixLocalPropertiesContent",
                      portal_type="Acquired Property",
                      commit=False,
                      property_id="organisation",
                      storage_id="default_organisation",
                      elementary_type="content",
                      content_portal_type="python: ('Organisation', )",
                      content_acquired_property_id= ('title',))
    # this property suppose that we can add some Organisation inside
    # Organisation, so we temporary patch the type information.
    ti = self.getTypesTool().getTypeInfo(obj)
    allowed_types = ti.getTypeAllowedContentTypeList()
    ti._setTypeAllowedContentTypeList(allowed_types + ['Organisation'])
    self.commit()
    try:
      self.assertEqual(sorted([
        'Property default_organisation_title was migrated from local properties.']),
        sorted([str(q.getMessage()) for q in constraint.fixConsistency(obj)]))
      self.assertEqual('foo', obj.getDefaultOrganisationTitle())
      self.assertEqual('foo', obj.default_organisation.getTitle())
      self.assertEqual(0, len(obj._local_properties))
    finally:
      ti._setTypeAllowedContentTypeList(allowed_types)

  def test_PropertyTypeValidityFixLocalPropertiesForCategories(self):
    """Tests PropertyTypeValidity can repairs categories when this property
    is added on the class later.
    """
    self.portal.portal_categories.newContent(
                              portal_type='Base Category',
                              id='testing_category')
    constraint = self._createGenericConstraint(
                   klass_name='PropertyTypeValidity',
                   id='type_validity_constraint', )
    obj = self._makeOne()
    obj.edit(testing_category=obj.getRelativeUrl())
    self.assertEqual(1, len(obj._local_properties))
    self.assertEqual([], constraint.checkConsistency(obj))
    # now add a 'local_property' property defined on a property sheet
    self._addProperty(obj.getPortalType(), "FixForCategories",
                      portal_type="Category Property",
                      property_id="testing_category")
    # fix consistency
    self.assertEqual(sorted([
      'Property testing_category was migrated from local properties.']),
      sorted([str(q.getMessage()) for q in constraint.fixConsistency(obj)]))
    # now we can use testing_category as any category accessor
    self.assertEqual(0, len(obj._local_properties))
    self.assertEqual(obj, obj.getTestingCategoryValue())

  def stepCreateContentExistence(self, sequence=None, sequence_list=None, **kw):
    """
      Create a Content Existence Constraint
    """
    self._createGenericConstraint(
                            sequence,
                            klass_name='ContentExistence',
                            id='ContentExistence',
                            description='ContentExistence test',
                            portal_type=(self.object_content_portal_type, )
                            )

  def stepCreateContentObject(self, sequence=None, sequence_list=None, **kw):
    """
      Create a Content Object inside one Object
    """
    document = sequence.get('document')
    content_object = document.newContent(portal_type=self.object_content_portal_type)
    sequence.edit(
        content_object = content_object,
    )

  def test_ContentExistenceConstraint(self):
    """
      Tests Content Existence
    """
    sequence_list = SequenceList()
    # Test Constraint without any content
    sequence_string = '\
              CreateObject \
              CreateContentExistence \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with content
    sequence_string = '\
              CreateObject \
              CreateContentExistence \
              CreateContentObject \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCreateStringAttributeMatch(self, sequence=None, sequence_list=None, **kw):
    """
      Create a String Atribute Match Constraint
    """
    self._createGenericConstraint(
                            sequence,
                            klass_name='StringAttributeMatch',
                            id='StringAttributeMatch',
                            description='StringAttributeMatch test',
                            title='^[^ ]'
                            )

  def stepSetObjectTitle0(self, sequence=None, sequence_list=None, **kw):
    """
      Set valid Title to Object
    """
    document = sequence.get('document')
    document.setTitle(self.object_title)
    sequence.edit(
        document = document,
    )

  def stepSetObjectTitle1(self, sequence=None, sequence_list=None, **kw):
    """
      Set empty (or invalid string) to Object
    """
    document = sequence.get('document')
    document.setTitle(' ')
    sequence.edit(
        document = document,
    )

  def test_StringAttributeMatchConstraint(self):
    """
      Tests string attribute match
    """
    sequence_list = SequenceList()
    # Test Constraint with empty Title
    sequence_string = '\
              CreateObject \
              CreateStringAttributeMatch \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with Title
    sequence_string = '\
              CreateObject \
              CreateStringAttributeMatch \
              SetObjectTitle0 \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with invalid Title
    # Not match with regex
    sequence_string = '\
              CreateObject \
              CreateStringAttributeMatch \
              SetObjectTitle1 \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def test_RegisterWithPropertySheet(self):
    # constraint are registred in property sheets
    obj = self._makeOne()
    obj.setTitle('b')
    self._addProperty(
                        obj.getPortalType(),
                        "TestRegisterWithPropertySheet",
                        commit=True,
                        property_id="title_constraint",
                        portal_type='Attribute Equality Constraint',
                        constraint_attribute_name = 'title',
                        constraint_attribute_value = 'string:a',
    )

    consistency_message_list = obj.checkConsistency()
    self.assertEqual(1, len(consistency_message_list))
    message = consistency_message_list[0]
    from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage
    self.assertTrue(isinstance(message, ConsistencyMessage))
    self.assertEqual(message.class_name, 'Attribute Equality Constraint')
    obj.setTitle('a')
    self.assertEqual(obj.checkConsistency(), [])

  def test_OverrideMessage(self):
    # messages can be overriden in property sheet
    obj = self._makeOne()
    obj.setTitle('b')
    self._addProperty(
                        obj.getPortalType(),
                        "TestOverrideMessage",
                        commit=True,
                        property_id="title_constraint",
                        portal_type='Attribute Equality Constraint',
                        constraint_attribute_name = 'title',
                        constraint_attribute_value = 'string:a',
                        message_invalid_attribute_value='Attribute ${attribute_name} does not match',

    )
    consistency_message_list = obj.checkConsistency()
    self.assertEqual(1, len(consistency_message_list))
    message = consistency_message_list[0]
    self.assertEqual('Attribute title does not match',
                  str(message.getTranslatedMessage()))

  def test_PropertyTypeValidityWithUnauthorizedCategory(self):
    person = self.portal.person_module.newContent(portal_type='Person')
    assignment = person.newContent(portal_type='Assignment')
    # add a source_title property on Assignment.
    self._addProperty('Assignment', "UnauthorizedCategory",
                      commit=False,
                      portal_type="Acquired Property",
                      property_id="source_title",
                      elementary_type="string",
                      acquisition_base_category=('source',),
                      acquisition_portal_type="python: ('Category',)",
                      acquisition_accessor_id="getTitle")
    self._addProperty('Assignment', "UnauthorizedCategory",
                      portal_type="Property Type Validity Constraint",
                      property_id="type_check")
    self.assertEqual([], person.checkConsistency())
    group3 = self.category_tool.restrictedTraverse(
      'group/testGroup3', self.category_tool.group.newContent(
      portal_type='Category',
      id='testGroup3'))
    group3.manage_permission('Access contents information', ['Manager'], 0)
    assignment.setSourceValue(group3)
    # modify title attribute directly to violate PropertyTypeValidity
    # constraint.
    group3.title=123
    # Manager can access testGroup3, so full information is included in
    # the error message.
    error_list = person.checkConsistency()
    self.assertEqual(1, len(error_list))
    expected_message = "Attribute source_title should be of type string but is of type <class 'int'>"
    if six.PY2:
      expected_message = "Attribute source_title should be of type string but is of type <type 'int'>"
    self.assertEqual(str(error_list[0].getMessage()), expected_message)
    self.stepLoginAsAssignee()
    # Assignee cannot access testGroup3, so full information is not
    # included in the error message.
    error_list = person.checkConsistency()
    self.assertEqual(1, len(error_list))
    self.assertEqual(str(error_list[0].getMessage()), 'There is something wrong.')

  def test_PropertyTypeValidityForMultivaluedProperty(self):
    """
      This test allows to check that a multivalued property which defines a
      type is composed of a list of elements of this type.
    """
    constraint = self._createGenericConstraint(
                   klass_name='PropertyTypeValidity',
                   id='multi_valuated_property', )
    obj = self._makeOne()
    self._addProperty(obj.getPortalType(), "ForMultivalued",
                      property_id="multi_valuated_property",
                      portal_type="Standard Property",
                      elementary_type="float",
                      multivalued=1)
    obj.edit(multi_valuated_property=[1.0, 2.0, 3.0, ])
    self.assertEqual([], constraint.checkConsistency(obj))

  def stepValidateObject(self, sequence=None, sequence_list=None, **kw):
    """
    """
    document = sequence.get('document')
    document.validate()

  def stepInvalidateObject(self, sequence=None, sequence_list=None, **kw):
    """
    """
    document = sequence.get('document')
    document.invalidate()

  def stepCreateAttributeUnicityConstraint(self, sequence=None,
                           sequence_list=None, **kw):
    """
      Create a default Constraint
    """
    constraint = self._createGenericConstraint(sequence,
                                  klass_name='AttributeUnicity',
                                  id='title_unicity_constraint',
                                  description='AttributeUnicity test',
                                  title="python: {'portal_type': object.getPortalType(),"\
                                  "'validation_state': 'validated', 'title': object.getTitle()}",
                                  condition="object/getTitle")
    sequence.set('constraint', constraint)

  def test_08_AttributeUnicity(self):
    """
      Test attribute unicity
    """
    sequence_list = SequenceList()
    # Test Constraint without unicity on title
    sequence_string = '\
              CreateObject \
              ValidateObject \
              SetObjectTitle \
              Tic \
              CreateAttributeUnicityConstraint \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '

    # invalidate object without Tic If zodb and catalog are not synchronized,
    # The constraint should still working
    sequence_string += '\
              InvalidateObject \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              Tic \
              ValidateObject \
              Tic \
              '

     # Test Constraint with Two object with same title
    sequence_string += '\
              CreateObject \
              SetObjectTitle \
              Tic \
              CallCheckConsistency \
              CheckIfConstraintFailed \
              '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def createConstraintThatMustBeCalledOnce(self):
    """
      Create a default allowing the check if they are called once
    """
    property_sheet = self.portal.portal_property_sheets.newContent(
                        id="TestConstraint", title="Test Constraint")
    property_sheet.newContent(portal_type="TALES Constraint",
                   id="check_title_constraint",
                   expression="python: object.setTitle(object.getTitle() + 'a')")
    portal_type = self.portal.portal_types[self.object_portal_type]
    if "TestConstraint" not in portal_type.getTypePropertySheetList():
      portal_type.setTypePropertySheetList(
       portal_type.getTypePropertySheetList() + ["TestConstraint"])

  # Expected failure until checkConsistency is reviewed to not execute
  # twice constraints
  @expectedFailure
  def test_09_CheckConstraintAreCalledOnce(self):
    """
    Make sure we call only one time a constraint in a particular object
    """
    self.createConstraintThatMustBeCalledOnce()
    document = self.stepCreateObject()
    document.setTitle("Foo")
    document.checkConsistency()
    self.assertEqual("Fooa", document.getTitle())

  def test_checkConsistency_is_recursive(self):
    self._addProperty(
        self.object_content_portal_type,
        self.id(),
        commit=True,
        property_id="title_constraint",
        portal_type='Attribute Equality Constraint',
        constraint_attribute_name = 'title',
        constraint_attribute_value = 'string:a',
    )

    obj = self._makeOne()
    self.assertEqual([], obj.checkConsistency())
    self.assertEqual([], obj.fixConsistency())

    obj.newContent(portal_type=self.object_content_portal_type)
    self.assertEqual(1, len(obj.checkConsistency()))
    self.assertEqual(1, len(obj.fixConsistency()))

    # non ERP5 objects are ignored
    from OFS.Image import manage_addFile
    manage_addFile(obj, self.id(),)
    self.assertEqual(1, len(obj.checkConsistency()))
    self.assertEqual(1, len(obj.fixConsistency()))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestConstraint))
  return suite
