"""
================================================================================
Update the letter dialog with parameters manually entered
================================================================================
"""
# parameters (*default)
# ------------------------------------------------------------------------------
# REQUEST:                  request object
# format:                   output format
# portal_skin:              skin to use for output
# cancel_url:               url to cancel dialog
# dialog_id:                id of current dialog

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

from Products.ERP5Type.Message import translateString
if dialog_id is not None:
  return context.Base_redirect(
    dialog_id,
    keep_items = dict(
      portal_status_message=translateString('Preview updated.'),
      cancel_url=cancel_url,
      portal_skin=portal_skin,
      override_source_organisation_title=override_source_organisation_title,
      override_source_person_title=override_source_person_title,
      override_destination_organisation_title=override_destination_organisation_title,
      override_destination_person_title=override_destination_person_title,
      override_date=override_date,
      format=format,
      display_head=display_head,
      display_svg=display_svg,
      display_source_address=display_source_address,
      document_download=document_download,
      document_save=document_save,
      **kw
    )
  )
