"""
================================================================================
Update a book dialog with parameters manually entered
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# XXX: url_param_string on this dialog goes easily over 2000 chars and
# Base_callDialogMethod sets an arbitrary limit for redirects at 2000 chars.
# Drop unnecessary fields, it's just a dialog update.

# parameters
# ------------------------------------------------------------------------------
# format                                output (html*, pdf)
# cancel_url                            url to revert from dialog
# dialog_id                             id of current dialog
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
from Products.ERP5Type.Message import translateString
if dialog_id is not None:
  request = container.REQUEST
  request.form['portal_status_message'] = translateString('Preview updated.')
  request.form['cancel_url'] = cancel_url
  request.form['portal_skin'] = portal_skin
  request.form['format'] = format
  request.form['display_svg'] = display_svg
  request.form['document_save'] = document_save
  request.form['document_download'] = document_download
  request.form['field_your_override_document_description'] = context.Base_getBookParameter(description=True)
  request.form['field_your_override_document_short_title'] = context.Base_getBookParameter(short_title=True)
  request.form['field_your_override_document_title'] = context.Base_getBookParameter(title=True)
  request.form['field_your_override_document_version'] = context.Base_getBookParameter(version=True)
  request.form['field_your_override_logo_reference'] = context.Base_getBookParameter(logo=True)
  request.form['field_your_override_source_person_title'] = context.Base_getBookParameter(source_person=True)
  request.form['field_your_override_document_reference'] = context.Base_getBookParameter(reference=True)
  request.form['field_your_override_source_organisation_title'] = context.Base_getBookParameter(source_organisation=True)
  request.form['transformation'] = transformation
  request.form['include_content_table'] = include_content_table
  request.form['include_history_table'] = include_history_table
  request.form['include_reference_table'] = include_reference_table
  request.form['include_linked_content'] = include_linked_content
  request.form['include_report_content'] = include_report_content
  request.form['margin15mm'] = margin15mm
  return context.Base_renderForm(dialog_id)
