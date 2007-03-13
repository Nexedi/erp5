##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Products.ERP5Type.tests.testERP5Type import PropertySheetTestCase
from AccessControl.SecurityManagement import newSecurityManager, \
                                             noSecurityManager
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList

class TestConstraint(PropertySheetTestCase):

  run_all_test = 1
  quiet = 1

  object_portal_type = "Organisation"
  object_content_portal_type = "Address"
  object_title = "Title test"

  def getTitle(self):
    return "Constraint"

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base',)

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('rc', '', ['Manager'], [])
    user = uf.getUserById('rc').__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self, quiet=1, run=run_all_test):
    self.login()
    self.portal = self.getPortal()
    self.category_tool = self.getCategoryTool()
    self.createCategories()

  def stepTic(self,**kw):
    self.tic()

  def createCategories(self):
    """ 
      Light install create only base categories, so we create 
      some categories for testing them
    """
    category_list = ['testGroup1', 'testGroup2']
    if len(self.category_tool.group.contentValues()) == 0 :
      for category_id in category_list:
        o = self.category_tool.group.newContent(portal_type='Category',
                                                id=category_id)

  def stepDeleteObjectModuleContent(self, sequence=None, 
                                    sequence_list=None, **kw):
    """
      Delete all objects in the module.
    """
    portal = self.getPortal()
    module = portal.getDefaultModule(self.object_portal_type)
    module.manage_delObjects(module.contentIds())

  def _makeOne(self):
    """Creates an object and reindex it
    """
    module = self.portal.getDefaultModule(self.object_portal_type)
    obj = module.newContent(portal_type=self.object_portal_type)
    get_transaction().commit()
    self.tic()
    return obj

  def stepCreateObject(self, sequence=None, sequence_list=None, **kw):
    """
      Create a object which will be tested.
    """
    portal = self.getPortal()
    module = portal.getDefaultModule(self.object_portal_type)
    object = module.newContent(portal_type=self.object_portal_type)
    group1 = object.portal_categories.restrictedTraverse('group/testGroup1')
    sequence.edit(
        object=object,
        group=group1,
    )

  def stepSetObjectGroup(self, sequence=None, 
                         sequence_list=None, **kw):
    """
      Set a group to object
    """
    object = sequence.get('object')
#     group1 = object.portal_categories.restrictedTraverse('group/testGroup1')
#     object.edit(group_value=group1)
    object.edit(group='testGroup1')
    self.assertNotEquals(
          object.getGroup(portal_type=()),
          None )
    
  def stepSetObjectGroupOrganisation(self, sequence=None,
                         sequence_list=None, **kw):
    """
      Set a group to object, forcing portal_type color to Organisation
    """
    object = sequence.get('object')
    object.setGroup(object.getRelativeUrl(),
                    portal_type='Organisation')
    self.assertNotEquals(
          object.getGroup(portal_type='Organisation'),
          None )
    
  def stepSetObjectGroupList(self, sequence=None,
                             sequence_list=None, **kw):
    """
      Set a group to object
    """
    object = sequence.get('object')
#     group1 = object.portal_categories.restrictedTraverse('group/testGroup1')
#     group2 = object.portal_categories.restrictedTraverse('group/testGroup2')
#     object.edit(group_value_list=[group1, group2])
    object.edit(group_list=['testGroup1', 'testGroup2'])

  def stepSetObjectTitle(self, sequence=None, 
                         sequence_list=None, **kw):
    """
      Set a different title value
    """
    object = sequence.get('object')
    object_title = self.object_title
    object.setTitle(object_title)

  def stepSetObjectNoneTitle(self, sequence=None, 
                             sequence_list=None, **kw):
    """
      Set a different title value
    """
    object = sequence.get('object')
    # Do not call edit, as we want to explicitely modify the property
    # (and edit modify only if value is different)
    object.setTitle(None)

  def stepSetObjectEmptyTitle(self, sequence=None,
                              sequence_list=None, **kw):
    """
      Set a different title value
    """
    object = sequence.get('object')
    # Do not call edit, as we want to explicitely modify the property
    # (and edit modify only if value is different)
    method = object.setTitle('')

  def stepSetObjectIntTitle(self, sequence=None,
                            sequence_list=None, **kw):
    """
      Set a different title value
    """
    object = sequence.get('object')
    object_title = self.object_title
    object.edit(title=12345)
  
  def stepSetObjectBadTypedProperty(self, sequence=None,
                            sequence_list=None, **kw):
    """
      Set a property with a bad type
    """
    object = sequence.get('object')
    property_name = 'ean13code'
    # make sure the property is defined on the object
    self.failUnless(not object.hasProperty(property_name))
    self.failUnless(object.getPropertyType(property_name) != 'int')
    object.setProperty(property_name, 12)
  
  def stepSetObjectIntLocalProperty(self, sequence=None,
                            sequence_list=None, **kw):
    """
      Set a local property on the object, with an int type.
    """
    object = sequence.get('object')
    object.edit(local_prop = 12345)

  def _createGenericConstraint(self, sequence, klass_name='Constraint',
                               **kw):
    """
      Create a Constraint
    """
    from Products.ERP5Type import Constraint
    module = Constraint
    file_path = "%s.%s" % (module.__name__, klass_name)
    __import__(file_path)
    file = getattr(module, klass_name)
    klass = file
#     klass = getattr(file, klass_name)
    constraint = klass(**kw)
    sequence.edit(
        constraint=constraint,
    )
    return constraint

  def stepCallCheckConsistency(self, sequence=None, 
                               sequence_list=None, **kw):
    """
      Call checkConsistency of a Constraint.
    """
    object = sequence.get('object')
    constraint = sequence.get('constraint')
    # Check
    error_list = constraint.checkConsistency(object)
    sequence.edit(
        error_list=error_list
    )
  
  def stepCallFixConsistency(self, sequence=None,
                                      sequence_list=None, **kw):
    """
      Call checkConsistency of a Constraint, fixing the errors.
    """
    object = sequence.get('object')
    constraint = sequence.get('constraint')
    # Check
    error_list = constraint.checkConsistency(object, fixit=1)
    sequence.edit(
        error_list=error_list
    )

  def stepCallRelatedCheckConsistency(self, sequence=None, 
                                      sequence_list=None, **kw):
    """
    Call checkConsistency of a Constraint.
    """
    object = sequence.get('group')
    constraint = sequence.get('constraint')
    # Check
    error_list = constraint.checkConsistency(object)
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
    self.failUnless(error_list != [],
                    "error_list : %s" % error_list)

  def stepCreateConstraint(self, sequence=None, 
                           sequence_list=None, **kw):
    """
      Create a default Constraint
    """
    self._createGenericConstraint(sequence, 
                                  klass_name='Constraint',
                                  id='default_constraint',
                                  description='constraint test')

  def test_01_Constraint(self, quiet=quiet, run=run_all_test):
    """
      Test default Constraint class
    """
    if not run: return
    sequence_list = SequenceList()
    # Test Constraint without any configuration
    sequence_string = '\
              CreateObject \
              CreateConstraint \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

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

  def test_02_PropertyExistence(self, quiet=quiet, run=run_all_test):
    """
      Test property existence
    """
    if not run: return
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
    # and so, is considered as a data
    sequence_string = '\
              CreateObject \
              SetObjectNoneTitle \
              CreatePropertyExistence2 \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test Constraint with property defined on object
    # With '' value
    # As disapointing as it could be, empty string is a data,
    # and test must succeed
    sequence_string = '\
              CreateObject \
              SetObjectEmptyTitle \
              CreatePropertyExistence2 \
              CallCheckConsistency \
              CheckIfConstraintSucceeded \
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
    sequence_list.play(self, quiet=quiet)

  def stepCreatePropertyTypeValidity(self, sequence=None, 
                                     sequence_list=None, **kw):
    """
      Create a PropertyExistence Constraint
    """
    self._createGenericConstraint(sequence, 
                                  klass_name='PropertyTypeValidity',
                                  id='property_type_validity',
                                  description='propertyTypeValidity test')

  def test_03_PropertyTypeValidity(self, quiet=quiet, run=run_all_test):
    """
      Test property type validity
    """
    if not run: return
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
    sequence_list.play(self, quiet=quiet)

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

  def test_04_AttributeEquality(self, quiet=quiet, run=run_all_test):
    """
      Test attribute equality
    """
    if not run: return
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
    sequence_list.play(self, quiet=quiet)

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

  def test_05_CategoryExistence(self, quiet=quiet, run=run_all_test):
    """
      Test category existence
    """
    if not run: return
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
    sequence_list.play(self, quiet=quiet)

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

  def test_06_CategoryMembershipArity(self, quiet=quiet, run=run_all_test):
    """
      Test category existence
    """
    if not run: return
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
    sequence_list.play(self, quiet=quiet)

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

  def test_07_CategoryRelatedMembershipArity(self, quiet=quiet, run=run_all_test):
    """
      Test related category existence
    """
    if not run: return
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
    sequence_list.play(self, quiet=quiet)

  def test_BooleanPropertiesPropertyTypeValidity(self):
    """Tests PropertyTypeValidity can handle boolean values.
    """
    obj = self._makeOne()
    obj.manage_addProperty('dummy_boolean_property', True, type='boolean')
    self.assertEquals([], obj.checkConsistency())
  
  def test_BooleanPropertiesPropertyTypeValidityFix(self):
    """Tests PropertyTypeValidity can fix boolean values.
    """
    obj = self._makeOne()
    prop_name = 'dummy_boolean_property'
    obj.manage_addProperty(prop_name, True, type='boolean')
    obj.setProperty(prop_name, 2)
    obj.fixConsistency()
    # should be fixed now
    self.assertEquals([], obj.checkConsistency())
    self.failUnless(obj.getPropertyType(prop_name))
  
  def test_TALESConstraint(self):
    """Tests TALESConstraint
    """
    constraint = self._createGenericConstraint(Sequence(),
                   klass_name='TALESConstraint',
                   id='tales_constraint',
                   expression='python: object.getTitle() != "foo"')
    obj = self._makeOne()
    self.assertEquals([], constraint.checkConsistency(obj))
    obj.setTitle('foo')
    self.assertEquals(1, len(constraint.checkConsistency(obj)))
    
  def test_TALESConstraintInvalidExpression(self):
    """Tests TALESConstraint with an invalid expression
    """
    constraint = self._createGenericConstraint(Sequence(),
                   klass_name='TALESConstraint',
                   id='tales_constraint',
                   expression='python: None / 3') # ValueError
    obj = self._makeOne()
    # an error during expression evaluation simply makes a consistency error
    self.assertEquals(1, len(constraint.checkConsistency(obj)))

    # an error during expression compilation is reraised to the programmer
    constraint = self._createGenericConstraint(Sequence(),
                   klass_name='TALESConstraint',
                   id='tales_constraint',
                   expression='python: None (" ')
    from Products.PageTemplates.TALES import CompilerError
    self.assertRaises(CompilerError, constraint.checkConsistency, obj)

    constraint = self._createGenericConstraint(Sequence(),
                   klass_name='TALESConstraint',
                   id='tales_constraint',
                   expression='error: " ')
    self.assertRaises(CompilerError, constraint.checkConsistency, obj)
  
  def test_PropertyTypeValidityFixLocalProperties(self):
    """Tests PropertyTypeValidity can repairs local property when this property
    is added on the class later.
    """
    constraint = self._createGenericConstraint(Sequence(),
                   klass_name='PropertyTypeValidity',
                   id='type_validity_constraint', )
    obj = self._makeOne()
    obj.edit(local_property='1')
    self.assertEquals([], constraint.checkConsistency(obj))
    # now add a 'local_property' property defined on a property sheet
    self._addProperty(obj.getPortalType(),
                  '''{'id': 'local_property', 'type': 'int'}''')
    constraint.fixConsistency(obj)
    self.assertEquals(1, obj.getLocalProperty())
    obj.edit(local_property=3)
    self.assertEquals(3, obj.getLocalProperty())
  
  def test_PropertyTypeValidityFixLocalPropertiesContent(self):
    """Tests PropertyTypeValidity can repairs local property of type content
    when this property is added on the class later.
    """
    constraint = self._createGenericConstraint(Sequence(),
                   klass_name='PropertyTypeValidity',
                   id='type_validity_constraint', )
    obj = self._makeOne()
    obj.edit(default_organisation_title='foo')
    self.assertEquals([], constraint.checkConsistency(obj))
    # now add a 'local_property' property defined on a property sheet
    self._addProperty(obj.getPortalType(),
                 ''' { 'id':         'organisation',
                        'storage_id': 'default_organisation',
                        'type':       'content',
                        'portal_type': ('Organisation', ),
                        'acquired_property_id': ('title', ),
                        'mode':       'w', }''')
    # this property suppose that we can add some Organisation inside
    # Organisation, so we temporary patch the type information.
    ti = self.getTypesTool().getTypeInfo(obj)
    allowed_types = list(ti.allowed_content_types)
    ti.allowed_content_types = allowed_types + ['Organisation']
    try:
      constraint.fixConsistency(obj)
      self.assertEquals('foo', obj.getDefaultOrganisationTitle())
      self.assertEquals('foo', obj.default_organisation.getTitle())
    finally:
      ti.allowed_content_types = tuple(allowed_types)
      
  def test_PropertyTypeValidityFixLocalPropertiesForCategories(self):
    """Tests PropertyTypeValidity can repairs categories when this property
    is added on the class later.
    """
    bc = self.getPortal().portal_categories.newContent(
                              portal_type='Base Category',
                              id='testing_category')
    constraint = self._createGenericConstraint(Sequence(),
                   klass_name='PropertyTypeValidity',
                   id='type_validity_constraint', )
    obj = self._makeOne()
    obj.edit(testing_category=obj.getRelativeUrl())
    self.assertEquals([], constraint.checkConsistency(obj))
    # now add a 'local_property' property defined on a property sheet
    self._addPropertySheet(obj.getPortalType(),
      '''class TestPropertySheet: _categories=('testing_category',)''')
    # fix consistency
    constraint.fixConsistency(obj)
    # now we can use testing_category as any category accessor
    self.assertEquals(obj, obj.getTestingCategoryValue())

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
    object = sequence.get('object')
    content_object = object.newContent(portal_type=self.object_content_portal_type)
    sequence.edit(
        content_object = content_object,
    )

  def test_ContentExistenceConstraint(self, quiet=quiet, run=run_all_test):
    """
      Tests Content Existence
    """

    if not run: return
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
    sequence_list.play(self, quiet=quiet)

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
    object = sequence.get('object')
    object.setTitle(self.object_title)
    sequence.edit(
        object = object,
    )

  def stepSetObjectTitle1(self, sequence=None, sequence_list=None, **kw):
    """
      Set empty (or invalid string) to Object
    """
    object = sequence.get('object')
    object.setTitle(' ')
    sequence.edit(
        object = object,
    )

  def test_StringAttributeMatchConstraint(self, quiet=quiet, run=run_all_test):
    """
      Tests Content Existence
    """
    if not run: return
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

    sequence_list.play(self, quiet=quiet)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestConstraint))
        return suite
