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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG

class TestGadgets(ERP5TypeTestCase):
  """Test Gadgets
  """
  run_all_test = 1
  quiet = 0
  
  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_knowledge_pad', 'erp5_web',)
    
  def getTitle(self):
    return "Gadgets"
  
  def afterSetUp(self):
    self.login()
    portal = self.getPortal()
    web_site_module = portal.web_site_module
    self.website = web_site_module.newContent(portal_type='Web Site')
    self.websection = self.website.newContent(portal_type='Web Section')
    
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
    self.assertNotEqual(None, getattr(portal, 'portal_gadgets', None))
    self.assertEqual(0, len(getattr(portal, 'knowledge_pad_module').contentValues()))
    
  def test_02(self, quiet=quiet, run=run_all_test):
    """ Check Gadgets """
    if not run: return
    portal = self.getPortal()
    knowledge_pad_module = getattr(portal, 'knowledge_pad_module')
    self.assertEqual(0, len(knowledge_pad_module.searchFolder(portal_type='Knowledge Pad')))
    portal.ERP5Site_createDefaultKnowledgePadListForUser()
    get_transaction().commit()
    self.tic()
    self.assertEqual(1, len(knowledge_pad_module.searchFolder(portal_type='Knowledge Pad')))
    default_pad = knowledge_pad_module.searchFolder(portal_type='Knowledge Pad')[0].getObject()
    self.assertEqual(None, default_pad.getPublicationSection())
    self.assertEqual('visible',default_pad.getValidationState())
    
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
        self.assertEqual(0, len(pad.searchFolder(portal_type='Knowledge Box')))
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
    websection.ERP5Site_createDefaultKnowledgePadListForUser(mode='web_section',
                                                             default_pad_group = pad_group)
    get_transaction().commit()
    self.tic()
    websection_pads = websection.ERP5Site_getKnowledgePadListForUser(mode='web_section',
                                                                     default_pad_group = pad_group)
    base_websection_pad, websection_pads = \
             websection.WebSite_getActiveKnowledgePadForUser(websection_pads,
                                                             default_pad_group = pad_group)
   
    # Check stick
    websection.WebSection_stickKnowledgePad(
                    base_websection_pad.getRelativeUrl(), '')
    get_transaction().commit()
    self.tic()
    websection_pads = websection.ERP5Site_getKnowledgePadListForUser(mode='web_section',
                                                                     default_pad_group = pad_group)
    current_websection_pad, websection_pads = \
             websection.WebSite_getActiveKnowledgePadForUser(websection_pads,
                                                             default_pad_group = pad_group)
    self.assertNotEqual(base_websection_pad.getObject(),
                     current_websection_pad.getObject())
    
    # check unstick
    websection.WebSection_unStickKnowledgePad(current_websection_pad.getRelativeUrl(), '')
    
    websection_pads = websection.ERP5Site_getKnowledgePadListForUser(mode='web_section',
                                                                     default_pad_group = pad_group)
    current_websection_pad, websection_pads = \
             websection.WebSite_getActiveKnowledgePadForUser(websection_pads,
                                                             default_pad_group = pad_group)
    self.assertEqual(base_websection_pad.getObject(),
                     current_websection_pad.getObject())
    
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestGadgets))
  return suite
