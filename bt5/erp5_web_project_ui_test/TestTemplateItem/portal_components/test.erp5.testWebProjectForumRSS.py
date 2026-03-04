# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2026 Nexedi SA and Contributors. All Rights Reserved.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
##############################################################################

"""Positive-path coverage for the project-app RSS feed deep-link.

The feed form DiscussionForum_viewLatestPostListAsRSS lives in erp5_discussion,
but its item <link> is the project-app push_history_stored_state deep-link built
from Base_getProjectAppBaseUrl (erp5_project). erp5_discussion deliberately does
NOT depend on erp5_project (its own test asserts the decoupled case), so the
deep-link is exercised here, where erp5_project is a natural dependency.
"""

import unittest
from xml.dom.minidom import parseString
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


def getNodeContent(node):
  return node.childNodes[0].nodeValue


def getSubnodeContent(node, tag_name, index=0):
  try:
    return getNodeContent(node.getElementsByTagName(tag_name)[index])
  except IndexError:
    return None


class TestWebProjectForumRSS(ERP5TypeTestCase):
  """Project-app RSS feed deep-link (requires erp5_project)."""

  def getTitle(self):
    return "Test Web Project Forum RSS"

  def getBusinessTemplateList(self):
    return ('erp5_web_project_ui', 'erp5_web_project_ui_test')

  def beforeTearDown(self):
    self.abort()
    for module in (self.portal.discussion_thread_module,):
      module.manage_delObjects(list(module.objectIds()))
    self.tic()

  def _createForumThreadWithPosts(self, n_posts=2):
    """Published group-predicate forum + one shared thread with n_posts posts."""
    portal = self.portal
    existing = set(portal.discussion_thread_module.objectIds())
    group = portal.portal_categories.group.newContent(
      portal_type='Category', title='RSS Feed Group')
    forum = portal.getDefaultModule("Discussion Forum").newContent(
      portal_type="Discussion Forum")
    forum.setMultimembershipCriterionBaseCategoryList(['group'])
    forum.setMembershipCriterionCategoryList([group.getRelativeUrl()])
    forum.edit(criterion_property=("portal_type",))
    forum.setCriterion("portal_type", ["Discussion Thread"])
    forum.publish()
    forum.DiscussionForum_createNewDiscussionThread('rss-feed-thread', 'first post')
    self.tic()
    thread, = [x for x in portal.discussion_thread_module.objectValues()
               if x.getId() not in existing]
    for i in range(n_posts - 1):
      thread.DiscussionThread_createNewDiscussionPost(
        title='reply %d' % (i + 1), text_content='reply body %d' % (i + 1))
    self.tic()
    return forum, thread

  def test_rss_feed_link_uses_push_history_stored_state(self):
    """Each item <link> is the project-app push_history_stored_state deep-link
    seeding the forum (p.jio_key) and targeting the thread + last_post."""
    forum, thread = self._createForumThreadWithPosts(n_posts=2)
    base = forum.Base_getProjectAppBaseUrl()
    post_count = thread.DiscussionThread_getDiscussionPostCount()
    doc = parseString(forum.DiscussionForum_viewLatestPostListAsRSS())
    links = [l for l in
             (getSubnodeContent(i, 'link') for i in doc.getElementsByTagName('item'))
             if l]
    self.assertTrue(links, 'feed items must have a project-app <link>')
    for link in links:
      self.assertIn('#!push_history_stored_state', link)
      self.assertIn(base, link)
      self.assertIn('p.jio_key=%s' % forum.getRelativeUrl(), link)
      self.assertIn('n.jio_key=%s' % thread.getRelativeUrl(), link)
      self.assertIn('n.last_post=%s' % post_count, link)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(
    unittest.defaultTestLoader.loadTestsFromTestCase(TestWebProjectForumRSS))
  return suite
