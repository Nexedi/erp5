from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
import transaction
from httplib import OK as HTTP_OK

class TestDiscussionThread(SecurityTestCase):
  """
  A Sample Test Class
  """

  def getTitle(self):
    return "TestDiscussionThread"

  def getBusinessTemplateList(self):
    """
    A tuple of Business Templates names to specify the dependencies we need to
    install.
    """
    return (
      'erp5_base',
      'erp5_web',
      'erp5_ingestion_mysql_innodb_catalog',
      'erp5_ingestion',
      'erp5_dms',
      'erp5_forum_tutorial')

  def setUpOnce(self):
    """
       Create users to interact with the discussion forums
       This is ran only once
    """
    self.portal.portal_types['Person Module'].updateRoleMapping()
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
      self.createSimpleUser(**user)

  def afterSetUp(self):
    """
    This is ran before each and every test, used to set up the environment
    """
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
    self.assertUserCanAccessDocument('forum_user', self.forum_module)
    self.assertUserCanViewDocument('forum_user', self.forum_module)
    self.assertUserCanAddDocument('forum_user', self.forum_module)

    self.login('forum_user')

    thread_content='Hey, lets create a new thread!'
    thread = self._newThread(content=thread_content)

    # user should be able to access/view the created thread
    self.assertUserCanViewDocument('forum_user', thread)
    self.assertUserCanAccessDocument('forum_user', thread)
    self.assertUserCanAddDocument('forum_user', thread)

    # get thread posts
    thread_posts = thread.objectValues()

    # thread should have only one post
    self.assertEquals(len(thread_posts), 1)

    # that unique post should have the right content
    self.assertEquals(thread_posts[0].getTextContent(), thread_content)

    # Check that the thread is inserted in the forum module
    self.assertEquals(thread.getParentValue().getRelativeUrl(), self.forum_module.getRelativeUrl())

    # the thread should have been published
    self.assertEquals(thread.getValidationState(), 'public')

    reply_content='Can we add a reply?'
    post = thread.DiscussionThreadModule_addReply(
        title='A new reply',
        text_content=reply_content,
        form_id='DiscussionThreadModule_viewAddReplyDialog',
        batch_mode=True,
        )

    self.assertUserCanViewDocument('forum_user', post)
    self.assertUserCanAccessDocument('forum_user', post)

    transaction.commit()
    self.tic()

    thread_posts = thread.objectValues()

    # original thread and reply:
    # thread should have two posts
    self.assertEquals(len(thread_posts), 2)

    # Check that post was inserted in thread
    self.assertEquals(post.getParentValue().getRelativeUrl(), thread.getRelativeUrl())

  def testSpyCannotAccessButVisitorCan(self):
    """
    Unassigneds can't display threads, and visitor can:
        - user creates a thread
        - outsiders can't read the thread
        - visitor can read the thread
    """
    self.login('forum_user')
    thread = self._newThread()

    self.failIfUserCanViewDocument('spy', thread)
    self.failIfUserCanAccessDocument('spy', thread)

    self.assertUserCanViewDocument('visitor', thread)
    self.assertUserCanAccessDocument('visitor', thread)

    # Check that visitor has permissions on related objects
    # for example, if visitor has no permissions on the Person
    # module, the above checks will pass, but the view
    # will not work, because Person.getTitle() will fail

    self.assertUserCanViewDocument('visitor', self.portal.person_module)
    self.assertUserCanAccessDocument('visitor', self.portal.person_module)

    response = self.publish('/%s/%s' % \
                    (self.portal.getId(), thread.getRelativeUrl()),
                     'visitor:visitor'
                     )
    self.assertEquals(response.getStatus(), HTTP_OK)

  def testVisitorCannotPost(self):
    """
    Use case:
        - user creates a thread
        - visitor cannot reply
        - visitor cannot post a new thread
    """
    self.login('forum_user')
    thread = self._newThread()

    # visitor cannot reply to a thread
    self.failIfUserCanAddDocument('visitor', thread)
    # visitor cannot create a new thread
    self.failIfUserCanAddDocument('visitor', self.forum_module)

  def testAdminCanModerate(self):
    """
    Use case:
        - admin creates a thread
        - admin can display it
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
        - user creates thread
        - user cannot close it
    """
    self.login('forum_user')
    thread = self._newThread()

    self.assertUserCanPassWorkflowTransition('forum_user', 'close_action', thread)
    self.failIfUserCanPassWorkflowTransition('another_forum_user', 'close_action', thread)


  def testCanPostIfNotOwner(self):
    """
    Use case:
        - forum_user creates a thread
        - another_forum_user displays it
        - another_forum_user replies
    """
    self.login('forum_user')
    thread = self._newThread()

    # other user (not thread owner) can access and view the thread
    self.assertUserCanViewDocument('another_forum_user', thread)
    self.assertUserCanAccessDocument('another_forum_user', thread)
    # ... and can reply to thread even if he did not start it
    self.assertUserCanAddDocument('another_forum_user', thread)

    response = self.publish('/%s/%s' % \
                    (self.portal.getId(), thread.getRelativeUrl()),
                     'another_forum_user:another_forum_user'
                     )
    self.assertEquals(response.getStatus(), HTTP_OK)
