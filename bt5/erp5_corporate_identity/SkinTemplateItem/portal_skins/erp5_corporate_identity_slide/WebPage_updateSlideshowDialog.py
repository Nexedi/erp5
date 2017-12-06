"""
================================================================================
Update the slide dialog with parameters manually entered
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
      override_logo_reference=override_logo_reference,
      override_source_organisation_title=override_source_organisation_title,
      display_note=display_note,
      display_svg=display_svg,
      document_save=document_save,
      document_download=document_download,
      format=format,
    )
  )
