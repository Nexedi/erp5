# pylint:disable=redefined-builtin
from Products.ERP5Type.Message import translateString
if dialog_id is not None:
  request = container.REQUEST
  request.form['portal_status_message'] = translateString('Preview updated.')
  request.form['cancel_url'] = cancel_url
  request.form['format'] = format
  request.form['send_to_maileva'] = send_to_maileva
  request.form['evoluation_remuneration'] = evoluation_remuneration
  request.form['taken_holiday'] = taken_holiday
  request.form['total_holiday'] = total_holiday
  return context.Base_renderForm(dialog_id)
