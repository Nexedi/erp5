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

  def getBusinessTemplateList(self):
    """Tuple of Business Templates we need to install"""
    return ('erp5_base',
            'erp5_web',
            'erp5_ingestion_mysql_innodb_catalog',
            'erp5_core_proxy_field_legacy',
            'erp5_ingestion',
            'erp5_dms',
            'erp5_crm',
            'erp5_knowledge_pad',
            'erp5_jquery',
            'erp5_jquery_ui',
            'erp5_jquery_plugin_spinbtn',
            'erp5_jquery_plugin_jgraduate',
            'erp5_jquery_plugin_svgicon',
            'erp5_jquery_plugin_hotkey',
            'erp5_jquery_plugin_jquerybbq',
            'erp5_jquery_plugin_svg_editor',
            'erp5_jquery_plugin_sheet',
            'erp5_jquery_plugin_mbmenu',
            'erp5_jquery_plugin_jqchart',
            'erp5_jquery_plugin_colorpicker',
            'erp5_jquery_plugin_elastic',
            'erp5_jquery_plugin_wdcalendar',
            'erp5_jquery_sheet_editor',
            'erp5_xinha_editor',
            'erp5_svg_editor',
            'erp5_web_ung_core',
            'erp5_web_ung_theme',
            'erp5_web_ung_role')

  def beforeTearDown(self):
    person_module = self.getPersonModule()
    person_module.manage_delObjects(list(person_module.objectIds()))
    self.stepTic()

  def afterSetUp(self):
    person = self.portal.person_module.newContent(portal_type='Person',
                                                  reference="ung_user")
    assignment = person.newContent(portal_type='Assignment')
    assignment.setFunction("function/ung_user")
    assignment.open()
    self.stepTic()

  def testERP5Site_createNewWebDocumentAsAnonymous(self):
    """Test use script ERP5Site_createNewWebDocument as Anonymous User"""
    self.logout()
    self.assertRaises(Unauthorized,
                      self.portal.ERP5Site_createNewWebDocument,
                      ("web_page_template"))

  def testERP5Site_createNewWebDocumentWithUNGRole(self):
    """Test use script ERP5Site_createNewWebDocument when a erp5 user have role
    to create and edit document in UNG"""
    self.portal.portal_preferences.ung_preference.enable()
    self.login("ung_user")
    web_page = self.portal.portal_catalog.getResultValue(portal_type="Web Page")
    self.assertEquals(web_page, None)
    self.portal.ERP5Site_createNewWebDocument("web_page_template")
    self.stepTic()
    web_page = self.portal.portal_catalog.getResultValue(portal_type="Web Page")
    self.assertEquals(web_page.getReference(), "default-Web.Page.Reference")
    self.assertEquals(len(self.portal.web_page_module.searchFolder()), 1)

  def testShareDocument(self):
    """Test the document sharing between erp5 users"""
    person = self.portal.person_module.newContent(portal_type='Person',
                                                  reference="ung_user2",
                                                  first_name="Gabriel")
    assignment = person.newContent(portal_type='Assignment')
    assignment.setFunction("function/ung_user")
    assignment.open()
    self.stepTic()
    self.login("ung_user")
    self.portal.ERP5Site_createNewWebDocument("web_table_template")
    self.stepTic()
    web_table = self.portal.portal_catalog.getResultValue(portal_type="Web Table")
    web_table.setReference("share-Web.Table")
    self.stepTic()
    self.login("ung_user2")
    self.assertEquals(len(self.portal.web_page_module.searchFolder()), 0)
    ung_web_site = self.portal.web_site_module.ung
    web_table = ung_web_site.WebSection_userFollowUpWebPage("share-Web.Table")
    self.assertNotEquals(web_table.getFollowUpList(), [])
    self.login("ERP5TypeTestCase")
    self.assertEquals(web_table.getFollowUpValue().getFirstName(), "Gabriel")

  def testBase_updateCalendarEventListWithERP5User(self):
    """ Test script Base_updateCalendarEventList with erp5 user"""
    self.logout()
    self.assertEquals('{"events": []}',
                      self.portal.Base_updateCalendarEventList("list"))
    self.login("ung_user")
    event_list = json.loads(self.portal.Base_updateCalendarEventList("list"))
    self.assertEquals(event_list.get("events"), [])
    event = self.portal.event_module.newContent(portal_type="Note")
    event.setStartDate(DateTime())
    event.setStopDate(DateTime()+1)
    self.stepTic()
    event_dict = json.loads(self.portal.Base_updateCalendarEventList("list"))
    event_list = event_dict.get("events")
    self.assertEquals(event_list[0][-2], "Note")
    form_dict = dict(CalendarStartTime=DateTime().strftime("%m/%d/%Y %H:%M"),
                     CalendarEndTime=DateTime().strftime("%m/%d/%Y %H:%M"),
                     CalendarTitle="One Sample",
                     portal_type="Web Message")
    self.portal.REQUEST.form.update(form_dict)
    self.portal.Base_updateCalendarEventList("add")
    self.stepTic()
    web_message = self.portal.portal_catalog.getResultValue(portal_type="Web Message")
    self.assertEquals(web_message.getTitle(), "One Sample")
    self.portal.REQUEST.form.clear()
    form_dict = dict(CalendarStartTime=DateTime().strftime("%m/%d/%Y %H:%M"),
                     CalendarEndTime=DateTime().strftime("%m/%d/%Y %H:%M"),
                     title="Buy Coffee",
                     event_id=web_message.getId())
    self.portal.REQUEST.form.update(form_dict)
    self.portal.Base_updateCalendarEventList("update")
    self.stepTic()
    self.assertEquals(web_message.getTitle(), "Buy Coffee")
    self.portal.REQUEST.form.clear()
    form_dict = dict(title=web_message.getTitle(),
                     id=web_message.getId())
    self.portal.REQUEST.form.update(form_dict)
    self.portal.Base_updateCalendarEventList("remove")
    self.stepTic()
    web_message = self.portal.portal_catalog.getResultValue(portal_type="Web Message")
    self.assertEquals(web_message, None)
  
  def testERPSite_createUNGUser(self):
    """Test if is possible create one user as Anonymous user"""
    self.logout()
    form_dict = dict(firstname="My First Name",
                     lastname="My Last Name",
                     password="ung_password")
    self.portal.REQUEST.form.update(form_dict)
    self.portal.ERPSite_createUNGUser()
    self.stepTic()
    self.login("ERP5TypeTestCase")
    person = self.portal.portal_catalog.getResultValue(portal_type="Person")
    self.assertEquals(person.getLastName(), "My Last Name")
    self.assertEquals(person.getValidationState(), "validated")

  def testBase_getPreferencePathList(self):
    """Test if with a normal user the paths of preference objects are returned correctly"""
    self.logout()
    self.assertEquals(json.loads(self.portal.Base_getPreferencePathList()), None)
    self.login("ung_user")
    preference_dict = json.loads(self.portal.Base_getPreferencePathList())
    self.assertEquals(preference_dict["preference"], "portal_preferences/1")
