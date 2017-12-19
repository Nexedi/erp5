"""
================================================================================
MAIN FILE: generate report (book header/footer and report content)
================================================================================
"""
# kw-parameters   (* default)
# ------------------------------------------------------------------------------
# format:                   output in html*, pdf
# ------
# document_version:         use as document version
# document_language:        use as document version
# document_reference:       use as document reference
# document_title            use as document title
# override_batch_mode       used for tests
# ------
# document_download:        download file directly (default None)     
# document_save:            save file in document module (default None)
# ------
# display_header            start headers at what level
# display_comment           include comments where applicable
# display_detail            include details where applicable
# display_depth             level of depth to display
# --------
# report_name               report to generate
# report_title              report title
# requirement_relative_url  XXX sale order has no direct relation to requirement

import re

from Products.PythonScripts.standard import html_quote
from base64 import b64encode
from datetime import datetime

blank = ''

# --------------------------  External parameters ------------------------------

# eg "Nexedi" specific parameters
customHandler = getattr(context, "WebPage_getCustomParameter", None)

# parameters common to all templates
commonHandler = getattr(context, "WebPage_getCommonParameter", None)
commonProxyHandler = getattr(context, "WebPage_getCommonProxyParameter", None)

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

# ------------------ HTML cleanup/converter methods ----------------------------
def translateText(snip):
  return doc_localiser.erp5_ui.gettext(snip, lang=doc_language).encode('utf-8').strip()

def setOverrideParam(my_context, my_override, my_param):
  if my_override is not None and my_override is not blank:
    return html_quote(my_override)
  try:
    return getattr(my_context, my_param) or None
  except:
    return blank

# XXX how to set checkbox correctly?
def setToNone(param):
  if param == blank or param == None or param == 0 or param == str(0):
    return None
  else:
    return param

# -------------------------- Setup ---------------------------------------------
doc_download = None #XXX not yet implemented
doc_save = setToNone(kw.get('document_save', None))
doc_display_header = setToNone(kw.get('display_header', None))
doc_display_comment = setToNone(kw.get('display_comment', None))
doc_display_detail = setToNone(kw.get('display_detail', None))
doc_display_depth = setToNone(kw.get('display_depth', None))

override_document_title = kw.get('document_title', None)
override_document_version = kw.get('document_version', None)
override_document_reference = kw.get('document_reference', None)
override_document_language = kw.get('document_language', None)
override_batch_mode = setToNone(kw.get('batch_mode', None))

doc_report_name = kw.get('report_name', None)
doc_report_title = kw.get('report_title', None)
doc_requirement_relative_url = kw.get('requirement_relative_url', None)
doc_format = setToNone(kw.get('format', None)) or 'html'

# -------------------------- Document Parameters  ------------------------------
doc = context
doc_localiser = doc.getPortalObject().Localizer
doc_language = setToNone(setOverrideParam(doc, override_document_language, "language")) or "en"
doc_uid = doc.getUid()
doc_relative_url = doc.getRelativeUrl()
doc_rendering_fix = getCommonParameter('wkhtmltopdf_rendering_fix', None) or blank
doc_title = setToNone(setOverrideParam(doc, override_document_title, "title")) or blank
doc_short_title = setToNone(setOverrideParam(doc, doc_report_title, "short_title")) or blank
doc_version = setToNone(setOverrideParam(doc, override_document_version, "version")) or "001"
doc_report = getattr(doc, doc_report_name)
doc_content = doc_report(
  display_report=True,
  display_depth=doc_display_depth,
  display_detail=doc_display_detail,
  display_header=doc_display_header or 1,
  display_comment=doc_display_comment,
  requirement_url=doc_requirement_relative_url,
  report_title=translateText(doc_report_title)
)
doc_aggregate_list = []
doc_absolute_url = doc.getAbsoluteUrl()
doc_reference = setToNone(setOverrideParam(doc, override_document_reference, "reference")) or blank
doc_revision = "1"
doc_modification_date = DateTime()
doc_short_date = doc_modification_date.strftime('%Y-%m-%d')

if override_batch_mode is not None:
  doc_modification_date = DateTime("1976-11-04")
  doc_revision = "1"
if doc_language is not None: # and doc_format == "pdf":
  doc.REQUEST['AcceptLanguage'].set(doc_language, 10)
if doc_language is None:
  doc_language = blank
if doc_reference is blank:
  doc_reference = "Report." + doc_title.replace(" ", ".")
doc_full_reference = '-'.join([doc_reference, doc_version, doc_language])

# --------------------------- Layout Parameters --------------------------------
doc_theme = doc.Base_getThemeDict(
  custom_theme=getCustomParameter("theme", None),
  override_batch_mode=override_batch_mode,
  format=doc_format,
  url=doc_absolute_url,
  css_path="/book_css/book"
)

# --------------------------- Source/Destination -------------------------------
doc_source = doc.Base_getSourceDict(
  override_source_person_title=None,
  override_source_organisation_title=None,
  default_company_title=getCustomParameter("default_company_title", None),
  default_bank_account_uid=getCustomParameter("default_bank_account_uid", None),
  theme_logo_url=doc_theme.get("theme_logo_url", None)
)

# --------------------------- Content Upgrades ---------------------------------

# ============================= Format: html ===================================
if doc_format == "html":
  html_file = doc.WebPage_createBook(
    book_raw_tables=None,
    book_raw_report=True,
    book_theme=doc_theme.get("theme"),
    book_title=doc_title,
    book_language=doc_language,
    book_theme_css_font_list=doc_theme.get("theme_css_font_list"),
    book_theme_css_url=doc_theme.get("theme_css_url"),
    book_template_css_url=doc_theme.get("template_css_url"),
    book_logo_url=doc_source.get("enhanced_logo_url") + '&display=thumbnail',
    book_logo_title=doc_source.get("theme_logo_description"),
    book_short_title=doc_short_title,
    book_reference=doc_reference,
    book_revision=doc_revision,
    book_version=doc_version,
    book_short_date=doc_short_date,
    book_full_reference=doc_full_reference,
    book_source_organisation_title=doc_source.get("organisation_title") or blank,
    book_content=doc_content,
  )

  return doc.Base_finishWebPageCreation(
    doc_download=doc_download,
    doc_save=doc_save,
    doc_version=override_document_version or doc_version or "001",
    doc_title=doc_title,
    doc_relative_url=doc_relative_url,
    doc_aggregate_list=doc_aggregate_list,
    doc_language=doc_language,
    doc_modification_date=doc_modification_date,
    doc_reference=doc_reference,
    doc_full_reference=doc_full_reference,
    doc_html_file=html_file
  )

# ============================= Format: pdf ====================================
if doc_format == "pdf":
  doc_content = doc.WebPage_createBookContent(
    book_format=doc_format,
    book_rendering_fix=doc_rendering_fix,
    book_theme=doc_theme.get("theme"),
    book_title=doc_title,
    book_language=doc_language,
    book_theme_css_font_list=doc_theme.get("theme_css_font_list"),
    book_theme_css_url=doc_theme.get("theme_css_url"),
    book_template_css_url=doc_theme.get("template_css_url"),
    book_content=doc_content,
  )

  doc_head = doc.WebPage_createBookHeader(
    book_theme=doc_theme.get("theme"),
    book_title=doc_title,
    book_language=doc_language,
    book_theme_css_font_list=doc_theme.get("theme_css_font_list"),
    book_theme_css_url=doc_theme.get("theme_css_url"),
    book_template_css_url=doc_theme.get("template_css_url"),
    book_logo_url=doc_source.get("enhanced_logo_url") + '&display=thumbnail',
    book_logo_title=doc_source.get("theme_logo_description"),
    book_short_title=doc_short_title,
    book_reference=doc_reference,
    book_revision=doc_revision,
    book_version=doc_version,
    book_short_date=doc_short_date,
  )

  doc_foot = doc.WebPage_createBookFooter(
    book_theme=doc_theme.get("theme"),
    book_title=doc_title,
    book_language=doc_language,
    book_theme_css_font_list=doc_theme.get("theme_css_font_list"),
    book_theme_css_url=doc_theme.get("theme_css_url"),
    book_theme_logo_url=doc_source.get("enhanced_logo_url") + '&display=thumbnail',
    book_theme_logo_alt=doc_theme.get("theme_logo_description"),
    book_template_css_url=doc_theme.get("template_css_url"),
    book_full_reference=doc_full_reference,
    book_source_organisation_title=doc_source.get("organisation_title") or blank,
  )

  # ================ encode and build cloudoo elements =========================
  header_embedded_html_data = doc.Base_convertHtmlToSingleFile(doc_head, allow_script=True)
  before_toc_data_list = []
  xsl_style_sheet_data = blank
  embedded_html_data = doc.Base_convertHtmlToSingleFile(doc_content, allow_script=True)
  footer_embedded_html_data = doc.Base_convertHtmlToSingleFile(doc_foot, allow_script=True)

  pdf_file = context.Base_cloudoooDocumentConvert(embedded_html_data, "html", "pdf", conversion_kw=dict(
    encoding="utf8",
    margin_top=40,
    margin_bottom=20,
    toc=False,
    before_toc_data_list=before_toc_data_list,
    xsl_style_sheet_data=b64encode(xsl_style_sheet_data),
    header_html_data=b64encode(header_embedded_html_data),
    header_spacing=10,
    footer_html_data=b64encode(footer_embedded_html_data),
    footer_spacing=3,
    )
  )

  return doc.WebPage_finishPdfCreation(
    doc_download=doc_download,
    doc_save=doc_save,
    doc_version=override_document_version or doc_version or "001",
    doc_title=doc_title,
    doc_relative_url=doc_relative_url,
    doc_aggregate_list=doc_aggregate_list,
    doc_language=doc_language,
    doc_modification_date=doc_modification_date,
    doc_reference=doc_reference,
    doc_full_reference=doc_full_reference,
    doc_pdf_file=pdf_file
  )
