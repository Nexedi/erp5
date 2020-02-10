##############################################################################
#
# Copyright (c) 2013 Nexedi KK and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestAccessTab(ERP5TypeTestCase):
  def getTitle(self):
    return "Access Tab Test"

  def afterSetUp(self):
    """ AfterSetup """
    self.addPreferenceForAccessTab()
    self.configureBusinessApplication()
    self.tic()

  def addPreferenceForAccessTab(self):
    """ Add a preference for access tab """
    preference_tool = self.portal.portal_preferences
    preference = getattr(preference_tool, "access_tab_test_preference", None)
    if preference is None:
      preference = preference_tool.newContent(id="access_tab_test_preference",
                                              portal_type="Preference")
    preference.setPreferredHtmlStyleAccessTab(True)
    if preference.getPreferenceState() != "enabled":
      preference.enable()

  def configureBusinessApplication(self):
    """ Configure business_application category on module property.
    This is mandatory for access_tab."""
    business_application = self.portal.portal_categories.business_application
    base = getattr(business_application, 'base', None)
    if base is None:
      base = self.portal.portal_categories.business_application.newContent(
                portal_type='Category',
                id='base',
                title='base')
    self.portal.organisation_module.setBusinessApplicationValue(base)
    self.portal.person_module.setBusinessApplicationValue(base)
    self.tic()

  def enableAccessTab(self):
    """ make enable access tab """
    portal = self.portal
    preference = portal.portal_preferences.access_tab_test_preference
    preference.setPreferredHtmlStyleAccessTab(True)
    self.tic()

  def checkSelectedTabDict(self):
    """ Check a script which is used in access tab view """
    tab_info = self.portal.ERP5Site_getSelectedTab()
    expected_tab_info = {'title': 'Browse',
                         'renderer': 'ERP5Site_renderViewActionList',
                         'id': 'browse_tab',
                         'icon': 'tab_icon/list.png'}
    self.assertEqual(tab_info, expected_tab_info)

  def checkStatusDict(self):
    """ Check a script which is used in access tab view """
    status_dict = self.portal.ERP5Site_getConfiguredStatusDict()
    expected_status_dict = {'express_mode': 'support_disabled',
                            'dms_mode': False,
                            'basic_mode': True}
    self.assertEqual(status_dict, expected_status_dict)

  def checkInformationDictBasic(self):
    """ Check a script which is used in the main part in access tab view """
    portal = self.portal
    info_dict = portal.ERP5Site_getCategorizedModuleActionInformationDict()
    view_list = info_dict['view']

    self.assertEqual(len(view_list), 1)
    self.assertEqual(len(view_list[0]), 2)

    base = view_list[0]
    (label, menu_list) = base
    self.assertEqual(label, 'base')
    self.assertEqual(len(menu_list), 2)
    organisation_menu = menu_list[0]
    person_menu = menu_list[1]

    self.assertEqual(len(organisation_menu), 2)
    self.assertEqual(type(organisation_menu), tuple)
    self.assertEqual(len(person_menu), 2)
    self.assertEqual(type(person_menu), tuple)

    (organisation_label, _) = organisation_menu
    (person_label, _) = person_menu
    self.assertEqual(organisation_label, 'Organisations')
    self.assertEqual(person_label, 'Persons')

  def addCurrencyModuleIntoAccessTab(self):
    """ add currency module into access tab page so that we can
    recognise existing cache is not used """
    base = self.portal.portal_categories.business_application.base
    self.portal.currency_module.setBusinessApplicationValue(base)
    self.tic()

  def checkInformationDictAfterSwitchingServerUrl(self):
    """ Check a script which is used in the main part in access tab view """
    # simulate a https access with '127.0.0.1' address
    request=self.portal.REQUEST
    request.setServerURL(protocol='https', hostname='127.0.0.1')
    portal = self.getPortal()

    # make sure that existing cache is not used because the server_url is
    # different when the view is cached.
    info_dict = portal.ERP5Site_getCategorizedModuleActionInformationDict()
    view_list = info_dict['view']
    self.assertEqual(len(view_list), 1)
    self.assertEqual(len(view_list[0]), 2)

    base = view_list[0]
    (_, menu_list) = base
    self.assertEqual(len(menu_list), 3)
    currency_menu = menu_list[0]

    self.assertEqual(len(currency_menu), 2)
    self.assertEqual(type(currency_menu), tuple)

    (currency_label, currency_url) = currency_menu
    self.assertEqual(currency_label, 'Currencies')
    self.assertTrue('https' in currency_url[0][1])

  def test_01_testAccessTab(self):
    """
     Test the basic functionalities of Access Tab.

     [setup]
     - enable accesstab flag on a preference
     - configure 'business_application' category at module property

     [test]
     - check access tab is usable
    """
    self.enableAccessTab()
    self.checkSelectedTabDict()
    self.checkStatusDict()
    self.checkInformationDictBasic()

  def test_02_testAccessTabCacheAfterSwitchingUrl(self):
    """
      Check that when access url is changed, exisiting access tab cache is
      not used.
      The view is cached with CachingMethod by (user, language and server_url)
    """
    self.enableAccessTab()
    self.checkInformationDictBasic()
    self.addCurrencyModuleIntoAccessTab()
    self.checkInformationDictAfterSwitchingServerUrl()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAccessTab))
  return suite
