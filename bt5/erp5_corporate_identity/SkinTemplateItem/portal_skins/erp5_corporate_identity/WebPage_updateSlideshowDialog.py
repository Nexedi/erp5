"""
================================================================================
Update the slide dialog with parameters manually entered
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# parameters   (* default)
# ------------------------------------------------------------------------------
# format:                   output in html*, pdf
# batch_mode:               used for tests
# cancel_url:               url to revert from dialog
# dialog_id:                id of the current dialog

# override_source_organisation_title: to use instead of default company
# override_logo_reference:  to use instead of default company logo in footer

# document_download:        download file directly (default None)
# document_save:            save file in document module (default None)

# display_note:             display slide notes (1) or not (0)*
# display_svg:              display svg-images as svg or png*

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
  request.form['field_your_override_logo_reference'] = context.Base_getSlideParameter(logo=True)
  request.form['field_your_override_source_organisation_title'] = context.Base_getSlideParameter(organisation=True)
  request.form['display_note'] = display_note

  return context.Base_renderForm(dialog_id)
