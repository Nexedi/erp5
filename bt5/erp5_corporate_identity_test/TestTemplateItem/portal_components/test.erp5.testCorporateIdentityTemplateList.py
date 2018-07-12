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
from Products.Localizer.itools.i18n.accept import AcceptLanguage
from PIL import Image
import cStringIO
import math
import io
import base64

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

class TestCorporateIdentityTemplateList(ERP5TypeTestCase):

  def getTitle(self):
    return "Test ERP5 Corporate Identity templates."

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
    # Make sure alternative language is available
    self.message_catalog = self.portal.Localizer.erp5_ui
    if 'de' not in self.message_catalog.get_available_languages():
      self.message_catalog.add_language('de')
    self.message_catalog.gettext('Notes', add=1)
    self.message_catalog.message_edit('Notes', 'de', 'Notizen', '')
    self.message_catalog.gettext('VAT ID', add=1)
    self.message_catalog.message_edit('VAT ID', 'de', 'USt-ID', '')
    self.message_catalog.gettext('Data Sheet', add=1)
    self.message_catalog.message_edit('Data Sheet', 'de', 'Datenblatt', '')
    self.message_catalog.gettext('Table of Contents', add=1)
    self.message_catalog.message_edit('Table of Contents', 'de', 'Inhaltsverzeichnis', '')
    self.message_catalog.gettext('Web Adress', add=1)
    self.message_catalog.message_edit('Web Adress', 'de', 'Web Adresse', '')
    self.message_catalog.gettext('Press Release', add=1)
    self.message_catalog.message_edit('Press Release', 'de', 'Pressemeldung', '')

    # Activating a system preference if none is activated
    preference = self.getDefaultSystemPreference()
    if preference.getPreferenceState() != "global":
      preference.enable()
    self.tic()

  def createTestEvent(self, target_language, source_relative_url, destination_relative_url):
    test_event = self.portal.event_module.newContent(
      portal_type="Letter",
      language=target_language,
      content_type="text/html",
      text_content="Hello",
      title="Test",
      source=source_relative_url,
      destination=destination_relative_url,
    )
    return test_event

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
    rms = math.sqrt(sum((a - b) ** 2 for a, b in zip(h1, h2)) / len(h1))

    # Note:
    # - rms is ~5300.0 same page, bmp without alpha and bmp transparent back
    # - rms is ~1125.7 same page, jpg and bmp images
    # - rms is ~512.9 cover (big title + short title) and introduction page
    # - rms is ~1.0 if date is 2017-06-07 vs 2017-06-06 with bmp images
    return rms

  def convertToPng(self, img_data):
    bmp_file = Image.open(io.BytesIO(img_data))
    img_buff = cStringIO.StringIO()
    bmp_file.save(img_buff, format='PNG', optimize=True, quality=75)
    img_data = img_buff.getvalue()
    return ''.join(['data:image/png;base64,', base64.encodestring(img_data)])

  def assertImageRenderingEquals(self, test_image_data, expected_image_data, message="Images rendering differs", max_rms=10.0):
    rms = self.computeImageRenderingRootMeanSquare(test_image_data, expected_image_data)
    if rms <= max_rms:
      return
    raise AssertionError("%(message)s\nComparing rendered image:\n%(base64_1)s\nWith expected image:\n%(base64_2)s\nRMS: %(rms)s > %(max_rms)s\nAssertionError: %(message)s" % {
      "message": message,
      "base64_1": self.convertToPng(test_image_data),
      "base64_2": self.convertToPng(expected_image_data),
      "rms": rms,
      "max_rms": max_rms,
    })

  def call(self, *args, **kw):
    return args[0](*args[1:], **kw)

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
    dump = getattr(self.portal, 'dump_data', None)
    kw["batch_mode"] = 1

    html = self.call(
      self.callWithNewRequestAcceptLanguage,
      self.callWithNewRequestForm,
      dict(),
      getattr(test_page, kw.get("test_method")),
      **kw
    )

    # update html test files or run tests
    if dump:
      expected_page.edit(text_content=html)
      self.tic()
    self.assertEquals(html.encode('UTF-8'), expected_page.getData())

  def runPdfTestPattern(self, id1, id2, id3, **kw):
    """
    Compare a rendered PDF page with a a pregenerated image
    """
    target_language=kw.get("lang", None) or "en"
    expected_image = getattr(self.portal.image_module, id2)
    image_source_pdf_doc = getattr(self.portal.document_module, id3)
    dump = getattr(self.portal, 'dump_data', None)
    kw["batch_mode"] = 1

    if id1 == None:

      # overrides are not set explicitly in Event-base letters
      # source and destination are selectedable, so the desired
      # values must be passed
      test_page = self.createTestEvent(
        target_language,
        kw["source_relative_url"],
        kw["destination_relative_url"]
      )
      self.tic()
    else:
      test_page = getattr(self.portal.web_page_module, id1)

    pdf_kw = dict(
      reference=test_page.getReference(),
      target_language=target_language
    )

    pdf_data = self.call(
      self.callWithNewRequestAcceptLanguage,
      self.callWithNewRequestForm,
      pdf_kw,
      getattr(test_page, kw.get("test_method")),
      **kw
    )

    image_source_pdf_doc.setData(pdf_data)
    _, bmp = image_source_pdf_doc.convert("bmp", frame=kw.get("page_number"))

    # update bmp files
    if dump:
      expected_image.setData(bmp)
      self.tic()
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
        use_skin="Slide",
        test_method="WebPage_exportAsSlideshow",
        override_publisher_title="Foobarbazbam",
        override_logo_reference="Template.Test.Image.Logo.Alternativ",
        display_svg="svg"
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
        use_skin="Slide",
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
      "template_test_slideshow_input_slide_6_004_en_bmp",
      "template_test_slideshow_input_004_en_pdf",
      **dict(
        page_number=6,
        display_note=1,
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
  #    ["template_test_slideshow_input_slide_4_003_en_bmp"],
  #    "template_test_slideshow_input_003_en_pdf",
  #    **dict(
  #      page_number=[4],
  #      override_source_organisation_title="Couscous",
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
        override_source_organisation_title="Couscous",
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
        override_source_organisation_title="Couscous",
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
      "template_test_slideshow_input_slide_7_005_de_bmp",
      "template_test_slideshow_input_005_de_pdf",
      **dict(
        page_number=7,
        display_note=1,
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
        subfield_field_override_date_year="1999",
        subfield_field_override_date_month="12",
        subfield_field_override_date_day="31"
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
        display_head=0,
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
        override_destination_organisation_title="Test Association",
        override_destination_person_title="Test Association Member",
        subfield_field_override_date_year="1999",
        subfield_field_override_date_month="12",
        subfield_field_override_date_day="31"
      )
    )

  @changeSkin('Letter')
  def test_pdfLetterEventOverrideSenderRecipientOrganisation(self):
    """
      Test:
      - Event as Letter
      - override recipient, sender and use organisations
      - export as pdf
    """
    self.runPdfTestPattern(
      None,
      "template_test_letter_input_page_0_005_en_bmp",
      "template_test_letter_input_005_en_pdf",
      **dict(
        page_number=0,
        test_method="Letter_send",
        format="pdf",
        use_skin="Letter",
        #override_source_organisation_title="Test Organisation",
        #override_destination_organisation_title="Test Organisation",
        source_relative_url="organisation_module/template_test_organisation",
        destination_relative_url="organisation_module/template_test_organisation",
        subfield_field_override_date_year="1999",
        subfield_field_override_date_month="12",
        subfield_field_override_date_day="31"
      )
    )

  @changeSkin('Letter')
  def test_pdfLetterEventOverrideSenderRecipientPerson(self):
    """
      Test:
      - Event as Letter
      - override recipient, sender and a person without any organisation
      - export as pdf
    """
    self.runPdfTestPattern(
      None,
      "template_test_letter_input_page_0_006_en_bmp",
      "template_test_letter_input_006_en_pdf",
      **dict(
        page_number=0,
        test_method="Letter_send",
        format="pdf",
        use_skin="Letter",
        #override_source_person_title="Test Unassociated Member",
        #override_destination_person_title="Test Unassociated Member",
        source_relative_url="person_module/template_test_no_member",
        destination_relative_url="person_module/template_test_no_member",
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
        display_head=0,
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
        test_method="WebPage_printAsLetter",
        use_skin="Letter"
      )
    )

  @changeSkin('Leaflet')
  def test_htmlLeaflet(self):
    """
      Test:
      - Web Page as Leaflet
      - as-is
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_leaflet_input_001_en_html",
      "template_test_leaflet_output_expected_001_en_html",
      **dict(
        test_method="WebPage_exportAsLeaflet",
        use_skin="Leaflet"
      )
    )

  @changeSkin('Leaflet')
  def test_htmlLeafletOverrides(self):
    """
      Test:
      - Web Page as Leaflet
      - Set all overrides and hide side panel
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_leaflet_input_001_en_html",
      "template_test_leaflet_output_expected_002_en_html",
      **dict(
        test_method="WebPage_exportAsLeaflet",
        override_source_person_title="Test Recipient",
        override_source_organisation_title="Test Association",
        override_leaflet_header_title="Couscous",
        use_skin="Leaflet"
      )
    )

  @changeSkin('Leaflet')
  def test_htmlLeafletContributorFollowUp(self):
    """
      Test:
      - Web Page as Leaflet
      - add follow up organisation and contributor
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_leaflet_input_002_de_html",
      "template_test_leaflet_output_expected_003_de_html",
      **dict(
        test_method="WebPage_exportAsLeaflet",
        use_skin="Leaflet"
      )
    )

  @changeSkin('Leaflet')
  def test_pdfLeaflet(self):
    """
      Test:
      - Web Page as Leaflet
      - as-is
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_leaflet_input_001_en_html",
      "template_test_leaflet_input_page_1_001_en_bmp",
      "template_test_leaflet_input_001_en_pdf",
      **dict(
        page_number=1,
        format="pdf",
        test_method="WebPage_exportAsLeaflet",
        use_skin="Leaflet"
      )
    )

  @changeSkin('Leaflet')
  def test_pdfLeafletOverrides(self):
    """
      Test:
      - Web Page as Leaflet
      - Set all overrides and hide side panel, display organisation logo
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_leaflet_input_001_en_html",
      "template_test_leaflet_input_page_0_002_en_bmp",
      "template_test_leaflet_input_002_en_pdf",
      **dict(
        page_number=0,
        test_method="WebPage_exportAsLeaflet",
        format="pdf",
        use_skin="Leaflet",
        override_source_organisation_title="Test Association",
        override_source_person_title="Test Recipient",
        override_leaflet_header_title="Couscous"
      )
    )

  @changeSkin('Leaflet')
  def test_pdfLeafletContributorFollowUp(self):
    """
      Test:
      - Web Page as Leaflet
      - add follow up organisation and contributor, test language translation
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_leaflet_input_002_de_html",
      "template_test_leaflet_input_page_0_003_de_bmp",
      "template_test_leaflet_input_003_de_pdf",
      **dict(
        page_number=0,
        test_method="WebPage_exportAsLeaflet",
        use_skin="Leaflet",
        format="pdf"
      )
    )

  @changeSkin('Leaflet')
  def test_pdfLeafletPrint(self):
    """
      Test:
      - Web Page as Leaflet
      - print as pdf
    """
    self.runPdfTestPattern(
      "template_test_leaflet_input_001_en_html",
      "template_test_leaflet_input_page_1_001_en_bmp",
      "template_test_leaflet_input_001_en_pdf",
      **dict(
        page_number=1,
        test_method="WebPage_printAsLeaflet",
        use_skin="Leaflet"
      )
    )

  @changeSkin('Book')
  def test_htmlBook(self):
    """
      Test:
      - Web Page as Book
      - without table of content
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_book_input_001_en_html",
      "template_test_book_output_expected_001_en_html",
      **dict(
        use_skin="Book",
        test_method="WebPage_exportAsBook",
        include_content_table=0,
        override_revision=1
      )
    )

  @changeSkin('Book')
  def testhtmlBookAllOptions(self):
    """
      Test:
      - Web Page as Book
      - with all tables and all override info set
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_book_input_001_en_html",
      "template_test_book_output_expected_002_en_html",
      **dict(
        use_skin="Book",
        test_method="WebPage_exportAsBook",
        include_history_table=1,
        include_content_table=1,
        include_reference_table=1,
        include_linked_content=1,
        include_report_content=1,
        override_document_description="foobar",
        override_document_title="Couscous",
        override_document_short_title="Cous",
        override_document_reference="P-XYZ-Foobar",
        override_logo_reference="Template.Test.Image.Erp5.Logo",
        override_source_organisation_title="Test Organisation",
        override_source_person_title="Test Sender",
        override_document_version="333",
        override_revision=1
      )
    )

  @changeSkin('Book')
  def test_htmlBookTranslation(self):
    """
      Test:
      - Web Page as Book
      - with table of content in German (header)
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_book_input_002_de_html",
      "template_test_book_output_expected_003_de_html",
      **dict(
        use_skin="Book",
        test_method="WebPage_exportAsBook",
        override_revision=1,
        lang="de"
      )
    )

  @changeSkin('Book')
  def test_pdfBook(self):
    """
      Test:
      - Web Page as Book
      - without table of content
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_book_input_001_en_html",
      "template_test_book_input_page_4_001_en_bmp",
      "template_test_book_input_001_en_pdf",
      **dict(
        page_number=4,
        use_skin="Book",
        test_method="WebPage_exportAsBook",
        format="pdf",
        override_revision=1
      )
    )

  # XXX change to a single pdf from which pics are generated!
  @changeSkin('Book')
  def testpdfBookAllOptions(self):
    """
      Test:
      - Web Page as Book
      - with all tables and all override info set
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_book_input_001_en_html",
      "template_test_book_input_page_4_002_en_bmp",
      "template_test_book_input_002_en_pdf",
      **dict(
        page_number=4,
        format="pdf",
        use_skin="Book",
        test_method="WebPage_exportAsBook",
        include_history_table=1,
        include_content_table=1,
        include_reference_table=1,
        include_linked_content=1,
        include_report_content=1,
        override_document_description="foobar",
        override_document_title="Couscous",
        override_document_short_title="Cous",
        override_document_reference="P-XYZ-Foobar",
        override_logo_reference="Template.Test.Image.Erp5.Logo",
        override_source_organisation_title="Test Organisation",
        override_source_person_title="Test Sender",
        override_document_version="333",
        override_revision=1
      )
    )

  # duplicate, just for page 5
  @changeSkin('Book')
  def testpdfBookAllOptionsDupe(self):
    """
      Test:
      - Web Page as Book
      - with all tables and all override info set
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_book_input_001_en_html",
      "template_test_book_input_page_5_002_en_bmp",
      "template_test_book_input_002_en_pdf",
      **dict(
        page_number=5,
        format="pdf",
        use_skin="Book",
        test_method="WebPage_exportAsBook",
        include_history_table=1,
        include_content_table=1,
        include_reference_table=1,
        include_linked_content=1,
        include_report_content=1,
        override_document_description="foobar",
        override_document_title="Couscous",
        override_document_short_title="Cous",
        override_document_reference="P-XYZ-Foobar",
        override_logo_reference="Template.Test.Image.Erp5.Logo",
        override_source_organisation_title="Test Organisation",
        override_source_person_title="Test Sender",
        override_document_version="333",
        override_revision=1
      )
    )

  # duplicate, just for page 10
  @changeSkin('Book')
  def testpdfBookAllOptionsDoubleDupe(self):
    """
      Test:
      - Web Page as Book
      - with all tables and all override info set
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_book_input_001_en_html",
      "template_test_book_input_page_10_002_en_bmp",
      "template_test_book_input_002_en_pdf",
      **dict(
        page_number=10,
        format="pdf",
        use_skin="Book",
        test_method="WebPage_exportAsBook",
        include_history_table=1,
        include_content_table=1,
        include_reference_table=1,
        include_linked_content=1,
        include_report_content=1,
        override_document_description="foobar",
        override_document_title="Couscous",
        override_document_short_title="Cous",
        override_document_reference="P-XYZ-Foobar",
        override_logo_reference="Template.Test.Image.Erp5.Logo",
        override_source_organisation_title="Test Organisation",
        override_source_person_title="Test Sender",
        override_document_version="333",
        override_revision=1
      )
    )

  @changeSkin('Book')
  def test_PdfBookTranslation(self):
    """
      Test:
      - Web Page as Book
      - with table of content with German (header)
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_book_input_002_de_html",
      "template_test_book_input_page_1_003_de_bmp",
      "template_test_book_input_001_en_pdf",
      **dict(
        use_skin="Book",
        test_method="WebPage_exportAsBook",
        page_number=1,
        format="pdf",
        override_revision=1
      )
    )

  @changeSkin('Book')
  def test_pdfBookPrint(self):
    """
      Test:
      - Web Page as Book
      - with table of content with German header
      - print as pdf (will also return the pdf-file with different header)
    """
    self.runPdfTestPattern(
      "template_test_book_input_002_de_html",
      "template_test_book_input_page_1_003_de_bmp",
      "template_test_book_input_001_en_pdf",
      **dict(
        use_skin="Book",
        test_method="WebPage_printAsBook",
        page_number=1,
        format="pdf",
        override_revision=1
      )
    )

  @changeSkin('Release')
  def test_htmlRelease(self):
    """
      Test:
      - Web Page as Release
      - as-is
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_release_input_001_en_html",
      "template_test_release_output_expected_001_en_html",
      **dict(
        test_method="WebPage_exportAsRelease",
        use_skin="Release",
        display_about=1
      )
    )

  @changeSkin('Release')
  def test_htmlReleaseOverrides(self):
    """
      Test:
      - Web Page as Release
      - Set all overrides and hide about section
      - export as html
    """
    self.runHtmlTestPattern(
      "template_test_release_input_002_de_html",
      "template_test_release_output_expected_002_de_html",
      **dict(
        test_method="WebPage_exportAsRelease",
        display_about=0,
        override_source_person_title="Test Association Member",
        override_source_organisation_title="Test Association",
        use_skin="Release"
      )
    )

  @changeSkin('Release')
  def test_pdfRelease(self):
    """
      Test:
      - Web Page as Release
      - as-is
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_release_input_001_en_html",
      "template_test_release_input_page_0_001_en_bmp",
      "template_test_release_input_001_en_pdf",
      **dict(
        page_number=0,
        format="pdf",
        test_method="WebPage_exportAsRelease",
        use_skin="Release"
      )
    )

  @changeSkin('Release')
  def test_pdfReleaseOverrides(self):
    """
      Test:
      - Web Page as Release
      - Set all overrides and hide about panel
      - export as pdf
    """
    self.runPdfTestPattern(
      "template_test_release_input_002_de_html",
      "template_test_release_input_page_0_002_de_bmp",
      "template_test_release_input_002_de_pdf",
      **dict(
        page_number=0,
        test_method="WebPage_exportAsRelease",
        format="pdf",
        use_skin="Release",
        override_source_organisation_title="Test Association",
        override_source_person_title="Test Association Member",
        display_about=0
      )
    )

  @changeSkin('Release')
  def test_pdfReleasePrint(self):
    """
      Test:
      - Web Page as Release
      - print as pdf
    """
    self.runPdfTestPattern(
      "template_test_release_input_001_en_html",
      "template_test_release_input_page_0_001_en_bmp",
      "template_test_release_input_001_en_pdf",
      **dict(
        page_number=0,
        test_method="WebPage_printAsRelease",
        use_skin="Release"
      )
    )
