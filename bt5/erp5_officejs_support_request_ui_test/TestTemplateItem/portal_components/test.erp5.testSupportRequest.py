##############################################################################
#
# Copyright (c) 2018- Nexedi SA and Contributors. All Rights Reserved.
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
import json
from StringIO import StringIO
import urlparse
import httplib

import feedparser
from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class FileUpload(StringIO):
  filename = 'attached_file.txt'


def ignoreKeys(list_of_dict, *ignored):
  """remove some keys from each dict dict to compare except some ignored keys.
  """
  new_list = []
  for d in list_of_dict:
    d = d.copy()
    for k in ignored:
      d.pop(k, None)
    new_list.append(d)
  return new_list


class SupportRequestTestCase(ERP5TypeTestCase, object):
  def afterSetUp(self):
    ERP5TypeTestCase.afterSetUp(self)
    self.assertEqual(self.portal.ERP5Site_setupSupportRequestPreference(), 'Done.')
    self.tic()
    self.assertEqual(self.portal.ERP5Site_createSupportRequestUITestDataSet(), 'Done.')
    self.tic()
    self.createUserAndLogin()

  def beforeTearDown(self):
    self.abort()
    self.tic()
    self.portal.person_module.manage_delObjects(
        [self.user.getId()])
    self.assertEqual(self.portal.ERP5Site_cleanupSupportRequestUITestDataSet(), 'Done.')
    self.tic()

  def createUserAndLogin(self):
    self.user = self.portal.person_module.newContent(
        first_name=self.id()
    )
    self.user.newContent(
        portal_type='Assignment'
    ).open()
    self.user_password = self.newPassword()
    self.user.newContent(
        id='erp5_login',
        portal_type='ERP5 Login',
        reference=self.user.getUserId(), # XXX workaround until https://lab.nexedi.com/nexedi/erp5/merge_requests/478
        password=self.user_password
    ).validate()
    self.user.validate()
    self.tic()
    # give this user some roles
    for role in ('Assignee', 'Assignor', 'Auditor',):
      self.portal.acl_users.zodb_roles.assignRoleToPrincipal(
          role, self.user.getUserId())
    self.tic()
    self.login(self.user.getUserId())

  def getWebSite(self):
    return self.portal.web_site_module.erp5_officejs_support_request_ui


class TestSupportRequestCreateNewSupportRequest(SupportRequestTestCase):
  def test_submit_support_request(self):
    self.getWebSite().SupportRequestModule_createSupportRequest(
        description='<b>Help !!!</b>',
        file=None,
        resource=self.portal.service_module.erp5_officejs_support_request_ui_test_service_001.getRelativeUrl(),
        title=self.id(),
        project='erp5_officejs_support_request_ui_test_project_001',
        # FIXME: project passed by the UI should be full relative URL
        #project=self.portal.project_module.erp5_officejs_support_request_ui_test_project_001.getRelativeUrl()
        source_reference='xxx-message-id'
    )
    # this creates synchronoulsy a support request
    support_request, = [sr for sr in self.portal.support_request_module.contentValues()
        if sr.getTitle() == self.id()]
    # the API to get comments works before ingestion, thanks to portal_session
    self.assertEqual(
      [dict(
        user=self.user.getTitle(),
        text='<b>Help !!!</b>',
        attachment_link=None,
        attachment_name=None,
        message_id='xxx-message-id'),],
      ignoreKeys(
          json.loads(support_request.SupportRequest_getCommentPostListAsJson()),
          'date'))

    # another activity will create a web message
    self.tic()
    self.assertEqual(
        'submitted',
        support_request.getSimulationState()
    )
    self.assertEqual(
        self.portal.project_module.erp5_officejs_support_request_ui_test_project_001,
        support_request.getSourceProjectValue()
    )
    self.assertEqual(
        self.portal.service_module.erp5_officejs_support_request_ui_test_service_001,
        support_request.getResourceValue()
    )
    self.assertEqual(self.user, support_request.getDestinationDecisionValue())
    web_message, = support_request.getFollowUpRelatedValueList(
        portal_type='Web Message'
    )
    self.assertEqual('stopped', web_message.getSimulationState())
    self.assertEqual('<b>Help !!!</b>', web_message.asStrippedHTML())
    self.assertEqual(self.user, web_message.getSourceValue())
    self.assertIsNotNone(web_message.getResourceValue())
    self.assertIsNotNone(web_message.getStartDate())

    # there's a html post
    post, = web_message.getAggregateValueList(
        portal_type='HTML Post'
    )
    self.assertEqual('<b>Help !!!</b>', str(post.getData()))
    # post have been archived once ingested
    self.assertEqual('archived', post.getValidationState())

    # the API to get comments works even after ingested
    self.assertEqual(
      [dict(
          user=self.user.getTitle(),
          text='<b>Help !!!</b>',
          date=web_message.getStartDate().ISO8601(),
          attachment_link=None,
          attachment_name=None,
          message_id='xxx-message-id'),],
      json.loads(support_request.SupportRequest_getCommentPostListAsJson()))

  def test_submit_support_request_with_attachment(self):
    self.getWebSite().SupportRequestModule_createSupportRequest(
        description='<b>Look at this file !</b>',
        file=FileUpload("the text content"),
        resource=self.portal.service_module.erp5_officejs_support_request_ui_test_service_001.getRelativeUrl(),
        title=self.id(),
        project='erp5_officejs_support_request_ui_test_project_001',
        # FIXME: project passed by the UI should be full relative URL
        #project=self.portal.project_module.erp5_officejs_support_request_ui_test_project_001.getRelativeUrl()
        source_reference='xxx-message-id',
    )
    support_request, = [sr for sr in self.portal.support_request_module.contentValues()
        if sr.getTitle() == self.id()]
    # the API to get comments works before ingestion, thanks to portal_session
    self.assertEqual(
      [dict(
          user=self.user.getTitle(),
          text='<b>Look at this file !</b>',
          attachment_name='attached_file.txt',
          message_id='xxx-message-id'),],
      ignoreKeys(
          json.loads(support_request.SupportRequest_getCommentPostListAsJson()),
          'date',
          'attachment_link'))

    self.tic()
    web_message, = support_request.getFollowUpRelatedValueList(
        portal_type='Web Message'
    )
    self.assertEqual('stopped', web_message.getSimulationState())
    self.assertEqual('<b>Look at this file !</b>', web_message.asStrippedHTML())

    # there's a html post
    post, = web_message.getAggregateValueList(
        portal_type='HTML Post'
    )
    self.assertEqual('<b>Look at this file !</b>', str(post.getData()))
    file_post, = post.getSuccessorValueList()
    self.assertEqual('the text content', str(file_post.getData()))

    # a text was ingested from the file post
    file_document, = web_message.getAggregateValueList(
        portal_type='Text'
    )
    self.assertEqual('attached_file.txt', file_document.getFilename())
    self.assertEqual('the text content', str(file_document.getData()))

    self.assertEqual(
      [dict(
          user=self.user.getTitle(),
          text='<b>Look at this file !</b>',
          date=web_message.getStartDate().ISO8601(),
          attachment_name='attached_file.txt',
          attachment_link=file_document.getRelativeUrl(),
          message_id='xxx-message-id')],
      json.loads(support_request.SupportRequest_getCommentPostListAsJson()))


class TestSupportRequestCommentOnExistingSupportRequest(SupportRequestTestCase):
  def test_comment_on_support_request(self):
    support_request = self.portal.support_request_module.erp5_officejs_support_request_ui_test_support_reuqest_001
    self.portal.PostModule_createHTMLPostForSupportRequest(
        follow_up=support_request.getRelativeUrl(),
        predecessor=None,
        data="<p>Hello !</p>",
        file=None,
        source_reference="xxx-message-id",
        web_site_relative_url=self.getWebSite().getRelativeUrl(),
    )
   # the API to get comments works before ingestion, thanks to portal_session
    self.assertEqual(
      [dict(
          user=self.user.getTitle(),
          text='<p>Hello !</p>',
          attachment_link=None,
          attachment_name=None,
          message_id='xxx-message-id'),],
      ignoreKeys(
         json.loads(support_request.SupportRequest_getCommentPostListAsJson()),
         'date'))
    self.tic()
    web_message, = support_request.getFollowUpRelatedValueList(
        portal_type='Web Message'
    )
    self.assertEqual('<p>Hello !</p>', web_message.asStrippedHTML())

    # the API to get comments also works once ingested
    self.assertEqual(
      [dict(
        user=self.user.getTitle(),
        text='<p>Hello !</p>',
        date=web_message.getStartDate().ISO8601(),
        attachment_link=None,
        attachment_name=None,
        message_id='xxx-message-id'),],
      json.loads(support_request.SupportRequest_getCommentPostListAsJson()))

  def test_comment_on_support_request_with_attachment(self):
    support_request = self.portal.support_request_module.erp5_officejs_support_request_ui_test_support_reuqest_001
    self.portal.PostModule_createHTMLPostForSupportRequest(
        follow_up=support_request.getRelativeUrl(),
        predecessor=None,
        data="<p>Please look at the <b>attached file</b></p>",
        file=FileUpload("the text content"),
        source_reference="xxx-message-id",
        web_site_relative_url=self.getWebSite().getRelativeUrl(),
    )
   # the API to get comments works before ingestion, thanks to portal_session
    self.assertEqual(
      [dict(
          user=self.user.getTitle(),
          text='<p>Please look at the <b>attached file</b></p>',
          attachment_name='attached_file.txt',
          message_id='xxx-message-id'),],
      ignoreKeys(
         json.loads(support_request.SupportRequest_getCommentPostListAsJson()),
         'date', 'attachment_link'))
    self.tic()
    web_message, = support_request.getFollowUpRelatedValueList(
        portal_type='Web Message'
    )

    self.assertEqual('<p>Please look at the <b>attached file</b></p>', web_message.asStrippedHTML())

    # a text document was ingested from the file post
    file_document, = web_message.getAggregateValueList(
        portal_type='Text'
    )
    self.assertEqual('attached_file.txt', file_document.getFilename())
    self.assertEqual('the text content', str(file_document.getData()))
    self.assertEqual('shared', file_document.getValidationState())
    # this document is also attached to the context of the support request
    # and is visible from the document tab.
    self.assertIn(
        file_document,
        [doc.getObject() for doc in support_request.Base_getRelatedDocumentList()])

    # the API to get comments also works once ingested
    self.assertEqual(
      [dict(
        user=self.user.getTitle(),
        text='<p>Please look at the <b>attached file</b></p>',
        date=web_message.getStartDate().ISO8601(),
        attachment_link=file_document.getRelativeUrl(),
        attachment_name='attached_file.txt',
        message_id='xxx-message-id'),],
      json.loads(support_request.SupportRequest_getCommentPostListAsJson()))

  def test_html_escape(self):
    support_request = self.portal.support_request_module.erp5_officejs_support_request_ui_test_support_reuqest_001
    self.portal.PostModule_createHTMLPostForSupportRequest(
        follow_up=support_request.getRelativeUrl(),
        predecessor=None,
        data="<p>look <script>alert('haha')</script></p>",
        file=FileUpload("the text content"),
        source_reference="xxx-message-id",
        web_site_relative_url=self.getWebSite().getRelativeUrl(),
    )

    self.tic()
    web_message, = support_request.getFollowUpRelatedValueList(
        portal_type='Web Message'
    )
    post, = web_message.getAggregateValueList(portal_type='HTML Post')
    # on the web message, the HTML is escaped for safety
    self.assertEqual('<p>look </p>', web_message.getTextContent())
    # but the post follow the "store what user entered as-is" rule.
    # (so looking at posts can be dangerous)
    self.assertEqual(
        "<p>look <script>alert('haha')</script></p>",
        str(post.getData()))

  def test_support_request_comment_include_other_event_type(self):
    support_request = self.portal.support_request_module.erp5_officejs_support_request_ui_test_support_reuqest_001
    event = self.portal.event_module.newContent(
        portal_type='Note',
        source_value=self.user,
        follow_up_value=support_request,
        resource_value=self.portal.service_module.erp5_officejs_support_request_ui_test_service_001,
        text_content="Notes from meeting...",
        start_date=DateTime(2001, 1, 1),
    )
    event.start()
    event.stop()
    self.tic()
    self.assertEqual(
      [dict(
        user=self.user.getTitle(),
        text="Notes from meeting...",
        date=DateTime(2001, 1, 1).ISO8601(),
        attachment_link=None,
        attachment_name=None,)],
      ignoreKeys(json.loads(support_request.SupportRequest_getCommentPostListAsJson()), 'message_id'))


class TestSupportRequestRSS(SupportRequestTestCase):
  # XXX token PAS plugin is not set up automatically when installing erp5_access_token
  # so we set it up the same way test.erp5.testERP5AccessTokenSkins is setting it up
  def _setupAccessTokenExtraction(self):
    pas = self.portal.acl_users
    access_extraction_list = [q for q in pas.objectValues() \
        if q.meta_type == 'ERP5 Access Token Extraction Plugin']
    if len(access_extraction_list) == 0:
      dispacher = pas.manage_addProduct['ERP5Security']
      dispacher.addERP5AccessTokenExtractionPlugin('token_login')
      pas.token_login.manage_activateInterfaces(('IExtractionPlugin',))
    elif len(access_extraction_list) > 1:
      raise ValueError("Too many token extraction plugins")
    self.tic()

  def afterSetUp(self):
    self._setupAccessTokenExtraction()
    SupportRequestTestCase.afterSetUp(self)
    self.attached_document = self.portal.document_module.newContent(
        portal_type='Text',
        filename='tmp.txt'
    )
    self.attached_document.publish()

    self.support_request = self.portal.support_request_module.erp5_officejs_support_request_ui_test_support_reuqest_001

    self.event = self.portal.event_module.newContent(
        portal_type='Web Message',
        source_value=self.user,
        follow_up_value=self.support_request,
        resource_value=self.portal.service_module.erp5_officejs_support_request_ui_test_service_001,
        text_content="<p>This is <b>Content</b></p>",
        start_date=DateTime(2001, 1, 1),
        aggregate_value_list=(self.attached_document, )
    )
    self.event.start()
    self.event.stop()
    self.tic()

  def _checkRSS(self, response):
    self.assertEqual(httplib.OK, response.getStatus())
    rss = feedparser.parse(response.getBody())
    self.assertEqual(rss['feed']['title'], "Support Requests")
    item, = rss.entries
    self.assertEqual(item['author'], self.user.getTitle())
    self.assertIn(self.support_request.getRelativeUrl(), item['link'])
    self.assertEqual(item['published'], DateTime(2001, 1, 1).rfc822())
    self.assertEqual(item['summary'], '<p>This is <b>Content</b></p>')
    enclosure, = [link for link in item['links'] if link['rel'] == 'enclosure']
    self.assertIn(
        self.attached_document.getRelativeUrl(),
        enclosure['href'])
    # https://pythonhosted.org/feedparser/bozo.html#advanced-bozo
    self.assertFalse(rss.bozo)

  def test_RSS(self):
    response = self.publish(
        "%s/support_request_module/SupportRequestModule_viewLastSupportRequestListAsRss" % self.getWebSite().getPath(),
        basic='%s:%s' % (self.user.erp5_login.getReference(), self.user_password))
    self._checkRSS(response)

  def test_RSS_with_token(self):
    response = self.publish(
        "%s/support_request_module/SupportRequestModule_generateRSSLinkAsJson" % self.getWebSite().getPath(),
        basic='%s:%s' % (self.user.erp5_login.getReference(), self.user_password))
    restricted_access_url = json.loads(response.getBody())['restricted_access_url']
    # make it relative url
    parsed_url = urlparse.urlparse(restricted_access_url)
    restricted_access_url = restricted_access_url.replace(
        '%s://%s' % (parsed_url.scheme, parsed_url.netloc), '', 1)
    # and check it (this time the request is not basic-authenticated)
    self._checkRSS(self.publish(restricted_access_url))
