"""
================================================================================
MAIN FILE: generate report (book header/footer and report content)
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# kw-parameters   (* default)
# ------------------------------------------------------------------------------
# format:                   output in html*, pdf
# ------
# document_version:         use as document version
# document_language:        use as document version
# document_reference:       use as document reference
# document_title            use as document title

# override_source_organisation organisation for report header/footer
# override_batch_mode       used for tests
# ------
# document_download:        download file directly (default None)
# document_save:            save file in document module (default None)
# ------
# display_header            start headers at what level
# display_comment           include comments where applicable
# display_detail            include details where applicable
# display_depth             level of depth to display
# display_sandbox           sandbox report for display in another html document
# display_milestone         show associated milestones
# display_orphan            show requirements not covered by task/item
# --------
# start_date                the start date of the report
# stop_date                 the stop date of the report
# --------
# report_name               report to generate
# report_title              report title
# report_header             custom report header

from Products.ERP5Type.Utils import str2bytes
from Products.PythonScripts.standard import html_quote
from base64 import b64encode

blank = ''
pref = context.getPortalObject().portal_preferences

# ------------------ HTML cleanup/converter methods ----------------------------
def translateText(snip):
  return context.Base_translateString(snip, lang=doc_language)
  #return doc_localiser.erp5_ui.gettext(snip, lang=doc_language).encode('utf-8').strip()

# -------------------------- Setup ---------------------------------------------
doc = context
doc_prefix = pref.getPreferredCorporateIdentityTemplateReportDocumentPrefix() or "Report."
doc_download = None #XXX not yet implemented
doc_save = int(kw.get('document_save') or 0)
get_doc_after_save = int(kw.get('get_doc_after_save') or 0)
doc_display_header = int(kw.get('display_header') or 0)
doc_display_comment = int(kw.get('display_comment') or 0)
doc_display_detail = int(kw.get('display_detail') or 0)
doc_display_depth = int(kw.get('display_depth') or 0)
doc_display_sandbox = int(kw.get('display_sandbox') or 0)
doc_display_embedded = int(kw.get('display_embedded') or 0)
doc_display_milestone = int(kw.get('display_milestone') or 0)
doc_display_orphan = int(kw.get('display_orphan') or 0)

override_document_title = kw.get('document_title')
override_document_version = kw.get('document_version')
override_document_reference = kw.get('document_reference')
override_document_language = kw.get('document_language')
override_source_organisation_title=kw.get('override_source_organisation', None)
override_batch_mode = kw.get('batch_mode')
css_path = kw.get('css_path', 'template_css/book')
conversion_dict = kw.get('conversion_dict', {})

# we are just caller, so if no dates are passed, the report must decide what to set
doc_report_start_date_input = kw.get('start_date', None) or getattr(context.REQUEST.form, 'start_date', None)
doc_report_start_date = None
if doc_report_start_date_input:
  doc_report_start_date = DateTime(doc_report_start_date_input)
doc_report_stop_date_input = kw.get('stop_date', None) or getattr(context.REQUEST.form, 'stop_date', None)
doc_report_stop_date = None
if doc_report_stop_date_input:
  doc_report_stop_date = DateTime(doc_report_stop_date_input)

doc_report_name = kw.get('report_name')
doc_report_title = kw.get('report_title')
doc_format = kw.get('format') or 'html'
doc_embed = doc_format == 'html' and (doc_display_embedded or doc_display_sandbox)

# -------------------------- Document Parameters  ------------------------------
doc_localiser = doc.getPortalObject().Localizer
doc_rendering_fix = doc.WebPage_getPdfOutputRenderingFix() or blank
doc_report = getattr(doc, doc_report_name)
doc_aggregate_list = []
doc_revision = "1"
doc_modification_date = DateTime()
doc_language = doc.getLanguage() if getattr(doc, 'getLanguage', None) else None
doc_translated_title = translateText(doc_report_title) if doc_report_title else blank

# fallback in case language is still None
if doc_language is None or doc_language == "":
  doc_language = doc_localiser.get_selected_language() or doc_localiser.get_default_language() or "en"

doc_language = html_quote(override_document_language) if override_document_language else doc_language

if doc_language is not None:
  doc.REQUEST['AcceptLanguage'].set(doc_language, 10)
else:
  doc_language = blank

# custom header
doc_header = None
doc_report_header = kw.get('report_header', None)
if doc_report_header:
  doc_report_header = getattr(doc, doc_report_header)
  doc_header = doc_report_header(language=doc_language)

doc_footer = None
doc_report_footer = kw.get('report_footer', None)
if doc_report_footer:
  doc_report_footer = getattr(doc, doc_report_footer)
  doc_footer = doc_report_footer(language=doc_language)

doc_content, report_override_doc_title, report_override_doc_subtitle = doc_report(
  display_report=None if doc_embed else True,
  format=doc_format,
  display_depth=doc_display_depth,
  display_detail=doc_display_detail,
  display_header=doc_display_header,
  display_comment=doc_display_comment,
  display_sandbox=doc_display_sandbox,
  display_embedded=doc_display_embedded,
  display_milestone=doc_display_milestone,
  display_orphan=doc_display_orphan,
  start_date=doc_report_start_date,
  stop_date=doc_report_stop_date,
  report_title=doc_translated_title,
  override_batch_mode=override_batch_mode,
  language = doc_language
)

if doc.isModuleType():
  doc_reference = html_quote(override_document_reference) if override_document_reference else blank
  doc_short_title = translateText(report_override_doc_subtitle if report_override_doc_subtitle else html_quote(doc_report_title) if doc_report_title else blank)
  doc_version = html_quote(override_document_version) if override_document_version else getattr(doc, "version", None) or "001"
  doc_title = translateText(html_quote(override_document_title) if override_document_title else report_override_doc_title if report_override_doc_title else blank)
else:
  doc_reference = html_quote(override_document_reference) if override_document_reference else doc.getReference() or blank
  doc_short_title = translateText(report_override_doc_subtitle if report_override_doc_subtitle else html_quote(doc_report_title) if doc_report_title else doc.getShortTitle() or blank)
  doc_version = html_quote(override_document_version) if override_document_version else getattr(doc, "version", None) or "001"
  doc_title = translateText(html_quote(override_document_title) if override_document_title else report_override_doc_title if report_override_doc_title else doc.getTitle() or blank)

# test overrides
if override_batch_mode:
  doc_modification_date = DateTime("1976-11-04")
  doc_revision = "1"
if doc_reference == blank:
  doc_reference = doc_prefix + doc_title.replace(" ", ".")
doc_full_reference = '-'.join([doc_reference, doc_version, doc_language])
doc_short_date = doc_modification_date.strftime('%Y-%m-%d')

# ------------------------------- Theme ----------------------------------------
doc_theme = doc.Base_getThemeDict(doc_format=doc_format, css_path=css_path, skin="Book")
# --------------------------- Source/Destination -------------------------------
doc_source = doc.Base_getSourceDict(
  override_source_person_title=None,
  override_source_organisation_title=override_source_organisation_title,
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
    book_embed=doc_embed,
    book_theme_css_font_list=doc_theme.get("theme_css_font_list"),
    book_theme_css_url=doc_theme.get("theme_css_url"),
    book_template_css_url=doc_theme.get("template_css_url"),
    book_logo_url=doc.Base_setUrl(path=doc_source.get("enhanced_logo_url"), display=None),
    book_logo_title=doc_source.get("theme_logo_description"),
    book_report_css_list=pref.getPreferredCorporateIdentityTemplateReportCssList() or [],
    book_report_js_list=pref.getPreferredCorporateIdentityTemplateReportJsList() or [],
    book_short_title=doc_short_title,
    book_reference=doc_reference,
    book_revision=doc_revision,
    book_version=doc_version,
    book_short_date=doc_short_date,
    book_full_reference=doc_full_reference,
    book_source_organisation_title=doc_source.get("organisation_title") or blank,
    book_content=doc_content,
    book_header = doc_header,
    book_footer = doc_footer
  )

  return doc.Base_finishWebPageCreation(
    doc_download=doc_download,
    doc_save=doc_save,
    doc_version=override_document_version or doc_version or "001",
    doc_title=doc_title,
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
    book_report_css_list=pref.getPreferredCorporateIdentityTemplateReportCssList() or [],
    book_report_js_list=pref.getPreferredCorporateIdentityTemplateReportJsList() or [],
    book_content=doc_content,
  )

  doc_head = doc.WebPage_createBookHeader(
    book_theme=doc_theme.get("theme"),
    book_title=doc_title,
    book_language=doc_language,
    book_theme_css_font_list=doc_theme.get("theme_css_font_list"),
    book_theme_css_url=doc_theme.get("theme_css_url"),
    book_template_css_url=doc_theme.get("template_css_url"),
    book_logo_url=doc.Base_setUrl(path=doc_source.get("enhanced_logo_url"), display=None),
    book_logo_title=doc_source.get("theme_logo_description"),
    book_short_title=doc_short_title,
    book_reference=doc_reference,
    book_revision=doc_revision,
    book_version=doc_version,
    book_short_date=doc_short_date,
    book_header = doc_header
  )

  doc_foot = doc.WebPage_createBookFooter(
    book_theme=doc_theme.get("theme"),
    book_title=doc_title,
    book_language=doc_language,
    book_theme_css_font_list=doc_theme.get("theme_css_font_list"),
    book_theme_css_url=doc_theme.get("theme_css_url"),
    book_theme_logo_url=doc.Base_setUrl(path=doc_source.get("enhanced_logo_url"), display=None),
    book_theme_logo_alt=doc_theme.get("theme_logo_description"),
    book_template_css_url=doc_theme.get("template_css_url"),
    book_full_reference=doc_full_reference,
    book_source_organisation_title=doc_source.get("organisation_title") or blank,
    book_footer = doc_footer
  )

  # ================ encode and build cloudoo elements =========================
  header_embedded_html_data = str2bytes(doc.Base_convertHtmlToSingleFile(doc_head, allow_script=True))
  before_toc_data_list = []
  xsl_style_sheet_data = blank.encode()
  embedded_html_data = str2bytes(doc.Base_convertHtmlToSingleFile(doc_content, allow_script=True))
  footer_embedded_html_data = str2bytes(doc.Base_convertHtmlToSingleFile(doc_foot, allow_script=True))
  default_conversion_kw = dict(
    encoding="utf8",
    margin_top=40,
    margin_bottom=20,
    toc=False,
    before_toc_data_list=before_toc_data_list,
    xsl_style_sheet_data=b64encode(xsl_style_sheet_data).decode(),
    header_html_data=b64encode(header_embedded_html_data).decode(),
    header_spacing=10,
    footer_html_data=b64encode(footer_embedded_html_data).decode(),
    footer_spacing=3,
  )
  default_conversion_kw.update(conversion_dict)
  pdf_file = doc.Base_cloudoooDocumentConvert(embedded_html_data, "html", "pdf", conversion_kw=default_conversion_kw)

  return doc.WebPage_finishPdfCreation(
    doc_download=doc_download,
    doc_save=doc_save,
    get_doc_after_save = get_doc_after_save,
    doc_version=override_document_version or doc_version or "001",
    doc_title=doc_title,
    doc_aggregate_list=doc_aggregate_list,
    doc_language=doc_language,
    doc_modification_date=doc_modification_date,
    doc_reference=doc_reference,
    doc_full_reference=doc_full_reference,
    doc_pdf_file=pdf_file
  )
