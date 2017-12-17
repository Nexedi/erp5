"""
================================================================================
Export WebPage as Book
================================================================================
"""

return context.WebPage_viewAsBook(
  override_document_description=override_document_description,
  override_document_short_title=override_document_short_title,
  override_document_title=override_document_title,
  override_document_version=override_document_version,
  override_logo_reference=override_logo_reference,
  override_source_organisation_title=override_source_organisation_title,
  override_source_person_title=override_source_person_title,
  override_document_reference=override_document_reference,
  document_save=document_save,
  document_download=document_download,
  display_svg=display_svg,
  batch_mode=batch_mode,
  transformation=transformation,
  include_content_table=include_content_table,
  include_history_table=include_history_table,
  include_reference_table=include_reference_table,
  include_linked_content=include_linked_content,
  include_report_content=include_report_content,
  format=format,
  **kw
)
