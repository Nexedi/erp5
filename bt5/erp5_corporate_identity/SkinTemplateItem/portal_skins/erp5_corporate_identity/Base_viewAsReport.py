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
# report_name               report to generate
# report_title              report title

from Products.PythonScripts.standard import html_quote
from base64 import b64encode

blank = ''
# ------------------ HTML cleanup/converter methods ----------------------------
def translateText(snip):
  return doc_localiser.erp5_ui.gettext(snip, lang=doc_language).encode('utf-8').strip()

# -------------------------- Setup ---------------------------------------------
doc = context
doc_download = None #XXX not yet implemented
doc_save = int(kw.get('document_save') or 0)
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
override_batch_mode = kw.get('batch_mode')

doc_report_name = kw.get('report_name')
doc_report_title = kw.get('report_title')
doc_format = kw.get('format') or 'html'
doc_embed = doc_format == 'html' and (doc_display_embedded or doc_display_sandbox)

# -------------------------- Document Parameters  ------------------------------
doc_localiser = doc.getPortalObject().Localizer
doc_rendering_fix = doc.Base_getTemplateParameter('wkhtmltopdf_rendering_fix') or blank
doc_report = getattr(doc, doc_report_name)
doc_aggregate_list = []
doc_revision = "1"
doc_modification_date = DateTime()
doc_language = doc.getLanguage() if getattr(doc, 'getLanguage', None) else None

doc_reference = html_quote(override_document_reference) if override_document_reference else doc.getReference() or blank
doc_short_title = html_quote(doc_report_title) if doc_report_title else doc.getShortTitle() or blank
doc_version = html_quote(override_document_version) if override_document_version else getattr(doc, "version", None) or "001"
doc_title = html_quote(override_document_title) if override_document_title else doc.getTitle() or blank
doc_language = html_quote(override_document_language) if override_document_language else doc_language
doc_translated_title = translateText(doc_report_title) if doc_report_title else blank

doc_content = doc_report(
  display_report=None if doc_embed else True,
  format=doc_format,
  display_depth=doc_display_depth,
  display_detail=doc_display_detail,
  display_header=doc_display_header or 1,
  display_comment=doc_display_comment,
  display_sandbox=doc_display_sandbox,
  display_embedded=doc_display_embedded,
  display_milestone=doc_display_milestone,
  display_orphan=doc_display_orphan,
  report_title=doc_translated_title
)

# test overrides
if override_batch_mode:
  doc_modification_date = DateTime("1976-11-04")
  doc_revision = "1"
if doc_language is not None:
  doc.REQUEST['AcceptLanguage'].set(doc_language, 10)
if doc_language is None:
  doc_language = blank
if doc_reference == blank:
  doc_reference = "Report." + doc_title.replace(" ", ".")
doc_full_reference = '-'.join([doc_reference, doc_version, doc_language])
doc_short_date = doc_modification_date.strftime('%Y-%m-%d')

# ------------------------------- Theme ----------------------------------------
doc_theme = doc.Base_getThemeDict(doc_format=doc_format, css_path="template_css/book")

# --------------------------- Source/Destination -------------------------------
doc_source = doc.Base_getSourceDict(
  override_source_person_title=None,
  override_source_organisation_title=None,
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
    book_report_css_list=doc.Base_getTemplateParameter("report_css_list") or [],
    book_report_js_list=doc.Base_getTemplateParameter("report_js_list") or [],
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
    book_report_css_list=doc.Base_getTemplateParameter("report_css_list") or [],
    book_report_js_list=doc.Base_getTemplateParameter("report_js_list") or [],
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
  )

  # ================ encode and build cloudoo elements =========================
  header_embedded_html_data = doc.Base_convertHtmlToSingleFile(doc_head, allow_script=True)
  before_toc_data_list = []
  xsl_style_sheet_data = blank
  embedded_html_data = doc.Base_convertHtmlToSingleFile(doc_content, allow_script=True)
  footer_embedded_html_data = doc.Base_convertHtmlToSingleFile(doc_foot, allow_script=True)

  pdf_file = doc.Base_cloudoooDocumentConvert(embedded_html_data, "html", "pdf", conversion_kw=dict(
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
    doc_aggregate_list=doc_aggregate_list,
    doc_language=doc_language,
    doc_modification_date=doc_modification_date,
    doc_reference=doc_reference,
    doc_full_reference=doc_full_reference,
    doc_pdf_file=pdf_file
  )
