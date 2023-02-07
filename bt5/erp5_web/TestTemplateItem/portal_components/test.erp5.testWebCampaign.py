##############################################################################
#
# Copyright (c) 2023 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from DateTime import DateTime

class TestWebCampaign(ERP5TypeTestCase):
  def getTitle(self):
    return "Test Web Campaign"

  def afterSetUp(self):
    now = DateTime()
    for category_id in ['test_category_1', 'test_category_2']:
      if not getattr(self.portal.portal_categories.publication_section, category_id, None):
        self.portal.portal_categories.publication_section.newContent(
          portal_type='Category',
          id=category_id
        )

    follow_up_project = getattr(self.portal.project_module, 'follow_up_project', None)
    if not follow_up_project:
      follow_up_project = self.portal.project_module.newContent(
        portal_type='Project',
        id='follow_up_project')

    for web_campaign_id in ['test_only_date', 'test_date_publication', 'test_date_publication_follow_up']:
      web_campaign = getattr(self.portal.web_campaign_module, web_campaign_id, None)
      if not web_campaign:
        web_campaign = self.portal.web_campaign_module.newContent(
          id=web_campaign_id,
          portal_type = 'Web Campaign'
        )
      if self.portal.portal_workflow.isTransitionPossible(web_campaign, 'publish'):
        web_campaign.publish()

      web_campaign.edit(
        start_date_range_min = now -1,
        start_date_range_max = now + 1
      )
    self.portal.web_campaign_module.test_date_publication.edit(
      publication_section='test_category_1'
    )
    self.portal.web_campaign_module.test_date_publication_follow_up.edit(
      publication_section='test_category_1',
      follow_up_value=follow_up_project
    )
    test_context = getattr(self.portal.web_page_module, 'test_context', None)
    if not test_context:
      test_context = self.portal.web_page_module.newContent(
        portal_type='Web Page',
        id='test_context'
      )
    test_context.edit(
      publication_section='test_category_1',
      follow_up_value=follow_up_project)
    self.test_context = test_context
    self.test_only_date = self.portal.web_campaign_module.test_only_date
    self.test_date_publication = self.portal.web_campaign_module.test_date_publication
    self.test_date_publication_follow_up = self.portal.web_campaign_module.test_date_publication_follow_up
    self.tic()

  def testGetWebCampaignOnlyPublishedState(self):
    web_campaign = self.test_context.WebSite_getWebCampaignValue()
    self.assertEqual(web_campaign, self.test_date_publication_follow_up)
    self.test_only_date.unpublish()
    self.test_date_publication.unpublish()
    self.test_date_publication_follow_up.unpublish()
    self.tic()
    web_campaign = self.test_context.WebSite_getWebCampaignValue()
    self.assertEqual(web_campaign, None)

  def testGetWebCampaignMultiMatch(self):
    self.test_context.edit(follow_up_value=None)
    self.tic()
    self.assertRaises(ValueError, self.test_context.WebSite_getWebCampaignValue)

  def testGetWebCampaignOnlyFollowUp(self):
    self.test_context.edit(publication_section='')
    self.tic()
    web_campaign = self.test_context.WebSite_getWebCampaignValue()
    self.assertEqual(web_campaign, self.test_date_publication_follow_up)
