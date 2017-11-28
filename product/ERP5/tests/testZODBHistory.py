# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Nexedi KK and Contributors. All Rights Reserved.
#                    Tatuya Kamada <tatuya@nexedi.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestZODBHistory(ERP5TypeTestCase):
  """
    Test ZODBHistory Extension
  """

  def getTitle(self):
    return "ZODB History Test"

  def getBusinessTemplateList(self):
    """ return business template list """
    return ('erp5_base',)

  def afterSetUp(self):
    """ AfterSetup """
    self.addPreferenceForZODBHistory()
    self.setUpUser()
    self.tic()

  def addPreferenceForZODBHistory(self):
    """ Add a preference for ZODB History """
    preference_tool = self.portal.portal_preferences
    preference = getattr(preference_tool, "zodb_history_test_preference", None)
    if preference is None:
      preference = preference_tool.newContent(id="zodb_history_test_preference",
                                              portal_type="Preference")
    if preference.getPreferenceState() != "enabled":
       preference.enable()

  def addOrganisation(self, organisation_id):
    """ Add an organisation """
    org = self.portal.organisation_module.newContent(id=organisation_id,
                                               portal_type='Organisation')
    self.commit()
    return org

  def setUpUser(self):
    """ Set up a user to test normal users can use this function. """
    self.addUser('tatuya')

  def addUser(self, user_name, role=['Member', 'Owner', 'Assignor']):
    """ Create a test user."""
    uf = self.portal.acl_users
    if not uf.getUserById(user_name):
      uf._doAddUser(user_name, '', role, [])

  def _clearCache(self):
    """ Clear cache to validate the preference modification. """
    self.portal.portal_caches.clearCache(
      cache_factory_list=('erp5_ui_short', # for preference cache
                          ))

  def test_01_testZODBHistory(self):
    """
     Make sure the very basic function that is possible to test in unittest.
     TODO: The details should be tested in a functional test.
    """
    self.loginByUserName('tatuya')
    org = self.addOrganisation('org')
    history_list = org.Base_getZODBChangeHistoryList(org)
    self.assertTrue(len(history_list) > 0)
    d = history_list[0]
    changes = d['changes']
    self.assertEqual(changes['portal_type'], 'Organisation')
    self.assertEqual(changes['id'], 'org')
    self.assertTrue(changes['uid'] is not None)

  def test_02_testZODBHistoryPreference(self):
    """
     Make sure the preference of zodb history size.
    """
    self.loginByUserName('tatuya')
    org2 = self.addOrganisation('org2')
    for i in range(60):
      org2.edit(title='org%d' % i)
      self.commit()
    history_list = org2.Base_getZODBHistoryList()
    preference = getattr(self.getPreferenceTool(),
                         'zodb_history_test_preference')
    # by default the history size is limited recent 50
    self.assertEqual(preference.getPreferredHtmlStyleZodbHistorySize(), 50)
    self.assertEqual(len(history_list), 50)

    # changes the limit to 100
    preference.setPreferredHtmlStyleZodbHistorySize(100)
    self._clearCache()
    self.assertEqual(preference.getPreferredHtmlStyleZodbHistorySize(), 100)
    history_list = org2.Base_getZODBHistoryList()
    # Now that the limit is 100, thus the history page show the all history
    # should be: create(1) + edit(60) = 61
    self.assertEqual(len(history_list), 61)

  def test_ZODBHistorySecurity(self):
    """
     Make sure ZODB History is not available when user does not have "View History" permission.
    """
    self.loginByUserName('tatuya')
    document = self.addOrganisation('document')

    # by default, users have a link to view ZODB history in history tab
    self.assertIn(
        'your_zodb_history',
        [field.getId() for field in document.Base_viewHistory.get_fields()])

    # when user does not have "View History" permission, the link is not displayed
    document.manage_permission('View History', [], 0)
    self.assertNotIn(
        'your_zodb_history',
        [field.getId() for field in document.Base_viewHistory.get_fields()])

    # accessing the form directly is not allowed either
    from zExceptions import Unauthorized
    self.assertRaises(Unauthorized, document.Base_viewZODBHistory)

  def test_ZODBHistoryBinaryData(self):
    """
     Make sure ZODB History view works with binary content
    """
    self.loginByUserName('tatuya')
    document = self.addOrganisation(self.id()).newContent(
        portal_type='Embedded File')

    document.setFile(
        open(os.path.join(
          os.path.dirname(__file__),
          'test_data',
          'images',
          'erp5_logo.png')))
    document.setTitle("ロゴ")
    self.commit()

    # no encoding error
    document.Base_viewZODBHistory()

    change, = document.Base_getZODBHistoryList()
    self.assertIn('data:(binary)', change.getProperty('changes'))
    self.assertIn('content_type:image/png', change.getProperty('changes'))
    self.assertIn('title:ロゴ', change.getProperty('changes'))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestZODBHistory))
  return suite
