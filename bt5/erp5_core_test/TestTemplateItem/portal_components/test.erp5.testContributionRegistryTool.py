# -*- coding: utf-8 -*-
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

class TestContributionRegistryTool(ERP5TypeTestCase):

  run_all_test = 1

  def getTitle(self):
    return "Contribution Registry Tool"

  def getBusinessTemplateList(self):
    return ('erp5_base',)

  def afterSetUp(self):
    self.setUpTestScript()
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

event = context.newContent(temp_object=True, portal_type='Event',
                           id='subobject', data=context.getData())

subject = event.getContentInformation().get('Subject', None)
if subject == 'Fax':
  return 'Fax Message'
return predicate.getDestinationPortalType()
""")
    self.portal.manage_addProduct['PythonScripts'].manage_addPythonScript(id='IngestionFile_testEvent')
    self.portal.IngestionFile_testEvent.write(python_script_src)
    self.tic()

  def setUpPredicate(self):
    portal_contribution_registry = self.portal.portal_contribution_registry

    predicate_id = 'webpage_by_content_type'
    if getattr(portal_contribution_registry, predicate_id, None) is None:
      predicate = portal_contribution_registry.newContent(
        portal_type='Contribution Predicate',
        id=predicate_id)
      predicate.setCriterion('content_type', identity=['text/html'])
      predicate.setDestinationPortalType('Web Page')
      self.tic()

    predicate_id = 'webpage_by_extension'
    if getattr(portal_contribution_registry, predicate_id, None) is None:
      predicate = portal_contribution_registry.newContent(
        portal_type='Contribution Predicate',
        id=predicate_id)
      predicate.setCriterion('extension_from_filename', identity=['html'])
      predicate.setDestinationPortalType('Web Page')
      self.tic()

    predicate_id = 'email_by_extension_and_content_type'
    if getattr(portal_contribution_registry, predicate_id, None) is None:
      predicate = portal_contribution_registry.newContent(
        portal_type='Contribution Predicate',
        id=predicate_id)
      predicate.setCriterion('extension_from_filename', identity=['eml'])
      predicate.setCriterion('content_type', identity=['message/rfc822'])
      predicate.setDestinationPortalType('Mail Message')
      predicate.setTestMethodId('IngestionFile_testEvent')
      self.tic()

    predicate_id = 'text_by_extension'
    if getattr(portal_contribution_registry, predicate_id, None) is None:
      predicate = portal_contribution_registry.newContent(
        portal_type='Contribution Predicate',
        id=predicate_id)
      predicate.setCriterion('extension_from_filename', identity=['odt', 'txt'])
      predicate.setDestinationPortalType('Text')
      self.tic()

    predicate_id = 'image_by_extension'
    if getattr(portal_contribution_registry, predicate_id, None) is None:
      predicate = portal_contribution_registry.newContent(
        portal_type='Contribution Predicate',
        id=predicate_id)
      predicate.setCriterion('extension_from_filename', identity=['jpg', 'png'])
      predicate.setDestinationPortalType('Image')
      self.tic()

  def testFindPortalTypeName(self, quiet=0, run=run_all_test):
    tool = self.portal.portal_contribution_registry

    # Test extension matching
    self.assertEqual(tool.findPortalTypeName(filename='test.txt'), 'Text')
    self.assertEqual(tool.findPortalTypeName(filename='test.odt'), 'Text')
    self.assertEqual(tool.findPortalTypeName(filename='001.jpg'), 'Image')
    self.assertEqual(tool.findPortalTypeName(filename='002.png'), 'Image')
    self.assertEqual(tool.findPortalTypeName(filename='002.PNG'), 'Image')
    self.assertEqual(tool.findPortalTypeName(filename='index.html'), 'Web Page')
    # Unknown extension
    self.assertEqual(tool.findPortalTypeName(filename='index.xxx'), 'File')

    # Test mimetype matching
    self.assertEqual(tool.findPortalTypeName(content_type='text/html'), 'Web Page')

    # Unknown mimetype
    self.assertEqual(tool.findPortalTypeName(content_type='application/octet-stream'), 'File')

    # Test both of extension and mimetype
    self.assertNotEqual(tool.findPortalTypeName(filename='message.eml'),
                        'Mail Message')
    self.assertNotEqual(tool.findPortalTypeName(content_type='message/rfc822'),
                        'Mail Message')
    self.assertEqual(tool.findPortalTypeName(filename='message.eml',
                                             content_type='message/rfc822'),
                     'Mail Message')

    # Test test script
    data = b"""\
Subject: Fax
"""
    self.assertEqual(tool.findPortalTypeName(filename='message.eml',
                                             content_type='message/rfc822',
                                             data=data),
                     'Fax Message')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestContributionRegistryTool))
  return suite
