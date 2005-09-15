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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, \
                                             noSecurityManager
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList

class TestConstraint(ERP5TypeTestCase):

  run_all_test = 1
  object_portal_type = "Organisation"
  object_title = "Title test"

  def getTitle(self):
    return "Constraint"

  def getBusinessTemplateList(self):
    """
    """
    return ()

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('rc', '', ['Manager'], [])
    user = uf.getUserById('rc').__of__(uf)
    newSecurityManager(None, user)

  def enableLightInstall(self):
    """
    You can override this. 
    Return if we should do a light install (1) or not (0)
    """
    return 1

  def enableActivityTool(self):
    """
    You can override this.
    Return if we should create (1) or not (0) an activity tool.
    """
    return 1

  def afterSetUp(self, quiet=1, run=run_all_test):
    self.login()
    portal = self.getPortal()
    self.category_tool = self.getCategoryTool()
    portal_catalog = self.getCatalogTool()
    #portal_catalog.manage_catalogClear()
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
    object.edit(title=object_title)

  def stepSetObjectNoneTitle(self, sequence=None, 
                             sequence_list=None, **kw):
    """
      Set a different title value
    """
    object = sequence.get('object')
    object_title = self.object_title
    object.edit(title=None)

  def stepSetObjectEmptyTitle(self, sequence=None, 
                              sequence_list=None, **kw):
    """
      Set a different title value
    """
    object = sequence.get('object')
    object_title = self.object_title
    object.edit(title='')

  def stepSetObjectIntTitle(self, sequence=None, 
                            sequence_list=None, **kw):
    """
      Set a different title value
    """
    object = sequence.get('object')
    object_title = self.object_title
    object.edit(title=12345)

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
      Call checkConsistency of a Constraint.
    """
    error_list = sequence.get('error_list')
    self.failIfDifferentSet(error_list, [])

  def stepCheckIfConstraintFailed(self, sequence=None, 
                                  sequence_list=None, **kw):
    """
      Call checkConsistency of a Constraint.
    """
    error_list = sequence.get('error_list')
    self.failUnless(error_list != [])

  def stepCreateConstraint(self, sequence=None, 
                           sequence_list=None, **kw):
    """
      Create a default Constraint
    """
    self._createGenericConstraint(sequence, 
                                  klass_name='Constraint',
                                  id='default_constraint',
                                  description='constraint test')

  def test_01_Constraint(self, quiet=0, run=run_all_test):
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

  def test_02_PropertyExistence(self, quiet=0, run=run_all_test):
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
    # Test Constraint with property defined on object
    # With None value
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
    # Has dissapointing it could be, empty string is a data,
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

  def test_03_PropertyTypeValidity(self, quiet=0, run=run_all_test):
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
              SetObjectIntTitle \
              CreatePropertyTypeValidity \
              CallCheckConsistency \
              CheckIfConstraintFailed \
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

  def test_04_AttributeEquality(self, quiet=0, run=run_all_test):
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

  def test_05_CategoryExistence(self, quiet=0, run=run_all_test):
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

  def test_06_CategoryMembershipArity(self, quiet=0, run=run_all_test):
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
    sequence_list.play(self)

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

  def test_07_CategoryRelatedMembershipArity(self, quiet=0, run=run_all_test):
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
    sequence_list.play(self)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestConstraint))
        return suite
