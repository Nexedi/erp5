#############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Yusei TAHARA <yusei@nexedi.com>
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

import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import transaction

class TestContributionRegistryTool(ERP5TypeTestCase):

  run_all_test = 1

  def getTitle(self):
    return "Contribution Registry Tool"

  def getBusinessTemplateList(self):
    return ()

  def afterSetUp(self):
    self.setUpTestScript()
    self.setUpMimeType()
    self.setUpPredicate()

  def setUpTestScript(self):
    if getattr(self.portal, 'IngestionFile_testEvent', None) is not None:
      return
    python_script_src = (
"""\
## Script (Python) "IngestionFile_testEvent"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=predicate=None
##title=
##
from Products.ERP5Type.Document import newTempEvent

event = newTempEvent(context, 'subobject', data=context.getData())

subject = event.getContentInformation().get('Subject', None)
if subject == 'Fax':
  return 'Fax Message'
return predicate.getDestinationPortalType()
""")
    self.portal.manage_addProduct['PythonScripts'].manage_addPythonScript(id='IngestionFile_testEvent')
    self.portal.IngestionFile_testEvent.write(python_script_src)
    transaction.commit()
    self.tic()

  def setUpMimeType(self):
    portal_categories = self.portal.portal_categories
    if getattr(portal_categories, 'mime_type', None) is None:
      mime_type = portal_categories.newContent(portal_type='Base Category',
                                               id='mime_type')
      text = mime_type.newContent(portal_type='Category', id='text')
      text.newContent(portal_type='Category', id='html')
      transaction.commit()
      self.tic()

    if getattr(portal_categories, 'mime_type', None) is None:
      mime_type = portal_categories.newContent(portal_type='Base Category',
                                               id='mime_type')
      message = mime_type.newContent(portal_type='Category', id='message')
      message.newContent(portal_type='Category', id='rfc822')
      transaction.commit()
      self.tic()

  def setUpPredicate(self):
    portal_contribution_registry = self.portal.portal_contribution_registry
    if getattr(portal_contribution_registry, 'webpage_mimetype', None) is None:
      predicate = portal_contribution_registry.newContent(
        portal_type='Contribution Predicate',
        id='webpage_mimetype')
      predicate._setMembershipCriterionCategoryList(['mime_type/text/html'])
      predicate._setMembershipCriterionBaseCategoryList(['mime_type'])
      predicate.setDestinationPortalType('Web Page')
      transaction.commit()
      self.tic()

    if getattr(portal_contribution_registry, 'my_predicate', None) is None:
      predicate = portal_contribution_registry.newContent(
        portal_type='Contribution Predicate',
        id='my_predicate')
      predicate._setMembershipCriterionCategoryList(['mime_type/message/rfc822'])
      predicate._setMembershipCriterionBaseCategoryList(['mime_type'])
      predicate.setCriterion('file_extension', identity=['eml'])
      predicate.setDestinationPortalType('Mail Message')
      predicate.setTestMethodId('IngestionFile_testEvent')
      transaction.commit()
      self.tic()

  def testFindPortalTypeName(self, quiet=0, run=run_all_test):
    tool = self.portal.portal_contribution_registry

    # Test extension matching
    self.assertEqual(tool.findPortalTypeName(file_name='test.txt'), 'Text')
    self.assertEqual(tool.findPortalTypeName(file_name='test.odt'), 'Text')
    self.assertEqual(tool.findPortalTypeName(file_name='001.jpg'), 'Image')
    self.assertEqual(tool.findPortalTypeName(file_name='002.PNG'), 'Image')
    self.assertEqual(tool.findPortalTypeName(file_name='002.PNG'), 'Image')
    self.assertEqual(tool.findPortalTypeName(file_name='index.html'), 'Web Page')
    # Unknown extension
    self.assertEqual(tool.findPortalTypeName(file_name='index.xxx'), 'File')

    # Test mimetype matching
    self.assertEqual(tool.findPortalTypeName(mime_type='text/html'), 'Web Page')

    # Unknown mimetype
    self.assertEqual(tool.findPortalTypeName(mime_type='application/octet-stream'), 'File')

    # Test both of extension and mimetype
    self.assertNotEqual(tool.findPortalTypeName(file_name='message.eml'),
                        'Mail Message')
    self.assertNotEqual(tool.findPortalTypeName(mime_type='message/rfc822'),
                        'Mail Message')
    self.assertEqual(tool.findPortalTypeName(file_name='message.eml',
                                             mime_type='message/rfc822'),
                     'Mail Message')

    # Test test script
    data = """\
Subject: Fax
"""
    self.assertEqual(tool.findPortalTypeName(file_name='message.eml',
                                             mime_type='message/rfc822',
                                             data=data),
                     'Fax Message')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestContributionRegistryTool))
  return suite
