# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors.
# All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
#          Fabien MORIN <fabien@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import unittest
from AccessControl.SecurityManagement import newSecurityManager
from erp5.component.test.testDms import DocumentUploadTestCase


class TestERP5Discussion(DocumentUploadTestCase):
  """Test for erp5_discussion business template.
  """

  manager_username = 'manager'
  manager_password = 'pwd'

  def getTitle(self):
    return "Test ERP5 Discussion"

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_core',
            'erp5_base',
            'erp5_xhtml_style',
            'erp5_ingestion',
            'erp5_web',
            'erp5_dms',
            'erp5_knowledge_pad',
            'erp5_rss_style',
            'erp5_jquery',
            'erp5_discussion', )

  def login(self, *args, **kw):
    uf = self.getPortal().acl_users
    uf._doAddUser(self.manager_username, self.manager_password, ['Manager'], [])
    user = uf.getUserById(self.manager_username).__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    self.login()
    self.portal_id = self.portal.getId()
    self.auth = '%s:%s' % (self.manager_username, self.manager_password)

  def beforeTearDown(self):
    self.abort()
    for module in (self.portal.discussion_thread_module,):
      module.manage_delObjects(list(module.objectIds()))
    self.tic()

  def stepCreateThread(self):

    module =  self.portal.getDefaultModule("Discussion Thread")
    return module.newContent(portal_type="Discussion Thread")

  def stepCreatePost(self,thread):
    return thread.newContent(portal_type="Discussion Post")

  def test_01_createDiscussionThread(self):
    """Create a new discussion thread"""

    self.stepCreateThread()
    self.tic()

  def test_02_createDiscussionPost(self):
    """Create a disucssion post inside a discussion thread"""

    thread = self.stepCreateThread()
    post = self.stepCreatePost(thread)
    # post is not indexed yet
    self.assertSameSet([], thread.DiscussionThread_getDiscussionPostList())

    # not indexed but its relative url is passed through REQUEST
    self.app.REQUEST.set('post_relative_url', post.getRelativeUrl())
    self.assertSameSet([post], thread.DiscussionThread_getDiscussionPostList())
    self.tic()

    # indexed already
    self.assertSameSet([post], thread.DiscussionThread_getDiscussionPostList())

  def test_03_createDiscussionThread(self):
    """
      Create a disucssion thread
    """
    portal = self.portal
    discussion_thread_id_set = set(portal.discussion_thread_module.objectIds())

    # create web sections & set predicates
    group1 = portal.portal_categories.group.newContent(portal_type='Category',
                                                       title = 'Group 1')
    web_site = portal.web_site_module.newContent(portal_type='Web Site')
    web_section1 = web_site.newContent(portal_type='Web Section')
    web_section1.setMultimembershipCriterionBaseCategoryList(['group'])
    web_section1.setMembershipCriterionCategoryList([group1.getRelativeUrl()])
    self.tic()

    web_section1.WebSection_createNewDiscussionThread('test1-new', 'test1 body')
    discussion_thread, = [x for x in self.portal.discussion_thread_module.objectValues() \
                          if x.getId() not in discussion_thread_id_set]
    discussion_thread_id_set.add(discussion_thread.getId())
    self.assertTrue(discussion_thread.getReference().startswith("test1-new-"))
    # not indexed yet
    self.assertSameSet([], web_section1.WebSection_getDiscussionThreadList())

    # not indexed but its relative url is passed through REQUEST
    self.app.REQUEST.set('thread_relative_url', discussion_thread.getRelativeUrl())
    self.assertSameSet([discussion_thread], web_section1.WebSection_getDiscussionThreadList())

    self.tic()
    # indexed already
    self.assertSameSet([discussion_thread], web_section1.WebSection_getDiscussionThreadList())
    discussion_post = discussion_thread.contentValues(filter={'portal_type': 'Discussion Post'})[0]
    attachment_list = discussion_post.DiscussionPost_getAttachmentList()
    self.assertEqual(discussion_thread.getValidationState(), 'published')
    self.assertEqual(0, len(attachment_list))

    # check attachment creation
    file_ = self.makeFileUpload('TEST-en-002.doc')
    web_section1.WebSection_createNewDiscussionThread('test1-new-with-attachment', 'test1 body', file=file_)
    discussion_thread, = [x for x in self.portal.discussion_thread_module.objectValues() \
                          if x.getId() not in discussion_thread_id_set]
    discussion_thread_id_set.add(discussion_thread.getId())
    self.assertTrue(discussion_thread.getReference().startswith("test1-new-with-attachment-"))
    self.tic()

    discussion_post = discussion_thread.contentValues(filter={'portal_type': 'Discussion Post'})[0]
    attachment_list = discussion_post.DiscussionPost_getAttachmentList()
    self.assertEqual(discussion_thread.getValidationState(), 'published')
    self.assertEqual(1, len(attachment_list))

  def test_MultipleForum(self):
    """
      Test multiple forums may exists within same ERP5 Web Site.
    """
    portal = self.portal

    # create web sections & set predicates
    group1 = portal.portal_categories.group.newContent(portal_type='Category',
                                                       title = 'Group 1')
    group2 = portal.portal_categories.group.newContent(portal_type='Category',
                                                       title = 'Group 2')
    web_site = portal.web_site_module.newContent(portal_type='Web Site')
    web_section1 = web_site.newContent(portal_type='Web Section')
    web_section2 = web_site.newContent(portal_type='Web Section')
    web_section1.setMultimembershipCriterionBaseCategoryList(['group'])
    web_section1.setMembershipCriterionCategoryList([group1.getRelativeUrl()])
    web_section2.setMultimembershipCriterionBaseCategoryList(['group'])
    web_section2.setMembershipCriterionCategoryList([group2.getRelativeUrl()])
    self.tic()

    # add threads on Web Section context
    web_section1.WebSection_createNewDiscussionThread('test1', 'test1 body')
    web_section2.WebSection_createNewDiscussionThread('test2', 'test2 body')
    self.tic()
    discussion_thread_object1 = portal.portal_catalog.getResultValue(portal_type = 'Discussion Thread',
                                                                    title = 'test1')
    discussion_thread_object2 = portal.portal_catalog.getResultValue(portal_type = 'Discussion Thread',
                                                                    title = 'test2')
    self.assertEqual(group1, discussion_thread_object1.getGroupValue())
    self.assertEqual(group2, discussion_thread_object2.getGroupValue())

    # check getDocumentValue.. on Web Section context (by default forum is public
    # so threads should be part of document list)
    self.assertSameSet([discussion_thread_object1], [x.getObject() for x  in web_section1.getDocumentValueList()])
    self.assertSameSet([discussion_thread_object2], [x.getObject() for x  in web_section2.getDocumentValueList()])

    # test RSS generation by testing indirectly its "get" method
    # (new post should be first in list)
    current_post_list = list(discussion_thread_object1.objectValues())
    new_post = discussion_thread_object1.newContent()
    self.tic()
    self.assertSameSet([new_post] + current_post_list, [x.getObject() for x in web_section1.WebSection_getLatestDiscussionPostList()])

    # test archiving threads so the do not belong any more to web section document list
    discussion_thread_object1.archive()
    discussion_thread_object2.archive()
    self.tic()

    self.assertSameSet([], web_section1.getDocumentValueList())
    self.assertSameSet([], web_section2.getDocumentValueList())

    # test new thread reference do no overlap any other traversable object
    web_section1.WebSection_createNewDiscussionThread(web_section1.getId(), 'test reference using web section')
    web_section1.WebSection_createNewDiscussionThread('image_module', 'test1 body')
    web_section1.WebSection_createNewDiscussionThread('manage_main', 'test1 body')
    self.tic()
    self.assertNotEqual(web_section1.getId(),
                        portal.portal_catalog.getResultValue(
                          portal_type = 'Discussion Thread',
                          title = web_section1.getId()).getReference())
    self.assertNotEqual('image_module',
                        portal.portal_catalog.getResultValue(
                          portal_type = 'Discussion Thread',
                          title = 'image_module').getReference())
    self.assertNotEqual('manage_main',
                        portal.portal_catalog.getResultValue(
                          portal_type = 'Discussion Thread',
                          title = 'manage_main').getReference())

  def test_02_ReferenceGenerationFromString(self):
    s = "a test by ivan !@#$%^&*()[]\\é"
    self.assertEqual('a-test-by-ivan', self.portal.Base_generateReferenceFromString(s))

  def test_AttachmentIngestion(self):
    """
    Test the attachment of a CSV file, from both newDiscussionPost and newDiscussionThread
    use cases.
    CSV wasn't chosen randomly, as it may be subjected to a portal type migration through
    discover metadata, which used to cause a bug.
    """
    discussion_thread_id_set = set(self.portal.discussion_thread_module.objectIds())

    web_site_value = self.portal.web_site_module.newContent(portal_type='Web Site')
    web_section_value = web_site_value.newContent(portal_type='Web Section')
    file_ = self.makeFileUpload('simple.csv')
    web_section_value.WebSection_createNewDiscussionThread(
      "Thread Title",
      "Post Content",
      file=file_
    )
    self.tic()
    thread_value, = [
      x for x in self.portal.discussion_thread_module.objectValues()
      if x.getId() not in discussion_thread_id_set
    ]

    post_value, = thread_value.objectValues(portal_type='Discussion Post')
    tested_post_value_set = {post_value,}
    attachment_list = post_value.DiscussionPost_getAttachmentList()
    self.assertEqual(1, len(attachment_list))

    thread_value.DiscussionThread_createNewDiscussionPost(
      title="Post Title",
      text_content="Post Content",
      file=file_,
    )
    self.tic()
    post_value, = [
      x for x in thread_value.objectValues()
      if x not in tested_post_value_set
    ]
    attachment_list = post_value.DiscussionPost_getAttachmentList()
    self.assertEqual(1, len(attachment_list))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Discussion))
  return suite
