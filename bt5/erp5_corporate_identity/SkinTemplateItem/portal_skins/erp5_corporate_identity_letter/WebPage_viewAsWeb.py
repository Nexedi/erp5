"""
================================================================================
Allow to render letters through the URL?portal_skin=Letter
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# parameters (* default)
# ------------------------------------------------------------------------------
# format:                   output in html*, pdf
# batch_mode:               used for tests

# override_source_organisation_title: to use instead of default company
# override_logo_reference:  to use instead of default company logo in footer

# document_download:        download file directly (default None)
# document_save:            save file in document module (default None)

# display_head:             display the email adress header* or not
# display_svg:              display svg-images as svg or png*
# display_source_address:   display the sender adress in the adress field, too
# override_source_organisation_title: use this organisation as sender
# override_source_person_title: use this person as sender
# override_destination_organisation_title: use this organisation as recipient
# override_destination_person_title: use this person as recipient
# override_date:            use this date as letter date (required field)
return context.Letter_viewAsLetter(
  format=format,
  display_head=display_head,
  display_svg=display_svg,
  display_source_address=display_source_address,
  override_source_organisation_title=override_source_organisation_title,
  override_source_person_title=override_source_person_title,
  override_destination_organisation_title=override_destination_organisation_title,
  override_destination_person_title=override_destination_person_title,
  override_date=override_date,
  document_save=document_save,
  document_download=document_download,
  batch_mode=batch_mode,
  destination_position_in_letter = destination_position_in_letter,
  display_sender_company_above_recipient = display_sender_company_above_recipient,
  destination_position_padding_left = destination_position_padding_left,
  **kw
)
