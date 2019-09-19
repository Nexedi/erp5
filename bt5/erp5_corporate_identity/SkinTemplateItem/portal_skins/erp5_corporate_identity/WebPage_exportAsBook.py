"""
================================================================================
Export WebPage as Book
================================================================================
"""

# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# parameters
# ------------------------------------------------------------------------------
# format                                output (html*, pdf)
# batch_mode                            used for tests
#
# document_download                     download file directly (None*)
# document_save                         save file in document module (None*)
#
# override_source_person_title          use instead of the document author
# override_source_organisation_title    use as publishing organisation
# override_document_description         use as cover page description
# override_document_short_title         use as cover page subtitle
# override_document_title               use as cover page title
# override_document_version             use as document version
# override_document_reference           use as document reference
# override_logo_reference               use as document header logo
#
# include_content_table                 include table of content (True*)
# include_history_table                 include history/authors (XXX not done)
# include_reference_table               include table of links/images/tables
# include_linked_content                embed content of linked documents
# include_report_content                embed content of report documents
#
# display_svg                           format for svg images (svg, png*)

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
  margin15mm = margin15mm,
  format=format,
  **kw
)
