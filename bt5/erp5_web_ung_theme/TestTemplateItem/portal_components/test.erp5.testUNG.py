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
from Products.ERP5Type.tests.utils import FileUpload
from DateTime import DateTime
import os.path
import Products.ERP5.tests
import re
import json


class TestUNG(ERP5TypeTestCase):
  """
    UNG Test Case
  """

  def getTitle(self):
    return "UNG Tests"

  def afterSetUp(self):
    """Clean up form"""
    self.portal.REQUEST.form.clear()

  def getDocumentPath(self):
    """ It returns a full path of document """
    folder_path = os.path.dirname(Products.ERP5.tests.__file__)
    filename = "tiolive-ERP5.Freedom.TioLive.Spreadsheet-001-en.ods"
    return os.path.join(folder_path,
                        "test_data",
                        filename), filename

  def assertCreateDocumentUsingTemplate(self, template, **kw):
    web_page_module = self.portal.web_page_module
    self.changeSkin("UNGDoc")
    self.portal.ERP5Site_createNewWebDocument(template)
    self.tic()
    web_page_search = web_page_module.searchFolder(**kw)
    self.assertEqual(1, len(web_page_search))

  def getTitleListToBySubjectDomain(self):
    parent = self.portal.portal_domains.ung_domain.by_subject
    self.changeSkin("UNGDoc")
    return [domain.getTitle() for domain in self.portal.ERP5Site_generateDomain(0, parent)]

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

  def testERP5Site_generateDomain(self):
    """Test if script ERP5Site_generateDomain generates the list of
    domains correctly"""
    self.changeSkin('UNGDoc')
    web_page = self.portal.web_page_module.newContent(portal_type="Web Page")
    self.tic()
    title_list = self.getTitleListToBySubjectDomain()
    self.assertFalse("Ung" in title_list)
    web_page.setSubjectList("Ung")
    self.tic()
    # The script uses cache (short) to store the results
    self.portal.portal_caches.clearAllCache()
    title_list = self.getTitleListToBySubjectDomain()
    self.assertTrue("Ung" in title_list, title_list)

  def testBase_changeWorkflowState(self):
    """Test if script change the state of object correctly"""
    self.changeSkin('UNGDoc')
    web_table = self.portal.web_page_module.newContent(portal_type="Web Table")
    web_table.Base_changeWorkflowState("publish_action")
    self.tic()
    self.assertEqual(web_table.getValidationState(), "published")
    self.changeSkin("UNGDoc")
    web_table.Base_changeWorkflowState("reject_action")
    self.assertEqual(web_table.getValidationState(), "draft")

  def testWebPage_getUNGIcon(self):
    """Test if the paths are returned correctly"""
    web_page = self.portal.web_page_module.newContent(portal_type="Web Page")
    web_table = self.portal.web_page_module.newContent(portal_type="Web Table")
    web_illustration = self.portal.web_page_module.newContent(portal_type="Web Illustration")
    self.tic()
    self.changeSkin("UNGDoc")
    self.assertEqual(web_page.WebPage_getUNGIcon(),
                      "<img src='ung_images/document.gif'/>")
    self.assertEqual(web_table.WebPage_getUNGIcon(),
                      "<img src='ung_images/table.jpg'/>")
    self.assertEqual(web_illustration.WebPage_getUNGIcon(),
                      "<img src='ung_images/svg.png'/>")

  def testERP5Site_userFollowUpWebPage(self):
    """Test if user is added in field Follow Up of Web Page"""
    self.changeSkin('UNGDoc')
    web_page = self.portal.web_page_module.newContent(portal_type="Web Page")
    web_page.setReference("new.Web-Page")
    self.tic()
    portal = self.portal
    person = portal.person_module.newContent(portal_type='Person',
                                             reference="ung_new_user")
    assignment = person.newContent(portal_type='Assignment')
    assignment.open()
    person.newContent(portal_type='ERP5 Login', reference=person.getReference()).validate()
    person = portal.person_module.newContent(portal_type='Person',
                                             reference="ung_new_user2")
    assignment = person.newContent(portal_type='Assignment')
    assignment.open()
    person.newContent(portal_type='ERP5 Login', reference=person.getReference()).validate()
    self.tic()
    self.loginByUserName("ung_new_user")
    self.changeSkin("UNGDoc")
    self.portal.ERP5Site_userFollowUpWebPage("new.Web-Page")
    self.tic()
    self.login("ERP5TypeTestCase")
    self.assertEqual("ung_new_user", web_page.getFollowUpValue().getReference())
    self.loginByUserName("ung_new_user2")
    self.changeSkin("UNGDoc")
    self.portal.ERP5Site_userFollowUpWebPage("new.Web-Page")
    self.tic()
    self.login("ERP5TypeTestCase")
    reference_list = [user.getReference() for user in web_page.getFollowUpValueList()]
    self.assertEqual(["ung_new_user", "ung_new_user2"],
                      sorted(reference_list))

  def testWebSection_getGadgetPathList(self):
    """Validate the gadget list"""
    self.changeSkin("UNGDoc")
    gadget_list = json.loads((self.portal.WebSection_getGadgetPathList()))
    for gadget in gadget_list:
      url = gadget.get("image_url").split("?")[0]
      url = url.replace("/default_image", "")
      catalog_result = self.portal.portal_catalog(relative_url=url)
      self.assertEqual(len(catalog_result), 1)
      self.assertEqual(catalog_result[0].getTitle(), gadget.get('title'))

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
    self.changeSkin("UNGDoc")
    portal.event_module.EventModule_createNewEvent()
    self.tic()
    event = portal.portal_catalog.getResultValue(
      portal_type="Note",
      title='Buy Phone' )
    self.assertEqual(event.getDescription(), "testUNG Sample")
    start_date = event.getStartDate()
    self.assertEqual(start_date.month(), 2)
    self.assertEqual(start_date.minute(), 12)

  def testWebPage_setSubjectList(self):
    """Test if string is inserted as subjects in object correctly"""
    web_table = self.portal.web_page_module.newContent(portal_type="Web Table")
    self.tic()
    self.changeSkin("UNGDoc")
    web_table.WebPage_setSubjectList("VPN")
    self.tic()
    subject_list = web_table.getSubjectList()
    self.assertEqual(["VPN"], subject_list)
    self.changeSkin("UNGDoc")
    web_table.WebPage_setSubjectList("VPN,ERP5")
    self.tic()
    self.changeSkin("UNGDoc")
    subject_list = web_table.getSubjectList()
    self.assertEqual(["ERP5", "VPN"], sorted(subject_list))

  def testWebSection_getDocumentUrl(self):
    """Test if script used to generated custom url to listbox works
    correctly"""
    web_illustration = self.portal.web_page_module.newContent(portal_type="Web Illustration")
    web_page = self.portal.web_page_module.newContent(portal_type="Web Page")
    self.tic()
    kw = dict(brain=web_illustration)
    self.changeSkin('UNGDoc')
    url = self.portal.WebSection_getDocumentUrl(**kw)
    pattern = "^http.*\/web_page_module\/[0-9]+\?editable_mode\:int\=1"
    self.assertNotEquals(re.search(pattern, url), None)
    kw = dict(brain=web_page)
    url = self.portal.WebSection_getDocumentUrl(**kw)
    pattern = "^http.*\/web_page_module\/[0-9]+\?editable_mode\:int\=1"
    self.assertNotEquals(re.search(pattern, url), None, url)
 
  def testBase_updateCalendarEventList(self):
    """Test script used to manage events in UNG Calendar """
    self.changeSkin('UNGDoc')
    event_dict = json.loads(self.portal.Base_updateCalendarEventList("list"))
    self.assertEqual(event_dict.get("events"), [])
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
    form_dict["event_portal_type"] = "Note"
    self.portal.REQUEST.form.update(form_dict)
    self.changeSkin("UNGDoc")
    self.portal.Base_updateCalendarEventList("update")
    self.tic()
    web_message = self.portal.portal_catalog.getResultValue(portal_type="Web Message")
    self.assertEqual(web_message, None)
    note = self.portal.portal_catalog.getResultValue(portal_type="Note",
          title="Buy Coffee")
    self.assertEqual(note.getTitle(), "Buy Coffee")
    self.portal.REQUEST.form.clear()
    form_dict = dict(title=note.getTitle(),
                     id=note.getId())
    self.portal.REQUEST.form.update(form_dict)
    self.changeSkin("UNGDoc")
    self.portal.Base_updateCalendarEventList("remove")
    self.tic()
    note = self.portal.portal_catalog.getResultValue(portal_type="Note",
                                                     title="Buy Coffee")
    self.assertEqual(note, None)
    self.portal.REQUEST.form.clear()
    start_date = DateTime()
    end_date = DateTime() + 1
    form_dict = dict(CalendarStartTime=start_date.strftime("%m/%d/%Y %H:%M"),
                     CalendarEndTime=end_date.strftime("%m/%d/%Y %H:%M"),
                     CalendarTitle="Another Sample",
                     portal_type="Letter")
    self.portal.REQUEST.form.update(form_dict)
    self.changeSkin("UNGDoc")
    self.portal.Base_updateCalendarEventList("add")
    self.tic()
    letter = self.portal.portal_catalog.getResultValue(portal_type="Letter",
                                                       title="Another Sample")
    self.assertEqual(letter.getPortalType(), "Letter")
    self.assertEqual(letter.getTitle(), "Another Sample")
    self.assertEqual(letter.getStartDate().hour(), start_date.hour())
    self.assertEqual(letter.getStartDate().day(), start_date.day())
    self.assertEqual(letter.getStopDate().hour(), end_date.hour())
    self.assertEqual(letter.getStopDate().day(), end_date.day())
    self.portal.REQUEST.form.clear()
    form_dict = dict(title="Change only the Title of Sample",
                     event_id=letter.getId())
    self.portal.REQUEST.form.update(form_dict)
    self.changeSkin("UNGDoc")
    self.portal.Base_updateCalendarEventList("update")
    self.tic()
    letter = self.portal.portal_catalog.getResultValue(portal_type="Letter",
                                                       title="Another Sample")
    self.assertEqual(letter, None)
    letter = self.portal.portal_catalog.getResultValue(portal_type="Letter",
                                                       title="Change only the Title of Sample")
    self.assertEqual(letter.getStartDate().hour(), start_date.hour())
    self.assertEqual(letter.getStartDate().day(), start_date.day())
    self.assertEqual(letter.getStopDate().hour(), end_date.hour())
    self.assertEqual(letter.getStopDate().day(), end_date.day())
  
  def testERPSite_createUNGUser(self):
    """Test if script creates an user correctly"""
    form_dict = dict(firstname="UNG",
                     lastname="User",
                     email="g@g.com",
                     password="ung_password",
                     login_name="ung_user")
    self.portal.REQUEST.form.update(form_dict)
    self.changeSkin("UNGDoc")
    response = json.loads(self.portal.ERPSite_createUNGUser())
    self.assertTrue(response)
    self.tic()
    person = self.portal.portal_catalog.getResultValue(portal_type="Person",
                                                       reference="ung_user")
    self.assertEqual(person.getFirstName(), "UNG")
    self.assertEqual(person.getLastName(), "User")
    self.assertEqual(person.getValidationState(), "validated")
    self.assertEqual(person.getEmail().getPortalType(), "Email")
    self.assertEqual(person.getEmailText(), "g@g.com")
    self.changeSkin("UNGDoc")
    response = json.loads(self.portal.ERPSite_createUNGUser())
    self.assertEqual(response, None)

  def testERP5Site_checkIfUserExistUsingHttpRequest(self):
    """Test script ERP5Site_checkIfUserExist to simulate the browser request"""
    script_path = self.portal.web_site_module.ung.getPath() + "/ERP5Site_checkIfUserExist"
    response = json.loads(self.publish(script_path).getBody())
    self.assertEqual(response, {'response': False})
    response = json.loads(self.publish(script_path + "?reference=ung_reference").getBody())
    self.assertEqual(response, {'response': True})

  def testERP5Site_checkIfUserExist(self):
    """Test script ERP5Site_checkIfUserExist"""
    self.changeSkin('UNGDoc')
    portal = self.portal
    form_dict = dict(firstname="UNG",
                     lastname="User",
                     email="g@g.com",
                     login_name="ung_reference")
    portal.REQUEST.form.update(form_dict)
    portal.ERPSite_createUNGUser()
    kw = dict(reference=form_dict["login_name"],)
    response = json.loads(portal.ERP5Site_checkIfUserExist(**kw))
    self.assertEqual(response.get("response"), False)
    self.tic()
    param_list = ["%s=%s" % (key,value) for key, value in kw.iteritems()]
    self.changeSkin("UNGDoc")
    response = json.loads(portal.ERP5Site_checkIfUserExist(**kw))
    self.assertEqual(response.get("response"), True)
    kw = dict(first_name="Not Exist",
              reference="no_reference",
             )
    self.changeSkin("UNGDoc")
    response = json.loads(portal.ERP5Site_checkIfUserExist(**kw))
    self.assertEqual(response.get("response"), False)
    self.loginByUserName("ung_reference")
    user = portal.portal_membership.getAuthenticatedMember().getUserValue()
    self.assertEqual(user.getFirstName(), "UNG")

  def testWebSection_addGadgetList(self):
    """Test if gadgets are added correctly"""
    obj = self.portal.knowledge_pad_module.newContent(portal_type="Knowledge Pad")
    obj.edit(publication_section_value=self.portal.web_site_module.ung)
    obj.visible()
    self.tic()
    gadget = self.portal.portal_gadgets.searchFolder()[0]
    gadget_id_list = gadget.getId()
    self.changeSkin("UNGDoc")
    self.portal.web_site_module.ung.WebSection_addGadgetList(gadget_id_list)
    self.tic()
    gadget = self.portal.portal_catalog.getResultValue(portal_type="Gadget",
                                                       validation_state="public")
    self.assertEqual(gadget_id_list, gadget.getId())
    self.portal.knowledge_pad_module.deleteContent(id=obj.getId())
    self.tic()
    obj = self.portal.knowledge_pad_module.newContent(portal_type="Knowledge Pad")
    obj.edit(publication_section_value=self.portal.web_site_module.ung)
    obj.visible()
    self.tic()
    gadget_id_list = []
    path_list = []
    gadget = self.portal.portal_gadgets.searchFolder()[0].getObject()
    gadget_id_list.append(gadget.getId())
    path_list.append(gadget.getRelativeUrl())
    gadget = self.portal.portal_gadgets.searchFolder()[1].getObject()
    gadget_id_list.append(gadget.getId())
    path_list.append(gadget.getRelativeUrl())
    self.portal.REQUEST.form["gadget_id_list"] = ",".join(gadget_id_list)
    self.changeSkin("UNGDoc")
    self.portal.web_site_module.ung.WebSection_addGadgetList()
    self.tic()
    self.assertEqual(len(obj.searchFolder()), 2)
    self.assertEqual(sorted([x.getSpecialise() for x in obj.searchFolder()]),
                      sorted(path_list))

  def testBase_getPreferencePathList(self):
    """Test if the paths of preference objects are returned correctly"""
    self.changeSkin('UNGDoc')
    self.logout()
    self.assertEqual(json.loads(self.portal.Base_getPreferencePathList()), None)
    self.login("ERP5TypeTestCase")
    self.changeSkin("UNGDoc")
    preference_dict = json.loads(self.portal.Base_getPreferencePathList())
    self.assertEqual(preference_dict, {})
    self.portal.portal_preferences.ung_preference.enable()
    self.tic()
    self.changeSkin("UNGDoc")
    preference_dict = json.loads(self.portal.Base_getPreferencePathList())
    self.assertEqual(preference_dict["preference"], "portal_preferences/ung_preference")

  def testWebSection_getWebPageObjectList(self):
    """Test if the paths of preference objects are returned correctly"""
    self.portal.web_page_module.manage_delObjects(list(self.portal.web_page_module.objectIds()))
    self.tic()
    self.portal.web_page_module.newContent(portal_type="Web Page")
    self.portal.web_page_module.newContent(portal_type="Web Table")
    self.portal.web_page_module.newContent(portal_type="Web Illustration")
    self.tic()
    kw = {"portal_type": "Web Page"}
    self.changeSkin('UNGDoc')
    result_list = self.portal.web_site_module.ung.WebSection_getWebPageObjectList(**kw)
    self.assertEqual(len(result_list), 1)
    self.assertEqual(result_list[0].getPortalType(), "Web Page")
    kw["portal_type"] = "Web Illustration"
    result_list = self.portal.web_site_module.ung.WebSection_getWebPageObjectList(**kw)
    self.assertEqual(len(result_list), 1)
    self.assertEqual(result_list[0].getPortalType(), "Web Illustration")
    kw["portal_type"] = "Web Table"
    result_list = self.portal.web_site_module.ung.WebSection_getWebPageObjectList(**kw)
    self.assertEqual(len(result_list), 1)
    self.assertEqual(result_list[0].getPortalType(), "Web Table")

  def testWebPage_updateWebDocument(self):
    """ Test if script load correctly the Web Page with data of one document
    """
    portal = self.portal
    document_path, filename = self.getDocumentPath()
    file = FileUpload(document_path, filename)
    document = portal.portal_contributions.newContent(file=file)
    web_page = portal.web_page_module.newContent(portal_type="Web Page")
    self.tic()
    self.changeSkin("UNGDoc")
    web_page.WebPage_updateWebDocument(document.getPath())
    self.tic()
    self.assertTrue(re.search("\>tiolive\<", web_page.getTextContent()) is not None)
    self.assertEqual(web_page.getTitle(), document.getTitle())
