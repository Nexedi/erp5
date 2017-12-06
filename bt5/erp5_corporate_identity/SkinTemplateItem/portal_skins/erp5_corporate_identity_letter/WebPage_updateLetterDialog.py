"""
================================================================================
Update the letter dialog with parameters manually entered
================================================================================
"""
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
