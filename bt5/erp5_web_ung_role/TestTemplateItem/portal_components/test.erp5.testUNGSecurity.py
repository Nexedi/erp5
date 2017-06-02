##############################################################################
#
# Copyright (c) 2002-2011 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc. 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################


from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from zExceptions import Unauthorized
from DateTime import DateTime
import json


class TestUNGSecurity(ERP5TypeTestCase):
  """Test Suite to validate all cases of permissions in UNG"""

  def getTitle(self):
    return "Test UNG Security"

  def beforeTearDown(self):
    self.abort()
    self.tic()
    person_module = self.getPersonModule()
    person_module.manage_delObjects(list(person_module.objectIds()))
    self.tic()

  def afterSetUp(self):
    if self.portal.portal_preferences.ung_preference.getPreferenceState() != "global":
      self.portal.portal_preferences.ung_preference.enable()
    person = self.portal.person_module.newContent(portal_type='Person',
                                                  reference="ung_user")
    assignment = person.newContent(portal_type='Assignment')
    assignment.setFunction("function/ung_user")
    assignment.open()
    login = person.newContent(
      portal_type='ERP5 Login',
      reference='ung_user',
    )
    login.validate()
    self.tic()

  def testERP5Site_createNewWebDocumentAsAnonymous(self):
    """Test use script ERP5Site_createNewWebDocument as Anonymous User"""
    self.logout()
    self.changeSkin("UNGDoc")
    self.assertRaises(Unauthorized,
                      self.portal.ERP5Site_createNewWebDocument,
                      ("web_page_template"))

  def testERP5Site_createNewWebDocumentWithUNGRole(self):
    """Test use script ERP5Site_createNewWebDocument when a erp5 user have role
    to create and edit document in UNG"""
    self.loginByUserName("ung_user")
    web_page = self.portal.portal_catalog.getResultValue(portal_type="Web Page")
    self.assertEqual(web_page, None)
    self.changeSkin("UNGDoc")
    self.portal.ERP5Site_createNewWebDocument("web_page_template")
    self.tic()
    web_page = self.portal.portal_catalog.getResultValue(portal_type="Web Page")
    self.assertEqual(web_page.getReference(), "default-Web.Page.Reference")
    self.assertEqual(len(self.portal.web_page_module.searchFolder()), 1)

  def testShareDocument(self):
    """Test the document sharing between erp5 users"""
    person = self.portal.person_module.newContent(portal_type='Person',
                                                  reference="ung_user2",
                                                  first_name="Gabriel")
    assignment = person.newContent(portal_type='Assignment')
    assignment.setFunction("function/ung_user")
    assignment.open()
    login = person.newContent(
      portal_type='ERP5 Login',
      reference='ung_user2',
    )
    login.validate()
    self.tic()
    self.loginByUserName("ung_user")
    self.changeSkin("UNGDoc")
    self.portal.ERP5Site_createNewWebDocument("web_table_template")
    self.tic()
    web_table = self.portal.portal_catalog.getResultValue(portal_type="Web Table")
    web_table.setReference("share-Web.Table")
    self.tic()
    self.loginByUserName("ung_user2")
    self.assertEqual(len(self.portal.web_page_module.searchFolder()), 0)
    ung_web_site = self.portal.web_site_module.ung
    self.changeSkin("UNGDoc")
    web_table = ung_web_site.ERP5Site_userFollowUpWebPage("share-Web.Table")
    self.tic()
    self.assertNotEquals(web_table.getFollowUpList(), [])
    self.assertEqual(len(self.portal.web_page_module.searchFolder()), 1)
    web_table = self.portal.web_page_module.searchFolder()[0]
    self.assertEqual(web_table.getPortalType(), "Web Table")
    self.login("ERP5TypeTestCase")
    self.assertEqual(web_table.getFollowUpValue().getFirstName(), "Gabriel")

  def testBase_updateCalendarEventListWithERP5User(self):
    """ Test script Base_updateCalendarEventList with erp5 user"""
    self.logout()
    self.changeSkin("UNGDoc")
    self.assertEqual('{"events": []}',
                      self.portal.Base_updateCalendarEventList("list"))
    self.loginByUserName("ung_user")
    self.changeSkin("UNGDoc")
    event_list = json.loads(self.portal.Base_updateCalendarEventList("list"))
    self.assertEqual(event_list.get("events"), [])
    event = self.portal.event_module.newContent(portal_type="Note")
    event.setStartDate(DateTime())
    event.setStopDate(DateTime()+1)
    self.tic()
    self.changeSkin("UNGDoc")
    event_dict = json.loads(self.portal.Base_updateCalendarEventList("list"))
    event_list = event_dict.get("events")
    self.assertEqual(event_list[0][-2], "Note")
    form_dict = dict(CalendarStartTime=DateTime().strftime("%m/%d/%Y %H:%M"),
                     CalendarEndTime=DateTime().strftime("%m/%d/%Y %H:%M"),
                     CalendarTitle="One Sample",
                     portal_type="Web Message")
    self.portal.REQUEST.form.update(form_dict)
    self.changeSkin("UNGDoc")
    self.portal.Base_updateCalendarEventList("add")
    self.tic()
    web_message = self.portal.portal_catalog.getResultValue(portal_type="Web Message")
    self.assertEqual(web_message.getTitle(), "One Sample")
    self.portal.REQUEST.form.clear()
    form_dict = dict(CalendarStartTime=DateTime().strftime("%m/%d/%Y %H:%M"),
                     CalendarEndTime=DateTime().strftime("%m/%d/%Y %H:%M"),
                     title="Buy Coffee",
                     event_id=web_message.getId())
    self.portal.REQUEST.form.update(form_dict)
    self.changeSkin("UNGDoc")
    self.portal.Base_updateCalendarEventList("update")
    self.tic()
    self.assertEqual(web_message.getTitle(), "Buy Coffee")
    self.portal.REQUEST.form.clear()
    form_dict = dict(title=web_message.getTitle(),
                     id=web_message.getId())
    self.portal.REQUEST.form.update(form_dict)
    self.changeSkin("UNGDoc")
    self.portal.Base_updateCalendarEventList("remove")
    self.tic()
    web_message = self.portal.portal_catalog.getResultValue(portal_type="Web Message")
    self.assertEqual(web_message, None)
  
  def testERPSite_createUNGUser(self):
    """Test if is possible create one user as Anonymous user"""
    self.logout()
    form_dict = dict(firstname="My First Name",
                     lastname="My Last Name",
                     password="ung_password",
                     login_name=self.id(),
    )
    self.portal.REQUEST.form.update(form_dict)
    self.changeSkin("UNGDoc")
    self.portal.ERPSite_createUNGUser()
    self.tic()
    self.login("ERP5TypeTestCase")
    person = self.portal.portal_catalog.getResultValue(portal_type="Person")
    self.assertEqual(person.getLastName(), "My Last Name")
    self.assertEqual(person.getValidationState(), "validated")

  def testBase_getPreferencePathList(self):
    """Test if with normal user the paths of preference objects are returned correctly"""
    person = self.portal.person_module.newContent(portal_type='Person',
                                                  reference="ung_user2")
    assignment = person.newContent(portal_type='Assignment')
    assignment.setFunction("function/ung_user")
    assignment.open()
    login = person.newContent(
      portal_type='ERP5 Login',
      reference='ung_user2',
    )
    login.validate()
    self.tic()
    self.loginByUserName("ung_user")
    self.changeSkin("UNGDoc")
    preference_dict = json.loads(self.portal.Base_getPreferencePathList())
    self.assertEqual(preference_dict, {u'preference': u'portal_preferences/1'})
    self.loginByUserName("ung_user2")
    self.changeSkin("UNGDoc")
    preference_dict = json.loads(self.portal.Base_getPreferencePathList())
    self.assertEqual(preference_dict, {u'preference': u'portal_preferences/2'})
  
  def testWebPage_shareDocument(self):
    """ """
    self.loginByUserName("ung_user")
    self.changeSkin("UNGDoc")
    self.portal.ERP5Site_createNewWebDocument("web_page_template")
    self.tic()
    web_page = self.portal.portal_catalog.getResultValue(portal_type="Web Page")
    self.assertEqual(web_page.getValidationState(), "draft")
    self.changeSkin("UNGDoc")
    response = web_page.WebPage_shareDocument()
    self.tic()
    self.assertEqual(response, "".join((self.portal.absolute_url(),
                                         "/?key=",
                                         web_page.getReference())))
    self.assertEqual(web_page.getValidationState(), "shared")
