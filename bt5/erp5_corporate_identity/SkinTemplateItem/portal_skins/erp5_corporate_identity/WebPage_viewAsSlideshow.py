"""
================================================================================
MAIN FILE: generate presentation in different output formats
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# kw-parameters   (* default)
# ------------------------------------------------------------------------------
# format:                   output in html*, pdf
# transformation:           convert content into nothing*, book
# ------
# override_source_organisation_title: to use instead of default company
# override_logo_reference:  to use instead of default company logo in footer
# override_batch_mode:      used for tests
# ------
# document_download:        download file directly (default None)
# document_save:            save file in document module (default None)
# ------
# display_note:             display slide notes (1) or not (0)*
# display_svg:              display svg-images as svg or png*
# ------
# remote_content:           convert legacy odp, sxi formats (not active)

import re

from Products.PythonScripts.standard import html_quote
from base64 import b64encode

blank = ''
flags = re.MULTILINE|re.DOTALL|re.IGNORECASE
details_separator = '</section><section class="ci-notes-continue"><section><h1>cont.</h1></section>'
pref = context.getPortalObject().portal_preferences

# ------------------ HTML cleanup/converter methods ----------------------------
def getHeaderSlideTitle(my_doc):
  return '<h1>' + html_quote(my_doc.getTitle()) + '</h1>'

def getSlideList(my_content):
  return re.findall(r'<section[^>]*?>(.*?)</section>', my_content, re.S)

#def getSectionSlideList(my_content):
#  return re.findall(r'(<section[^>]*?>.*?</section>)', my_content, re.S)

def getSlideDetailsList(my_content):
  return re.findall(r'<section.*?>\s?<section>.*?</details>\s?</section>', my_content, re.S)

def getDetails(my_content):
  return my_content.find("</details>")

def getDetailsList(my_slide):
  return re.findall(r'<details.*?>.*?<\/details>', my_slide, re.S)

#def getNestedSection(my_content):
#  return my_content.find("<section") > -1

# please look the other direction until we can use beautifulsoup
def getSlideFront(my_content):

  # is there an image on the slide?
  img = re.search(r'(<img.*?/>)', slide_content, flags=flags)
  if img:
    return img.group()

  # is there another tag on the slide?
  tag = re.search(r'<(.*?)( |>)', slide_content, flags=flags)
  if tag:
    key = tag.group(1)
    element = re.search(r'(<%s.*?</%s>)'%(key, key), my_content, flags=flags)
    if element:
      return element.group()

  # empty slide
  return None

# opinionated
# TODO h1: chapter, h2:slide ?
def setH1AndH2AsSlideHeaders(my_content):
  for start_tag in re.findall(r'<h2', my_content, flags=flags):
    my_content = my_content.replace(start_tag, '<h1')
  for end_tag in re.findall(r'\/h2>', my_content, flags=flags):
    my_content = my_content.replace(end_tag, '/h1>')
  return my_content

def removePlaceholders(my_content):
  if my_content.find('${') > -1:
    for substitution_string in re.findall(r'(\${.*})', my_content):
      my_content = my_content.replace(substitution_string, blank)
  return my_content

def removeComments(my_content):
  for comment_string in re.findall(r'(<!--.*?-->)', my_content, flags=flags):
    my_content = my_content.replace(comment_string, blank)
  return my_content

def removeImageWrappers(my_content):
  img_list = re.findall(r'(<p style=\"text-align: center;\">(.*?)</p>)', my_content, flags=flags)
  for wrapped_image in img_list:
    my_content = my_content.replace(wrapped_image[0], wrapped_image[1])
  return my_content

def removeLineBreaks(my_content):
  return my_content.replace('\n', '').replace('\r', '')

def splitMultipleDetails(my_content):
  for slide in getSlideDetailsList(my_content):
    detail_list = getDetailsList(slide)
    for detail in detail_list[:-1]:
      my_content = my_content.replace(detail, ''.join([detail, details_separator]))
  return my_content

#def removeSlidesWithoutDetailsFromNotes(my_content):
#  for slide in getSlideList(my_content):
#    if getNestedSection(slide) == False:
#      my_content = my_content.replace(slide, blank)
#  content = my_content.replace('<section></section>', blank)
#  content = re.sub(r'<section class="[^"]*"></section>', blank, content)
#  return content

#def removeSectionTags(my_content):
#  content = re.sub(r'<section class="[^"]*">', blank, my_content)
#  content = content.replace('</section>', blank)
#  content = content.replace('<section>', blank)
#  return content

#def removeDetailTags(my_content):
#  content = my_content.replace('</details>', blank)
#  content = content.replace('<details>', blank)
#  content = content.replace('<details open="open">', blank)
#  return content

def removeEmptyDetails(my_content):
  content = my_content.replace('<details open="open"></details>', blank)
  content = content.replace('<details></details>', blank)
  content = content.replace('<details open=""></details>', blank)
  content = content.replace('<details>&nbsp;</details>', blank)
  content = content.replace('<details> </details>', blank)
  return content

def addLastSlide(my_last_slide):
  # XXXX This condition is not accurate
  if my_last_slide.count("<div") != 2:
    last_slide=None
    # search first through web reference
    if doc_theme['theme']:
      last_slide_list = context.portal_catalog(
        portal_type='Web Page',
        reference='%s-Marketing.Slideshow.Last.Slide' % doc_theme['theme'].upper(),
        limit=1)
      if last_slide_list:
        last_slide=last_slide_list[0]
    if not last_slide:
      # get default one
      last_slide_relative_url = pref.getPreferredCorporateIdentityTemplateSlideLastSlideRelativeUrl()
      if last_slide_relative_url:
        last_slide = doc.restrictedTraverse(last_slide_relative_url)

    if last_slide:
      return last_slide.getTextContent()

  return blank

# -------------------------- Setup ---------------------------------------------
doc = context
doc_prefix = pref.getPreferredCorporateIdentityTemplateSlideDocumentPrefix() or "Slideshow."
doc_upgraded_content = None
doc_slide_iter = None
doc_format = kw.get('format') or 'html'
doc_display_notes = int(kw.get('display_note') or 0)
doc_display_svg = kw.get('display_svg') or 'png'
doc_download = int(kw.get('document_download') or 0)
doc_save = int(kw.get('document_save') or 0)
doc_ooo = kw.get('remote_content') or None
doc_content = doc_ooo or doc.getTextContent()
if not doc_content:
  return
doc_is_slideshow = getSlideList(doc_content) or None

override_logo_reference = kw.get('override_logo_reference', None)
override_source_organisation_title = kw.get("override_source_organisation_title", None)
override_batch_mode = kw.get('batch_mode')

doc_theme = doc.Base_getThemeDict(doc_format=doc_format, css_path="template_css/slide", skin="Slide")

# --------------------- Convert any page into a slideshow ----------------------
# Note: mileage varies depending on the cleanliness of the HTML page
if doc_is_slideshow is None:

  doc_upgraded_content = removePlaceholders(doc_content)
  doc_upgraded_content = removeComments(doc_upgraded_content)
  doc_upgraded_content = removeImageWrappers(doc_upgraded_content)
  doc_upgraded_content = setH1AndH2AsSlideHeaders(doc_upgraded_content)
  doc_upgraded_content = removeLineBreaks(doc_upgraded_content)

  section_start = '<section>'
  details_start = '<details open="open">'
  details_end = '</details>'
  section_end = '</section>'

  # separate by <h1>, these will be our slide headers
  fake_slide_list = re.split(r'(<h1.*?/h1>)', doc_upgraded_content, flags=flags)

  # insert page title if first element isn't a <h1>
  if '<h1' not in fake_slide_list[0]:
    fake_slide_list.insert(0, getHeaderSlideTitle(doc))

  # opinionated add of a "Thank you" slide if the last slide doesn't
  # contain the default two <div> columns
  last_slide_content = addLastSlide(fake_slide_list[-1])

  # fake_slide_list will be <h1>,<content>,<h1>,<content> so we need to go
  # over two items at a time
  doc_slide_iter = iter(fake_slide_list)
  doc_content = blank
  for x in doc_slide_iter:
    slide_header = x

    # remove whitespace so we don't end up with empty <details>
    slide_content = " ".join(next(doc_slide_iter).split())

    # build slides assuming the first element after the header is on the slide
    # (an img, a paragraph, a list, whatever). The rest goes into details. If
    # there is an img on the slide, move it to the top
    slide_front = getSlideFront(slide_content)
    if slide_front:
      slide_content = slide_content.replace(slide_front, blank)
    else:
      slide_front = blank

    # build a new doc from slides
    doc_content = doc_content + section_start + slide_header + slide_front \
      + details_start + slide_content + details_end + section_end \

# other case: we have a slideshow, doc_is_slideshow contains the slides
else:
  last_slide_content = addLastSlide(doc_is_slideshow[-1])

# add last slide if required
doc_content = doc_content + last_slide_content

# -------------------------- Document Parameters  ------------------------------
doc_content = removeEmptyDetails(doc_content)
doc_title = doc.getShortTitle() or doc.getTitle()
doc_language = doc.getLanguage()
doc_description = doc.getDescription()
doc_creation_date = doc.getCreationDate()
doc_creation_year = doc_creation_date.strftime('%Y') if doc_creation_date else blank
doc_version = doc.getVersion() or "001"
doc_reference = doc.getReference()
doc_relative_url = doc.getRelativeUrl()
doc_aggregate_list = []
doc_modification_date = doc.getModificationDate()

if override_batch_mode:
  doc_version = "001"
  doc_creation_year = "1976"
if doc_language and doc_language != blank:
  doc.REQUEST['AcceptLanguage'].set(doc_language, 10)
else:
  doc_language = blank
if doc_reference is None:
  doc_reference = doc_prefix + doc_title.replace(" ", ".")
doc_full_reference = '-'.join([doc_reference, doc_version, doc_language])

# --------------------------- Layout Parameters --------------------------------
doc_css = ''.join(['.ci-slideshow-intro.present:not(.slide-background):before {',
  'content: "%s";' % (doc_theme.get("theme_logo_description")),
  'background: #FFF url("%s") center no-repeat;' % (doc.Base_setUrl(path=doc_theme.get("theme_logo_url"), display="medium")),
  #'background-size: auto 120px;',
  #'background-size: auto 45% !important;',
'}'])

# ---------------------------------- Source ------------------------------------
doc_source = doc.Base_getSourceDict(
  override_source_organisation_title=override_source_organisation_title,
  override_logo_reference=override_logo_reference,
  theme_logo_url=doc_theme.get("theme_logo_url", None)
)
# --------------------------- Content Upgrades ---------------------------------
for image in re.findall('(<img.*?/>)', doc_content):
  doc_content = doc_content.replace(
    image,
    doc.WebPage_validateImage(
      img_string=image,
      img_svg_format=doc_display_svg
    )
  )

# ========================= TRANSFORMATION: book ===============================
# XXX still dirty
#if doc_transformation == "book":
#
#  intro_slide = ''.join([
#    '<h1 i18n:translate="" i18n:domain="erp5_ui">Introduction</h1>',
#    '<p>%s</p>' % doc_description,
#    '${WebPage_insertTableOfReferences}'
#  ])
#  doc_content = ''.join([intro_slide, doc_content])
#
#  for slide in getSectionSlideList(doc_content):
#    mod_slide = removeEmptyDetails(slide)
#    mod_slide = removeDetailTags(mod_slide)
#    if slide.find('class="chapter"') == -1:
#      mod_slide = doc.WebPage_downgradeHeaders(mod_slide, 1)
#    mod_slide = removeSectionTags(mod_slide)
#    doc_content = doc_content.replace(slide, mod_slide)
#
#  for table in re.findall('(<table.*?<\/table>)', doc_content):
#    doc_content = doc_content.replace(table, doc.WebPage_validateTable(table_string=table))
#
#  for link in re.findall('(<a.*?<\/a>)', document_content):
#    doc_content = doc_content.replace(link, doc.WebPage_validateLink(link_string=link, link_toc=true))


# ------------- backcompat: old slideshow -------------------------------------
# requires to wrap content of slides that contain <details> into nested
# <section> tags. Done here, after book, because it adds more complexity
if getDetails(doc_content) > -1:
  for slide in getSlideList(doc_content):
    if getDetails(slide) > -1:
      cleaned = slide.split('<details')[0]
      wrapped = ''.join(["<section>", cleaned, "</section>"])
      updated = slide.replace(cleaned, wrapped)

      # fix closed details
      details = updated.replace('<details>', '<details open="open">')

      # XXX split content above 1600 chars into multiple details tags?
      doc_content = doc_content.replace(slide, details)

# ======================== Format: html ==================================
if doc_format == "html":
  doc_output = doc.WebPage_createSlideshow(
    doc_format=doc_format,
    doc_theme=doc_theme.get("theme"),
    doc_title=doc_title,
    doc_language=doc_language,
    doc_template_css_url=doc_theme.get("template_css_url"),
    doc_theme_css_font_list=doc_theme.get("theme_css_font_list"),
    doc_theme_css_url=doc_theme.get("theme_css_url"),
    doc_footer_url_description=doc_theme.get("theme_logo_description"),
    doc_footer_url=doc_source.get("enhanced_logo_data_url", doc.Base_setUrl(path=doc_source.get("enhanced_logo_url"), display=None)),
    doc_description=doc_description,
    doc_creation_year=doc_creation_year,
    doc_copyright=doc_source.get("organisation_title", blank),
    doc_author_list=doc_source.get("contributor_title_string"),
    doc_css=doc_css,
    doc_content=doc_content
  )

  return doc.Base_finishWebPageCreation(
    doc_download=doc_download,
    doc_save=doc_save,
    doc_version=doc_version,
    doc_title=doc_title,
    doc_relative_url=doc_relative_url,
    doc_aggregate_list=doc_aggregate_list,
    doc_language=doc_language,
    doc_modification_date=doc_modification_date,
    doc_reference=doc_reference,
    doc_full_reference=doc_full_reference,
    doc_html_file=doc_output
  )

# ============================= Format: pdf/mhtml ====================================
if doc_format == "pdf" or doc_format == "mhtml":
  doc_slideshow_footer = doc.WebPage_createSlideshowFooter(
    doc_format=doc_format,
    doc_theme=doc_theme.get("theme"),
    doc_title=doc_title,
    doc_language=doc_language,
    doc_template_css_url=doc_theme.get("template_css_url"),
    doc_theme_css_font_list=doc_theme.get("theme_css_font_list"),
    doc_theme_css_url=doc_theme.get("theme_css_url"),
    doc_footer_url_description=doc_theme.get("theme_logo_description"),
    doc_footer_url=doc_source.get("enhanced_logo_data_url", doc.Base_setUrl(path=doc_source.get("enhanced_logo_url"), display=None)),
    doc_description=doc_description,
    doc_creation_year=doc_creation_year,
    doc_copyright=doc_source.get("organisation_title", blank),
    doc_author_list=doc_source.get("contributor_title_string"),
    doc_css=doc_css
  )
  doc_slideshow_cover = doc.WebPage_createSlideshowCover(
    doc_format=doc_format,
    doc_theme=doc_theme.get("theme"),
    doc_title=doc_title,
    doc_language=doc_language,
    doc_template_css_url=doc_theme.get("template_css_url"),
    doc_theme_css_font_list=doc_theme.get("theme_css_font_list"),
    doc_theme_css_url=doc_theme.get("theme_css_url"),
    doc_css=doc_css,
    doc_orientation="ci-orientation-portrait" if doc_display_notes else "ci-corientation-landscape"
  )
  # outputting just the content requires to drop wrapping <divs> (reveal/slides)
  # and add extra css to recreate the same layout. so a separate output=content
  # instead of defaulting to None
  if doc_display_notes:
    doc_slideshow_notes = doc.WebPage_createSlideshowNotes(
      doc_format=doc_format,
      doc_theme=doc_theme.get("theme"),
      doc_title=doc_title,
      doc_language=doc_language,
      doc_template_css_url=doc_theme.get("template_css_url"),
      doc_theme_css_font_list=doc_theme.get("theme_css_font_list"),
      doc_theme_css_url=doc_theme.get("theme_css_url"),
      #doc_notes=splitMultipleDetails(removeSlidesWithoutDetailsFromNotes(doc_content)),
      doc_notes=splitMultipleDetails(doc_content)
    )
  else:
    doc_slideshow_content = doc.WebPage_createSlideshowContent(
    doc_format=doc_format,
    doc_theme=doc_theme.get("theme"),
    doc_title=doc_title,
    doc_language=doc_language,
    doc_template_css_url=doc_theme.get("template_css_url"),
    doc_theme_css_font_list=doc_theme.get("theme_css_font_list"),
    doc_theme_css_url=doc_theme.get("theme_css_url"),
    doc_content=doc_content
  )

  # ================ encode and build cloudoo elements =========================
  footer_embedded_html_data = doc.Base_convertHtmlToSingleFile(doc_slideshow_footer, allow_script=True).encode('utf-8')
  #embedded_html_data = doc.Base_convertHtmlToSingleFile(doc_slideshow_content, allow_script=True).encode('utf-8')
  cover = doc.Base_convertHtmlToSingleFile(doc_slideshow_cover, allow_script=True).encode('utf-8')
  before_body_data_list = [
    b64encode(cover).decode(),
  ]
  if doc_format == "mhtml":
    context.REQUEST.RESPONSE.setHeader("Content-Type", "text/html;")
    return doc.Base_convertHtmlToSingleFile(doc_slideshow_cover, allow_script=True)
  if doc_display_notes:
    #after_body_data_list = [
    #  b64encode(doc.Base_convertHtmlToSingleFile(doc_slideshow_notes, allow_script=True).encode('utf-8')).decode(),
    #]
    embedded_html_data = doc.Base_convertHtmlToSingleFile(doc_slideshow_notes, allow_script=True).encode('utf-8')
    after_body_data_list = []
  else:
    embedded_html_data = doc.Base_convertHtmlToSingleFile(doc_slideshow_content, allow_script=True).encode('utf-8')
    after_body_data_list = []
    #after_body_data_list = []
  pdf_file = doc.Base_cloudoooDocumentConvert(embedded_html_data, "html", "pdf", conversion_kw=dict(
      encoding="utf8",
      orientation= "portrait" if doc_display_notes else "landscape",
      margin_top=12,
      margin_bottom=20,
      before_body_data_list=before_body_data_list,
      after_body_data_list=after_body_data_list,
      header_spacing=10,
      footer_html_data=b64encode(footer_embedded_html_data).decode(),
      footer_spacing=3
    )
  )

  return doc.WebPage_finishPdfCreation(
    doc_download=doc_download,
    doc_save=doc_save,
    doc_version=doc_version,
    doc_title=doc_title,
    doc_relative_url=doc_relative_url,
    doc_aggregate_list=doc_aggregate_list,
    doc_language=doc_language,
    doc_modification_date=doc_modification_date,
    doc_reference=doc_reference,
    doc_full_reference=doc_full_reference,
    doc_pdf_file=pdf_file
  )
