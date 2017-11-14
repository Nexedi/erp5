"""
================================================================================
MAIN FILE: generate presentation in different output formats
================================================================================
"""
# kw-parameters   (* default)
# ------------------------------------------------------------------------------
# format:                   output in html*, pdf
# note_display:             display slide notes (1) or not (0)*
# svg_display:              display svg-images as svg or png*
# transformation:           convert content into nothing*, book
# ------
# override_logo_reference:  to use instead of default company logo in footer
# override_publisher_title: to use instead of default company publisher
# override_batch_mode:      used for tests
# ------
# flag_download:            download file directly (default None)            
# flag_save:                save file in document module (default None)
# flag_ooo:                 convert from legacy odp, sxi formats (default None)

import re

from Products.PythonScripts.standard import html_quote
from base64 import b64encode

empty_string = ''

# --------------------------  External parameters ------------------------------

# eg "Nexedi" specific parameters
customHandler = getattr(context, "WebPage_getCustomParameter", None)

# parameters common to all templates
commonHandler = getattr(context, "WebPage_getCommonParameter", None)
commonProxyHandler = getattr(context, "WebPage_getCommonProxyParameter", None)

# parameters specific to this template
localHandler = getattr(context, "WebPage_getLocalParameter", None)
localProxyHandler = getattr(context, "WebPage_getLocalProxyParameter", None)

def getCustomParameter(my_parameter, my_override_data):
  if customHandler is not None:
    source_data = my_override_data or doc_uid
    return customHandler(parameter=my_parameter, source_data=source_data)

def getCommonParameter(my_parameter, my_override_data):
  if commonHandler is not None:
    source_data = my_override_data or doc_uid
    return commonHandler(parameter=my_parameter, source_data=source_data)

def getCommonProxyParameter(my_parameter, my_override_data):
  if commonProxyHandler is not None:
    source_data = my_override_data or doc_uid
    return commonProxyHandler(parameter=my_parameter, source_data=source_data)

def getLocalParameter(my_parameter, my_override_data):
  if localHandler is not None:
    source_data = my_override_data or doc_uid
    return localHandler(parameter=my_parameter, source_data=source_data)

def getLocalProxyParameter(my_parameter, my_override_data):
  if localProxyHandler is not None:
    source_data = my_override_data or doc_uid
    return localProxyHandler(parameter=my_parameter, source_data=source_data)

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
      my_content = my_content.replace(slide, empty_string)
  content = my_content.replace('<section></section>', empty_string)
  content = re.sub(r'<section class="[^"]*"></section>', empty_string, content)
  return content

def removeSectionTags(my_content):
  content = re.sub(r'<section class="[^"]*">', empty_string, my_content)
  content = content.replace('</section>', empty_string)
  content = content.replace('<section>', empty_string)
  return content
  
def removeDetailTags(my_content):
  content = my_content.replace('</details>', empty_string)
  content = content.replace('<details>', empty_string)
  content = content.replace('<details open="open">', empty_string)
  return content

def removeEmptyDetails(my_content):
  content = my_content.replace('<details open="open"></details>', empty_string)
  content = content.replace('<details></details>', empty_string)
  content = content.replace('<details>&nbsp;</details>', empty_string)
  content = content.replace('<details> </details>', empty_string)
  # more to come
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
    return result_list[1].replace("</body>", "")

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

      # XXX cloudooo html-transformation mixes up slide order! dirty fix
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
doc_converted_content = None
doc_uid = doc.getUid()
doc_url = doc.getAbsoluteUrl()
doc_format = kw.get('format', 'html')
doc_transformation = kw.get('transformation', None)
doc_display_notes = kw.get('note_display', None)
doc_display_svg = kw.get('svg_display', None)
doc_download = kw.get('flag_download', None)
doc_save = kw.get('flag_save', None)
doc_ooo = kw.get('flag_ooo', None)

override_doc_logo = kw.get('override_logo_reference', None)
override_doc_publisher = kw.get("override_publisher_title", None)
override_batch_mode = kw.get('batch_mode', False)

follow_up_doc_publisher = None

# ---------- backward compatability with legacy odp/sxi presentations ----------
# note: this has to come first to convert file into html and then continue
if doc_ooo is not None:
  doc_portal = doc.getPortalObject()
  if doc.getPortalType() in ["Presentation"]:
    raw_data = doc_portal.portal_transforms.convertToData(
      "text/html",
      str(context.getData() or empty_string),
      context=context,
      mimetype=context.getContentType()
    )
    if raw_data is None:
      raise ValueError("Failed to convert to %r" % "text/html")

    # got something
    page_list = getPageList(raw_data)
    if len(page_list) > 0:
      page_content = sortContent(page_list)
      doc_converted_content = empty_string
      for slide in page_content:
        if slide[1].find("<center>") > -1:
          slide_content_list = slide[1].split("<h3>Notes:</h3>")
          if len(slide_content_list) != 2:
            slide_content = slide[1]
            slide_notes = empty_string
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
doc_language = doc.getLanguage()
doc_description = doc.getDescription()
doc_creation_year = doc.getCreationDate().strftime('%Y')
doc_full_reference = '-'.join([doc.getReference(), doc.getVersion(), doc_language])

if doc_language and doc_format == "pdf":
  doc.REQUEST['AcceptLanguage'].set(doc_language, 10)

# --------------------------- Layout Parameters --------------------------------
doc_theme_claim = empty_string
doc_theme_logo = None
doc_theme_logo_url = None
doc_theme_footer_url = override_doc_logo
doc_pdf = ".pdf" if doc_format == "pdf" else empty_string
doc_template_css_url = ''.join([doc_url, "/slide_css/slide", doc_pdf, ".css"])
doc_fallback_img_url = ''.join([doc_url, '/', getCommonParameter("fallback_image", None)])
doc_logo_prefix = getCustomParameter("default_logo_prefix", None)

# XXX simplify
doc_theme_css_font_list = getCustomParameter("default_theme_font_css_url_list", None) or []
doc_theme_css_url = (
  getCustomParameter("default_theme_css_url", None) or 
  getCommonParameter("default_theme_css_url", None) or 
  empty_string
)

doc_publisher_list = getLocalProxyParameter("publisher", None)
if doc_publisher_list and len(doc_publisher_list) > 0:
  follow_up_doc_publisher = doc_publisher_list[0].get("organisation") or None
doc_publisher = (
  getCustomParameter("default_company_title", None) or
  empty_string
)
doc_copyright = (
  override_doc_publisher or
  follow_up_doc_publisher or
  getCustomParameter("default_company_title", None) or
  empty_string
)

# theme
doc_theme = (
  getLocalProxyParameter("theme", None) or
  getCustomParameter("theme", None) or
  doc_publisher
)
if doc_theme and override_batch_mode:
  doc_theme = "default"
if doc_theme:
  doc_theme = doc_theme.lower()
  if doc_logo_prefix:
    doc_theme_logo_url = doc_logo_prefix + doc_theme.capitalize()
    doc_theme_logo = context.restrictedTraverse(doc_theme_logo_url)
    doc_theme_footer_url = doc_theme_footer_url or (doc_logo_prefix + doc_publisher)
  if doc_theme_logo:
    doc_theme_claim = doc_theme_logo.getDescription()
else:
  doc_theme = "default"
  doc_theme_logo_url = doc_fallback_img_url

doc_theme_footer_url = doc_theme_footer_url or doc_fallback_img_url
doc_author_list = ', '.join(c.get("name") for c in getLocalProxyParameter("author", [])) or empty_string
doc_css = ''.join(['.ci-slideshow-intro.present:not(.slide-background):before {',
  'content: "%s";' % (doc_theme_claim),
  'background: #FFF url("%s?format=png&amp;display=small") center no-repeat;' % (doc_theme_logo_url),
  'background-size: auto 120px;'
'}'])

# --------------------------- Content Upgrades ---------------------------------

for image in re.findall('(<img.*?/>)', doc_content):
  doc_content = doc_content.replace(image, context.WebPage_validateImage(img_string=image, img_svg_format=doc_display_svg))

# ========================= TRANSFORMATION: book ===============================

# XXX still dirty
if doc_transformation == "book":

  intro_slide = ''.join([
    '<h1 i18n:translate="" i18n:domain="erp5_ui">Introduction</h1>',
    '<p>%s</p>' % doc_description,
    '${WebPage_insertTableOfReferences}'
  ])
  doc_content = ''.join([intro_slide, doc_content])

  for slide in getSectionSlideList(doc_content):
    mod_slide = removeEmptyDetails(slide)
    mod_slide = removeDetailTags(mod_slide)
    if slide.find('class="chapter"') == -1:
      mod_slide = context.WebPage_downgradeHeaders(mod_slide, 1)
    mod_slide = removeSectionTags(mod_slide)
    doc_content = doc_content.replace(slide, mod_slide)

  for table in re.findall('(<table.*?<\/table>)', doc_content):
    doc_content = doc_content.replace(table, context.WebPage_validateTable(table_string=table))

  for link in re.findall('(<a.*?<\/a>)', document_content):
    doc_content = doc_content.replace(link, context.WebPage_validateLink(link_string=link, link_toc=true))

  # XXX return?
  return document_content

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

# ============================= Format: html ===================================
if doc_format == "html":
  doc.REQUEST.RESPONSE.setHeader("Content-Type", "text/html;")
  return context.WebPage_createSlideshow(
    # meta
    doc_format=doc_format,
    doc_theme=doc_theme,
    doc_title=html_quote(doc_title),
    doc_language=doc_language,
    doc_template_css_url=doc_template_css_url,
    doc_theme_css_font_list=doc_theme_css_font_list,
    doc_theme_css_url=doc_theme_css_url,
    #footer
    doc_theme_footer_url=html_quote(doc_theme_footer_url),
    doc_description=html_quote(doc_description),
    doc_creation_year=html_quote(doc_creation_year),
    doc_copyright=html_quote(doc_copyright),
    doc_author_list=html_quote(doc_author_list),
    # cover
    doc_css=doc_css,
    # content
    doc_content=doc_content,
    # notes are on the slide
    #doc_display_notes=doc_display_notes,
    #doc_notes=removeSlidesWithoutDetailsFromNotes(doc_content)
  )

# ============================= Format: pdf ====================================
if doc_format == "pdf":
  doc_slideshow_footer = context.WebPage_createSlideshowFooter(
    # meta
    doc_format=doc_format,
    doc_theme=doc_theme,
    doc_title=html_quote(doc_title),
    doc_language=doc_language,
    doc_template_css_url=doc_template_css_url,
    doc_theme_css_font_list=doc_theme_css_font_list,
    doc_theme_css_url=doc_theme_css_url,
    #footer
    doc_theme_footer_url=html_quote(doc_theme_footer_url),
    doc_description=html_quote(doc_description),
    doc_creation_year=html_quote(doc_creation_year),
    doc_copyright=html_quote(doc_copyright),
    doc_author_list=html_quote(doc_author_list)
  )
  doc_slideshow_cover = context.WebPage_createSlideshowCover(
    # meta
    doc_format=doc_format,
    doc_theme=doc_theme,
    doc_title=html_quote(doc_title),
    doc_language=doc_language,
    doc_template_css_url=doc_template_css_url,
    doc_theme_css_font_list=doc_theme_css_font_list,
    doc_theme_css_url=doc_theme_css_url,
    # cover
    doc_css=doc_css
  )

  # outputting just the content requires to drop wrapping <divs> (reveal/slides)
  # and add extra css to recreate the same layout. so a separate output=content
  # instead of defaulting to None
  doc_slideshow_content = context.WebPage_createSlideshowContent(
    # meta
    doc_format=doc_format,
    doc_theme=doc_theme,
    doc_title=html_quote(doc_title),
    doc_language=doc_language,
    doc_template_css_url=doc_template_css_url,
    doc_theme_css_font_list=doc_theme_css_font_list,
    doc_theme_css_url=doc_theme_css_url,
    # content
    doc_content=doc_content
  )
  if doc_display_notes:
    doc_slideshow_notes = context.WebPage_createSlideshowNotes(
      # meta
      doc_format=doc_format,
      doc_theme=doc_theme,
      doc_title=html_quote(doc_title),
      doc_language=doc_language,
      doc_template_css_url=doc_template_css_url,
      doc_theme_css_font_list=doc_theme_css_font_list,
      doc_theme_css_url=doc_theme_css_url,
      # notes
      doc_notes=removeSlidesWithoutDetailsFromNotes(doc_content)
    )

  # ================ encode and build cloudoo elements =========================
  # parameters => https://lab.nexedi.com/nexedi/cloudooo/blob/master/cloudooo/handler/wkhtmltopdf/handler.py
  # before_body_data_list
  # embedded_html_data
  # after_body_data_list
  # footer_embedded_html_data
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

  pdf_file = context.Base_cloudoooDocumentConvert(embedded_html_data, "html", "pdf", conversion_kw=dict(
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

  if doc_save:
    dms_module = getattr(context, 'document_module', None)
    if dms_module is not None:
      save_document = dms_module.newContent(
        portal_type="PDF",
        title=doc_title,
        language=doc_language,
        reference=doc_full_reference
      )
      save_document.edit(
        source_reference=''.join([doc_reference, '.pdf']), 
        file=pdf_file
      )
    
      message = context.Base_translateString(
        '%(portal_type)s created successfully as PDF Document.' % {
          'portal_type': save_document.getTranslatedPortalType()
        }
      )
    
      return document.Base_redirect(
        keep_items=dict(portal_status_message=message)
      )
  elif doc_download:
    doc.REQUEST.RESPONSE.setHeader("Content-Type", "application/pdf;")
    doc.REQUEST.RESPONSE.setHeader("Content-Disposition", 'attachment; filename="' + doc_full_reference + '.pdf"')
  else:
    doc.REQUEST.RESPONSE.setHeader("Content-Type", "application/pdf;")
    doc.REQUEST.RESPONSE.setHeader("Content-Disposition", 'filename="' + doc_full_reference + '.pdf"')
  return pdf_file

# XXX throw if all fails?
raise Exception("No or unsupported format: " + str(doc_format))
