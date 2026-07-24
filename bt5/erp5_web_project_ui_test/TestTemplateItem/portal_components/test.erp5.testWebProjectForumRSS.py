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
by the erp5_web_project_ui provider DiscussionPost_getAppItemRSSUrl, which
self-derives the app base from the request (portal.absolute_url()). erp5_discussion
deliberately does NOT depend on erp5_web_project_ui (its own test asserts the
decoupled case), so the deep-link is exercised here, where the provider is present.
"""

import unittest
from collections import OrderedDict
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
  """Project-app RSS feed deep-link (requires erp5_web_project_ui)."""

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
    # the item <link> self-derives the app base from the request (portal.absolute_url())
    base = self.portal.absolute_url()
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

  def test_thread_url_helper_builds_push_history_jio_key(self):
    """ListBox_getDiscussionThreadUrl (the SPA thread-row link) returns a
    push_history command whose jio_key is the thread relative url."""
    _, thread = self._createForumThreadWithPosts(n_posts=2)
    brain, = self.portal.portal_catalog(uid=thread.getUid())
    url_dict = self.portal.ListBox_getDiscussionThreadUrl(brain, url_dict=True)
    self.assertEqual('push_history', url_dict['command'])
    self.assertEqual(thread.getRelativeUrl(), url_dict['options']['jio_key'])

  def test_thread_last_post_url_helper_carries_post_count(self):
    """ListBox_getDiscussionThreadLastPostUrl adds last_post == the thread post
    count: the page the SPA/RSS deep-link jumps to. A wrong count silently
    sends the reader to the wrong page."""
    _, thread = self._createForumThreadWithPosts(n_posts=3)
    brain, = self.portal.portal_catalog(uid=thread.getUid())
    url_dict = self.portal.ListBox_getDiscussionThreadLastPostUrl(
      brain, url_dict=True)
    self.assertEqual(thread.getRelativeUrl(), url_dict['options']['jio_key'])
    self.assertEqual(3, thread.DiscussionThread_getDiscussionPostCount())
    self.assertEqual(3, url_dict['options']['last_post'])

  def test_last_post_widget_helpers_resolve_post_and_author(self):
    """The last-post / author SPA widgets are thin wrappers over
    DiscussionThread_getLastPost and DiscussionPost_getAuthorDict; assert those
    resolve a Discussion Post in the thread and an author dict with its keys."""
    _, thread = self._createForumThreadWithPosts(n_posts=2)
    last_post = thread.DiscussionThread_getLastPost()
    self.assertNotEqual(None, last_post)
    self.assertEqual('Discussion Post', last_post.getPortalType())
    self.assertEqual(thread.getRelativeUrl(),
                     last_post.getParentValue().getRelativeUrl())
    author_dict = last_post.DiscussionPost_getAuthorDict()
    for key in ('author_title', 'author_url', 'author_signature',
                'author_thumbnail_url'):
      self.assertIn(key, author_dict)
    self.assertTrue(author_dict['author_title'])

  def test_filter_project_actions_promotes_project_view_regardless_of_order(self):
    """Base_filterProjectActions must replace object_view with the project_view
    actions even when object_view is iterated AFTER project_view: the dict-order
    case that blanked the SPA (empty _links.view) before the ordering fix."""
    project_view_action_list = [
      {'id': 'project_view', 'title': 'Discussion Threads'}]
    # OrderedDict forces the previously-crashing order: object_view inserted last.
    actions = OrderedDict()
    actions['project_view'] = project_view_action_list
    actions['object_view'] = [{'id': 'view', 'title': 'View'},
                              {'id': 'view_rss', 'title': 'RSS'}]
    result = self.portal.Base_filterProjectActions(actions=actions)
    self.assertEqual(project_view_action_list, result['object_view'])
    self.assertEqual(project_view_action_list, result['project_view'])

  def test_filter_project_actions_without_project_view_keeps_only_named(self):
    """With no project_view category, object_view keeps only actions whose id
    contains 'project_view' (none here, so it is emptied, not left populated)."""
    actions = {'object_view': [{'id': 'view'}, {'id': 'view_rss'}]}
    result = self.portal.Base_filterProjectActions(actions=actions)
    self.assertEqual([], result['object_view'])


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(
    unittest.defaultTestLoader.loadTestsFromTestCase(TestWebProjectForumRSS))
  return suite
