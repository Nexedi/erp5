# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#
#                     Nicolas Delaby <nicolas@nexedi.com>
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
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

clear_module_name_list = """
data_protection_request_module
""".strip().split()

class TestDataProtection(ERP5TypeTestCase):

  document_edit_kw = {'description': 'Description with compromised data'}
  # Selection name of listbox's form
  # DataProtectionRequest_viewEraseSomeOriginalDataDialog
  selection_name = 'data_protection_request_erase_data_selection'

  def getTitle(self):
    return "Data Protection"

  def getBusinessTemplateList(self):
    return ('erp5_base',
            'erp5_data_protection',)

  def beforeTearDown(self):
    # clear modules if necessary
    for module_name in clear_module_name_list:
      module = getattr(self.portal, module_name)
      module.manage_delObjects(list(module.objectIds()))

    self.tic()

  def stepCreatePersonDocument(self, sequence=None, sequence_list=None, **kw):
    """
    """
    portal = self.getPortal()
    portal_type = 'Person'
    module = portal.getDefaultModule(portal_type)
    person = module.newContent(portal_type=portal_type)
    sequence.set('document_relative_url', person.getRelativeUrl())

  def stepEditDocument(self, sequence=None, sequence_list=None, **kw):
    """
    """
    portal = self.getPortal()
    document = portal.restrictedTraverse(sequence.get('document_relative_url'))
    document.edit(**self.document_edit_kw)

  def stepValidateDocument(self, sequence=None, sequence_list=None, **kw):
    """
    """
    portal = self.getPortal()
    document = portal.restrictedTraverse(sequence.get('document_relative_url'))
    portal.portal_workflow.doActionFor(document, 'validate_action',
                                       comment='Comment with compromised data')

  def stepCreateDataProtectionRequest(self, sequence=None,
                                      sequence_list=None, **kw):
    """
    """
    portal = self.getPortal()
    portal_type = 'Data Protection Request'
    document = portal.restrictedTraverse(sequence.get('document_relative_url'))
    document.Base_addDataProtectionRequest(
                          description='I think the description is compromised')
    self.tic()
    data_protection = document.getAgentRelatedValueList(
                                                    portal_type=portal_type)[0]
    sequence.set('data_protection_request_relative_url',
                 data_protection.getRelativeUrl())

  def stepSubmitDataProtectionRequest(self, sequence=None,
                                      sequence_list=None, **kw):
    """
    """
    portal = self.getPortal()
    data_protection = portal.restrictedTraverse(
                          sequence.get('data_protection_request_relative_url'))
    data_protection.submit()

  def stepEraseDocumentProperties(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    """
    portal = self.getPortal()
    data_protection = portal.restrictedTraverse(
                          sequence.get('data_protection_request_relative_url'))
    portal.portal_selections.setSelectionCheckedUidsFor(self.selection_name,
                                                  list(self.document_edit_kw.keys()))
    # False means keep workflow history comments
    data_protection.DataProtectionRequest_eraseSomeOriginalData('View', False)

  def stepCheckErasedDataProperties(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    """
    portal = self.getPortal()
    document = portal.restrictedTraverse(sequence.get('document_relative_url'))
    for property_id in self.document_edit_kw.keys():
      # Properties are now deleted, so check that None
      # or default value is returned.
      self.assertFalse(document.getProperty(property_id))
    # View History permission is now granted only for Manager
    self.assertEqual(document._View_History_Permission, ('Manager',))

  def stepEraseWorkflowHistoryCommentList(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    """
    portal = self.getPortal()
    data_protection = portal.restrictedTraverse(
                          sequence.get('data_protection_request_relative_url'))
    # True means delete workflow history comments
    data_protection.DataProtectionRequest_eraseSomeOriginalData('View', True)

  def stepCheckErasedWorkflowHistoryCommentList(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    """
    portal = self.getPortal()
    document = portal.restrictedTraverse(sequence.get('document_relative_url'))
    workflow_history = document.workflow_history
    for workflow_id in workflow_history:
      # All comments are removed except last one
      self.assertFalse([history for history in
                       workflow_history[workflow_id][:-1]
                       if history.get('comment')])
    # Last comment of edit workflow is filled by data protection action
    self.assertTrue(workflow_history['edit_workflow'][-1].get('comment'))
    # View History permission is now granted only for Manager
    self.assertEqual(document._View_History_Permission, ('Manager',))

  def test_01_dataProtectionRequest(self):
    """This test create a person with a compromised description.
    A data protection request is create from this document.
    Then user erase properties and workflow history and check
    expected result.
      - property on object are deleted
      - Worlkflow history comments are deleted
      - Permission "View History" is granted only for Manager
    """
    sequence_list = SequenceList()
    sequence_string = '\
    CreatePersonDocument \
    EditDocument \
    ValidateDocument \
    Tic \
    CreateDataProtectionRequest \
    Tic \
    EraseDocumentProperties \
    Tic \
    CheckErasedDataProperties \
    EraseWorkflowHistoryCommentList \
    Tic \
    CheckErasedWorkflowHistoryCommentList \
    '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestDataProtection))
  return suite
