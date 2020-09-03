"""
================================================================================
Print letter in any of the supported formats
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# parameters (*default)
# ------------------------------------------------------------------------------
# #REQUEST:                 request object
# format:                   output format
# portal_skin:              skin to use for output
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

return context.Letter_viewAsLetter(
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
  **kw
)
