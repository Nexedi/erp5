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

    object                                 type                  publication section                     follow up
    test web page                          Web Page              test_category_1                         follow_up_project_1
    test web page_2                        Web Page              test_category_1                         follow_up_project_1
    test_web_site                          Web Site              test_categpry_1                         follow_up_project_1
    test_only_date                         Web Campaign
    test_valide_web_campaign_1             Web Campaign          test_category_1                         follow_up_project_1
    test_valide_web_campaign_2             Web Campaign          test_category_2                         follow_up_project_2

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

    test_web_campaign_default_page = getattr(self.portal.web_page_module, 'test_web_campaign_default_page', None)
    if not test_web_campaign_default_page:
      test_web_campaign_default_page = self.portal.web_page_module.newContent(
        portal_type='Web Page',
        id='test_web_campaign_default_page',
        reference='test_web_campaign_default_page'
      )
    test_web_page = getattr(self.portal.web_page_module, 'test_web_page', None)
    if not test_web_page:
      test_web_page = self.portal.web_page_module.newContent(
        portal_type='Web Page',
        id='test_web_page'
      )
    test_web_page.edit(
      publication_section='test_category_1',
      follow_up_value=follow_up_project_1,
      reference='test_web_page_for_web_campaign'
    )

    test_web_page_2 = getattr(self.portal.web_page_module, 'test_web_page_2', None)
    if not test_web_page_2:
      test_web_page_2 = self.portal.web_page_module.newContent(
        portal_type='Web Page',
        id='test_web_page_2'
      )
    test_web_page_2.edit(
      publication_section='test_category_1',
      follow_up_value=follow_up_project_1,
      reference='test_web_page_2_for_web_campaign'
    )

    test_web_site = getattr(self.portal.web_site_module, 'test_web_site', None)
    if not test_web_site:
      test_web_site = self.portal.web_site_module.newContent(
        portal_type='Web Site',
        id='test_web_site'
      )
    test_web_site.edit(
      membership_criterion_base_category_list = ['follow_up', 'publication_section'],
      membership_criterion_category_list =['publication_section/test_category_1', 'follow_up/%s' % follow_up_project_1.getRelativeUrl()]
    )

    self.test_web_site = test_web_site
    self.test_web_page = test_web_page
    self.test_web_page_2 = test_web_page_2
    self.test_web_campaign_default_page = test_web_campaign_default_page
    if self.portal.portal_workflow.isTransitionPossible(test_web_page, 'publish'):
      test_web_page.publish()
    if self.portal.portal_workflow.isTransitionPossible(test_web_page_2, 'publish'):
      test_web_page_2.publish()

    if self.portal.portal_workflow.isTransitionPossible(test_web_campaign_default_page, 'publish'):
      test_web_campaign_default_page.publish()
    self.tic()

    for web_campaign_id in ['test_only_date', 'test_valide_web_campaign_1', 'test_valide_web_campaign_2']:
      web_campaign = getattr(self.portal.web_campaign_module, web_campaign_id, None)
      if not web_campaign:
        web_campaign = self.portal.web_campaign_module.newContent(
          id=web_campaign_id,
          portal_type = 'Web Campaign',
        )
      if self.portal.portal_workflow.isTransitionPossible(web_campaign, 'publish'):
        web_campaign.publish()

      web_campaign.edit(
        start_date_range_min = now -1,
        start_date_range_max = now + 1,
        aggregate_value=test_web_campaign_default_page,
        display_domain_list=['web_section', 'web_content'],
        causality_value=None
      )
    self.portal.web_campaign_module.test_valide_web_campaign_1.edit(
      publication_section='test_category_1',
      follow_up_value=follow_up_project_1
    )
    self.portal.web_campaign_module.test_valide_web_campaign_2.edit(
      publication_section='test_category_2',
      follow_up_value=follow_up_project_2
    )

    self.test_only_date = self.portal.web_campaign_module.test_only_date
    self.test_valide_web_campaign_1 = self.portal.web_campaign_module.test_valide_web_campaign_1
    self.test_valide_web_campaign_2 = self.portal.web_campaign_module.test_valide_web_campaign_2
    self.web_page_to_delete_list = []
    self.tic()

  def beforeTearDown(self):
    if self.web_page_to_delete_list:
      self.portal.web_page_module.manage_delObjects(self.web_page_to_delete_list)
      self.tic()

  def testSearchWebCampaignWithWebPageContext(self):
    web_campaign = self.test_web_page.WebSite_getWebCampaignValue()
    #only test_valide_web_campaign_1 match
    self.assertEqual(web_campaign, self.test_valide_web_campaign_1)
    self.test_valide_web_campaign_1.unpublish()
    self.tic()
    web_campaign = self.test_web_page.WebSite_getWebCampaignValue()
    self.assertEqual(web_campaign, None)
    self.test_valide_web_campaign_1.publish()
    # test web page now has only publication section
    self.test_web_page.edit(follow_up_value=None)
    self.tic()
    web_campaign = self.test_web_page.WebSite_getWebCampaignValue()
    self.assertEqual(web_campaign, self.test_valide_web_campaign_1)
    # change publication_section, valide_web_campaign_2 should match
    self.test_web_page.edit(publication_section='test_category_2')
    self.tic()
    web_campaign = self.test_web_page.WebSite_getWebCampaignValue()
    self.assertEqual(web_campaign, self.test_valide_web_campaign_2)
    # now change date
    date_range_min = self.test_valide_web_campaign_2.getStartDateRangeMin()
    self.test_valide_web_campaign_2.edit(start_date_range_min=None)
    self.tic()
    self.assertEqual(self.test_web_page.WebSite_getWebCampaignValue(), self.test_valide_web_campaign_2)
    self.test_valide_web_campaign_2.edit(
      start_date_range_max=None,
      start_date_range_min=date_range_min)
    self.tic()
    self.assertEqual(self.test_web_page.WebSite_getWebCampaignValue(), self.test_valide_web_campaign_2)
    self.test_valide_web_campaign_2.edit(start_date_range_min = None)
    self.tic()
    self.assertEqual(self.test_web_page.WebSite_getWebCampaignValue(), None)
    self.test_valide_web_campaign_2.edit(start_date_range_min = date_range_min)
    self.test_web_page.edit(
      publication_section='',
      follow_up=''
    )
    self.tic()
    self.assertEqual(self.test_web_page.WebSite_getWebCampaignValue(), None)

  def testSearchWebCampaignWithWebSiteContext(self):
    web_campaign = self.test_web_site.WebSite_getWebCampaignValue()
    #only test_valide_web_campaign_1 match
    self.assertEqual(web_campaign, self.test_valide_web_campaign_1)
    self.test_valide_web_campaign_1.unpublish()
    self.tic()
    web_campaign = self.test_web_site.WebSite_getWebCampaignValue()
    self.assertEqual(web_campaign, None)
    self.test_valide_web_campaign_1.publish()
    # test web page now has only publication section
    self.test_web_site.edit(follow_up_value=None)
    self.tic()
    web_campaign = self.test_web_site.WebSite_getWebCampaignValue()
    self.assertEqual(web_campaign, self.test_valide_web_campaign_1)
    # change publication_section, valide_web_campaign_2 should match
    self.test_web_site.edit(
      membership_criterion_base_category_list = ['publication_section'],
      membership_criterion_category_list =['publication_section/test_category_2']
    )
    self.tic()
    web_campaign = self.test_web_site.WebSite_getWebCampaignValue()
    self.assertEqual(web_campaign, self.test_valide_web_campaign_2)
    # now change date
    date_range_min = self.test_valide_web_campaign_2.getStartDateRangeMin()
    self.test_valide_web_campaign_2.edit(start_date_range_min=None)
    self.tic()
    self.assertEqual(self.test_web_site.WebSite_getWebCampaignValue(), self.test_valide_web_campaign_2)
    self.test_valide_web_campaign_2.edit(
      start_date_range_max=None,
      start_date_range_min=date_range_min)
    self.tic()
    self.assertEqual(self.test_web_site.WebSite_getWebCampaignValue(), self.test_valide_web_campaign_2)
    self.test_valide_web_campaign_2.edit(start_date_range_min = None)
    self.tic()
    self.assertEqual(self.test_web_site.WebSite_getWebCampaignValue(), None)
    self.test_valide_web_campaign_2.edit(start_date_range_min = date_range_min)
    self.test_web_site.edit(
      membership_criterion_base_category_list = [],
      membership_criterion_category_list =[]
    )
    self.tic()
    self.assertEqual(self.test_web_site.WebSite_getWebCampaignValue(), None)

  def testSearchWebCampaignOnlyContext(self):
    web_page_campaign = self.test_web_page.WebSite_getWebCampaignValue()
    web_site_campaign = self.test_web_site.WebSite_getWebCampaignValue()
    self.assertEqual(web_page_campaign, self.test_valide_web_campaign_1)
    self.assertEqual(web_page_campaign, web_site_campaign)
    self.assertEqual(web_page_campaign.getDisplayDomainList(), ['web_section', 'web_content'])
    self.test_valide_web_campaign_1.edit(display_domain_list=['web_section'])
    self.tic()
    web_page_campaign = self.test_web_page.WebSite_getWebCampaignValue()
    web_site_campaign = self.test_web_site.WebSite_getWebCampaignValue()
    self.assertTrue(web_page_campaign is None)
    self.assertEqual(web_site_campaign, self.test_valide_web_campaign_1)
    self.test_valide_web_campaign_1.edit(display_domain_list=['web_content'])
    self.tic()
    web_page_campaign = self.test_web_page.WebSite_getWebCampaignValue()
    web_site_campaign = self.test_web_site.WebSite_getWebCampaignValue()
    self.assertEqual(web_page_campaign, self.test_valide_web_campaign_1)
    self.assertTrue(web_site_campaign is None)


  def testSearchWebCampaignOnlySpecifyWebPage(self):
    web_page_campaign = self.test_web_page.WebSite_getWebCampaignValue()
    web_page_campaign_2 = self.test_web_page_2.WebSite_getWebCampaignValue()
    web_site_campaign = self.test_web_site.WebSite_getWebCampaignValue()
    self.assertEqual(web_page_campaign, self.test_valide_web_campaign_1)
    self.assertEqual(web_page_campaign, web_page_campaign_2)
    self.assertEqual(web_site_campaign, web_page_campaign_2)
    self.test_valide_web_campaign_1.edit(
      causality_value=self.test_web_page_2,
      display_domain='specify_page'
    )
    self.tic()
    web_page_campaign = self.test_web_page.WebSite_getWebCampaignValue()
    web_page_campaign_2 = self.test_web_page_2.WebSite_getWebCampaignValue()
    web_site_campaign = self.test_web_site.WebSite_getWebCampaignValue()
    self.assertTrue(web_page_campaign is None)
    self.assertTrue(web_site_campaign is None)
    self.assertEqual(web_page_campaign_2, self.test_valide_web_campaign_1)
    self.test_valide_web_campaign_1.edit(causality_value=self.test_web_page)
    self.tic()
    web_page_campaign = self.test_web_page.WebSite_getWebCampaignValue()
    web_page_campaign_2 = self.test_web_page_2.WebSite_getWebCampaignValue()
    web_site_campaign = self.test_web_site.WebSite_getWebCampaignValue()
    self.assertEqual(web_page_campaign, self.test_valide_web_campaign_1)
    self.assertTrue(web_site_campaign is None)
    self.assertTrue(web_page_campaign_2 is None)

  def testSearchWebCampaignWhenSpecifyWebPageChangeValue(self):
    self.test_valide_web_campaign_1.edit(causality_value=self.test_web_page_2)
    self.tic()
    web_page_campaign_2 = self.test_web_page_2.WebSite_getWebCampaignValue()
    self.assertEqual(web_page_campaign_2, self.test_valide_web_campaign_1)
    self.test_web_page_2.edit(publication_section='test_category_1')
    self.tic()
    web_page_campaign_2 = self.test_web_page_2.WebSite_getWebCampaignValue()
    self.assertEqual(web_page_campaign_2, self.test_valide_web_campaign_1)


  def testSearchWebCampaignWithMultiLanguageSpecifyPageState(self):
    self.test_valide_web_campaign_1.edit(causality_value=self.test_web_page_2)
    self.tic()
    new_web_page = self.test_web_page_2.Base_createCloneDocument(batch_mode=True)
    new_web_page.edit(language='fr')
    self.web_page_to_delete_list.append(new_web_page.getId())
    self.tic()
    new_web_page.publish()
    self.tic()
    web_page_campaign = self.test_web_page_2.WebSite_getWebCampaignValue()
    new_web_page_campaign = new_web_page.WebSite_getWebCampaignValue()
    self.assertEqual(web_page_campaign, self.test_valide_web_campaign_1)
    self.assertEqual(new_web_page_campaign, self.test_valide_web_campaign_1)

    self.test_web_page_2.unpublish()
    self.tic()
    new_web_page_campaign = new_web_page.WebSite_getWebCampaignValue()
    self.assertEqual(new_web_page_campaign, self.test_valide_web_campaign_1)


  def testSearchWebCampaignWithMultiMatch(self):
    self.test_valide_web_campaign_2.edit(
      publication_section_list=self.test_valide_web_campaign_1.getPublicationSectionList(),
      follow_up = self.test_valide_web_campaign_1.getFollowUp()
    )
    self.tic()
    self.assertEqual(self.test_web_page.WebSite_getWebCampaignValue(), None)
    web_campaign_list = self.test_web_page.WebSite_getWebCampaignValue(batch=1)
    self.assertEqual(len(web_campaign_list), 2)
    self.assertTrue(self.test_valide_web_campaign_1 in web_campaign_list)
    self.assertTrue(self.test_valide_web_campaign_2 in web_campaign_list)

  def testSearchWebCampaignWithMultiMatchSpecifyPage(self):
    self.test_valide_web_campaign_2.edit(
      display_domain='specify_page',
      causality_value=self.test_web_page_2
    )
    self.test_valide_web_campaign_1.edit(
      display_domain='specify_page',
      causality_value=self.test_web_page_2
    )
    self.tic()
    self.assertEqual(self.test_web_page_2.WebSite_getWebCampaignValue(), None)
    web_campaign_list = self.test_web_page_2.WebSite_getWebCampaignValue(batch=1)
    self.assertEqual(len(web_campaign_list), 2)
    self.assertTrue(self.test_valide_web_campaign_1 in web_campaign_list)
    self.assertTrue(self.test_valide_web_campaign_2 in web_campaign_list)

  def testSearchWebCampaignMultiMatchWithSpecifyPage(self):
    self.test_valide_web_campaign_2.edit(
      publication_section_list=self.test_valide_web_campaign_1.getPublicationSectionList(),
      follow_up = self.test_valide_web_campaign_1.getFollowUp(),
      causality_value=self.test_web_page_2
    )
    self.tic()
    self.assertEqual(self.test_web_page.WebSite_getWebCampaignValue(), self.test_valide_web_campaign_1)
    self.assertEqual(self.test_web_page_2.WebSite_getWebCampaignValue(), self.test_valide_web_campaign_2)
