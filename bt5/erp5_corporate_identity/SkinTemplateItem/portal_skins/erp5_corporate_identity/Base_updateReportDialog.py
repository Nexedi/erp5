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
  request = container.REQUEST
  request.form['portal_status_message']=translateString('Preview updated.')
  request.form['cancel_url']=cancel_url
  request.form['portal_skin']=portal_skin
  request.form['format']=format
  request.form['document_save']=document_save
  request.form['document_download']=document_download
  request.form['document_language']=document_language
  request.form['document_reference']=document_reference
  request.form['document_version']=document_version
  request.form['document_title']=document_title
  request.form['display_milestone']=display_milestone
  request.form['display_depth']=display_depth
  request.form['display_detail']=display_detail
  request.form['display_comment']=display_comment
  request.form['display_header']=display_header
  request.form['display_orphan']=display_orphan
  request.form['start_date']=start_date
  request.form['stop_date']=stop_date
  request.form['report_name']=report_name
  request.form['report_title']=report_title
  request.form['override_source_organisation_title']=override_source_organisation_title
  request.form['requirement_relative_url']=requirement_relative_url

  return context.Base_renderForm(dialog_id)
