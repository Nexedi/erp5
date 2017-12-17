"""
================================================================================
Export WebPage as Report
================================================================================
"""
return context.Base_viewAsReport(
  format=format,
  document_save=document_save,
  document_download=document_download,
  document_language=document_language,
  document_reference=document_reference,
  document_version=document_version,
  display_depth=display_depth,
  display_detail=display_detail,
  display_comment=display_comment,
  display_header=display_header,
  report_name=report_name,
  requirement_relative_url=requirement_relative_url,
  batch_mode=batch_mode,
  **kw
)
