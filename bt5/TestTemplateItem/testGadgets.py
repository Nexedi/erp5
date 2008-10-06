# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                     Ivan Tyagov <ivan@nexedi.com>
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
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG

def _getGadgetInstanceUrlFromKnowledgePad(knowledge_pad,  gadget):
  """ Get Knowledge Box's relative URL specialising a gadget in a Knowledge Pad."""
  return knowledge_pad.searchFolder(
                portal_type = 'Knowledge Box',  
                specialise_uid = gadget.getUid())[0].getObject().getRelativeUrl()

class TestGadgets(ERP5TypeTestCase,  ZopeTestCase.Functional):
  """Test Gadgets
  """
  run_all_test = 1
  quiet = 0
  manager_username = 'ivan'
  manager_password = ''
  
  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_knowledge_pad', 'erp5_web', 
            'erp5_ingestion', 'erp5_crm', 'erp5_pdm', 'erp5_trade', 
            'erp5_dms',  'erp5_dms_mysql_innodb_catalog', 
            'erp5_project',  'erp5_km')
    
  def getTitle(self):
    return "Gadgets"
  
  def afterSetUp(self):
    self.login()
    portal = self.getPortal()
    web_site_module = portal.web_site_module
    self.website = web_site_module.newContent(portal_type='Web Site')
    self.websection = self.website.newContent(portal_type='Web Section')
    self.webpage = portal.web_page_module.newContent(
		            portal_type = 'Web Page', 
                            reference = 'web-page-reference', 
                            language = 'en')
    self.auth = '%s:%s' % (self.manager_username, self.manager_password)
    self.web_site_url = '%s/web_site_module/%s' %(portal.getId(),  self.website.getId())
    self.web_section_url = '%s/%s' %(self.web_site_url,  self.websection.getId())
    self.web_page_url = '%s/web_page_module/%s' %(self.web_site_url,  self.webpage.getId())
    web_front_knowledge_pad_relative_url = self.website.ERP5Site_addNewKnowledgePad( \
                                                 pad_title =  'Web Front Knowledge Pad', \
                                                 mode='web_front')
    self.web_front_knowledge_pad = portal.restrictedTraverse(
                                     web_front_knowledge_pad_relative_url)
    self.base_url_pattern = '%s/%s?parent_web_section_url=%s&box_relative_url=%s&is_gadget_mode=1'
    
    # Web Section Pad
    web_section_knowledge_pad_relative_url = self.websection.ERP5Site_addNewKnowledgePad( \
                                               pad_title = 'Web Section Knowledge Pad', \
                                               mode = 'web_section')    
    self.web_section_knowledge_pad = portal.restrictedTraverse(
                                       web_section_knowledge_pad_relative_url)
    # Web Section Content Pad
    self.web_section_content_knowledge_pad_relative_url = self.webpage.ERP5Site_addNewKnowledgePad(
                                                       pad_title =  'Web Section Knowledge Pad', \
                                                       mode = 'web_section')    
    self.web_section_content_knowledge_pad = portal.restrictedTraverse(
                                          self.web_section_content_knowledge_pad_relative_url)
    get_transaction().commit()
    self.tic()

    
  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('ivan', '', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('ivan').__of__(uf)
    newSecurityManager(None, user)  
  
  def test_01ProperPoolInitialization(self, quiet=quiet, run=run_all_test):
    """ Check that it's properly initialized """
    if not run: return
    portal = self.getPortal()
    self.assertNotEqual(None, 
		        getattr(portal, 'portal_gadgets', None))
 
  def test_02(self, quiet=quiet, run=run_all_test):
    """ Check Gadgets """
    if not run: return
    portal = self.getPortal()
    knowledge_pad_module = getattr(portal, 'knowledge_pad_module')
    # remove created by login method pads
    knowledge_pad_module.manage_delObjects(list(knowledge_pad_module.objectIds()))
    get_transaction().commit()
    self.tic()
    
    portal.ERP5Site_createDefaultKnowledgePadListForUser()
    get_transaction().commit()
    self.tic()
    self.assertEqual(1, 
		     len(knowledge_pad_module.searchFolder(portal_type='Knowledge Pad')))
    default_pad = knowledge_pad_module.searchFolder(
		    portal_type='Knowledge Pad')[0].getObject()
    self.assertEqual(None, 
		    default_pad.getPublicationSection())
    self.assertEqual('visible',
		     default_pad.getValidationState())
    
    # add box, test if box visible
    gadget = portal.portal_gadgets.erp5_persons
    kw = {'uids': (gadget.getUid(),),
          'listbox_list_selection_name': '',}
    default_pad.KnowledgePad_addBoxList(**kw)
    box = default_pad.contentValues(portal_type='Knowledge Box')[0]
    self.assertEqual('visible', box.getValidationState())
    
    # toggle box state
    portal.KnowledgeBox_toggleVisibility(box.getRelativeUrl())
    self.assertEqual('invisible', box.getValidationState())
    portal.KnowledgeBox_toggleVisibility(box.getRelativeUrl())
    self.assertEqual('visible', box.getValidationState())
    portal.KnowledgePad_deleteBox(box.getRelativeUrl())
    self.assertEqual('deleted', box.getValidationState())
    
    # add new pad 
    portal.ERP5Site_addNewKnowledgePad(pad_title='Test')
    get_transaction().commit()
    self.tic()
    pads = knowledge_pad_module.ERP5Site_getKnowledgePadListForUser()
    self.assertEqual(2, len(pads))
    for pad in pads:
      pad = pad.getObject() 
      if pad == default_pad:
        # default (first) pad is invisible now
        self.assertEqual('invisible', pad.getValidationState())
      else:
        self.assertEqual('visible', pad.getValidationState())
        self.assertEqual(0, 
                        len(pad.searchFolder(portal_type='Knowledge Box')))
        new_pad = pad

    self.assertEqual(new_pad, 
                     portal.ERP5Site_getActiveKnowledgePadForUser(pads)[0].getObject())
    
    # remove newly added tab, check visibility
    portal.ERP5Site_deleteKnowledgePad(new_pad.getRelativeUrl())
    get_transaction().commit()
    self.tic()
    pads = knowledge_pad_module.ERP5Site_getKnowledgePadListForUser()
    self.assertEqual(1, len(pads))
    self.assertEqual(default_pad, 
                     portal.ERP5Site_getActiveKnowledgePadForUser(pads)[0].getObject())
    manuallly_created_pad = knowledge_pad_module.newContent(portal_type='Knowledge Pad')
    portal.ERP5Site_toggleActiveKnowledgePad(manuallly_created_pad.getRelativeUrl())
    get_transaction().commit()
    self.tic()
    self.assertEqual('invisible', default_pad.getValidationState())
    
    # check for Web context (i.e. Site/Section)
    website = self.website
    website.ERP5Site_createDefaultKnowledgePadListForUser(mode='web_front')
    get_transaction().commit()
    self.tic()
    website_pads = website.ERP5Site_getKnowledgePadListForUser(mode='web_front')
    self.assertEqual(1, len(website_pads))
    self.assertEqual(website, website_pads[0].getPublicationSectionValue())

    # depending on context we should have different list of pads for user
    self.assertNotEqual(portal.ERP5Site_getKnowledgePadListForUser(),
                        website.ERP5Site_getKnowledgePadListForUser())
    
    # check Web Section
    pad_group = None
    websection = self.websection
    websection.ERP5Site_createDefaultKnowledgePadListForUser(
	                mode='web_section',
                        default_pad_group = pad_group)
    get_transaction().commit()
    self.tic()
    websection_pads = websection.ERP5Site_getKnowledgePadListForUser(
		        mode='web_section',
                        default_pad_group = pad_group)
    base_websection_pad, websection_pads = \
             websection.WebSite_getActiveKnowledgePadForUser(websection_pads,
                                                             default_pad_group = pad_group)
   
    # Check stick
    websection.WebSection_stickKnowledgePad(
                    base_websection_pad.getRelativeUrl(), '')
    get_transaction().commit()
    self.tic()
    websection_pads = websection.ERP5Site_getKnowledgePadListForUser(
		        mode='web_section',
                        default_pad_group = pad_group)
    current_websection_pad, websection_pads = \
             websection.WebSite_getActiveKnowledgePadForUser(websection_pads,
                                                             default_pad_group = pad_group)
    self.assertNotEqual(base_websection_pad.getObject(),
                     current_websection_pad.getObject())
    
    # check unstick
    websection.WebSection_unStickKnowledgePad(current_websection_pad.getRelativeUrl(), '')
    
    websection_pads = websection.ERP5Site_getKnowledgePadListForUser(
		        mode='web_section',
                        default_pad_group = pad_group)
    current_websection_pad, websection_pads = \
             websection.WebSite_getActiveKnowledgePadForUser(websection_pads,
                                                             default_pad_group = pad_group)
    self.assertEqual(base_websection_pad.getObject(),
                     current_websection_pad.getObject())

  def test_03DefaultKnowledgePadFromPreference(self, quiet=quiet, run=run_all_test):
    """ Check Gadgets """
    if not run: return
    portal = self.getPortal()
    website = self.website
    websection = self.websection
    default_pad_group = 'default_section_pad'
    default_pad_group_section_content_title = 'default_content_pad'
    
    knowledge_pad_module = getattr(portal, 'knowledge_pad_module')
    knowledge_pad_module.manage_delObjects(list(knowledge_pad_module.objectIds()))
    self.assertEqual(0, 
		     len(knowledge_pad_module.objectValues(portal_type='Knowledge Pad')))

    # create 4 knowledge pad in active preference for every mode 
    # (ERP5, Web Site front, Web Section, Web Section content)
    user_pref =portal.portal_preferences.getActivePreference()
    if user_pref is None:
      # enable the default site wide preference
      user_pref = portal.portal_preferences.objectValues(portal_type='Preference')[0]
      user_pref.enable()
    get_transaction().commit()
    self.tic()
    self.assertNotEqual(None,  portal.portal_preferences.getActivePreference())
    
    # Create knowledge pads in active preference
    # ERP5 mode
    erp5_knowledge_pad = user_pref.newContent(portal_type = 'Knowledge Pad', 
                                              title = "erp5")
    erp5_knowledge_pad1 = erp5_knowledge_pad.newContent(portal_type = 'Knowledge Box', 
                                                        title = "erp5_1")
    erp5_knowledge_pad.visible(); 
    erp5_knowledge_pad.public()
    erp5_knowledge_pad1.visible(); 
    erp5_knowledge_pad1.public()
    
    # Web front mode
    web_front_knowledge_pad = user_pref.newContent(portal_type = 'Knowledge Pad', 
                                                   title = "web")
    web_front_knowledge_pad.setPublicationSectionValue(website)
    web_front_knowledge_pad1 = web_front_knowledge_pad.newContent(portal_type = 'Knowledge Box', 
                                                                  title = "web_1")
    web_front_knowledge_pad.visible();  
    web_front_knowledge_pad.public()
    web_front_knowledge_pad1.visible(); 
    web_front_knowledge_pad1.public()
    
    # Web Section mode
    websection_knowledge_pad = user_pref.newContent(portal_type = 'Knowledge Pad', 
                                                    title = "web_section")
    websection_knowledge_pad.setGroupValue(default_pad_group)
    websection_knowledge_pad1 = websection_knowledge_pad.newContent( \
                                                    portal_type = 'Knowledge Box',  
                                                    title = "web_section_1")
    websection_knowledge_pad.visible(); 
    websection_knowledge_pad.public()
    websection_knowledge_pad1.visible(); 
    websection_knowledge_pad1.public()
    
    # Web Section content mode
    websection_content_knowledge_pad = user_pref.newContent( \
		                          portal_type = 'Knowledge Pad', \
                                          title = "web_section_content")
    websection_content_knowledge_pad.setGroupValue(default_pad_group_section_content_title)
    websection_content_knowledge_pad1 = websection_content_knowledge_pad.newContent( \
                                          portal_type = 'Knowledge Box', \
                                          title = "web_section_content_1")
    websection_content_knowledge_pad.visible(); 
    websection_content_knowledge_pad.public()
    websection_content_knowledge_pad1.visible(); 
    websection_content_knowledge_pad1.public()    
    get_transaction().commit()
    self.tic()    
    
    # check that 4 different modes return knowledge_pads from preference
    # ERP5 front
    knowledge_pads = portal.ERP5Site_getKnowledgePadListForUser(mode="erp5_front")
    self.assertEqual(1,  len(knowledge_pads))
    self.assertEqual(erp5_knowledge_pad,  knowledge_pads[0].getObject())
                            
    # web_front
    knowledge_pads = website.ERP5Site_getKnowledgePadListForUser(mode="web_front")
    self.assertEqual(1, len(knowledge_pads))
    self.assertEqual(web_front_knowledge_pad,  
                     knowledge_pads[0].getObject())     
        
    # web_section
    knowledge_pads = websection.ERP5Site_getKnowledgePadListForUser( \
                                        mode="web_section",  \
                                        default_pad_group = default_pad_group)
    self.assertEqual(1, len(knowledge_pads))
    self.assertEqual(websection_knowledge_pad,  
                     knowledge_pads[0].getObject())  

    # web_section content
    knowledge_pads = websection.ERP5Site_getKnowledgePadListForUser( \
                                  mode="web_section",  \
                                  default_pad_group = default_pad_group_section_content_title)
    self.assertEqual(1, len(knowledge_pads))
    self.assertEqual(websection_content_knowledge_pad,  
                     knowledge_pads[0].getObject())            

    # Check that creating a real knowledge pad from active preference (knowledge pad as a template)
    # is possible and it's exactly the same as original in preference
    # ERP5 front
    portal.ERP5Site_createDefaultKnowledgePadListForUser(mode='erp5_front')
    get_transaction().commit()
    self.tic()    
    erp5_knowledge_pad = portal.ERP5Site_getKnowledgePadListForUser(
                                  mode="erp5_front")[0].getObject()
    self.assertEqual(portal.knowledge_pad_module,  
                     erp5_knowledge_pad.getParentValue())
    self.assertEqual("erp5",  
                     erp5_knowledge_pad.getTitle())
    self.assertEqual("visible",  
                     erp5_knowledge_pad.getValidationState())
    self.assertEqual("erp5_1",  
                     erp5_knowledge_pad.objectValues()[0].getTitle())
    self.assertEqual("visible",  
                     erp5_knowledge_pad.objectValues()[0].getValidationState())    
    
    # Web Site front
    website.ERP5Site_createDefaultKnowledgePadListForUser(mode='web_front')
    get_transaction().commit()
    self.tic()    
    web_knowledge_pad = website.ERP5Site_getKnowledgePadListForUser(
                                       mode="web_front")[0].getObject()
    self.assertEqual(portal.knowledge_pad_module,  
                     erp5_knowledge_pad.getParentValue())
    self.assertEqual("web",  
                     web_knowledge_pad.getTitle())
    self.assertEqual("visible",  
                     web_knowledge_pad.getValidationState())
    self.assertEqual("web_1",  
                     web_knowledge_pad.objectValues()[0].getTitle())
    self.assertEqual("visible",  
                     web_knowledge_pad.objectValues()[0].getValidationState())    
        
    # Web Section 
    websection.ERP5Site_createDefaultKnowledgePadListForUser( \
                                      mode='web_section', \
                                      default_pad_group = default_pad_group)
    get_transaction().commit()
    self.tic()    
    websection_knowledge_pad = websection.ERP5Site_getKnowledgePadListForUser( \
                                      mode="web_section", \
                                      default_pad_group = default_pad_group)[0].getObject()
    self.assertEqual(portal.knowledge_pad_module,  
                     websection_knowledge_pad.getParentValue())
    self.assertEqual("web_section",  
                     websection_knowledge_pad.getTitle())
    self.assertEqual("visible",  
                     websection_knowledge_pad.getValidationState())
    self.assertEqual("web_section_1",  
                     websection_knowledge_pad.objectValues()[0].getTitle())
    self.assertEqual("visible",  
                     websection_knowledge_pad.objectValues()[0].getValidationState())        
    
    # Web Section content
    websection.ERP5Site_createDefaultKnowledgePadListForUser( \
                               mode='web_section', \
                               default_pad_group = default_pad_group_section_content_title)
    get_transaction().commit()
    self.tic()    
    websection_content_knowledge_pad = websection.ERP5Site_getKnowledgePadListForUser( \
                     mode="web_section", \
                     default_pad_group = default_pad_group_section_content_title)[0].getObject()
    self.assertEqual(portal.knowledge_pad_module,  
                     websection_content_knowledge_pad.getParentValue())
    self.assertEqual("web_section_content",  
                     websection_content_knowledge_pad.getTitle())
    self.assertEqual("visible",  
                     websection_content_knowledge_pad.getValidationState())
    self.assertEqual("web_section_content_1",  
                     websection_content_knowledge_pad.objectValues()[0].getTitle())
    self.assertEqual("visible",  
                     websection_content_knowledge_pad.objectValues()[0].getValidationState())       

  def test_04WebFrontGagets(self, quiet=quiet, run=run_all_test):
    """ Check different Web / KM Gadgets """
    if not run: return
    portal = self.getPortal()
    request = self.app.REQUEST

    # all known so far gadgets 
    portal_gadgets = portal.portal_gadgets
    km_my_tasks_gadget = portal_gadgets.km_my_tasks
    km_my_documents_gadget = portal_gadgets.km_my_documents
    km_my_contacts_gadget = portal_gadgets.km_my_contacts
    
    response = self.publish('%s/WebSite_viewHomeAreaFormRenderer' %self.web_site_url, self.auth)
    self.failUnless(self.web_front_knowledge_pad.getTitle() in response.getBody())

    # Web Front gadgets
    web_front_gadgets = [km_my_tasks_gadget,  km_my_documents_gadget,  km_my_contacts_gadget]
    for gadget in web_front_gadgets:
      self.web_front_knowledge_pad.KnowledgePad_addBoxList(**{'uids':[gadget.getUid()]})
    get_transaction().commit()
    self.tic()
     
    # check that gadgets are added to web front page view
    response = self.publish('%s/WebSite_viewHomeAreaFormRenderer' %self.web_site_url, self.auth)
    for gadget in web_front_gadgets:
      self.failUnless(gadget.getTitle() in response.getBody())

  def test_05MyTaskGaget(self, quiet=quiet, run=run_all_test):
    """ Check My Task Gadgets """
    if not run: return    
    portal = self.getPortal()
    km_my_tasks_gadget = portal.portal_gadgets.km_my_tasks
    
    # add gadget
    self.web_front_knowledge_pad.KnowledgePad_addBoxList(**{'uids':[km_my_tasks_gadget.getUid()]})
    
    # "My Tasks" gadget (add a new document which should be shown shown in it)
    project = portal.project_module.newContent(portal_type = 'Project', \
                                               title = 'Project: title (български)')
    visit = portal.event_module.newContent(portal_type = 'Visit', \
                                           title = 'Visit: title (български)')
    get_transaction().commit()
    self.tic()
    # simulate asynchronous gadget view (on Web Site, Web Section,Web Section content )
    gadget_view_form_id  = km_my_tasks_gadget.view_form_id
    km_my_tasks_box_url = _getGadgetInstanceUrlFromKnowledgePad( \
		                                        self.web_front_knowledge_pad,  \
                                            km_my_tasks_gadget) 
    for response in [
                  self.publish(self.base_url_pattern %(self.web_site_url,  
                                                  gadget_view_form_id, 
                                                  self.website.getRelativeUrl(), 
                                                  km_my_tasks_box_url )
                               , self.auth), 
                  self.publish(self.base_url_pattern  %(self.web_section_url,  
                                                   gadget_view_form_id, 
                                                   self.websection.getRelativeUrl(), 
                                                   km_my_tasks_box_url)
                               , self.auth), 
                  self.publish(self.base_url_pattern %(self.web_page_url,  
                                                  gadget_view_form_id, 
                                                  self.webpage.getRelativeUrl(),  
                                                  km_my_tasks_box_url)
                               , self.auth)]:
      self.failUnless(project.getTitle() in response.getBody())
      self.failUnless(visit.getTitle() in response.getBody())

  def test_06MyDocumentsGadget(self, quiet=quiet, run=run_all_test):
    """ Check My Document Gadgets """
    if not run: return 
    portal = self.getPortal()
    km_my_documents_gadget = portal.portal_gadgets.km_my_documents
    
    # add gadget
    self.web_front_knowledge_pad.KnowledgePad_addBoxList(**{'uids':[km_my_documents_gadget.getUid()]})
    
    # "My Documents" gadget (add a new document which should be shown shown in it)
    web_page = portal.web_page_module.newContent( \
                        portal_type = 'Web Page', \
                        reference = 'web-page-123', \
                        title = 'Web Page: title 123 (български)')
    presentation = portal.document_module.newContent( \
                        portal_type = 'Presentation', \
                        reference = 'presentation-456', 
                        title = 'Presentation: title 456 (български)')
    get_transaction().commit()
    self.tic()
    # simulate asynchronous gadget view (on Web Site, Web Section,Web Section content )
    gadget_view_form_id  = km_my_documents_gadget.view_form_id
    km_my_documents_gadget_box_url = _getGadgetInstanceUrlFromKnowledgePad( \
                                         self.web_front_knowledge_pad, \
                                         km_my_documents_gadget)
    for response in [
            self.publish(self.base_url_pattern %(self.web_site_url,  
		                                             gadget_view_form_id, 
                                                 self.website.getRelativeUrl(),  
					                                       km_my_documents_gadget_box_url)
                         , self.auth), 
            self.publish(self.base_url_pattern %(self.web_section_url,  
                                                 gadget_view_form_id, 
                                                 self.websection.getRelativeUrl(), 
					                                       km_my_documents_gadget_box_url)
                         , self.auth), 
            self.publish(self.base_url_pattern %(self.web_page_url,  
		                                             gadget_view_form_id, 
                                                 self.webpage.getRelativeUrl(),  
					                                       km_my_documents_gadget_box_url)
			                   , self.auth)]:
      self.failUnless(web_page.getReference() in response.getBody())
      self.failUnless(presentation.getReference() in response.getBody())
    
  def test_07MyContactsGadget(self, quiet=quiet, run=run_all_test):
    """ Check My Contacts Gadgets """
    if not run: return 
    portal = self.getPortal()
    km_my_contacts_gadget = portal.portal_gadgets.km_my_contacts
    
    # add gadget
    self.web_front_knowledge_pad.KnowledgePad_addBoxList(**{'uids':[km_my_contacts_gadget.getUid()]})
    
    # "My Contacts" gadget (add a new document which should be shown shown in it)
    person = portal.person_module.newContent(portal_type = 'Person',
                                             title = 'John Doe')
    get_transaction().commit()
    self.tic()
    # simulate asynchronous gadget view (on Web Site, Web Section,Web Section content )
    gadget_view_form_id  = km_my_contacts_gadget.view_form_id
    km_my_contacts_gadget_box_url = _getGadgetInstanceUrlFromKnowledgePad(
                                       self.web_front_knowledge_pad,  
                                       km_my_contacts_gadget)     
    for response in [
            self.publish(self.base_url_pattern  %(self.web_site_url,  
		                                              gadget_view_form_id, 
                                                  self.website.getRelativeUrl(), 
         	                                        km_my_contacts_gadget_box_url)
                         , self.auth), 
            self.publish(self.base_url_pattern %(self.web_section_url,  
		                                             gadget_view_form_id, 
                                                 self.websection.getRelativeUrl(),  
					                                       km_my_contacts_gadget_box_url)
                         , self.auth), 
            self.publish(self.base_url_pattern %(self.web_page_url,  
                                                 gadget_view_form_id, 
                                                 self.webpage.getRelativeUrl(), 
                                                 km_my_contacts_gadget_box_url)
                         , self.auth)]:
      self.failUnless(person.getTitle() in response.getBody())
    
  def test_08WebSectionGadget(self, quiet=quiet, run=run_all_test):
    """ Check Web Section Gadgets """
    if not run: return 
    portal = self.getPortal()
    km_subsection_gadget = portal.portal_gadgets.km_subsection
    km_latest_documents_gadget = portal.portal_gadgets.km_latest_documents
    km_assigned_member_gadget = portal.portal_gadgets.km_assigned_member
    km_document_relations_gadget = portal.portal_gadgets.km_document_relations
    
    web_section_gadgets = [km_subsection_gadget,  
                           km_latest_documents_gadget,  
                           km_assigned_member_gadget]
    for gadget in web_section_gadgets:
      self.web_section_knowledge_pad.KnowledgePad_addBoxList(**{'uids':[gadget.getUid()]})
    get_transaction().commit()
    self.tic()      
    
    # check that gadgets are added to web section page view
    response = self.publish('%s/WebSection_viewColumnOne' %self.web_section_url, self.auth)
    for gadget in web_section_gadgets:
      self.failUnless(gadget.getTitle() in response.getBody())     
    
  def test_09SubsectionGadget(self, quiet=quiet, run=run_all_test):
    """ Check Subsection Gadgets """
    if not run: return 
    portal = self.getPortal()
    km_subsection_gadget = portal.portal_gadgets.km_subsection
    
    # add gadget
    self.web_section_knowledge_pad.KnowledgePad_addBoxList(**{'uids':[km_subsection_gadget.getUid()]})
    get_transaction().commit()
    self.tic()
 
    # "Subsections" gadget
    gadget_view_form_id  = km_subsection_gadget.view_form_id
    km_subsection_gadget_box_url = _getGadgetInstanceUrlFromKnowledgePad( \
                                     self.web_section_knowledge_pad,  \
                                     km_subsection_gadget)
    self.failUnless('No subsections found.' in 
                      self.publish(self.base_url_pattern %(self.web_section_url, 
			                                                     gadget_view_form_id, 
                                                           self.websection.getRelativeUrl(),
                                                           km_subsection_gadget_box_url)
                                   , self.auth).getBody())
    # .. create subsection and make sure it appears in gadget
    subsection = self.websection.newContent(portal_type='Web Section',  
                                       title='Sub Section 12345')
    get_transaction().commit()
    self.tic()
    self.failUnless(subsection.getTitle() in 
		      self.publish(self.base_url_pattern %(self.web_section_url,  
			                                         gadget_view_form_id, 
                                               self.websection.getRelativeUrl(),  
						                                   km_subsection_gadget_box_url)  
                                    , self.auth).getBody())

  def test_10LatestContentGadget(self, quiet=quiet, run=run_all_test):
    """ Check Latest Content Gadgets """
    if not run: return 
    portal = self.getPortal()
    request = self.app.REQUEST
    km_latest_documents_gadget = portal.portal_gadgets.km_latest_documents

    # add gadget
    self.web_section_knowledge_pad.KnowledgePad_addBoxList(
                               **{'uids':[km_latest_documents_gadget.getUid()]})

    # "Latest Content" gadget
    gadget_view_form_id  = km_latest_documents_gadget.view_form_id
    publication_section_category_id_list = ['documentation',  'administration']
    for category_id in publication_section_category_id_list:
      portal.portal_categories.publication_section.newContent(portal_type = 'Category', 
                                                              id = category_id)    
    latest_docs_subsection = self.websection.newContent(portal_type='Web Section')
    latest_docs_subsection.edit(membership_criterion_base_category = ['publication_section'], 
                                membership_criterion_category=['publication_section/%s' 
                                              %publication_section_category_id_list[0]])
    get_transaction().commit()
    self.tic()
    km_latest_documents_gadget_box_url = _getGadgetInstanceUrlFromKnowledgePad(
                                           self.web_section_knowledge_pad,  
                                           km_latest_documents_gadget)  
    # set here to prevent  failing to render a form's field which reads directly requets
    request.set('box_relative_url',  km_latest_documents_gadget_box_url)  
    self.failUnless('0 record(s)' in 
                    self.publish(self.base_url_pattern  
                           %(self.web_section_url+'/%s' %latest_docs_subsection.getId(),
                             gadget_view_form_id, 
                             latest_docs_subsection.getRelativeUrl(),
                             km_latest_documents_gadget_box_url)
	                  , self.auth).getBody())
    # add some documents to this web section
    presentation = portal.document_module.newContent(
		                      portal_type = 'Presentation', 
                          reference = 'Presentation-12456_', 
                          publication_section_list = publication_section_category_id_list[:1])
    presentation.publish()
    get_transaction().commit()
    self.tic()
    self.failUnless(presentation.getReference() in 
    	  self.publish(self.base_url_pattern 
                    %(self.web_section_url+'/%s' %latest_docs_subsection.getId(),  
                      gadget_view_form_id, 
                      latest_docs_subsection.getRelativeUrl(), 
                      km_latest_documents_gadget_box_url)
                    , self.auth).getBody())

  def test_11AssignedMembersGadget(self, quiet=quiet, run=run_all_test):
    """ Check Assigned Members Gadgets """
    if not run: return 
    portal = self.getPortal()
    request = self.app.REQUEST
    km_assigned_member_gadget = portal.portal_gadgets.km_assigned_member
    
    # add gadget
    self.web_section_knowledge_pad.KnowledgePad_addBoxList(
                               **{'uids':[km_assigned_member_gadget.getUid()]})
    gadget_view_form_id  = km_assigned_member_gadget.view_form_id
    project = portal.project_module.newContent(
                                   portal_type = 'Project',  
		                               title='KM Impl')
    assigned_members_subsection = self.websection.newContent(portal_type = 'Web Section')
    assigned_members_subsection.edit(membership_criterion_base_category = ['follow_up'], 
                                     membership_criterion_category = ['follow_up/%s'%project.getId()])
    get_transaction().commit()
    self.tic()
    km_assigned_member_gadget_box_url = _getGadgetInstanceUrlFromKnowledgePad(
                                          self.web_section_knowledge_pad,  
                                          km_assigned_member_gadget)
    
    self.failUnless('0 record(s)' in 
          self.publish(self.base_url_pattern 
            %(self.web_section_url+'/%s' %assigned_members_subsection.getId(),  
              gadget_view_form_id, 
              assigned_members_subsection.getRelativeUrl(),  
              km_assigned_member_gadget_box_url) 
          , self.auth).getBody()) 
    # .. add assignment for a person to this project
    person = portal.person_module.newContent(portal_type = 'Person', 
                                             title = 'John Doe 1.234', 
                                             reference = 'person_12345')    
    assignment =  person.newContent(portal_type = 'Assignment')
    get_transaction().commit()
    self.tic()
    self.failUnless('1 record(s)' in 
            self.publish(self.base_url_pattern 
              %(self.web_section_url+'/%s' %assigned_members_subsection.getId(),  
                gadget_view_form_id, 
                assigned_members_subsection.getRelativeUrl(),  
                km_assigned_member_gadget_box_url)
            , self.auth).getBody())
    self.failUnless(person.getTitle() in 
		      self.publish(self.base_url_pattern 
            %(self.web_section_url+'/%s' %assigned_members_subsection.getId(),  
              gadget_view_form_id, 
              assigned_members_subsection.getRelativeUrl(),
              km_assigned_member_gadget_box_url)
            , self.auth).getBody())
    
  def test_11WebSectionContentGadget(self, quiet=quiet, run=run_all_test):
    """ Check  Web Section Content Gadgets """
    if not run: return     
    portal = self.getPortal()
    request = self.app.REQUEST

    km_document_relations_gadget = portal.portal_gadgets.km_document_relations    
    web_section_content_gadgets = [km_document_relations_gadget]
    for gadget in web_section_content_gadgets:
      self.web_section_content_knowledge_pad.KnowledgePad_addBoxList(**{'uids':[gadget.getUid()]})
    get_transaction().commit()
    self.tic()

    # check that gadgets are added to web section page view
    response = self.publish('%s/WebSection_viewColumnOne' %self.web_page_url, self.auth)

    for gadget in web_section_content_gadgets:
      self.failUnless(gadget.getTitle() in response.getBody())
    return
    
  def test_12RelationGadget(self, quiet=quiet, run=run_all_test):
    """ Check  Relation Gadgets """
    if not run: return     
    portal = self.getPortal()
    request = self.app.REQUEST
    km_document_relations_gadget = portal.portal_gadgets.km_document_relations

    # add gadget
    self.web_section_content_knowledge_pad.KnowledgePad_addBoxList(
                               **{'uids':[km_document_relations_gadget.getUid()]})    
    get_transaction().commit()
    self.tic()

    # "Relation" gadget
    gadget_view_form_id  = km_document_relations_gadget.view_form_id
    km_document_relations_gadget_box_url = _getGadgetInstanceUrlFromKnowledgePad(
                                             self.web_section_content_knowledge_pad,  
                                             km_document_relations_gadget)
    # relation gadget requires 'current_web_document' in REQUEST which seems to be set in 
    # normal web mode in traversal (i.e. it's not available for .publish() 
    # method - that's why we call it directly) 
    request.set('is_gadget_mode',  1)
    request.set('parent_web_section_url',  self.webpage.getRelativeUrl())
    request.set('box_relative_url',  km_document_relations_gadget_box_url)    
    relation_form_renderer = getattr(self.website.web_page_module[self.webpage.getId()],  
                                     gadget_view_form_id)

    # no related docs should exist
    self.failUnless('No related documents found.' in relation_form_renderer())

    # set related docs
    similar_doc = portal.web_page_module.newContent(
                           portal_type = 'Web Page', 
                           reference = '1.891', 
                           title = 'Similar document 1.891')
    predecessor_doc = portal.document_module.newContent(
                           portal_type = 'Spreadsheet', 
                           reference = 'r-7.3451', 
                           title = 'Predecessor document r-7.3451')
    successor_doc = portal.document_module.newContent(
                           portal_type = 'Text', 
                           reference = 'a-661ee1', 
                           title = 'Successor document a-661ee1')
    self.webpage.setSimilarValueList([similar_doc])
    self.webpage.setPredecessorValueList([predecessor_doc])
    self.webpage.setSuccessorValueList([successor_doc])    
    get_transaction().commit()
    self.tic()

    # .. should be in gadget html 
    self.failUnless(similar_doc.getTitle() in relation_form_renderer())
    self.failUnless(predecessor_doc.getTitle() in relation_form_renderer())
    self.failUnless(successor_doc.getTitle() in relation_form_renderer())

  def test_13AdminToolboxGadget(self, quiet=quiet, run=run_all_test):
    """ Check admin toolbox gadget """
    if not run: return
    portal = self.getPortal()
    request = self.app.REQUEST
    km_admin_gadget = portal.portal_gadgets.km_admin

    # add gadget
    self.web_section_content_knowledge_pad.KnowledgePad_addBoxList(
                               **{'uids':[km_admin_gadget.getUid()]})    
    get_transaction().commit()
    self.tic()

    gadget_view_form_id  = km_admin_gadget.view_form_id
    km_admin_gadget_box_url = _getGadgetInstanceUrlFromKnowledgePad(
                                             self.web_section_content_knowledge_pad,  
                                             km_admin_gadget)

    request.set('is_gadget_mode',  1)
    request.set('parent_web_section_url',  self.webpage.getRelativeUrl())
    request.set('box_relative_url',  km_admin_gadget_box_url)
    relation_form_renderer = getattr(self.website.web_page_module[self.webpage.getId()],  
                                     gadget_view_form_id)

    # "view" mode for Web Page
    request.set('editable_mode',  0)
    self.failUnless('Edit Web Page' in relation_form_renderer())
    self.failUnless('Edit Parent Web Site' in relation_form_renderer())

    # "edit" mode  for Web Page
    request.set('editable_mode',  1)
    self.failUnless('View Web Page' in relation_form_renderer())
    self.failUnless('Edit Parent Web Site' in relation_form_renderer())    

    # "view" mode for Web Section
    request.set('editable_mode',  0)
    relation_form_renderer = getattr(self.website[self.websection.getId()],  
                                     gadget_view_form_id)
    self.failUnless('Edit Web Section' in relation_form_renderer())

    # "edit" mode  for Web Section
    request.set('editable_mode',  1)
    self.failUnless('View Web Section' in relation_form_renderer())

    # "view" mode for Web Section having a default Web Page
    request.set('editable_mode',  0)
    self.websection.setAggregateValue(self.webpage)
    self.webpage.publish()
    get_transaction().commit()
    self.tic()
    relation_form_renderer = getattr(self.website[self.websection.getId()],  
                                     gadget_view_form_id)
    self.failUnless('Edit Web Page' in relation_form_renderer())
    self.failUnless('Edit Parent Web Section' in relation_form_renderer())

    # "edit" mode for Web Section having a default Web Page
    request.set('editable_mode',  1)
    self.failUnless('View Web Section' in relation_form_renderer())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestGadgets))
  return suite
