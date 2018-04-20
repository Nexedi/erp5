"""
================================================================================
Export WebPage as Report
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# parameters   (* default)
# ------------------------------------------------------------------------------
# format:                   output in html*, pdf
# batch_mode:               used for tests
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
# display_orphan            show requirements not covered by task
# display_detail            include details where applicable
# display_depth             level of depth to display
# display_milestone         show milestones where applicable
#
# report_name               report to generate
# report_title              report title

return context.Base_viewAsReport(
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
  display_orphan=display_orphan,
  display_header=display_header,
  display_milestone=display_milestone,
  report_name=report_name,
  report_title=report_title,
  batch_mode=batch_mode,
  **kw
)
