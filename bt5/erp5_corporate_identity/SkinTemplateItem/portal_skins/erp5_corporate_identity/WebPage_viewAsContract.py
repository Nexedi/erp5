import re
import six

from base64 import b64encode
from Products.ERP5Type.Utils import bytes2str, str2bytes 

blank = b''
pref = context.getPortalObject().portal_preferences

contract_format = kw.get('format') or 'html'
contract_save = int(kw.get('document_save') or 0)
contract_display_svg = kw.get('display_svg') or 'png'

contract_include_content_table = int(kw.get('include_content_table') or 0)
contract_include_history_table = int(kw.get('include_history_table') or 0)
contract_include_reference_table = int(kw.get('include_reference_table') or 0)
contract_include_linked_content = int(kw.get('include_linked_content') or 0)
contract_include_report_content = int(kw.get('include_report_content') or 0)

override_batch_mode = kw.get('batch_mode')

contract_relative_url = context.getRelativeUrl()
#contract_prefix = pref.getPreferredCorporateIdentityTemplateContractDocumentPrefix() or "Contract."
contract_prefix='Contract.'
contract_rendering_fix = context.WebPage_getPdfOutputRenderingFix() or blank
contract_content = context.getTextContent()
if not contract_content:
  return
contract_aggregate_list = []
contract_revision = context.getRevision()
contract_modification_date = context.getModificationDate()
contract_language = context.getLanguage()

contract_reference = context.getReference()
contract_short_title = context.getShortTitle()
contract_version = context.getVersion() or "001"
contract_description = context.getDescription()
contract_title = context.getTitle()

if six.PY2 and isinstance(contract_content, six.text_type):
  contract_content = contract_content.encode("UTF-8")

contract_history_section_list = re.findall('<section.+?>.+?</section>', contract_content, re.S)
for contract_history_section in contract_history_section_list:
  contract_content = contract_content.replace(contract_history_section, '')
"""
for header in re.findall("<h[1-6].*</h[1-6]>", contract_content or ""):
  convert_to_h2 = True
  for tag in ['introduction', 'annex', 'appendix']:
    if tag in header.lower():
      convert_to_h2 = False
      break
  if convert_to_h2:
    header_list = re.findall("<(h[1-6]).*>", header)
    if len(header_list):
      tag = header_list[0]
      key = tag[1]
      contract_content = contract_content.replace(
        header,
        header.replace(tag, 'h%s' % (int(key) + 1))
      )
"""

# override for tests
if override_batch_mode:
  contract_modification_date = DateTime("1976-11-04")
  contract_revision = "1"

contract_short_date = contract_modification_date.strftime('%Y-%m-%d')
if contract_language:
  context.REQUEST['AcceptLanguage'].set(contract_language, 10)
else:
  contract_language = blank

if not contract_reference:
  contract_reference = contract_prefix + contract_title.replace(" ", ".")
contract_full_reference = '-'.join([contract_reference, contract_version, contract_language])

# ------------------------------- Theme ----------------------------------------
contract_theme = context.Base_getThemeDict(doc_format=contract_format, css_path="template_css/contract", skin="Contract")

# --------------------------- Source/Destination -------------------------------
contract_source = context.Base_getSourceDict(
  theme_logo_url=contract_theme.get("theme_logo_url", None)
)

# --------------------------- Content Upgrades ---------------------------------
contract_reference_list = []
contract_report_css_list = contract_report_js_list = []
contract_applicable_document_list = []
contract_abbreviation_list = []
contract_image_list = []
contract_table_list = []
contract_table_of_content = blank



# old generate book, this embed link like <a href="Template.Test.context.Embeddable.Document">This link should be embedded</a>
if contract_include_linked_content:
  contract_content = context.WebPage_embedLinkedDocumentList(doc_content=contract_content)

# embed reports, link like <a href="project_module/1234?report=bam>, which has report=
if contract_include_report_content:
  contract_report_css_list = pref.getPreferredCorporateIdentityTemplateReportCssList() or []
  contract_report_js_list = pref.getPreferredCorporateIdentityTemplateReportJsList() or []
  contract_content = context.WebPage_embedReportDocumentList(doc_content=contract_content, doc_language=contract_language, doc_format=contract_format)

# table of links
if contract_include_reference_table:
  contract_link_list = context.WebPage_createLinkOverview(contract_content)
  table_link_list = context.WebPage_createTableOverview(contract_content)
  image_link_list = context.WebPage_createImageOverview(contract_content)
  for referenced_document in contract_link_list.get("reference_list", []):
    contract_reference_list.append(referenced_document.get("item"))
    contract_content = contract_content.replace(referenced_document.get("input"), referenced_document.get("output"),1)
  for applicable_document in contract_link_list.get("applicable_list", []):
    contract_applicable_document_list.append(applicable_document.get("item"))
    contract_content = contract_content.replace(applicable_document.get("input"), applicable_document.get("output"),1)
  for abbreviation in contract_link_list.get("abbreviation_list", []):
    contract_abbreviation_list.append(abbreviation.get("item"))
    contract_content = contract_content.replace(abbreviation.get("input"), abbreviation.get("output"),1)
  for figure in image_link_list.get("figure_list", []):
    contract_image_list.append(figure.get("item"))
    contract_content = contract_content.replace(figure.get("input"), figure.get("output"), 1)
  for table in table_link_list.get("table_list", []):
    contract_table_list.append(table.get("item"))
    contract_content = contract_content.replace(table.get("input"), table.get("output"), 1)

  # in order for the reference tables to be in the table of content, they must
  # be added beforehand to content
  contract_references = context.WebPage_createContractTableOfReferences(
    contract_format=contract_format,
    contract_theme=contract_theme.get("theme"),
    contract_title=contract_title,
    contract_language=contract_language,
    contract_theme_css_font_list=contract_theme.get("theme_css_font_list"),
    contract_theme_css_url=contract_theme.get("theme_css_url"),
    contract_template_css_url=contract_theme.get("template_css_url"),
    contract_include_reference=contract_include_reference_table,
    contract_reference_list=contract_reference_list,
    contract_applicable_document_list=contract_applicable_document_list,
    contract_abbreviation_list=contract_abbreviation_list,
    contract_image_list=contract_image_list,
    contract_table_list=contract_table_list
  )
  contract_references = context.Base_unescape(contract_references)
  contract_content = contract_content.replace("${WebPage_insertTableOfReferences}", contract_references.encode('UTF-8').strip())
else:
  contract_content = contract_content.replace("${WebPage_insertTableOfReferences}", blank)

# table of content has to be created manually to run over everything that
# should be indexed in the toc
if contract_include_content_table:
  contract_translated_toc_title = context.Base_translateString("Table of Contents", lang=contract_language)
  if contract_format == "pdf":
    contract_table_of_content = context.WebPage_createContractXslTableOfContent(
      contract_toc_title=contract_translated_toc_title,
    ).encode('UTF-8').strip()
  elif contract_format == "html":
    contract_content, contract_table_of_content = context.WebPage_createTableOfContent(
      doc_content=contract_content,
      doc_reference=contract_reference,
      doc_toc_title=contract_translated_toc_title,
      type='contract'
    )

for image in re.findall('(<img.*?/>)', contract_content):
  contract_content = contract_content.replace(
    image,
    context.WebPage_validateImage(
      img_string=image,
      img_svg_format=contract_display_svg,
      img_wrap=True
    )
  )
# ============================ Transformation ==================================

# ========================== Format: mhtml/html ================================
if contract_format == "html" or contract_format == "mhtml":
  context.REQUEST.RESPONSE.setHeader("Content-Type", "text/html; charset=utf-8")
  contract_output = context.WebPage_createContract(
    contract_history_section_list = contract_history_section_list,
    contract_theme=contract_theme.get("theme"),
    contract_title=contract_title,
    contract_language=contract_language,
    contract_theme_css_font_list=contract_theme.get("theme_css_font_list"),
    contract_theme_css_url=contract_theme.get("theme_css_url"),
    contract_template_css_url=contract_theme.get("template_css_url"),
    contract_report_css_list=contract_report_css_list,
    contract_report_js_list=contract_report_js_list,
    contract_short_title=contract_short_title,
    contract_description=contract_description,
    contract_source_person_title=contract_source.get("contributor_title_string").split(','),
    contract_include_history=contract_include_history_table,
    contract_logo_url=context.Base_setUrl(path=contract_source.get("enhanced_logo_url"), display="small"),
    contract_logo_title=contract_theme.get("theme_logo_description"),
    contract_reference=contract_reference,
    contract_revision=contract_revision,
    contract_version=contract_version,
    contract_short_date=contract_short_date,
    contract_full_reference=contract_full_reference,
    contract_source_organisation_title=contract_source.get("organisation_title") or blank,
    contract_content=contract_content,
    contract_table_of_content=contract_table_of_content
  )
  if contract_format == "html":
    return context.Base_finishWebPageCreation(
      doc_save=contract_save,
      doc_version=contract_version,
      doc_title=contract_title,
      doc_relative_url=contract_relative_url,
      doc_aggregate_list=contract_aggregate_list,
      doc_language=contract_language,
      doc_modification_date=contract_modification_date,
      doc_reference=contract_reference,
      doc_full_reference=contract_full_reference,
      doc_html_file=contract_output
    )

  return context.Base_convertHtmlToSingleFile(contract_output, allow_script=True)

# ============================= Format: pdf ====================================
elif contract_format == "pdf":
  contract_cover = context.WebPage_createContractCover(
    contract_theme=contract_theme.get("theme"),
    contract_title=contract_title,
    contract_language=contract_language,
    contract_theme_css_font_list=contract_theme.get("theme_css_font_list"),
    contract_theme_css_url=contract_theme.get("theme_css_url"),
    contract_template_css_url=contract_theme.get("template_css_url"),
    contract_short_title=contract_short_title,
    contract_description=contract_description,
    contract_source_person_title=contract_source.get("contributor_title_string").split(",")
  )

  contract_history = context.WebPage_createContractTableOfHistory(
    contract_history_section_list = contract_history_section_list,
    contract_theme=contract_theme.get("theme"),
    contract_title=contract_title,
    contract_language=contract_language,
    contract_theme_css_font_list=contract_theme.get("theme_css_font_list"),
    contract_theme_css_url=contract_theme.get("theme_css_url"),
    contract_theme_logo_url=context.Base_setUrl(path=contract_source.get("enhanced_logo_url"), display="small"),
    contract_theme_logo_alt=contract_theme.get("theme_logo_alt"),
    contract_template_css_url=contract_theme.get("template_css_url"),
    contract_include_history=contract_include_history_table
  )

  # contract_references created and added above
  contract_content = context.WebPage_createContractContent(
    contract_format=contract_format,
    contract_rendering_fix=contract_rendering_fix,
    contract_theme=contract_theme.get("theme"),
    contract_title=contract_title,
    contract_language=contract_language,
    contract_theme_css_font_list=contract_theme.get("theme_css_font_list"),
    contract_theme_css_url=contract_theme.get("theme_css_url"),
    contract_template_css_url=contract_theme.get("template_css_url"),
    contract_report_css_list=contract_report_css_list,
    contract_report_js_list=contract_report_js_list,
    contract_content=contract_content,
  )

  contract_head = context.WebPage_createContractHeader(
    contract_theme=contract_theme.get("theme"),
    contract_title=contract_title,
    contract_language=contract_language,
    contract_theme_css_font_list=contract_theme.get("theme_css_font_list"),
    contract_theme_css_url=contract_theme.get("theme_css_url"),
    contract_template_css_url=contract_theme.get("template_css_url"),
    contract_logo_url=context.Base_setUrl(path=contract_source.get("enhanced_logo_url"), display="small"),
    contract_logo_title=contract_theme.get("theme_logo_description"),
    contract_short_title=contract_short_title,
    contract_reference=contract_reference,
    contract_revision=contract_revision,
    contract_version=contract_version,
    contract_short_date=contract_short_date
  )

  contract_foot = context.WebPage_createContractFooter(
    contract_theme=contract_theme.get("theme"),
    contract_title=contract_title,
    contract_language=contract_language,
    contract_theme_css_font_list=contract_theme.get("theme_css_font_list"),
    contract_theme_css_url=contract_theme.get("theme_css_url"),
    contract_theme_logo_url=context.Base_setUrl(path=contract_source.get("enhanced_logo_url"), display="small"),
    contract_theme_logo_alt=contract_theme.get("theme_logo_description"),
    contract_template_css_url=contract_theme.get("template_css_url"),
    contract_full_reference=contract_full_reference,
    contract_source_organisation_title=contract_source.get("organisation_title") or blank,
  )

  # ================ encode and build cloudoo elements =========================
  header_embedded_html_data = str2bytes(context.Base_convertHtmlToSingleFile(contract_head, allow_script=True))
  before_toc_data_list = [
    bytes2str(b64encode(str2bytes(context.Base_convertHtmlToSingleFile(contract_cover, allow_script=True)))),
  ]
  after_toc_data_list = []
  if contract_include_history_table:
    before_toc_data_list.append(
      bytes2str(b64encode(str2bytes(context.Base_convertHtmlToSingleFile(contract_history, allow_script=True))))
    )
  #if contract_include_reference_table:
  #  after_toc_data_list.append(
  #    bytes2str(b64encode(str2bytes(context.Base_convertHtmlToSingleFile(contract_references, allow_script=True))))
  #  )
  xsl_style_sheet_data = contract_table_of_content
  embedded_html_data = str2bytes(context.Base_convertHtmlToSingleFile(contract_content, allow_script=True))
  footer_embedded_html_data = str2bytes(context.Base_convertHtmlToSingleFile(contract_foot, allow_script=True))
  margin_top = 40
  margin_bottom = 20
  pdf_file = context.Base_cloudoooDocumentConvert(embedded_html_data, "html", "pdf", conversion_kw=dict(
    encoding="utf8",
    margin_top=margin_top,
    margin_bottom=margin_bottom,
    toc=True if contract_include_content_table else False,
    before_toc_data_list=before_toc_data_list,
    xsl_style_sheet_data=bytes2str(b64encode(xsl_style_sheet_data)),
    after_toc_data_list=after_toc_data_list,
    header_html_data=bytes2str(b64encode(header_embedded_html_data)),
    header_spacing=10,
    footer_html_data=bytes2str(b64encode(footer_embedded_html_data)),
    footer_spacing=3,
    )
  )
  return context.WebPage_finishPdfCreation(
    doc_save=contract_save,
    doc_version=contract_version or "001",
    doc_title=contract_title,
    doc_relative_url=contract_relative_url,
    doc_aggregate_list=contract_aggregate_list,
    doc_language=contract_language,
    doc_modification_date=contract_modification_date,
    doc_reference=contract_reference,
    doc_full_reference=contract_full_reference,
    doc_pdf_file=pdf_file
  )
