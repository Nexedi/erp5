##############################################################################
#
# Copyright (c) 2002-2018 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestCorporateIdentityMethod(ERP5TypeTestCase):

  def getTitle(self):
    return "Test ERP5 Corporate Identity Method."

  def getBusinessTemplateList(self):
    return (
      'erp5_base',
      'erp5_font',
      'erp5_web',
      'erp5_dms',
      'erp5_corporate_identity',
      'erp5_corporate_identity_test',
      'erp5_ui_test_core'
    )

  def afterSetUp(self):
    test_person = self.portal.portal_catalog.getResultValue(
      portal_type='Person',
      reference = 'Person For Test Parameter')
    if not test_person:
      test_person =  self.portal.person_module.newContent(
        portal_type='Person',
        reference='Person For Test Parameter',
        first_name='Test',
        last_name='Person Parameter',
        default_email_url_string='test@info.com',
        default_telephone_telephone_number="123",
        default_address_street_address="street 1",
        default_address_zip_code="456"
      )
    self.test_person = test_person

    test_web_page = self.portal.portal_catalog.getResultValue(
      portal_type='Web Page',
      reference ='Web Page For Test Parameter')
    if not test_web_page:
      test_web_page = self.portal.web_page_module.newContent(
        portal_type='Web Page',
        reference='Web Page For Test Parameter')
    self.test_web_page = test_web_page

    test_organisation = self.portal.portal_catalog.getResultValue(
      portal_type='Organisation',
      reference='Organisation For Test Parameter')
    if not test_organisation:
      test_organisation = self.portal.organisation_module.newContent(
        portal_type='Organisation',
        reference='Organisation For Test Parameter',
        title='Test Organisation Parameter',
        default_email_url_string='test@test.com',
        default_telephone_telephone_number="123",
        default_address_street_address="street 1",
        default_address_zip_code="456"
      )
    self.test_organisation = test_organisation

    test_product = self.portal.portal_catalog.getResultValue(
      portal_type='Product',
      reference='Product For Test Parameter')
    if not test_product:
      test_product = self.portal.product_module.newContent(
        portal_type='Product',
        title='Product Software',
        reference='Product For Test Parameter')
    self.test_product = test_product

    test_web_site = self.portal.portal_catalog.getResultValue(
      portal_type='Web Site',
      reference='Web Site For Test Parameter')
    if not test_web_site:
      test_web_site = self.portal.web_site_module.newContent(
        portal_type='Web Site',
        reference='Web Site For Test Parameter')
    self.test_web_site = test_web_site

    # Activating a system preference if none is activated
    preference = self.getDefaultSystemPreference()
    if preference.getPreferenceState() != "global":
      preference.enable()
    if self.portal.portal_preferences.default_site_preference.getPreferenceState() != "global":
      self.portal.portal_preferences.default_site_preference.enable()
    self.tic()

  def test_WebPage_createImageOverview(self):
    web_page = self.portal.web_page_module.template_test_slideshow_input_001_en_html
    document_content = '<div><img src="http://test.png" /></div>'
    expected_dict ={'figure_list': []}
    output_dict = web_page.WebPage_createImageOverview(document_content)
    self.assertEquals(output_dict, expected_dict)
    document_content = '<div><img src="http://test.png" alt="test" /></div>'
    expected_dict ={'figure_list': [{'input': '<img src="http://test.png" alt="test" />',
                                     'item': {'id': 'Figure-1', 'title': 'test'},
                                     'output': '<a href="#Figure-1"></a><img src="http://test.png" alt="test" /><span>Figure-1 - test</span>'}]}
    output_dict = web_page.WebPage_createImageOverview(document_content)
    self.assertEquals(output_dict, expected_dict)


  def test_validateImage(self):
    web_page = self.portal.web_page_module.template_test_slideshow_input_001_en_html
    img_string = ''
    output_string = web_page.WebPage_validateImage(img_string=img_string)
    self.assertEqual(output_string, img_string)

    img_string = '<img alt="alt">'
    output_string = web_page.WebPage_validateImage(img_string=img_string)
    self.assertEqual(output_string, img_string)

    img_string='<img src="data:image/png;;base64,iVBO">'
    output_string = web_page.WebPage_validateImage(img_string=img_string)
    self.assertEqual(output_string, img_string)

    # add format
    img_string='<img src="http://test.png">'
    output_string = web_page.WebPage_validateImage(img_string=img_string)
    self.assertEqual(output_string, '<img src="http://test.png?format=">')

    img_string='<img src="http://test.png?version=1">'
    output_string = web_page.WebPage_validateImage(img_string=img_string)
    self.assertEqual(output_string, '<img src="http://test.png?version=1&amp;format=">')

    img_string = '<img src="test.png?version=1">'
    output_string = web_page.WebPage_validateImage(img_string=img_string)
    self.assertTrue('The following image could not be found in erp5 OR is not following' in output_string)

    img_string ='<img src="/Template.Test.Image.Map?version=1">'
    output_string = web_page.WebPage_validateImage(img_string=img_string)
    self.assertEqual(output_string, '<img src="/Template.Test.Image.Map?version=1&amp;format=">')

    img_string = '<img src="Template.Test.Image.Map?version=1">'
    output_string = web_page.WebPage_validateImage(img_string=img_string)
    self.assertEqual(output_string, '<img src="Template.Test.Image.Map?version=1&amp;format=">')

    img_string = '<img src="Template.Test.Image.Map/getData">'
    output_string = web_page.WebPage_validateImage(img_string=img_string)
    self.assertEqual(output_string, '<img src="Template.Test.Image.Map/getData?format=">')

    img_string = '<img src="./Template.Test.Image.Map?version=1">'
    output_string = web_page.WebPage_validateImage(img_string=img_string)
    self.assertEqual(output_string, '<img src="Template.Test.Image.Map?version=1&amp;format=">')

    img_string = '<img src="Template.Test.Image.Map?version=1">'
    output_string = web_page.WebPage_validateImage(img_string=img_string, img_fullscreen_link=True)
    self.assertEqual(output_string, '<a target="_blank" rel="noopener noreferrer" href="Template.Test.Image.Map?version=1&amp;format=" title="Template Test Image Map"><img src="Template.Test.Image.Map?version=1&amp;format="><a>')

    img_string = '<img src="Template.Test.Image.Map?version=1">'
    output_string = web_page.WebPage_validateImage(img_string=img_string, img_wrap=True)
    self.assertEqual(output_string, '<p class="ci-book-img" style="text-align:center"><img src="Template.Test.Image.Map?version=1&amp;format="></p>')

  def test_webPage_embedLinkedDocumentList(self):
    web_page = self.portal.web_page_module.template_test_slideshow_input_001_en_html

    doc_content = '<div> [<a href="Https://Template.Test.Book.Embeddable.Document">This link should be embedded</a>] </div>'
    output =web_page.WebPage_embedLinkedDocumentList(doc_content)
    self.assertEqual(doc_content, output)

    doc_content = '<div> [<a href="Template.Test.Book.Embeddable.Document">This link should be embedded</a>] </div>'
    output =web_page.WebPage_embedLinkedDocumentList(doc_content)
    self.assertEqual(doc_content, output)

    # be careful of space between <div> <a>
    doc_content = '<div> <a href="Template.Test.Book.Embeddable.Document">This link should be embedded</a> </div>'
    output =web_page.WebPage_embedLinkedDocumentList(doc_content)
    self.assertEqual(output, '<div> %s </div>' %web_page.restrictedTraverse('Template.Test.Book.Embeddable.Document').asStrippedHTML())

  def test_webPage_embedReportDocumentList(self):
    web_page_no_follow_up = self.portal.web_page_module.template_test_slideshow_input_001_en_html
    web_page_with_follow_up = self.portal.web_page_module.template_test_book_embed_reportdocument_html

    doc_content = '<div>${WebPage_insertFollowUpCorporareIdentityTestReport}</div>'
    output =web_page_no_follow_up.WebPage_embedReportDocumentList(doc_content)
    self.assertEqual(output, doc_content)

    output =web_page_with_follow_up.WebPage_embedReportDocumentList(doc_content)
    self.assertEqual(output, '<div>%s</div>' % web_page_with_follow_up.Base_generateCorporareIdentityTestReport(display_comment=True)[0])

    # it has no matter with/without follow up
    doc_content = '<div> <a href="sale_opportunity_module/template_test_embed_sale_opportunity?report=Base_generateCorporareIdentityTestReport&amp;test=23"></a> </div>'
    output =web_page_with_follow_up.WebPage_embedReportDocumentList(doc_content)
    self.assertEqual(output, '<div> test report {"test": "23", "document_language": null, "format": null} </div>')

    doc_content = '<div> <a href="sale_opportunity_module/template_test_embed_sale_opportunity?report=Base_generateCorporareIdentityTestReport&amp;test=23"></a> </div>'
    output =web_page_no_follow_up.WebPage_embedReportDocumentList(doc_content)
    self.assertEqual(output, '<div> test report {"test": "23", "document_language": null, "format": null} </div>')

  def test_getTemplateProxyParameter_override_person(self):
    output_dict_list = self.test_person.Base_getTemplateProxyParameter(
      parameter='override_person',
      source_data=self.test_person.getTitle())
    self.assertEqual(len(output_dict_list), 1)
    output_dict = output_dict_list[0]
    self.assertEqual(output_dict['postal_code'], self.test_person.getDefaultAddress().getZipCode())
    self.assertEqual(output_dict['address'], self.test_person.getDefaultAddress().getStreetAddress())
    self.assertEqual(output_dict['email'], self.test_person.getDefaultEmail().getUrlString())
    self.assertEqual(output_dict['name'], self.test_person.getTitle())
    self.assertEqual(output_dict['phone'], self.test_person.getDefaultTelephoneValue().getCoordinateText())

  def test_getTemplateProxyParameter_author(self):
    self.test_web_page.edit(
      contributor_value=None)
    self.tic()
    output_dict_list = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='author')
    self.assertEqual(len(output_dict_list), 0)
    self.test_web_page.edit(
      contributor_value=self.test_person)
    self.tic()
    output_dict_list = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='author')
    self.assertEqual(len(output_dict_list), 1)
    output_dict = output_dict_list[0]
    self.assertEqual(output_dict['postal_code'], self.test_person.getDefaultAddress().getZipCode())
    self.assertEqual(output_dict['address'], self.test_person.getDefaultAddress().getStreetAddress())
    self.assertEqual(output_dict['email'], self.test_person.getDefaultEmail().getUrlString())
    self.assertEqual(output_dict['name'], self.test_person.getTitle())
    self.assertEqual(output_dict['phone'], self.test_person.getDefaultTelephoneValue().getCoordinateText())

  def test_getTemplateProxyParameter_override_organisation(self):
    output_dict_list = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='override_organisation',
      source_data = self.test_organisation.getTitle()
    )
    self.assertEqual(len(output_dict_list), 1)
    output_dict = output_dict_list[0]
    self.assertEqual(output_dict['postal_code'], self.test_organisation.getDefaultAddress().getZipCode())
    self.assertEqual(output_dict['address'], self.test_organisation.getDefaultAddress().getStreetAddress())
    self.assertEqual(output_dict['email'], self.test_organisation.getDefaultEmail().getUrlString())
    self.assertEqual(output_dict['organisation_title'], self.test_organisation.getTitle())
    self.assertEqual(output_dict['phone'], self.test_organisation.getDefaultTelephoneValue().getCoordinateText())

  def test_getTemplateProxyParameter_override_organisation_relative_url(self):
    output_dict_list = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='override_organisation_relative_url',
      source_data = self.test_organisation.getRelativeUrl()
    )
    self.assertEqual(len(output_dict_list), 1)
    output_dict = output_dict_list[0]
    self.assertEqual(output_dict['postal_code'], self.test_organisation.getDefaultAddress().getZipCode())
    self.assertEqual(output_dict['address'], self.test_organisation.getDefaultAddress().getStreetAddress())
    self.assertEqual(output_dict['email'], self.test_organisation.getDefaultEmail().getUrlString())
    self.assertEqual(output_dict['organisation_title'], self.test_organisation.getTitle())
    self.assertEqual(output_dict['phone'], self.test_organisation.getDefaultTelephoneValue().getCoordinateText())

  def test_getTemplateProxyParameter_source(self):
    output_dict_list = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='source',
      source_data = self.test_person.getUid()
    )
    self.assertEqual(len(output_dict_list), 1)
    output_dict = output_dict_list[0]
    self.assertEqual(output_dict['postal_code'], self.test_person.getDefaultAddress().getZipCode())
    self.assertEqual(output_dict['address'], self.test_person.getDefaultAddress().getStreetAddress())
    self.assertEqual(output_dict['email'], self.test_person.getDefaultEmail().getUrlString())
    self.assertEqual(output_dict['name'], self.test_person.getTitle())
    self.assertEqual(output_dict['phone'], self.test_person.getDefaultTelephoneValue().getCoordinateText())

    self.test_person.edit(
      career_subordination_value = self.test_organisation)
    self.tic()
    output_dict_list = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='source',
      source_data = self.test_person.getUid()
    )
    self.assertEqual(len(output_dict_list), 1)
    output_dict = output_dict_list[0]
    self.assertEqual(output_dict['postal_code'], self.test_organisation.getDefaultAddress().getZipCode())
    self.assertEqual(output_dict['address'], self.test_organisation.getDefaultAddress().getStreetAddress())
    self.assertEqual(output_dict['email'], self.test_organisation.getDefaultEmail().getUrlString())
    self.assertEqual(output_dict['organisation_title'], self.test_organisation.getTitle())
    self.assertEqual(output_dict['phone'], self.test_organisation.getDefaultTelephoneValue().getCoordinateText())

    output_dict_list = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='source',
      source_data = self.test_organisation.getUid()
    )
    self.assertEqual(len(output_dict_list), 1)
    output_dict = output_dict_list[0]
    self.assertEqual(output_dict['postal_code'], self.test_organisation.getDefaultAddress().getZipCode())
    self.assertEqual(output_dict['address'], self.test_organisation.getDefaultAddress().getStreetAddress())
    self.assertEqual(output_dict['email'], self.test_organisation.getDefaultEmail().getUrlString())
    self.assertEqual(output_dict['organisation_title'], self.test_organisation.getTitle())
    self.assertEqual(output_dict['phone'], self.test_organisation.getDefaultTelephoneValue().getCoordinateText())

    self.test_person.edit(
      career_subordination_value = None)
    self.tic()

  def test_getTemplateProxyParameter_destination(self):
    output_dict_list = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='destination',
      source_data = self.test_person.getUid()
    )
    self.assertEqual(len(output_dict_list), 1)
    output_dict = output_dict_list[0]
    self.assertEqual(output_dict['postal_code'], self.test_person.getDefaultAddress().getZipCode())
    self.assertEqual(output_dict['address'], self.test_person.getDefaultAddress().getStreetAddress())
    self.assertEqual(output_dict['email'], self.test_person.getDefaultEmail().getUrlString())
    self.assertEqual(output_dict['name'], self.test_person.getTitle())
    self.assertEqual(output_dict['phone'], self.test_person.getDefaultTelephoneValue().getCoordinateText())

    self.test_person.edit(
      career_subordination_value = self.test_organisation)
    self.tic()
    output_dict_list = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='destination',
      source_data = self.test_person.getUid()
    )
    self.assertEqual(len(output_dict_list), 1)
    output_dict = output_dict_list[0]
    self.assertEqual(output_dict['postal_code'], self.test_organisation.getDefaultAddress().getZipCode())
    self.assertEqual(output_dict['address'], self.test_organisation.getDefaultAddress().getStreetAddress())
    self.assertEqual(output_dict['email'], self.test_organisation.getDefaultEmail().getUrlString())
    self.assertEqual(output_dict['organisation_title'], self.test_organisation.getTitle())
    self.assertEqual(output_dict['phone'], self.test_organisation.getDefaultTelephoneValue().getCoordinateText())

    output_dict_list = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='destination',
      source_data = self.test_organisation.getUid()
    )
    self.assertEqual(len(output_dict_list), 1)
    output_dict = output_dict_list[0]
    self.assertEqual(output_dict['postal_code'], self.test_organisation.getDefaultAddress().getZipCode())
    self.assertEqual(output_dict['address'], self.test_organisation.getDefaultAddress().getStreetAddress())
    self.assertEqual(output_dict['email'], self.test_organisation.getDefaultEmail().getUrlString())
    self.assertEqual(output_dict['organisation_title'], self.test_organisation.getTitle())
    self.assertEqual(output_dict['phone'], self.test_organisation.getDefaultTelephoneValue().getCoordinateText())

    self.test_person.edit(
      career_subordination_value = None)
    self.tic()

  def test_getTemplateProxyParameter_organisation(self):
    output_dict_list = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='organisation',
    )
    self.assertEqual(len(output_dict_list), 0)
    self.test_web_page.edit(
      follow_up_value = self.test_organisation,
    )
    self.tic()
    output_dict_list = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='organisation',
    )
    self.assertEqual(len(output_dict_list), 1)
    output_dict = output_dict_list[0]
    self.assertEqual(output_dict['postal_code'], self.test_organisation.getDefaultAddress().getZipCode())
    self.assertEqual(output_dict['address'], self.test_organisation.getDefaultAddress().getStreetAddress())
    self.assertEqual(output_dict['email'], self.test_organisation.getDefaultEmail().getUrlString())
    self.assertEqual(output_dict['organisation_title'], self.test_organisation.getTitle())
    self.assertEqual(output_dict['phone'], self.test_organisation.getDefaultTelephoneValue().getCoordinateText())
    self.test_web_page.edit(
      follow_up_value = None
    )
    self.tic()

  def test_getTemplateProxyParameter_person(self):
    output_dict_list = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='person',
    )
    self.assertEqual(len(output_dict_list), 0)
    self.test_web_page.edit(
      follow_up_value = self.test_person,
    )
    self.tic()
    output_dict_list = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='person',
    )
    self.assertEqual(len(output_dict_list), 1)
    output_dict = output_dict_list[0]
    self.assertEqual(output_dict['postal_code'], self.test_person.getDefaultAddress().getZipCode())
    self.assertEqual(output_dict['address'], self.test_person.getDefaultAddress().getStreetAddress())
    self.assertEqual(output_dict['email'], self.test_person.getDefaultEmail().getUrlString())
    self.assertEqual(output_dict['name'], self.test_person.getTitle())
    self.assertEqual(output_dict['phone'], self.test_person.getDefaultTelephoneValue().getCoordinateText())
    self.test_web_page.edit(
      follow_up_value = None
    )
    self.tic()

  def test_getTemplateProxyParameter_logo(self):
    for lang in ['en','fr']:
      self.test_web_page.edit(language=lang)
      self.tic()
      output_dict_list = self.test_web_page.Base_getTemplateProxyParameter(
        parameter='logo',
        source_data='Template.Test.Theme.Logo.Default'
      )
      self.assertEqual(len(output_dict_list), 1)
      output_dict = output_dict_list[0]
      self.assertEqual(output_dict['reference'], self.portal.image_module.template_test_image_theme_logo_png.getReference())
      self.assertEqual(output_dict['relative_url'], self.portal.image_module.template_test_image_theme_logo_png.getRelativeUrl())
      self.assertEqual(output_dict['description'], self.portal.image_module.template_test_image_theme_logo_png.getDescription())
      self.test_web_page.edit(language='fr')
    self.tic()

  def test_getTemplateProxyParameter_product(self):
    self.test_web_page.edit(
      follow_up_value = self.test_product)
    self.tic()
    output_dict_list = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='product',
    )
    self.assertEqual(len(output_dict_list), 1)
    output_dict = output_dict_list[0]
    self.assertEqual(output_dict['title'], self.test_product.getTitle())

  def test_getTemplateProxyParameter_theme(self):
    self.test_product.edit(
      title='Product Software')
    self.test_web_page.edit(
      follow_up_value = self.test_product)
    self.tic()
    output = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='theme',
    )
    self.assertEqual(output, self.test_product.getTitle().split(' ')[0].lower())

    self.test_product.edit(
      title='Product Software xxxx')
    self.tic()
    output = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='theme',
    )
    self.assertEqual(output, self.test_product.getTitle().split(' ')[0].lower())

    self.test_product.edit(
      title='Product xxxx')
    self.tic()
    output = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='theme',
    )
    self.assertEqual(output, None)

  def test_getTemplateProxyParameter_theme_through_web_site(self):
    self.test_web_site.edit(
      membership_criterion_category_list = []
    )
    self.tic()
    output = self.test_web_site.Base_getTemplateProxyParameter(
      parameter='theme',
    )
    self.assertEqual(output, None)

    self.test_product.edit(
      title='Product Software')
    self.test_web_site.edit(
      membership_criterion_category_list = ['follow_up/%s' % self.test_product.getRelativeUrl()]
    )
    self.tic()
    output = self.test_web_site.Base_getTemplateProxyParameter(
      parameter='theme',
    )
    self.assertEqual(output, self.test_product.getTitle().split(' ')[0].lower())

    self.test_product.edit(
      title='Product Software xxxx')
    self.tic()
    output = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='theme',
    )
    self.assertEqual(output, self.test_product.getTitle().split(' ')[0].lower())

    self.test_product.edit(
      title='Product xxxx')
    self.tic()
    output = self.test_web_page.Base_getTemplateProxyParameter(
      parameter='theme',
    )
    self.assertEqual(output, None)

