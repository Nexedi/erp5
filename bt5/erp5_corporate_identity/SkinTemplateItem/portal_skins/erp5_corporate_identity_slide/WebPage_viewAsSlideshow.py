"""
================================================================================
MAIN FILE: generate presentation in different output formats
================================================================================
"""
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
# flag_ooo:                 convert legacy odp, sxi formats (not active)

import re

from Products.PythonScripts.standard import html_quote
from base64 import b64encode

blank = ''

# ------------------ HTML cleanup/converter methods ----------------------------
def getSlideList(my_content):
  return re.findall(r'<section[^>]*?>(.*?)</section>', my_content, re.S)

def getSectionSlideList(my_content):
  return re.findall(r'(<section[^>]*?>.*?</section>)', my_content, re.S)

def getDetails(my_content):
  return my_content.find("</details>")

def getNestedSection(my_content):
  return my_content.find("<section") > -1

def removeSlidesWithoutDetailsFromNotes(my_content):
  slide_list = getSlideList(my_content)
  for slide in slide_list:
    if getNestedSection(slide) is False:
      my_content = my_content.replace(slide, blank)
  content = my_content.replace('<section></section>', blank)
  content = re.sub(r'<section class="[^"]*"></section>', blank, content)
  return content

def removeSectionTags(my_content):
  content = re.sub(r'<section class="[^"]*">', blank, my_content)
  content = content.replace('</section>', blank)
  content = content.replace('<section>', blank)
  return content
  
def removeDetailTags(my_content):
  content = my_content.replace('</details>', blank)
  content = content.replace('<details>', blank)
  content = content.replace('<details open="open">', blank)
  return content

def removeEmptyDetails(my_content):
  content = my_content.replace('<details open="open"></details>', blank)
  content = content.replace('<details></details>', blank)
  content = content.replace('<details>&nbsp;</details>', blank)
  content = content.replace('<details> </details>', blank)
  return content

def getPageList(my_content):
  return re.findall(r'<html>(.*?)</html>', my_content, re.S)

def getPageTitle(my_full_page):
  result = re.search('<title>(.+?)</title>', my_full_page)
  if result:
    return result.group(1)

def getPageContent(my_full_page):
  result_list = my_full_page.split("</center><br>")
  if len(result_list) == 2:
    return result_list[1].replace("</body>", blank)

def addSlideContent(my_content, my_notes):
  return ''.join([
    '<section>',
    my_content,
    '<details open="open">',
    my_notes,
    '</details></section>'
  ])

def sortContent(my_page_list):
  try:
    page_content_list = []
    page_tuple_first = None
    page_tuple_last = None
    for page in my_page_list:
      page_title = getPageTitle(page)

      # Note cloudooo default html transformation mixes slide order. dirty fix
      if page_title.find("Commercial") > -1:
        page_content = getPageContent(page)
        if page_content.find("<center>") > -1:
          page_tuple_last = (page_title, page_content, "first")
      elif page_title.find("ERP5") > -1:
        page_content = getPageContent(page)
        if page_content.find("<center>") > -1:
          page_tuple_first = (page_title, page_content, "last")
      else:
        page_content = getPageContent(page)
        if page_title.find("Slide") > -1:
          slide_number = int(page_title.replace("Slide ", ""))
          page_content_list.append((slide_number, page_content, None))
        else:
          if page_content.find("<center>") > -1:
            page_tuple_first = (page_title, page_content, "first")
      sort_content_list = sorted(page_content_list, key=lambda page_foo: page_foo[0])
    if page_tuple_last is not None:
      sort_content_list.append(page_tuple_last)
    if page_tuple_first is not None:
      sort_content_list = [page_tuple_first] + sort_content_list
    return sort_content_list

  except Exception as e:
    raise e

# -------------------------- Setup ---------------------------------------------
doc = context
doc_prefix = "Slideshow."
doc_converted_content = None
doc_uid = doc.getUid()
doc_url = doc.getAbsoluteUrl()
doc_format = kw.get('format', 'html')
doc_transformation = kw.get('transformation', None)
doc_display_notes = doc.Base_setToNone(param=kw.get('display_note', None))
doc_display_svg = doc.Base_setToNone(param=kw.get('display_svg', 'png'))
doc_download = doc.Base_setToNone(param=kw.get('document_download', None))
doc_save = doc.Base_setToNone(param=kw.get('document_save', None))
doc_ooo = doc.Base_setToNone(param=kw.get('flag_ooo', None))

override_logo_reference = kw.get('override_logo_reference', None)
override_source_organisation_title = kw.get("override_source_organisation_title", None)
override_batch_mode = doc.Base_setToNone(param=kw.get('batch_mode', None))
override_source_person_title = None

# ---------- backward compatability with legacy odp/sxi presentations ----------
# note: this has to come first to convert file into html and then continue
if doc_ooo is not None:
  doc_portal = doc.getPortalObject()
  if doc.getPortalType() in ["Presentation"]:
    raw_data = doc_portal.portal_transforms.convertToData(
      "text/html",
      str(doc.getData() or blank),
      context=context,
      mimetype=doc.getContentType()
    )
    if raw_data is None:
      raise ValueError("Failed to convert to %r" % "text/html")

    # got something
    page_list = getPageList(raw_data)
    if len(page_list) > 0:
      page_content = sortContent(page_list)
      doc_converted_content = blank
      for slide in page_content:
        if slide[1].find("<center>") > -1:
          slide_content_list = slide[1].split("<h3>Notes:</h3>")
          if len(slide_content_list) != 2:
            slide_content = slide[1]
            slide_notes = blank
          else:
            slide_content = slide_content_list[0]
            slide_content = slide_content.replace("<center>", "")
            slide_content = slide_content.replace("</center>", "")
            slide_notes = slide_content_list[1]
          doc_converted_content += addSlideContent(slide_content, slide_notes)

# -------------------------- Document Parameters  ------------------------------
doc_uid = doc.getUid()
doc_dirty_content = doc_converted_content or doc.getTextContent()
doc_content = removeEmptyDetails(doc_dirty_content)
doc_title = doc.getTitle()
doc_language = doc.Base_setToNone(param=doc.getLanguage())
doc_description = doc.getDescription()
doc_creation_year = doc.getCreationDate().strftime('%Y')
doc_version = doc.getVersion() or "001"
doc_reference = doc.getReference()
doc_relative_url = doc.getRelativeUrl()
doc_aggregate_list = []
doc_modification_date = doc.getModificationDate()

if override_batch_mode is not None:
  doc_version = "001"
  doc_creation_year = "1976"
if doc_language is not None: #and doc_format == "pdf":
  doc.REQUEST['AcceptLanguage'].set(doc_language, 10)
if doc_language is None:
  doc_language = blank
if doc_reference is None:
  doc_reference = doc_prefix + doc_title.replace(" ", ".")
doc_full_reference = '-'.join([doc_reference, doc_version, doc_language])

# --------------------------- Layout Parameters --------------------------------
doc_theme = doc.Base_getThemeDict(format=doc_format, css_path="slide_css/slide")
doc_css = ''.join(['.ci-slideshow-intro.present:not(.slide-background):before {',
  'content: "%s";' % (doc_theme.get("theme_logo_description")),
  'background: #FFF url("%s") center no-repeat;' % (doc_theme.get("theme_logo_url")),
  'background-size: auto 120px;'
'}'])

# ---------------------------------- Source ------------------------------------
doc_source = doc.Base_getSourceDict(
  override_source_person_title=override_source_person_title,
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
#

# ------------- backwards compatability with old slideshow ---------------------
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

# ======================== Format: html/mhtml ==================================
if doc_format == "html" or doc_format == "mhtml":
  doc_output = doc.WebPage_createSlideshow(
    doc_format=doc_format,
    doc_theme=doc_theme.get("theme"),
    doc_title=doc_title,
    doc_language=doc_language,
    doc_template_css_url=doc_theme.get("template_css_url"),
    doc_theme_css_font_list=doc_theme.get("theme_css_font_list"),
    doc_theme_css_url=doc_theme.get("theme_css_url"),
    doc_footer_url=doc.Base_setUrl(path=doc_source.get("enhanced_logo_url")),
    doc_description=doc_description,
    doc_creation_year=doc_creation_year,
    doc_copyright=doc_source.get("organisation_title", blank),
    doc_author_list=doc_source.get("contributor_title_string"),
    doc_css=doc_css,
    doc_content=doc_content
  )
  if doc_format == "html":
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
  if doc_format == "mhtml":
    context.REQUEST.RESPONSE.setHeader("Content-Type", "text/html;")
    return doc.Base_convertHtmlToSingleFile(doc_output, allow_script=True)

# ============================= Format: pdf ====================================
if doc_format == "pdf":
  doc_slideshow_footer = doc.WebPage_createSlideshowFooter(
    doc_format=doc_format,
    doc_theme=doc_theme.get("theme"),
    doc_title=doc_title,
    doc_language=doc_language,
    doc_template_css_url=doc_theme.get("template_css_url"),
    doc_theme_css_font_list=doc_theme.get("theme_css_font_list"),
    doc_theme_css_url=doc_theme.get("theme_css_url"),
    doc_footer_url=doc.Base_setUrl(path=doc_source.get("enhanced_logo_url")),
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
    doc_css=doc_css
  )

  # outputting just the content requires to drop wrapping <divs> (reveal/slides)
  # and add extra css to recreate the same layout. so a separate output=content
  # instead of defaulting to None
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
  if doc_display_notes:
    doc_slideshow_notes = doc.WebPage_createSlideshowNotes(
      doc_format=doc_format,
      doc_theme=doc_theme.get("theme"),
      doc_title=doc_title,
      doc_language=doc_language,
      doc_template_css_url=doc_theme.get("template_css_url"),
      doc_theme_css_font_list=doc_theme.get("theme_css_font_list"),
      doc_theme_css_url=doc_theme.get("theme_css_url"),
      doc_notes=removeSlidesWithoutDetailsFromNotes(doc_content)
    )
  
  # ================ encode and build cloudoo elements =========================
  footer_embedded_html_data = doc.Base_convertHtmlToSingleFile(doc_slideshow_footer, allow_script=True)
  embedded_html_data = doc.Base_convertHtmlToSingleFile(doc_slideshow_content, allow_script=True)
  before_body_data_list = [
    b64encode(doc.Base_convertHtmlToSingleFile(doc_slideshow_cover, allow_script=True)),
  ]
  if doc_display_notes:
    after_body_data_list = [
      b64encode(doc.Base_convertHtmlToSingleFile(doc_slideshow_notes, allow_script=True)),
    ]
  else:
    after_body_data_list = []

  pdf_file = doc.Base_cloudoooDocumentConvert(embedded_html_data, "html", "pdf", conversion_kw=dict(
      encoding="utf8",
      orientation="landscape",
      margin_top=12,
      margin_bottom=20,
      before_body_data_list=before_body_data_list,
      after_body_data_list=after_body_data_list,
      header_spacing=10,
      footer_html_data=b64encode(footer_embedded_html_data),
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
