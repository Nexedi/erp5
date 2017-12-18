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
from Products.ERP5Type.tests.utils import createZODBPythonScript
from PIL import Image
import transaction
import functools
import cStringIO
import math
import re
import io
import base64

host_url = r"https?://localhost(?::[0-9]+)?/[^/]+/"
test_url = "https://softinst73908.host.vifib.net/erp5/"

#def setDomainDict(script_id, script_param, script_code):
#  def wrapper(func):
#    @functools.wraps(func)
#    def wrapped(self, *args, **kwargs):
#      if script_id in self.portal.portal_skins.custom.objectIds():
#        raise ValueError('Precondition failed: %s exists in custom' % script_id)
#      createZODBPythonScript(
#        self.portal.portal_skins.custom,
#        script_id,
#        script_param,
#        script_code,
#      )
#      try:
#        func(self, *args, **kwargs)
#      finally:
#        if script_id in self.portal.portal_skins.custom.objectIds():
#          self.portal.portal_skins.custom.manage_delObjects(script_id)
#        transaction.commit()
#    return wrapped
#  return wrapper
  
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
      'erp5_font',
      'erp5_web',
      'erp5_dms',
      'erp5_corporate_identity',
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
    self.message_catalog.gettext('Table Of Contents', add=1)
    self.message_catalog.message_edit('Table Of Contents', 'de', 'Inhaltsverzeichnis', '')

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
        #https://softinst77579.host.vifib.net/
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
    dump = getattr(self.portal, 'dump_data', None)
    kw["batch_mode"] = 1

    html = getattr(test_page, kw.get("test_method"))(portal_skin=kw.get("use_skin"), **kw)
    html = re.sub(host_url, test_url, html)

    # update html test files or run tests
    if dump:
      expected_page.edit(text_content=html)
    self.assertEquals(html, expected_page.getData())

  def runPdfTestPattern(self, id1, id2, id3, **kw):
    """
    Compare a rendered PDF page with a a pregenerated image
    """
    test_page = getattr(self.portal.web_page_module, id1)
    expected_image = getattr(self.portal.image_module, id2)
    image_source_pdf_doc = getattr(self.portal.document_module, id3)
    dump = getattr(self.portal, 'dump_data', None)
    kw["batch_mode"] = 1

    pdf_kw = dict(
      reference=test_page.getReference(),
      target_language=kw.get("lang", None) or "en",
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

    # XXX don't overwrite file to create image, use temporary-pdf?
    image_source_pdf_doc.setData(pdf_data)
    _, bmp = image_source_pdf_doc.convert("bmp", frame=kw.get("page_number"))

    # update bmp files
    if dump:
      expected_image.setData(bmp)
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
  def test_htmlSlideshowDump(self):
    """
      Test:
      - Web Page as Slideshow
      - export as mhtml
    """
    self.runHtmlTestPattern(
      "template_test_slideshow_input_001_en_html",
      "template_test_slideshow_output_expected_004_en_html",
      **dict(
        use_skin="Slide",
        test_method="WebPage_exportAsSlideshow",
        format="mhtml"
      )
    )
