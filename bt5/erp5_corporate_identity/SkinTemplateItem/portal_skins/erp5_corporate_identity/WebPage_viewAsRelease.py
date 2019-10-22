"""
================================================================================
MAIN FILE: render press release in different output formats
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# kw-parameters   (* default)
# ------------------------------------------------------------------------------
# format:                   output in html*, pdf
# display_about:            display automatic about info (1)* or not (0)
# display_svg:              display images as svg or png*
# transformation:           convert content into nothing*, book
# ------
# override_source_organisation_title used instead of follow-up organisation
# override_source_person_title used instead of contributor
# override_batch_mode       used for tests
# ------
# document_downalod:        download file directly (default None)
# document_save:            save file in document module (default None)

import re
from base64 import b64encode

blank = ''
pref = context.getPortalObject().portal_preferences
re_tag = re.compile(r'<[^>]+>')

# ------------------ HTML cleanup/converter methods ----------------------------
def removeTags(text):
  return re_tag.sub('', text)

def removeHardcodedAbout(my_content):
  release_about = re.findall('(<h[1-6]>About.*)', release_content, re.S)
  if len(release_about) > 0:
    return my_content.replace(release_about[0], "")
  return my_content

# -------------------------- Setup ---------------------------------------------
release = context
release_prefix = pref.getPreferredCorporateIdentityTemplateReleaseDocumentPrefix() or "Release."
release_format = kw.get('format') or 'html'
release_display_about = int(kw.get('display_about') or 0)
release_display_svg = kw.get('display_svg') or "png"
release_download = int(kw.get('document_download') or 0)
release_save = int(kw.get('document_save') or 0)

override_source_person_title = kw.get('override_source_person_title', None)
override_source_organisation_title = kw.get("override_source_organisation_title", None)
override_batch_mode = kw.get('batch_mode')

# -------------------------- Document Parameters  ------------------------------
release_content = release.getTextContent()
release_title = release.getTitle()
release_language = release.getLanguage()
release_short_title = release.getShortTitle()
release_description = release.getDescription()
release_creation_date = release.getCreationDate()
release_modification_date = release.getModificationDate()
release_aggregate_list = []
release_relative_url = release.getRelativeUrl()
release_creation_year = release_creation_date.strftime('%Y') if release_creation_date else blank
#release_creation_month = release_creation_date.strftime('%b')
#release_date = ''.join([release_creation_month, "-", release_creation_year])
release_reference = release.getReference()
release_version = release.getVersion() or "001"

# test overrides
if override_batch_mode:
  release_creation_year="1976"
if release_language is not None:
  release.REQUEST['AcceptLanguage'].set(release_language, 10)
if release_language is None:
  release_language = blank
if release_reference is None:
  release_reference = release_prefix + release_title.replace(" ", ".")
release_full_reference = '-'.join([release_reference, release_version, release_language])

# ---------------------------- Theme Parameters --------------------------------
release_theme = release.Base_getThemeDict(doc_format=release_format, css_path="template_css/release", skin="Release")
release_css = ''.join([
  'html .ci-press-release .ci-press-release-logo:before {',
    'background: url("%s") center no-repeat;' % (release_theme.get("theme_logo_url")),
    'background-size: contain;',
  '}'
])
# ---------------------------------- Source ------------------------------------
release_source = release.Base_getSourceDict(
  override_source_person_title=override_source_person_title,
  override_source_organisation_title=override_source_organisation_title,
  theme_logo_url=release_theme.get("theme_logo_url", None),
)

# --------------------------- Content Upgrades ---------------------------------
# remove any hand written about stuff
release_content = removeHardcodedAbout(release_content)

for image in re.findall('(<img.*?/>)', release_content):
  release_content = release_content.replace(
    image,
    release.WebPage_validateImage(
      img_string=image,
      img_svg_format=release_display_svg,
      img_wrap=True
    )
  )

# ========================= TRANSFORMATION: book ===============================
# # backcompat image cleanup attempt
# raw_image_list = re.findall('(<div class="left.*?<\/div>)', release_content, re.S)
# if len(raw_image_list):
#    for image in raw_image_list:
#      clean_image = re.findall('(<img.*?\/>)', image, re.S)
#      if len(clean_image):
#        alted = re.findall('alt="(.*?)"', clean_image[0], re.S)
#        if len(alted):
#          release_content = release_content.replace(image, clean_image[0])
#        else:
#          new_image = clean_image.replace("<img", '<img alt="XXX Missing Description"')
#          release_content = release_content.replace(image, new_image)
#  for table in re.findall('(<table.*?<\/table>)', release_content):
#    release_content = release_content.replace(table, release.WebPage_validateTable(table_string=table))
#
#  for link in re.findall('(<a.*?<\/a>)', release_content):
#    release_content = release_content.replace(link, release.WebPage_validateLink(link_string=link, link_toc=true))

# ------------------------ counter, about & authors ------------------------
if release_display_about:
  release_about = release.WebPage_createReleaseAbout(
    release_word_count=len(removeTags(release_content).split()),
    release_character_count=len(release_content),
    release_organisation_list=release.Base_getTemplateProxyParameter(parameter="organisation"),
    release_contributor_list=release.Base_getTemplateProxyParameter(parameter="author"),
    release_relative_url=release_relative_url,
  )
  #release_content = release_content.decode() + release_about.decode()
  if isinstance(release_content, unicode):
    release_content = release_content.encode("UTF-8")
  if isinstance(release_about, unicode):
    release_about = release_about.encode("UTF-8")

  release_content = release_content + release_about

# ============================= Format: html ===================================
if release_format == "html":
  release_output = release.WebPage_createRelease(
    release_theme=release_theme.get("theme"),
    release_title=release_title,
    release_language=release_language,
    release_theme_css_font_list=release_theme.get("theme_css_font_list"),
    release_theme_css_url=release_theme.get("theme_css_url"),
    release_template_css_url=release_theme.get("template_css_url"),
    release_full_reference=release_full_reference,
    release_css=release_css,
    release_theme_logo_url=release_theme.get("theme_logo_url"),
    release_creation_year=release_creation_year,
    release_copyright=release_source.get("organisation_title", blank),
    release_contributor_list=release_source.get("contributor_title_string"),
    release_description=release_description,
    release_short_title=release_short_title,
    release_organisation_logo=release_theme.get("theme_logo_url"),
    release_organisation=release_source.get("organisation_title", blank),
    release_organisation_claim=release_theme.get("theme_logo_description"),
    release_content=release_content,
  )
  return release.Base_finishWebPageCreation(
    doc_download=release_download,
    doc_save=release_save,
    doc_version=release_version,
    doc_title=release_title,
    doc_relative_url=release_relative_url,
    doc_aggregate_list=release_aggregate_list,
    doc_language=release_language,
    doc_modification_date=release_modification_date,
    doc_reference=release_reference,
    doc_full_reference=release_full_reference,
    doc_html_file=release_output
  )

# ============================= Format: pdf ====================================
if release_format == "pdf":
  release_foot = release.WebPage_createReleaseFooter(
    release_theme=release_theme.get("theme"),
    release_title=release_title,
    release_language=release_language,
    release_theme_css_font_list=release_theme.get("theme_css_font_list"),
    release_theme_css_url=release_theme.get("theme_css_url"),
    release_template_css_url=release_theme.get("template_css_url"),
    release_full_reference=release_full_reference,
    release_theme_logo_url=release_theme.get("theme_logo_url"),
    release_creation_year=release_creation_year,
    release_copyright=release_source.get("organisation_title", blank),
    release_contributor_list=release_source.get("contributor_title_string"),
  )

  release_head = release.WebPage_createReleaseHeader(
    release_theme=release_theme.get("theme"),
    release_title=release_title,
    release_short_title=release_short_title,
    release_description=release_description,
    release_language=release_language,
    release_theme_css_font_list=release_theme.get("theme_css_font_list"),
    release_theme_css_url=release_theme.get("theme_css_url"),
    release_template_css_url=release_theme.get("template_css_url"),
    release_theme_logo_url=release_theme.get("theme_logo_url"),
    release_organisation=release_source.get("organisation_title", blank),
    release_organisation_claim=release_theme.get("theme_logo_description"),
  )

  release_content = release.WebPage_createReleaseContent(
    release_theme=release_theme.get("theme"),
    release_title=release_title,
    release_language=release_language,
    release_theme_css_font_list=release_theme.get("theme_css_font_list"),
    release_theme_css_url=release_theme.get("theme_css_url"),
    release_template_css_url=release_theme.get("template_css_url"),
    release_css=release_css,
    release_theme_logo_url=release_theme.get("theme_logo_url"),
    release_description=release_description,
    release_short_title=release_short_title,
    release_organisation_logo=release_theme.get("theme_logo_url"),
    release_content=release_content,
  )

  # ================ encode and build cloudoo elements =========================
  embedded_html_data = release.Base_convertHtmlToSingleFile(release_content, allow_script=True)
  header_embedded_html_data = release.Base_convertHtmlToSingleFile(release_head, allow_script=True)
  footer_embedded_html_data = release.Base_convertHtmlToSingleFile(release_foot, allow_script=True)
  pdf_file = release.Base_cloudoooDocumentConvert(embedded_html_data, "html", "pdf", conversion_kw=dict(
      encoding="utf8",
      orientation="portrait",
      margin_top=30,
      margin_bottom=20,
      margin_left=0,
      margin_right=0,
      header_html_data=b64encode(header_embedded_html_data),
      header_spacing=10,
      footer_html_data=b64encode(footer_embedded_html_data),
      footer_spacing=3
    )
  )

  return release.WebPage_finishPdfCreation(
    doc_download=release_download,
    doc_save=release_save,
    doc_version=release_version,
    doc_title=release_title,
    doc_relative_url=release_relative_url,
    doc_aggregate_list=release_aggregate_list,
    doc_language=release_language,
    doc_modification_date=release_modification_date,
    doc_reference=release_reference,
    doc_full_reference=release_full_reference,
    doc_pdf_file=pdf_file
  )
