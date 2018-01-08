"""
================================================================================
Update the slide dialog with parameters manually entered
================================================================================
"""
# parameters   (* default)
# ------------------------------------------------------------------------------
# format:                   output in html*, pdf
# batch_mode:               used for tests
# cancel_url:               url to revert from dialog
# dialog_id:                id of the current dialog

# override_source_organisation_title: to use instead of default company
# override_logo_reference:  to use instead of default company logo in footer

# document_download:        download file directly (default None)
# document_save:            save file in document module (default None)

# display_note:             display slide notes (1) or not (0)*
# display_svg:              display svg-images as svg or png*

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
