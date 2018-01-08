"""
================================================================================
Update a book report dialog with parameters manually entered
================================================================================
"""
# parameters   (* default)
# ------------------------------------------------------------------------------
# format:                   output in html*, pdf
# cancel_url:               url to cancel dialog
# dialog_id:                id of current_dialog
# portal_skin:              portal_skin used
#
# document_version:         use as document version
# document_language:        use as document version
# document_reference:       use as document reference
# document_title            use as document title
# override_batch_mode       used for tests
#
# document_download:        download file directly
# document_save:            save file in document module
#
# display_header            start headers at what level
# display_comment           include comments where applicable
# display_detail            include details where applicable
# display_depth             level of depth to display
#
# report_name               report to generate
# report_title              report title
# requirement_relative_url  XXX sale order has no direct relation to requirement

from Products.ERP5Type.Message import translateString
if dialog_id is not None:
  return context.Base_redirect(
    dialog_id,
    keep_items = dict(
      portal_status_message=translateString('Preview updated.'),
      cancel_url=cancel_url,
      portal_skin=portal_skin,
      format=format,
      document_save=document_save,
      document_download=document_download,
      document_language=document_language,
      document_reference=document_reference,
      document_version=document_version,
      document_title=document_title,
      display_depth=display_depth,
      display_detail=display_detail,
      display_comment=display_comment,
      display_header=display_header,
      report_name=report_name,
      report_title=report_title,
      requirement_relative_url=requirement_relative_url,
      **kw
    )
  )
