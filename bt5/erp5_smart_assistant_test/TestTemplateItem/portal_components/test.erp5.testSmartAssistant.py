##############################################################################
#
# Copyright (c) 2002-2018 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase

class TestSmartAssistant(SecurityTestCase):
  """
  A Sample Test Class
  """

  user_id_dict = {}
  
  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return ('erp5_base',)

  def afterSetUp(self):
    """
    This is ran before each and every test, used to set up the environment
    """
    user_list = [
      dict(title='Smart Assistant User 1', reference='smart_assistant_user1', function='smart_assistant/user'),
      dict(title='Smart Assistant User 2', reference='smart_assistant_user2', function='smart_assistant/user'),
      dict(title='Smart Assistant Miner', reference='smart_assistant_miner', function='smart_assistant/miner'),
      dict(title='Spy', reference='spy', function=None),
    ]

    for user in user_list:
      if not self.portal.acl_users.searchUsers(login=user['reference'], exact_match=True):
        self.user_id_dict[user['reference']] = \
          self.createSimpleUser(**user).Person_getUserId()

    self.commit()
    self.tic()

    self.smart_assistant_file_module = self.portal.getDefaultModule(portal_type='Smart Assistant File')
    self.assertTrue(self.smart_assistant_file_module is not None)
    self.smart_assistant_image_module = self.portal.getDefaultModule(portal_type='Smart Assistant Image')
    self.assertTrue(self.smart_assistant_image_module is not None)
    self.smart_assistant_sound_module = self.portal.getDefaultModule(portal_type='Smart Assistant Sound')
    self.assertTrue(self.smart_assistant_sound_module is not None)
    self.smart_assistant_text_module = self.portal.getDefaultModule(portal_type='Smart Assistant Text')
    self.assertTrue(self.smart_assistant_text_module is not None)
    
  def testUserCanCreateFileContent(self):
    """
    Use case:
        - user creates a document
        - that user can see it
        - that user can delete it
    """
    
    self.assertUserCanAccessDocument(self.user_id_dict['smart_assistant_user1'], self.smart_assistant_file_module)
    self.assertUserCanViewDocument(self.user_id_dict['smart_assistant_user1'], self.smart_assistant_file_module)
    self.assertUserCanAddDocument(self.user_id_dict['smart_assistant_user1'], self.smart_assistant_file_module)
    
    self.login(self.user_id_dict['smart_assistant_user1'])
    file = self.smart_assistant_file_module.newContent(title="test", portal_type='Smart Assistant File')
    
    self.assertUserCanViewDocument(self.user_id_dict['smart_assistant_user1'], file)
    self.assertUserCanAccessDocument(self.user_id_dict['smart_assistant_user1'], file)
    
    self.assertEqual(file.getParentValue().getRelativeUrl(), self.smart_assistant_file_module.getRelativeUrl())

    self.assertUserCanPassWorkflowTransition(self.user_id_dict['smart_assistant_user1'], 'delete_action', file)
    file.delete()
    self.failIfUserCanViewDocument(self.user_id_dict['smart_assistant_user1'], file)
    self.failIfUserCanAccessDocument(self.user_id_dict['smart_assistant_user1'], file)
    
  def testUserCanCreateImageContent(self):
    """
    Use case:
        - user creates a document
        - that user can see it
        - that user can delete it
    """
    
    self.assertUserCanAccessDocument(self.user_id_dict['smart_assistant_user1'], self.smart_assistant_image_module)
    self.assertUserCanViewDocument(self.user_id_dict['smart_assistant_user1'], self.smart_assistant_image_module)
    self.assertUserCanAddDocument(self.user_id_dict['smart_assistant_user1'], self.smart_assistant_image_module)
    
    self.login(self.user_id_dict['smart_assistant_user1'])
    image = self.smart_assistant_image_module.newContent(title="test", portal_type='Smart Assistant Image')
    
    self.assertUserCanViewDocument(self.user_id_dict['smart_assistant_user1'], image)
    self.assertUserCanAccessDocument(self.user_id_dict['smart_assistant_user1'], image)
    
    self.assertEqual(image.getParentValue().getRelativeUrl(), self.smart_assistant_image_module.getRelativeUrl())

    self.assertUserCanPassWorkflowTransition(self.user_id_dict['smart_assistant_user1'], 'delete_action', image)
    image.delete()
    self.failIfUserCanViewDocument(self.user_id_dict['smart_assistant_user1'], image)
    self.failIfUserCanAccessDocument(self.user_id_dict['smart_assistant_user1'], image)
    
  def testUserCanCreateSoundContent(self):
    """
    Use case:
        - user creates a document
        - that user can see it
        - that user can delete it
    """
    
    self.assertUserCanAccessDocument(self.user_id_dict['smart_assistant_user1'], self.smart_assistant_sound_module)
    self.assertUserCanViewDocument(self.user_id_dict['smart_assistant_user1'], self.smart_assistant_sound_module)
    self.assertUserCanAddDocument(self.user_id_dict['smart_assistant_user1'], self.smart_assistant_sound_module)
    
    self.login(self.user_id_dict['smart_assistant_user1'])
    sound = self.smart_assistant_sound_module.newContent(title="test", portal_type='Smart Assistant Sound')
    
    self.assertUserCanViewDocument(self.user_id_dict['smart_assistant_user1'], sound)
    self.assertUserCanAccessDocument(self.user_id_dict['smart_assistant_user1'], sound)
    
    self.assertEqual(sound.getParentValue().getRelativeUrl(), self.smart_assistant_sound_module.getRelativeUrl())

    self.assertUserCanPassWorkflowTransition(self.user_id_dict['smart_assistant_user1'], 'delete_action', sound)
    sound.delete()
    self.failIfUserCanViewDocument(self.user_id_dict['smart_assistant_user1'], sound)
    self.failIfUserCanAccessDocument(self.user_id_dict['smart_assistant_user1'], sound)
    
  def testUserCanCreateTextContent(self):
    """
    Use case:
        - user creates a document
        - that user can see it
        - that user can delete it
    """
    
    self.assertUserCanAccessDocument(self.user_id_dict['smart_assistant_user1'], self.smart_assistant_text_module)
    self.assertUserCanViewDocument(self.user_id_dict['smart_assistant_user1'], self.smart_assistant_text_module)
    self.assertUserCanAddDocument(self.user_id_dict['smart_assistant_user1'], self.smart_assistant_text_module)
    
    self.login(self.user_id_dict['smart_assistant_user1'])
    text = self.smart_assistant_text_module.newContent(title="test", portal_type='Smart Assistant Text')
    
    self.assertUserCanViewDocument(self.user_id_dict['smart_assistant_user1'], text)
    self.assertUserCanAccessDocument(self.user_id_dict['smart_assistant_user1'], text)
    
    self.assertEqual(text.getParentValue().getRelativeUrl(), self.smart_assistant_text_module.getRelativeUrl())

    self.assertUserCanPassWorkflowTransition(self.user_id_dict['smart_assistant_user1'], 'delete_action', text)
    text.delete()
    self.failIfUserCanViewDocument(self.user_id_dict['smart_assistant_user1'], text)
    self.failIfUserCanAccessDocument(self.user_id_dict['smart_assistant_user1'], text)
    
    
  def testSpyAndUserCannotAccessOtherUserFileContent(self):
    
    self.login(self.user_id_dict['smart_assistant_user1'])
    file = self.smart_assistant_file_module.newContent(title="test", portal_type='Smart Assistant File')

    self.failIfUserCanViewDocument(self.user_id_dict['spy'], file)
    self.failIfUserCanAccessDocument(self.user_id_dict['spy'], file)
    
    self.failIfUserCanViewDocument(self.user_id_dict['smart_assistant_user2'], file)
    self.failIfUserCanAccessDocument(self.user_id_dict['smart_assistant_user2'], file)
    
  def testSpyAndUserCannotAccessOtherUserImgaeContent(self):
    
    self.login(self.user_id_dict['smart_assistant_user1'])
    image = self.smart_assistant_image_module.newContent(title="test", portal_type='Smart Assistant Image')

    self.failIfUserCanViewDocument(self.user_id_dict['spy'], image)
    self.failIfUserCanAccessDocument(self.user_id_dict['spy'], image)
    
    self.failIfUserCanViewDocument(self.user_id_dict['smart_assistant_user2'], image)
    self.failIfUserCanAccessDocument(self.user_id_dict['smart_assistant_user2'], image)

  def testSpyAndUserCannotAccessOtherUserSoundContent(self):
    
    self.login(self.user_id_dict['smart_assistant_user1'])
    sound = self.smart_assistant_sound_module.newContent(title="test", portal_type='Smart Assistant Sound')

    self.failIfUserCanViewDocument(self.user_id_dict['spy'], sound)
    self.failIfUserCanAccessDocument(self.user_id_dict['spy'], sound)
    
    self.failIfUserCanViewDocument(self.user_id_dict['smart_assistant_user2'], sound)
    self.failIfUserCanAccessDocument(self.user_id_dict['smart_assistant_user2'], sound)
    
  def testSpyAndUserCannotAccessOtherUserTextContent(self):
    
    self.login(self.user_id_dict['smart_assistant_user1'])
    text = self.smart_assistant_text_module.newContent(title="test", portal_type='Smart Assistant Text')

    self.failIfUserCanViewDocument(self.user_id_dict['spy'], text)
    self.failIfUserCanAccessDocument(self.user_id_dict['spy'], text)
    
    self.failIfUserCanViewDocument(self.user_id_dict['smart_assistant_user2'], text)
    self.failIfUserCanAccessDocument(self.user_id_dict['smart_assistant_user2'], text)
    
  def testUserCannotValidateFileMinerCan(self):
    self.login(self.user_id_dict['smart_assistant_user1'])
    file = self.smart_assistant_file_module.newContent(title="test", portal_type='Smart Assistant File')
    
    self.assertUserCanPassWorkflowTransition(self.user_id_dict['smart_assistant_user1'], 'submit_action', file)
    file.submit()
    
    self.failIfUserCanPassWorkflowTransition(self.user_id_dict['smart_assistant_user1'], 'validate_action', file)
    
    self.login(self.user_id_dict['smart_assistant_miner'])
    self.assertUserCanPassWorkflowTransition(self.user_id_dict['smart_assistant_miner'], 'validate_action', file)
    file.validate()
    
  def testUserCannotValidateImageMinerCan(self):
    self.login(self.user_id_dict['smart_assistant_user1'])
    image = self.smart_assistant_image_module.newContent(title="test", portal_type='Smart Assistant Image')
    
    self.assertUserCanPassWorkflowTransition(self.user_id_dict['smart_assistant_user1'], 'submit_action', image)
    image.submit()
    
    self.failIfUserCanPassWorkflowTransition(self.user_id_dict['smart_assistant_user1'], 'validate_action', image)
    
    self.login(self.user_id_dict['smart_assistant_miner'])
    self.assertUserCanPassWorkflowTransition(self.user_id_dict['smart_assistant_miner'], 'validate_action', image)
    image.validate()
  
  def testUserCannotValidateSoundMinerCan(self):
    self.login(self.user_id_dict['smart_assistant_user1'])
    sound = self.smart_assistant_sound_module.newContent(title="test", portal_type='Smart Assistant Sound')
    
    self.assertUserCanPassWorkflowTransition(self.user_id_dict['smart_assistant_user1'], 'submit_action', sound)
    sound.submit()
    
    self.failIfUserCanPassWorkflowTransition(self.user_id_dict['smart_assistant_user1'], 'validate_action', sound)
    
    self.login(self.user_id_dict['smart_assistant_miner'])
    self.assertUserCanPassWorkflowTransition(self.user_id_dict['smart_assistant_miner'], 'validate_action', sound)
    sound.validate()
    
  def testUserCannotValidateTextMinerCan(self):
    self.login(self.user_id_dict['smart_assistant_user1'])
    text = self.smart_assistant_text_module.newContent(title="test", portal_type='Smart Assistant Text')
    
    self.assertUserCanPassWorkflowTransition(self.user_id_dict['smart_assistant_user1'], 'submit_action', text)
    text.submit()
    
    self.failIfUserCanPassWorkflowTransition(self.user_id_dict['smart_assistant_user1'], 'validate_action', text)
    
    self.login(self.user_id_dict['smart_assistant_miner'])
    self.assertUserCanPassWorkflowTransition(self.user_id_dict['smart_assistant_miner'], 'validate_action', text)
    text.validate()
    
  
    
  
    
    
    
    
    
    
    
