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
    '''
    Initial Test Data:

    object                                    publication section                     follow up
    test web page                             test_category_1                         follow_up_project_1
    test_only_date
    test_valide_web_campaign_1                test_category_1                         follow_up_project_1
    test_valide_web_campaign_2                test_category_2                         follow_up_project_2

    '''

    now = DateTime()
    for category_id in ['test_category_1', 'test_category_2']:
      if not getattr(self.portal.portal_categories.publication_section, category_id, None):
        self.portal.portal_categories.publication_section.newContent(
          portal_type='Category',
          id=category_id
        )

    follow_up_project_1 = getattr(self.portal.project_module, 'follow_up_project_1', None)
    if not follow_up_project_1:
      follow_up_project_1 = self.portal.project_module.newContent(
        portal_type='Project',
        id='follow_up_project_1')

    follow_up_project_2 = getattr(self.portal.project_module, 'follow_up_project_2', None)
    if not follow_up_project_2:
      follow_up_project_2 = self.portal.project_module.newContent(
        portal_type='Project',
        id='follow_up_project_2')

    for web_campaign_id in ['test_only_date', 'test_valide_web_campaign_1', 'test_valide_web_campaign_2']:
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
    self.portal.web_campaign_module.test_valide_web_campaign_1.edit(
      publication_section='test_category_1',
      follow_up_value=follow_up_project_1
    )
    self.portal.web_campaign_module.test_valide_web_campaign_2.edit(
      publication_section='test_category_2',
      follow_up_value=follow_up_project_2
    )
    test_context = getattr(self.portal.web_page_module, 'test_context', None)
    if not test_context:
      test_context = self.portal.web_page_module.newContent(
        portal_type='Web Page',
        id='test_context'
      )
    test_context.edit(
      publication_section='test_category_1',
      follow_up_value=follow_up_project_1)
    self.test_context = test_context
    self.test_only_date = self.portal.web_campaign_module.test_only_date
    self.test_valide_web_campaign_1 = self.portal.web_campaign_module.test_valide_web_campaign_1
    self.test_valide_web_campaign_2 = self.portal.web_campaign_module.test_valide_web_campaign_2
    self.tic()

  def testSearchWebCampaignWithPublicationSectionAndFollowUp(self):
    web_campaign = self.test_context.WebSite_getWebCampaignValue()
    #only test_valide_web_campaign_1 match
    self.assertEqual(web_campaign, self.test_valide_web_campaign_1)
    self.test_valide_web_campaign_1.unpublish()
    self.tic()
    web_campaign = self.test_context.WebSite_getWebCampaignValue()
    self.assertEqual(web_campaign, None)
    self.test_valide_web_campaign_1.publish()
    # test web page now has only publication section
    self.test_context.edit(follow_up_value=None)
    self.tic()
    web_campaign = self.test_context.WebSite_getWebCampaignValue()
    self.assertEqual(web_campaign, self.test_valide_web_campaign_1)
    # change publication_section, valide_web_campaign_2 should match
    self.test_context.edit(publication_section='test_category_2')
    self.tic()
    web_campaign = self.test_context.WebSite_getWebCampaignValue()
    self.assertEqual(web_campaign, self.test_valide_web_campaign_2)

  def testSearchWebCampaignWithDate(self):
    self.assertEqual(self.test_context.WebSite_getWebCampaignValue(), self.test_valide_web_campaign_1)
    date_range_min = self.test_valide_web_campaign_1.getStartDateRangeMin()
    self.test_valide_web_campaign_1.edit(start_date_range_min=None)
    self.tic()
    self.assertEqual(self.test_context.WebSite_getWebCampaignValue(), self.test_valide_web_campaign_1)
    self.test_valide_web_campaign_1.edit(
      start_date_range_max=None,
      start_date_range_min=date_range_min)
    self.tic()
    self.assertEqual(self.test_context.WebSite_getWebCampaignValue(), self.test_valide_web_campaign_1)
    self.test_valide_web_campaign_1.edit(start_date_range_min = None)
    self.tic()
    self.assertEqual(self.test_context.WebSite_getWebCampaignValue(), None)


  def testSearchWebCampaignWithNoContextValue(self):
    self.test_context.edit(
      publication_section='',
      follow_up=''
    )
    self.tic()
    self.assertEqual(self.test_context.WebSite_getWebCampaignValue(), None)

  def testSearchWebCampaignWithMultiMatch(self):
    self.test_valide_web_campaign_2.edit(
      publication_section_list=self.test_valide_web_campaign_1.getPublicationSectionList(),
      follow_up = self.test_valide_web_campaign_1.getFollowUp()
    )
    self.tic()
    self.assertEqual(self.test_context.WebSite_getWebCampaignValue(), None)
    web_campaign_list = self.test_context.WebSite_getWebCampaignValue(batch=1)
    self.assertEqual(len(web_campaign_list), 2)
    self.assertTrue(self.test_valide_web_campaign_1 in web_campaign_list)
    self.assertTrue(self.test_valide_web_campaign_2 in web_campaign_list)
