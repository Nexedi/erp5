"""
================================================================================
MAIN FILE: generate book in different output formats
================================================================================
"""
# kw-parameters   (* default)
# ------------------------------------------------------------------------------
# format                                output (html*, pdf)
# transformation                        convert into (XXX not done)
# ------
# override_source_person_title          use instead of the document author
# override_source_organisation_title    use as publishing organisation
# override_document_description         use as cover page description
# override_document_short_title         use as cover page subtitle
# override_document_title               use as cover page title
# override_document_version             use as document version
# override_document_reference           use as document reference
# override_logo_reference               use as document header logo
# override_batch_mode                   used for tests
# ------
# book_include_content_table            include table of content (True*)
# book_include_history_table            include history/authors (XXX not done)
# book_include_reference_table          include table of links/images/tables
# book_include_linked_content           embed content of linked documents
# book_include_report_content           embed content of report documents
# ------
# document_download                     download file directly (None*)     
# document_save                         save file in document module (None*)
# ------
# display_svg                           format for svg images (svg, png*)

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
    source_data = my_override_data or book_uid
    return customHandler(parameter=my_parameter, source_data=source_data)

def getCommonParameter(my_parameter, my_override_data):
  if commonHandler is not None:
    source_data = my_override_data or book_uid
    return commonHandler(parameter=my_parameter, source_data=source_data)

def getCommonProxyParameter(my_parameter, my_override_data):
  if commonProxyHandler is not None:
    source_data = my_override_data or book_uid
    return commonProxyHandler(parameter=my_parameter, source_data=source_data)

# ------------------ HTML cleanup/converter methods ----------------------------
def translateText(snip):
  return book_localiser.erp5_ui.gettext(snip, lang=book_language).encode('utf-8').strip()

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

# XXX change url so convert does not fail    
def setUrl(path):
  if path.find("common") > -1:
    return path
  else:
    return path + "&display=thumbnail"

# -------------------------- Setup ---------------------------------------------
book = context
book_format = setToNone(kw.get('format', None)) or 'html'
book_transformation = kw.get('transformation', None)

book_download = setToNone(kw.get('document_download', None))
book_save = setToNone(kw.get('document_save', None))
book_display_svg = setToNone(kw.get('display_svg', None))

book_include_content_table = kw.get('include_content_table', None)
if book_include_content_table is None:
  book_include_content_table = 1
else:
  book_include_content_table = setToNone(book_include_content_table)

book_include_history_table = setToNone(kw.get('include_history_table', None))
book_include_reference_table = setToNone(kw.get('include_reference_table', None))
book_include_linked_content = setToNone(kw.get('include_linked_content', None))
book_include_report_content = setToNone(kw.get('include_report_content', None))

override_source_person_title = kw.get('override_source_person_title', None)
override_source_organisation_title = kw.get("override_source_organisation_title", None)
override_document_description = kw.get('override_document_description', None)
override_document_short_title = kw.get('override_document_short_title', None)
override_document_title = kw.get('override_document_title', None)
override_document_version = kw.get('override_document_version', None)
override_document_reference = kw.get('override_document_reference', None)
override_logo_reference = kw.get('override_logo_reference', None)
override_batch_mode = setToNone(kw.get('batch_mode', None))

# -------------------------- Document Parameters  ------------------------------
book_form = book.REQUEST
book_localiser = book.getPortalObject().Localizer
book_portal_type = book.getPortalType()
book_uid = book.getUid()
book_relative_url = book.getRelativeUrl()
book_prefix = "Book."
book_rendering_fix = getCommonParameter('wkhtmltopdf_rendering_fix', None) or blank

book_dialog_id = book_form.get('dialog_id', None)
book_title = setOverrideParam(book, override_document_title, "title")
book_short_title = setOverrideParam(book, override_document_short_title, "short_title")
book_version = setOverrideParam(book, override_document_version, "version")
book_description = setOverrideParam(book, override_document_description, "description")
book_content = book.getTextContent()
book_language = setToNone(book.getLanguage())
book_aggregate_list = []
book_absolute_url = book.getAbsoluteUrl()
book_reference = (html_quote(override_document_reference) if override_document_reference else book.getReference()) or blank
book_revision = book.getRevision()
book_modification_date = book.getModificationDate()

if override_batch_mode is not None:
  book_modification_date = DateTime("1976-11-04")
  book_revision = "1"
book_short_date = book_modification_date.strftime('%Y-%m-%d')
if book_language is not None: #and book_format == "pdf":
  book.REQUEST['AcceptLanguage'].set(book_language, 10)
if book_language is None:
  book_language = blank
if book_reference is None:
  book_reference = book_prefix + book_title.replace(" ", ".")
book_full_reference = '-'.join([book_reference, book_version, book_language])

# --------------------------- Layout Parameters --------------------------------
book_theme = book.Base_getThemeDict(
  custom_theme=getCustomParameter("theme", None),
  override_batch_mode=override_batch_mode,
  format=book_format,
  url=book_absolute_url,
  css_path="/book_css/book"
)

# --------------------------- Source/Destination -------------------------------
book_source = book.Base_getSourceDict(
  override_source_person_title=override_source_person_title,
  override_source_organisation_title=override_source_organisation_title,
  override_logo_reference=override_logo_reference,
  default_company_title=getCustomParameter("default_company_title", None),
  default_bank_account_uid=getCustomParameter("default_bank_account_uid", None),
  theme_logo_url=book_theme.get("theme_logo_url", None)
)

# --------------------------- Content Upgrades ---------------------------------
book_reference_list = []
book_applicable_document_list = []
book_abbreviation_list = []
book_signature_list = []
book_version_list = []
book_distribution_list = []
book_image_list = []
book_table_list = []
book_table_of_content = blank

# backcompat
book_content.replace("${WebPage_insertTableOfReferences}", blank)

# XXX: not done
if book_include_history_table is not None:
  book_signature_list = []
  book_version_list = []
  book_distribution_list = []

# old generate book
if book_include_linked_content is not None:
  book_content = book.WebPage_embedLinkedDocumentList(doc_content=book_content)

# embed reports
if book_include_report_content is not None:
  book_content = book.WebPage_embedReportDocumentList(doc_content=book_content)

# table of links
if book_include_reference_table is not None:
  book_link_list = book.WebPage_createLinkOverview(book_content)
  table_link_list = book.WebPage_createTableOverview(book_content)
  image_link_list = book.WebPage_createImageOverview(book_content)
  for referenced_document in book_link_list.get("reference_list", []):
    book_reference_list.append(referenced_document.get("item"))
    book_content = book_content.replace(referenced_document.get("input"), referenced_document.get("output"))
  for applicable_document in book_link_list.get("applicable_list", []):
    book_applicable_document_list.append(applicable_document.get("item"))
    book_content = book_content.replace(applicable_document.get("input"), applicable_document.get("output"))
  for abbreviation in book_link_list.get("abbreviation_list", []):
    book_abbreviation_list.append(abbreviation.get("item"))
    book_content = book_content.replace(abbreviation.get("input"), abbreviation.get("output"))
  for figure in image_link_list.get("figure_list", []):
    book_image_list.append(figure.get("item"))
    book_content = book_content.replace(figure.get("input"), figure.get("output"))
  for table in table_link_list.get("table_list", []):
    book_table_list.append(table.get("item"))
    book_content = book_content.replace(table.get("input"), table.get("output"))

  # in order for the reference tables to be in the table of content, they must
  # be added beforehand to content
  book_references = book.WebPage_createBookTableOfReferences(
    book_format=book_format,
    book_theme=book_theme.get("theme"),
    book_title=book_title,
    book_language=book_language,
    book_theme_css_font_list=book_theme.get("theme_css_font_list"),
    book_theme_css_url=book_theme.get("theme_css_url"),
    book_template_css_url=book_theme.get("template_css_url"),
    book_include_reference=book_include_reference_table,
    book_reference_list=book_reference_list,
    book_applicable_document_list=book_applicable_document_list,
    book_abbreviation_list=book_abbreviation_list,
    book_image_list=book_image_list,
    book_table_list=book_table_list
  )
  if book_format == 'html' or book_format == 'mhtml':
    book_content = book_references.encode('utf-8').strip() + book_content
  
# table of content has to be created manually to run over everything that
# should be indexed in the toc
if book_include_content_table is not None:
  book_translated_toc_title = translateText("Table of Contents")
  if book_format == "pdf":
    book_table_of_content = book.WebPage_createBookXslTableOfContent(
      book_toc_title=book_translated_toc_title
    ).encode('utf-8').strip()
  elif book_format == "html":
    book_content, book_table_of_content = book.WebPage_createTableOfContent(
      doc_content=book_content,
      doc_url=book_absolute_url,
      doc_toc_title=book_translated_toc_title
    )

for image in re.findall('(<img.*?/>)', book_content):
  book_content = book_content.replace(
    image,
    book.WebPage_validateImage(
      img_string=image,
      img_svg_format=book_display_svg,
      img_wrap=True
    )
  )
# ============================ Transformation ==================================    

# ========================== Format: mhtml/html ================================
if book_format == "html" or book_format == "mhtml":
  book.REQUEST.RESPONSE.setHeader("Content-Type", "text/html;")
  book_output = book.WebPage_createBook(
    book_theme=book_theme.get("theme"),
    book_title=book_title,
    book_language=book_language,
    book_theme_css_font_list=book_theme.get("theme_css_font_list"),
    book_theme_css_url=book_theme.get("theme_css_url"),
    book_template_css_url=book_theme.get("template_css_url"),
    book_short_title=book_short_title,
    book_description=book_description,
    book_source_person_title=book_source.get("contributor_title_string").split(','),
    book_include_history=book_include_history_table,
    book_signature_list=book_signature_list,
    book_version_list=book_version_list,
    book_distribution_list=book_distribution_list,
    book_logo_url=setUrl(book_source.get("enhanced_logo_url")),
    book_logo_title=book_theme.get("theme_logo_description"),
    book_reference=book_reference,
    book_revision=book_revision,
    book_version=book_version,
    book_short_date=book_short_date,
    book_full_reference=book_full_reference,
    book_source_organisation_title=book_source.get("organisation_title") or blank,
    book_content=book_content,
    book_table_of_content=book_table_of_content
  )
  if book_format == "html":
    return book_output
  if book_format == "mhtml":
    return book.Base_convertHtmlToSingleFile(book_output, allow_script=True)

# ============================= Format: pdf ====================================
if book_format == "pdf":
  book_cover = book.WebPage_createBookCover(
    book_theme=book_theme.get("theme"),
    book_title=book_title,
    book_language=book_language,
    book_theme_css_font_list=book_theme.get("theme_css_font_list"),
    book_theme_css_url=book_theme.get("theme_css_url"),
    book_template_css_url=book_theme.get("template_css_url"),
    book_short_title=book_short_title,
    book_description=book_description,
    book_source_person_title=book_source.get("contributor_title_string").split(",")
  )

  book_history = book.WebPage_createBookTableOfHistory(
    book_theme=book_theme.get("theme"),
    book_title=book_title,
    book_language=book_language,
    book_theme_css_font_list=book_theme.get("theme_css_font_list"),
    book_theme_css_url=book_theme.get("theme_css_url"),
    book_theme_logo_url=setUrl(book_source.get("enhanced_logo_url")),
    book_theme_logo_alt=book_theme.get("theme_logo_alt"),
    book_template_css_url=book_theme.get("template_css_url"),
    book_include_history=book_include_history_table,
    book_signature_list=book_signature_list,
    book_version_list=book_version_list,
    book_distribution_list=book_distribution_list,
  )

  # book_references created above

  book_content = book.WebPage_createBookContent(
    book_format=book_format,
    book_rendering_fix=book_rendering_fix,
    book_theme=book_theme.get("theme"),
    book_title=book_title,
    book_language=book_language,
    book_theme_css_font_list=book_theme.get("theme_css_font_list"),
    book_theme_css_url=book_theme.get("theme_css_url"),
    book_template_css_url=book_theme.get("template_css_url"),
    book_content=book_content,
  )
  book_head = book.WebPage_createBookHeader(
    book_theme=book_theme.get("theme"),
    book_title=book_title,
    book_language=book_language,
    book_theme_css_font_list=book_theme.get("theme_css_font_list"),
    book_theme_css_url=book_theme.get("theme_css_url"),
    book_template_css_url=book_theme.get("template_css_url"),
    book_logo_url=setUrl(book_source.get("enhanced_logo_url")),
    book_logo_title=book_theme.get("theme_logo_description"),
    book_short_title=book_short_title,
    book_reference=book_reference,
    book_revision=book_revision,
    book_version=book_version,
    book_short_date=book_short_date
  )
  
  book_foot = book.WebPage_createBookFooter(
    book_theme=book_theme.get("theme"),
    book_title=book_title,
    book_language=book_language,
    book_theme_css_font_list=book_theme.get("theme_css_font_list"),
    book_theme_css_url=book_theme.get("theme_css_url"),
    book_theme_logo_url=setUrl(book_source.get("enhanced_logo_url")),
    book_theme_logo_alt=book_theme.get("theme_logo_description"),
    book_template_css_url=book_theme.get("template_css_url"),
    book_full_reference=book_full_reference,
    book_source_organisation_title=book_source.get("organisation_title") or blank,
  )

  # ================ encode and build cloudoo elements =========================
  header_embedded_html_data = book.Base_convertHtmlToSingleFile(book_head, allow_script=True)
  before_toc_data_list = [
    b64encode(book.Base_convertHtmlToSingleFile(book_cover, allow_script=True)),
  ]
  after_toc_data_list = []
  if book_include_history_table is not None:
    before_toc_data_list.append(
      b64encode(book.Base_convertHtmlToSingleFile(book_history, allow_script=True))
    )
  if book_include_reference_table is not None: 
    after_toc_data_list.append(
      b64encode(book.Base_convertHtmlToSingleFile(book_references, allow_script=True))
    )
  xsl_style_sheet_data = book_table_of_content
  embedded_html_data = book.Base_convertHtmlToSingleFile(book_content, allow_script=True)
  footer_embedded_html_data = book.Base_convertHtmlToSingleFile(book_foot, allow_script=True)

  pdf_file = context.Base_cloudoooDocumentConvert(embedded_html_data, "html", "pdf", conversion_kw=dict(
    encoding="utf8",
    margin_top=40,
    margin_bottom=20,
    toc=True if book_include_content_table is not None else False,
    before_toc_data_list=before_toc_data_list,
    xsl_style_sheet_data=b64encode(xsl_style_sheet_data),
    after_toc_data_list=after_toc_data_list,
    header_html_data=b64encode(header_embedded_html_data),
    header_spacing=10,
    footer_html_data=b64encode(footer_embedded_html_data),
    footer_spacing=3,
    )
  )

  return book.WebPage_finishPdfCreation(
    doc_download=book_download,
    doc_save=book_save,
    doc_version=override_document_version or book_version or "001",
    doc_title=book_title,
    doc_relative_url=book_relative_url,
    doc_aggregate_list=book_aggregate_list,
    doc_language=book_language,
    doc_modification_date=book_modification_date,
    doc_reference=book_reference,
    doc_full_reference=book_full_reference,
    doc_pdf_file=pdf_file
  )
