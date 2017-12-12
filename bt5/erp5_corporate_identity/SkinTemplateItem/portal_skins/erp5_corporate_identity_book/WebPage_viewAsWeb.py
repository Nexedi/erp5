"""
================================================================================
View WebPage as Book or Report
================================================================================
"""
if context.REQUEST["portal_skin"] == "Report":
  return context.Base_viewAsReport(
    format=format,
    document_save=document_save,
    document_download=document_download,
    document_language=document_language,
    document_reference=document_reference,
    document_version=document_version,
    document_title=document_title,
    display_detail=display_detail,
    display_comment=display_comment,
    display_header=display_header,
    display_depth=display_depth,
    report_name=report_name,
    report_title=report_title,
    requirement_relative_url=requirement_relative_url,
    batch_mode=batch_mode,
    **kw
  )

if context.REQUEST["portal_skin"] == "Book":
  return context.WebPage_viewAsBook(
    format=format,
    override_document_reference=override_document_reference,
    override_document_description=override_document_description,
    override_document_short_title=override_document_short_title,
    override_document_title=override_document_title,
    override_document_version=override_document_version,
    override_logo_reference=override_logo_reference,
    override_source_organisation_title=override_source_organisation_title,
    override_source_person_title=override_source_person_title,
    document_save=document_save,
    document_download=document_download,
    include_content_table=include_content_table,
    include_history_table=include_history_table,
    include_reference_table=include_reference_table,
    include_linked_content=include_linked_content,
    include_report_content=include_report_content,
    display_svg=display_svg,
    transformation=transformation,
    batch_mode=batch_mode,
    **kw
  )
