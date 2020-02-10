##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                     Vincent Pelletier <vincent@nexedi.com>
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
#from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFActivity.ActivityTool import ActivityTool
from Products.CMFActivity.Errors import ActivityPendingError

class TestCopySupport(ERP5TypeTestCase):
  """
    Test CopySupport methods
  """

  def getBusinessTemplateList(self):
    return ('erp5_base', )

  def getTitle(self):
    return "CopySupport"

  def afterSetUp(self):
    portal = self.portal = self.getPortalObject()
    self.organisation_module = portal.organisation_module
    self.person_module = portal.person_module

  def test_01_setIdConcurency(self):
    """
      Check that it is impossible to call setId when there are remaining
      operations from a previous setId call.
      Also, check that external relations are correctly updated.
    """
    organisation = self.organisation_module.newContent(
                     portal_type='Organisation')
    person = self.person_module.newContent(portal_type='Person',
               career_subordination_value=organisation)
    self.tic()
    self.assertEqual(0, len(self.portal.portal_activities.getMessageList()))
    self.assertTrue(person.getCareerSubordination().startswith('organisation_module'))
    self.assertTrue(person.getCareerSubordinationValue().aq_base is organisation.aq_base)
    # Try to rename: must work
    self.organisation_module.setId('new_organisation_module')
    self.commit()
    try:
      self.assertTrue(person.getCareerSubordination().startswith('organisation_module'))
      initial_activity_count = len(self.portal.portal_activities.getMessageList())
      self.assertNotEqual(0, initial_activity_count)
      # Try to rename again with pending activities: must raise
      self.assertRaises(ActivityPendingError, self.organisation_module.setId, 'organisation_module')
      self.commit()
      # Activity count must not have changed
      self.assertEqual(initial_activity_count, len(self.portal.portal_activities.getMessageList()))
      self.tic()
      # Check that external relation was updated
      self.assertTrue(person.getCareerSubordination().startswith('new_organisation_module'))
      self.assertTrue(person.getCareerSubordinationValue().aq_base is organisation.aq_base)
    except Exception:
      self.abort()
      raise
    finally:
      # Rename back to original name
      self.organisation_module.setId('organisation_module')
      self.tic()
    # Check that relation is back to what it was
    self.assertTrue(person.getCareerSubordination().startswith('organisation_module'))
    self.assertTrue(person.getCareerSubordinationValue().aq_base is organisation.aq_base)

  def test_02_unindexObjectDependency(self):
    person = self.portal.person_module.newContent(portal_type='Person',
                                                  address_city='Lille')
    self.tic()
    getPath = self.portal.portal_catalog.getpath
    address = person.default_address
    self.assertEqual(address.getPath(), getPath(address.getUid()))
    person.recursiveReindexObject()
    address.setId('old_address')
    self.tic()
    self.assertEqual(address.getPath(), getPath(address.getUid()))

  def test_03_unindexObjectGrouping(self):
    person = self.portal.person_module.newContent(portal_type='Person',
                                                  address_city='Lille',
                                                  email_text='foo@bar.com')
    self.tic()
    search_catalog = self.portal.portal_catalog.unrestrictedSearchResults
    uid_list = [person.getUid(),
                person.default_address.getUid(),
                person.default_email.getUid()]
    uid_list.sort()
    self.assertEqual(len(search_catalog(uid=uid_list)), len(uid_list))
    self.portal.person_module._delObject(person.getId())
    del person
    self.commit()
    self.assertEqual(len(search_catalog(uid=uid_list)), len(uid_list))
    activity_tool = self.portal.portal_activities
    self.assertEqual(len(activity_tool.getMessageList()), len(uid_list))

    ActivityTool_invokeGroup = ActivityTool.invokeGroup
    invokeGroup_list = []
    def invokeGroup(self, method_id, message_list, activity, merge_duplicate):
      invokeGroup_list.extend((method_id,
                               sorted(m.kw.get('uid') for m in message_list),
                               activity,
                               merge_duplicate))
      return ActivityTool_invokeGroup(self, method_id, message_list,
                                      activity, merge_duplicate)
    try:
      ActivityTool.invokeGroup = invokeGroup
      self.tic()
    finally:
      ActivityTool.invokeGroup = ActivityTool_invokeGroup
    self.assertEqual(invokeGroup_list,
      ['portal_catalog/uncatalogObjectList', uid_list, 'SQLQueue', False])
    self.assertEqual(len(search_catalog(uid=uid_list)), 0)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCopySupport))
  return suite
