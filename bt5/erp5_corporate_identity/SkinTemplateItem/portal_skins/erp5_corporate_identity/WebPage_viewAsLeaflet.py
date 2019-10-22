"""
================================================================================
MAIN FILE: render two pager in different output formats
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# kw-parameters   (* default)
# ------------------------------------------------------------------------------
# format:                   output in html*, pdf
# display_side:             display side bar (1)* or not (0)
# display_svg:              display images as svg or png*
# transformation:           convert content into nothing*, book
# ------
# override_leaflet_header_title custom title to use in the leaflet header
# override_source_organisation_title used instead of follow-up organisation
# override_source_person_title used instead of contributor
# override_batch_mode       used for tests
# ------
# document_downalod:        download file directly (default None)
# document_save:            save file in document module (default None)

import re

from Products.PythonScripts.standard import html_quote
from base64 import b64encode

blank = ''
pref = context.getPortalObject().portal_preferences

# ------------------ HTML cleanup/converter methods ----------------------------
def removeLegalesePlaceholders(content):
  content = content.replace("${legalese}", "")
  content = content.replace("${document_id}", "")
  return content

# -------------------------- Setup ---------------------------------------------
leaflet = context
leaflet_prefix = pref.getPreferredCorporateIdentityTemplateLeafletDocumentPrefix() or "Leaflet."
leaflet_format = kw.get('format') or 'html'
leaflet_display_svg = kw.get('display_svg') or "png"
leaflet_download = int(kw.get('document_download') or 0)
leaflet_save = int(kw.get('document_save') or 0)
leaflet_display_side = int(kw.get('display_side') or 1)

override_leaflet_header_title = kw.get('override_leaflet_header_title')
override_source_person_title = kw.get('override_source_person_title', None)
override_source_organisation_title = kw.get("override_source_organisation_title", None)
override_batch_mode = kw.get('batch_mode')


# -------------------------- Document Parameters  ------------------------------
leaflet_content = leaflet.getTextContent()
leaflet_title = leaflet.getTitle()
leaflet_relative_url = leaflet.getRelativeUrl()
leaflet_language = leaflet.getLanguage()
leaflet_creation_date = leaflet.getCreationDate()
leaflet_date = leaflet_creation_date.strftime('%Y-%b') if leaflet_creation_date else blank
leaflet_year = leaflet_creation_date.strftime('%Y') if leaflet_creation_date else blank
leaflet_reference = leaflet.getReference()
leaflet_version = leaflet.getVersion() or "001"
leaflet_aggregate_list = []
leaflet_modification_date = leaflet.getModificationDate()

# test overrides
if override_batch_mode:
  leaflet_date="Nov-1976"
  leaflet_year="1976"
if leaflet_language and leaflet_language != blank:
  leaflet.REQUEST['AcceptLanguage'].set(leaflet_language, 10)
else:
  leaflet_language = blank
if leaflet_reference is None:
  leaflet_reference = leaflet_prefix + leaflet_title.replace(" ", ".")
leaflet_full_reference = '-'.join([leaflet_reference, leaflet_version, leaflet_language])

# ---------------------------- Theme Parameters --------------------------------
leaflet_theme = leaflet.Base_getThemeDict(doc_format=leaflet_format, css_path="template_css/leaflet", skin="Leaflet")

if override_leaflet_header_title and override_leaflet_header_title != blank:
  leaflet_theme["theme_logo_description"] = html_quote(override_leaflet_header_title)
if leaflet_theme.get("theme").lower() == leaflet_theme.get("theme_logo_description").lower():
  leaflet_theme["theme_logo_description"] = blank
leaflet_recycle_url = "template_images/recycle.png"
leaflet_css = ''.join([
  'html .ci-leaflet #left-summary:before {',
    'background: url("%s") center no-repeat;' % (leaflet_theme.get("theme_logo_url")),
    'background-size: contain;',
  '}'
])

# ---------------------------------- Source ------------------------------------
leaflet_source = leaflet.Base_getSourceDict(
  override_source_person_title=override_source_person_title,
  override_source_organisation_title=override_source_organisation_title,
  theme_logo_url=leaflet_theme.get("theme_logo_url", None)
)

if leaflet_source.get("enhanced_logo_url") != blank:
  leaflet_css = ''.join([
    leaflet_css,
    'html .ci-leaflet #legalese:before {',
      'background: url("%s") center no-repeat;' % (leaflet_source.get("enhanced_logo_url")),
      'background-size: contain;',
      'content: "";',
      'display: block;',
      'height: 60px;',
    '}'
  ])

# --------------------------- Content Upgrades ---------------------------------
leaflet_content = removeLegalesePlaceholders(leaflet_content)

# custom layout in leaflet
for image in re.findall('(<div class="left-icon">.*?</div>)', leaflet_content):
  img_caption = blank
  caption_list = re.findall('<p class="excerpt">(.*?)</p>', image, re.S)
  if len(caption_list) > 0:
    img_caption=caption_list[0]
  leaflet_content = leaflet_content.replace(
    image,
    leaflet.WebPage_validateImage(
      img_string=image,
      img_svg_format=leaflet_display_svg,
      img_caption=img_caption
    )
  )

# legalese
if leaflet_display_side:
  leaflet_legalese = leaflet.WebPage_createLegalese(
    leaflet_organisation=leaflet_source.get("organisation_title",  None) or blank,
    leaflet_address=leaflet_source.get("address", None) or blank,
    leaflet_postal_code=leaflet_source.get("postal_code", None) or blank,
    leaflet_city=leaflet_source.get("city", None) or blank,
    leaflet_country=leaflet_source.get("country", None) or blank,
    leaflet_email=leaflet_source.get("email", None) or blank,
    leaflet_phone=leaflet_source.get("phone", None) or blank,
    leaflet_date=leaflet_date,
    leaflet_year=leaflet_year,
    leaflet_recycle_url=leaflet_recycle_url
  )
  #leaflet_content = leaflet_legalese.decode() + leaflet_content.decode()

  if isinstance(leaflet_legalese, unicode):
    leaflet_legalese = leaflet_legalese.encode("UTF-8")
  if isinstance(leaflet_content, unicode):
    leaflet_content = leaflet_content.encode("UTF-8")

  leaflet_content = leaflet_legalese + leaflet_content

# ========================= TRANSFORMATION: book ===============================
# XXX still dirty
#if leaflet_transformation == "book":
#
#  leaflet_summary = re.findall('<div id="left-summary">.*?<\/div>', leaflet_content, re.S)
#  leaflet_content = leaflet_content.replace(leaflet_summary[0], "")
#
#  for table in re.findall('(<table.*?<\/table>)', leaflet_content):
#    leaflet_content = leaflet_content.replace(table, leaflet.WebPage_validateTable(table_string=table))
#
#  for link in re.findall('(<a.*?<\/a>)', leaflet_content):
#    leaflet_content = leaflet_content.replace(link, leaflet.WebPage_validateLink(link_string=link, link_toc=true))
#
#  leaflet_content = leaflet_content.replace('<h2 class="summary">', '<h1>')
#  leaflet_content = leaflet_content.replace('</h2>', '</h1>')
#  leaflet_stripped_content = re.findall('<div id="main-content">(.*)?<\/div>', leaflet_content, re.S)
#  leaflet_content = leaflet_stripped_content[0]
#  intro = '<h1 i18n:translate="" i18n:domain="erp5_ui">Introduction</h1>'
#  description = '<p>' + leaflet_description + '</p>'
#  toc = '${WebPage_insertTableOfReferences}'
#  header = '<h1>' + leaflet_title + '</h1>'
#
#  leaflet_content = ''.join([intro, description, toc, header, leaflet_content])

# ============================= Format: html ===================================
if leaflet_format == "html":
  leaflet_output = leaflet.WebPage_createLeaflet(
    leaflet_theme=leaflet_theme.get("theme"),
    leaflet_title=leaflet_title,
    leaflet_language=leaflet_language,
    leaflet_theme_css_font_list=leaflet_theme.get("theme_css_font_list"),
    leaflet_theme_css_url=leaflet_theme.get("theme_css_url"),
    leaflet_template_css_url=leaflet_theme.get("template_css_url"),
    leaflet_organisation=leaflet_source.get("organisation_title", blank),
    leaflet_organisation_claim=leaflet_theme.get("theme_logo_description") or blank,
    leaflet_logo_url=leaflet.Base_setUrl(path=leaflet_source.get("enhanced_logo_url"), display=None),
    leaflet_copyright=leaflet_source.get("organisation_title", blank),
    leaflet_full_reference=leaflet_full_reference,
    leaflet_year=leaflet_year,
    leaflet_contributor_list=leaflet_source.get("contributor_title_string") or blank,
    leaflet_content=leaflet_content,
    leaflet_display_side=leaflet_display_side,
    leaflet_theme_logo_url=leaflet_theme.get("theme_logo_url"),
    leaflet_theme_logo_alt=leaflet_theme.get("theme_logo_alt"),
    leaflet_css=leaflet_css,
  )
  return leaflet.Base_finishWebPageCreation(
    doc_download=leaflet_download,
    doc_save=leaflet_save,
    doc_version=leaflet_version,
    doc_title=leaflet_title,
    doc_relative_url=leaflet_relative_url,
    doc_aggregate_list=leaflet_aggregate_list,
    doc_language=leaflet_language,
    doc_modification_date=leaflet_modification_date,
    doc_reference=leaflet_reference,
    doc_full_reference=leaflet_full_reference,
    doc_html_file=leaflet_output
  )

# ============================= Format: pdf ====================================
if leaflet_format == "pdf":
  leaflet_head = leaflet.WebPage_createLeafletHeader(
    leaflet_theme=leaflet_theme.get("theme"),
    leaflet_title=leaflet_title,
    leaflet_language=leaflet_language,
    leaflet_theme_css_font_list=leaflet_theme.get("theme_css_font_list"),
    leaflet_theme_css_url=leaflet_theme.get("theme_css_url"),
    leaflet_template_css_url=leaflet_theme.get("template_css_url"),
    leaflet_organisation=leaflet_source.get("organisation_title", blank),
    leaflet_organisation_claim=leaflet_theme.get("theme_logo_description"),
  )

  leaflet_foot = leaflet.WebPage_createLeafletFooter(
    leaflet_theme=leaflet_theme.get("theme"),
    leaflet_title=leaflet_title,
    leaflet_language=leaflet_language,
    leaflet_theme_css_font_list=leaflet_theme.get("theme_css_font_list"),
    leaflet_theme_css_url=leaflet_theme.get("theme_css_url"),
    leaflet_template_css_url=leaflet_theme.get("template_css_url"),
    leaflet_logo_url=leaflet.Base_setUrl(path=leaflet_source.get("enhanced_logo_url"), display=None),
    leaflet_copyright=leaflet_source.get("organisation_title", blank),
    leaflet_full_reference=leaflet_full_reference,
    leaflet_year=leaflet_year,
    leaflet_contributor_list=leaflet_source.get("contributor_title_string"),
  )

  leaflet_content = leaflet.WebPage_createLeafletContent(
    leaflet_theme=leaflet_theme.get("theme"),
    leaflet_title=leaflet_title,
    leaflet_language=leaflet_language,
    leaflet_theme_css_font_list=leaflet_theme.get("theme_css_font_list"),
    leaflet_theme_css_url=leaflet_theme.get("theme_css_url"),
    leaflet_template_css_url=leaflet_theme.get("template_css_url"),
    leaflet_content=leaflet_content,
    leaflet_display_side=leaflet_display_side,
    leaflet_theme_logo_url=leaflet_theme.get("theme_logo_url"),
    leaflet_theme_logo_alt=leaflet_theme.get("theme_logo_description"),
    leaflet_css=leaflet_css
  )

  # ================ encode and build cloudoo elements =========================
  embedded_html_data = leaflet.Base_convertHtmlToSingleFile(leaflet_content, allow_script=True)
  header_embedded_html_data = leaflet.Base_convertHtmlToSingleFile(leaflet_head, allow_script=True)
  footer_embedded_html_data = leaflet.Base_convertHtmlToSingleFile(leaflet_foot, allow_script=True)
  pdf_file = leaflet.Base_cloudoooDocumentConvert(embedded_html_data, "html", "pdf", conversion_kw=dict(
      encoding="utf8",
      orientation="portrait",
      margin_top=50,
      margin_bottom=20,
      margin_left=0,
      margin_right=0,
      header_html_data=b64encode(header_embedded_html_data),
      header_spacing=10,
      footer_html_data=b64encode(footer_embedded_html_data),
      footer_spacing=3
    )
  )
  return leaflet.WebPage_finishPdfCreation(
    doc_download=leaflet_download,
    doc_save=leaflet_save,
    doc_version=leaflet_version,
    doc_title=leaflet_title,
    doc_relative_url=leaflet_relative_url,
    doc_aggregate_list=leaflet_aggregate_list,
    doc_language=leaflet_language,
    doc_modification_date=leaflet_modification_date,
    doc_reference=leaflet_reference,
    doc_full_reference=leaflet_full_reference,
    doc_pdf_file=pdf_file
  )
