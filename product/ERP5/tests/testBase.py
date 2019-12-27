# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004, 2005, 2006 Nexedi SARL and Contributors.
# All Rights Reserved.
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

import unittest
import os
from unittest import skip

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl import getSecurityManager
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.Base import Base
from Products.ERP5Type.Utils import convertToUpperCase
from zExceptions import BadRequest
from Products.ERP5Type.Workflow import addWorkflowByType
from Products.CMFCore.WorkflowCore import WorkflowException

def getDummyTypeBaseMethod(self):
  """ Use a type Base method
  """
  script = self._getTypeBasedMethod('getDummyTypeBaseMethod')
  if script is not None:
    return script()
  return "Script Not Found"

Base.getDummyTypeBaseMethod = getDummyTypeBaseMethod


class TestBase(ERP5TypeTestCase, ZopeTestCase.Functional):

  run_all_test = 1
  quiet = 1

  object_portal_type = "Organisation"
  not_defined_property_id = "azerty_qwerty"
  not_defined_property_value = "qwerty_azerty"

  temp_class = "Amount"
  defined_property_id = "title"
  defined_property_value = "a_wonderful_title"
  not_related_to_temp_object_property_id = "string_index"
  not_related_to_temp_object_property_value = "a_great_index"

  username = 'rc'

  def getTitle(self):
    return "Base"

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base',)

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser(self.username, '', ['Manager'], [])
    user = uf.getUserById(self.username).__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    self.login()
    portal = self.getPortal()
    self.category_tool = self.getCategoryTool()
    portal_catalog = self.getCatalogTool()
    #portal_catalog.manage_catalogClear()
    self.createCategories()

    #Overwrite immediateReindexObject() with a crashing method
    def crashingMethod(self):
      self.ImmediateReindexObjectIsCalled()
    from erp5.component.document.Organisation import Organisation
    Organisation.immediateReindexObject = crashingMethod

  def beforeTearDown(self):
    # Remove crashing method
    from erp5.component.document.Organisation import Organisation
    del Organisation.immediateReindexObject

  def createCategories(self):
    """
      Light install create only base categories, so we create
      some categories for testing them
    """
    category_list = ['testGroup1', 'testGroup2']
    if 'testGroup1' not in self.category_tool.group.contentIds():
      for category_id in category_list:
        o = self.category_tool.group.newContent(portal_type='Category',
                                                id=category_id)

  def stepRemoveWorkflowsRelated(self, sequence=None, sequence_list=None,
                                 **kw):
    """
      Remove workflow related to the portal type
    """
    self.getWorkflowTool().setChainForPortalTypes(
        ['Organisation'], ())

  def stepAssociateWorkflows(self, sequence=None, sequence_list=None, **kw):
    """
      Associate workflow to the portal type
    """
    self.getWorkflowTool().setChainForPortalTypes(
        ['Organisation'], ('validation_workflow', 'edit_workflow'))

  def stepAssociateWorkflowsExcludingEdit(self, sequence=None,
                                          sequence_list=None, **kw):
    """
      Associate workflow to the portal type
    """
    self.getWorkflowTool().setChainForPortalTypes(
        ['Organisation'], ('validation_workflow',))

  def stepCreateObject(self, sequence=None, sequence_list=None, **kw):
    """
      Create a object_instance which will be tested.
    """
    portal = self.getPortal()
    module = portal.getDefaultModule(self.object_portal_type)
    object_instance = module.newContent(portal_type=self.object_portal_type)
    sequence.edit(
        object_instance=object_instance,
        current_title=object_instance.getId(), # title defaults to id
        current_group_value=None
    )

  def stepCheckTitleValue(self, sequence=None, sequence_list=None, **kw):
    """
      Check if getTitle return a correect value
    """
    object_instance = sequence.get('object_instance')
    current_title = sequence.get('current_title')
    self.assertEqual(object_instance.getTitle(), current_title)

  def stepSetDifferentTitleValueWithEdit(self, sequence=None,
                                         sequence_list=None, **kw):
    """
      Set a different title value
    """
    object_instance = sequence.get('object_instance')
    current_title = sequence.get('current_title')
    new_title_value = '%s_a' % current_title
    object_instance.edit(title=new_title_value)
    sequence.edit(
        current_title=new_title_value
    )

  def stepCheckIfActivitiesAreCreated(self, sequence=None, sequence_list=None,
                                      **kw):
    """
      Check if there is a activity in activity queue.
    """
    portal = self.getPortal()
    self.commit()
    message_list = portal.portal_activities.getMessageList()
    method_id_list = [x.method_id for x in message_list]
    # XXX FIXME: how many activities should be created normally ?
    # Sometimes it's one, sometimes 2...
    self.assertTrue(len(message_list) > 0)
    self.assertTrue(len(message_list) < 3)
    for method_id in method_id_list:
      self.assertTrue(method_id in ["immediateReindexObject"])

  def stepSetSameTitleValueWithEdit(self, sequence=None, sequence_list=None,
                                    **kw):
    """
      Set a different title value
    """
    object_instance = sequence.get('object_instance')
    object_instance.edit(title=object_instance.getTitle())

  def stepCheckIfMessageQueueIsEmpty(self, sequence=None,
                                     sequence_list=None, **kw):
    """
      Check if there is no activity in activity queue.
    """
    portal = self.getPortal()
    message_list = portal.portal_activities.getMessageList()
    self.assertEqual(len(message_list), 0)

  def test_01_areActivitiesWellLaunchedByPropertyEdit(self, quiet=quiet,
                                                      run=run_all_test):
    """
      Test if setter does not call a activity if the attribute
      value is not changed.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test without workflows associated to the portal type
    sequence_string = '\
              RemoveWorkflowsRelated \
              CreateObject \
              Tic \
              CheckTitleValue \
              SetDifferentTitleValueWithEdit \
              CheckIfActivitiesAreCreated \
              CheckTitleValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              SetSameTitleValueWithEdit \
              CheckTitleValue \
              CheckIfMessageQueueIsEmpty \
              SetDifferentTitleValueWithEdit \
              CheckIfActivitiesAreCreated \
              CheckTitleValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test with workflows associated to the portal type
    sequence_string = '\
              AssociateWorkflows \
              CreateObject \
              Tic \
              CheckTitleValue \
              SetDifferentTitleValueWithEdit \
              CheckIfActivitiesAreCreated \
              CheckTitleValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              SetSameTitleValueWithEdit \
              CheckIfActivitiesAreCreated \
              CheckTitleValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              SetDifferentTitleValueWithEdit \
              CheckIfActivitiesAreCreated \
              CheckTitleValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test with workflows associated to the portal type, excluding edit_workflow
    sequence_string = '\
              AssociateWorkflowsExcludingEdit \
              CreateObject \
              Tic \
              CheckTitleValue \
              SetDifferentTitleValueWithEdit \
              CheckIfActivitiesAreCreated \
              CheckTitleValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              SetSameTitleValueWithEdit \
              CheckIfMessageQueueIsEmpty \
              CheckTitleValue \
              SetDifferentTitleValueWithEdit \
              CheckIfActivitiesAreCreated \
              CheckTitleValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def stepCheckGroupValue(self, sequence=None, sequence_list=None, **kw):
    """
      Check if getTitle return a correect value
    """
    object_instance = sequence.get('object_instance')
    current_group_value = sequence.get('current_group_value')
    self.assertEqual(object_instance.getGroupValue(), current_group_value)

  def stepSetDifferentGroupValueWithEdit(self, sequence=None,
                                         sequence_list=None, **kw):
    """
      Set a different title value
    """
    object_instance = sequence.get('object_instance')
    current_group_value = sequence.get('current_group_value')
    group1 = object_instance.portal_categories.\
                       restrictedTraverse('group/testGroup1')
    group2 = object_instance.portal_categories.\
                       restrictedTraverse('group/testGroup2')
    if (current_group_value is None) or \
       (current_group_value == group2) :
      new_group_value = group1
    else:
      new_group_value = group2
#     new_group_value = '%s_a' % current_title
    object_instance.edit(group_value=new_group_value)
    sequence.edit(
        current_group_value=new_group_value
    )

  def stepSetSameGroupValueWithEdit(self, sequence=None, sequence_list=None,
                                    **kw):
    """
      Set a different title value
    """
    object_instance = sequence.get('object_instance')
    object_instance.edit(group_value=object_instance.getGroupValue())


  def test_02_areActivitiesWellLaunchedByCategoryEdit(self, quiet=quiet,
                                                      run=run_all_test):
    """
      Test if setter does not call a activity if the attribute
      value is not changed.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test without workflows associated to the portal type
    sequence_string = '\
              RemoveWorkflowsRelated \
              CreateObject \
              Tic \
              CheckGroupValue \
              SetDifferentGroupValueWithEdit \
              CheckIfActivitiesAreCreated \
              CheckGroupValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              SetSameGroupValueWithEdit \
              CheckIfMessageQueueIsEmpty \
              SetDifferentGroupValueWithEdit \
              CheckIfActivitiesAreCreated \
              CheckGroupValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test with workflows associated to the portal type
    sequence_string = '\
              AssociateWorkflows \
              CreateObject \
              Tic \
              CheckGroupValue \
              SetDifferentGroupValueWithEdit \
              CheckIfActivitiesAreCreated \
              CheckGroupValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              SetSameGroupValueWithEdit \
              CheckIfActivitiesAreCreated \
              CheckGroupValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              SetDifferentGroupValueWithEdit \
              CheckIfActivitiesAreCreated \
              CheckGroupValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test with workflows associated to the portal type, excluding edit_workflow
    sequence_string = '\
              AssociateWorkflowsExcludingEdit \
              CreateObject \
              Tic \
              CheckGroupValue \
              SetDifferentGroupValueWithEdit \
              CheckIfActivitiesAreCreated \
              CheckGroupValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              SetSameGroupValueWithEdit \
              CheckIfMessageQueueIsEmpty \
              SetDifferentGroupValueWithEdit \
              CheckIfActivitiesAreCreated \
              CheckGroupValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def stepSetDifferentTitleValueWithSetter(self, sequence=None,
                                           sequence_list=None, **kw):
    """
      Set a different title value
    """
    object_instance = sequence.get('object_instance')
    current_title = sequence.get('current_title')
    new_title_value = '%s_a' % current_title
    object_instance.setTitle(new_title_value)
    sequence.edit(
        current_title=new_title_value
    )

  def stepSetSameTitleValueWithSetter(self, sequence=None,
                                      sequence_list=None, **kw):
    """
      Set a different title value
    """
    object_instance = sequence.get('object_instance')
    object_instance.setTitle(object_instance.getTitle())

  def test_03_areActivitiesWellLaunchedByPropertySetter(self, quiet=quiet,
                                                        run=run_all_test):
    """
      Test if setter does not call a activity if the attribute
      value is not changed.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test without workflows associated to the portal type
    sequence_string = '\
              RemoveWorkflowsRelated \
              CreateObject \
              Tic \
              CheckTitleValue \
              SetDifferentTitleValueWithSetter \
              CheckIfActivitiesAreCreated \
              CheckTitleValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              SetSameTitleValueWithSetter \
              CheckIfActivitiesAreCreated \
              CheckTitleValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              SetDifferentTitleValueWithSetter \
              CheckIfActivitiesAreCreated \
              CheckTitleValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test with workflows associated to the portal type
    sequence_string = '\
              AssociateWorkflows \
              CreateObject \
              Tic \
              CheckTitleValue \
              SetDifferentTitleValueWithSetter \
              CheckIfActivitiesAreCreated \
              CheckTitleValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              SetSameTitleValueWithSetter \
              CheckIfActivitiesAreCreated \
              CheckTitleValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              SetDifferentTitleValueWithSetter \
              CheckIfActivitiesAreCreated \
              CheckTitleValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def stepSetDifferentGroupValueWithSetter(self, sequence=None,
                                           sequence_list=None, **kw):
    """
      Set a different title value
    """
    object_instance = sequence.get('object_instance')
    current_group_value = sequence.get('current_group_value')
    group1 = object_instance.portal_categories.\
                                   restrictedTraverse('group/testGroup1')
    group2 = object_instance.portal_categories.\
                                   restrictedTraverse('group/testGroup2')
    if (current_group_value is None) or \
       (current_group_value == group2) :
      new_group_value = group1
    else:
      new_group_value = group2
#     new_group_value = '%s_a' % current_title
    object_instance.setGroupValue(new_group_value)
    sequence.edit(
        current_group_value=new_group_value
    )

  def stepSetSameGroupValueWithSetter(self, sequence=None,
                                      sequence_list=None, **kw):
    """
      Set a different title value
    """
    object_instance = sequence.get('object_instance')
    object_instance.setGroupValue(object_instance.getGroupValue())

  def test_04_areActivitiesWellLaunchedByCategorySetter(self, quiet=quiet,
                                                        run=run_all_test):
    """
      Test if setter does not call a activity if the attribute
      value is not changed.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test without workflows associated to the portal type
    sequence_string = '\
              RemoveWorkflowsRelated \
              CreateObject \
              Tic \
              CheckGroupValue \
              SetDifferentGroupValueWithSetter \
              CheckIfActivitiesAreCreated \
              CheckGroupValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              SetSameGroupValueWithSetter \
              CheckIfActivitiesAreCreated \
              CheckGroupValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              SetDifferentGroupValueWithSetter \
              CheckIfActivitiesAreCreated \
              CheckGroupValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test with workflows associated to the portal type
    sequence_string = '\
              AssociateWorkflows \
              CreateObject \
              Tic \
              CheckGroupValue \
              SetDifferentGroupValueWithSetter \
              CheckIfActivitiesAreCreated \
              CheckGroupValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              SetSameGroupValueWithSetter \
              CheckIfActivitiesAreCreated \
              CheckGroupValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              SetDifferentGroupValueWithSetter \
              CheckIfActivitiesAreCreated \
              CheckGroupValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def stepSetObjectNotDefinedProperty(self, sequence=None,
                                      sequence_list=None, **kw):
    """
    Set a not defined property on the object_instance.
    """
    object_instance = sequence.get('object_instance')
    object_instance.setProperty(self.not_defined_property_id,
                       self.not_defined_property_value)

  def stepCheckNotDefinedPropertySaved(self, sequence=None,
                                       sequence_list=None, **kw):
    """
    Check if a not defined property is stored on the object_instance.
    """
    object_instance = sequence.get('object_instance')
    self.assertEqual(self.not_defined_property_value,
                      getattr(object_instance, self.not_defined_property_id))

  def stepCheckGetNotDefinedProperty(self, sequence=None,
                                     sequence_list=None, **kw):
    """
    Check getProperty with a not defined property.
    """
    object_instance = sequence.get('object_instance')
    self.assertEqual(self.not_defined_property_value,
                    object_instance.getProperty(self.not_defined_property_id))

  def stepCheckObjectPortalType(self, sequence=None,
                                sequence_list=None, **kw):
    """
    Check the portal type of the object_instance.
    """
    object_instance = sequence.get('object_instance')
    object_instance.getPortalType()
    self.assertEqual(self.object_portal_type,
                      object_instance.getPortalType())

  def stepCreateTempObject(self, sequence=None, sequence_list=None, **kw):
    """
      Create a temp object_instance which will be tested.
    """
    portal = self.getPortal()
    tmp_object = portal.newContent(temp_object=True,
      portal_type='Organisation', id="a_wonderful_id")
    sequence.edit(
        object_instance=tmp_object,
        current_title='',
        current_group_value=None
    )

  def test_05_getPropertyWithoutPropertySheet(self, quiet=quiet, run=run_all_test):
    """
    Test if set/getProperty work without any property sheet.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test on object_instance.
    sequence_string = '\
              CreateObject \
              SetObjectNotDefinedProperty \
              CheckNotDefinedPropertySaved \
              CheckGetNotDefinedProperty \
              '
    sequence_list.addSequenceString(sequence_string)
    # Test on temp object_instance.
    sequence_string = '\
              CreateTempObject \
              CheckObjectPortalType \
              SetObjectNotDefinedProperty \
              CheckNotDefinedPropertySaved \
              CheckGetNotDefinedProperty \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def stepCreateTempClass(self, sequence=None, sequence_list=None, **kw):
    """
    Create a temp object_instance which will be tested.
    """
    portal = self.getPortal()
    tmp_object = portal.newContent(temp_object=True, portal_type='Amount',
      id="another_wonderful_id")
    sequence.edit(
        object_instance=tmp_object,
        current_title='',
        current_group_value=None
    )

  def stepCheckTempClassPortalType(self, sequence=None,
                                   sequence_list=None, **kw):
    """
    Check the portal type of the object_instance.
    """
    object_instance = sequence.get('object_instance')
    object_instance.getPortalType()
    self.assertEqual(self.temp_class,
                      object_instance.getPortalType())

  def stepSetObjectDefinedProperty(self, sequence=None,
                                      sequence_list=None, **kw):
    """
    Set a defined property on the object_instance.
    """
    object_instance = sequence.get('object_instance')
    object_instance.setProperty(self.defined_property_id,
                       self.defined_property_value)

  def stepCheckDefinedPropertySaved(self, sequence=None,
                                       sequence_list=None, **kw):
    """
    Check if a defined property is stored on the object_instance.
    """
    object_instance = sequence.get('object_instance')
    self.assertEqual(self.defined_property_value,
                      getattr(object_instance, self.defined_property_id))

  def stepCheckGetDefinedProperty(self, sequence=None,
                                     sequence_list=None, **kw):
    """
    Check getProperty with a defined property.
    """
    object_instance = sequence.get('object_instance')
    self.assertEqual(self.defined_property_value,
                    object_instance.getProperty(self.defined_property_id))

  def stepSetObjectNotRelatedProperty(self, sequence=None,
                                      sequence_list=None, **kw):
    """
    Set a defined property on the object_instance.
    """
    object_instance = sequence.get('object_instance')
    object_instance.setProperty(
                       self.not_related_to_temp_object_property_id,
                       self.not_related_to_temp_object_property_value)

  def stepCheckNotRelatedPropertySaved(self, sequence=None,
                                       sequence_list=None, **kw):
    """
    Check if a defined property is stored on the object_instance.
    """
    object_instance = sequence.get('object_instance')
    self.assertEqual(self.not_related_to_temp_object_property_value,
                      getattr(object_instance,
                              self.not_related_to_temp_object_property_id))

  def stepCheckGetNotRelatedProperty(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Check getProperty with a defined property.
    """
    object_instance = sequence.get('object_instance')
    self.assertEqual(self.not_related_to_temp_object_property_value,
                    object_instance.getProperty(
                         self.not_related_to_temp_object_property_id))

  def test_06_getPropertyOnTempClass(self, quiet=quiet, run=1):
    """
    Test if set/getProperty work in temp object without
    a portal type with the same name.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test on temp tempAmount.
    sequence_string = '\
              CreateTempClass \
              CheckTempClassPortalType \
              SetObjectDefinedProperty \
              CheckDefinedPropertySaved \
              CheckGetDefinedProperty \
              SetObjectNotDefinedProperty \
              CheckNotDefinedPropertySaved \
              CheckGetNotDefinedProperty \
              SetObjectNotRelatedProperty \
              CheckNotRelatedPropertySaved \
              CheckGetNotRelatedProperty \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def stepCheckEditMethod(self, sequence=None,
                          sequence_list=None, **kw):
    """
    Check if edit method works.
    """
    object_instance = sequence.get('object_instance')
    object_instance.edit(title='toto')
    self.assertEqual(object_instance.getTitle(),'toto')
    object_instance.edit(title='tutu')
    self.assertEqual(object_instance.getTitle(),'tutu')

  def stepSetEditProperty(self, sequence=None,
                          sequence_list=None, **kw):
    """
    Check if edit method works.
    """
    object_instance = sequence.get('object_instance')
    # can't override a method:
    self.assertRaises(BadRequest, object_instance.setProperty, 'edit',
                      "now this object is 'read only !!!'")
    # can't change the portal type and other internal instance attributes
    self.assertRaises(BadRequest, object_instance.setProperty,
                      'portal_type', "Other")
    self.assertRaises(BadRequest, object_instance.setProperty,
                      'workflow_history', {})
    self.assertRaises(BadRequest, object_instance.setProperty,
                      '__dict__', {})


  def test_07_setEditProperty(self, quiet=quiet, run=run_all_test):
    """
    Test if setProperty erase existing accessors/methods.
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = '\
              CreateObject \
              CheckEditMethod \
              SetEditProperty \
              CheckEditMethod \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def stepCreateBaseCategory(self, sequence=None, sequence_list=None, **kw):
    """
    Create a base category.
    """
    portal = self.getPortal()
    module = portal.portal_categories
    object_instance = module.newContent(portal_type="Base Category")
    sequence.edit(
        object_instance=object_instance,
    )

  def stepSetBadTalesExpression(self, sequence=None, sequence_list=None, **kw):
    """
    Set a wrong tales expression
    """
    object_instance = sequence.get('object_instance')
    tales_expression = "python: 1 + 'a'"
    object_instance.edit(acquisition_portal_type_list=tales_expression)
    sequence.edit(
        tales_expression=tales_expression,
    )

  def stepCheckTalesExpression(self, sequence=None, sequence_list=None, **kw):
    """
    Set a wrong tales expression
    """
    object_instance = sequence.get('object_instance')
    tales_expression = sequence.get('tales_expression')
    self.assertEqual(object_instance.getAcquisitionPortalTypeList(evaluate=0),
                      tales_expression)

  def stepSetGoodTalesExpression(self, sequence=None,
                                 sequence_list=None, **kw):
    """
    Set a wrong tales expression
    """
    object_instance = sequence.get('object_instance')
    tales_expression = "python: 1 + 1"
    object_instance.edit(acquisition_portal_type_list=tales_expression)
    sequence.edit(
        tales_expression=tales_expression,
    )

  def test_07_setEditTalesExpression(self, quiet=quiet, run=run_all_test):
    """
    Test if edit update a tales expression.
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = '\
              CreateBaseCategory \
              SetBadTalesExpression \
              CheckTalesExpression \
              SetGoodTalesExpression \
              CheckTalesExpression \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_08_emptyObjectAcquiresTitle(self, quiet=quiet, run=run_all_test):
    """
    Test that an empty object has no title, and that getTitle on it acquires a
    value form the object's id.
    """
    if not run: return
    portal = self.getPortal()
    portal_type = "Organisation"
    module = portal.getDefaultModule(portal_type=portal_type)
    obj = module.newContent(portal_type=portal_type)
    # XXX title is an empty string by default, but it's still unsure wether it
    # should be None or ''
    self.assertEqual(obj.title, '')
    self.assertEqual(obj.getProperty("title"), obj.getId())
    self.assertEqual(obj._baseGetTitle(), obj.getId())
    self.assertEqual(obj.getTitle(), obj.getId())

  def test_09_setPropertyDefinedProperty(self, quiet=quiet, run=run_all_test):
    """Test for setProperty on Base, when the property is defined.
    """
    if not run: return
    portal = self.getPortal()
    portal_type = "Organisation"
    module = portal.getDefaultModule(portal_type=portal_type)
    obj = module.newContent(portal_type=portal_type)
    title = 'Object title'
    obj.setProperty('title', title)
    self.assertEqual(obj.getProperty('title'), title)
    obj.setProperty('title', title)
    self.assertEqual(obj.getProperty('title'), title)
    obj.edit(title=title)
    self.assertEqual(obj.getProperty('title'), title)

  def test_10_setPropertyNotDefinedProperty(self, quiet=quiet,
                                            run=run_all_test):
    """Test for setProperty on Base, when the property is not defined.
    """
    if not run: return
    portal = self.getPortal()
    portal_type = "Organisation"
    module = portal.getDefaultModule(portal_type=portal_type)
    obj = module.newContent(portal_type=portal_type)
    property_value = 'Object title'
    property_name = 'a_dummy_not_exising_property'
    obj.setProperty(property_name, property_value)
    self.assertEqual(obj.getProperty(property_name), property_value)
    obj.setProperty(property_name, property_value)
    self.assertEqual(obj.getProperty(property_name), property_value)
    obj.edit(**{property_name: property_value})
    self.assertEqual(obj.getProperty(property_name), property_value)

  def test_11_setPropertyPropertyDefinedOnInstance(self,
                                        quiet=quiet, run=run_all_test):
    """Test for setProperty on Base, when the property is defined on the
    instance, the typical example is 'workflow_history' property.
    """
    if not run: return
    portal = self.getPortal()
    portal_type = "Organisation"
    module = portal.getDefaultModule(portal_type=portal_type)
    obj = module.newContent(portal_type=portal_type)

    property_value = 'Property value'
    property_name = 'a_dummy_object_property'
    setattr(obj, property_name, property_value)
    self.assertRaises(BadRequest, obj.setProperty,
                     property_name, property_value)

    self.assertRaises(BadRequest, obj.setProperty,
                     'workflow_history', property_value)

  def test_12_editTempObject(self, quiet=quiet, run=run_all_test):
    """Simple t
    est to edit a temp object.
    """
    portal = self.getPortal()
    tmp_object = portal.newContent(temp_object=True, portal_type='Organisation',
      id="a_wonderful_id")
    tmp_object.edit(title='new title')
    self.assertEqual('new title', tmp_object.getTitle())

  def test_13_aqDynamicWithNonExistentWorkflow(self, quiet=quiet, run=run_all_test):
    """Test if _aq_dynamic still works even if an associated workflow
    is not present in the portal. This may cause an infinite recursion."""
    if not run: return

    portal = self.getPortal()
    portal_type = "Organisation"
    module = portal.getDefaultModule(portal_type = portal_type)
    obj = module.newContent(portal_type = portal_type)

    # Add a non-existent workflow.
    pw = self.getWorkflowTool()
    dummy_worlflow_id = 'never_existent_workflow'
    addWorkflowByType(pw, 'erp5_workflow', dummy_worlflow_id)

    self.commit()

    cbt = pw._chains_by_type
    props = {}
    for id, wf_ids in cbt.iteritems():
      if id == portal_type:
        wf_ids = list(wf_ids) + [dummy_worlflow_id]
      props['chain_%s' % id] = ','.join(wf_ids)
    pw.manage_changeWorkflows('', props = props)
    pw.manage_delObjects([dummy_worlflow_id])

    self.commit()

    try:
      self.assertRaises(AttributeError, getattr, obj,
                        'thisMethodShouldNotBePresent')
    finally:
      # Make sure that the artificial workflow is not referred to any longer.
      cbt = pw._chains_by_type
      props = {}
      for id, wf_ids in cbt.iteritems():
        if id == portal_type:
          # Remove the non-existent workflow.
          wf_ids = [wf_id for wf_id in wf_ids \
                    if wf_id != dummy_worlflow_id]
        props['chain_%s' % id] = ','.join(wf_ids)
      pw.manage_changeWorkflows('', props = props)

      self.commit()

  def test_14_UpdateRoleMappingwithNoDefinedRoleAndAcquisitionActivatedOnWorkflow(self, quiet=quiet, run=run_all_test):
    """updateRoleMappingsFor does a logical AND between all workflow defining security,
    if a workflow defines no permission and is set to acquire permissions,
    and another workflow defines permission and is set not to acquire perm,
    then user have no permissions.
    It may depends on which workflow pass the last transition.
    """
    if not run: return

    portal = self.getPortal()
    portal_type = "Organisation"
    module = portal.getDefaultModule(portal_type=portal_type)

    # Add a non-existent workflow.
    pw = self.getWorkflowTool()
    dummy_simulation_worlflow_id = 'fake_simulation_workflow'
    dummy_validation_worlflow_id = 'fake_validation_workflow'
    #Assume that erp5_styles workflow Manage permissions with acquired Role by default
    addWorkflowByType(pw, 'erp5_workflow', dummy_simulation_worlflow_id)
    addWorkflowByType(pw, 'erp5_workflow', dummy_validation_worlflow_id)
    dummy_simulation_worlflow = pw[dummy_simulation_worlflow_id]
    dummy_validation_worlflow = pw[dummy_validation_worlflow_id]
    dummy_validation_worlflow.variables.setStateVar('validation_state')
    cbt = pw._chains_by_type
    props = {}
    for id, wf_ids in cbt.iteritems():
      if id == portal_type:
        old_wf_ids = wf_ids
      props['chain_%s' % id] = ','.join([dummy_validation_worlflow_id, dummy_simulation_worlflow_id])
    pw.manage_changeWorkflows('', props=props)
    permission_list = list(dummy_simulation_worlflow.permissions)
    manager_has_permission = {}
    for permission in permission_list:
      manager_has_permission[permission] = ('Manager',)
    manager_has_no_permission = {}
    for permission in permission_list:
      manager_has_no_permission[permission] = ()

    user = getSecurityManager().getUser()
    try:
      self.assertTrue(permission_list)
      self.assertFalse(dummy_simulation_worlflow.states.draft.permission_roles)
      #1
      obj = module.newContent(portal_type=portal_type)
      #No role is defined by default on workflow
      for permission in permission_list:
        self.assertTrue(user.has_permission(permission, module))
      #then check permission is acquired
      for permission in permission_list:
        self.assertTrue(user.has_permission(permission, obj))
      #2 Now configure both workflow with same configuration
      dummy_simulation_worlflow.states.draft.permission_roles = manager_has_permission.copy()
      dummy_validation_worlflow.states.draft.permission_roles = manager_has_permission.copy()
      dummy_simulation_worlflow.updateRoleMappingsFor(obj)
      dummy_validation_worlflow.updateRoleMappingsFor(obj)

      for permission in permission_list:
        self.assertTrue(user.has_permission(permission, obj))
      #3 change only dummy_simulation_worlflow
      dummy_simulation_worlflow.states.draft.permission_roles = manager_has_no_permission.copy()
      dummy_simulation_worlflow.updateRoleMappingsFor(obj)

      for permission in permission_list:
        self.assertFalse(user.has_permission(permission, obj))
      #4 enable acquisition for dummy_simulation_worlflow
      dummy_simulation_worlflow.states.draft.permission_roles = None
      dummy_simulation_worlflow.updateRoleMappingsFor(obj)
      for permission in permission_list:
        self.assertTrue(user.has_permission(permission, obj))
    finally:
      # Make sure that the artificial workflow is not referred to any longer.
      cbt = pw._chains_by_type
      props = {}
      for id, wf_ids in cbt.iteritems():
        if id == portal_type:
          # Remove the non-existent workflow.
          wf_ids = old_wf_ids
        props['chain_%s' % id] = ','.join(wf_ids)
      pw.manage_changeWorkflows('', props=props)
      pw.manage_delObjects([dummy_simulation_worlflow_id, dummy_validation_worlflow_id])

  def test_getViewPermissionOwnerDefault(self):
    """Test getViewPermissionOwner method behaviour"""
    portal = self.getPortal()
    obj = portal.organisation_module.newContent(portal_type='Organisation')
    self.assertEqual(self.username, obj.getViewPermissionOwner())

  def test_getViewPermissionOwnerNoOwnerLocalRole(self):
    # the actual owner doesn't have Owner local role
    portal = self.getPortal()
    obj = portal.organisation_module.newContent(portal_type='Organisation')
    obj.manage_delLocalRoles(self.username)
    self.assertEqual(self.username, obj.getViewPermissionOwner())

  def test_getViewPermissionOwnerNoViewPermission(self):
    # the owner cannot view the object
    portal = self.getPortal()
    obj = portal.organisation_module.newContent(portal_type='Organisation')
    obj.manage_permission('View', [], 0)
    self.assertEqual(None, obj.getViewPermissionOwner())

  def test_Member_Base_download(self):
    # tests that members can download files
    class DummyFile(file):
      def __init__(self, filename):
        self.filename = os.path.basename(filename)
        file.__init__(self, filename)
    portal = self.getPortal()
    organisation = portal.organisation_module.newContent(portal_type='Organisation')
    file_document = organisation.newContent(portal_type='Embedded File',
                                            file=DummyFile(__file__),
                                            content_type='text/plain')

    # login as a member
    uf = self.portal.acl_users
    uf._doAddUser('member_user', 'secret', ['Member'], [])
    user = uf.getUserById('member_user').__of__(uf)
    newSecurityManager(None, user)

    # if it didn't raise Unauthorized, Ok
    basic = '%s:' % self.username
    response = self.publish('%s/Base_download' % file_document.getPath(),
                            basic=basic)
    self.assertEqual(file_document.getData(), response.body)
    self.assertEqual('text/plain',
                      response.getHeader('content-type').split(';')[0])
    self.assertEqual('attachment; filename="%s"' % os.path.basename(__file__),
                      response.getHeader('content-disposition'))

  def test_getTypeBasedMethod(self):
    """
    Test that getTypeBasedMethod look up at ancestor classes
    and stop after Base and Folder Classes
    """
    from Products.ERP5Type.tests.utils import createZODBPythonScript
    portal = self.getPortal()

    base_script = createZODBPythonScript(portal.portal_skins.custom,
                        'Base_fooMethod',
                        'scripts_params=None',
                        '# Script body\n'
                        'return context.getId()' )
    xml_object_script = createZODBPythonScript(portal.portal_skins.custom,
                        'XMLObject_dummyMethod',
                        'scripts_params=None',
                        '# Script body\n'
                        'return context.getId()' )
    person_script = createZODBPythonScript(portal.portal_skins.custom,
                        'Person_dummyMethod',
                        'scripts_params=None',
                        '# Script body\n'
                        'return context.getId()' )
    copy_container_script = createZODBPythonScript(portal.portal_skins.custom,
                        'CopyContainer_dummyFooMethod',
                        'scripts_params=None',
                        '# Script body\n'
                        'return context.getId()' )
    cmfbtree_folder_script = createZODBPythonScript(portal.portal_skins.custom,
                        'CMFBTreeFolder_dummyFoo2Method',
                        'scripts_params=None',
                        '# Script body\n'
                        'return context.getId()' )
    org = portal.organisation_module.newContent(portal_type='Organisation')
    pers = portal.person_module.newContent(portal_type='Person')

    self.assertEqual(org._getTypeBasedMethod('dummyMethod'), xml_object_script)
    self.assertEqual(pers._getTypeBasedMethod('dummyMethod'), person_script)
    self.assertEqual(org._getTypeBasedMethod('fooMethod'), base_script)
    self.assertEqual(pers._getTypeBasedMethod('fooMethod'), base_script)
    self.assertEqual(org._getTypeBasedMethod('dummyFooMethod'), None)
    self.assertEqual(org._getTypeBasedMethod('dummyFoo2Method'), None)

    # Call the scripts to make sure the context are appropriated.
    self.assertEqual(org._getTypeBasedMethod('dummyMethod')(), org.getId())
    self.assertEqual(pers._getTypeBasedMethod('dummyMethod')(), pers.getId())
    self.assertEqual(org._getTypeBasedMethod('fooMethod')(), org.getId())
    self.assertEqual(pers._getTypeBasedMethod('fooMethod')(), pers.getId())

    self.assertEqual(pers.getDummyTypeBaseMethod(), "Script Not Found")

    person_dummy_script = createZODBPythonScript(portal.portal_skins.custom,
                        'Person_getDummyTypeBaseMethod',
                        'scripts_params=None',
                        '# Script body\n'
                        'return context.getId()' )

    dummy_script_by_activity = createZODBPythonScript(portal.portal_skins.custom,
                        'Person_getDummyTypeBaseMethodByActivity',
                        'scripts_params=None',
                        '# Script body\n'
                        'context.getDummyTypeBaseMethod()\n'
                        'return context.getDummyTypeBaseMethod()' )


    self.commit()# Flush transactional cache.
    self.assertEqual(pers.getDummyTypeBaseMethod(), pers.getId())
    # Call once more to check cache.
    self.assertEqual(pers.getDummyTypeBaseMethod(), pers.getId())

    pers.activate().Person_getDummyTypeBaseMethodByActivity()
    self.tic()

  def test_translate_table(self):
    """check if Person portal type that is installed in erp5_base is
    well indexed in translate table or not.
    """
    self.getPortal().person_module.newContent(portal_type='Person',
                                         title='translate_table_test')
    self.tic()
    self.assertEqual(1, len(self.getPortal().portal_catalog(
      portal_type='Person', title='translate_table_test')))
    self.assertEqual(1, len(self.getPortal().portal_catalog(
      translated_portal_type='Person', title='translate_table_test')))

  def test_TemporaryObjectPublicMethodListForAnonymous(self):
    """make sure temporary object methods are actually public.
    Thanks to owner role, even for Anonymous users
    """
    self.logout()
    organisation = self.portal.organisation_module.newContent(
                                                    portal_type='Organisation',
                                                    temp_object=True)
    user = getSecurityManager().getUser()
    self.assertTrue('Owner' in user.getRolesInContext(organisation))
    from AccessControl.ZopeGuards import guarded_getattr
    property_map_dict = organisation.propertyMap()
    property_id_list = ('edit', 'setProperty', 'getProperty') + \
              tuple(['get' + convertToUpperCase(property_map['id'])\
                     for property_map in property_map_dict])

    for property_id in property_id_list:
      # should not raise Unauthorized
      guarded_getattr(organisation, property_id)

  def test_TemporaryObjectPublicMethodList(self):
    """make sure temporary object methods are actually public.
    Thanks to owner role.
    """
    uf = self.getPortal().acl_users
    uf._doAddUser('BOBBY', '', ['Member',], [])
    user = uf.getUserById('BOBBY').__of__(uf)
    newSecurityManager(None, user)
    organisation = self.portal.organisation_module.newContent(
                                                    portal_type='Organisation',
                                                    temp_object=True)
    user = getSecurityManager().getUser()
    self.assertTrue('Owner' in user.getRolesInContext(organisation))
    from AccessControl.ZopeGuards import guarded_getattr
    property_map_dict = organisation.propertyMap()
    property_id_list = ('edit', 'setProperty', 'getProperty') + \
              tuple(['get' + convertToUpperCase(property_map['id'])\
                     for property_map in property_map_dict])

    for property_id in property_id_list:
      # should not raise Unauthorized
      guarded_getattr(organisation, property_id)

  @skip("isIndexable is not designed to work like tested here, this test \
      must be rewritten once we know how to handle correctly templates")
  def test_NonIndexable(self):
    """check if a document is not indexed where we set isIndexable=0 in the same transaction of newContent().
    """
    person = self.portal.person_module.newContent(portal_type='Person')
    person.isIndexable = 0
    self.tic()
    self.assertFalse(person.isIndexable)
    self.assertEqual(0, len(self.portal.portal_catalog(uid=person.getUid())))

  @skip("isIndexable is not designed to work like tested here, this test \
      must be rewritten once we know how to handle correctly templates")
  def test_NonIndexable2(self):
    """check if a document is not indexed where we call edit() and set isIndexable=0 after it is already indexed.
    """
    person = self.portal.person_module.newContent(portal_type='Person')
    self.tic()
    self.assertTrue(person.isIndexable)
    self.assertEqual(1, len(self.portal.portal_catalog(uid=person.getUid())))

    # edit() will register a reindex activity because isIndexable is
    # not yet False when edit() is called.
    person.edit()
    person.isIndexable = 0
    self.tic()
    self.assertFalse(person.isIndexable)
    self.assertEqual(0, len(self.portal.portal_catalog(uid=person.getUid())))

  @skip("isIndexable is not designed to work like tested here, this test \
      must be rewritten once we know how to handle correctly templates")
  def test_NonIndexable3(self):
    """check if a document is not indexed where we set isIndexable=0 and call edit() after it is already indexed.
    """
    person = self.portal.person_module.newContent(portal_type='Person')
    self.tic()
    self.assertTrue(person.isIndexable)
    self.assertEqual(1, len(self.portal.portal_catalog(uid=person.getUid())))

    # edit() will not register a reindex activity because isIndexable
    # is already False when edit() is called.
    person.isIndexable = 0
    person.edit()
    self.tic()
    self.assertFalse(person.isIndexable)
    self.assertEqual(0, len(self.portal.portal_catalog(uid=person.getUid())))

  def test_metaWorkflowTransition(self):
    """Test Meta Transtion, jump from state to another without explicitely
    transtion defined.
    """
    module = self.portal.person_module
    person = module.newContent(portal_type='Person')
    self.assertEqual(person.getValidationState(), 'draft')
    self.assertTrue(self.portal.portal_workflow.isTransitionPossible(person,
                                                                 'invalidate'))
    # test low-level implementation
    self.portal.portal_workflow.validation_workflow._executeMetaTransition(
                                                         person, 'invalidated')
    self.assertEqual(person.getValidationState(), 'invalidated')
    validation_history = person.workflow_history['validation_workflow']
    self.assertEqual(len(validation_history), 2)
    self.assertEqual(validation_history[-1]['comment'],
                                      'Jump from \'draft\' to \'invalidated\'')
    person = module.newContent(portal_type='Person')
    self.assertEqual(person.getValidationState(), 'draft')

    # test high-level implementation
    self.portal.portal_workflow._jumpToStateFor(person, 'invalidated')
    self.assertEqual(person.getValidationState(), 'invalidated')

    person = module.newContent(portal_type='Person')
    self.assertEqual(person.getValidationState(), 'draft')
    self.portal.portal_workflow._jumpToStateFor(person, 'invalidated',
                                               wf_id='validation_workflow')
    self.assertEqual(person.getValidationState(), 'invalidated')
    person = module.newContent(portal_type='Person')
    self.assertEqual(person.getValidationState(), 'draft')
    self.assertRaises(WorkflowException,
                      self.portal.portal_workflow._jumpToStateFor,
                      person, 'invalidated', wf_id='edit_workflow')
    self.assertEqual(person.getValidationState(), 'draft')


class TestERP5PropertyManager(unittest.TestCase):
  """Tests for ERP5PropertyManager.
  """
  def _makeOne(self, *args, **kw):
    from Products.ERP5Type.patches.PropertyManager import ERP5PropertyManager
    ob = ERP5PropertyManager(*args, **kw)
    # add missing methods for createExpressionContext
    ob.getPortalObject = lambda : None
    ob.absolute_url = lambda: ''
    return ob

  def test_setProperty(self):
    """_setProperty adds a new property if not present."""
    ob = self._makeOne('ob')
    dummy_property_value = 'test string value'
    ob._setProperty('a_dummy_property', dummy_property_value)

    # the property appears in property map
    self.assertTrue('a_dummy_property' in [x['id'] for x in ob.propertyMap()])
    # the value and can be retrieved using getProperty
    self.assertEqual(ob.getProperty('a_dummy_property'), dummy_property_value)
    # the value is also stored as a class attribute
    self.assertEqual(ob.a_dummy_property, dummy_property_value)

  def test_setPropertyExistingProperty(self):
    """_setProperty raises an error if the property already exists."""
    ob = self._makeOne('ob')
    # make sure that title property exists
    self.assertTrue('title' in [x['id'] for x in ob.propertyMap()])
    # trying to call _setProperty will with an existing property raises:
    #         BadRequest: Invalid or duplicate property id: title
    self.assertRaises(BadRequest, ob._setProperty, 'title', 'property value')

  def test_updatePropertyExistingProperty(self):
    """_updateProperty should be used if the existing property already exists.
    """
    ob = self._makeOne('ob')
    # make sure that title property exists
    self.assertTrue('title' in [x['id'] for x in ob.propertyMap()])
    prop_value = 'title value'
    ob._updateProperty('title', prop_value)
    self.assertEqual(ob.getProperty('title'), prop_value)
    self.assertEqual(ob.title, prop_value)

  def test_setPropertyTypeInt(self):
    """You can specify the type of the property in _setProperty"""
    ob = self._makeOne('ob')
    dummy_property_value = 3
    ob._setProperty('a_dummy_property', dummy_property_value, type='int')
    self.assertEqual(['int'], [x['type'] for x in ob.propertyMap()
                                        if x['id'] == 'a_dummy_property'])
    self.assertEqual(type(ob.getProperty('a_dummy_property')), type(1))

  def test_setPropertyTALESType(self):
    """ERP5PropertyManager can use TALES Type for properties, TALES will then
    be evaluated in getProperty.
    """
    ob = self._makeOne('ob')
    dummy_property_value = 'python: 1+2'
    ob._setProperty('a_dummy_property', dummy_property_value, type='tales')
    self.assertEqual(ob.getProperty('a_dummy_property'), 1+2)

  def test_setPropertyTypeDate(self):
    """You can specify the type of the property in _setProperty"""
    ob = self._makeOne('ob')
    from DateTime import DateTime
    dummy_property_value = DateTime()
    ob._setProperty('a_dummy_property', dummy_property_value, type='date')
    self.assertEqual(['date'], [x['type'] for x in ob.propertyMap()
                                        if x['id'] == 'a_dummy_property'])
    self.assertEqual(type(ob.getProperty('a_dummy_property')), type(DateTime()))
    #Set Property without type argument
    ob._setProperty('a_second_dummy_property', dummy_property_value)
    self.assertEqual(['date'], [x['type'] for x in ob.propertyMap()
                                        if x['id'] == 'a_second_dummy_property'])
    self.assertEqual(type(ob.getProperty('a_second_dummy_property')),
                      type(DateTime()))

  def test_setPropertyTypeLines(self):
    ob = self._makeOne('ob')
    ob._setProperty('a_dummy_list_property', ('1', '2'), type='lines')
    self.assertEqual(['lines'], [x['type'] for x in ob.propertyMap()
                                        if x['id'] == 'a_dummy_list_property'])
    self.assertEqual(ob.getProperty('a_dummy_list_property'), ('1', '2'))

    #Set Property without type argument
    ob._setProperty('a_second_dummy_property_list', ('3', '4'))
    self.assertEqual(['lines'], [x['type'] for x in ob.propertyMap()
                                if x['id'] == 'a_second_dummy_property_list'])
    self.assertEqual(ob.getProperty('a_second_dummy_property_list'),
                                    ('3', '4'))
    # same, but passing a list, not a tuple
    ob._setProperty('a_third_dummy_property_list', ['5', '6'])
    self.assertEqual(['lines'], [x['type'] for x in ob.propertyMap()
                                if x['id'] == 'a_third_dummy_property_list'])
    self.assertEqual(ob.getProperty('a_third_dummy_property_list'),
                                    ('5', '6'))

  def test_getPropertyNonExistantProps(self):
    """getProperty return None if the value is not found.
    """
    ob = self._makeOne('ob')
    self.assertEqual(ob.getProperty('a_dummy_property'), None)

  def test_getPropertyDefaultValue(self):
    """getProperty accepts a default value, if the property is not defined.
    """
    ob = self._makeOne('ob')
    self.assertEqual(ob.getProperty('a_dummy_property', 100), 100)
    prop_value = 3
    ob._setProperty('a_dummy_property', prop_value)
    self.assertEqual(ob.getProperty('a_dummy_property', 100), prop_value)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestBase))
  suite.addTest(unittest.makeSuite(TestERP5PropertyManager))
  return suite
