"""
================================================================================
MAIN FILE: generate letter in different output formats
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# kw-parameters   (* default)
# ------------------------------------------------------------------------------
# format:                   output in html*, pdf
# transformation:           convert content into nothing*, book
# ------
# override_source_person:   to use instead of the underlying document creator
# override_source_organisation: to use instead of document creator organisation
# override_destination_person: to use instead of event destination/null
# override_destination_organisation: to use instead of event destination/null
# override_date             to use instead of current date
# override_batch_mode       used for tests
# ------
# document_download:        download file directly (default None)
# document_save:            save file in document module (default None)
# ------
# display_head:             display letter adress head (1)* or not (0)
# display_svg               display images in svg or png*
# display_source_address    display source adress in adress field

import re

from base64 import b64encode

blank = ''
pref = context.getPortalObject().portal_preferences

# -------------------------- Setup ---------------------------------------------
letter = context
letter_format = kw.get('format') or 'html'
letter_display_head = int(kw.get('display_head') or 0)
letter_display_svg = kw.get('display_svg') or 'png'
letter_download = int(kw.get('document_download') or 0)
letter_save = int(kw.get('document_save') or 0)

override_source_person_title = kw.get('override_source_person_title', None)
override_source_organisation_title = kw.get("override_source_organisation_title", None)
override_destination_person_title = kw.get("override_destination_person_title", None)
override_destination_organisation_title = kw.get("override_destination_organisation_title", None)
override_date = kw.get("override_date")
override_batch_mode = kw.get('batch_mode', None)

destination_position_in_letter = kw.get('destination_position_in_letter', 'right')
display_sender_company_above_recipient = kw.get('display_sender_company_above_recipient', 0)
destination_position_padding_left = kw.get('destination_position_padding_left', '100px')
letter_header_margin_to_top = kw.get('letter_header_margin_to_top') or 26
# -------------------------- Document Parameters  ------------------------------
letter_portal_type = letter.getPortalType()
letter_relative_url = letter.getRelativeUrl()
letter_prefix = pref.getPreferredCorporateIdentityTemplateLetterDocumentPrefix() or "Letter."

# letter can be Web Page or Event created in Ticket module
if letter_portal_type == "Web Page":
  letter_title = letter.getTitle()
  letter_modification_date = DateTime(override_date) if override_date else letter.getCreationDate()
  letter_content = letter.getTextContent()
  letter_language = letter.getLanguage()
  letter_aggregate_list = []
  letter_source = None
  letter_destination = None
  letter_reference = letter.getReference()
  letter_version = letter.getVersion() or "001"
else:
  letter_format = 'pdf'
  letter_save = letter_save or True
  letter_modification_date = letter.getStartDate() or letter.getCreationDate()
  letter_title = letter.getTitle()
  letter_content = letter.getTextContent()
  letter_aggregate_list = letter.getAggregateList()
  letter_language = kw.get('select_language')
  letter_source = letter.getSource()
  letter_destination = letter.getDestination()
  # cut corner to retrieve path to css files
  letter_version = "001"
  letter_reference = letter.getReference()

if not letter_content:
  return

# overrides for tests
if override_batch_mode:
  letter_modification_date = DateTime("1976-11-04")

if letter_language and letter_language != blank:
  letter.REQUEST['AcceptLanguage'].set(letter_language, 10)
else:
  letter_language = blank
if letter_reference is None:
  letter_reference = letter_prefix + letter_title.replace(" ", ".")
letter_full_reference = '-'.join([letter_reference, letter_version, letter_language])

# --------------------------- Layout Parameters --------------------------------
letter_theme = letter.Base_getThemeDict(doc_format=letter_format, css_path="template_css/letter", skin="Letter")

# --------------------------- Source/Destination -------------------------------
letter_source = letter.Base_getSourceDict(
  source=letter_source,
  override_source_person_title=override_source_person_title,
  override_source_organisation_title=override_source_organisation_title,
  override_logo_reference=None,
  theme_logo_url=letter_theme.get("theme_logo_url", None),
  letter_context=True
)
letter_destination = letter.Base_getDestinationDict(
  destination=letter_destination,
  override_destination_person_title=override_destination_person_title,
  override_destination_organisation_title=override_destination_organisation_title,
)

# ========================= TRANSFORMATION: book ===============================

# --------------------------- Content Upgrades ---------------------------------
for image in re.findall('(<img.*?/>)', letter_content):
  letter_content = letter_content.replace(
    image,
    letter.WebPage_validateImage(
      img_string=image,
      img_svg_format=letter_display_svg
    )
  )
# ============================= Format: html ===================================
if letter_format == "html":
  letter_output = letter.Letter_createLetter(
    letter_display_head=letter_display_head,
    letter_theme=letter_theme.get("theme"),
    letter_title=letter_title,
    letter_language=letter_language,
    letter_theme_css_font_list=letter_theme.get("theme_css_font_list"),
    letter_theme_css_url=letter_theme.get("theme_css_url"),
    letter_template_css_url=letter_theme.get("template_css_url"),
    letter_theme_logo_url=letter.Base_setUrl(path=letter_source.get("enhanced_logo_url"), display=None),
    letter_theme_logo_alt=letter_theme.get("theme_logo_description"),
    letter_timestamp=letter_modification_date.strftime('%Y-%m-%d'),
    letter_destination_company=letter_destination.get("organisation_title", blank),
    letter_destination_person=letter_destination.get("name", blank),
    letter_destination_address=letter_destination.get("address", blank),
    letter_destination_postal_code=letter_destination.get("postal_code", blank),
    letter_destination_city=letter_destination.get("city", blank),
    letter_destination_country=letter_destination.get("country", blank),
    letter_destination_position = destination_position_in_letter,
    letter_destination_position_padding_left = destination_position_padding_left,
    letter_source_company=letter_source.get("corporate_name", letter_source.get("organisation_title", blank)),
    letter_source_company_corporate_name=letter_source.get("corporate_name", blank),
    letter_source_company_capital=letter_source.get("social_capital", blank),
    letter_source_company_capital_currency=letter_source.get("social_capital_currency", blank),
    letter_source_registered_court=letter_source.get("registered_court", blank),
    letter_source_ape_code=letter_source.get("activity_code", blank),
    letter_source_address=letter_source.get("address", blank),
    letter_source_postal_code=letter_source.get("postal_code", blank),
    letter_source_city=letter_source.get("city", blank),
    letter_source_country_code=letter_source.get("codification", blank),
    letter_source_country=letter_source.get("country", blank),
    letter_content = letter_content,
    letter_display_sender_company_above_recipient = display_sender_company_above_recipient,
    letter_source_vat=letter_source.get("vat", blank),
    letter_source_corporate_registration=letter_source.get("corporate_registration", blank),
    letter_source_phone=letter_source.get("phone", blank),
    letter_source_fax=letter_source.get("fax", blank),
    letter_source_mail=letter_source.get("email", blank),
    letter_source_website=letter_source.get("website", blank),
    letter_source_bank=letter_source.get("bank", blank),
    letter_source_bic=letter_source.get("bic", blank),
    letter_source_iban=letter_source.get("iban", blank)
  )
  return letter.Base_finishWebPageCreation(
    doc_download=letter_download,
    doc_save=letter_save,
    doc_version=letter_version,
    doc_title=letter_title,
    doc_relative_url=letter_relative_url,
    doc_aggregate_list=letter_aggregate_list,
    doc_language=letter_language,
    doc_modification_date=letter_modification_date,
    doc_reference=letter_reference,
    doc_full_reference=letter_full_reference,
    doc_html_file=letter_output
  )

# ============================= Format: pdf ====================================
if letter_format == "pdf":
  letter_head = letter.Letter_createLetterHeader(
    letter_display_head=letter_display_head,
    letter_theme=letter_theme.get("theme"),
    letter_title=letter_title,
    letter_language=letter_language,
    letter_theme_css_font_list=letter_theme.get("theme_css_font_list"),
    letter_theme_css_url=letter_theme.get("theme_css_url"),
    letter_template_css_url=letter_theme.get("template_css_url"),
    letter_theme_logo_url=letter.Base_setUrl(path=letter_source.get("enhanced_logo_url"), display=None),
    letter_theme_logo_alt=letter_theme.get("theme_logo_description"),
    letter_timestamp=letter_modification_date.strftime('%Y-%m-%d'),
    letter_source_city=letter_source.get("city", blank)
  )

  letter_content = letter.Letter_createLetterContent(
    letter_display_head=letter_display_head,
    letter_theme=letter_theme.get("theme"),
    letter_title=letter_title,
    letter_language=letter_language,
    letter_theme_css_font_list=letter_theme.get("theme_css_font_list"),
    letter_theme_css_url=letter_theme.get("theme_css_url"),
    letter_template_css_url=letter_theme.get("template_css_url"),
    letter_theme_logo_url=letter.Base_setUrl(path=letter_source.get("enhanced_logo_url"), display=None),
    letter_theme_logo_alt=letter_theme.get("theme_logo_description"),
    letter_timestamp=letter_modification_date.strftime('%Y-%m-%d'),
    letter_destination_company=letter_destination.get("organisation_title", blank),
    letter_destination_person=letter_destination.get("name", blank),
    letter_destination_address=letter_destination.get("address", blank),
    letter_destination_postal_code=letter_destination.get("postal_code", blank),
    letter_destination_city=letter_destination.get("city", blank),
    letter_destination_country=letter_destination.get("country", blank),
    letter_destination_position = destination_position_in_letter,
    letter_destination_position_padding_left = destination_position_padding_left,
    letter_source_company=letter_source.get("corporate_name", letter_source.get("organisation_title", blank)),
    letter_source_address=letter_source.get("address", blank),
    letter_source_postal_code=letter_source.get("postal_code", blank),
    letter_source_city=letter_source.get("city", blank),
    letter_source_country_code=letter_source.get("codification", blank),
    letter_display_sender_company_above_recipient = display_sender_company_above_recipient,
    letter_content = letter_content
  )

  letter_foot = letter.Letter_createLetterFooter(
    letter_theme=letter_theme.get("theme"),
    letter_title=letter_title,
    letter_language=letter_language,
    letter_theme_css_font_list=letter_theme.get("theme_css_font_list"),
    letter_theme_css_url=letter_theme.get("theme_css_url"),
    letter_template_css_url=letter_theme.get("template_css_url"),
    letter_source_company=letter_source.get("corporate_name", letter_source.get("organisation_title", blank)),
    letter_source_company_corporate_name=letter_source.get("corporate_name", blank),
    letter_source_company_capital=letter_source.get("social_capital", blank),
    letter_source_company_capital_currency=letter_source.get("social_capital_currency", blank),
    letter_source_registered_court=letter_source.get("registered_court", blank),
    letter_source_ape_code=letter_source.get("activity_code", blank),
    letter_source_address=letter_source.get("address", blank),
    letter_source_postal_code=letter_source.get("postal_code", blank),
    letter_source_city=letter_source.get("city", blank),
    letter_source_country=letter_source.get("country", blank),
    letter_source_vat=letter_source.get("vat", blank),
    letter_source_corporate_registration=letter_source.get("corporate_registration", blank),
    letter_source_phone=letter_source.get("phone", blank),
    letter_source_fax=letter_source.get("fax", blank),
    letter_source_mail=letter_source.get("email", blank),
    letter_source_website=letter_source.get("website", blank),
    letter_source_bank=letter_source.get("bank", blank),
    letter_source_bic=letter_source.get("bic", blank),
    letter_source_iban=letter_source.get("iban", blank),
  )

  # ================ encode and build cloudoo elements =========================
  embedded_html_data = letter.Base_convertHtmlToSingleFile(letter_content, allow_script=True).encode('utf-8')
  header_embedded_html_data = letter.Base_convertHtmlToSingleFile(letter_head, allow_script=True).encode('utf-8')
  footer_embedded_html_data = letter.Base_convertHtmlToSingleFile(letter_foot, allow_script=True).encode('utf-8')
  pdf_file = letter.Base_cloudoooDocumentConvert(embedded_html_data, "html", "pdf", conversion_kw=dict(
      encoding="utf8",
      margin_top=letter_header_margin_to_top,
      margin_bottom=30,
      margin_left=0,
      margin_right=0,
      header_spacing=1,
      header_html_data=b64encode(header_embedded_html_data).decode(),
      footer_html_data=b64encode(footer_embedded_html_data).decode(),
    )
  )

  # return file for comparison in portal-component tests
  if override_batch_mode:
    if letter_portal_type != "Web Page":
      return pdf_file

  return letter.WebPage_finishPdfCreation(
    doc_download=letter_download,
    doc_save=letter_save,
    doc_version=letter_version,
    doc_title=letter_title,
    doc_relative_url=letter_relative_url,
    doc_aggregate_list=letter_aggregate_list,
    doc_language=letter_language,
    doc_modification_date=letter_modification_date,
    doc_reference=letter_reference,
    doc_full_reference=letter_full_reference,
    doc_pdf_file=pdf_file
  )
