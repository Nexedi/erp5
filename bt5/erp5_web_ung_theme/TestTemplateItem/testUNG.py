##############################################################################
#
# Copyright (c) 2002-2011 Nexedi SA and Contributors. All Rights Reserved.
#                         Gabriel M. Monnerat <gabriel@tiolive.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from DateTime import DateTime
import re
import json


class TestUNG(ERP5TypeTestCase):
  """
    UNG Test Case
  """

  def getTitle(self):
    return "UNG Tests"

  def getBusinessTemplateList(self):
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
            'erp5_web_ung_theme',)

  def afterSetUp(self):
    """Clean up form"""
    self.portal.REQUEST.form.clear()

  def assertCreateDocumentUsingTemplate(self, template, **kw):
    web_page_module = self.portal.web_page_module
    self.portal.ERP5Site_createNewWebDocument(template)
    self.stepTic()
    web_page_search = web_page_module.searchFolder(**kw)
    self.assertEquals(1, len(web_page_search))

  def getTitleListToBySubjectDomain(self):
    parent = self.portal.portal_domains.ung_domain.by_subject
    return [domain.getTitle() for domain in self.portal.WebPageModule_generateDomain(0, parent)]

  def testERP5Site_createNewWebDocument(self):
    """Test if the script creates the objects using Templates correctly"""
    web_page_module = self.portal.web_page_module
    self.assertCreateDocumentUsingTemplate("web_page_template",
                                           portal_type="Web Page",
                                           reference="default-Web.Page.Reference")
    self.assertCreateDocumentUsingTemplate("web_table_template",
                                           portal_type="Web Table",
                                           reference="default-Web.Table.Reference")
    self.assertCreateDocumentUsingTemplate("web_illustration_template",
                                           portal_type="Web Illustration",
                                           reference="default-Web.Illustration.Reference")

  def testWebPageModule_generateDomain(self):
    """Test if script WebPageModule_generateDomain generates the list of
    domains correctly"""
    web_page = self.portal.web_page_module.newContent(portal_type="Web Page")
    self.stepTic()
    title_list = self.getTitleListToBySubjectDomain()
    self.assertFalse("Ung" in title_list)
    web_page.setSubjectList("Ung")
    self.stepTic()
    # The script uses cache (short) to store the results
    self.portal.portal_caches.clearAllCache()
    title_list = self.getTitleListToBySubjectDomain()
    self.assertTrue("Ung" in title_list, title_list)

  def testBase_changeWorkflowState(self):
    """Test if script change the state of object correctly"""
    web_table = self.portal.web_page_module.newContent(portal_type="Web Table")
    web_table.Base_changeWorkflowState("publish_action")
    self.stepTic()
    self.assertEquals(web_table.getValidationState(), "published")
    web_table.Base_changeWorkflowState("reject_action")
    self.assertEquals(web_table.getValidationState(), "draft")

  def testWebPage_getUNGIcon(self):
    """Test if the paths are returned correctly"""
    web_page = self.portal.web_page_module.newContent(portal_type="Web Page")
    web_table = self.portal.web_page_module.newContent(portal_type="Web Table")
    web_illustration = self.portal.web_page_module.newContent(portal_type="Web Illustration")
    self.stepTic()
    self.assertEquals(web_page.WebPage_getUNGIcon(),
                      "<img src='ung_images/document.gif'/>")
    self.assertEquals(web_table.WebPage_getUNGIcon(),
                      "<img src='ung_images/table.jpg'/>")
    self.assertEquals(web_illustration.WebPage_getUNGIcon(),
                      "<img src='ung_images/svg.png'/>")

  def testWebSection_deleteObjectList(self):
    """Test if objects are deleted correctly"""
    web_page = self.portal.web_page_module.newContent(portal_type="Web Page")
    relative_url = web_page.getRelativeUrl()
    self.portal.REQUEST.set("uids", [web_page.getUid(),])
    self.stepTic()
    self.portal.WebSection_deleteObjectList()
    self.stepTic()
    self.assertEquals(web_page.getValidationState(), "deleted")
    self.portal.REQUEST.set("uids", [web_page.getUid(),])
    self.stepTic()
    self.portal.WebSection_deleteObjectList()
    self.stepTic()
    self.assertEquals(len(self.portal.portal_catalog(relative_url=relative_url)), 0)

  def testWebSection_userFollowUpWebPage(self):
    """Test if user is added in field Follow Up of Web Page"""
    web_page = self.portal.web_page_module.newContent(portal_type="Web Page")
    web_page.setReference("new.Web-Page")
    self.stepTic()
    portal = self.portal
    person = portal.person_module.newContent(portal_type='Person',
                                             reference="ung_new_user")
    assignment = person.newContent(portal_type='Assignment')
    assignment.open()
    person = portal.person_module.newContent(portal_type='Person',
                                             reference="ung_new_user2")
    assignment = person.newContent(portal_type='Assignment')
    assignment.open()
    self.stepTic()
    self.login("ung_new_user")
    self.portal.WebSection_userFollowUpWebPage("new.Web-Page")
    self.stepTic()
    self.login("ERP5TypeTestCase")
    self.assertEquals("ung_new_user", web_page.getFollowUpValue().getReference())
    self.login("ung_new_user2")
    self.portal.WebSection_userFollowUpWebPage("new.Web-Page")
    self.stepTic()
    self.login("ERP5TypeTestCase")
    reference_list = [user.getReference() for user in web_page.getFollowUpValueList()]
    self.assertEquals(["ung_new_user", "ung_new_user2"],
                      sorted(reference_list))

  def testWebSection_getGadgetPathList(self):
    """Validate the gadget list"""
    gadget_list = json.loads((self.portal.WebSection_getGadgetPathList()))
    for gadget in gadget_list:
      url = gadget.get("image_url").split("?")[0]
      url = url.replace("/default_image", "")
      catalog_result = self.portal.portal_catalog(relative_url=url)
      self.assertEquals(len(catalog_result), 1)
      self.assertEquals(catalog_result[0].getTitle(), gadget.get('title'))

  def testEventModule_createNewEvent(self):
    """Test if script creates correctly a new event"""
    portal = self.portal
    event_dict = dict(portal_type="Note",
                      title="Buy Phone",
                      event_text_content="testUNG Sample",
                      start_date_hour=11,
                      start_date_minute=12,
                      start_date_day=12,
                      start_date_month=02,
                      start_date_year=2011,
                      stop_date_hour=12,
                      stop_date_minute=12,
                      stop_date_day=13,
                      stop_date_month=02,
                      stop_date_year=2011)
    portal.REQUEST.form.update(event_dict)
    portal.event_module.EventModule_createNewEvent()
    self.stepTic()
    event = portal.portal_catalog.getResultValue(portal_type="Note")
    self.assertEquals(event.getDescription(), "testUNG Sample")
    start_date = event.getStartDate()
    self.assertEquals(start_date.month(), 2)
    self.assertEquals(start_date.minute(), 12)

  def testWebPage_setSubjectList(self):
    """Test if string is inserted as subjects in object correctly"""
    web_table = self.portal.web_page_module.newContent(portal_type="Web Table")
    self.stepTic()
    web_table.WebPage_setSubjectList("VPN")
    self.stepTic()
    subject_list = web_table.getSubjectList()
    self.assertEquals(["VPN"], subject_list)
    web_table.WebPage_setSubjectList("VPN,ERP5")
    self.stepTic()
    subject_list = web_table.getSubjectList()
    self.assertEquals(["ERP5", "VPN"], sorted(subject_list))

  def testWebSection_getDocumentUrl(self):
    """Test if script used to generated custom url to listbox works
    correctly"""
    web_illustration = self.portal.web_page_module.newContent(portal_type="Web Illustration")
    web_page = self.portal.web_page_module.newContent(portal_type="Web Page")
    self.stepTic()
    kw = dict(brain=web_illustration)
    url = self.portal.WebSection_getDocumentUrl(**kw)
    pattern = "^http.*\/web_page_module\/[0-9]+\/WebIllustration_viewEditor\?editable_mode\:int\=1"
    self.assertNotEquals(re.search(pattern, url), None)
    kw = dict(brain=web_page)
    url = self.portal.WebSection_getDocumentUrl(**kw)
    pattern = "^http.*\/web_page_module\/[0-9]+\/WebPage_viewEditor\?editable_mode\:int\=1"
    self.assertNotEquals(re.search(pattern, url), None, url)
 
  def testBase_updateCalendarEventList(self):
    """Test script used to manage events in UNG Calendar """
    event_dict = json.loads(self.portal.Base_updateCalendarEventList("list"))
    self.assertEquals(event_dict.get("events"), [])
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
    """Test if script creates an user correctly"""
    form_dict = dict(firstname="UNG",
                     lastname="User",
                     email="g@g.com",
                     password="ung_password",
                     login_name="ung_user")
    self.portal.REQUEST.form.update(form_dict)
    response = json.loads(self.portal.ERPSite_createUNGUser())
    self.assertTrue(response)
    self.stepTic()
    person = self.portal.portal_catalog.getResultValue(portal_type="Person",
                                                       first_name="UNG")
    self.assertEquals(person.getLastName(), "User")
    self.assertEquals(person.getValidationState(), "validated")
    self.assertEquals(person.getEmail().getPortalType(), "Email")
    self.assertEquals(person.getEmailText(), "g@g.com")
    self.assertEquals(person.getReference(), "ung_user")
    response = json.loads(self.portal.ERPSite_createUNGUser())
    self.assertEquals(response, None)

  def testERP5Site_getUserValidationState(self):
    """Test script ERP5Site_getUserValidationState"""
    portal = self.portal
    form_dict = dict(firstname="UNG",
                     lastname="User",
                     email="g@g.com",
                     login_name="ung_reference")
    portal.REQUEST.form.update(form_dict)
    portal.ERPSite_createUNGUser()
    kw = dict(first_name=form_dict["firstname"],
              last_name=form_dict["lastname"],
              reference=form_dict["login_name"],
             )
    response = json.loads(portal.ERP5Site_getUserValidationState(**kw))
    self.assertEquals(response.get("response"), False)
    self.stepTic()
    response = json.loads(portal.ERP5Site_getUserValidationState(**kw))
    self.assertEquals(response.get("response"), True)
    kw = dict(first_name="Not Exist",
              reference="no_reference",
             )
    response = json.loads(portal.ERP5Site_getUserValidationState(**kw))
    self.assertEquals(response.get("response"), False)
    self.login("ung_reference")
    user = portal.ERP5Site_getAuthenticatedMemberPersonValue()
    self.assertEquals(user.getFirstName(), "UNG")

  def testWebSection_addGadget(self):
    """Test if gadgets are added correctly"""
    obj = self.portal.knowledge_pad_module.newContent(portal_type="Knowledge Pad")
    obj.edit(publication_section_value=self.portal.web_site_module.ung)
    obj.visible()
    self.stepTic()
    gadget = self.portal.portal_gadgets.searchFolder()[0]
    gadget_id = gadget.getId()
    self.portal.web_site_module.ung.WebSection_addGadget(gadget_id)
    self.stepTic()
    gadget = self.portal.portal_catalog.getResultValue(portal_type="Gadget",
                                                       validation_state="visible")
    self.assertEquals(gadget_id, gadget.getId())