"""
================================================================================
View a WebPage as Letter in the defined output format
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# parameters (*default)
# ------------------------------------------------------------------------------
# format:                   output format
# batch_mode:               used for tests

# display_source_address    display source (!) adress in adress field or not*
# display_svg               display images in svg or png*
# display_head              display letter adress head (1)* or not (0)

# document_download:        download file directly (default None)
# document_save:            save file in document module (default None)

# override_source_organisation_title: override event sender career subordinate
# override_source_person_title: override event sender title
# override_destination_organisation_title: override event recipient subordinate
# override_destination_person_title: overide event recipient
# override_date             to use instead of current date

return context.Base_viewAsLetter(
  format=format,
  display_head=display_head,
  display_svg=display_svg,
  override_source_organisation_title=override_source_organisation_title,
  override_source_person_title=override_source_person_title,
  override_destination_organisation_title=override_destination_organisation_title,
  override_destination_person_title=override_destination_person_title,
  override_date=override_date,
  document_save=document_save,
  document_download=document_download,
  batch_mode=batch_mode,
  destination_position_in_letter = destination_position_in_letter,
  display_sender_company_above_recipient=display_sender_company_above_recipient,
  destination_position_padding_left = destination_position_padding_left,
  letter_header_margin_to_top = letter_header_margin_to_top,
  **kw
)
