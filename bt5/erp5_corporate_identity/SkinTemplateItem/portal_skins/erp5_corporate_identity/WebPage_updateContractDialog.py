# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

from Products.ERP5Type.Message import translateString
if dialog_id is not None:
  request = container.REQUEST
  request.form['portal_status_message'] = translateString('Preview updated.')
  request.form['cancel_url'] = cancel_url
  request.form['portal_skin'] = portal_skin
  request.form['format'] = format
  request.form['display_svg'] = display_svg
  request.form['document_save'] = document_save
  request.form['include_content_table'] = include_content_table
  request.form['include_history_table'] = include_history_table
  request.form['include_reference_table'] = include_reference_table
  request.form['include_linked_content'] = include_linked_content
  request.form['include_report_content'] = include_report_content
  return context.Base_renderForm(dialog_id)
