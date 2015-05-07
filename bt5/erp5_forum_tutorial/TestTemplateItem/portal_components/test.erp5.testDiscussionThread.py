##############################################################################
#
# Copyright (c) 2002-2015 Nexedi SA and Contributors. All Rights Reserved.
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
from httplib import OK as HTTP_OK
import transaction

class TestDiscussionThread(SecurityTestCase):
  """
  A Sample Test Class
  """

  def getTitle(self):
    return "Test Discussion thread"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return ('erp5_base',
        'erp5_web',
       'erp5_ingestion_mysql_innodb_catalog',
       'erp5_ingestion',
       'erp5_dms',
       'erp5_forum_tutorial')

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """

    user_list=[
        dict(title='Dictator', reference='admin', function='forum/administrator'),
        dict(title='Forum User', reference='forum_user', function='forum/user'),
        dict(title='Another_Forum_user', reference='another_forum_user', function='forum/user'),
        dict(title='Forum Visitor', reference='visitor', function='forum/visitor'),
        dict(title='Spy', reference='spy', function=None),
       ]

    for user in user_list:
      if len(self.portal.portal_catalog(portal_type='Person', reference=user['reference']))==0:
        self.createSimpleUser(**user)
#    self.tic()
    self.forum_module = self.portal.getDefaultModule(portal_type='Discussion Thread')
    self.assertTrue(self.forum_module is not None)

  def _newThread(self, content=''):
    """Helper function to create new Thread"""
    return self.forum_module.DiscussionThreadModule_addThread(
      title='Some title',
      text_content=content,
      form_id='DiscussionThreadModule_viewAddThreadDialog',
      batch_mode=True
      )
      
  def testUserCanCreateContent(self):
    """
    Use case:
    - user creates a thread
    - that user can see it
    - that user can reply to this thread
    """
    # forum user should be able to access/view the forum module
    self.assertUserCanViewDocument('forum_user', self.forum_module)
    self.assertUserCanAccessDocument('forum_user', self.forum_module)
    self.assertUserCanAddDocument('forum_user', self.forum_module)

    self.login('forum_user')
  
    thread_content="Hey, let's create a new thread!"
    thread = self._newThread(content=thread_content)
  
    self.assertUserCanViewDocument('forum_user', thread)
    self.assertUserCanAccessDocument('forum_user', thread)
    self.assertUserCanAddDocument('forum_user', thread)
  
    thread_posts = thread.objectValues()
    self.assertEquals(len(thread_posts), 1)
    self.assertEquals(thread_posts[0].getTextContent(), thread_content)
    self.assertEquals(thread.getParentValue().getRelativeUrl(), self.forum_module.getRelativeUrl())
    self.assertEquals(thread.getValidationState(), 'public')
  
    reply_content = 'Can we add a reply?'
    post = thread.DiscussionThreadModule_addReply(
      title='A new reply',
      text_content = reply_content,
      form_id = 'DiscussionThreadModule_viewAddReplyDialog',
      batch_mode=True,
    )
    
    self.assertUserCanViewDocument('forum_user', post)
    self.assertUserCanAccessDocument('forum_user', post)
  
    transaction.commit()
    self.tic()
  
    thread_posts = thread.objectValues()
  
    self.assertEquals(len(thread_posts), 2)

    self.assertEquals(len(thread.searchFolder(SearchableText=reply_content)), 1)
    self.assertEquals(post.getParentValue().getRelativeUrl(), thread.getRelativeUrl())
  
  def testSpyCannotAccessButVisitorCan(self):
    """
    Unassigned can't display threads, and visitor can:
      - user creates a thread
      - outsiders can't read hthe thread
      - visitors can read the thread
    """
    self.login('forum_user')
    thread =self._newThread()
  
    self.failIfUserCanViewDocument('spy', thread)
    self.failIfUserCanAccessDocument('spy', thread)
  
    self.assertUserCanViewDocument('visitor', thread)
    self.assertUserCanAccessDocument('visitor', thread)
  
    self.assertUserCanAccessDocument('visitor', self.portal.person_module.searchFolder(reference='forum_user')[0].getObject())
  
  def testVisistorsCannotPost(self):
    """
    Use case:
      - user creates a thread
      - visitor cannot reply
      - visitor cannot post a thread 
    """
    self.login('forum_user')
    thread = self._newThread()
    
    self.failIfUserCanAddDocument('visitor', thread)
    self.failIfUserCanAddDocument('visitor', self.forum_module)
    
  def testAdminCanModerate(self):
    """
    Use case:
      - admin creates a thread
      - admin closes it
      - admin can display it
      - admin reopens it
    """
    self.login('admin')
    thread = self._newThread()
    
    self.assertUserCanPassWorkflowTransition('admin', 'close_action', thread)
    thread.close()
    transaction.commit()
    
    self.assertUserCanViewDocument('admin', thread)
    self.assertUserCanAccessDocument('admin', thread)
    self.assertUserCanPassWorkflowTransition('admin', 'unclose_action', thread)
  
  def testUserCannotModerate(self):
    """
    Use case:
      - user creates a thread
      - user cannot close it
    """
    self.login('forum_user')
    thread  = self._newThread()
    
    self.assertUserCanPassWorkflowTransition('forum_user', 'close_action', thread)
    self.failIfUserCanPassWorkflowTransition('another_forum_user', 'close_action', thread)
    
  def testHiddenState(self):
    """
    Use case:
      - forum creates a thread
      - admin hides it
      - forum_user still see his thread
      - and can reply
      - but another forum_user cannot display it
      - user cannot unhide it
    """
    self.login('forum_user')
    thread  = self._newThread()

    self.failIfUserCanPassWorkflowTransition('another_forum_user', 'unhide_action', thread)
      
  def testCanPostIfNotOwner(self):
    """
    Use case:
      - forum_user creates a thread
      - another_forum_user displays it
      - another_forum_user replies 
    """
    self.login('forum_user')
    thread = self._newThread()
      
    self.assertUserCanViewDocument('another_forum_user', thread)
    self.assertUserCanAccessDocument('another_forum_user', thread)
    self.assertUserCanAddDocument('another_forum_user', thread)