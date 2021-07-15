"""
================================================================================
Update a book report dialog with parameters manually entered
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

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
# override_source_organisation_title organisation for report header/footer
#
# document_download:        download file directly
# document_save:            save file in document module
#
# display_header            start headers at what level
# display_comment           include comments where applicable
# display_detail            include details where applicable
# display_depth             level of depth to display
# display_milestone         show milestones if applicable
# display_orphan            show requirements not covered by task
#
# start_date                the start date of a report
# stop_date                 the stop date of a report
#
# report_name               report to generate
# report_title              report title
# requirement_relative_url  XXX sale order has no direct relation to requirement

from Products.ERP5Type.Message import translateString
if dialog_id is not None:
  return context.Base_renderForm(
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
      display_milestone=display_milestone,
      display_depth=display_depth,
      display_detail=display_detail,
      display_comment=display_comment,
      display_header=display_header,
      display_orphan=display_orphan,
      start_date=start_date,
      stop_date=stop_date,
      report_name=report_name,
      report_title=report_title,
      override_source_organisation_title=override_source_organisation_title,
      requirement_relative_url=requirement_relative_url,
      **kw
    )
  )
