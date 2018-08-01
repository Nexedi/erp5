"""
================================================================================
View WebPage as Book or Report
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# parameters
# ------------------------------------------------------------------------------
# format                                output (html*, pdf)
# batch_mode                            used for tests
# transformation                        (not done)
#
# include_content_table                 include table of content (True*)
# include_history_table                 include history/authors (XXX not done)
# include_reference_table               include table of links/images/tables
# include_linked_content                embed content of linked documents
# include_report_content                embed content of report documents

# document_download                     download file directly (None*)
# document_save                         save file in document module (None*)
# document_language                     language to generate report in
# document_reference                    reference of document for report
# document_version                      version of document for report
# document_title                        document title for report
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
# requirement_relative_url              XXX relate sale order to requirement
#
# start_date                            start date of the report
# stop_date                             stop date of the report
#
# report_name                           name of report to call
# report_title                          title of report
#
# display_depth                         depth to report (eg sale order lines)
# display_detail                        show details on report
# display_sandbox                       embed report inside iframe
# display_embedded                      omit footer/header inside iframe
# display_comment                       show comments on report
# display_header                        display report header
# display_svg                           format for svg images (svg, png*)
# display_milestone                     whether to show milestones or not
# display_orphan                        display orphan requirements

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
    display_sandbox=display_sandbox,
    display_embedded=display_embedded,
    display_milestone=display_milestone,
    display_orphan=display_orphan,
    start_date=start_date,
    stop_date=stop_date,
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
