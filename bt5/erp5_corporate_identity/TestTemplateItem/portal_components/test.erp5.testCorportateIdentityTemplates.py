##############################################################################
#
# Copyright (c) 2002-2017 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.Localizer.itools.i18n.accept import AcceptLanguage
from Products.ERP5.tests.testERP5WebWithDms import customScript
from PIL import Image
from urlparse import urlparse
import cStringIO
import math, operator
import re
import base64

host_url = r"https?://localhost(?::[0-9]+)?/[^/]+/"
test_url = "https://softinst73908.host.vifib.net/"

def changeSkin(skin_name):
  """
  Change skin for following commands and attribute resolution.
  Caution: In case of more annotations, this one has to be at the bottom (last)!
  """
  def decorator(func):
    def wrapped(self, *args, **kwargs):
      default_skin = self.portal.portal_skins.default_skin
      self.portal.portal_skins.changeSkin(skin_name)
      self.app.REQUEST.set('portal_skin', skin_name)
      try:
        v = func(self, *args, **kwargs)
      finally:
        self.portal.portal_skins.changeSkin(default_skin)
        self.app.REQUEST.set('portal_skin', default_skin)
      return v
    return wrapped
  return decorator

class TestCorporateIdentityTemplates(ERP5TypeTestCase):

  def getTitle(self):
    return "Test ERP5 Corporate Identity templates."

  def getBusinessTemplateList(self):
    return (
      'erp5_base',
      'erp5_corporate_identity'
    )

  def afterSetUp(self):
    # Make sure alternative language is available
    self.message_catalog = self.portal.Localizer.erp5_ui
    if 'de' not in self.message_catalog.get_available_languages():
      self.message_catalog.add_language('de')
    self.message_catalog.gettext('Notes', add=1)
    self.message_catalog.message_edit('Notes', 'de', 'Notizen', '')
    self.message_catalog.gettext('VAT ID', add=1)
    self.message_catalog.message_edit('VAT ID', 'de', 'USt-ID', '')

    # Activating a system preference if none is activated
    for preference in self.portal.portal_catalog(portal_type="System Preference"):
      if preference.getPreferenceState() == "global":
        break
    else:
      self.portal.portal_preferences.default_nexedi_system_preference.enable()
      self.tic()

  def computeImageRenderingRootMeanSquare(self, image_data_1, image_data_2):
    """
      Compute and return the RMS (Root Mean Square) of image_data_1 and 2.
      This value can be used to compare two images in rendering point of view.

      Both image_data should be in the same quality as most as possible
      (better compare lossless format) to reduce quality differences beside
      rendering differences.
    """
    # https://duckduckgo.com/?q=python+compare+images&ia=qa
    # https://stackoverflow.com/a/1927681/
    # http://snipplr.com/view/757/compare-two-pil-images-in-python/
    # http://effbot.org/zone/pil-comparing-images.htm
    # http://effbot.org/imagingbook/image.htm
    image1 = Image.open(cStringIO.StringIO(image_data_1))
    image2 = Image.open(cStringIO.StringIO(image_data_2))

    # image can be converted into greyscale without transparency
    h1 = image1.histogram()
    h2 = image2.histogram()
    rms = math.sqrt(
      #reduce(operator.add, map(lambda a, b: (a - b) ** 2, h1, h2)) / len(h1)
      sum((a - b) ** 2 for a, b in zip(h1, h2)) / len(h1)
    )

    # Note:
    # - rms is ~5300.0 same page, bmp without alpha and bmp transparent back
    # - rms is ~1125.7 same page, jpg and bmp images
    # - rms is ~512.9 cover (big title + short title) and introduction page
    # - rms is ~1.0 if date is 2017-06-07 vs 2017-06-06 with bmp images
    return rms

  def isImageRenderingEqual(self, image_data_1, image_data_2, max_rms=10.0):
    return self.computeImageRenderingRootMeanSquare(image_data_1, image_data_2) <= max_rms

  def assertImageRenderingEquals(self, test_image_data, expected_image_data, message="Images rendering differs", max_rms=10.0):
    rms = self.computeImageRenderingRootMeanSquare(test_image_data, expected_image_data)
    if rms <= max_rms:
      return
    raise AssertionError("%(message)s\nComparing image:\n%(base64_1)s\nWith image:\n%(base64_2)s\nRMS: %(rms)s > %(max_rms)s\nAssertionError: %(message)s" % {
      "message": message,
      "base64_1": base64.encodestring(test_image_data),
      "base64_2": base64.encodestring(expected_image_data),
      "rms": rms,
      "max_rms": max_rms,
    })

  def call(self, *args, **kw):
    return args[0](*args[1:], **kw)

  def callWithPublicCloudoooOnSystemPreference(self, *args, **kw):
    """
    Calls 'doSomething' with '*args' and '**kw' after setting cloudooo server 
    url preference to 'https://cloudooo.erp5.net/' and finally restores the 
    preference to its original value.
    """
    system_preference = self.portal.portal_preferences.getActiveSystemPreference()
    if system_preference is None:
      return args[0](*args[1:], **kw)
    preferred_document_conversion_server_url = system_preference.getPreferredDocumentConversionServerUrl()
    try:
      system_preference.edit(
        preferred_document_conversion_server_url="https://cloudooo.erp5.net/",
      )
      return args[0](*args[1:], **kw)
    finally:
      system_preference.edit(
        preferred_document_conversion_server_url=preferred_document_conversion_server_url,
      )

  def callWithNewRequestAcceptLanguage(self, *args, **kw):
    """
    Call 'doSomething' with '*args' and '**kw' after setting 
    'REQUEST["AcceptLanguage"]' to '"*"' and finally restores it to its 
    original value.
    """
    has_original_accept_language = "AcceptLanguage" in self.app.REQUEST
    if has_original_accept_language:
      original_accept_language = self.app.REQUEST
    try:
      self.app.REQUEST["AcceptLanguage"] = AcceptLanguage()
      self.app.REQUEST["AcceptLanguage"].set("*", 0)
      return args[0](*args[1:], **kw)
    finally:
      if has_original_accept_language:
        self.app.REQUEST["AcceptLanguage"] = original_accept_language
      else:
        # `del self.app.REQUEST["AcceptLanguage"]` raises `AttributeError: __delitem__`
        self.app.REQUEST["AcceptLanguage"] = AcceptLanguage()

  def callWithNewRequestForm(self, *args, **kw):
    """
    Calls 'doSomething' with '*args' and '**kw' after setting 'REQUEST.form' to
    'new_form' dict and finally restores it to its original value.
    """
    has_original_form = hasattr(self.app.REQUEST, "form")
    if has_original_form:
      original_form = self.app.REQUEST.form
    try:
      self.app.REQUEST.form = args[0]
      return args[1](portal_skin=kw.get("use_skin"), **kw)
    finally:
      if has_original_form:
        self.app.REQUEST.form = original_form
      else:
        delattr(self.app.REQUEST, "form")

  def runHtmlTestPattern(self, id1, id2, **kw):
    """
    Compare rendered HTML page with pregenerated HTML output
    """
    test_page = getattr(self.portal.web_page_module, id1)
    expected_page = getattr(self.portal.web_page_module, id2)

    kw["override_date"] = kw.get("override_date", test_page.getModificationDate())

    html = getattr(test_page, kw.get("test_method"))(portal_skin=kw.get("use_skin"), **kw)
    html = re.sub(host_url, test_url, html)
    html = html.replace(test_page.getReference(), expected_page.getReference())

    self.assertEquals(html, expected_page.getData())

  def runPdfTestPattern(self, id1, id2, id3, **kw):
    """
    Compare a rendered PDF page with a a pregenerated image
    """
    test_page = getattr(self.portal.web_page_module, id1)
    expected_image = getattr(self.portal.image_module, id2)
    image_source_pdf_doc = getattr(self.portal.document_module, id3)

    kw["override_date"] = kw.get("override_date", test_page.getModificationDate())

    pdf_kw = dict(
      reference=test_page.getReference(),
      target_language="en",
      version=test_page.getVersion(),
    )

    pdf_data = self.call(
      self.callWithPublicCloudoooOnSystemPreference,
      self.callWithNewRequestAcceptLanguage,
      self.callWithNewRequestForm,
      pdf_kw,
      getattr(test_page, kw.get("test_method")),
      **kw
    )

    image_source_pdf_doc.setData(pdf_data)
    _, bmp = image_source_pdf_doc.convert("bmp", frame=kw.get("page_number"))

    self.assertImageRenderingEquals(str(bmp), str(expected_image.getData()))

    
  ##############################################################################
  # What rendering is tested:
  # - Web Page as Slideshow, Letter, Leaflet (Two Page) and Book
  ##############################################################################

  ##############################################################################
  # How to compare two images ?
  # - do a root-mean-square of image histogram using PIL
  # - compare with a maximum RMS value
  # - better to compare lossless images
  #
  # How to detect line spacing distance average on non-scanned document ?
  # - turn into greyscale
  # - select paragraph (rectangle)
  # - cut a selected part of the image into ~4px line slices
  # - sum the black color of each lines (see Figure 1)
  # - do a FFT of the results and get the absis value of the first spike (f)
  #   in the resulted curve (see Figure 2)
  #
  # How to detect letter spacing distance average on non-scanned document ?
  # - turn into greyscale
  # - select line (rectangle)
  # - cut a selected part of the image into ~2px column slices
  # - sum the black color of each columns (see Figure 1)
  # - do a FFT of the results and get the absis value of the first spike (f)
  #   in the resulted curve (see Figure 2)
  #
  # How to detect font alteration on non-scanned document ?
  # - turn into greyscale
  # - select line or piece of text (rectangle)
  # - use an OCR to convert selected part into a string
  # - regenerate the image from the string
  # - compare the images
  #
  #
  # Figure 1:
  #
  # sum of black color
  # ^
  # |
  # |  /\    /\    /\    /\
  # | /  \  /  \  /  \  /  \
  # |/    \/    \/    \/    \
  # |                        ...
  # +-----------------------------------------------------> line/column number
  #
  #
  # Figure 2:
  #
  # amplitude                                               FFT
  # ^
  # |     ^
  # |    /|\         ^
  # |   / | \       / \       ^
  # |  /  |  \     /   \     / \
  # |-'   |   '---'     '---'   '--...
  # +-----+-----------------------------------------------> frequency
  #       f
  ##############################################################################

  @changeSkin('Slide')
  def test_htmlSlideshow(self):
    """
      Test:
      - Web Page as Slideshow
      - without follow up
      - without contributor
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_slideshow_input_001_en_html",
      "template_test_slideshow_output_expected_001_en_html",
      **dict(
        use_skin="Slide",
        test_method="WebPage_exportAsSlideshow"
      )
    )

  @changeSkin('CI')
  def test_htmlSlideShowBackcompatSkinCi(self):
    """
      Test:
      - backcompat test for portal_skin "CI"
      - Web Page as Slideshow
      - without follow up
      - without contributor
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_slideshow_input_001_en_html",
      "template_test_slideshow_output_expected_001_en_html",
      **dict(
        use_skin="CI",
        test_method="WebPage_exportAsSlideshow"
      )
    )

  @changeSkin('CI_slideshow')
  def test_htmlSlideShowBackcompatSkinCislideshow(self):
    """
      Test:
      - backcompat test for portal_skin "CI_slideshow"
      - Web Page as Slideshow
      - without follow up
      - without contributor
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_slideshow_input_001_en_html",
      "template_test_slideshow_output_expected_001_en_html",
      **dict(
        use_skin="CI_slideshow",
        test_method="WebPage_exportAsSlideshow"
      )
    )

  @changeSkin('CI_Slideshow')
  def test_htmlSlideShowBackcompatSkinCiSlideshow(self):
    """
      Test:
      - backcompat test for portal_skin "CI_Slideshow"
      - Web Page as Slideshow
      - without follow up
      - without contributor
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_slideshow_input_001_en_html",
      "template_test_slideshow_output_expected_001_en_html",
      **dict(
        use_skin="CI_slideshow",
        test_method="WebPage_exportAsSlideshow"
      )
    )

  @changeSkin('SlideShow')
  def test_htmlSlideShowBackcompatSkinSlideShow(self):
    """
      Test:
      - backcompat test for portal_skin "SlideShow"
      - Web Page as Slideshow
      - without follow up
      - without contributor
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_slideshow_input_001_en_html",
      "template_test_slideshow_output_expected_001_en_html",
      **dict(
        use_skin="SlideShow",
        test_method="WebPage_exportAsSlideshow"
      )
    )

  @changeSkin('WhiteSlideShow')
  def test_htmlSlideShowBackcompatSkinWhiteSlideShow(self):
    """
      Test:
      - backcompat test for portal_skin "WhiteSlideShow"
      - Web Page as Slideshow
      - without follow up
      - without contributor
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_slideshow_input_001_en_html",
      "template_test_slideshow_output_expected_001_en_html",
      **dict(
        use_skin="WhiteSlideShow",
        test_method="WebPage_exportAsSlideshow"
      )
    )

  @changeSkin('Slide')
  def test_htmlSlideShowOptionsSet(self):
    """
      Test:
      - Web Page as Slideshow
      - without follow up
      - without contributor
      - html options (override publisher, logo, display svg as svg)
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_slideshow_input_001_en_html",
      "template_test_slideshow_output_expected_002_en_html",
      **dict(
        use_skin="WhiteSlideShow",
        test_method="WebPage_exportAsSlideshow",
        override_publisher_title="Foobarbazbam",
        override_logo_reference="Template.Test.Image.Logo.Alternativ",
        svg_display="svg"
      )
    )

  @changeSkin('Slide')
  def test_htmlSlideShowContributorPublisher(self):
    """
      Test:
      - Web Page as Slideshow
      - with follow-up organisation (Publisher)
      - with contributors
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_slideshow_input_002_en_html",
      "template_test_slideshow_output_expected_003_en_html",
      **dict(
        use_skin="WhiteSlideShow",
        test_method="WebPage_exportAsSlideshow"
      )
    )

  @changeSkin('Slide')
  def test_pdfSlideShow(self):
    """
      Test:
      - Web Page as Slideshow
      - without follow up
      - without contributor
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_slideshow_input_001_en_html",
      "template_test_slideshow_input_slide_0_001_en_bmp",
      "template_test_slideshow_input_001_en_pdf",
      **dict(
        page_number=0,
        use_skin="Slide",
        test_method="WebPage_exportAsSlideshow",
        format="pdf"
      )
    )

  @changeSkin('Slide')
  def test_pdfSlideshowNotes(self):
    """
      Test:
      - Web Page as Slideshow
      - with notes
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_slideshow_input_001_en_html",
      "template_test_slideshow_input_slide_13_004_en_bmp",
      "template_test_slideshow_input_004_en_pdf",
      **dict(
        page_number=13,
        note_display=1,
        use_skin="Slide",
        test_method="WebPage_exportAsSlideshow",
        format="pdf"
      )
    )

  @changeSkin('Slide')
  def test_pdfSlideshowContributorFollowUp(self):
    """
      Test:
      - Web Page as Slideshow
      - with contributor
      - with follow-up organisation
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_slideshow_input_002_en_html",
      "template_test_slideshow_input_slide_0_002_en_bmp",
      "template_test_slideshow_input_002_en_pdf",
      **dict(
        page_number=0,
        use_skin="Slide",
        test_method="WebPage_exportAsSlideshow",
        format="pdf"
      )
    )

  #XXX no SVG rendering in PDF + fails due to white vs alpha background
  #@changeSkin('Slide')
  #def test_pdfSlideshowKeepSvg(self):
  #  """
  #    Test:
  #    - Web Page as Slideshow
  #    - with custom logo
  #    - with custom company title
  #    - with svg rendered as svg
  #    - export as pdf
  #  """
  #  self.runPdfTestPattern(
  #    "template_test_slideshow_input_002_en_html",
  #    "template_test_slideshow_input_slide_4_003_en_bmp",
  #    "template_test_slideshow_input_003_en_pdf",
  #    **dict(
  #      page_number=4,
  #      override_publisher_title="Couscous",
  #      override_logo_reference="Template.Test.Image.Erp5.Logo",
  #      use_skin="Slide",
  #      test_method="WebPage_exportAsSlideshow",
  #      format="pdf"
  #    )
  #  )

  @changeSkin('Slide')
  def test_pdfSlideshowOverrides(self):
    """
      Test:
      - Web Page as Slideshow
      - with custom logo
      - with custom company title
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_slideshow_input_002_en_html",
      "template_test_slideshow_input_slide_0_003_en_bmp",
      "template_test_slideshow_input_003_en_pdf",
      **dict(
        page_number=0,
        override_publisher_title="Couscous",
        override_logo_reference="Template.Test.Image.Erp5.Logo",
        use_skin="Slide",
        test_method="WebPage_exportAsSlideshow",
        format="pdf"
      )
    )

  @changeSkin('Slide')
  def test_pdfSlideshowPrint(self):
    """
      Test:
      - Web Page as Slideshow
      - with custom logo
      - with custom company title
      - print as pdf (will also return the pdf-file with different header)
    """
    self.runPdfTestPattern(
      "template_test_slideshow_input_002_en_html",
      "template_test_slideshow_input_slide_0_003_en_bmp",
      "template_test_slideshow_input_003_en_pdf",
      **dict(
        page_number=0,
        override_publisher_title="Couscous",
        override_logo_reference="Template.Test.Image.Erp5.Logo",
        use_skin="Slide",
        test_method="WebPage_printAsSlideshow",
        format="pdf"
      )
    )

  @changeSkin('Slide')
  def test_pdfSlideshowNotesLocaliser(self):
    """
      Test:
      - Web Page as Slideshow
      - with notes
      - test different language output
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_slideshow_input_003_de_html",
      "template_test_slideshow_input_slide_8_005_de_bmp",
      "template_test_slideshow_input_005_de_pdf",
      **dict(
        page_number=8,
        note_display=1,
        lang="de",
        test_method="WebPage_exportAsSlideshow",
        use_skin="Slide",
        format="pdf"
      )
    )
  
  @changeSkin('Letter')
  def test_htmlLetter(self):
    """
      Test:
      - Web Page as Letter
      - override date (needed to match output files)
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_letter_input_001_en_html",
      "template_test_letter_output_expected_001_en_html",
      **dict(
        test_method="WebPage_exportAsLetter",
        use_skin="Letter"
      )
    )
  
  @changeSkin('Letter')
  def test_htmlLetterFollowUpContributor(self):
    """
      Test:
      - Web Page as Letter
      - override date (needed to match output files)
      - use follow-up organisation/person as recipient
      - use contributor as author
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_letter_input_002_en_html",
      "template_test_letter_output_expected_002_en_html",
      **dict(
        test_method="WebPage_exportAsLetter",
        use_skin="Letter"
      )
    )

  @changeSkin('Letter')
  def test_htmlLetterOverrideSenderRecipient(self):
    """
      Test:
      - Web Page as Letter
      - override date (needed to match output files)
      - override recipient, sender, their organisations and date
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_letter_input_003_en_html",
      "template_test_letter_output_expected_003_en_html",
      **dict(
        test_method="WebPage_exportAsLetter",
        use_skin="Letter",
        override_source_organisation_title="Test Association",
        override_source_person_title="Test Association Member",
        override_destination_organisation_title="Test Association",
        override_destination_person_title="Test Association Member",
        override_date = "1999-12-31"
      )
    )

  @changeSkin('Letter')
  def test_htmlLetterLocaliserHeadDisplay(self):
    """
      Test:
      - Web Page as Letter
      - override date (needed to match output files)
      - test German
      - test multi-page letter with hidden header on first page
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_letter_input_004_de_html",
      "template_test_letter_output_expected_004_de_html",
      **dict(
        test_method="WebPage_exportAsLetter",
        use_skin="Letter",
        head_display=0,
        lang="de"
      )
    )

  @changeSkin('Letter')
  def test_pdfLetter(self):
    """
      Test:
      - Web Page as Letter
      - override date (needed to match output files)
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_letter_input_001_en_html",
      "template_test_letter_input_page_0_001_en_bmp",
      "template_test_letter_input_001_en_pdf",
      **dict(
        page_number=0,
        test_method="WebPage_exportAsLetter",
        format="pdf",
        use_skin="Letter"
      )
    )

  @changeSkin('Letter')
  def test_pdfLetterFollowupContributor(self):
    """
      Test:
      - Web Page as Letter
      - use follow-up organisation/person as recipient
      - use contributor as author
      - override date (needed to match output files)
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_letter_input_002_en_html",
      "template_test_letter_input_page_0_002_en_bmp",
      "template_test_letter_input_002_en_pdf",
      **dict(
        page_number=0,
        test_method="WebPage_exportAsLetter",
        format="pdf",
        use_skin="Letter"
      )
    )

  @changeSkin('Letter')
  def test_pdfLetterOverrideSenderRecipient(self):
    """
      Test:
      - Web Page as Letter
      - override date (needed to match output files)
      - override recipient, sender, their organisations and date
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_letter_input_003_en_html",
      "template_test_letter_input_page_0_003_en_bmp",
      "template_test_letter_input_003_en_pdf",
      **dict(
        page_number=0,
        test_method="WebPage_exportAsLetter",
        format="pdf",
        use_skin="Letter",
        override_source_organisation_title="Test Association",
        override_source_person_title="Test Association Member",
        override_destination_organisation_title="Test Associatino",
        override_destination_person_title="Test Association Member",
        subfield_field_override_date_year="1999",
        subfield_field_override_date_month="12",
        subfield_field_override_date_day="31"
      )
    )
    
  @changeSkin('Letter')
  def test_pdfLetterLocaliserHeadDisplay(self):
    """
      Test:
      - Web Page as Letter
      - override date (needed to match output files)
      - test multi-page letter with hidden header on first page
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_letter_input_004_de_html",
      "template_test_letter_input_page_1_004_de_bmp",
      "template_test_letter_input_004_de_pdf",
      **dict(
        page_number=1,
        test_method="WebPage_exportAsLetter",
        format="pdf",
        lang="de",
        head_display=0,
        use_skin="Letter"
      )
    )

  @changeSkin('Letter')
  def test_pdfLetterPrint(self):
    """
      Test:
      - Web Page as Letter
      - override date (needed to match output files)
      - print as pdf
    """
    self.runPdfTestPattern(
      "template_test_letter_input_001_en_html",
      "template_test_letter_input_page_0_001_en_bmp",
      "template_test_letter_input_001_en_pdf",
      **dict(
        page_number=0,
        test_method="WebPage_PrintAsLetter",
        use_skin="Letter"
      )
    )



  '''
  
  def dumpOrCheckPrintout(self, delivery=None, report_name=None, prefix=None):
    """
    render printout as html, then either compare with previous dumps, or
    dump value
    """
    dump_printout = getattr(self.portal, 'dump_notification', None)
    printout_content = getattr(delivery, report_name)(batch_mode=True, test_mode=True)
    printout_name = "%s_%s" % (prefix, report_name)
    web_page_id = "test_printout_%s" % printout_name
    if dump_printout:
      former_web_page = getattr(self.portal.web_page_module, web_page_id, None)
      if former_web_page is None:
        former_web_page = self.portal.web_page_module.newContent(id=web_page_id)
      former_web_page.edit(title=printout_name)
      former_web_page.setTextContent(printout_content)
    else:
      former_web_page = getattr(self.portal.web_page_module, web_page_id)
      self.assertEqual(former_web_page.getTextContent(),
                       printout_content)
    self.tic()



  def test_CI_twoPage(self):
    """
      Test:
      - Web Page as Two Page
      - without follow up
      - without contributor
      - export as Default
      - html format
    """
    self.runTestPattern1("nexedi_ci_test_twopage_sample_001_en", "nexedi_ci_test_twopage_sample_002_en")

  def test_CI_twoPageContributor(self):
    """
      Test:
      - Web Page as Two Page
      - without follow up
      - with contributor (email only)
      - export as Default
      - html format
    """
    self.runTestPattern1("nexedi_ci_test_twopage_sample_003_en", "nexedi_ci_test_twopage_sample_004_en")

  def test_CI_twoPageContributorFollowUpOrganisation(self):
    """
      Test:
      - Web Page as Two Page
      - with follow up (organisation)
      - with contributor (email only)
      - export as Default
      - html format
    """
    self.runTestPattern1("nexedi_ci_test_twopage_sample_005_en", "nexedi_ci_test_twopage_sample_006_en")

  def test_CI_twoPageContributorFollowUpOrganisationPerson(self):
    """
      Test:
      - Web Page as Two Page
      - with follow up (organisation + person)
      - with contributor (email only)
      - export as Default
      - html format
    """
    self.runTestPattern1("nexedi_ci_test_twopage_sample_007_en", "nexedi_ci_test_twopage_sample_008_en")

  @customScript("ERP5Site_getWebSiteDomainDict", "", r'return {}')
  def test_CI_twoPageChapterPdfPage1(self):
    """
      Test:
      - Web Page as Two Page
      - without follow up
      - without contributor
      - export as Chapter
      - pdf format (page 1)
    """
    self.runTestPattern3("nexedi_ci_test_twopage_sample_001_en", "nexedi_ci_test_twopage_sample_001_en_image_p01", 0)

  @customScript("ERP5Site_getWebSiteDomainDict", "", r'return {}')
  def test_CI_twoPageChapterPdfPage6(self):
    """
      Test:
      - Web Page as Two Page
      - without follow up
      - without contributor
      - export as Chapter
      - pdf format (page 6)
    """
    self.runTestPattern3("nexedi_ci_test_twopage_sample_001_en", "nexedi_ci_test_twopage_sample_001_en_image_p06", 5)

  def test_CI_pressRelease(self):
    """
      Test:
      - Web Page as Press Release
      - without follow up
      - without contributor
      - export as Default
      - html format
    """
    self.runTestPattern1("nexedi_ci_test_pressrelease_sample_001_en", "nexedi_ci_test_pressrelease_sample_002_en")

  def test_CI_pressReleaseContributor(self):
    """
      Test:
      - Web Page as Press Release
      - without follow up
      - with contributor (email only)
      - export as Default
      - html format
    """
    self.runTestPattern1("nexedi_ci_test_pressrelease_sample_003_en", "nexedi_ci_test_pressrelease_sample_004_en")

  def test_CI_pressReleaseContributorFollowUpOrganisation(self):
    """
      Test:
      - Web Page as Press Release
      - with follow up (organisation)
      - with contributor (email only)
      - export as Default
      - html format
    """
    self.runTestPattern2("nexedi_ci_test_pressrelease_sample_005_en", "nexedi_ci_test_pressrelease_sample_006_en", "Nexedi")

  def test_CI_pressReleaseContributorFollowUpOrganisationPerson(self):
    
      Test:
      - Web Page as Press Release
      - with follow up (organisation + person)
      - with contributor (email only)
      - export as Default
      - html format
    """
    self.runTestPattern2("nexedi_ci_test_pressrelease_sample_007_en", "nexedi_ci_test_pressrelease_sample_008_en", "Nexedi")

'''