from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
from six.moves.http_client import OK as HTTP_OK

class TestDiscussionThread(SecurityTestCase):
  """
  A Sample Test Class
  """

  user_id_dict = {}

  def getTitle(self):
    return "TestDiscussionThread"

  def afterSetUp(self):
    """
    This is ran before each and every test, used to set up the environment
    """
    user_list = [
      # This is Dictator, a user of our portal and a forum admin
      dict(title='Dictator', reference='admin', function='forum/administrator'),
      # This is "Forum User", a user of our portal. He's funny, but has no administrative power
      dict(title='Forum User', reference='forum_user', function='forum/user'),
      # This is yet another user. He has no administrative power
      dict(title='Another Forum User', reference='another_forum_user', function='forum/user'),
      # This is a Lurker. He is lurking in the forum, but is not an User
      dict(title='Forum visitor', reference='visitor', function='forum/visitor'),
      # This is a Spy. He has an ERP5 account, but no specific forum access.
      dict(title='Spy', reference='spy', function=None),
    ]
    # now we create the users
    for user in user_list:
      if not self.portal.acl_users.searchUsers(login=user['reference'], exact_match=True):
        self.user_id_dict[user['reference']] = \
          self.createSimpleUser(**user).Person_getUserId()

    self.commit()
    self.tic()

    self.forum_module = self.portal.getDefaultModule(portal_type='Discussion Thread')
    self.assertTrue(self.forum_module is not None)

  def _newThread(self, content=''):
    """Helper function to create a new Thread"""
    return self.forum_module.DiscussionThreadModule_addThread(
        title='Some title',
        text_content=content,
        form_id='DiscussionThreadModule_viewAddThreadDialog',
        batch_mode=True,
        )

  def testUserCanCreateContent(self):
    """
    Use case:
        - user creates a thread
        - that user can see it
        - that user can reply to his thread
    """
    # forum_user should be able to access/view the forum module
    self.assertUserCanAccessDocument(self.user_id_dict['forum_user'], self.forum_module)
    self.assertUserCanViewDocument(self.user_id_dict['forum_user'], self.forum_module)
    self.assertUserCanAddDocument(self.user_id_dict['forum_user'], self.forum_module)

    self.login(self.user_id_dict['forum_user'])

    thread_content='Hey, lets create a new thread!'
    thread = self._newThread(content=thread_content)

    # user should be able to access/view the created thread
    self.assertUserCanViewDocument(self.user_id_dict['forum_user'], thread)
    self.assertUserCanAccessDocument(self.user_id_dict['forum_user'], thread)
    self.assertUserCanAddDocument(self.user_id_dict['forum_user'], thread)

    # get thread posts
    thread_posts = thread.objectValues()

    # thread should have only one post
    self.assertEqual(len(thread_posts), 1)

    # that unique post should have the right content
    self.assertEqual(thread_posts[0].getTextContent(), thread_content)

    # Check that the thread is inserted in the forum module
    self.assertEqual(thread.getParentValue().getRelativeUrl(), self.forum_module.getRelativeUrl())

    # the thread should have been published
    self.assertEqual(thread.getValidationState(), 'public')

    reply_content='Can we add a reply?'
    post = thread.DiscussionThreadModule_addReply(
        title='A new reply',
        text_content=reply_content,
        form_id='DiscussionThreadModule_viewAddReplyDialog',
        batch_mode=True,
        )

    self.assertUserCanViewDocument(self.user_id_dict['forum_user'], post)
    self.assertUserCanAccessDocument(self.user_id_dict['forum_user'], post)

    self.tic()

    thread_posts = thread.objectValues()

    # original thread and reply:
    # thread should have two posts
    self.assertEqual(len(thread_posts), 2)

    # Check that post was inserted in thread
    self.assertEqual(post.getParentValue().getRelativeUrl(), thread.getRelativeUrl())

  def testSpyCannotAccessButVisitorCan(self):
    """
    Unassigneds can't display threads, and visitor can:
        - user creates a thread
        - outsiders can't read the thread
        - visitor can read the thread
    """
    self.login(self.user_id_dict['forum_user'])
    thread = self._newThread()

    self.failIfUserCanViewDocument(self.user_id_dict['spy'], thread)
    self.failIfUserCanAccessDocument(self.user_id_dict['spy'], thread)

    self.assertUserCanViewDocument(self.user_id_dict['visitor'], thread)
    self.assertUserCanAccessDocument(self.user_id_dict['visitor'], thread)

    # Check that visitor has permissions on related objects
    # for example, if visitor has no permissions on the Person
    # module, the above checks will pass, but the view
    # will not work, because Person.getTitle() will fail

    self.assertUserCanViewDocument(self.user_id_dict['visitor'], self.portal.person_module)
    self.assertUserCanAccessDocument(self.user_id_dict['visitor'], self.portal.person_module)

    response = self.publish('/%s/%s' % \
                    (self.portal.getId(), thread.getRelativeUrl()),
                     'visitor:visitor'
                     )
    self.assertEqual(response.getStatus(), HTTP_OK)

  def testVisitorCannotPost(self):
    """
    Use case:
        - user creates a thread
        - visitor cannot reply
        - visitor cannot post a new thread
    """
    self.login(self.user_id_dict['forum_user'])
    thread = self._newThread()

    # visitor cannot reply to a thread
    self.failIfUserCanAddDocument(self.user_id_dict['visitor'], thread)
    # visitor cannot create a new thread
    self.failIfUserCanAddDocument(self.user_id_dict['visitor'], self.forum_module)

  def testAdminCanModerate(self):
    """
    Use case:
        - admin creates a thread
        - admin can display it
        - admin closes it
        - admin can display it
        - admin reopens it
    """
    self.login(self.user_id_dict['admin'])
    thread = self._newThread()

    self.assertUserCanPassWorkflowTransition(self.user_id_dict['admin'], 'close_action', thread)
    thread.close()
    self.commit()

    self.assertUserCanViewDocument(self.user_id_dict['admin'], thread)
    self.assertUserCanAccessDocument(self.user_id_dict['admin'], thread)
    self.assertUserCanPassWorkflowTransition(self.user_id_dict['admin'], 'unclose_action', thread)

  def testUserCannotModerate(self):
    """
    Use case:
        - user creates thread
        - user cannot close it
    """
    self.login(self.user_id_dict['forum_user'])
    thread = self._newThread()

    self.assertUserCanPassWorkflowTransition(self.user_id_dict['forum_user'], 'close_action', thread)
    self.failIfUserCanPassWorkflowTransition(self.user_id_dict['another_forum_user'], 'close_action', thread)


  def testCanPostIfNotOwner(self):
    """
    Use case:
        - forum_user creates a thread
        - another_forum_user displays it
        - another_forum_user replies
    """
    self.login(self.user_id_dict['forum_user'])
    thread = self._newThread()

    # other user (not thread owner) can access and view the thread
    self.assertUserCanViewDocument(self.user_id_dict['another_forum_user'], thread)
    self.assertUserCanAccessDocument(self.user_id_dict['another_forum_user'], thread)
    # ... and can reply to thread even if he did not start it
    self.assertUserCanAddDocument(self.user_id_dict['another_forum_user'], thread)

    response = self.publish('/%s/%s' % \
                    (self.portal.getId(), thread.getRelativeUrl()),
                     'another_forum_user:another_forum_user'
                     )
    self.assertEqual(response.getStatus(), HTTP_OK)
